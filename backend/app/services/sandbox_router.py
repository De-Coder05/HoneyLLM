"""Mirror Maze — LLM-driven decoy ("Sarah").

Phase 3, Steps 3.2 (persona) + 3.3 (bait). A flagged attacker is rerouted here
instead of getting a hard failure. The decoy runs Llama-3 with the "Sarah"
persona (sandbox/persona/sarah_prompt.md), seeded ONLY with the synthetic bait
from the INTERNAL section of the source of truth. It produces varied, believable
responses that leak fake secrets to waste the attacker's time and capture their
technique (PRD §5). Every value it can leak is synthetic and non-functional
(rules.md §2).

*** ISOLATION CAVEAT (Step 3.1 still pending) ***
This runs in the SAME process as the gateway today — there is NO Docker
zero-egress boundary yet (Docker isn't installed). That hard boundary is the
project's core safety guarantee (Architecture §5) and MUST be built before this
is anything but a local demo. It is safe as a demo only because the decoy is
given exclusively synthetic bait and has no handle to real data (there is none;
all NexTel data is synthetic). Do not treat the current setup as isolated.
"""

from __future__ import annotations

import re
import time
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Optional

import httpx

from app.core.config import get_settings
from app.core.logging import get_logger
from app.models.schemas import ChatMessage
from app.services.ollama_client import OllamaClient, OllamaError

logger = get_logger(__name__)

_SOURCE_OF_TRUTH = Path(__file__).resolve().parents[3] / "data" / "nextel_source_of_truth.md"
_PERSONA_FILE = Path(__file__).resolve().parents[3] / "sandbox" / "persona" / "sarah_prompt.md"


@dataclass
class SandboxResult:
    reply: str
    latency_ms: float


@lru_cache
def load_internal_bait() -> str:
    """The INTERNAL bait block — the ONLY knowledge the decoy is seeded with.
    Mirror of rag.load_public_context but for the honey. Comment-wrapped markers
    only (the header legend uses bare tokens)."""
    text = _SOURCE_OF_TRUTH.read_text(encoding="utf-8")
    m = re.search(
        r"<!--\s*\[\[INTERNAL-START\]\]\s*-->(.*?)<!--\s*\[\[INTERNAL-END\]\]\s*-->",
        text,
        re.DOTALL,
    )
    if not m:
        raise RuntimeError(f"INTERNAL markers not found in {_SOURCE_OF_TRUTH}")
    # Strip the internal HTML comments so only the bait bullet list remains.
    block = re.sub(r"<!--.*?-->", "", m.group(1), flags=re.DOTALL)
    return block.strip()


@lru_cache
def load_persona_template() -> str:
    """Everything after the '## SYSTEM PROMPT' marker — contains {internal_context}."""
    text = _PERSONA_FILE.read_text(encoding="utf-8")
    marker = "## SYSTEM PROMPT (rendered to the model)"
    idx = text.find(marker)
    if idx == -1:
        raise RuntimeError(f"SYSTEM PROMPT marker not found in {_PERSONA_FILE}")
    return text[idx + len(marker):].strip()


class SandboxRouter:
    def __init__(self, client: Optional[OllamaClient] = None) -> None:
        self.settings = get_settings()
        self.client = client or OllamaClient()

    def _system_prompt(self) -> str:
        # Public data lets the decoy answer normal questions and generalize;
        # internal bait is leaked only when asked (the persona enforces that).
        from app.services.rag import load_public_context

        return (
            load_persona_template()
            .replace("{public_context}", load_public_context())
            .replace("{internal_context}", load_internal_bait())
        )

    async def handle(
        self,
        message: str,
        session_id: str,
        history: Optional[list[ChatMessage]] = None,
    ) -> SandboxResult:
        # Prefer the ISOLATED container decoy when configured (Step 3.1). Fall
        # back to in-process generation if it is unreachable, so the demo never
        # breaks when Docker is down.
        if self.settings.decoy_service_url:
            try:
                return await self._handle_via_container(message, history)
            except (httpx.HTTPError, ValueError) as exc:
                logger.warning("Decoy container unreachable (%s); using in-process fallback.", exc)

        return await self._handle_in_process(message, history)

    async def _handle_via_container(
        self, message: str, history: Optional[list[ChatMessage]]
    ) -> SandboxResult:
        payload = {
            "message": message,
            "history": [{"role": m.role, "content": m.content} for m in (history or [])],
        }
        url = self.settings.decoy_service_url.rstrip("/") + "/decoy"
        async with httpx.AsyncClient(timeout=self.settings.decoy_service_timeout_s) as client:
            resp = await client.post(url, json=payload)
            resp.raise_for_status()
            data = resp.json()
        return SandboxResult(reply=data.get("reply", "").strip(), latency_ms=data.get("latency_ms", 0.0))

    async def _handle_in_process(
        self, message: str, history: Optional[list[ChatMessage]]
    ) -> SandboxResult:
        messages: list[dict] = [{"role": "system", "content": self._system_prompt()}]
        if history:
            # Carry the prior exchange so the decoy conversation stays coherent
            # across turns (the deception must hold multi-turn).
            for m in history[-8:]:
                messages.append({"role": m.role, "content": m.content})
        messages.append({"role": "user", "content": message})

        start = time.perf_counter()
        try:
            result = await self.client.chat(
                model=self.settings.decoy_model,
                messages=messages,
                # Higher temperature for varied, human-sounding replies (so the
                # decoy is not detectable by identical responses).
                options={"temperature": 0.85, "top_p": 0.95},
                keep_alive=self.settings.ollama_keep_alive,
            )
        except OllamaError as exc:
            latency_ms = (time.perf_counter() - start) * 1000.0
            logger.error("Decoy generation failed: %s", exc)
            # Stay in character even on failure — never emit an error that hints
            # at the security layer.
            return SandboxResult(
                reply="Sorry, my console's lagging a bit — what were you trying to pull up?",
                latency_ms=latency_ms,
            )
        return SandboxResult(reply=result.text.strip(), latency_ms=result.latency_ms)
