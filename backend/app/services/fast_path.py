"""Fast-path sieve classifier (tier 1) — TF-IDF + Logistic Regression.

Loads the model trained by ml/train_fast_path.py and scores a prompt's
adversarial probability in ~2 ms (vs ~700 ms for the 8B Guard). Used as the
first tier of the two-tier sieve: obviously-benign traffic is resolved here
without ever calling the Guard; anything above the calibrated safe-threshold
escalates to the Guard (tier 2), which remains the authoritative verdict +
taxonomy labeler.

Degrades safely: if the model artifact is missing (e.g. `train_fast_path.py`
hasn't been run), `available` is False and the sieve simply always escalates to
the Guard — the fast path is a latency optimization, never a correctness
dependency.
"""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Optional

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class FastPath:
    # backend/app/services/fast_path.py -> repo root is parents[3]
    _REPO_ROOT = Path(__file__).resolve().parents[3]

    def __init__(self, model_path: Optional[Path] = None) -> None:
        self.settings = get_settings()
        raw = model_path or Path(self.settings.fast_path_model_path)
        # Resolve relative paths against the repo root, not the process cwd, so
        # the model loads whether uvicorn is started from backend/ or the root.
        self.model_path = raw if raw.is_absolute() else (self._REPO_ROOT / raw).resolve()
        self._model = None
        self.available = False
        self._load()

    def _load(self) -> None:
        if not self.settings.use_fast_path:
            logger.info("Fast-path disabled by config; sieve will always use the Guard.")
            return
        if not self.model_path.exists():
            logger.warning(
                "Fast-path model not found at %s — run ml/train_fast_path.py. "
                "Sieve will escalate every request to the Guard until then.",
                self.model_path,
            )
            return
        try:
            import joblib

            self._model = joblib.load(self.model_path)
            self.available = True
            logger.info("Fast-path model loaded from %s", self.model_path)
        except Exception as exc:  # noqa: BLE001 - never let this break startup
            logger.error("Failed to load fast-path model (%s); escalating all to Guard.", exc)

    def _score_sync(self, text: str) -> float:
        return float(self._model.predict_proba([text])[:, 1][0])

    async def score(self, text: str) -> Optional[float]:
        """Return P(adversarial) in [0,1], or None if the fast path is unavailable."""
        if not self.available:
            return None
        # CPU work (~2 ms) off the event loop to honour the no-blocking rule.
        return await asyncio.to_thread(self._score_sync, text)
