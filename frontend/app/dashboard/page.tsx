"use client";

/**
 * Threat Intelligence Dashboard (Phase 5, Step 5.2). Dark SOC aesthetic
 * (design.md §2). Polls /overview + /events every second — the <1s refresh
 * target (PRD §8). Every number here is derived from the forensic log, so it is
 * reconcilable against the raw log (an exit criterion).
 */

import { useEffect, useRef, useState } from "react";
import {
  getOverview, getEvents, type Overview, type FeedEvent,
} from "@/lib/api";
import {
  Card, StatTile, StatusChip, TimeSeries, TaxonomyBars, TierBar, DwellMeter, fmtDuration,
} from "@/components/soc";

const REFRESH_MS = 1000;

export default function DashboardPage() {
  const [ov, setOv] = useState<Overview | null>(null);
  const [events, setEvents] = useState<FeedEvent[]>([]);
  const [live, setLive] = useState(true);
  const [err, setErr] = useState<string | null>(null);
  const liveRef = useRef(live);
  liveRef.current = live;

  useEffect(() => {
    let stop = false;
    async function tick() {
      if (liveRef.current) {
        try {
          const [o, e] = await Promise.all([getOverview(), getEvents(40)]);
          if (!stop) { setOv(o); setEvents(e); setErr(null); }
        } catch {
          if (!stop) setErr("backend unreachable");
        }
      }
      if (!stop) setTimeout(tick, REFRESH_MS);
    }
    tick();
    return () => { stop = true; };
  }, []);

  const t = ov?.totals;
  const attackRate = t?.attack_rate != null ? `${(t.attack_rate * 100).toFixed(0)}%` : "—";
  const lat = ov?.latency.overall_p50_ms;

  return (
    <main className="min-h-screen bg-[#0d0d0d] p-5 text-white">
      {/* Header */}
      <header className="mb-5 flex items-center justify-between">
        <div className="flex items-baseline gap-3">
          <h1 className="text-lg font-semibold">Honey-LLM</h1>
          <span className="text-sm text-[#898781]">· Threat Intelligence</span>
        </div>
        <div className="flex items-center gap-3 text-xs text-[#898781]">
          {err ? (
            <span className="text-[#d03b3b]">● {err}</span>
          ) : (
            <button onClick={() => setLive((v) => !v)} className="inline-flex items-center gap-1.5">
              <span className={`inline-block h-2 w-2 rounded-full ${live ? "animate-pulse bg-[#0ca30c]" : "bg-[#898781]"}`} />
              {live ? "LIVE · auto-refresh 1s" : "PAUSED"}
            </button>
          )}
          {ov && <span className="font-mono tabular-nums">{new Date(ov.generated_at).toLocaleTimeString()}</span>}
        </div>
      </header>

      {/* Stat tiles */}
      <div className="mb-5 grid grid-cols-2 gap-3 md:grid-cols-5">
        <StatTile label="Total Requests" value={t ? String(t.requests) : "—"} />
        <StatTile label="Attacks Detected" value={t ? String(t.attacks_detected) : "—"} accent="#ec835a"
          sub={t ? `${t.benign} benign` : undefined} />
        <StatTile label="Attack Rate" value={attackRate} />
        <StatTile label="Avg Dwell Time" value={ov ? fmtDuration(ov.dwell.avg_dwell_seconds) : "—"}
          sub={ov ? `${ov.dwell.captured_sessions} sessions` : undefined} />
        <StatTile label="Sieve Latency p50" value={lat != null ? `${lat.toFixed(0)} ms` : "—"}
          sub={ov?.latency.overall_p95_ms != null ? `p95 ${ov.latency.overall_p95_ms.toFixed(0)} ms` : undefined} />
      </div>

      {/* Charts row */}
      <div className="mb-5 grid grid-cols-1 gap-3 lg:grid-cols-2">
        <Card title="Attack Frequency">
          <TimeSeries data={ov?.timeseries ?? []} />
        </Card>
        <Card title="Attack Taxonomy">
          <TaxonomyBars data={ov?.taxonomy_breakdown ?? []} />
        </Card>
      </div>

      {/* Tier + dwell row */}
      <div className="mb-5 grid grid-cols-1 gap-3 lg:grid-cols-2">
        <Card title="Sieve Tier — which stage decided">
          <TierBar breakdown={ov?.tier_breakdown ?? {}} />
          <div className="mt-3 flex gap-4 text-xs text-[#898781]">
            {ov && Object.entries(ov.latency.by_tier).map(([tier, v]) => (
              <span key={tier} className="font-mono tabular-nums">
                {tier}: {v.p50_ms != null ? `${v.p50_ms}ms` : "—"}
              </span>
            ))}
          </div>
        </Card>
        <Card title="Attacker Dwell Time">
          <DwellMeter avg={ov?.dwell.avg_dwell_seconds ?? 0} target={ov?.dwell.target_seconds ?? 300} />
          <div className="mt-3 max-h-24 space-y-1 overflow-y-auto">
            {(ov?.dwell.sessions ?? []).filter((s) => s.dwell_seconds > 0).map((s) => (
              <div key={s.session_id} className="flex items-center justify-between text-xs">
                <span className="font-mono text-[#c3c2b7]">{s.session_id}</span>
                <span className="text-[#898781]">
                  <span className="font-mono tabular-nums">{s.turns_in_maze}</span> turns ·
                  <span className="font-mono tabular-nums text-[#c3c2b7]"> {fmtDuration(s.dwell_seconds)}</span>
                </span>
              </div>
            ))}
          </div>
        </Card>
      </div>

      {/* Live event feed */}
      <Card title="Live Event Feed">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="text-[#898781]">
              <tr className="border-b border-white/10">
                <th className="py-1.5 pr-3 font-medium">Time</th>
                <th className="py-1.5 pr-3 font-medium">Session</th>
                <th className="py-1.5 pr-3 font-medium">Verdict</th>
                <th className="py-1.5 pr-3 font-medium">Taxonomy</th>
                <th className="py-1.5 pr-3 font-medium">Tier</th>
                <th className="py-1.5 pr-3 text-right font-medium">Latency</th>
                <th className="py-1.5 pr-3 font-medium">Origin</th>
                <th className="py-1.5 font-medium">Prompt</th>
              </tr>
            </thead>
            <tbody>
              {events.map((e, i) => (
                <tr key={i} className="border-b border-white/5">
                  <td className="py-1.5 pr-3 font-mono tabular-nums text-[#898781]">
                    {e.ts ? new Date(e.ts).toLocaleTimeString() : "—"}
                  </td>
                  <td className="py-1.5 pr-3 font-mono text-[#c3c2b7]">{e.session_id}</td>
                  <td className="py-1.5 pr-3">
                    {e.verdict === "unsafe"
                      ? <StatusChip kind="serious" label="attack" />
                      : e.verdict === "safe"
                        ? <StatusChip kind="good" label="benign" />
                        : <StatusChip kind="warning" label={e.verdict} />}
                  </td>
                  <td className="py-1.5 pr-3 text-[#c3c2b7]">{e.taxonomy ?? "—"}</td>
                  <td className="py-1.5 pr-3 text-[#c3c2b7]">{e.decided_by}</td>
                  <td className="py-1.5 pr-3 text-right font-mono tabular-nums text-[#c3c2b7]">
                    {e.sieve_latency_ms != null ? `${Math.round(e.sieve_latency_ms)}ms` : "—"}
                  </td>
                  <td className="py-1.5 pr-3 font-mono text-[#898781]">{e.client_ip ?? "—"}</td>
                  <td className="py-1.5 max-w-[240px] truncate text-[#898781]">{e.prompt_preview}</td>
                </tr>
              ))}
              {events.length === 0 && (
                <tr><td colSpan={8} className="py-6 text-center text-[#898781]">No events yet — send traffic to /chat</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </Card>
    </main>
  );
}
