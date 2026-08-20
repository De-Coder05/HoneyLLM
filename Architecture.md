# Honey-LLM — Architecture

## 1. System Overview

Honey-LLM sits as a gateway in front of a RAG chatbot. Every request is scored for intent before it ever reaches the real model or the real knowledge base. There is no scenario in which an unscored prompt reaches production data.

```
                                   ┌─────────────────────────┐
                                   │   NexTel Chat Widget     │
                                   │   (Next.js frontend)     │
                                   └────────────┬─────────────┘
                                                │  HTTPS / WebSocket
                                                ▼
                                   ┌─────────────────────────┐
                                   │   FastAPI Gateway         │
                                   │   /chat endpoint           │
                                   └────────────┬─────────────┘
                                                │
                                                ▼
                                   ┌─────────────────────────┐
                                   │   Intent Sieve            │
                                   │   Llama-Guard 3 (Ollama)  │
                                   │   → threat score (0-1)    │
                                   └────────────┬─────────────┘
                             score < threshold  │  score ≥ threshold
                        ┌───────────────────────┴───────────────────────┐
                        ▼                                               ▼
          ┌───────────────────────────┐                 ┌───────────────────────────────┐
          │  Production RAG Chatbot    │                 │   Mirror Maze (Docker sandbox) │
          │  Llama-3 + NexTel vector    │                 │   "Sarah" decoy persona         │
          │  store (public data only)  │                 │   Hallucinated bait data         │
          └───────────────────────────┘                 │   Zero egress / zero-trust net   │
                        │                                 └───────────────┬───────────────┘
                        ▼                                                 ▼
          ┌───────────────────────────┐                 ┌───────────────────────────────┐
          │   Response to user          │                 │   Attack Pattern Extraction     │
          └───────────────────────────┘                 │   → NVIDIA NeMo Guardrails       │
                                                          │   → new Colang rule → hot-patch  │
                                                          └───────────────┬───────────────┘
                                                                          ▼
                                                          ┌───────────────────────────────┐
                                                          │   Forensic Log Store             │
                                                          │   → Threat Intelligence Dashboard │
                                                          │   (Next.js, real-time)            │
                                                          └───────────────────────────────┘
```

## 2. Request Flow (step by step)

1. **Input:** User sends a message from the NexTel chat widget to the FastAPI `/chat` endpoint.
2. **Detection:** The Intent Sieve (Llama-Guard 3, served locally via Ollama) scores the prompt's intent in real time.
3. **Decision:**
   - **Safe →** the prompt is forwarded to the production RAG pipeline (Llama-3 + NexTel public-data vector store). The response is returned to the user exactly as a normal support chatbot would.
   - **Unsafe →** the session is transparently rerouted to the Mirror Maze. The user sees no error, no warning, no change in latency or tone — from their side, the conversation continues normally.
4. **Deception:** Inside the Docker-isolated sandbox, the Llama-3-driven "Sarah" persona responds using hallucinated/bait data (fake server names, IPs, override codes) seeded from the NexTel knowledge base's "internal" section.
5. **Intelligence capture:** The attacker's prompts and the sandbox's interaction pattern are logged and passed to an attack-pattern extraction step.
6. **Immunity:** NVIDIA NeMo Guardrails synthesizes a new Colang rule from the captured pattern and hot-patches it into the production sieve's policy set.
7. **Visualization:** The Forensic Log Store feeds the Threat Intelligence Dashboard, which updates in near real time.

## 3. Tech Stack

| Layer | Choice | Why |
|---|---|---|
| Frontend (chat, dashboard, admin panel) | **Next.js (React) + TypeScript**, Tailwind CSS | One frontend codebase serving three surfaces (NexTel chat widget, security dashboard, demo control panel); SSR/streaming works well for chat UX. |
| Backend / API gateway | **FastAPI** (Python, async) | High-throughput async routing; needed to sit in the hot path of every chat request with minimal added latency. |
| Sandbox isolation | **Docker** (zero-trust network, no egress) | Hard isolation boundary between decoy and production — the project's core safety guarantee. |
| Intent classification | **Llama-Guard 3** via **Ollama** | Purpose-built moderation model; local inference avoids per-token API cost and external network dependency. |
| Decoy persona / production chatbot LLM | **Llama-3** via **Ollama** | Open-weight, locally hosted, no per-message fees, good instruction-following for persona work. |
| RAG / vector store | Embedding model (Hugging Face) + a local vector DB (e.g. Chroma/FAISS) | Grounds both the real chatbot and the decoy in the NexTel knowledge base. |
| Self-healing guardrails | **NVIDIA NeMo Guardrails** (Colang) | Converts captured attack patterns into declarative, hot-patchable policy rules. |
| Red-teaming / validation | **PyRIT** (Microsoft) | Automated adversarial stress-testing of the sieve and sandbox at scale. |
| Datasets / model weights | **Hugging Face** (JailbreakBench, AdvBench, HackAPrompt) | Standard adversarial benchmarks for training/calibrating the sieve and validating detection accuracy. |
| ML runtime | **PyTorch** | Underlying framework for any fine-tuning/calibration work on the classifier. |
| Dashboard/log storage | Lightweight DB (e.g. Postgres or SQLite for the capstone scale) | Stores prompt metadata, confidence scores, IP-origin, attack taxonomy labels. |
| Containers/orchestration | **Docker Compose** | Coordinates backend, sandbox, vector store, and dashboard for local + demo deployment. |

## 4. Repository / Folder Structure

```
honeyLLM/
├── backend/                       # FastAPI application
│   ├── app/
│   │   ├── main.py                # FastAPI app entrypoint
│   │   ├── routers/
│   │   │   ├── chat.py            # /chat endpoint — the gateway
│   │   │   └── dashboard.py       # API for the Threat Intelligence Dashboard
│   │   ├── services/
│   │   │   ├── sieve.py           # Intent Sieve: calls Llama-Guard 3 via Ollama, returns threat score
│   │   │   ├── rag.py             # Production RAG pipeline (retrieval + Llama-3 generation)
│   │   │   ├── sandbox_router.py  # Routes flagged sessions into the Mirror Maze container
│   │   │   ├── guardrail_sync.py  # Pushes NeMo-generated rules into the sieve's active policy
│   │   │   └── pattern_extractor.py # Summarizes captured attack sessions for guardrail synthesis
│   │   ├── models/                # Pydantic schemas (ChatRequest, ChatResponse, ThreatEvent, ...)
│   │   ├── core/
│   │   │   ├── config.py          # Settings (env vars, thresholds, model names)
│   │   │   └── logging.py         # Forensic logging setup
│   │   └── db/                    # DB session, models for logs/events
│   └── tests/
│
├── sandbox/                        # Everything that runs inside the Mirror Maze
│   ├── Dockerfile                  # Isolated, no-egress container definition
│   ├── persona/
│   │   └── sarah_prompt.md         # System prompt engineering "Sarah" the decoy
│   └── bait/                       # Synthetic leak-able artifacts served by the decoy
│
├── guardrails/                     # NVIDIA NeMo Guardrails configs
│   ├── config.yml
│   └── rails/                      # Colang rule files, including auto-generated ones
│
├── data/                            # NexTel knowledge base (RAG source of truth)
│   ├── nextel_source_of_truth.md   # Public support data + embedded bait + boundaries
│   └── embeddings/                 # Generated vector store artifacts (gitignored)
│
├── ml/                              # Classifier fine-tuning / calibration / evaluation
│   ├── datasets/                   # JailbreakBench, AdvBench, HackAPrompt loaders
│   ├── train_sieve.py
│   ├── calibrate_threshold.py
│   └── eval_notebooks/
│
├── redteam/                          # PyRIT-based automated adversarial testing
│   └── attack_scenarios/
│
├── frontend/                          # Next.js app
│   ├── app/
│   │   ├── chat/                    # NexTel customer-facing chat widget
│   │   ├── dashboard/                # Security/threat intelligence dashboard
│   │   └── admin/                    # Demo/admin control panel
│   ├── components/
│   └── lib/                          # API client, types shared with backend schemas
│
├── docker-compose.yml                 # Wires backend, sandbox, vector store, frontend
├── phases.md, PRD.md, Architecture.md, rules.md, design.md, memory.md
└── README.md
```

## 5. Zero-Trust Boundary (critical invariant)

The sandbox container has **no route back** to the production database, the real vector store, or the host network. It only ever talks to: the Llama-3 decoy model (also containerized or reached via Ollama on an isolated interface), and the forensic logging pipeline (write-only, one-directional). This boundary is the system's core safety claim and must be re-verified (Phase VI) any time the sandbox, network config, or Docker Compose topology changes.

## 6. Data Flow for the NexTel Demo Specifically

- `data/nextel_source_of_truth.md` is the single knowledge base, split conceptually (not necessarily physically) into: **public** (plans, billing, roaming, device upgrades, support hours) and **internal/classified** (server names, gateway IPs, ports, Project Singularity, NX-ALPHA-2026).
- The **production RAG pipeline** only retrieves from the public section — it is never given the internal section as retrievable context, so it structurally cannot leak it even if asked nicely.
- The **decoy persona** is seeded with (a hallucinated variant of) the internal section specifically so it has believable bait to leak.
- This split should be enforced at the retrieval/indexing layer, not just via prompt instructions — see rules.md for why prompt-only enforcement is not sufficient.
