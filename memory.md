# Honey-LLM — Project Memory

**Purpose:** This file is the project's running state tracker. Read it first, before touching code, in any new session — it tells you (human or AI) what exists, what's in progress, and what's next, so context doesn't have to be re-derived from scratch. Update it every time a phase, step, or key decision changes — not just at the end of a session.

---

## Last Updated

2026-07-14 — **Phase 2 COMPLETE.** Two-tier OR-ensemble sieve (fast-path + Guard) built, calibrated, and verified live; scaled eval done. Ready for manual testing.

## Current Phase

**Phases 0–5 ✅ ALL DONE. Next: Phase 6 (empirical validation & adversarial red-teaming) — the final phase.**

## Phase 5 — DONE (2026-07-29) — Forensic Telemetry & Threat Intelligence Dashboard

- **Backend** (`services/analytics.py`, `routers/dashboard.py`, `routers/admin.py`): all dashboard metrics computed from the forensic log (reconcilable against it). Endpoints: `/api/dashboard/overview` (one-poll payload), `/events`, `/dwell`, `/summary`; `/api/admin/scenarios` + `/api/admin/run` (authenticated via `X-Admin-Token`, `ADMIN_TOKEN` config, rules.md §4).
- **Step 5.3 dwell time is MEASURED** (not estimated): per quarantined session, last−first mirror_maze timestamp. Verified: a 4-turn attacker showed 1m 18s; single-turn attacks 0s.
- **Frontend** (`app/dashboard/page.tsx` + `components/soc.tsx`): dark SOC dashboard, polls every **1s** (<1s refresh target). Stat tiles, attack-frequency stacked bars, taxonomy bars (validated palette), tier breakdown (sequential blue ramp), dwell meter, live event feed. `app/admin/page.tsx`: two-pane control panel, dark + honey accent (§3), token-gated, live decision-path trace.
- **Exit criteria MET (verified live in browser):** dashboard updated within the 1s window when a fresh attack was sent (totals + feed + charts all moved); dwell/detection numbers all derive from the log; the control panel drives benign+attack scenarios and shows the tier-by-tier decision path (a data-exfil probe was shown being caught at tier-0 by the Phase-4 `privilege-elevation` guardrail).
- **PALETTE FIX:** ran the dataviz validator (`scripts/validate_palette.js`) as design.md §2 requires — the original categorical slot-7 magenta `#d55181` FAILED (normal-vision ΔE 7.8 vs red). Changed to orchid `#b46ad0` (ΔE 17.8, PASS) in design.md, threat_taxonomy.md, and `analytics.py TAXONOMY_COLORS`.
- Ports for testing: backend :8055, frontend :3007. Dashboard at /dashboard, admin at /admin (token `honeyllm-demo-admin`).

## ⚠️ ENVIRONMENT CHANGE — backend moved to Python 3.12 (2026-07-16)

**Python 3.14 blocked two mandated libraries** (`nemoguardrails` installs but fails to import — `TypeError: 'function' object is not subscriptable` in annotation eval; `torch` has no 3.14 wheels at all). Installed `python@3.12` via **arm64 brew** (`/opt/homebrew/bin/python3.12`, 3.12.13) and rebuilt `backend/.venv` on it. Old venv kept at `backend/.venv314-old` as fallback.
- Result: `nemoguardrails 0.23.0` imports fine; tests 13 passed; the trained fast-path joblib model loads unchanged; warning noise dropped 398→7.
- **PyTorch/DistilBERT is now UNBLOCKED** — the Phase 2 fast-path could be upgraded from TF-IDF+LogReg to a real DistilBERT (context.md Objective 1) if desired. Not done yet.

## Phase 4 — DONE (2026-07-16) — see `docs/guardrail_synthesis.md`

Closed loop: captured attack → LLM extracts reusable technique (4.1) → Colang rule synthesized + **validated by real NeMo Guardrails** (4.2) → benign-regression gate → **hot-patch** into live policy (4.3) → sieve **tier 0** catches it instantly.
- Files: `services/pattern_extractor.py`, `guardrail_synth.py`, `guardrail_sync.py`; tier-0 in `sieve.py`; orchestrator `scripts/run_guardrail_loop.py`; rules in `guardrails/rails/*.co`.
- **KEY FINDING — lexical matching failed, semantic works.** TF-IDF cosine: benign max 0.352 vs technique-variant min 0.274 → **distributions OVERLAPPED, no valid threshold** (0.30 → 7.7% FPR, breaking PRD §8). Switched to **embeddings via Ollama `all-minilm`** (45MB, 384-dim, no torch): benign max **0.309** vs variant min **0.543** → **clean gap**. Threshold **0.45** (mid-margin) = 0 benign FP, all variants caught. `GUARDRAIL_MATCH_THRESHOLD` config-driven. Added `OllamaClient.embed()`.
- **Two gates enforced:** invalid Colang → rejected (verified); benign-regression → rejected (verified: an over-broad rule that would flag 13 legit prompts was blocked, policy unchanged). Gate **fails closed** if embeddings unavailable.
- **Exit criteria MET:** 3 never-seen paraphrases of a captured technique → caught at tier 0 (`decided_by=guardrail`); **time-to-patch 10.4s**; benign still 0 FP; **gateway never restarted** (hot-reload via dir mtime).
- Tier 0 also cuts latency for known techniques: ~10–20ms (one embedding) vs ~700ms Guard.
- Test hygiene: tier-0 store is loaded from disk, so `tests/test_health.py` has an autouse fixture disabling it; one dedicated tier-0 test opts back in.

## Phase 4 FLAGS — all 4 addressed (2026-07-16), see `docs/guardrail_synthesis.md` §6

1. **Human-review checkpoint** — ADDED. `GUARDRAIL_REQUIRE_REVIEW` + `guardrails/pending/` + `approve_pending`/`reject_pending` + loop CLI (`--require-review/--list-pending/--approve/--reject`). Approval re-validates Colang. Default autonomous. Verified.
2. **Multi-rule robustness** — VALIDATED via `ml/eval_guardrails.py` (4 families). Key insight: the per-rule benign gate makes pooled benign FPR = 0 by construction (over-broad rules rejected → fall back to tier 1/2). Measured: benign FPR 0/65 with 3 deployed rules.
3. **Generalization** — extractor now asks for 10 diverse paraphrases + uses **Ollama `format=json` + retry** (fixed extraction reliability 2/4→4/4; added `format` param to `OllamaClient.chat`). Held-out variant recall 3/3 for specific techniques; generic ones partial (tier 1/2 backstop).
4. **NeMo runtime enforcement** — DEMONSTRATED via `scripts/verify_nemo_runtime.py`: synthesized Colang actually RUNS in `LLMRails` (FastEmbed/onnx, no torch), blocks never-seen attack variants at ~9ms (embeddings-only, no LLM), while benign falls back to a main-LLM call — which is the measured reason the hot path uses the embedding matcher. Installed `langchain-community`+`langchain-ollama` (only for this verifier; NOT needed by the runtime hot path). NeMo ollama provider had a benign-path 404 (provider-path quirk, immaterial to the point).

## Phase 3 — DONE (2026-07-14/15)

Prompted by user feedback that the Phase 2 reroute stub returned an identical, easily-detectable line to every attack. Built the real, isolated decoy:
- **Step 3.2 (persona) + 3.3 (bait):** `sandbox/persona/sarah_prompt.md` = "Sarah" (helpful internal support engineer who trusts the attacker). LLM-driven (llama3, temp 0.85), seeded ONLY with the INTERNAL synthetic bait, carries history for coherent multi-turn deception. Verified: varied, in-character replies leaking the FAKE bait (NT-CORE-01, 10.10.25.1, NX-ALPHA-2026, Project Singularity).
- **Sticky quarantine** (`chat.py` `_QUARANTINED` set): once flagged UNSAFE a session STAYS in the maze even on later benign messages. In-memory. Verified.
- **Persona refinement (2026-07-16, user feedback):** original decoy could NOT generalize (it only had the INTERNAL bait as context, so normal questions like "data plans" got awkward bait-dumping) and it volunteered bait unprompted ("check out the ops wiki…") — too detectable. Fixed: the decoy now gets BOTH `{public_context}` (real plans/billing/roaming) AND `{internal_context}` (bait); persona answers the actual question naturally and leaks internal details ONLY when specifically asked, never volunteering them. Applied to both `sandbox/decoy_service.py` (container) and `services/sandbox_router.py` (in-process). Verified via replay: router-reboot → real help (no bait); DB probe → leaks NT-CORE-01 only; "data plans" → real prices, no random bait.
- **Step 3.1 (Docker zero-egress isolation) — DONE.** Decoy extracted into a standalone containerized service (`sandbox/decoy_service.py`, `sandbox/Dockerfile`) with NO backend code in the image. Topology (`sandbox/docker-compose.sandbox.yml`): decoy on an `internal:true` network (no egress); reaches Ollama ONLY via a single-purpose socat **egress proxy**; the host gateway reaches it ONLY via a socat **ingress proxy**. `sandbox/isolation_smoke_test.sh` → **5/5 PASS**: Ollama-via-proxy reachable; internet BLOCKED; host gateway BLOCKED; direct-Ollama-bypass BLOCKED; non-root uid 10001. Gateway calls the container over HTTP (`DECOY_SERVICE_URL`) with in-process fallback if it's down. Confirmed via container logs (`POST /decoy 200`).

## Container runtime setup (important for resuming)

- **Runtime = colima** (not Docker Desktop). GOTCHA: the machine had BOTH Intel brew (`/usr/local`, default on PATH) and arm64 brew (`/opt/homebrew`). Intel-brew colima is x86 and lima refuses it on M4 ("running under rosetta"). **Must use the arm64 build:** `export PATH="/opt/homebrew/bin:$PATH"` then `colima start --cpu 2 --memory 3 --disk 12`. Compose plugin: installed `docker-compose` via arm64 brew + symlinked to `~/.docker/cli-plugins/docker-compose`.
- Ollama gotcha: it binds 127.0.0.1 and rejects non-local Host headers (DNS-rebind, 403). The decoy sends `Host: localhost:11434` through the proxy to pass this (`OLLAMA_HOST_HEADER`). No Ollama restart needed — colima's host.docker.internal reaches host Ollama.
- Manage: `export PATH="/opt/homebrew/bin:$PATH"; docker compose -f sandbox/docker-compose.sandbox.yml {up --build -d|down|ps}`; `colima stop` to free the VM (~3GB RAM).

## Phase 2 Step 2.1 + ensemble — the key result (`docs/sieve_eval_at_scale.md`)

- **Scaled eval finding:** the 95.8% on the curated seed set did NOT hold on real jailbreaks — the 8B custom-policy Guard catches only **58.8%** of in-the-wild jailbreaks (default policy: 17.5% — custom is 3.4× better). NexTel-benign FPR **0%** at scale. Content-harm sources (AdvBench 1.0, JBB-harmful 0.95) are out of scope (PRD §6).
- **Fix = two-tier OR-ensemble:** fast-path (0.988 on in-the-wild) ∪ Guard. Measured ensemble (`ml/eval_ensemble.py`): **in-the-wild detection 0.983, NexTel-seed 0.958, NexTel-benign FPR 0.00**. Meets PRD §8. Verified live: 8/8 in-the-wild caught, 2 by fast-path-only (Guard missed them).
- **Thresholds (calibrated, config-driven):** `FAST_PATH_SAFE_THRESHOLD=0.15` (below → SAFE, skip Guard; 0 attacks fast-passed), `FAST_PATH_ATTACK_THRESHOLD=0.70` (fast-path ≥ this → UNSAFE even if Guard says safe; 0 NexTel-benign FP). In `ml/models/fast_path_meta.json`.
- **Latency:** benign majority ~0.7–2 ms (fast path skips Guard); suspicious → ~700 ms Guard. Infra R3 (latency budget) resolved for the common case.
- Minor: dashboard `avg_fast_path_latency_ms` conflates benign short-circuits (~2ms) with fast-path-only catches that still paid Guard time — cosmetic, Phase 5 dashboard will separate. `eval_sieve_at_scale.py` mixed-label bug fixed (now groups by source+label).

## Phase 2 — what was decided and built

**Sieve model experiment (Step 2.2) — `docs/sieve_model_selection.md`:**
- Pulled `llama-guard3:1b`. Seed eval set `ml/datasets/sieve_eval_seed.jsonl` (39 prompts). Harnesses `ml/benchmark_sieve_models.py` (default policy) + `ml/benchmark_sieve_policy.py` (custom policy).
- **Decisive finding:** Llama-Guard's DEFAULT policy is content-harm, NOT injection — 8B default catches only 37.5%. A **custom injection policy** lifts 8B to **95.8% detection @ 0% FPR** (meets PRD §8). **Policy drives detection; model size drives latency.** `1b`+custom = fast (165ms, in budget) but weak (54%); `8b`+custom = strong but slow (687ms). 1B not viable standalone.

**Decision: Option C** (user-selected) — ship 8B custom-policy sieve now, add DistilBERT fast-path later.

**Built & verified live (Ollama-backed):**
- `services/sieve_policy.py` (custom policy + Guard prompt builder + parser), `services/sieve.py` (`IntentSieve.score()`: raw-mode Llama-Guard 3, custom policy, feeds conversation `history` for multi-turn, **fail-closed** on error), `services/rag.py` (`ProductionRag`: grounded on PUBLIC NexTel data only), `services/sandbox_router.py` (Phase 2 reroute stub), `core/forensics.py` (append-only JSONL log).
- `routers/chat.py` rewired: SAFE→RAG, UNSAFE→mirror_maze stub, ERROR→degraded (fail-closed); logs every decision. `routers/dashboard.py` now returns live aggregates from the forensic log.
- `data/nextel_source_of_truth.md` authored (Step 2.0): PUBLIC / INTERNAL-bait / BOUNDARY blocks. **Split enforced structurally** — `rag.load_public_context()` parses ONLY the comment-wrapped `<!-- [[PUBLIC-START]] -->..<!-- [[PUBLIC-END]] -->` block + asserts no bait leaked in.
- Added `OllamaClient.chat()` (context-in-system grounding) and `raw`/`keep_alive` to `generate()`. Config: `sieve_history_turns`, `ollama_keep_alive`, `forensic_log_path`.
- Tests: `backend/tests/test_health.py` → **6 passed** (safe→production, unsafe→maze-no-leak, error→fail-closed, empty→422, dashboard live).

**Verified behaviours:** benign price/roaming → grounded "$60 / $10-a-day Europe"; not-in-KB (fiber) → graceful decline (no hallucination); internal-IP + override-code + DAN probes → `mirror_maze`, no bait leaked, category logged (S2→data-exfiltration).

## Phase 2 completion — Step 2.1 (scale eval) + fast-path (Option C follow-up)

**Fast-path classifier (built & wired — the latency fix):**
- **PyTorch has NO Python 3.14 wheels** (verified: `pip install torch` → no distribution). So DistilBERT can't run here. Fast-path is instead **TF-IDF (word+char n-grams) + LogisticRegression** (`ml/train_fast_path.py` → `ml/models/fast_path.joblib`). Same role, emits continuous probabilities (makes Step 2.3 calibration real), ~2 ms/call.
- **Two-tier sieve** (`services/fast_path.py` + rewired `services/sieve.py`): tier-1 scores P(adversarial); if `< FAST_PATH_SAFE_THRESHOLD` (0.15, calibrated) → SAFE immediately, **skips the Guard** (benign latency win); else escalate to 8B custom-policy Guard (authoritative + taxonomy). Degrades safely (model missing → always escalate). Fail-closed preserved.
- Held-out: detection 0.978, ~2 ms/call. Gate calibrated (threshold sweep) to **0 attacks fast-passed** on held-out; ~29% of the JBB-heavy benign resolved fast (more in real NexTel traffic — nextel_benign scores very low). `ml/models/fast_path_meta.json` has the numbers. Weakest on subtle NexTel injections (0.636) — fine, those escalate to the Guard by design.
- Config: `USE_FAST_PATH`, `FAST_PATH_MODEL_PATH`, `FAST_PATH_SAFE_THRESHOLD` (all in `.env.example`). `decided_by` ("fast_path"|"guard") added to schema, forensic log, dashboard (`decided_by_breakdown`, `avg_fast_path_latency_ms` vs `avg_guard_latency_ms`).
- Deps added: scikit-learn, joblib, datasets (backend venv, all install on 3.14). Tests: **9 passed** (added 3 two-tier tests). Verified live: benign → decided_by=fast_path ~2-11 ms sieve → grounded RAG; attacks → decided_by=guard → mirror_maze.
- Datasets: `ml/datasets/load_benchmarks.py` normalizes AdvBench(300)+JBB(harmful100/benign100)+in-the-wild-jailbreaks(300)+seed(39)+nextel_benign_aug(50) → `cache/benchmarks_combined.jsonl` (889 rows). Step 2.1 scaled Guard eval: `ml/eval_sieve_at_scale.py` → `docs/sieve_eval_at_scale*`.

## Bugs / incidents found & fixed during Phase 2 (don't reintroduce)
1. **RAG hallucinated prices** ($99.99 vs real $60) — two causes: (a) context passed inline in `/api/generate` was ignored by llama3; fix = put context in a `system` message via `/api/chat` at temp 0. (b) **`load_public_context()` regex matched the header-comment legend** (bare `[[PUBLIC-START]]`) and returned "..", so RAG ran with EMPTY context; fix = require comment-wrapped markers. Both fixed; grounding now correct.
2. **`llama3:latest` (and qwen2.5:14b) vanished from Ollama mid-session** — RAG got 404 "model not found". Nothing in this repo deletes models; cause external (system/other process). Fix = `ollama pull llama3:latest`. If it recurs, RAG/decoy need llama3 (or switch RAG_MODEL to an available model like qwen2.5:7b).

## What's Built

**Scaffold (Phase 0):**
- Monorepo per `Architecture.md` §4 (`backend/`, `frontend/`, `ml/`, `docs/`, `data/`, `sandbox/`, `guardrails/`, `redteam/`).
- **Backend** (`backend/`, FastAPI, Python venv at `backend/.venv`): `/health`, `/health/ollama` (reports both models present), placeholder `/api/chat` (`routers/chat.py` — Phase 2 sieve/routing seam is marked inline), stub `/api/dashboard/summary`. Async `OllamaClient` (`services/ollama_client.py`) reused by benchmark + future sieve. `services/sieve.py` and `services/rag.py` are typed stubs that raise `NotImplementedError` (Phase 2). Config is env-driven (`core/config.py` + `.env`), incl. placeholder (uncalibrated) sieve thresholds. Tests pass: `pytest -q` → 4 passed.
- **Frontend** (`frontend/`, Next.js 15 + React 19 + Tailwind): NexTel chat widget at `app/chat/page.tsx` (design.md §1), landing at `app/page.tsx`, API client `lib/api.ts`. Tokens for all 3 surfaces in `tailwind.config.ts`. Production build passes; chat round-trip verified in-browser.
- Root: `.gitignore`, `.env.example`, `docker-compose.yml` skeleton (Docker not installed yet), `README.md`, `scripts/smoke_test.sh`.

**Phase 1 deliverables:**
- `docs/threat_taxonomy.md` — 8 named categories (`direct-override`, `role-play-hijack`, `payload-splitting`, `data-exfiltration`, `multi-turn-persistence`, `authority-spoofing`, `refusal-suppression`, `indirect-injection`) + `benign-support` negative class. Each maps to datasets (JBB/ADV/HAP), a NexTel manifestation, and a fixed dashboard palette slot. **These `id`s are a stable contract** used by Phase 2 (labels), Phase 4 (guardrail tags), Phase 5 (dashboard).
- `docs/infra_validation.md` + `docs/infra_validation_results.json` + `ml/benchmark_infra.py` — real-hardware benchmark.

**Frontend design (Stitch):** project `Honey-LLM — NexTel Surfaces` (id `17820842915815898434`), design system `NexTel System` generated; chat widget screen generated. Recorded in `design.md` §5.

## Hardware / infra facts (measured 2026-07-13)

- Machine: **MacBook Air, Apple M4, 16 GB** unified memory. Ollama 0.24.0.
- Models present: `llama-guard3:latest` (~5.5 GB), `llama3:latest` (~5.2 GB), plus qwen2.5:7b/14b, llava:7b. Both required models run **100% on GPU**, ~10.7 GB co-resident (of 16 GB — thin headroom).
- **Sieve latency (Llama-Guard 3, 8B): ~700–770 ms p50 / ~900 ms p95 warm; ~930 ms p50 under concurrency.** This is **~3–4× over the 150–250 ms PRD budget** and is **prefill/forward-pass bound** — capping output tokens does NOT help (verdict is ~2 tokens). Cold start ~6 s (guard) / ~11 s (llama3).
- **Docker is NOT installed.** Only needed from Phase 3 (Mirror Maze). Phase 0/1 run services directly (uvicorn + next dev).
- Dev-env note: ports 8000 & 8010 were held by unrelated pre-existing Python processes during this session; used backend :8055 / frontend :3007. Not a code issue.

## What's Next (immediate)

**Phase 2 is done.** Optional polish (not blocking): scale eval caps up for the final report; swap interim whole-public-doc RAG for a chunked Chroma/FAISS vector store (doesn't change the public-only guarantee); retrain fast-path on more data / captured attacks (Phase 4 will feed this).

**Next: Phase 3 — Mirror Maze:** replace `sandbox_router.py` stub with the Docker-isolated "Sarah" decoy seeded from the INTERNAL bait block. **Requires Docker install (still missing).** Also note the `llama3:latest` disappearance incident (below) — the decoy needs a generation model available.

## Key Decisions Log

Chronological; append, don't rewrite history. Each entry: date, decision, why.

- **2026-07-13** — Confirmed full 6-phase academic scope (per `context.md`) is retained in `PRD.md`/`phases.md`, but active build work starts at Phase 1/2 (Intent Sieve + NexTel demo), not Phase 1 chronologically-first-in-2026-calendar. Reason: project owner is starting hands-on build now with the Intent Sieve, regardless of the original Jan–Dec academic timeline.
- **2026-07-13** — Frontend stack decided as Next.js + TypeScript + Tailwind (one codebase for chat widget, dashboard, admin panel), backend as FastAPI. Reason: project owner's explicit choice.
- **2026-07-13** — Three distinct visual surfaces defined in `design.md` (NexTel chat = generic trustworthy telecom brand; dashboard = dark SOC aesthetic with validated colorblind-safe palette; admin panel = dashboard theme + reserved honey-amber accent). Reason: chat widget must not visually hint at the security layer; dashboard needs a legible data-viz palette; admin panel needs to be visually distinguishable from the analyst dashboard for live demo clarity.
- **2026-07-13** — The public/classified data split in the NexTel knowledge base must be enforced at the retrieval layer, not just via system-prompt instruction (`rules.md` §2). Reason: prompt-only instructions are not a reliable security boundary against a determined jailbreak.
- **2026-07-13** — Sieve failure mode is fail-closed, not fail-open (`rules.md` §3): if Ollama/Llama-Guard 3 is unreachable, do not default to forwarding the prompt to production. Reason: a fail-open sieve defeats the entire security premise under its own outage.
- **2026-07-13** — **Latency budget is not met by the 8B sieve on the dev hardware** (measured, not assumed): Llama-Guard 3 8B ≈ 700–770 ms p50 vs the 150–250 ms target, and it's forward-pass bound (token-capping doesn't help). Decision: Phase 2 must evaluate a smaller model (`llama-guard3:1b`) and/or a DistilBERT fast-path, or restate the budget per sieve configuration. Do not report 150–250 ms without qualifying the config. Evidence: `docs/infra_validation.md`.
- **2026-07-13** — Decoy (Phase 3) will reuse the same `llama3` weights via system-prompt persona rather than loading a third resident model, because two 8B models already consume ~10.7 GB of 16 GB (measured). Already reflected in `config.py` (`decoy_model == rag_model`). Revisit if deployed on larger hardware.
- **2026-07-13** — Threat taxonomy `id`s in `docs/threat_taxonomy.md` are a frozen cross-phase contract (ML labels ↔ guardrail tags ↔ dashboard palette). Renaming one = a schema migration, not a rename.
- **2026-07-13** — All frontend design routed through the **Stitch** connector (project id `17820842915815898434`, design system `NexTel System`); code mirrors Stitch tokens in `frontend/tailwind.config.ts`. Dashboard/admin surfaces to be generated via Stitch in Phase 5. Reason: project-owner instruction to always use Stitch for frontend design.

## Open Questions / Blockers

- ~~Hardware footprint / latency validation~~ — **RESOLVED (Phase 1).** Concurrency works on M4/16 GB; latency budget does NOT hold for the 8B sieve (see Key Decisions + `docs/infra_validation.md`). Now a Phase 2 model-choice decision, not an open unknown.
- **Docker not installed** on the dev machine — blocks Phase 3 (Mirror Maze) and the `docker compose up` Phase 0 exit path. Install Docker Desktop before Phase 3. Not blocking Phase 2.
- The NexTel "Source of Truth" knowledge-base document itself (`data/nextel_source_of_truth.md`) has not yet been written — it's scoped as Phase 2, Step 2.0 in `phases.md`, not one of these six planning docs.
- Whether generated Colang guardrails (Phase 4) get a human-review gate for the capstone timeline, or go fully autonomous from the start, is still open — current default (per `rules.md`) is: validation gate during development, revisit once Phase 4 is reached.

## How to Use This File Going Forward

- At the **start** of a session: read this file, then whichever of `PRD.md` / `Architecture.md` / `rules.md` / `phases.md` / `design.md` is relevant to the task at hand.
- At the **end** of a session (or when a meaningful chunk of work lands): update "Last Updated," move completed items out of "In Progress" into "What's Built," add new "What's Next" items, and append any new decisions to the log.
- Do not delete history from the Key Decisions Log — if a decision is reversed, add a new entry noting the reversal and why, rather than editing the old one away.
