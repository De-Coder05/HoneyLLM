# Ci 

THAPAR INSTITUTE OF ENGINEERING& TECHNOLOGY Deemed to be University 

## **Table of Contents** 

|**Li**|**st of **|**Figures**||
|---|---|---|---|
|**Li**|**st of **|**Tables**||
|**M**|**ento**|**r Consent Form**||
|**1**|**Pro**|**ject Overview**|**1**|
|**2**|**Nee**|**d Analysis**|**2**|
||2.1|The “Smart Mirror” Trap: Enterprise Adoption vs. Defensive Lag . . . . .|2|
||2.2|The Shift: Machine-Speed Autonomous Warfare . . . . . . . . . . . . . . .|2|
||2.3|The “Shadow Trust” Gap: Vulnerability of the Semantic Layer . . . . . . .|2|
||2.4|The 16-Minute Failure Window: Addressing Reactive Lag . . . . . . . . . .|3|
|**3**|**Lite**|**rature Survey**|**4**|
||3.1|LLM in the Shell: Generative Honeypots [10] . . . . . . . . . . . . . . . . .|4|
||3.2|LLM Honeypot: Leveraging LLMs as Interactive Honeypot Systems [8] . .|4|
||3.3|HoneyLLM: Enabling Shell Honeypots with Large Language Models [4] . .|5|
||3.4|Cloak, Honey, Trap: Proactive Defenses Against LLM Agents [2] . . . . . .|5|
||3.5|Beekeeper: Accelerating Honeypot Analysis with LLM-Driven Feedback [5]|6|
||3.6|Comparative Summary . . . . . . . . . . . . . . . . . . . . . . . . . . . . .|6|
|**4**|**Obj**|**ectives**|**8**|
|**5**|**Met**|**hodology**|**9**|
||5.1|Phase I: Adversarial Profling and System Architecture Design . . . . . . .|9|
||5.2|Phase II: Development of the Semantic Intent Sieve . . . . . . . . . . . . .|10|
||5.3|Phase III: Engineered Deception and High-Interaction Sandboxing . . . . .|10|
||5.4|Phase IV: Autonomous Guardrail Synthesis and Policy Hardening . . . . .|10|
||5.5|Phase V: Forensic Telemetry and Intelligence Visualization . . . . . . . . .|11|
||5.6|Phase VI: Empirical Validation and Adversarial Red-Teaming<br>. . . . . . .|11|
|**6**|**Wo**|**rk Plan**|**12**|
|**7**|**Pro**|**ject Outcomes**|**13**|



|**8**<br>**Individual Roles**|**14**|
|---|---|
|**9**<br>**Course Subjects**|**15**|
|**References**|**16**|



## **List of Figures** 

|1|Phase-wise Methodology Roadmap<br>. . . . . . . . . . . . . . . . . . . . . .<br>9|
|---|---|
|2|Project Work Plan – Gantt Chart (January – December) . . . . . . . . . .<br>12|



## **List of Tables** 

2 Comparative Summary of Literature Survey . . . . . . . . . . . . . . . . . 6 



## **1 Project Overview** 

In the modern digital landscape of 2026, a critical vulnerability is exposed by the rapid integration of Large Language Models (LLMs) into core business infrastructures [7]. While productivity is significantly enhanced, a new frontier of “semantic warfare” is opened, where traditional defenses are rendered obsolete by the deceptive nature of prompt injection attacks [9]. It is observed that standard security measures, designed for static code exploits, are powerless against malicious instructions disguised as natural, persuasive conversation. 

As autonomous AI agents begin to outnumber human users in corporate networks, the traditional “block-and-alert” philosophy is found to be insufficient. Consequently, the development of a defense mechanism capable of understanding semantic intent using machine learning techniques becomes essential [3]. 

To address these risks and provide a more robust defensive posture, a proactive framework titled **Honey-LLM** is introduced. A specialized machine learning classifier, known as the “ **Intent Sieve** ,” is employed to scrutinize every interaction for hidden malicious intent, utilizing advanced semantic analysis to calculate a real-time threat score [3]. When a threshold for adversarial behavior is exceeded, the attacker is seamlessly and invisibly redirected into a fully isolated “ **Mirror Maze** ”, a generative sandbox environment hosted on zero-trust Docker architecture. 

Within this decoy system, a fine-tuned LLM is utilized to mimic a vulnerable system. High-fidelity realism is maintained through the dynamic generation of “hallucinated” responses, a known characteristic of generative models [7, 1]. 

The ultimate goal of this research is the transition from static, reactive security to an autonomous, self-hardening ecosystem. 

1 

## **2 Need Analysis** 

### **2.1 The “Smart Mirror” Trap: Enterprise Adoption vs. Defensive Lag** 

While over **91% of enterprise leaders** are under extreme pressure to implement AI in 2026, defensive capabilities have failed to keep pace. Statistics indicate that **97% of organizations** that suffered ...AI-related breaches lacked even basic access controls, particularly against prompt injection vulnerabilities identified by OWASP [9]. This “defensive lag” makes the implementation of generative honeypots essential; research shows that high-interaction generative environments can increase attacker engagement and “dwell time” by **3–5** _×_ , providing the necessary window to capture and analyze complex zeroday techniques. 

### **2.2 The Shift: Machine-Speed Autonomous Warfare** 

By 2026, it is projected that **over 80% of all web and routine customer interactions** are ...handled by autonomous AI agents powered by advanced LLM architectures [7].. This shift has enabled the rise of “machine-speed” attacks; LLM-powered pentesting agents like ARACNE can achieve successful compromises in **less than 5 actions** . Furthermore, AIorchestrated cyber operations have compressed traditional 3-to-6-month attack campaigns into just **24 to 48 hours** , rendering human-led reactive security obsolete. 

### **2.3 The “Shadow Trust” Gap: Vulnerability of the Semantic Layer** 

Prompt Injection remains the **#1 critical vulnerability** in the OWASP Top 10 for LLMs [9], appearing in over **73% of production AI deployments** assessed during security audits. Traditional Web Application Firewalls (WAFs) are ineffective here because they cannot interpret natural language or track context across multiple conversation turns. Independent red-teaming has shown that while a single jailbreak attempt might fail, persistence-scaled attacks reach a **78.5% success rate** in multi-turn scenarios, successfully tricking agents into leaking sensitive data or executing malicious code. 

2 

### **2.4 The 16-Minute Failure Window: Addressing Reactive Lag** 

Current security operations suffer from a fatal “Reactive Lag”. Enterprise analysis has found that uncontrolled AI agents reach their first critical security failure in a median time of just **16 minutes** . In contrast, the average time for a human-led Security Operations Center (SOC) to even discover a standard breach is **204 days** . Honey-LLM is required to close this gap by utilizing **Automated Guardrail Synthesis** to convert captured attack patterns into protection rules instantly, rather than waiting for days of human triage. Organizations using such AI-powered autonomous defenses have demonstrated the ability to contain breaches **108 days faster** , saving an average of **$1.76M to $2.22M per incident** .Machine learning-driven adaptive security mechanisms are required to reduce this lag [3]. 

3 

## **3 Literature Survey** 

### **3.1 LLM in the Shell: Generative Honeypots [10]** 

The paper _“LLM in the Shell: Generative Honeypots”_ explores the use of Large Language Models to enhance the realism of cybersecurity honeypots. Traditional honeypots rely on static scripts and predefined responses, making them predictable and easier for skilled attackers to detect. To address this limitation, the authors propose a system called _shelLM_ , which simulates a realistic Linux command-line environment using an LLM. 

Unlike conventional systems, shelLM dynamically generates responses to attacker commands, enabling it to handle previously unseen inputs while maintaining the illusion of a real system. Experimental evaluation showed a True Negative Rate of around 0.90, indicating that most users perceived the simulated environment as genuine. 

However, the approach focuses mainly on improving interaction realism and does not include mechanisms for detecting malicious intent or strengthening system defenses. The proposed **Honey-LLM** framework extends this idea by introducing an _Intent Sieve_ that detects malicious prompts and redirects attackers to a controlled environment before they reach production systems. 

### **3.2 LLM Honeypot: Leveraging LLMs as Interactive Honeypot Systems [8]** 

This work proposes an LLM-based honeypot framework trained on attacker command logs, Linux documentation, and system behavior data. The model generates realistic system responses, allowing the honeypot to closely mimic actual operating systems. 

The authors evaluate response quality using similarity metrics such as Cosine Similarity, Jaro–Winkler Distance, and Levenshtein Distance. Results show that LLM-generated outputs closely resemble real system responses, enhancing credibility and increasing attacker engagement. The system also logs attacker commands for threat intelligence collection and behavioral analysis. 

Despite its effectiveness in improving interaction quality and data collection, the framework primarily focuses on deception and monitoring rather than active defense. In contrast, the proposed Honey-LLM system integrates deception into the production pipeline, enabling real-time detection of malicious users and automatic redirection to a honeypot 

4 

environment. 

### **3.3 HoneyLLM: Enabling Shell Honeypots with Large Language Models [4]** 

Presented at IEEE CNS 2024, this paper introduces a shell-based honeypot architecture powered by LLMs. The system generates contextual command-line responses using prompt engineering and contextual reasoning, allowing it to simulate authentic Linux environments and maintain coherent attacker interactions. 

The approach improves engagement and enables more detailed threat intelligence collection compared to static honeypots. However, it primarily focuses on enhancing realism within the honeypot environment. 

The proposed Honey-LLM framework extends this concept by integrating an _Intent-Aware Detection Layer_ that classifies user prompts in real time to distinguish legitimate users from attackers. Malicious users are redirected into a generative deception sandbox, where the system produces fake credentials, documents, and artifacts to prolong engagement. Additionally, _Automated Guardrail Synthesis_ converts captured attack prompts into security rules, transforming the system into a self-adaptive and proactive defense mechanism. 

### **3.4 Cloak, Honey, Trap: Proactive Defenses Against LLM Agents [2]** 

This study, presented at the USENIX Security Symposium 2025, introduces the _CHeaT (Cloak–Honey–Trap)_ framework to defend against autonomous LLM-driven attackers. The framework uses cloaking techniques, honey tokens, and trap inputs to detect and disrupt malicious agents performing reconnaissance and exploitation. 

Experimental results across Capture-the-Flag environments demonstrate that these strategies effectively prevent system compromise by exploiting weaknesses in LLM reasoning. While the framework focuses on defending against AI-driven attackers, it does not emphasize interactive deception environments. 

The proposed Honey-LLM system builds upon this idea by combining proactive defense with LLM-powered honeypots, enabling real-time attacker engagement, adaptive responses, and automated threat intelligence collection. 

5 

### **3.5 Beekeeper: Accelerating Honeypot Analysis with LLM-Driven Feedback [5]** 

The _Beekeeper_ system, presented at USENIX Security 2025, uses an LLM as an automated attacker to evaluate honeypot performance. It interacts with honeypots, identifies weaknesses, and generates feedback to improve realism and effectiveness. 

This framework serves as a testing and auditing tool, helping developers refine honeypot designs before deployment. However, it does not directly protect production systems from real attackers. 

In contrast, the proposed Honey-LLM system operates as an active defense layer. It incorporates malicious prompt detection via the Intent Sieve, hallucination-driven deception, and automated guardrail synthesis to continuously improve system security. This transforms honeypots from passive research tools into dynamic, autonomous cybersecurity defense systems. 

### **3.6 Comparative Summary** 

Table 2: Comparative Summary of Literature Survey 

|**Paper**|**Approach**|**Key Con-**<br>**tribution**|**State of**<br>**the Art**|**Research**<br>**Gap**|**Contrast**<br>**with**<br>**Honey-**<br>**LLM**|
|---|---|---|---|---|---|
|LLM in the|LLM-|First use of|Establishes|No intent|Adds Intent|
|Shell:<br>Generative|driven<br>shell|LLMs for<br>dynamic|LLM-<br>based|detection<br>before|Sieve to<br>detect|
|Honeypots|simulation|Linux shell|responses|interaction;|attackers|
|(shelLM)||simulation;|as better|no feedback|_before_|
|[10]||handles<br>unseen<br>attacker<br>commands|than static<br>honeypots;<br>high<br>realism|loop;<br>limited to<br>CLI|interaction|



6 

|**Paper**|**Approach**|**Key Con-**<br>**tribution**|**State of**<br>**the Art**|**Research**<br>**Gap**|**Contrast**<br>**with**<br>**Honey-**<br>**LLM**|
|---|---|---|---|---|---|
|LLM|LLM-|Uses attacker|Introduces|Passive|Integrates|
|Honeypot:|driven,|logs + Linux|quantita-|system; no|deception|
|Advanced|threat in-|docs;|tive|real-time|into|
|Interactive|telligence|validates|realism|protection|production|
|Honeypot||realism via|metrics;|or|with|
|Systems [8]||similarity<br>metrics|improves<br>threat<br>intel<br>collection|adaptation|automatic<br>attacker<br>redirection|
|HoneyLLM:<br>Enabling<br>Shell<br>Honeypots<br>with LLMs<br>[4]|LLM-<br>driven,<br>contextual<br>shell|Prompt<br>engineering<br>for coherent<br>and<br>contextual<br>shell<br>responses|Improves<br>attacker<br>engage-<br>ment and<br>dwell time|Only<br>shell-based;<br>no intent<br>classifca-<br>tion; no rule<br>generation|Adds intent<br>detection,<br>sandboxing,<br>and<br>automated<br>guardrail<br>synthesis|
|Cloak,<br>Honey,|Proactive<br>defense,|Cloaking,<br>honey|First<br>proactive|Limited to<br>AI|Extends to<br>real-time|
|Trap|deception|tokens, and|defense|attackers in|honeypot|
|(CHeaT)<br>[2]|tokens|traps to<br>disrupt AI<br>attackers|framework<br>against<br>LLM<br>attackers|controlled<br>settings; no<br>live<br>honeypot|engagement<br>and adaptive<br>responses|
|Beekeeper:|Audit|Simulates|Introduces|Only pre-|Works as live|
|Honeypot|tool,|attackers|automated|deployment;|defence with|
|Analysis|LLM-as-|and tests|red-|no live|self-healing|
|with LLM-<br>Driven|attacker|honeypot<br>weaknesses|teaming<br>for|defense or<br>adaptation|and<br>deception|
|Feedback<br>[5]||automati-<br>cally|honeypots|||



7 

## **4 Objectives** 

1. **To develop a high-accuracy “Intent Sieve” classifier:** The primary goal is to design and train a specialized machine learning classifier, utilizing architectures such as **DistilBERT** or **Llama-Guard** , capable of distinguishing between benign user queries and malicious prompt injections. This objective aims to achieve a **Detection Accuracy of** _>_ **95%** on standard adversarial benchmarks (such as **JailbreakBench** ), ensuring that legitimate users are rarely rerouted and the system maintains a minimal **False Positive Rate** . 

2. **To implement a high-fidelity generative “Mirror Maze” sandbox:** This objective focuses on constructing a zero-trust environment using **Docker-based isolation** to host a secondary, fine-tuned LLM designed to maintain a “vulnerable” persona. The goal is to maximize **Attacker Dwell Time** by providing dynamically hallucinated data, including fake API keys and system logs, that are consistent and believable enough to prevent an adversary from detecting the deception for a minimum of **5–10 minutes** of interaction. 

3. **To automate “Self-Healing” security guardrails:** To engineer an autonomous “Self-Healing” security framework that functions as a digital immune system by capturing adversarial patterns in the honeypot and instantly synthesizing permanent guardrails (e.g., via **NVIDIA NeMo** or **Colang** ). This objective aims to eliminate manual intervention by reducing the “time-to-patch” from hours to seconds, ensuring the production infrastructure achieves immediate and permanent immunity to newly identified exploitation techniques. 

4. **To validate system integrity and ensure zero-leakage security:** This aims to demonstrate that even if an attacker successfully “breaks” the Honey-LLM persona within the sandbox, they remain strictly isolated from the host server and the production database. The objective is to verify **Zero-Escape Security** , ensuring that the deceptive environment acts as a total “dead end” for malicious scripts or lateral movement attempts. 

5. **To create a real-time Threat Intelligence Dashboard:** To provide value to security analysts, the project will include a visualization layer that maps attack patterns, labels common injection techniques (e.g., “DAN” style jailbreaks vs. “Payload Splitting”), and tracks the geographic/IP origin of the threats. The objective is to turn “hidden” conversational attacks into quantifiable security data. 

8 



<!-- Start of picture text -->
Automated<br>Dataset F Aversarial Pattern Adversarial Stress<br>and Pre-processingCuration Extraction Testing<br>Baseline + Iniacti i idati<br>Infrastructure ; ;Bait Inject Metric Validation \<br>Provisioning Fine-TuningBinary ClassifierEls thelUnyjexeuateta AutoGenerationGuardrail \IntcarieeAudit<br>Stage 3 Stage 6<br>Dynamic Policy Threat Intelligence<br>Saale Persona Deployment Dashboard Development<br>Inference Engineering Performance Overhead<br>Thread Caliibration Evaluation \<br>Actor Modeling and eS Forensic Logging<br> Taxonomy CoOnteinenbation Pipeline<br><!-- End of picture text -->

SLM. 

### **5.2 Phase II: Development of the Semantic Intent Sieve** 

- **Step 2.1 – Dataset Curation and Pre-processing:** Consolidation, normalization, and labeling of adversarial datasets (e.g., JailbreakBench, AdvBench). 

- **Step 2.2 – Fine-Tuning the Binary Classifier:** Use of moderation model (Llama-Guard 3), inspired by constitutional AI principles [1], to serve as the “Intent Sieve,” built using established machine learning techniques [3]. 

- **Step 2.3 – Inference Calibration:** Refinement of classification threshold to balance minimized False Positives (FP) with low latency. 

### **5.3 Phase III: Engineered Deception and High-Interaction Sandboxing** 

- **Step 3.1 – Zero-Trust Containerization:** Implementation of Docker-isolated sandbox with restricted network protocols. 

- **Step 3.2 – Persona Engineering (Honey-LLM):** Directing the decoy model with system-level instructions to confidently provide fake data in response to malicious queries (Hallucination-as-a-Service). 

- **Step 3.3 – Bait Injection (Honey-Data):** Deployment of synthetically generated non-functional API keys, dummy internal documentation, and simulated database schemas. 

### **5.4 Phase IV: Autonomous Guardrail Synthesis and Policy Hardening** 

- **Step 4.1 – Adversarial Pattern Extraction:** Development of a summarization model to identify the core logic of successful sandbox injections. 

- **Step 4.2 – Automated Guardrail Generation:** Using NVIDIA NeMo Guardrails framework to dynamically program security policies [6]. 

- **Step 4.3 – Dynamic Policy Deployment:** Implementing a “hot-patching” mechanism to inject guardrails into the production environment in near real-time. 

10 

### **5.5 Phase V: Forensic Telemetry and Intelligence Visualization** 

- **Step 5.1 – Forensic Logging Pipeline:** Creation of a secure database capturing prompt metadata, IP-origin data, and classifier confidence scores. 

- **Step 5.2 – Threat Intelligence Dashboard Development:** Visualization interface to categorize attack styles and visualize global threat origins. 

- **Step 5.3 – Metric Validation (Dwell Time Analysis):** Implementation of analytics to measure the generative deception efficacy via Adversarial Dwell Time. 

### **5.6 Phase VI: Empirical Validation and Adversarial Red-Teaming** 

- **Step 6.1 – Automated Adversarial Stress Testing:** Subjecting the Sieve to thousands of novel jailbreak attempts using automated frameworks. 

- **Step 6.2 – Sandbox Integrity Audit:** Performing break-out simulations to confirm impenetrable container isolation. 

- **Step 6.3 – Performance Overhead Evaluation:** Auditing latency to confirm unhindered user experience for legitimate production traffic. 

11 



<!-- Start of picture text -->
Honey-LLM: A Deceptive Defense Ecosystem for LLMs — Project Work Plan (Jan — Dec)<br>PT January February = March April May June July August September October November December<br>fsmienmrcnecwredeonUanuary = Februal FeLeMeehan 1 2 3 4 5 6 7 8 PITTPITT9 10 11 12 TTTT 13 14TTT TTT15 TTT16 17 18irre19 TTT 20 21 tie22 Tee23 24ye25 26 27ettt28 et29TT30 31 32 TT33ee 34 TT35 eee36 37 38 39 40PE 41eeeETE42 43 44 EEee45 46 47 48<br>a(Identity prompt injection bots, jalbreak researchers, dataee exfitrators) |<br>|(Design API gateway redtrecton architecture) ee<br>ssowipsoscmmuvecrsuo(Deploy crvenvormens | dL LI TT MM<br>[simMarchGPU—ceaterdevommenyAprilenvironments; set upproduction = LLM & decoy SLM) |FEacu | TTETT TTT TT | PTTPTT TTT TT TTT TTTTTTrT TTTye eteT eeeeeeee eeeee eeTe etee<br>Ea(Consolidate JailbreakBench, AdvBench, HackAPromet datasets)<br>Jssiseeronmeerraermencowon(DistiBERT /LlamaGuard.3; tomecwon  optimize F'1-score for intent detection) | TT TT TTT TT | MB<br>litaneemsravenemvevmamernemmery(Minimize false positives; ensure low-latency Ive inference) LL LT TTT TTT TT TT<br>ftornractnsinmonigfsesonwarreineimarnomonemecwy‘StepMay 31:— JuneZero-Tiust Docker Containenzation FETTT[sewn TTT TT TTTTT TTTTTT TT TTTttt yyy TTPrPPT TTT TTT TTTTTT TT etTrt Teeter tree yt ey ttey<br>[Meowneccvunomrremerenen(Program decoy LLM with vulnerable persona: deploy ry  hallycination-os-0-service) ravereneesens | | TT TTTTTTTTTTTT TT MTT TTT TTT TTT<br>lderatesProranmass(Deployfake API keys, dummy docs, simulatedmuescoooemeseoues | LTT TTT TT TTT TTTTTT TT TT |<br>(July ~ August) Be Eee ery PEEEEEEEE EEE<br>Peer DB schemas as lures)<br>Siwesataateeevemawmes(Post.hoc analysis script, summarize core logic of 1 TTT<br>[naiCawwrmmcrrevnaestomencesrwors(NVIDIA Nelo /Colang: synthesize new polices fromsuccessful extracted patterns)injections) | LTT TTT TT TTT TTTTTTTTTTTT<br>linstrovaswensremeasonarennownsimy(Inject new guardrails into production layer in near real-time) LL TTTTTT TT TVTTT |<br>frstpneeestenin(September— October [acu TT TTT TTT TTT TTT TTT ttt eee eee tt ey EEEEEEEEPict<br>liceweseinan(Capture prompt metadata, IP-origin cegnen.cosnerentimosoey  data, classifier confidence scores) | LL TTT TT TTT TIT TTT TTT TTT TT TTT TTT tt ty |<br>[scone(Streamiit cam/ Grafana; cesowecategorize attack screestyles, geographiccorwnemenromapping) LT TTT TTT TTT TTT TT TTT |<br>litsrseonernarinecnmccemneny(easure adversarial dwell ime; evaluate deception effcacy) Ls LT TTT TTT TTT TTTTTTTTTTTT<br>jitrnenatearernmeNovember — Decembei mTjaws TTT TTT TTTEP TT tit tttELErrr terre et ret ee eeRELYeet<br>g licmermrnamnnsneimeensoenwnonStep 61: Automated Adversarial Stress Testing LTT TT TTT TTT TT TTT TTT TTT TTT TT<br>(Venty Docker isolation remains impenetrable under exploitation)<br>litwrisercawrronmmecerseneremcenn LL LT TTT TTT TTT TTT TTT TTT TT TT TTT<br>(Ensure security layers do not degrade legitimate user experience)<br>lisiwccsawssnasarawesmoncrenres | LLL TTT TTT TT TTT TTT TTT TTT TT ETT<br>Legend: Peo actual ociayGl step active weeks<br><!-- End of picture text -->

## **7 Project Outcomes** 

1. **End-to-End Honey-LLM Security Framework** 

   - A fully integrated system combining prompt interception, intent classification, decision routing, generative deception, and feedback mechanisms. The framework supports **real-time processing (** _∼_ **150–250 ms per query)** and demonstrates a complete, deployable AI security pipeline for LLM-based applications. 

2. **Accurate Detection and Effective Containment of Attacks** The Intent Sieve model achieves _∼_ **90–95% detection accuracy** with a **false positive rate below 5%** , enabling reliable identification of prompt injection attempts. Malicious inputs are automatically redirected to a sandbox, significantly reducing the probability of system compromise. 

3. **High-Fidelity Deception and Threat Intelligence Generation** 

   - The generative honeypot produces **contextually consistent and believable responses** , maintaining attacker engagement for **5–10 minutes average dwell time** . It captures structured data on prompt patterns, attack strategies, and behavioral sequences for further analysis. 

4. **Secure Isolation and Zero-Leakage Assurance** The Docker-based sandbox ensures **complete (100%) isolation** between malicious interactions and production systems. Testing confirms **zero unauthorized access** to sensitive data, maintaining strong system integrity even under adversarial conditions. 

5. **Adaptive, Scalable, and India-Relevant Security Solution** 

   - The system continuously improves by learning from captured attacks, reducing **timeto-patch from hours to near real-time** . It provides a scalable model for enterprise deployment and is highly relevant for India, enhancing security in **fintech, e-governance, and large-scale digital platforms** handling sensitive user data. 

6. **Real-Time Monitoring and Analytical Dashboard** 

   - A dashboard that tracks **attack frequency, classification types** (e.g., jailbreak, prompt leakage, role override), and system metrics such as detection rate and response latency. It supports near real-time updates ( _<_ **1 sec refresh** ) and visualizes trends (e.g., **top 3 attack patterns, daily attack counts** ), enabling effective monitoring and data-driven security analysis. 

13 

**8 Individual Roles** 

- **Anoushka Singh – Strategy Lead & Security Architect** 

Coordinates the project and oversees system architecture and security design. 

- **Tarun Krishna Shastri – Machine Learning Engineer** 

Develops and trains the intent detection classifier and handles adversarial datasets. 

- **Devansh Wadhwani – Systems & Infrastructure Engineer** Deploys the computational infrastructure and builds the Honey-LLM deception environment. 

- **Shreya Giri – Data Analyst & Documentation Lead** 

Manages telemetry, builds the threat dashboard, and prepares all research documentation. 

14 

## **9 Course Subjects** 

The following curriculum subjects are directly applicable to this project: 

- Artificial Intelligence 

- Machine Learning 

- Database Management Systems 

- Computer Networks 

- Data Structures and Algorithms 

15 

## **References** 

- [1] Anthropic. Constitutional ai: Harmlessness from ai feedback. _arXiv preprint arXiv:2212.08073_ , 2022. 

- [2] Daniel Ayzenshteyn, Ron Weiss, and Yisroel Mirsky. Cloak, honey, trap: Proactive defenses against LLM agents. Ben-Gurion University of the Negev, 2025. 

- [3] Ian Goodfellow, Yoshua Bengio, and Aaron Courville. _Deep Learning_ . MIT Press, 2016. 

- [4] Chenglong Guan, Gang Cao, and Sencun Zhu. HoneyLLM: Enabling shell honeypots with large language models. In _2024 IEEE Conference on Communications and Network Security (CNS)_ , Taipei, Taiwan, 2024. IEEE. 

- [5] Niklas Ilg, David Germek, Paul Duplys, and Michael Menth. Beekeeper: Accelerating honeypot analysis with LLM-driven feedback. _IEEE Access_ , 13, 2025. 

- [6] NVIDIA. Nemo guardrails documentation, 2024. 

- [7] OpenAI. Gpt-4 technical report. _arXiv preprint arXiv:2303.08774_ , 2023. 

- [8] H. Tunc Otal and M. Ali Canbaz. LLM honeypot: Leveraging large language models as advanced interactive honeypot systems. In _2024 IEEE Conference on Communications and Network Security (CNS)_ , Taipei, Taiwan, 2024. IEEE. 

- [9] OWASP Foundation. Owasp top 10 for large language model applications, 2023. 

- [10] Matej Sladi´c, Veronica Valeros, Carlos Catania, and Sebastian Garcia. LLM in the shell: Generative honeypots. In _2024 IEEE European Symposium on Security and Privacy Workshops (EuroS&PW)_ , Vienna, Austria, 2024. IEEE. 

16 

