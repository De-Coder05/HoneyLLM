"""Pydantic schemas — the validated boundary for every request/response.

rules.md §3: "Validate at the boundary (Pydantic schemas in FastAPI) — don't
pass unvalidated user input directly into prompts, container calls, or DB
queries."

These schemas are deliberately forward-looking: the fields the Intent Sieve
(Phase 2) and routing layer will populate already exist as Optional, so wiring
them in later does not change the public contract the frontend depends on.
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class HealthResponse(BaseModel):
    status: str = "ok"
    app: str
    environment: str
    version: str


class OllamaHealth(BaseModel):
    reachable: bool
    base_url: str
    models_available: list[str] = Field(default_factory=list)
    sieve_model_present: bool = False
    rag_model_present: bool = False
    detail: Optional[str] = None


class ChatMessage(BaseModel):
    role: str  # "user" | "assistant"
    content: str = Field(min_length=1, max_length=8000)


class ChatRequest(BaseModel):
    """A single turn from the NexTel chat widget.

    `session_id` and `history` exist now (unused in Phase 0/1) because the sieve
    must be able to score multi-turn persistence attacks, not just the latest
    message in isolation (rules.md §2). The frontend contract is fixed from the
    start so Phase 2 doesn't force a breaking change.
    """

    session_id: str = Field(min_length=1, max_length=128)
    message: str = Field(min_length=1, max_length=8000)
    history: list[ChatMessage] = Field(default_factory=list)


class SieveVerdict(str, Enum):
    """Routing verdicts from the Intent Sieve.

    BORDERLINE is a first-class outcome, not a rounding of SAFE/UNSAFE — the
    middle band gets its own documented behavior (rules.md §3). ERROR exists so
    the sieve can fail *closed* (never silently forward to production).
    """

    SAFE = "safe"
    BORDERLINE = "borderline"
    UNSAFE = "unsafe"
    ERROR = "error"


class ChatResponse(BaseModel):
    session_id: str
    reply: str
    # Telemetry fields — populated starting Phase 2. Kept out of the user-
    # visible reply; the customer must never see the security layer (design.md).
    verdict: Optional[SieveVerdict] = None
    threat_score: Optional[float] = None
    routed_to: Optional[str] = None  # "production" | "mirror_maze" (Phase 2/3)
    decided_by: Optional[str] = None  # "guardrail" | "fast_path" | "guard"
    matched_taxonomy: Optional[str] = None  # Phase 1 taxonomy id (admin trace)
    matched_guardrail: Optional[str] = None  # synthesized rule slug (admin trace)
    latency_ms: Optional[float] = None
    timestamp: datetime = Field(default_factory=_utcnow)
