"""Forensic logging — append-only JSONL of every sieve decision.

rules.md §2: every rerouted session must be logged with enough metadata to feed
the dashboard and the guardrail-synthesis pipeline. rules.md §3: a logging
failure must NEVER block the chat path — so writes are best-effort and swallow
their own errors (logged, not raised).

Phase 2 writes here; Phase 5 builds the real store + dashboard on top. Both safe
and unsafe decisions are recorded (not just attacks) so benign/attack ratios and
false-positive review are possible later.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)


def _log_path() -> Path:
    return Path(get_settings().forensic_log_path)


def record_event(
    *,
    session_id: str,
    message: str,
    verdict: str,
    threat_score: Optional[float],
    routed_to: str,
    decided_by: Optional[str],
    matched_taxonomy: Optional[str],
    guard_categories: Optional[list[str]],
    sieve_latency_ms: Optional[float],
    total_latency_ms: Optional[float],
    client_ip: Optional[str],
) -> None:
    """Append one event. Best-effort: never raises to the caller."""
    event: dict[str, Any] = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "session_id": session_id,
        # Store the prompt for guardrail synthesis (Phase 4) and review. This is
        # synthetic-demo data; a real deployment would apply retention/PII rules.
        "message": message,
        "verdict": verdict,
        "threat_score": threat_score,
        "routed_to": routed_to,
        "decided_by": decided_by,
        "matched_taxonomy": matched_taxonomy,
        "guard_categories": guard_categories,
        "sieve_latency_ms": sieve_latency_ms,
        "total_latency_ms": total_latency_ms,
        "client_ip": client_ip,
    }
    try:
        with _log_path().open("a", encoding="utf-8") as f:
            f.write(json.dumps(event) + "\n")
    except OSError as exc:  # disk full, permissions, etc. — degrade observability only
        logger.error("Forensic log write failed (non-blocking): %s", exc)
