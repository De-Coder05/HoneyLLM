"""Phase 5 — Forensic telemetry analytics.

Reads the append-only forensic log and computes everything the Threat
Intelligence Dashboard needs, including the MEASURED (not estimated) attacker
dwell time (Step 5.3). Aggregates are computed on read — fine at capstone scale
(a JSONL scan is sub-millisecond for thousands of events); a real deployment
would back this with the DB in Architecture §3.

All metrics are derived from the same log the gateway writes on every request,
so the dashboard numbers are reconcilable against the raw log (an exit criterion).
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Optional

from app.core.config import get_settings

# Phase-1 taxonomy id -> fixed categorical colour (design.md §2 / threat_taxonomy.md).
# Colour follows the entity, never its rank, so the mapping is frozen here.
TAXONOMY_COLORS: dict[str, str] = {
    "direct-override": "#3987e5",        # 1 blue
    "role-play-hijack": "#199e70",       # 2 aqua
    "payload-splitting": "#c98500",      # 3 yellow
    "data-exfiltration": "#008300",      # 4 green
    "multi-turn-persistence": "#9085e9", # 5 violet
    "authority-spoofing": "#e66767",     # 6 red
    "refusal-suppression": "#b46ad0",    # 7 orchid (was #d55181; failed CVD validator)
    "indirect-injection": "#d95926",     # 8 orange
}
_OTHER_COLOR = "#898781"


def _log_path() -> Path:
    return Path(get_settings().forensic_log_path)


def load_events(log_path: Optional[Path] = None) -> list[dict]:
    path = log_path or _log_path()
    events: list[dict] = []
    if not path.exists():
        return events
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return events


def _pctl(values: list[float], p: float) -> Optional[float]:
    if not values:
        return None
    v = sorted(values)
    if len(v) == 1:
        return round(v[0], 1)
    k = (len(v) - 1) * p
    lo = int(k)
    hi = min(lo + 1, len(v) - 1)
    return round(v[lo] + (v[hi] - v[lo]) * (k - lo), 1)


def _parse_ts(s: Optional[str]) -> Optional[datetime]:
    if not s:
        return None
    try:
        return datetime.fromisoformat(s)
    except ValueError:
        return None


def compute_dwell_times(events: list[dict]) -> dict:
    """Dwell time = seconds an attacker keeps engaging AFTER first being trapped
    in the Mirror Maze. Measured from logged timestamps, per quarantined session.

    Validates the Phase 3 deception-efficacy claim (PRD §8: 5-10 min target).
    """
    by_session: dict[str, list[dict]] = defaultdict(list)
    for e in events:
        if e.get("routed_to") == "mirror_maze":
            by_session[e.get("session_id", "?")].append(e)

    sessions = []
    for sid, evs in by_session.items():
        ts = sorted(t for t in (_parse_ts(e.get("ts")) for e in evs) if t)
        if not ts:
            continue
        dwell_s = (ts[-1] - ts[0]).total_seconds()
        taxonomy = next((e.get("matched_taxonomy") for e in evs if e.get("matched_taxonomy")), None)
        sessions.append({
            "session_id": sid,
            "turns_in_maze": len(evs),
            "dwell_seconds": round(dwell_s, 1),
            "first_seen": ts[0].isoformat(),
            "last_seen": ts[-1].isoformat(),
            "taxonomy": taxonomy,
        })

    dwell_values = [s["dwell_seconds"] for s in sessions]
    multi = [v for v in dwell_values if v > 0]  # single-turn sessions have 0 dwell
    return {
        "captured_sessions": len(sessions),
        "avg_dwell_seconds": round(sum(multi) / len(multi), 1) if multi else 0.0,
        "median_dwell_seconds": _pctl(multi, 0.5) if multi else 0.0,
        "max_dwell_seconds": round(max(dwell_values), 1) if dwell_values else 0.0,
        "avg_turns_in_maze": round(sum(s["turns_in_maze"] for s in sessions) / len(sessions), 1) if sessions else 0.0,
        "target_seconds": 300,  # PRD §8 lower bound (5 min)
        "sessions": sorted(sessions, key=lambda s: s["last_seen"], reverse=True)[:20],
    }


def compute_timeseries(events: list[dict], buckets: int = 20) -> list[dict]:
    """Attack frequency over time: safe vs unsafe counts in equal time buckets
    spanning the log. Single axis (counts), per design.md chart rules."""
    ts_events = [(t, e) for e in events if (t := _parse_ts(e.get("ts")))]
    if not ts_events:
        return []
    ts_events.sort(key=lambda x: x[0])
    t0, t1 = ts_events[0][0], ts_events[-1][0]
    span = (t1 - t0).total_seconds() or 1.0
    width = span / buckets
    series = [{"bucket": i, "safe": 0, "unsafe": 0} for i in range(buckets)]
    for t, e in ts_events:
        idx = min(int((t - t0).total_seconds() / width), buckets - 1)
        if e.get("verdict") == "unsafe":
            series[idx]["unsafe"] += 1
        else:
            series[idx]["safe"] += 1
    for i, b in enumerate(series):
        b["t"] = (t0.timestamp() + i * width)
    return series


def compute_overview(events: Optional[list[dict]] = None) -> dict:
    events = events if events is not None else load_events()
    total = len(events)

    verdicts = Counter(e.get("verdict") for e in events)
    routing = Counter(e.get("routed_to") for e in events)
    tiers = Counter(e.get("decided_by") for e in events if e.get("decided_by"))
    attacks = verdicts.get("unsafe", 0)

    taxonomy = Counter(e.get("matched_taxonomy") for e in events if e.get("matched_taxonomy"))
    taxonomy_breakdown = [
        {"taxonomy": k, "count": v, "color": TAXONOMY_COLORS.get(k, _OTHER_COLOR)}
        for k, v in taxonomy.most_common()
    ]

    def _lat(tier: Optional[str]) -> list[float]:
        return [e["sieve_latency_ms"] for e in events
                if e.get("sieve_latency_ms") is not None
                and (tier is None or e.get("decided_by") == tier)]

    latency = {
        "overall_p50_ms": _pctl(_lat(None), 0.5),
        "overall_p95_ms": _pctl(_lat(None), 0.95),
        "by_tier": {
            t: {"p50_ms": _pctl(_lat(t), 0.5), "count": len(_lat(t))}
            for t in ("guardrail", "fast_path", "guard")
        },
    }

    return {
        "generated_at": datetime.now().astimezone().isoformat(),
        "totals": {
            "requests": total,
            "attacks_detected": attacks,
            "benign": verdicts.get("safe", 0),
            "attack_rate": round(attacks / total, 3) if total else None,
        },
        "verdict_breakdown": dict(verdicts),
        "routing_breakdown": dict(routing),
        "tier_breakdown": dict(tiers),
        "taxonomy_breakdown": taxonomy_breakdown,
        "latency": latency,
        "dwell": compute_dwell_times(events),
        "timeseries": compute_timeseries(events),
    }


def recent_events(limit: int = 50, events: Optional[list[dict]] = None) -> list[dict]:
    """Latest events for the live feed — redacted to what the SOC view shows."""
    events = events if events is not None else load_events()
    out = []
    for e in events[-limit:][::-1]:
        msg = e.get("message", "") or ""
        out.append({
            "ts": e.get("ts"),
            "session_id": e.get("session_id"),
            "verdict": e.get("verdict"),
            "routed_to": e.get("routed_to"),
            "decided_by": e.get("decided_by"),
            "taxonomy": e.get("matched_taxonomy"),
            "matched_guardrail": e.get("matched_guardrail"),
            "threat_score": e.get("threat_score"),
            "sieve_latency_ms": e.get("sieve_latency_ms"),
            "client_ip": e.get("client_ip"),
            "prompt_preview": (msg[:120] + "…") if len(msg) > 120 else msg,
        })
    return out
