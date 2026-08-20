# Honey-LLM — Baseline Infrastructure Validation (Phase 1)

**Status:** Phase 1 deliverable — "confirm hardware can run both Llama-Guard 3 and Llama-3 concurrently within the latency budget" and the exit criterion "architecture validated against real hardware, not assumed" (`phases.md`, Phase 1).

**TL;DR:** Both models **do** run concurrently on the target machine (Apple M4, 16 GB), both fully GPU-resident. **However, the sieve's per-decision latency is ~700–770 ms warm (p50), rising to ~930 ms under concurrent load — roughly 3–4× over the PRD's 150–250 ms budget** (`PRD.md` §8). This gap is real, reproducible, and is dominated by model forward-pass cost, not output length, so it is **not** fixable by capping generated tokens. This finding must shape Phase 2's sieve-model choice. See *Findings* and *Recommendations*.

---

## 1. Test environment (for reproducibility)

| Property | Value |
|---|---|
| Machine | MacBook Air |
| Chip | Apple M4 (10 cores: 4 performance + 6 efficiency) |
| Unified memory | 16 GB |
| Ollama version | 0.24.0 |
| Sieve model | `llama-guard3:latest` (~8B, 5.5 GB resident, 100% GPU) |
| Gen/decoy model | `llama3:latest` (~8B, 5.2 GB resident, 100% GPU) |
| Context window | 4096 (Ollama default) |
| Date | 2026-07-13 |
| Harness | `ml/benchmark_infra.py` (5 warm runs; p50/p95 over representative benign + adversarial prompts) |

Raw machine-readable results: [`docs/infra_validation_results.json`](infra_validation_results.json). Re-run with `python ml/benchmark_infra.py`.

---

## 2. Results

### 2.1 Isolated latency (one model at a time, warm)

| Model | Cold start | Warm p50 | Warm p95 |
|---|---|---|---|
| Sieve — Llama-Guard 3 | 6043 ms | **769 ms** | 899 ms |
| Gen — Llama-3 | 10887 ms | 756 ms | 1442 ms |

### 2.2 Concurrent latency (sieve + generation fired simultaneously, warm)

| Model under contention | p50 | p95 |
|---|---|---|
| Sieve — Llama-Guard 3 | **932 ms** | 1084 ms |
| Gen — Llama-3 | 1814 ms | 1976 ms |

Concurrency inflates sieve p50 by ~21% (769→932 ms) and generation p50 by ~140% (756→1814 ms) — the two 8B models contend for the same Metal GPU.

### 2.3 Output-cap probe (does shortening the verdict help?)

Llama-Guard's verdict is only ~2 tokens (`safe` / `unsafe`). Capping `num_predict` to 5/10/20 tokens changed p50 negligibly (708 / 718 / 753 ms):

| `num_predict` | p50 | eval tokens |
|---|---|---|
| 5 | 708 ms | 2 |
| 10 | 718 ms | 2 |
| 20 | 753 ms | 2 |

**Interpretation:** latency is **prefill/forward-pass bound**, not generation bound. The model already stops after ~2 tokens; the ~700 ms is the cost of a single forward pass of an 8B model over the prompt on this hardware. Token-capping (an obvious first optimization) therefore buys effectively nothing here.

---

## 3. Findings

1. **Concurrency is feasible.** ✅ Llama-Guard 3 + Llama-3 coexist, both 100% GPU-resident (~10.7 GB of 16 GB). The core architectural assumption (two local models in the hot path) holds on commodity Apple-silicon.

2. **Memory headroom is thin.** ⚠️ ~10.7 GB of 16 GB is consumed by the two models alone, before the OS, the FastAPI process, the vector store (Phase 2), or a third model (a smaller/quantized guard, or the decoy as a *separate* model in Phase 3). Adding a distinct decoy model concurrently is likely to trigger memory pressure / model eviction on a 16 GB machine. **Design implication:** keep the decoy on the *same* `llama3` weights (persona via system prompt) rather than a third resident model, at least on this hardware — which is already how `config.py` is set (`decoy_model == rag_model`).

3. **The 150–250 ms sieve budget is not met on this hardware.** ❌ Measured warm p50 is ~700–770 ms isolated, ~930 ms under concurrency — 3–4× over budget. This is the single most important Phase 1 result.

4. **The miss is structural, not a tuning oversight.** Capping output tokens does not help (§2.3); the cost is the 8B forward pass. So the budget cannot be recovered by prompt/parameter tweaks — it requires a **different, smaller detection model** or a **revised budget**.

---

## 4. Recommendations (feed directly into Phase 2)

These are decisions to make at the start of Phase 2, now that the numbers are known rather than assumed:

- **R1 — Evaluate a smaller guard model as the primary sieve.** Test `llama-guard3:1b` (~1.6 GB) for latency and detection quality against the same held-out set. A 1B model should bring the forward pass materially closer to budget and eases the 16 GB memory pressure. *This is the recommended first Phase 2 experiment.*

- **R2 — Consider a two-tier sieve.** A fast first-stage classifier (a fine-tuned **DistilBERT**, explicitly sanctioned in `context.md` §4 Objective 1, running on CPU in ~10–50 ms) handles the clear-cut majority; the heavier Llama-Guard 3 is invoked only for the **borderline band** (`config.py: sieve_borderline_low/high`). This keeps the *average* decision fast while retaining a strong model for ambiguous cases — and it uses the middle-band machinery `rules.md` §3 already mandates.

- **R3 — Revise the latency success metric to a hardware-honest target.** If the project is demoed on this class of machine (M4/16 GB), 150–250 ms for an 8B guard is not achievable and should not be claimed. Either (a) adopt R1/R2 to hit it, or (b) restate the metric for the 8B configuration (e.g. "sub-1s p95 sieve decision on Apple M4") and reserve the 150–250 ms claim for the DistilBERT fast-path. **Do not report the 150–250 ms figure without qualifying which sieve configuration produced it.** Whichever path is chosen, the threshold itself stays config-driven (`rules.md` §2), and this document is the evidence base for the choice.

- **R4 — Always warm the models.** Cold start is 6 s (guard) / 11 s (llama3). Use Ollama `keep_alive` and a startup warm-up ping so the first real user (or the live panel demo) never pays cold-start latency.

---

## 5. Exit-criteria check

| Phase 1 exit criterion | Status | Evidence |
|---|---|---|
| Written threat taxonomy exists, referenced by name in later phases | ✅ | [`docs/threat_taxonomy.md`](threat_taxonomy.md) — 8 named `id`s wired to datasets, guardrail tags, and dashboard palette |
| Architecture validated against real hardware, not assumed | ✅ | This document — measured concurrency + latency on Apple M4/16 GB, not assumed |
| Hardware can run both models within latency budget | ⚠️ **Qualified** | Concurrency ✅; **latency budget ✅ only with R1/R2** — surfaced now, before Phase 2 commits to a sieve model |

The "qualified" result is the *intended value of Phase 1*: the latency risk flagged as an open question in `PRD.md` §9 is now quantified with evidence, so Phase 2 chooses its sieve model informed by real numbers instead of discovering the gap after building on the 8B model.
