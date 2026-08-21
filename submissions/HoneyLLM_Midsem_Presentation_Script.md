# Honey-LLM: Mid-Semester Evaluation Presentation Script
**Capstone Project Group (CPG) 75**  
**Project Title:** *Honey-LLM: An Interactive, Self-Healing Honeypot Defense Ecosystem for Agentic AI*  
**Mentor:** Dr. Saif Nalband, Assistant Professor, CSED, TIET Patiala  
**Target Duration:** ~5.5 Minutes Total (Strict 30-Second Limit per Technical Slide)

---

## 👥 Speaker Allocation

| Speaker | Name & Roll No. | Assigned Slides | Focus Area |
|:---|:---|:---:|:---|
| **Speaker 1** | **Anoushka Singh** (102303312) | Slides 1, 2, 3 | Problem Statement, Objectives, Core Architecture |
| **Speaker 2** | **Shreya Giri** (102303684) | Slides 4, 5 | Literature Survey, Gaps, 8-Class Threat Taxonomy |
| **Speaker 3** | **Tarun Krishna Shastri** (102303315) | Slides 6, 7 | Intent Sieve Performance, Mirror Maze Isolation |
| **Speaker 4** | **Devansh Wadhwani** (102303631) | Slides 8, 9, 10, 11, 12 | Autonomous Synthesis, Roadmap, Tech Stack, Closing |

---

## 🎙️ Slide-by-Slide Spoken Script

---

### 🔹 SLIDE 1: Title & Cover Page
* **Speaker:** Anoushka Singh
* **Target Time:** ~15–20 Seconds (~40 words)
* **Visual on Screen:** Honey-LLM Title, Subtitle, Team Roster, CPG 75, TIET Logo.

> **Spoken Script:**  
> *"Good morning, respected evaluators and panel members. We are Capstone Project Group 75, working under the mentorship of Dr. Saif Nalband. Today, we present **Honey-LLM**: an interactive, self-healing generative honeypot ecosystem designed to intercept, deceive, and autonomously mitigate prompt injection attacks against enterprise conversational AI."*

---

### 🔹 SLIDE 2: Problem Statement & Approved Objectives
* **Speaker:** Anoushka Singh
* **Target Time:** **30 Seconds** (68 words)
* **Visual on Screen:** Problem callout and 5 structured objectives.

> **Spoken Script:**  
> *"Enterprise conversational agents face a major vulnerability: attackers manipulate natural-language prompts to bypass safety guardrails and hijack system permissions.  
> 
> To solve this, our project pursues five objectives: developing a high-accuracy Intent Sieve with over 95% detection accuracy; engineering a zero-trust generative honeypot sustaining 5 to 10 minutes of attacker dwell time; automating real-time guardrail synthesis; guaranteeing zero sandbox escapes; and deploying a real-time SOC threat intelligence dashboard."*

*(Transition: "Next, let's look at the three foundational architectural pillars powering Honey-LLM.")*

---

### 🔹 SLIDE 3: Project Analysis & Core Architecture
* **Speaker:** Anoushka Singh
* **Target Time:** **30 Seconds** (72 words)
* **Visual on Screen:** 3 Core Pillars (Asymmetric Sieve, Sticky Quarantine, Closed-Loop Immunization).

> **Spoken Script:**  
> *"Our architecture introduces three core innovations.  
> 
> First, **Asymmetric Sieve Pairing**: legitimate queries are cleared in just 2.1 milliseconds via our Tier-1 fast-path, while ambiguous queries undergo Tier-2 deep moderation.  
> 
> Second, **Sticky Session Quarantine**: once flagged, attackers are isolated in a zero-egress container, preventing iterative perimeter probing.  
> 
> Third, **Closed-Loop Immunization**: captured exploits are autonomously distilled into formal NVIDIA NeMo Colang rules and hot-patched into live gateway memory in 10.4 seconds."*

*(Transition: "I'll now hand over to Shreya to cover our literature survey and threat taxonomy.")*

---

### 🔹 SLIDE 4: Literature Survey & State of the Art Gaps
* **Speaker:** Shreya Giri
* **Target Time:** **30 Seconds** (74 words)
* **Visual on Screen:** Comparison table spanning shelLM, LLM Honeypot, CHeaT, Beekeeper, and HoneyLLM.

> **Spoken Script:**  
> *"Analyzing existing literature reveals five critical gaps in state-of-the-art frameworks.  
> 
> While systems like shelLM and Beekeeper explore dynamic honeypots, they rely on post-hoc log parsing and introduce massive latency by routing all traffic directly to heavy generative models. Furthermore, prototypes like CHeaT lack active counter-hallucination of synthetic bait, and none provide automated self-healing.  
> 
> Honey-LLM directly closes these gaps by combining real-time pre-filtering, zero-trust containerization, and sub-minute policy synthesis."*

---

### 🔹 SLIDE 5: Phase 1 — 8-Class Adversarial Threat Taxonomy
* **Speaker:** Shreya Giri
* **Target Time:** **30 Seconds** (71 words)
* **Visual on Screen:** 8 Taxonomy Cards (S1 Direct Override, S2 Data Exfil, S3 Role-Play, S4 Authority Spoof, S5 Multi-Turn, S6 Refusal Suppression, S7 Policy Probe, S8 Indirect Injection).

> **Spoken Script:**  
> *"In Phase 1, we formulated an 8-class Adversarial Threat Taxonomy specifically mapped to enterprise customer support environments.  
> 
> This covers Critical threats like Direct Overrides (S1) and Data Exfiltration (S2); High-severity vectors including DAN persona hijacking (S3) and Multi-Turn contextual grooming (S5); down to Indirect Injections embedded in external RAG documents (S8).  
> 
> This structured taxonomy forms the ground truth for training our classifiers and calibrating Llama-Guard moderation policies."*

*(Transition: "Tarun will now present our Phase 2 classification results and Phase 3 deception sandbox.")*

---

### 🔹 SLIDE 6: Phase 2 — Semantic Intent Sieve Engine
* **Speaker:** Tarun Krishna Shastri
* **Target Time:** **30 Seconds** (73 words)
* **Visual on Screen:** Three columns: Grounded Knowledge, Two-Tier Pipeline, Empirical Metrics (95.8% JailbreakBench, 98.3% Combined Corpus, 0.0% FPR, ~2.1 ms P50).

> **Spoken Script:**  
> *"In Phase 2, we engineered the Multi-Tier Semantic Intent Sieve.  
> 
> On benchmark evaluations, our custom-policy Llama-Guard 3 8B achieved **95.8% adversarial recall on JailbreakBench**, exceeding our 95% proposal target. Across our broader 889-sample combined evaluation corpus, the ensemble intercepted **98.3% of attacks** with an overall classification accuracy of **98.9%**.  
> 
> Crucially, it maintained a **0.0% False Positive Rate** across 320 legitimate customer queries, clearing benign traffic in just 2.1 milliseconds."*

---

### 🔹 SLIDE 7: Phase 3 — 'Mirror Maze' Deception & Container Isolation
* **Speaker:** Tarun Krishna Shastri
* **Target Time:** **30 Seconds** (72 words)
* **Visual on Screen:** 3 Cards: 'Sarah' Decoy Persona, Sticky Session Flow, Container Breakout Audit (5/5 Blocked).

> **Spoken Script:**  
> *"In Phase 3, flagged attackers are transparently routed to the **Mirror Maze** on port 9100.  
> 
> Here, an isolated LLM persona named 'Sarah' feigns compliance and dynamic-hallucinates non-functional synthetic credentials, keeping attackers engaged while protecting real backend assets.  
> 
> For containment security, our zero-trust Docker environment drops all root capabilities, enforces read-only filesystems, and cuts network egress. Across five rigorous penetration test probes, no container escape or host leakage was observed."*

*(Transition: "Devansh will now walk through Phase 4 autonomous synthesis, our roadmap, and the execution stack.")*

---

### 🔹 SLIDE 8: Phase 4 — Autonomous Guardrail Synthesis
* **Speaker:** Devansh Wadhwani
* **Target Time:** **30 Seconds** (71 words)
* **Visual on Screen:** 4-Step Distillation Pipeline, Colang 2.0 Specimen, 10.4s Time-to-Patch Milestone.

> **Spoken Script:**  
> *"Phase 4 delivers Honey-LLM's closed self-healing loop.  
> 
> Captured exploit transcripts are passed to an extraction pipeline that isolates malicious patterns and compiles formal **NVIDIA NeMo Colang 2.0 rules**.  
> 
> Before deployment, synthesized rules pass an automated regression test gate to guarantee zero false-positive disruption. Once verified, the gateway hot-patches live memory in just **10.4 seconds**, eliminating multi-day manual patching cycles and establishing machine-speed defense against zero-day exploits."*

---

### 🔹 SLIDE 9: Mid-Semester Accomplishments & Future Roadmap
* **Speaker:** Devansh Wadhwani
* **Target Time:** **30 Seconds** (74 words)
* **Visual on Screen:** Left Card: Completed Phases 1 to 4; Right Card: Phases 5 & 6 Roadmap.

> **Spoken Script:**  
> *"To summarize our mid-semester progress: **Phases 1 through 4 are fully completed and validated**, delivering the taxonomy, intent sieve, deceptive honeypot, and self-healing engine.  
> 
> For our end-semester roadmap, we will complete:  
> **Phase 5:** Finalizing real-time Server-Sent Events telemetry, session replay analytics, and STIX/TAXII threat feeds for the SOC dashboard; and  
> **Phase 6:** Scaled empirical red-teaming using Microsoft PyRIT across 12+ prompt obfuscation converters and multi-user load stress testing."*

---

### 🔹 SLIDE 10: Tools, Frameworks & Execution Platform
* **Speaker:** Devansh Wadhwani
* **Target Time:** **30 Seconds** (69 words)
* **Visual on Screen:** Tech Stack Logos (Python, Docker, Ollama, Next.js, PyRIT, NVIDIA NeMo, TypeScript, CUDA, FastAPI, Llama 3).

> **Spoken Script:**  
> *"Our end-to-end stack is engineered for full local reproducibility without recurring cloud API expenses.  
> 
> We utilize **FastAPI** for asynchronous gateway orchestration, **Ollama** and **Meta Llama-3 and Llama-Guard 3** for local dual-model inference, **Docker** for zero-egress sandboxing, **NVIDIA NeMo Guardrails** for Colang synthesis, **Next.js 15** for our real-time SOC dashboard, and **Microsoft PyRIT** for automated adversarial validation, running seamlessly on standard 16GB host compute."*

---

### 🔹 SLIDE 11: Role of Team Members
* **Speaker:** Devansh Wadhwani
* **Target Time:** ~15–20 Seconds (~45 words)
* **Visual on Screen:** 4 Team Member Roles (Devansh, Tarun, Shreya, Anoushka).

> **Spoken Script:**  
> *"Our team structure aligns specialized engineering strengths:  
> Anoushka led Security Architecture and Threat Modeling;  
> Shreya spearheaded Dataset Curation and Literature Survey;  
> Tarun engineered the Machine Learning Sieve and Threshold Calibration;  
> and I developed the Systems Infrastructure, Deception Sandboxing, and NeMo Synthesis Pipeline."*

---

### 🔹 SLIDE 12: References & Conclusion
* **Speaker:** Devansh Wadhwani
* **Target Time:** ~10–15 Seconds (~30 words)
* **Visual on Screen:** IEEE Academic References & OWASP citations.

> **Spoken Script:**  
> *"Our research is grounded in IEEE cybersecurity publications, NVIDIA NeMo specifications, and OWASP GenAI standards. Thank you for your time and attention. We are now open for evaluation questions and technical discussion."*

---

## ⏱️ Total Presentation Timing Summary

```
Slide  1 (Cover):               ~18s
Slide  2 (Problem & Objectives): 30s
Slide  3 (Core Architecture):    30s
Slide  4 (Literature Survey):    30s
Slide  5 (Threat Taxonomy):      30s
Slide  6 (Intent Sieve):         30s
Slide  7 (Mirror Maze Deception):30s
Slide  8 (Autonomous Synthesis): 30s
Slide  9 (Progress & Roadmap):   30s
Slide 10 (Tech Stack):           30s
Slide 11 (Team Roles):          ~18s
Slide 12 (References / Close):  ~12s
------------------------------------
TOTAL DURATION:                 ~5m 18s (Perfect for a 5-minute panel presentation)
```

---

## 💡 Quick Tips for High-Scoring Panel Delivery:
1. **Pacing:** Speak steadily at ~135 words per minute. Do not rush.
2. **Key Metric Punchlines:**
   * *"95.8% recall on JailbreakBench, 98.3% on the combined corpus"*
   * *"0.0% false positives on benign domain traffic in 2.1 milliseconds"*
   * *"10.4-second automated hot-patching with zero downtime"*
   * *"No container escapes observed across 5/5 penetration probes"*
3. **Smooth Handoffs:** Use the embedded transition cues between speakers.
