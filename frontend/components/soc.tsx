/**
 * SOC dashboard primitives (Phase 5). Dark, dense, legible (design.md §2).
 * Charts follow the dataviz mark specs: thin marks, 2px surface gaps between
 * stacked/adjacent segments, a legend for >=2 series, direct value labels,
 * recessive gridlines, status colors always with an icon + text label, and
 * mono tabular-nums for every technical value.
 */

const SOC = {
  card: "#1a1a19", ink: "#ffffff", ink2: "#c3c2b7", muted: "#898781",
  grid: "#2c2c2a", axis: "#383835",
  good: "#0ca30c", warning: "#fab219", serious: "#ec835a", critical: "#d03b3b",
} as const;

// Sequential blue ramp (design.md §2) — used for the tier breakdown (a magnitude:
// cheap fast-path -> expensive Guard), so categorical taxonomy hues stay reserved.
const TIER_COLORS: Record<string, string> = {
  fast_path: "#86b6ef",
  guardrail: "#3987e5",
  guard: "#184f95",
  degraded: "#898781",
};
const TIER_LABELS: Record<string, string> = {
  fast_path: "Fast-path", guardrail: "Guardrail", guard: "Guard", degraded: "Degraded",
};

export function fmtDuration(sec: number): string {
  if (!sec || sec < 1) return "0s";
  const m = Math.floor(sec / 60);
  const s = Math.round(sec % 60);
  return m > 0 ? `${m}m ${s}s` : `${s}s`;
}

export function Card({ title, children, className = "" }: { title?: string; children: React.ReactNode; className?: string }) {
  return (
    <div className={`rounded-lg border border-white/10 bg-[#1a1a19] p-4 ${className}`}>
      {title && <h3 className="mb-3 text-[11px] font-semibold uppercase tracking-wider text-[#898781]">{title}</h3>}
      {children}
    </div>
  );
}

export function StatTile({ label, value, sub, accent }: { label: string; value: string; sub?: string; accent?: string }) {
  return (
    <div className="rounded-lg border border-white/10 bg-[#1a1a19] p-4">
      <div className="text-[11px] font-semibold uppercase tracking-wider text-[#898781]">{label}</div>
      <div className="mt-1 font-mono text-3xl font-semibold tabular-nums" style={{ color: accent ?? SOC.ink }}>{value}</div>
      {sub && <div className="mt-1 text-xs text-[#898781]">{sub}</div>}
    </div>
  );
}

const ICON = { good: "✓", serious: "⚠", warning: "◐", critical: "✕", muted: "•" };

export function StatusChip({ kind, label }: { kind: keyof typeof ICON; label: string }) {
  const color = kind === "good" ? SOC.good : kind === "serious" ? SOC.serious
    : kind === "warning" ? SOC.warning : kind === "critical" ? SOC.critical : SOC.muted;
  return (
    <span className="inline-flex items-center gap-1.5 rounded px-1.5 py-0.5 text-xs font-medium"
      style={{ color, backgroundColor: color + "1a" }}>
      <span aria-hidden>{ICON[kind]}</span>{label}
    </span>
  );
}

/** Attack-frequency stacked bars over time. Single y-axis (counts). */
export function TimeSeries({ data }: { data: { safe: number; unsafe: number }[] }) {
  const W = 460, H = 150, padB = 18, padL = 8;
  const max = Math.max(1, ...data.map((d) => d.safe + d.unsafe));
  const n = Math.max(data.length, 1);
  const bw = (W - padL) / n;
  const barW = Math.max(2, bw - 3); // ~3px gap between bars
  const scaleY = (v: number) => (H - padB) * (v / max);
  return (
    <div>
      <div className="mb-2 flex items-center gap-4 text-xs text-[#c3c2b7]">
        <Legend color={SOC.good} label="Benign" />
        <Legend color={SOC.serious} label="Attacks" />
      </div>
      <svg viewBox={`0 0 ${W} ${H}`} className="w-full" role="img" aria-label="Attack frequency over time">
        {[0.25, 0.5, 0.75, 1].map((f) => (
          <line key={f} x1={padL} x2={W} y1={(H - padB) * (1 - f)} y2={(H - padB) * (1 - f)} stroke={SOC.grid} strokeWidth={1} />
        ))}
        {data.map((d, i) => {
          const x = padL + i * bw;
          const hU = scaleY(d.unsafe), hS = scaleY(d.safe);
          const yS = H - padB - hS;
          const yU = yS - hU - (hU > 0 && hS > 0 ? 2 : 0); // 2px surface gap between segments
          return (
            <g key={i}>
              {hS > 0 && <rect x={x} y={yS} width={barW} height={hS} rx={2} fill={SOC.good} />}
              {hU > 0 && <rect x={x} y={yU} width={barW} height={hU} rx={2} fill={SOC.serious} />}
            </g>
          );
        })}
        <line x1={padL} x2={W} y1={H - padB} y2={H - padB} stroke={SOC.axis} strokeWidth={1} />
      </svg>
      <div className="mt-1 flex justify-between text-[10px] text-[#898781]"><span>earlier</span><span>now</span></div>
    </div>
  );
}

function Legend({ color, label }: { color: string; label: string }) {
  return (
    <span className="inline-flex items-center gap-1.5">
      <span className="inline-block h-2.5 w-2.5 rounded-sm" style={{ backgroundColor: color }} />{label}
    </span>
  );
}

/** Horizontal bars, one per taxonomy, each in its fixed categorical color. */
export function TaxonomyBars({ data }: { data: { taxonomy: string; count: number; color: string }[] }) {
  const max = Math.max(1, ...data.map((d) => d.count));
  if (data.length === 0) return <Empty label="No attacks recorded yet" />;
  return (
    <div className="space-y-2">
      {data.map((d) => (
        <div key={d.taxonomy} className="flex items-center gap-2">
          <span className="inline-block h-2.5 w-2.5 shrink-0 rounded-sm" style={{ backgroundColor: d.color }} />
          <span className="w-40 shrink-0 truncate text-xs text-[#c3c2b7]">{d.taxonomy}</span>
          <div className="relative h-4 flex-1 rounded-sm bg-white/5">
            <div className="h-4 rounded-sm" style={{ width: `${(d.count / max) * 100}%`, backgroundColor: d.color }} />
          </div>
          <span className="w-8 shrink-0 text-right font-mono text-xs tabular-nums text-[#c3c2b7]">{d.count}</span>
        </div>
      ))}
    </div>
  );
}

/** Which tier decided — horizontal stacked bar (sequential ramp) + legend. */
export function TierBar({ breakdown }: { breakdown: Record<string, number> }) {
  const entries = Object.entries(breakdown).filter(([, v]) => v > 0);
  const total = entries.reduce((a, [, v]) => a + v, 0) || 1;
  if (entries.length === 0) return <Empty label="No decisions yet" />;
  return (
    <div>
      <div className="flex h-6 w-full gap-0.5 overflow-hidden rounded">
        {entries.map(([tier, v]) => (
          <div key={tier} className="h-6" style={{ width: `${(v / total) * 100}%`, backgroundColor: TIER_COLORS[tier] ?? SOC.muted }} title={`${TIER_LABELS[tier] ?? tier}: ${v}`} />
        ))}
      </div>
      <div className="mt-2 flex flex-wrap gap-x-4 gap-y-1 text-xs text-[#c3c2b7]">
        {entries.map(([tier, v]) => (
          <span key={tier} className="inline-flex items-center gap-1.5">
            <span className="inline-block h-2.5 w-2.5 rounded-sm" style={{ backgroundColor: TIER_COLORS[tier] ?? SOC.muted }} />
            {TIER_LABELS[tier] ?? tier} <span className="font-mono tabular-nums text-[#898781]">{v}</span>
          </span>
        ))}
      </div>
    </div>
  );
}

/** Dwell-time meter: average vs the 5-minute target. */
export function DwellMeter({ avg, target }: { avg: number; target: number }) {
  const pct = Math.min(100, (avg / target) * 100);
  const color = avg >= target ? SOC.good : avg >= target * 0.5 ? SOC.warning : SOC.serious;
  return (
    <div>
      <div className="flex items-baseline justify-between">
        <span className="font-mono text-2xl font-semibold tabular-nums text-white">{fmtDuration(avg)}</span>
        <span className="text-xs text-[#898781]">target {fmtDuration(target)}</span>
      </div>
      <div className="mt-2 h-2 w-full rounded-full bg-white/5">
        <div className="h-2 rounded-full" style={{ width: `${pct}%`, backgroundColor: color }} />
      </div>
    </div>
  );
}

function Empty({ label }: { label: string }) {
  return <div className="py-6 text-center text-xs text-[#898781]">{label}</div>;
}
