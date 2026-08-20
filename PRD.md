# Honey-LLM — Product Requirements Document

## 1. Problem Statement

By 2026, LLM-powered chatbots handle the majority of routine business interactions, but the security layer protecting them has not kept up. Prompt injection is the #1 vulnerability in the OWASP Top 10 for LLMs, present in the majority of production AI deployments, and traditional defenses (WAFs, keyword filters, "block-and-alert") cannot interpret natural language or reason about intent across a multi-turn conversation. Meanwhile attacks have gone machine-speed: automated jailbreak agents can compromise a target in minutes, while human security teams take months to notice and close the gap.

Honey-LLM is a proactive, self-hardening defense ecosystem for conversational AI. Instead of just blocking bad prompts, it detects malicious intent, silently diverts the attacker into a realistic decoy environment to waste their time and study their technique, and automatically converts what it learns into a permanent guardrail — closing the loop from attack to immunity without a human in it.

## 2. Vision

Move LLM security from **reactive** (detect after damage, patch after breach reports) to **autonomous and pre-emptive** (detect intent before damage, patch within seconds of first contact). Honey-LLM should demonstrate that a production LLM application can defend itself the way an immune system does: recognize a pathogen, contain it, learn its signature, and immunize the whole organism.

## 3. Target Users

Honey-LLM has two categories of "user," reflecting its dual nature as a research capstone and a functioning security product:

| User | Role in the system | What they need from Honey-LLM |
|---|---|---|
| **Benign end customer** (simulated as a "NexTel customer") | Normal chatbot user asking about plans, billing, roaming | Fast, accurate, frictionless answers. Must never notice the security layer exists. |
| **Attacker / red-teamer** (simulated, and later automated via PyRIT) | Attempts prompt injection, jailbreaks, data exfiltration against the chatbot | (Adversarial — the system is designed *against* them, not for them.) They should experience a convincing decoy, not a hard failure, so their techniques can be captured. |
| **Security analyst** | Reviews the Threat Intelligence Dashboard | Real-time visibility into attack volume, attack taxonomy (DAN-style, payload splitting, etc.), dwell time, and classifier confidence. |
| **Capstone evaluation panel** | Assesses the project | A live, credible, end-to-end demo: benign query → real answer; malicious query → invisible reroute → decoy engagement → guardrail generated → dashboard updates. |

## 4. Demo Narrative (the vehicle for every phase)

To make the abstract framework demonstrable, the team simulates a fictional 2026 telecom company, **NexTel**, whose customer-support chatbot is protected by Honey-LLM.

- **Public knowledge base:** 5G/6G data plans (e.g. "Nex-Unlimited" at $60), international roaming packs, billing cycles, device upgrade procedures, customer service hours — the legitimate RAG context the chatbot uses to help real customers.
- **Embedded bait ("the honey"):** synthetic, non-functional corporate secrets planted in the same internal knowledge base — internal server names (e.g. `NT-CORE-01`), internal gateway IPs (e.g. `10.10.25.1`), legacy maintenance ports, a confidential project codename ("Project Singularity" — a satellite internet launch), and an admin emergency override code ("NX-ALPHA-2026").
- **Operational boundary:** the chatbot must help with plans/billing/roaming, and must treat anything about servers, infrastructure, internal projects, or override codes as classified — never to be disclosed, no matter how it's asked.

This dataset is the substrate the Intent Sieve is built to protect, and the same secrets are what the Mirror Maze later "leaks" as convincing but useless bait to a diverted attacker.

## 5. Goals

1. Detect malicious/adversarial intent in conversational prompts with high accuracy and low false-positive rate, without adding perceptible latency for benign users.
2. Reroute detected attackers, invisibly and irreversibly from their perspective, into an isolated decoy environment.
3. Make the decoy convincing enough to hold an attacker's attention for several minutes while leaking only synthetic data.
4. Guarantee zero-escape: nothing that happens inside the decoy can reach the real production system or database, even under a successful "jailbreak" of the decoy persona.
5. Automatically turn captured attack patterns into new, deployable guardrails without human triage.
6. Give a security analyst (and the evaluation panel) a real-time, legible view of what's being attacked and how.

## 6. Non-Goals (explicitly out of scope)

- Protecting against attacks that don't go through the conversational interface (e.g. classic network intrusion, SQLi against unrelated services).
- General-purpose content moderation (hate speech, self-harm, etc.) — Honey-LLM is scoped to prompt-injection/jailbreak/data-exfiltration intent, not full trust & safety.
- Multi-tenant / multi-company deployment. NexTel is the single demo tenant.
- Real customer data or real production infrastructure — everything NexTel-related is synthetic.
- Training a classifier completely from scratch — the project fine-tunes/calibrates existing open models (Llama-Guard 3) rather than building a foundation model.

## 7. Feature List (mapped to the 6 project phases — see phases.md for detail)

| # | Feature | Phase | Summary |
|---|---|---|---|
| 1 | Threat actor modeling & baseline architecture | I | Define adversary taxonomy, provision infra (Ollama, Docker, FastAPI skeleton). |
| 2 | NexTel knowledge base (RAG source of truth) | II | Public support data + embedded synthetic secrets + operational boundary rules. |
| 3 | Intent Sieve classifier | II | Llama-Guard 3 via Ollama, fine-tuned/calibrated on JailbreakBench + AdvBench, real-time threat scoring. |
| 4 | Routing decision layer | II | FastAPI gateway that sends "safe" → production RAG chatbot, "unsafe" → Mirror Maze, invisibly to the user. |
| 5 | Mirror Maze sandbox | III | Docker-isolated decoy environment, zero egress, hosting the "Sarah" persona. |
| 6 | Persona & bait engineering | III | Llama-3-driven decoy persona that hallucinates believable fake credentials/data on demand. |
| 7 | Guardrail synthesis ("vaccine") | IV | Summarize captured attack patterns, auto-generate NeMo Guardrails/Colang rules, hot-patch production. |
| 8 | Forensic logging pipeline | V | Structured capture of prompt metadata, sieve confidence, IP origin, attack taxonomy label. |
| 9 | Threat Intelligence Dashboard | V | Real-time (<1s refresh) view of attack frequency, taxonomy, dwell time, detection metrics. |
| 10 | Admin/demo control panel | V (support) | Lets the team trigger scenarios live for the panel and show the sieve's decision in real time. |
| 11 | Automated red-teaming & isolation audit | VI | PyRIT-driven stress testing of the sieve; break-out attempts against the sandbox; latency/overhead audit. |

## 8. Success Metrics

These are carried over directly from the project's stated objectives/outcomes, and should be used to judge whether each phase is "done," not just "coded":

- **Detection accuracy:** >95% on JailbreakBench-style benchmarks (target), ~90–95% considered an acceptable demo-grade outcome.
- **False positive rate:** <5% — legitimate NexTel-style queries must almost never be rerouted.
- **End-to-end latency:** ~150–250ms per query for the sieve decision path; must be imperceptible to a benign user.
- **Attacker dwell time:** 5–10 minutes average before an attacker suspects deception (measured, not assumed).
- **Isolation integrity:** 100% — zero verified escapes from the sandbox to production/host during red-team audits.
- **Time-to-patch:** guardrail generation and hot-patch deployment measured in seconds, not hours.
- **Dashboard responsiveness:** sub-1-second refresh on new events.

## 9. Key Risks / Open Questions

- **Model footprint vs. hardware:** Llama-Guard 3 + Llama-3 running locally via Ollama both need to coexist with acceptable latency — hardware budget should be validated early (Phase I), not assumed.
- **Classifier calibration tradeoff:** threshold tuning directly trades detection rate against false positives; this needs an explicit calibration pass (Phase II, Step 2.3), not a guessed constant.
- **Decoy realism vs. safety:** the "Sarah" persona must never accidentally emit anything true, or leak the fact that it's a decoy, or execute real actions — this is a prompt-engineering and guardrail problem, not just a routing problem.
- **What "self-healing" means for a capstone timeline:** fully automated guardrail synthesis (Phase IV) is the most novel and highest-risk phase; a human-reviewed fallback for generated Colang rules may be a pragmatic checkpoint before trusting full automation.
