"""Intent Sieve — two-tier: fast-path classifier + Llama-Guard 3 (8B).

Phase 2 (docs/sieve_model_selection.md, Option C; completed with the fast-path).

  TIER 1 (fast_path.py, ~2 ms): a TF-IDF + LogReg classifier scores P(adversarial).
    If that score is below the calibrated safe-threshold, the request is resolved
    SAFE immediately — the common, latency-sensitive benign case skips the Guard.
  TIER 2 (Llama-Guard 3 8B, ~700 ms): everything at/above the threshold escalates
    here for a verdict against the custom injection policy, WITH recent
    conversation history so multi-turn attacks are visible (rules.md §2). This
    tier is the taxonomy labeler.

OR-ensemble (Step 2.1, docs/sieve_eval_at_scale.md): the scaled eval showed the
8B Guard misses ~41% of real in-the-wild jailbreaks that the fast path catches
(and the fast path misses semantic exfiltration the Guard catches). So on the
escalated path the verdict is UNSAFE if the Guard says unsafe OR the fast path
is highly confident (>= fast_path_attack_threshold, calibrated to 0 NexTel-benign
false positives). Neither tier alone meets the detection goal at scale; together
they do.

If the fast path is unavailable (model not trained / disabled), every request
goes straight to the Guard — the fast path is a latency optimization, never a
correctness dependency.

Failure behaviour is FAIL-CLOSED (rules.md §3): if Ollama is unreachable or
returns something unparseable, the verdict is ERROR — never a silent SAFE.

Threat score: the fast path emits a real probability; the Guard is binary
(unsafe→1.0 / safe→0.0). `threat_score` carries whichever tier decided.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Optional

from app.core.config import get_settings
from app.core.logging import get_logger
from app.models.schemas import ChatMessage, SieveVerdict
from app.services import guardrail_sync, sieve_policy
from app.services.fast_path import FastPath
from app.services.ollama_client import OllamaClient, OllamaError

logger = get_logger(__name__)


@dataclass
class SieveResult:
    verdict: SieveVerdict
    threat_score: float
    latency_ms: float
    decided_by: str = "guard"  # "guardrail" | "fast_path" | "guard"
    matched_taxonomy: Optional[str] = None  # Phase 1 taxonomy id (best-effort)
    guard_categories: Optional[list[str]] = None  # raw S1..S4 codes
    fast_path_score: Optional[float] = None  # tier-1 probability, when computed
    matched_guardrail: Optional[str] = None  # slug of the synthesized rule that fired
    raw: Optional[str] = None


def _format_conversation(message: str, history: Optional[list[ChatMessage]], max_turns: int) -> str:
    lines: list[str] = []
    if history:
        for m in history[-max_turns:]:
            role = "User" if m.role == "user" else "Assistant"
            lines.append(f"{role}: {m.content}")
    lines.append(f"User: {message}")
    return "\n\n".join(lines)


class IntentSieve:
    def __init__(
        self,
        client: Optional[OllamaClient] = None,
        fast_path: Optional[FastPath] = None,
    ) -> None:
        self.settings = get_settings()
        self.client = client or OllamaClient()
        self.fast_path = fast_path or FastPath()

    async def score(
        self,
        message: str,
        history: Optional[list[ChatMessage]] = None,
    ) -> SieveResult:
        # --- TIER 0: synthesized guardrails (~1 ms) — Phase 4 immunity ---
        # A technique captured in the honeypot and turned into a Colang rule is
        # caught here instantly, before any model runs. This is what makes a
        # previously-successful attack fail on replay.
        if self.settings.use_guardrails:
            g_start = time.perf_counter()
            hit = await guardrail_sync.store.match(message)
            if hit is not None:
                return SieveResult(
                    verdict=SieveVerdict.UNSAFE,
                    threat_score=1.0,
                    latency_ms=(time.perf_counter() - g_start) * 1000.0,
                    decided_by="guardrail",
                    matched_taxonomy=hit.taxonomy,
                    matched_guardrail=hit.slug,
                    raw=f"guardrail:{hit.slug} score={hit.score}",
                )

        # --- TIER 1: fast-path classifier (~2 ms) ---
        # Score only the latest message: the fast path is a cheap benign filter,
        # and multi-turn reasoning is the Guard's job (tier 2).
        fast_start = time.perf_counter()
        fast_score = await self.fast_path.score(message)
        if fast_score is not None and fast_score < self.settings.fast_path_safe_threshold:
            fast_latency = (time.perf_counter() - fast_start) * 1000.0
            return SieveResult(
                verdict=SieveVerdict.SAFE,
                threat_score=fast_score,
                latency_ms=fast_latency,
                decided_by="fast_path",
                fast_path_score=fast_score,
            )

        # --- TIER 2: Llama-Guard 3 (authoritative; ~700 ms) ---
        conversation = _format_conversation(message, history, self.settings.sieve_history_turns)
        prompt = sieve_policy.build_guard_prompt(conversation)

        start = time.perf_counter()
        try:
            result = await self.client.generate(
                model=self.settings.sieve_model,
                prompt=prompt,
                raw=True,
                options={"temperature": 0, "num_predict": 20},
                keep_alive=self.settings.ollama_keep_alive,
            )
        except OllamaError as exc:
            latency_ms = (time.perf_counter() - start) * 1000.0
            logger.error("Sieve failed (fail-closed): %s", exc)
            return SieveResult(
                verdict=SieveVerdict.ERROR,
                threat_score=1.0,  # fail-closed: treat as maximally suspicious
                latency_ms=latency_ms,
                decided_by="guard",
                fast_path_score=fast_score,
                raw=str(exc),
            )

        verdict_str, cats = sieve_policy.parse_guard_response(result.text)

        # Unparseable Guard output — fail closed rather than guess.
        if verdict_str == "error":
            logger.warning("Sieve produced unparseable output: %r", result.text[:80])
            return SieveResult(
                verdict=SieveVerdict.ERROR,
                threat_score=1.0,
                latency_ms=result.latency_ms,
                decided_by="guard",
                fast_path_score=fast_score,
                raw=result.text.strip(),
            )

        # OR-ensemble: flag UNSAFE if the Guard says unsafe OR the fast path is
        # highly confident (Step 2.1 — the Guard alone misses ~41% of real
        # in-the-wild jailbreaks that the fast path catches).
        guard_unsafe = verdict_str == "unsafe"
        fastpath_attack = (
            fast_score is not None and fast_score >= self.settings.fast_path_attack_threshold
        )
        if guard_unsafe or fastpath_attack:
            if guard_unsafe:
                taxonomy = sieve_policy.CATEGORY_TO_TAXONOMY.get(cats[0]) if cats else None
                decided_by = "guard"
            else:
                # Fast path caught what the Guard missed; no Guard category.
                taxonomy = None
                decided_by = "fast_path"
            return SieveResult(
                verdict=SieveVerdict.UNSAFE,
                threat_score=max(1.0 if guard_unsafe else 0.0, fast_score or 0.0),
                latency_ms=result.latency_ms,
                decided_by=decided_by,
                matched_taxonomy=taxonomy,
                guard_categories=cats or None,
                fast_path_score=fast_score,
                raw=result.text.strip(),
            )

        # Both tiers agree it is safe.
        return SieveResult(
            verdict=SieveVerdict.SAFE,
            threat_score=fast_score if fast_score is not None else 0.0,
            latency_ms=result.latency_ms,
            decided_by="guard",
            fast_path_score=fast_score,
            raw=result.text.strip(),
        )
