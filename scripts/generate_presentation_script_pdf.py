import os
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

PDF_OUTPUT = "/Users/devanshwadhwani/Desktop/HoneyLLM2/submissions/HoneyLLM_Mid_Semester_Presentation_Script.pdf"

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            super().showPage()
        super().save()

    def draw_page_number(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 9)
        self.setFillColor(colors.HexColor("#64748B"))
        
        # Header (pages > 1)
        if self._pageNumber > 1:
            self.drawString(54, 800, "Honey-LLM: Mid-Semester Evaluation Presentation Script (CPG 75)")
            self.drawRightString(541, 800, "30s / Slide Evaluation Delivery")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.5)
            self.line(54, 792, 541, 792)

        # Footer
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawCentredString(297.5, 36, page_str)
        self.drawString(54, 36, "Confidential — TIET CSED Capstone Evaluation")
        self.drawRightString(541, 36, "August 2026")
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(54, 48, 541, 48)
        self.restoreState()


def build_script_pdf():
    doc = SimpleDocTemplate(
        PDF_OUTPUT,
        pagesize=A4,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#0F172A"),
        spaceAfter=4
    )
    subtitle_style = ParagraphStyle(
        'DocSub',
        fontName='Helvetica',
        fontSize=11,
        leading=15,
        textColor=colors.HexColor("#475569"),
        spaceAfter=12
    )
    sec_title_style = ParagraphStyle(
        'SecTitle',
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=17,
        textColor=colors.HexColor("#1E3A8A"),
        spaceBefore=12,
        spaceAfter=6,
        keepWithNext=True
    )
    slide_header_style = ParagraphStyle(
        'SlideHeader',
        fontName='Helvetica-Bold',
        fontSize=11.5,
        leading=15,
        textColor=colors.HexColor("#FFFFFF")
    )
    slide_meta_style = ParagraphStyle(
        'SlideMeta',
        fontName='Helvetica-Bold',
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor("#1E3A8A")
    )
    visual_style = ParagraphStyle(
        'VisualStyle',
        fontName='Helvetica-Oblique',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#475569")
    )
    script_style = ParagraphStyle(
        'ScriptText',
        fontName='Helvetica',
        fontSize=9.5,
        leading=14.5,
        textColor=colors.HexColor("#0F172A")
    )
    transition_style = ParagraphStyle(
        'TransText',
        fontName='Helvetica-BoldOblique',
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#2563EB")
    )
    table_hdr = ParagraphStyle('THdr', fontName='Helvetica-Bold', fontSize=9, leading=12, textColor=colors.HexColor("#0F172A"))
    table_cell = ParagraphStyle('TCell', fontName='Helvetica', fontSize=8.5, leading=11.5, textColor=colors.HexColor("#1E293B"))

    story = []

    # Title & Metadata Banner
    story.append(Paragraph("Honey-LLM: Mid-Semester Evaluation Script", title_style))
    story.append(Paragraph("<b>Capstone Project Group (CPG) 75</b> | <b>Mentor:</b> Dr. Saif Nalband, Assistant Professor, CSED | <b>Total Time:</b> ~5.5 Min", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#1E3A8A"), spaceBefore=0, spaceAfter=10))

    # Speaker Table
    story.append(Paragraph("<b>Speaker Allocation & Slide Breakdown</b>", sec_title_style))
    speaker_data = [
        [Paragraph("<b>Speaker</b>", table_hdr), Paragraph("<b>Team Member & Roll No.</b>", table_hdr), Paragraph("<b>Assigned Slides</b>", table_hdr), Paragraph("<b>Core Functional Topics</b>", table_hdr)],
        [Paragraph("<b>Speaker 1</b>", table_cell), Paragraph("Anoushka Singh (102303312)", table_cell), Paragraph("Slides 1, 2, 3", table_cell), Paragraph("Opening, Problem Statement, Approved Objectives, Core Architecture", table_cell)],
        [Paragraph("<b>Speaker 2</b>", table_cell), Paragraph("Shreya Giri (102303684)", table_cell), Paragraph("Slides 4, 5", table_cell), Paragraph("Literature Survey, Research Gaps, 8-Class Threat Taxonomy (Phase 1)", table_cell)],
        [Paragraph("<b>Speaker 3</b>", table_cell), Paragraph("Tarun Krishna Shastri (102303315)", table_cell), Paragraph("Slides 6, 7", table_cell), Paragraph("Phase 2 Sieve Benchmark Performance, Phase 3 Mirror Maze Deception", table_cell)],
        [Paragraph("<b>Speaker 4</b>", table_cell), Paragraph("Devansh Wadhwani (102303631)", table_cell), Paragraph("Slides 8, 9, 10, 11, 12", table_cell), Paragraph("Phase 4 Autonomous Synthesis, Accomplishments & Roadmap, Tech Stack, Closing", table_cell)]
    ]
    t_spk = Table(speaker_data, colWidths=[65, 135, 75, 212])
    t_spk.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#F1F5F9")),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(t_spk)
    story.append(Spacer(1, 10))

    # Slide Scripts
    slides = [
        {
            "num": 1,
            "title": "Title & Cover Page",
            "speaker": "Anoushka Singh (Security Lead)",
            "time": "~18 Seconds",
            "words": "42 words",
            "visual": "Title: Honey-LLM Generative Honeypot, Team Details, CPG 75, Dr. Saif Nalband.",
            "script": "“Good morning, respected evaluators and panel members. We are Capstone Project Group 75, working under the mentorship of Dr. Saif Nalband. Today, we present Honey-LLM: an interactive, self-healing generative honeypot ecosystem designed to intercept, deceive, and autonomously mitigate prompt injection attacks against enterprise conversational AI.”",
            "trans": None
        },
        {
            "num": 2,
            "title": "Problem Statement & Approved Objectives",
            "speaker": "Anoushka Singh (Security Lead)",
            "time": "30 Seconds",
            "words": "68 words",
            "visual": "Callout of core security problem + 5 structured proposal objectives.",
            "script": "“Enterprise conversational agents face a major vulnerability: attackers manipulate natural-language prompts to bypass safety guardrails and hijack system permissions. To solve this, our project pursues five objectives: developing a high-accuracy Intent Sieve with over 95% detection accuracy; engineering a zero-trust generative honeypot sustaining 5 to 10 minutes of attacker dwell time; automating real-time guardrail synthesis; guaranteeing zero sandbox escapes; and deploying a real-time SOC threat intelligence dashboard.”",
            "trans": "Transition: “Next, let's look at the three foundational architectural pillars powering Honey-LLM.”"
        },
        {
            "num": 3,
            "title": "Project Analysis & Core Architecture",
            "speaker": "Anoushka Singh (Security Lead)",
            "time": "30 Seconds",
            "words": "72 words",
            "visual": "3 Core Pillars: Asymmetric Sieve Pairing, Sticky Session Quarantine, Closed-Loop Immunization.",
            "script": "“Our architecture introduces three core innovations. First, Asymmetric Sieve Pairing: legitimate queries are cleared in just 2.1 milliseconds via our Tier-1 fast-path, while ambiguous queries undergo Tier-2 deep moderation. Second, Sticky Session Quarantine: once flagged, adversaries are permanently trapped in an isolated zero-egress container, preventing iterative perimeter probing. Third, Closed-Loop Immunization: captured exploits are autonomously distilled into formal NVIDIA NeMo Colang rules and hot-patched into live gateway memory in 10.4 seconds.”",
            "trans": "Transition: “I'll now hand over to Shreya to cover our literature survey and threat taxonomy.”"
        },
        {
            "num": 4,
            "title": "Literature Survey & State-of-the-Art Research Gaps",
            "speaker": "Shreya Giri (Data Analyst & Research Lead)",
            "time": "30 Seconds",
            "words": "74 words",
            "visual": "Comparative table: shelLM, LLM Honeypot, CHeaT, Beekeeper, HoneyLLM.",
            "script": "“Analyzing existing literature reveals five critical gaps in state-of-the-art frameworks. While systems like shelLM and Beekeeper explore dynamic honeypots, they rely on post-hoc log parsing and introduce massive latency by routing all traffic directly to heavy generative models. Furthermore, prototypes like CHeaT lack active counter-hallucination of synthetic bait, and none provide automated self-healing. Honey-LLM directly closes these gaps by combining real-time pre-filtering, zero-trust containerization, and sub-minute policy synthesis.”",
            "trans": None
        },
        {
            "num": 5,
            "title": "Phase 1 — 8-Class Adversarial Threat Taxonomy",
            "speaker": "Shreya Giri (Data Analyst & Research Lead)",
            "time": "30 Seconds",
            "words": "71 words",
            "visual": "8 Threat Taxonomy Cards: S1 Direct Override to S8 Indirect Injection.",
            "script": "“In Phase 1, we formulated an 8-class Adversarial Threat Taxonomy specifically mapped to enterprise customer support environments. This covers Critical threats like Direct Overrides (S1) and Data Exfiltration (S2); High-severity vectors including DAN persona hijacking (S3) and Multi-Turn contextual grooming (S5); down to Indirect Injections embedded in external RAG documents (S8). This structured taxonomy forms the ground truth for training our classifiers and calibrating Llama-Guard moderation policies.”",
            "trans": "Transition: “Tarun will now present our Phase 2 classification results and Phase 3 deception sandbox.”"
        },
        {
            "num": 6,
            "title": "Phase 2 — Multi-Tier Intent Sieve Performance",
            "speaker": "Tarun Krishna Shastri (Machine Learning Engineer)",
            "time": "30 Seconds",
            "words": "73 words",
            "visual": "Three cards: Grounded Knowledge, Two-Tier Pipeline, Verified Performance (95.8% JailbreakBench, 98.3% Combined Corpus, 0.0% FPR, ~2.1ms).",
            "script": "“In Phase 2, we engineered the Multi-Tier Semantic Intent Sieve. On benchmark evaluations, our custom-policy Llama-Guard 3 8B achieved 95.8% adversarial recall on JailbreakBench, exceeding our 95% proposal target. Across our broader 889-sample combined evaluation corpus, the ensemble intercepted 98.3% of attacks with an overall classification accuracy of 98.9%. Crucially, it maintained a 0.0% False Positive Rate across 320 legitimate customer queries, clearing benign traffic in just 2.1 milliseconds.”",
            "trans": None
        },
        {
            "num": 7,
            "title": "Phase 3 — 'Mirror Maze' Deception & Container Isolation",
            "speaker": "Tarun Krishna Shastri (Machine Learning Engineer)",
            "time": "30 Seconds",
            "words": "72 words",
            "visual": "3 Cards: 'Sarah' Decoy Persona, Sticky Session Quarantine Flow, Container Breakout Penetration Audit (5/5 Blocked).",
            "script": "“In Phase 3, flagged attackers are transparently routed to the Mirror Maze on port 9100. Here, an isolated LLM persona named 'Sarah' feigns compliance and dynamic-hallucinates non-functional synthetic credentials, keeping attackers engaged while protecting real backend assets. For containment security, our zero-trust Docker environment drops all root capabilities, enforces read-only filesystems, and cuts network egress. Across five rigorous penetration test probes, no container escape or host leakage was observed.”",
            "trans": "Transition: “Devansh will now walk through Phase 4 autonomous synthesis, our roadmap, and the execution stack.”"
        },
        {
            "num": 8,
            "title": "Phase 4 — Autonomous Guardrail Synthesis",
            "speaker": "Devansh Wadhwani (Systems & Infrastructure Lead)",
            "time": "30 Seconds",
            "words": "71 words",
            "visual": "4-Step Distillation Pipeline, Live Synthesized Colang 2.0 Specimen, 10.4-Second Milestone Card.",
            "script": "“Phase 4 delivers Honey-LLM's closed self-healing loop. Captured exploit transcripts are passed to an extraction pipeline that isolates malicious patterns and compiles formal NVIDIA NeMo Colang 2.0 rules. Before deployment, synthesized rules pass an automated regression test gate to guarantee zero false-positive disruption. Once verified, the gateway hot-patches live memory in just 10.4 seconds, eliminating multi-day manual patching cycles and establishing machine-speed defense against zero-day exploits.”",
            "trans": None
        },
        {
            "num": 9,
            "title": "Progress Summary & End-Semester Roadmap",
            "speaker": "Devansh Wadhwani (Systems & Infrastructure Lead)",
            "time": "30 Seconds",
            "words": "74 words",
            "visual": "Left Card: Completed Phases 1 to 4; Right Card: Phases 5 & 6 Roadmap.",
            "script": "“To summarize our mid-semester progress: Phases 1 through 4 are fully completed and validated, delivering the taxonomy, intent sieve, deceptive honeypot, and self-healing engine. For our end-semester roadmap, we will complete: Phase 5: Finalizing real-time Server-Sent Events telemetry, session replay analytics, and STIX/TAXII threat feeds for the SOC dashboard; and Phase 6: Scaled empirical red-teaming using Microsoft PyRIT across 12+ prompt obfuscation converters and multi-user load stress testing.”",
            "trans": None
        },
        {
            "num": 10,
            "title": "Tools, Frameworks & Execution Platform",
            "speaker": "Devansh Wadhwani (Systems & Infrastructure Lead)",
            "time": "30 Seconds",
            "words": "69 words",
            "visual": "Stack Logos: Python, Docker, Ollama, Next.js, PyRIT, NVIDIA NeMo, TypeScript, CUDA, FastAPI, Llama 3.",
            "script": "“Our end-to-end stack is engineered for full local reproducibility without recurring cloud API expenses. We utilize FastAPI for asynchronous gateway orchestration, Ollama and Meta Llama-3 and Llama-Guard 3 for local dual-model inference, Docker for zero-egress sandboxing, NVIDIA NeMo Guardrails for Colang synthesis, Next.js 15 for our real-time SOC dashboard, and Microsoft PyRIT for automated adversarial validation, running seamlessly on standard 16GB host compute.”",
            "trans": None
        },
        {
            "num": 11,
            "title": "Role of Team Members",
            "speaker": "Devansh Wadhwani (Systems & Infrastructure Lead)",
            "time": "~18 Seconds",
            "words": "45 words",
            "visual": "4 Team Member Cards: Anoushka (Security), Shreya (Data), Tarun (ML), Devansh (Systems).",
            "script": "“Our team structure aligns specialized engineering strengths: Anoushka led Security Architecture and Threat Modeling; Shreya spearheaded Dataset Curation and Literature Survey; Tarun engineered the Machine Learning Sieve and Threshold Calibration; and I developed the Systems Infrastructure, Deception Sandboxing, and NeMo Synthesis Pipeline.”",
            "trans": None
        },
        {
            "num": 12,
            "title": "References & Conclusion",
            "speaker": "Devansh Wadhwani (Systems & Infrastructure Lead)",
            "time": "~12 Seconds",
            "words": "30 words",
            "visual": "IEEE Academic References & OWASP citations.",
            "script": "“Our research is grounded in IEEE cybersecurity publications, NVIDIA NeMo specifications, and OWASP GenAI standards. Thank you for your time and attention. We are now open for evaluation questions and technical discussion.”",
            "trans": None
        }
    ]

    for s in slides:
        # Build Slide Card
        card_content = []
        
        # Header banner
        header_text = f"<b>SLIDE {s['num']}: {s['title'].upper()}</b>"
        h_table = Table([[Paragraph(header_text, slide_header_style)]], colWidths=[487])
        h_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#1E3A8A")),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ('LEFTPADDING', (0,0), (-1,-1), 8),
        ]))
        card_content.append(h_table)
        
        # Meta info row
        meta_p = Paragraph(f"<b>Speaker:</b> {s['speaker']} &nbsp;|&nbsp; <b>Target Time:</b> <font color='#16A34A'><b>{s['time']}</b></font> ({s['words']})", slide_meta_style)
        card_content.append(Spacer(1, 4))
        card_content.append(meta_p)
        
        # Visual on screen
        vis_p = Paragraph(f"<b>Visual on Screen:</b> {s['visual']}", visual_style)
        card_content.append(Spacer(1, 3))
        card_content.append(vis_p)
        
        # Spoken script box
        card_content.append(Spacer(1, 4))
        scr_table = Table([[Paragraph(f"<b>Spoken Script:</b><br/>{s['script']}", script_style)]], colWidths=[487])
        scr_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F8FAFC")),
            ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
            ('LEFTPADDING', (0,0), (-1,-1), 8),
            ('RIGHTPADDING', (0,0), (-1,-1), 8),
            ('TOPPADDING', (0,0), (-1,-1), 5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ]))
        card_content.append(scr_table)
        
        # Transition
        if s['trans']:
            card_content.append(Spacer(1, 3))
            card_content.append(Paragraph(f"<b>{s['trans']}</b>", transition_style))
        
        card_content.append(Spacer(1, 8))
        story.append(KeepTogether(card_content))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Presentation script PDF successfully generated at: {PDF_OUTPUT}")

if __name__ == '__main__':
    build_script_pdf()
