"use client";

/**
 * Admin / Demo Control Panel (Phase 5, supporting). Same dark base as the
 * dashboard, plus the reserved "honey" amber accent used ONLY here (design.md
 * §3) so the control layer is visually distinct from the analyst dashboard.
 *
 * Left: scenario picker (benign + jailbreak-by-taxonomy presets + free text).
 * Right: the sieve's decision path for the last run, in real time.
 * Authenticated (rules.md §4) — the token is sent as X-Admin-Token.
 */

import { useState } from "react";
import {
  getScenarios, runScenario, type Scenario, type DecisionTrace,
} from "@/lib/api";

const HONEY = "#E8A93A";

interface TraceRow { message: string; trace: DecisionTrace }

export default function AdminPage() {
  const [token, setToken] = useState("");
  const [authed, setAuthed] = useState(false);
  const [scenarios, setScenarios] = useState<Record<string, Scenario[]>>({});
  const [custom, setCustom] = useState("");
  const [history, setHistory] = useState<TraceRow[]>([]);
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState<string | null>(null);

  async function authenticate() {
    try {
      const s = await getScenarios(token);
      setScenarios(s); setAuthed(true); setErr(null);
    } catch {
      setErr("Invalid admin token");
    }
  }

  async function run(message: string) {
    if (!message.trim() || busy) return;
    setBusy(true); setErr(null);
    try {
      const res = await runScenario(token, message);
      setHistory((h) => [{ message, trace: res.trace }, ...h].slice(0, 12));
    } catch {
      setErr("Run failed — is the backend up?");
    } finally {
      setBusy(false);
    }
  }

  if (!authed) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-[#0d0d0d] text-white">
        <div className="w-80 rounded-lg border border-white/10 bg-[#1a1a19] p-6">
          <h1 className="text-lg font-semibold">Honey-LLM Control Panel</h1>
          <p className="mt-1 text-xs text-[#898781]">Authenticated surface — enter the admin token.</p>
          <input
            type="password" value={token} onChange={(e) => setToken(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && authenticate()}
            placeholder="admin token"
            className="mt-4 w-full rounded border border-white/10 bg-black/40 px-3 py-2 text-sm outline-none focus:border-[#E8A93A]"
          />
          {err && <p className="mt-2 text-xs text-[#d03b3b]">{err}</p>}
          <button onClick={authenticate}
            className="mt-3 w-full rounded px-3 py-2 text-sm font-medium text-black"
            style={{ backgroundColor: HONEY }}>Unlock</button>
        </div>
      </main>
    );
  }

  const last = history[0];

  return (
    <main className="min-h-screen bg-[#0d0d0d] p-5 text-white">
      <header className="mb-5">
        <h1 className="inline-block text-lg font-semibold" style={{ borderBottom: `2px solid ${HONEY}`, paddingBottom: 4 }}>
          Honey-LLM · Control Panel
        </h1>
        <span className="ml-3 text-xs text-[#898781]">drive a scenario, watch the sieve decide</span>
      </header>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        {/* Left: scenario picker */}
        <div className="space-y-4">
          <Section title="Benign scenarios">
            <div className="grid grid-cols-1 gap-2">
              {(scenarios.benign ?? []).map((s) => (
                <ScenarioButton key={s.label} s={s} onClick={() => run(s.prompt)} disabled={busy} />
              ))}
            </div>
          </Section>
          <Section title="Attack scenarios (by taxonomy)">
            <div className="grid grid-cols-1 gap-2">
              {(scenarios.attack ?? []).map((s) => (
                <ScenarioButton key={s.label} s={s} onClick={() => run(s.prompt)} disabled={busy} attack />
              ))}
            </div>
          </Section>
          <Section title="Custom prompt">
            <textarea value={custom} onChange={(e) => setCustom(e.target.value)}
              placeholder="Type any prompt to run through the sieve…"
              className="h-20 w-full resize-none rounded border border-white/10 bg-black/40 px-3 py-2 text-sm outline-none focus:border-[#E8A93A]" />
            <button onClick={() => run(custom)} disabled={busy || !custom.trim()}
              className="mt-2 rounded px-4 py-2 text-sm font-medium text-black disabled:opacity-40"
              style={{ backgroundColor: HONEY }}>
              {busy ? "Running…" : "Run through sieve"}
            </button>
          </Section>
          {err && <p className="text-xs text-[#d03b3b]">{err}</p>}
        </div>

        {/* Right: live decision trace */}
        <div className="space-y-4">
          <Section title="Decision path (latest)">
            {last ? <Trace row={last} /> : <p className="py-8 text-center text-xs text-[#898781]">Run a scenario to see the sieve's decision.</p>}
          </Section>
          <Section title="Recent runs">
            <div className="space-y-1">
              {history.slice(1).map((r, i) => (
                <div key={i} className="flex items-center justify-between text-xs">
                  <span className="max-w-[60%] truncate text-[#898781]">{r.message}</span>
                  <span className="flex items-center gap-2">
                    <Verdict v={r.trace.verdict} />
                    <span className="text-[#898781]">{r.trace.decided_by}</span>
                  </span>
                </div>
              ))}
            </div>
          </Section>
        </div>
      </div>
    </main>
  );
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="rounded-lg border border-white/10 bg-[#1a1a19] p-4">
      <h3 className="mb-3 text-[11px] font-semibold uppercase tracking-wider text-[#898781]">{title}</h3>
      {children}
    </div>
  );
}

function ScenarioButton({ s, onClick, disabled, attack }: { s: Scenario; onClick: () => void; disabled: boolean; attack?: boolean }) {
  return (
    <button onClick={onClick} disabled={disabled}
      className="flex items-center justify-between rounded border border-white/10 bg-black/30 px-3 py-2 text-left text-sm hover:border-[#E8A93A]/60 disabled:opacity-40">
      <span>{s.label}</span>
      {attack && s.taxonomy && <span className="font-mono text-[10px] text-[#898781]">{s.taxonomy}</span>}
    </button>
  );
}

function Verdict({ v }: { v: string }) {
  const color = v === "unsafe" ? "#ec835a" : v === "safe" ? "#0ca30c" : "#fab219";
  const label = v === "unsafe" ? "attack" : v === "safe" ? "benign" : v;
  return <span className="rounded px-1.5 py-0.5 text-[11px] font-medium" style={{ color, backgroundColor: color + "1a" }}>{label}</span>;
}

function Trace({ row }: { row: TraceRow }) {
  const t = row.trace;
  const steps = [
    { k: "Guardrail (tier 0)", hit: t.decided_by === "guardrail", detail: t.matched_guardrail ?? "no match" },
    { k: "Fast-path (tier 1)", hit: t.decided_by === "fast_path", detail: t.fast_path_score != null ? `score ${t.fast_path_score.toFixed(3)}` : "—" },
    { k: "Guard (tier 2)", hit: t.decided_by === "guard", detail: t.guard_categories?.length ? t.guard_categories.join(",") : "8B Llama-Guard" },
  ];
  return (
    <div>
      <p className="mb-3 rounded bg-black/30 px-3 py-2 text-sm text-[#c3c2b7]">{row.message}</p>
      <div className="space-y-2">
        {steps.map((s) => (
          <div key={s.k} className={`flex items-center justify-between rounded border px-3 py-2 text-xs ${s.hit ? "border-[#E8A93A]/60 bg-[#E8A93A]/10" : "border-white/10"}`}>
            <span className={s.hit ? "font-medium text-white" : "text-[#898781]"}>
              {s.hit ? "▶ " : ""}{s.k}
            </span>
            <span className="font-mono text-[#898781]">{s.detail}</span>
          </div>
        ))}
      </div>
      <div className="mt-3 grid grid-cols-2 gap-2 text-xs">
        <Field label="Verdict"><Verdict v={t.verdict} /></Field>
        <Field label="Routed to"><span className="font-mono text-[#c3c2b7]">{t.routed_to}</span></Field>
        <Field label="Taxonomy"><span className="text-[#c3c2b7]">{t.matched_taxonomy ?? "—"}</span></Field>
        <Field label="Sieve latency"><span className="font-mono tabular-nums text-[#c3c2b7]">{t.sieve_latency_ms} ms</span></Field>
      </div>
    </div>
  );
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="rounded border border-white/10 px-2 py-1.5">
      <div className="text-[10px] uppercase tracking-wider text-[#898781]">{label}</div>
      <div className="mt-0.5">{children}</div>
    </div>
  );
}
