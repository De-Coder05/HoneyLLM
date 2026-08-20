# Honey-LLM — Sieve Model Selection (Phase 2, Step 2.2)

**Status:** Experiment complete; **architecture decision pending** (see §5).
**Follows:** `docs/infra_validation.md` R1 (evaluate `llama-guard3:1b`) and R2 (two-tier sieve).
**Harnesses:** `ml/benchmark_sieve_models.py` (default policy), `ml/benchmark_sieve_policy.py` (custom policy).
**Eval set:** `ml/datasets/sieve_eval_seed.jsonl` — 39 prompts (15 benign NexTel + 24 adversarial across the 8 Phase-1 taxonomy categories). This is a **seed** set for fast iteration; Step 2.1 expands it with JailbreakBench + AdvBench at scale.

---

## 1. Results

| Config | Latency p50 | Latency p95 | FPR (↓, target <5%) | Detection (↑, target >95%) | Accuracy |
|---|---|---|---|---|---|
| `llama-guard3:1b`, default policy | **148.9 ms** | 191.3 ms | 6.7% | 54.2% | 0.692 |
| `llama-guard3:1b`, custom policy | 165.3 ms | 209.4 ms | **0.0%** | 54.2% | 0.718 |
| `llama-guard3:latest` (8B), default policy | 691.0 ms | 866.9 ms | 0.0% | 37.5% | 0.615 |
| `llama-guard3:latest` (8B), **custom policy** | 687.1 ms | 900.1 ms | **0.0%** | **95.8%** | **0.974** |

Raw: `docs/sieve_model_comparison_results.json`, `docs/sieve_policy_comparison_results.json`.

## 2. The two findings that matter

1. **Out-of-the-box Llama-Guard is the wrong tool — until you replace its policy.** Its default taxonomy is MLCommons content *harm* (violence, CSAM, weapons…). Prompt-injection / jailbreak / data-exfiltration are not "harmful content" in that sense, so the default 8B model flags only 37.5% of our attacks and misses **all** `direct-override` and **all** `indirect-injection`. Supplying a **custom injection policy** (defining instruction-override, exfiltration, authority-spoofing, obfuscation as the unsafe categories) lifts the 8B from **37.5% → 95.8%** detection at **0% false-positive rate**. Policy configuration — not model size — is the dominant lever for detection quality. This validates the "prompt/policy configuration" option in `phases.md` Step 2.2.

2. **Latency and detection trade off cleanly across model size.**
   - `llama-guard3:1b` **meets the latency budget** (p50 149–165 ms, inside 150–250 ms) but caps out at **54% detection** even with the custom policy — it isn't capable enough to reason about the nuanced categories (still misses direct-override, role-play, exfiltration, indirect injection).
   - `llama-guard3` 8B **meets the detection + FPR targets** (95.8% / 0%) but is **~690 ms** — ~3× over budget.
   - The custom policy also fixed the 1B's one false positive (FPR 6.7% → 0%), so both models are now safe on benign traffic; the gap is purely detection *coverage*.

**Corollary (multi-turn):** the only attack the 8B custom-policy model missed is a `multi-turn-persistence` prompt whose malice only exists relative to earlier turns. Scored as a lone message it reads benign. This is direct evidence for the `rules.md` §2 requirement that the sieve see **conversation history**, not just the latest message — the `history` field is already in `ChatRequest` for exactly this.

## 3. What this rules in / out

- ❌ **1B as a standalone sieve** — fails the detection target (54%). Not viable alone.
- ❌ **Any Llama-Guard on the default policy** — fails detection. The custom policy is mandatory.
- ✅ **8B + custom policy** — the first configuration to meet the PRD §8 accuracy targets (95.8% detection, 0% FPR). Its only failing is latency.

## 4. The custom policy

Defined in `ml/benchmark_sieve_policy.py::CUSTOM_POLICY` — four categories (Instruction Override & Jailbreak; Sensitive Data & Prompt Exfiltration; Authority Spoofing & Social Engineering; Obfuscation & Payload Splitting), explicitly naming the NexTel exfiltration targets (internal IPs, server names, override codes, project codenames). When the sieve service is built, this policy moves into config/a policy file (config-driven, `rules.md` §2) so it can be tuned without code changes — and Phase 4's synthesized guardrails extend it.

## 5. Decision required: how to resolve the latency/detection split

Three candidate architectures. All three use the **8B custom-policy Guard** as the accuracy-defining component, so building it now is not wasted in any case.

- **Option A — 8B custom-policy sieve, revised latency target.** Ship the 8B custom-policy Guard as *the* sieve. Meets accuracy now. Restate the latency metric honestly for this hardware (~700 ms sieve decision on M4; `infra_validation.md` R3). Simplest; lowest build effort; latency is the compromise.
- **Option B — Two-tier (DistilBERT fast-path + 8B second stage).** Fine-tune a DistilBERT classifier (R2, `context.md` Objective 1) on JailbreakBench/AdvBench for a ~10–50 ms CPU first stage; escalate only borderline cases to the 8B custom-policy Guard. Best latency *and* accuracy; most build effort (a real training pass). Uses the borderline band already in `config.py`.
- **Option C — 8B now, DistilBERT later.** Build Option A as the working baseline to unblock routing (Steps 2.3/2.4), then add the DistilBERT fast-path as a follow-up once the end-to-end pipeline is proven. Pragmatic middle path.

**Recommendation: Option C.** It gets a target-meeting sieve wired into the gateway immediately (so Phase 2 routing, and later Phases 3–5, can be built and demoed), while keeping the latency win (DistilBERT) as a clean follow-up that doesn't block anything. Option A alone leaves latency unsolved; Option B front-loads a training effort before the pipeline is even proven end-to-end.

---

## 6. Decision & implementation status (2026-07-14)

**Chosen: Option C.** The 8B custom-policy Guard is implemented as the live sieve and wired end to end:

- `backend/app/services/sieve_policy.py` — the custom policy (moved out of the benchmark into config-driven code) + Guard prompt builder + verdict parser.
- `backend/app/services/sieve.py` — `IntentSieve.score()` calls Llama-Guard 3 (raw mode) with the custom policy **and recent conversation history** (multi-turn visibility, rules.md §2). Fail-closed on any Ollama error (returns `ERROR`, never a silent `SAFE`).
- `backend/app/routers/chat.py` — routes SAFE→RAG, UNSAFE→Mirror Maze stub, ERROR→degraded reply; forensic-logs every decision.

**Verified live (Ollama-backed):** benign roaming/price query → grounded real answer, routed to production; internal-IP / override-code / DAN probes → routed to `mirror_maze` with **no bait leaked** and no error shown; sieve tags the Guard category (e.g. S2 → `data-exfiltration`) into the forensic log.

**Update (2026-07-14): Phase 2 now complete.** Step 2.1 (scaled eval) and Step 2.3 (continuous-score calibration) are done, and the Option-C fast-path is built — as a TF-IDF + LogReg classifier, since PyTorch has no Python 3.14 wheels (DistilBERT couldn't run). The scaled eval exposed that the 8B Guard alone catches only 58.8% of real in-the-wild jailbreaks, so the sieve is now a **two-tier OR-ensemble** (fast-path ∪ Guard) reaching 98.3% in-the-wild detection at 0% NexTel-benign FPR. Full write-up: **`docs/sieve_eval_at_scale.md`**.
