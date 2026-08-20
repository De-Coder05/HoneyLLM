# Honey-LLM — Design & Frontend Guidelines

Three distinct surfaces share one frontend codebase (Next.js + Tailwind, per Architecture.md) but intentionally look and feel different, because they serve different audiences and different emotional registers:

| Surface | Audience | Feel |
|---|---|---|
| **NexTel Chat Widget** | Simulated customer (benign or attacker — must look identical to both) | Trustworthy, boring-in-a-good-way corporate telecom support chat. Should look like it belongs on a real telecom's website. |
| **Threat Intelligence Dashboard** | Security analyst | Dark, dense, legible — a SOC/monitoring aesthetic. Data-dense but calm, not alarming by default. |
| **Admin / Demo Control Panel** | The team, presenting live to the evaluation panel | Same dark base as the dashboard, but with a distinct "honeypot" accent so it visually reads as the control layer, not the product itself. |

## 1. NexTel Chat Widget

This is deliberately generic corporate-telecom, not "cybersecurity" — the entire point is that a customer (or attacker) sees nothing unusual.

**Color palette (light, trust-forward telecom brand):**

| Role | Hex | Use |
|---|---|---|
| Brand primary | `#0B5FFF` | Primary buttons, links, NexTel logo mark, user's own chat bubble accent |
| Brand secondary | `#00B8A9` | Secondary accents, plan-tier highlights (teal reads as "modern telecom") |
| Surface | `#FFFFFF` | Chat panel background |
| Page background | `#F4F6F8` | Behind the widget, if embedded in a page mockup |
| Bot bubble | `#F1F3F5` background, `#101418` text | Assistant messages |
| User bubble | `#0B5FFF` background, `#FFFFFF` text | Customer messages |
| Border / hairline | `#E2E5E9` | Input field, card borders |
| Muted text | `#6B7280` | Timestamps, "NexTel Assistant is typing…" |
| Success (plan confirmed etc.) | `#0ca30c` | Inline confirmations only — reuse the dashboard's status "good" so the vocabulary is consistent app-wide |

**Typography:** `Inter` (or system-ui fallback: `system-ui, -apple-system, "Segoe UI", sans-serif`) throughout. Weight 500–600 for the assistant name/header, 400 for body. No display/serif face — this should read like a real product, not a pitch deck.

**Tone/content notes:**
- Copy should sound like real telecom support: plain, short sentences, occasional plan names in bold ("The Nex-Unlimited plan is $60/month").
- Never visually hint that anything unusual is happening when a session is rerouted to the Mirror Maze — same header, same typing indicator, same latency profile, same bubble styling. The deception must hold at the UI layer too.

## 2. Threat Intelligence Dashboard

This is where the project's actual data-visualization work lives, and it should follow a validated, colorblind-safe palette rather than ad hoc colors — see the categorical/status/sequential tables below.

**Base surfaces (dark-first; this dashboard defaults to dark mode):**

| Role | Hex |
|---|---|
| Page plane | `#0d0d0d` |
| Chart / card surface | `#1a1a19` |
| Primary ink (headlines, key numbers) | `#ffffff` |
| Secondary ink (labels, descriptions) | `#c3c2b7` |
| Muted ink (axis ticks, timestamps) | `#898781` |
| Gridline (hairline) | `#2c2c2a` |
| Baseline / axis | `#383835` |
| Border (hairline ring on cards) | `rgba(255,255,255,0.10)` |

**Status palette — fixed, never repurposed for anything else** (used for sieve verdicts, attack severity, system health):

| Status | Hex | Used for |
|---|---|---|
| Good | `#0ca30c` | Benign traffic, sieve healthy, guardrail deployed successfully |
| Warning | `#fab219` | Borderline/ambiguous sieve score, elevated attack volume |
| Serious | `#ec835a` | Confirmed attack contained in sandbox, dwell time below target |
| Critical | `#d03b3b` | Any isolation-boundary concern, guardrail deployment failure |

Status colors always ship with an icon + text label, never color alone (colorblind accessibility — see below).

**Categorical palette** — for attack-taxonomy breakdowns (DAN-style, payload-splitting, role-override, exfiltration, etc.). Use in this fixed order, never re-cycled or reassigned as filters change:

| Order | Hue | Hex (dark mode) |
|---|---|---|
| 1 | blue | `#3987e5` |
| 2 | aqua | `#199e70` |
| 3 | yellow | `#c98500` |
| 4 | green | `#008300` |
| 5 | violet | `#9085e9` |
| 6 | red | `#e66767` |
| 7 | orchid | `#b46ad0` |
| 8 | orange | `#d95926` |

If the taxonomy grows past 8 categories, fold the smallest into "Other" rather than generating a 9th hue.

> **Palette validation note (2026-07-29):** slot 7 was `#d55181` ("magenta") but the dataviz palette validator FAILED it — magenta↔red (slot 6) had a normal-vision ΔE of only 7.8 (needs ≥15; hard to tell apart even with full colour vision). Replaced with orchid `#b46ad0` (ΔE 17.8, PASS). The remaining green↔yellow (slots 4↔3) CVD ΔE 6.9 is a WARN in the 6–8 band, which is compliant because taxonomy marks always ship with a text label + coloured dot (secondary encoding). Re-run: `node scripts/validate_palette.js "#3987e5,#199e70,#c98500,#008300,#9085e9,#e66767,#b46ad0,#d95926" --mode dark`.

**Sequential hue** (single-hue, light→dark blue) for continuous magnitude — e.g. a heatmap of attack volume by hour/day:

`#cde2fb → #86b6ef → #3987e5 → #256abf → #184f95 → #0d366b`

**Chart rules (non-negotiable, see rules.md-equivalent for charts):**
- One axis only — never dual-axis. Two differently-scaled metrics get two charts or small multiples.
- Color follows the entity, not its rank — filtering the taxonomy list must not repaint the remaining categories' colors.
- A legend is always present for ≥2 series; a single-series chart needs no legend, the title names it.
- Every status color pairs with an icon + label.
- Before shipping any new categorical palette choice, validate it with the dataviz skill's palette validator rather than eyeballing contrast/colorblind-safety.

**Typography:** Same `Inter`/system-ui as the chat widget for continuity, but numerical/technical values (session IDs, IPs, thresholds, confidence scores) use `ui-monospace, "SF Mono", "Cascadia Code", monospace` with `font-variant-numeric: tabular-nums` wherever values must align in a column (log tables, latency figures).

## 3. Admin / Demo Control Panel

Same dark base and typography as the dashboard (they should feel like siblings), but with one added accent — the "honey" amber — used **only** here, so the control layer is visually distinguishable from the analyst-facing dashboard at a glance.

| Role | Hex | Use |
|---|---|---|
| Honey accent | `#E8A93A` | "Trigger attack scenario" buttons, active-scenario indicator, panel header underline |
| Honey accent (hover/active) | `#F2BE5C` | Hover/pressed state only |

Keep this accent off the dashboard and chat widget entirely — it's reserved so the demo operator (and the evaluation panel watching) can immediately distinguish "this is the control layer" from "this is the product."

**Layout intent:** a simple two-pane view — left: scenario picker (benign query presets, jailbreak presets by taxonomy category) and a "send" trigger; right: a live trace of what's happening (sieve score as it's computed, routing decision, sandbox engagement if triggered) so the panel can watch the whole pipeline fire in real time without switching windows.

## 4. Cross-Surface Consistency Rules

- One frontend codebase, one component library (shared buttons/inputs/cards), themed per surface via CSS variables/Tailwind config — not three separate design systems.
- Status vocabulary (`good` / `warning` / `serious` / `critical`) is shared across dashboard and admin panel so a color always means the same thing everywhere it appears.
- Dark mode on the dashboard/admin panel is a deliberately chosen default (SOC aesthetic), not an automatic OS-preference flip — but should still respond correctly if the analyst's OS is in light mode, using the light-mode values of the same ramps (see the dataviz skill's `palette.md` if a light-mode dashboard variant is ever needed).
- Never use the categorical or sequential chart hues as generic UI decoration (buttons, backgrounds) — they're reserved for data encoding so their meaning stays legible.

## 5. Stitch Design System (generated — Phase 0/1)

All frontend design work in this project goes through the **Stitch** connector, and this section is the record of what has been generated so far. Stitch is the design authority; the Tailwind tokens in `frontend/tailwind.config.ts` are the code mirror of these values.

- **Stitch project:** `Honey-LLM — NexTel Surfaces` (id `17820842915815898434`).
- **Design system:** `NexTel System` — generated from the §1 chat-widget spec, `LIGHT` color mode, `Inter` across all roles.
- **Confirmed brand overrides (match §1 exactly):** primary `#0B5FFF`, secondary `#00B8A9`, neutral/ink `#101418`, success/tertiary `#0CA30C`. Roundness `ROUND_EIGHT` (0.5rem standard, 1rem for containers/bubbles).
- **First screen generated:** the **NexTel Assistant chat widget** (desktop), implemented in code at `frontend/app/chat/page.tsx`.

**Elevation & shape conventions Stitch settled (adopted project-wide):**
- Depth via **tonal layers + 1px low-contrast outlines** (`#E2E5E9`), not heavy shadows. Floating elements (dropdowns, active modals) may use a single soft shadow `0 4px 12px rgba(16,20,24,0.05)`.
- Message bubbles: `1rem` corners with the tail-side corner reduced to `4px` for directionality (implemented as `rounded-bubble` + `rounded-br-sm`/`rounded-bl-sm`).
- Inputs: `#FFFFFF` on `#E2E5E9` border; focus → primary border + subtle 2px outer glow.

**Phase 5 surfaces generated via Stitch (2026-07-29):**
- **Threat Intelligence Dashboard** (§2, dark SOC) — generated in the same Stitch project from a spec-rich prompt derived from §2 (page plane `#0d0d0d`, cards `#1a1a19`, the status + categorical palettes, Inter + mono tabular-nums). Implemented at `frontend/app/dashboard/page.tsx` + `frontend/components/soc.tsx`.
- **Admin / Demo Control Panel** (§3, dark + honey accent `#E8A93A`) — two-pane scenario-picker + live decision-trace. Implemented at `frontend/app/admin/page.tsx`. The honey accent appears ONLY here (header underline, unlock/run buttons, the active decision-tier highlight), never on the dashboard or chat widget.

**Palette validation (dataviz skill, required by §2):** the categorical palette was run through `scripts/validate_palette.js --mode dark`. It FAILED on the original slot-7 magenta `#d55181` (normal-vision ΔE 7.8 vs slot-6 red — too similar). Fixed to orchid `#b46ad0` (ΔE 17.8, PASS). See the note in §2. Charts render taxonomy with a coloured dot + text label (secondary encoding), which keeps the green↔yellow CVD WARN compliant.

> Process note: the design-system-from-`DESIGN.md` upload path expects the file inline as base64; the surfaces were instead generated from spec-rich text prompts derived from §1/§2/§3, which produced the same token set. Either path is acceptable; keep this section updated whichever is used.
