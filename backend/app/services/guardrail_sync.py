"""Phase 4, Step 4.3 — Dynamic policy deployment (validation gate + hot-patch).

Holds the sieve's ACTIVE guardrail policy and deploys new rules into it at
runtime, with no redeploy: rules live as Colang files in `guardrails/rails/`, and
the store reloads whenever that directory changes (mtime check). A running
gateway therefore picks up a freshly synthesized rule on the very next request —
that is the "time-to-patch measured in seconds" claim.

Two gates stand between a synthesized rule and production (rules.md §2/§3):
  1. It must be valid Colang (NeMo parses it)      -> guardrail_synth.validate_colang
  2. It must not fire on the benign regression set -> passes_benign_regression here
A rule that would reroute real NexTel customers is REJECTED and logged, so
"self-healing" never becomes "self-inflicted false positives".

Matching is SEMANTIC (embedding cosine over the rule's `define user` utterances),
not lexical. TF-IDF was tried first and measured: benign NexTel traffic scored up
to 0.35 against a rule while paraphrased attacks scored as low as 0.27 — the
distributions overlapped, so no threshold could both generalize and hold the
<5% FPR promise. Embeddings separate them cleanly. Cost is ~10-20 ms per request
(a small local model via Ollama), still ~30x cheaper than the 8B Guard.
"""

from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import numpy as np

from app.core.config import get_settings
from app.core.logging import get_logger
from app.services.guardrail_synth import SynthesizedGuardrail, validate_colang
from app.services.ollama_client import OllamaClient, OllamaError

logger = get_logger(__name__)

_REPO_ROOT = Path(__file__).resolve().parents[3]


@dataclass
class GuardrailRule:
    slug: str
    taxonomy: Optional[str]
    core_technique: str
    utterances: list[str]


@dataclass
class GuardrailMatch:
    slug: str
    taxonomy: Optional[str]
    core_technique: str
    score: float


def _rails_dir() -> Path:
    d = _REPO_ROOT / get_settings().guardrails_rails_dir
    d.mkdir(parents=True, exist_ok=True)
    return d


def _pending_dir() -> Path:
    d = _REPO_ROOT / get_settings().guardrails_pending_dir
    d.mkdir(parents=True, exist_ok=True)
    return d


def parse_colang_rule(text: str) -> Optional[GuardrailRule]:
    """Pull the rule's identity + example utterances back out of a Colang file."""
    m = re.search(r"define user attempt_(\w+)", text)
    if not m:
        return None
    slug = m.group(1).replace("_", "-")
    tech = re.search(r"#\s*technique:\s*(.+)", text)
    tax = re.search(r"#\s*taxonomy\s*:\s*(.+)", text)
    taxonomy = tax.group(1).strip() if tax else None
    if taxonomy in ("unclassified", "None", ""):
        taxonomy = None

    # utterances = the quoted lines under `define user attempt_...`
    block = text[m.end():]
    block = re.split(r"\ndefine ", block)[0]
    utterances = re.findall(r'^\s+"(.+)"\s*$', block, re.MULTILINE)
    if not utterances:
        return None
    return GuardrailRule(
        slug=slug,
        taxonomy=taxonomy,
        core_technique=tech.group(1).strip() if tech else slug,
        utterances=[u.replace('\\"', '"') for u in utterances],
    )


def _cosine(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Cosine similarity of one vector `a` against rows of `b`."""
    a_n = a / (np.linalg.norm(a) + 1e-12)
    b_n = b / (np.linalg.norm(b, axis=1, keepdims=True) + 1e-12)
    return b_n @ a_n


class GuardrailStore:
    """Active policy set. Reloads from disk when the rails dir changes."""

    def __init__(self, client: Optional[OllamaClient] = None) -> None:
        self.settings = get_settings()
        self.client = client or OllamaClient()
        self.rules: list[GuardrailRule] = []
        self._embeddings: Optional[np.ndarray] = None   # utterance embeddings
        self._owner: list[int] = []                     # utterance index -> rule index
        self._corpus: list[str] = []
        self._stamp: Optional[float] = None
        self.reload()

    # --- loading -------------------------------------------------------
    def _dir_stamp(self) -> float:
        d = _rails_dir()
        stamps = [d.stat().st_mtime]
        stamps += [p.stat().st_mtime for p in d.glob("*.co")]
        return max(stamps)

    def reload(self) -> None:
        rules: list[GuardrailRule] = []
        for p in sorted(_rails_dir().glob("*.co")):
            try:
                rule = parse_colang_rule(p.read_text(encoding="utf-8"))
            except OSError as exc:
                logger.error("Could not read guardrail %s: %s", p, exc)
                continue
            if rule:
                rules.append(rule)
        self.rules = rules
        self._stamp = self._dir_stamp()

        corpus, owner = [], []
        for i, r in enumerate(rules):
            for u in r.utterances:
                corpus.append(u)
                owner.append(i)
        self._corpus, self._owner = corpus, owner
        self._embeddings = None  # re-embedded lazily on next match
        logger.info("Guardrail policy loaded: %d rule(s), %d utterance(s)", len(rules), len(corpus))

    def _maybe_reload(self) -> None:
        """Cheap stat-based check so a hot-patched rule is live on the next request."""
        try:
            if self._dir_stamp() != self._stamp:
                logger.info("Guardrail rails changed on disk — hot-reloading policy.")
                self.reload()
        except OSError:
            pass

    async def _ensure_embeddings(self) -> bool:
        """Embed the active rules' utterances once per (re)load."""
        if self._embeddings is not None:
            return True
        if not self._corpus:
            return False
        try:
            vecs = await self.client.embed(self._corpus, keep_alive=self.settings.ollama_keep_alive)
        except OllamaError as exc:
            logger.error("Guardrail embedding failed (%s); tier-0 disabled this request.", exc)
            return False
        self._embeddings = np.array(vecs, dtype=float)
        return True

    # --- matching ------------------------------------------------------
    async def match(self, message: str) -> Optional[GuardrailMatch]:
        self._maybe_reload()
        if not self.rules:
            return None
        if not await self._ensure_embeddings():
            return None
        try:
            q = np.array((await self.client.embed([message]))[0], dtype=float)
        except OllamaError as exc:
            logger.error("Guardrail match embedding failed (%s); skipping tier-0.", exc)
            return None
        sims = _cosine(q, self._embeddings)
        best = int(sims.argmax())
        score = float(sims[best])
        if score < self.settings.guardrail_match_threshold:
            return None
        rule = self.rules[self._owner[best]]
        return GuardrailMatch(
            slug=rule.slug, taxonomy=rule.taxonomy,
            core_technique=rule.core_technique, score=round(score, 3),
        )


# Module-level singleton shared by the sieve and the sync/deploy path.
store = GuardrailStore()


# --- validation gate + hot-patch ---------------------------------------
def load_benign_regression_set() -> list[str]:
    """Real NexTel customer queries. A new rule that fires on ANY of these is
    rejected — protecting the <5% FPR promise (PRD §8)."""
    prompts: list[str] = []
    p = _REPO_ROOT / "ml" / "datasets" / "nextel_benign_aug.jsonl"
    if p.exists():
        for line in p.open(encoding="utf-8"):
            line = line.strip()
            if line:
                try:
                    prompts.append(json.loads(line)["text"])
                except (json.JSONDecodeError, KeyError):
                    continue
    seed = _REPO_ROOT / "ml" / "datasets" / "sieve_eval_seed.jsonl"
    if seed.exists():
        for line in seed.open(encoding="utf-8"):
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
            except json.JSONDecodeError:
                continue
            if r.get("label") == "benign":
                prompts.append(r["text"])
    return prompts


async def passes_benign_regression(
    guardrail: SynthesizedGuardrail,
    benign: Optional[list[str]] = None,
    client: Optional[OllamaClient] = None,
) -> tuple[bool, list[str]]:
    """Would this rule fire on legitimate customer traffic? Returns (ok, offenders).

    Uses the SAME semantic matcher the runtime uses, so the gate measures exactly
    what will happen in production.
    """
    benign = benign if benign is not None else load_benign_regression_set()
    if not guardrail.utterances or not benign:
        return True, []
    client = client or OllamaClient()
    try:
        rule_vecs = np.array(await client.embed(guardrail.utterances), dtype=float)
        benign_vecs = np.array(await client.embed(benign), dtype=float)
    except OllamaError as exc:
        # Fail closed on the GATE: if we cannot prove the rule is safe, do not
        # deploy it (rules.md §3 — never ship an unvalidated guardrail).
        logger.error("Benign regression gate could not run (%s) — refusing deploy.", exc)
        return False, [f"<gate unavailable: {exc}>"]

    threshold = get_settings().guardrail_match_threshold
    offenders = []
    for i, bv in enumerate(benign_vecs):
        if _cosine(bv, rule_vecs).max() >= threshold:
            offenders.append(benign[i])
    return (len(offenders) == 0), offenders


@dataclass
class DeployResult:
    deployed: bool
    reason: str
    path: Optional[str] = None
    seconds: float = 0.0
    status: str = "deployed"  # "deployed" | "rejected" | "pending_review"


async def hot_patch(guardrail: SynthesizedGuardrail) -> DeployResult:
    """Validate -> benign-regression gate -> write to the active policy dir.

    The running gateway picks it up on the next request (no redeploy).
    """
    start = time.perf_counter()

    ok, detail = validate_colang(guardrail.colang)
    if not ok:
        logger.error("Guardrail REJECTED (invalid Colang): %s", detail)
        return DeployResult(False, f"invalid Colang: {detail}", seconds=time.perf_counter() - start)

    ok, offenders = await passes_benign_regression(guardrail)
    if not ok:
        logger.error(
            "Guardrail REJECTED (would false-positive on %d benign prompt(s), e.g. %r)",
            len(offenders), offenders[0][:60],
        )
        return DeployResult(
            False,
            f"benign regression failed: would flag {len(offenders)} legitimate prompt(s)",
            seconds=time.perf_counter() - start,
            status="rejected",
        )

    # Passed both automated gates. Park for human review, or go live.
    if get_settings().guardrail_require_review:
        path = _pending_dir() / f"{guardrail.slug}.co"
        path.write_text(guardrail.colang, encoding="utf-8")
        seconds = time.perf_counter() - start
        logger.info("Guardrail PENDING REVIEW -> %s (%s) in %.2fs", path.name, detail, seconds)
        return DeployResult(
            False, f"passed gates, awaiting human approval ({detail})",
            path=str(path), seconds=seconds, status="pending_review",
        )

    path = _rails_dir() / f"{guardrail.slug}.co"
    path.write_text(guardrail.colang, encoding="utf-8")
    store.reload()
    seconds = time.perf_counter() - start
    logger.info("Guardrail DEPLOYED -> %s (%s) in %.2fs", path.name, detail, seconds)
    return DeployResult(True, f"deployed ({detail})", path=str(path), seconds=seconds, status="deployed")


# --- human-review queue management -------------------------------------
def list_pending() -> list[str]:
    return sorted(p.stem for p in _pending_dir().glob("*.co"))


def approve_pending(slug: str) -> DeployResult:
    """Promote a reviewed rule from pending -> active (goes live immediately)."""
    src = _pending_dir() / f"{slug}.co"
    if not src.exists():
        return DeployResult(False, f"no pending rule named {slug!r}", status="rejected")
    # Re-validate on approval — the file could have been hand-edited during review.
    ok, detail = validate_colang(src.read_text(encoding="utf-8"))
    if not ok:
        return DeployResult(False, f"pending rule is invalid Colang: {detail}", status="rejected")
    dst = _rails_dir() / f"{slug}.co"
    dst.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
    src.unlink()
    store.reload()
    logger.info("Guardrail APPROVED and DEPLOYED -> %s", dst.name)
    return DeployResult(True, f"approved and deployed ({detail})", path=str(dst), status="deployed")


def reject_pending(slug: str) -> bool:
    src = _pending_dir() / f"{slug}.co"
    if src.exists():
        src.unlink()
        logger.info("Pending guardrail REJECTED by reviewer -> %s", slug)
        return True
    return False
