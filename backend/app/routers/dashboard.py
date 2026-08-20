"""/api/dashboard — Threat Intelligence Dashboard API (Phase 5).

Serves the aggregates computed by services/analytics.py from the forensic log.
Endpoints are read-only and cheap enough to poll at the <1s dashboard refresh
target. `/overview` is the one-shot payload the dashboard polls; `/events` is the
live feed; `/summary` is kept for backwards compatibility.
"""

from __future__ import annotations

from fastapi import APIRouter, Query

from app.services import analytics

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/overview")
async def overview() -> dict:
    """Everything the dashboard needs in one poll: totals, taxonomy, latency,
    dwell time, tier breakdown, and the attack-frequency time series."""
    return analytics.compute_overview()


@router.get("/events")
async def events(limit: int = Query(default=50, ge=1, le=500)) -> dict:
    return {"events": analytics.recent_events(limit=limit)}


@router.get("/dwell")
async def dwell() -> dict:
    """Measured attacker dwell time (Step 5.3) — validates Phase 3 efficacy."""
    return analytics.compute_dwell_times(analytics.load_events())


@router.get("/summary")
async def summary() -> dict:
    """Backwards-compatible compact summary (superseded by /overview)."""
    ov = analytics.compute_overview()
    return {
        "status": "live",
        "total_requests": ov["totals"]["requests"],
        "attacks_detected": ov["totals"]["attacks_detected"],
        "attack_rate": ov["totals"]["attack_rate"],
        "verdict_breakdown": ov["verdict_breakdown"],
        "routing_breakdown": ov["routing_breakdown"],
        "tier_breakdown": ov["tier_breakdown"],
        "taxonomy_breakdown": {t["taxonomy"]: t["count"] for t in ov["taxonomy_breakdown"]},
    }
