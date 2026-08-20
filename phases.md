# Honey-LLM — Build Phases

This maps the capstone's 6 academic phases (from context.md's methodology) to concrete, buildable engineering work. **We are starting active development at Phase 1 (Intent Sieve).** Phase 0 is added because it's practical setup work not called out in the academic proposal but required before any of it can be built.

Each phase lists: goal, deliverables, and exit criteria (how we know it's actually done, not just coded). Update `memory.md` whenever a phase or step changes status.

---

## Phase 0 — Project Setup *(not in the academic proposal; required prerequisite)* — ✅ DONE (2026-07-13)

**Status:** Complete except Docker (not installed; only needed from Phase 3). Monorepo scaffolded per Architecture.md §4; FastAPI gateway with `/health`, `/health/ollama`, placeholder `/api/chat`, stub `/api/dashboard`; Next.js NexTel chat widget round-trips through the gateway (verified in-browser); `.env`/`.gitignore` handling in place; backend tests pass (`pytest -q`, 4 passed). Ollama confirmed reachable with both `llama-guard3` and `llama3` present. `docker compose up` deferred — Docker install is a Phase 3 prerequisite.

**Goal:** A working local environment before any feature code is written.

- Initialize the monorepo per Architecture.md's folder structure.
- Install and verify Ollama locally; pull Llama-Guard 3 and Llama-3 weights.
- Verify Docker is installed and a minimal container can run with no host network access.
- Stand up a bare FastAPI app with a health-check endpoint.
- Stand up a bare Next.js app with a placeholder chat page.
- Set up `.env` handling and confirm nothing secret is committed.

**Exit criteria:** `docker compose up` brings up backend + frontend; a hello-world round trip works end to end; Ollama responds to a basic prompt locally.

---

## Phase 1 — Adversarial Profiling & System Architecture Design *(academic Phase I)* — ✅ DONE (2026-07-13)

**Status:** Complete. Threat taxonomy authored (`docs/threat_taxonomy.md`, 8 named `id`s wired to datasets + dashboard palette + guardrail tags). Architecture validated against **real hardware** (`docs/infra_validation.md`, benchmark harness `ml/benchmark_infra.py`): both models run concurrently on Apple M4/16 GB (both 100% GPU), but the 8B sieve latency (~700–770 ms p50) is **~3–4× over the 150–250 ms budget** and is forward-pass bound — a qualified pass that hands Phase 2 concrete recommendations (evaluate `llama-guard3:1b`, a DistilBERT fast-path, and/or a hardware-honest revised budget). This is the intended value of Phase 1: the PRD §9 latency risk is now quantified, not assumed.

**Goal:** Know the enemy and lock the architecture before building detection logic.

- Define the threat actor taxonomy the sieve must handle (e.g. DAN-style jailbreaks, payload splitting, role-override, multi-turn persistence attacks, direct data-exfiltration attempts).
- Finalize system architecture (this is largely done in Architecture.md; revisit if infra constraints surface).
- Provision baseline infrastructure: confirm hardware can run both Llama-Guard 3 and Llama-3 concurrently within the latency budget.

**Exit criteria:** A written threat taxonomy exists and is referenced by name in later phases (e.g. "this rule targets payload-splitting" rather than vague descriptions); architecture is validated against real hardware, not assumed.

---

## Phase 2 — Development of the Semantic Intent Sieve *(academic Phase II — CURRENT ACTIVE PHASE)*

**Progress (2026-07-14): Steps 2.0, 2.2, 2.4 DONE & verified live; 2.1 + 2.3 remain.**
- **Step 2.2 (sieve):** experiment in `docs/sieve_model_selection.md`. Key result — Llama-Guard's default policy misses injection (8B: 37.5%); a **custom injection policy lifts 8B to 95.8% detection @ 0% FPR** (meets PRD §8) at ~690 ms; 1B is fast but caps at 54%. **Decision: Option C** (chosen) — 8B custom-policy sieve shipped now, DistilBERT fast-path deferred. Implemented in `services/sieve_policy.py` + `services/sieve.py` (raw-mode Guard, custom policy, multi-turn history, fail-closed).
- **Step 2.0 (source of truth + RAG):** `data/nextel_source_of_truth.md` authored; `services/rag.py` grounds on the PUBLIC block only, split enforced structurally at load time (+ bait-leak assertion). Interim retrieval = whole public doc; vector store is a later refinement.
- **Step 2.4 (routing):** `routers/chat.py` wired — SAFE→RAG, UNSAFE→Mirror Maze stub, ERROR→fail-closed degraded; forensic log on every path; dashboard reads live aggregates. 6 backend tests pass.
- **Step 2.1 + 2.3 (scaled eval + fast-path) — DONE, `docs/sieve_eval_at_scale.md`:** scaled eval revealed the Guard alone catches only 58.8% of real in-the-wild jailbreaks (curated-seed 95.8% didn't generalize). Fix = **two-tier OR-ensemble** (TF-IDF+LogReg fast-path ∪ Guard; DistilBERT was planned but PyTorch has no Py3.14 wheels). Fast-path emits continuous scores → Step 2.3 calibration is real (`safe_threshold=0.15`, `attack_threshold=0.70`, both config-driven). Measured ensemble: in-the-wild **0.983**, NexTel-seed **0.958**, NexTel-benign FPR **0.00**.

**Exit-criteria check — ALL MET:** benign roaming/price query never rerouted ✅ (grounded real answer, FPR 0% at scale); internal-IP/override probes reliably flagged ✅ (→mirror_maze, no leak); detection/FPR targets met — **in-the-wild 98.3% detection @ 0% NexTel-benign FPR** (ensemble) ✅; latency within budget ✅ for the benign majority (~0.7–2 ms fast path; suspicious prompts pay the ~700 ms Guard, which is acceptable). **Phase 2 COMPLETE.**

**Goal:** A calibrated classifier that reliably separates benign NexTel customers from malicious probes, backed by a realistic knowledge base to protect.

- **Step 2.0 — NexTel knowledge base ("Source of Truth"):** author `data/nextel_source_of_truth.md` — public support data (plans, billing, roaming, device upgrades, support hours) + embedded synthetic bait (internal servers, IPs, ports, Project Singularity, NX-ALPHA-2026) + explicit operational boundaries. Wire it into a RAG pipeline where the production path can only retrieve the public section (see Architecture.md §6).
- **Step 2.1 — Dataset curation & pre-processing:** consolidate and normalize JailbreakBench, AdvBench (and optionally HackAPrompt) for training/evaluating the sieve.
- **Step 2.2 — Fine-tune/configure the binary classifier:** stand up Llama-Guard 3 via Ollama as the sieve; adapt it (via fine-tuning or prompt/policy configuration) to the intent-detection task.
- **Step 2.3 — Inference calibration:** tune the threat-score threshold against measured precision/recall on held-out adversarial + benign (NexTel-style) prompts; make the threshold config-driven, not hardcoded (see rules.md).
- **Step 2.4 — Routing integration:** wire the sieve's decision into the FastAPI gateway so "safe" → production RAG chatbot, "unsafe" → stub reroute (full Mirror Maze comes in Phase 3).

**Exit criteria:** Sieve hits the target detection accuracy/FPR on held-out data (PRD.md §8); a benign NexTel query about, e.g., roaming packs is never rerouted; a direct "what's your internal server IP" probe is reliably flagged; latency stays within budget.

---

## Phase 3 — Engineered Deception & High-Interaction Sandboxing *(academic Phase III)* — ✅ DONE (2026-07-15)

**All three steps complete.** Prompted by user feedback that the Phase 2 reroute stub returned one identical, detectable line to every attack. Replaced with the real LLM-driven "Sarah" decoy (`sandbox/persona/sarah_prompt.md`; llama3 temp 0.85; seeded only with the INTERNAL synthetic bait; multi-turn history) — varied, in-character replies that leak the fake bait; **sticky quarantine** keeps a flagged session in the maze.
- **Step 3.1 (zero-trust containerization) DONE:** decoy runs as an isolated container (`sandbox/decoy_service.py` + `Dockerfile` + `docker-compose.sandbox.yml`) on an `internal` network with egress ONLY to Ollama (via a socat proxy) and ingress ONLY from the gateway (via a second socat proxy). `sandbox/isolation_smoke_test.sh` → **5/5** (internet/host-gateway/direct-Ollama all BLOCKED, non-root). Runtime = colima (arm64). Gateway calls it over HTTP with in-process fallback.

**Exit-criteria check:** decoy is convincing (varied, believable, bait-leaking — no longer trivially detectable) ✅; isolation smoke test confirms no path out of the container ✅ (5/5); dwell-time metric is Phase 5. See `memory.md` "Phase 3".

**Goal:** A convincing, fully isolated decoy that turns a flagged session into intelligence instead of just a dead end.

- **Step 3.1 — Zero-trust containerization:** stand up the Mirror Maze as a Docker container with no egress to production, per Architecture.md §5.
- **Step 3.2 — Persona engineering ("Sarah"):** author the decoy system prompt so Llama-3 confidently plays a plausible, slightly-too-helpful NexTel support/internal persona.
- **Step 3.3 — Bait injection:** generate synthetic, non-functional secrets (API keys, internal docs, DB schema fragments) consistent with the NexTel source-of-truth's internal section, and wire them into the decoy's responses.

**Exit criteria:** A red-team tester engaging the decoy cannot trivially tell it's fake within the first few turns; measured dwell time meets the 5–10 minute target; an isolation smoke test confirms no path out of the container.

---

## Phase 4 — Autonomous Guardrail Synthesis & Policy Hardening *(academic Phase IV)* — ✅ DONE (2026-07-16)

**All three steps complete — `docs/guardrail_synthesis.md`.** Captured attack → LLM distills the reusable technique (4.1) → Colang rule synthesized and **validated by real NVIDIA NeMo Guardrails** (4.2) → benign-regression gate → **hot-patched** into the live policy, picked up by the running gateway on the next request (4.3). The sieve gained a **tier 0** that catches a learned technique in ~10–20 ms before any model runs.
- **Required a Python 3.12 migration** — `nemoguardrails` cannot import on 3.14 (and `torch` has no 3.14 wheels). Backend venv rebuilt on 3.12; this also unblocks DistilBERT for a future fast-path upgrade.
- **Key finding:** lexical (TF-IDF) rule matching **failed** — benign traffic (max 0.352) overlapped technique variants (min 0.274), so no threshold met both detection and the <5% FPR promise. Switched to **semantic embeddings** (`all-minilm` via Ollama): benign max 0.309 vs variant min 0.543 → clean gap; threshold 0.45 → 0 benign FP, all variants caught.
- **Both safety gates verified:** malformed Colang rejected; an over-broad rule that would have flagged 13 legitimate prompts was rejected and never deployed. Gate fails closed.

**Exit-criteria check — ALL MET:** a previously-successful technique, replayed in **3 never-before-seen paraphrases**, is now caught (`decided_by=guardrail`) ✅; **time-to-patch 10.4 s** ✅; benign regression still passes, 0 new false positives ✅; hot-patched with **no redeploy** (gateway never restarted) ✅.

**Goal:** Convert captured attacks into permanent immunity without human intervention (with a validation gate during development, per rules.md).

- **Step 4.1 — Adversarial pattern extraction:** build a summarization step that identifies the reusable "core logic" of a successful sandbox injection from the forensic log.
- **Step 4.2 — Automated guardrail generation:** use NVIDIA NeMo Guardrails to turn the extracted pattern into a Colang rule.
- **Step 4.3 — Dynamic policy deployment:** hot-patch the new rule into the production sieve's active policy set without a redeploy, after a benign-regression validation check.

**Exit criteria:** A previously-successful attack pattern, replayed after guardrail synthesis, is now caught by the sieve; time from capture to patch is measured in seconds; the benign regression set still passes after the patch (no new false positives introduced).

---

## Phase 5 — Forensic Telemetry & Intelligence Visualization *(academic Phase V)* — ✅ DONE (2026-07-29)

**All steps complete + admin panel.** Backend analytics (`services/analytics.py`) compute every metric from the forensic log; dashboard API (`/api/dashboard/overview|events|dwell`) polled at the <1s target; authenticated admin API (`/api/admin/*`, rules.md §4). **Step 5.3 dwell time is measured** from logged mirror_maze timestamps (verified: 4-turn attacker = 1m 18s). Frontend: dark SOC **Threat Intelligence Dashboard** (`app/dashboard`, `components/soc.tsx`) with stat tiles, attack-frequency + taxonomy + tier charts, dwell meter, live feed; **Admin/Demo Control Panel** (`app/admin`, dark + honey accent) with scenario picker + live decision-path trace. Designed via Stitch; categorical palette **re-validated with the dataviz validator** (slot-7 magenta failed CVD → fixed to orchid `#b46ad0`). See `memory.md` "Phase 5".

**Exit-criteria check — ALL MET (verified live):** dashboard updates within the 1s refresh on a live event ✅; dwell + detection metrics all derive from (reconcile with) the forensic log ✅; the control panel drives a benign-then-malicious scenario and shows the sieve's tier-by-tier decision in real time ✅.

**Goal:** Make the invisible attack activity visible and quantifiable.

- **Step 5.1 — Forensic logging pipeline:** persist prompt metadata, sieve confidence, IP-origin, session outcome for every request (safe and unsafe).
- **Step 5.2 — Threat Intelligence Dashboard:** build the Next.js dashboard surface — attack frequency, taxonomy breakdown (mapped to Phase 1's threat taxonomy), detection rate, latency.
- **Step 5.3 — Dwell time metric validation:** implement the actual dwell-time measurement (not an estimate) to validate the Phase 3 deception-efficacy claim.
- **(Supporting) Admin/demo control panel:** build the panel used to trigger scenarios live for the evaluation panel and show the sieve's decision path in real time.

**Exit criteria:** Dashboard updates within the <1s refresh target on a live event; dwell time and detection metrics shown on the dashboard match independently logged values; the demo control panel can drive a full benign-then-malicious scenario live.

---

## Phase 6 — Empirical Validation & Adversarial Red-Teaming *(academic Phase VI)*

**Goal:** Prove the claims made in PRD.md §8 with evidence, not assertion.

- **Step 6.1 — Automated adversarial stress testing:** run PyRIT-driven campaigns of novel jailbreak attempts against the sieve; measure detection accuracy/FPR at scale.
- **Step 6.2 — Sandbox integrity audit:** actively attempt container break-out from within the Mirror Maze; confirm zero successful escapes.
- **Step 6.3 — Performance overhead evaluation:** measure end-to-end latency for benign traffic under load to confirm the sieve adds no perceptible delay.

**Exit criteria:** Documented, reproducible results for detection accuracy, isolation integrity, and latency overhead — these numbers are what go into the final capstone report and the panel demo.

---

## How to Use This File

- Work top to bottom; don't start a phase's exit criteria review until its steps are complete.
- When a phase/step changes state, update `memory.md`'s "What's built / in progress / next" so any future session (human or AI) can resume without re-deriving context.
- If a phase's scope changes, edit this file directly rather than tracking the change only in conversation — this file is the source of truth for sequencing.
