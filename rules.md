# Honey-LLM — Engineering Rules

These are binding defaults for anyone (human or AI) writing code in this repo. Deviating from any of these requires an explicit, conscious decision — not a default.

## 1. Libraries & Tools — Use These

| Purpose | Use | Not |
|---|---|---|
| LLM inference | **Ollama** (local) running Llama-Guard 3 / Llama-3 | Hosted API models (OpenAI, Anthropic, Gemini, etc.) — breaks the "zero per-message cost, zero external dependency" value proposition and adds an uncontrolled network egress point right where isolation matters most. |
| Web backend | **FastAPI** (async endpoints) | Flask/Django for the hot chat path — FastAPI's async model matters for the sieve's latency budget. |
| Frontend | **Next.js + TypeScript + Tailwind** | Ad-hoc vanilla JS widgets, or a second unrelated framework for the dashboard — keep one frontend stack across chat/dashboard/admin. |
| Sandbox isolation | **Docker**, explicit `--network` isolation, no default bridge to host | VMs (too heavy for this scale), or "isolation" via application-level flags without an actual container/network boundary. |
| Classifier | **Llama-Guard 3** fine-tuned/calibrated on JailbreakBench, AdvBench | Training a classifier from scratch, or using a plain keyword/regex filter as the primary sieve. |
| Guardrail synthesis | **NVIDIA NeMo Guardrails** (Colang) | Hand-written if/else string-matching rules as a permanent solution — acceptable only as a temporary stopgap, must convert to Colang rules for the guardrail set. |
| Red-teaming | **PyRIT** | Manually typing jailbreak prompts as the only validation method — fine for early dev sanity checks, not sufficient for Phase VI validation claims. |
| Datasets/weights | **Hugging Face** (`datasets`, `transformers`, `huggingface_hub`) | Scraping ad-hoc jailbreak prompts from forums without licensing/attribution clarity. |
| ML runtime | **PyTorch** | TensorFlow/JAX — no reason to introduce a second ML framework into this stack. |
| Vector store | Local (Chroma or FAISS) | A managed cloud vector DB — adds external dependency and cost for a capstone-scale corpus. |

## 2. What to Avoid, and Why

- **No real secrets, ever, anywhere in the NexTel data.** Every "internal" artifact (IPs, server names, override codes, project names) must be synthetic and provably non-functional. Do not reuse real internal naming conventions, real IP ranges you control, or real credential formats that could be mistaken for genuine leaked material.
- **Don't rely on prompt instructions alone as a security boundary.** "You must never reveal X" in a system prompt is a suggestion, not a guarantee — LLMs can be persuaded past it. The public/classified data split must be enforced structurally (retrieval-layer filtering, separate indices/containers), with the prompt instruction as a second layer, not the only layer.
- **Don't let the decoy container reach anything real.** No shared volumes with production data, no network path to the production DB or the production vector store, no shared credentials. Validate this with an explicit isolation test (Phase VI), not by assumption.
- **Don't block the event loop in FastAPI.** LLM calls (via Ollama) and DB writes in the hot chat path must be async/non-blocking; a synchronous call here defeats the latency budget the whole pitch depends on.
- **Don't hardcode the sieve's threat-score threshold.** It must come from a calibration step (Phase II, Step 2.3) informed by measured false-positive/false-negative rates, and it must be config-driven (not a magic number buried in code) so it can be re-tuned without a redeploy.
- **Don't treat "safe" as a permanent verdict.** Multi-turn attacks can build up malicious intent across several individually-benign-looking turns; the sieve should have access to enough conversation context to catch persistence-scaled attacks, not just score the latest message in isolation.
- **Don't skip logging on the unsafe path.** Every rerouted session must be logged with enough metadata (prompt, score, timestamp, session id) to feed both the dashboard and the guardrail-synthesis pipeline — a decoy interaction that isn't logged is a wasted attack sample.
- **Don't auto-deploy a generated guardrail without a validation gate**, at least while the project is being built. A newly synthesized Colang rule should be tested against a benign regression set before being hot-patched into production, so "self-healing" doesn't become "self-inflicted false positives."
- **Don't commit model weights, embeddings, or `.env` files.** These are large and/or secret; keep them gitignored, document how to regenerate/populate them.
- **Don't over-fit the demo to the happy path.** The panel will likely try edge cases live; the sieve's behavior on ambiguous prompts (neither clearly benign nor clearly malicious) should be a deliberate, explainable decision, not undefined behavior.

## 3. Error Handling & Failure Boundaries for AI Components

AI components fail differently from normal code — they can be slow, wrong, or subtly manipulated rather than crash cleanly. Handle each failure mode explicitly:

| Failure | Required behavior |
|---|---|
| **Ollama / model server unreachable or times out** | Fail closed for the sieve specifically: if the sieve cannot score a prompt, do **not** default to "safe" and forward to production — either return a graceful degraded response or route to a lightweight fallback check. Never silently skip the sieve. |
| **Sieve returns a low-confidence / borderline score** | Define an explicit middle band (not just a binary threshold) and a documented behavior for it (e.g. extra scrutiny turn, stricter RAG context) rather than treating "unsure" as either extreme. |
| **Decoy persona ("Sarah") is pushed to break character or reveal it's a decoy** | Treat this as a signal to capture and feed into guardrail synthesis, not just a UX bug — it's an attack pattern worth learning from. |
| **RAG retrieval returns no relevant public context** | The production chatbot should say it doesn't have that information rather than letting the LLM freely hallucinate an answer — especially important since "hallucination" is otherwise a deliberate feature of this system (in the decoy) and must stay contained there. |
| **Guardrail synthesis produces a malformed/invalid Colang rule** | Validate before hot-patch; reject and log rather than deploying a broken rule that could either block everyone or block no one. |
| **Dashboard/log pipeline is down** | Must never block the chat path — logging and detection are decoupled; a logging failure degrades observability, not user-facing behavior. |
| **Any component receiving unexpected/malformed input** | Validate at the boundary (Pydantic schemas in FastAPI) — don't pass unvalidated user input directly into prompts, container calls, or DB queries. |

## 4. Security Baseline (independent of the AI-specific rules above)

- Secrets (API keys if any are ever introduced, DB credentials) live in environment variables, never in code or committed config.
- All inputs into shell/container calls must be parameterized — never string-concatenate user input into a command.
- The admin/demo control panel must be authenticated, even for a local demo — it's the one surface that can trigger/toggle real system behavior.
