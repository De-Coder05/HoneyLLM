"""/api/chat — the gateway endpoint (Phase 2: sieve + routing live).

Every request now flows: Intent Sieve -> routing decision -> response, with a
forensic log written on every path. The customer-visible `reply` never carries
telemetry — a rerouted attacker sees a normal support reply, no error, no hint
(design.md §1).

Routing:
  SAFE       -> production RAG (public NexTel data only)
  UNSAFE     -> Mirror Maze reroute (Phase 2 stub; Phase 3 = real decoy)
  ERROR/     -> FAIL CLOSED (rules.md §3): never forward to production on a sieve
  unparsed      failure. Return a graceful degraded reply instead.
"""

from __future__ import annotations

import time

from fastapi import APIRouter, Request

from app.core import forensics
from app.core.logging import get_logger
from app.models.schemas import ChatRequest, ChatResponse, SieveVerdict
from app.services.rag import ProductionRag
from app.services.sandbox_router import SandboxRouter
from app.services.sieve import IntentSieve

router = APIRouter(prefix="/api", tags=["chat"])
logger = get_logger(__name__)

# Instantiated once; each holds a stateless OllamaClient wrapper.
_sieve = IntentSieve()
_rag = ProductionRag()
_sandbox = SandboxRouter()

# Sticky quarantine: once a session is flagged, it STAYS in the Mirror Maze even
# if a later message looks benign. A session that flips between the decoy and the
# real bot mid-conversation would itself reveal the security layer. In-memory for
# now; Phase 5's forensic store makes this durable.
_QUARANTINED: set[str] = set()

_DEGRADED_REPLY = (
    "Thanks for contacting NexTel. I'm having a brief issue on my end right now — "
    "please try again in a moment, or I can connect you with a human agent."
)


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, http_request: Request) -> ChatResponse:
    start = time.perf_counter()
    client_ip = http_request.client.host if http_request.client else None

    sieve_result = await _sieve.score(request.message, request.history)
    already_quarantined = request.session_id in _QUARANTINED

    if sieve_result.verdict is SieveVerdict.UNSAFE or already_quarantined:
        # Sticky: flag now (if not already) and keep this session in the maze.
        _QUARANTINED.add(request.session_id)
        sandbox_result = await _sandbox.handle(
            request.message, request.session_id, request.history
        )
        reply = sandbox_result.reply
        routed_to = "mirror_maze"
    elif sieve_result.verdict is SieveVerdict.SAFE:
        rag_result = await _rag.answer(request.message, request.history)
        reply = rag_result.reply
        routed_to = "production"
    else:
        # ERROR / borderline-unhandled -> fail closed. Do NOT reach production.
        reply = _DEGRADED_REPLY
        routed_to = "degraded"

    total_latency_ms = (time.perf_counter() - start) * 1000.0

    forensics.record_event(
        session_id=request.session_id,
        message=request.message,
        verdict=sieve_result.verdict.value,
        threat_score=sieve_result.threat_score,
        routed_to=routed_to,
        decided_by=sieve_result.decided_by,
        matched_taxonomy=sieve_result.matched_taxonomy,
        guard_categories=sieve_result.guard_categories,
        sieve_latency_ms=round(sieve_result.latency_ms, 1),
        total_latency_ms=round(total_latency_ms, 1),
        client_ip=client_ip,
    )
    logger.info(
        "chat session=%s verdict=%s by=%s routed=%s sieve=%.0fms total=%.0fms",
        request.session_id, sieve_result.verdict.value, sieve_result.decided_by,
        routed_to, sieve_result.latency_ms, total_latency_ms,
    )

    return ChatResponse(
        session_id=request.session_id,
        reply=reply,
        verdict=sieve_result.verdict,
        threat_score=sieve_result.threat_score,
        routed_to=routed_to,
        decided_by=sieve_result.decided_by,
        matched_taxonomy=sieve_result.matched_taxonomy,
        matched_guardrail=sieve_result.matched_guardrail,
        latency_ms=round(total_latency_ms, 1),
    )
