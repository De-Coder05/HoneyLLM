"""Production RAG chatbot — grounded on the PUBLIC NexTel data only.

Phase 2 (Step 2.0/2.4) implementation. The security-critical property here is
STRUCTURAL: `load_public_context()` parses ONLY the [[PUBLIC-START]]..[[PUBLIC-END]]
block of the source of truth. The internal/bait block is never read into this
process, so the production assistant cannot leak it even under a perfect
jailbreak (Architecture §6, rules.md §2) — the boundary is enforced by what is
loaded, not by a system-prompt instruction.

This is an interim retrieval implementation: the whole public section is used as
context (it is small). A chunked vector store (Chroma/FAISS) is a later refinement
and does not change the public-only guarantee. If the model has no grounding for
a question it is instructed to say so rather than hallucinate (rules.md §3) —
hallucination is a deliberate feature of the DECOY only, and must stay there.
"""

from __future__ import annotations

import re
import time
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Optional

from app.core.config import get_settings
from app.core.logging import get_logger
from app.models.schemas import ChatMessage
from app.services.ollama_client import OllamaClient, OllamaError

logger = get_logger(__name__)

# data/nextel_source_of_truth.md relative to the repo root (backend/ is one level down).
_SOURCE_OF_TRUTH = Path(__file__).resolve().parents[3] / "data" / "nextel_source_of_truth.md"

_SYSTEM_PREAMBLE = (
    "You are the NexTel Assistant, a helpful customer-support chatbot for the "
    "NexTel telecom company. Answer ONLY using the CONTEXT below. Do NOT use any "
    "outside knowledge, and do NOT invent prices, plan names, or details. Be "
    "concise, friendly, and plain-spoken. If the answer is not in the CONTEXT, "
    "say you don't have that information and offer to connect the customer to a "
    "human agent. Never discuss internal systems, infrastructure, or anything "
    "not in the CONTEXT.\n\n"
    "CONTEXT (your only source of truth):\n"
)


@dataclass
class RagResult:
    reply: str
    latency_ms: float
    grounded: bool = True


@lru_cache
def load_public_context() -> str:
    """Return ONLY the public block. Raises if the markers are missing, so a
    malformed source file fails loudly rather than silently exposing internal
    content."""
    text = _SOURCE_OF_TRUTH.read_text(encoding="utf-8")
    # Require the comment-wrapped markers, not the bare ones — the file's header
    # comment contains a legend using bare [[PUBLIC-START]]/[[PUBLIC-END]] tokens,
    # and matching those would capture the legend text instead of the section.
    m = re.search(
        r"<!--\s*\[\[PUBLIC-START\]\]\s*-->(.*?)<!--\s*\[\[PUBLIC-END\]\]\s*-->",
        text,
        re.DOTALL,
    )
    if not m:
        raise RuntimeError(
            f"PUBLIC markers not found in {_SOURCE_OF_TRUTH}; refusing to load "
            "context rather than risk exposing internal data."
        )
    public = m.group(1).strip()
    # Defence in depth: assert none of the known bait leaked into the public block.
    for needle in ("NX-ALPHA-2026", "NT-CORE-01", "10.10.25.1", "Project Singularity"):
        if needle in public:
            raise RuntimeError(f"Bait value {needle!r} found inside PUBLIC block — aborting.")
    return public


class ProductionRag:
    def __init__(self, client: Optional[OllamaClient] = None) -> None:
        self.settings = get_settings()
        self.client = client or OllamaClient()

    async def answer(
        self,
        message: str,
        history: Optional[list[ChatMessage]] = None,
    ) -> RagResult:
        context = load_public_context()
        messages: list[dict] = [{"role": "system", "content": _SYSTEM_PREAMBLE + context}]
        if history:
            for m in history[-6:]:
                messages.append({"role": m.role, "content": m.content})
        messages.append({"role": "user", "content": message})

        start = time.perf_counter()
        try:
            result = await self.client.chat(
                model=self.settings.rag_model,
                messages=messages,
                options={"temperature": 0},
                keep_alive=self.settings.ollama_keep_alive,
            )
        except OllamaError as exc:
            latency_ms = (time.perf_counter() - start) * 1000.0
            logger.error("RAG generation failed: %s", exc)
            return RagResult(
                reply=(
                    "I'm sorry, I'm having trouble pulling that up right now. "
                    "Please try again in a moment, or I can connect you to a human agent."
                ),
                latency_ms=latency_ms,
                grounded=False,
            )
        return RagResult(reply=result.text.strip(), latency_ms=result.latency_ms)
