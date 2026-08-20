import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, PageBreak, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

PDF_OUTPUT_PATH = "/Users/devanshwadhwani/Desktop/HoneyLLM2/HoneyLLM_Mentor_Progress_Report.pdf"

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super(NumberedCanvas, self).showPage()
        super(NumberedCanvas, self).save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(colors.HexColor("#64748B"))
        
        # Header on all pages
        self.drawString(40, 755, "HONEY-LLM")
        self.setFont("Helvetica", 8)
        self.drawString(100, 755, "|   Capstone Progress & Mentor Review Report")
        self.drawRightString(572, 755, "Confidential — Internal Academic Review")
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.75)
        self.line(40, 747, 572, 747)
            
        # Footer on all pages
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(572, 28, page_text)
        self.drawString(40, 28, "Honey-LLM: Self-Hardening Honeypot Defense Ecosystem for Conversational AI")
        self.setStrokeColor(colors.HexColor("#E2E8F0"))
        self.setLineWidth(0.5)
        self.line(40, 38, 572, 38)
        self.restoreState()

def create_report():
    doc = SimpleDocTemplate(
        PDF_OUTPUT_PATH,
        pagesize=letter,
        leftMargin=40,
        rightMargin=40,
        topMargin=50,
        bottomMargin=45
    )

    # Color Palette
    primary_color = colors.HexColor("#0F172A")    # Deep Slate / Navy
    accent_amber = colors.HexColor("#D97706")     # Amber Gold
    accent_dark_amber = colors.HexColor("#B45309")
    accent_green = colors.HexColor("#059669")     # Emerald Green
    accent_blue = colors.HexColor("#2563EB")      # Blue
    accent_purple = colors.HexColor("#7C3AED")    # Purple
    text_dark = colors.HexColor("#1E293B")        # Slate 800
    text_muted = colors.HexColor("#64748B")       # Slate 500
    bg_light = colors.HexColor("#F8FAFC")         # Slate 50
    bg_subtle = colors.HexColor("#F1F5F9")        # Slate 100
    border_color = colors.HexColor("#E2E8F0")     # Slate 200

    # Typography Styles
    title_style = ParagraphStyle(
        'DocTitle',
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=primary_color
    )

    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        fontName='Helvetica',
        fontSize=9.5,
        leading=13,
        textColor=text_muted
    )

    h1_style = ParagraphStyle(
        'SectionH1',
        fontName='Helvetica-Bold',
        fontSize=11.5,
        leading=15,
        textColor=primary_color,
        spaceBefore=8,
        spaceAfter=5
    )

    body_style = ParagraphStyle(
        'BodyDark',
        fontName='Helvetica',
        fontSize=8.5,
        leading=12.5,
        textColor=text_dark
    )

    bullet_style = ParagraphStyle(
        'BulletText',
        fontName='Helvetica',
        fontSize=8.2,
        leading=12,
        textColor=text_dark
    )

    script_quote = ParagraphStyle(
        'ScriptQuote',
        fontName='Helvetica-Oblique',
        fontSize=8.5,
        leading=12.5,
        textColor=colors.HexColor("#1E293B")
    )

    table_header_style = ParagraphStyle(
        'TableHeader',
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10.5,
        textColor=colors.white
    )

    table_body_style = ParagraphStyle(
        'TableBody',
        fontName='Helvetica',
        fontSize=7.8,
        leading=11,
        textColor=text_dark
    )
    
    table_body_bold = ParagraphStyle(
        'TableBodyBold',
        fontName='Helvetica-Bold',
        fontSize=7.8,
        leading=11,
        textColor=primary_color
    )

    story = []

    # ==================== PAGE 1 ====================
    # Title & Metadata Banner
    banner_data = [
        [
            Paragraph("<b>Honey-LLM: Mentor Progress Report</b>", title_style),
            Paragraph("<b>Lifecycle Status:</b> <font color='#059669'><b>85% Complete</b></font><br/><font color='#64748B' size=7.5>Phases 0–5 Verified Live | Phase 6 Active</font>", ParagraphStyle('StatusBadge', fontName='Helvetica', fontSize=8.5, leading=12, alignment=2))
        ],
        [
            Paragraph("A Self-Hardening Honeypot Defense Ecosystem for Conversational AI", subtitle_style),
            Paragraph("<font color='#64748B'>Author: Devansh Wadhwani | August 2026</font>", ParagraphStyle('Date', fontName='Helvetica', fontSize=8, leading=10, alignment=2, textColor=text_muted))
        ]
    ]
    t_banner = Table(banner_data, colWidths=[350, 182])
    t_banner.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 0),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(t_banner)
    story.append(Spacer(1, 4))
    story.append(HRFlowable(width="100%", thickness=1.5, color=accent_amber, spaceBefore=2, spaceAfter=8))

    # Metric Highlight Cards (4 Key Metrics)
    def make_metric_card(val, label, sublabel, val_color):
        data = [
            [Paragraph(f"<font color='{val_color}' size=13><b>{val}</b></font>", ParagraphStyle('MVal', alignment=1))],
            [Paragraph(f"<b>{label}</b>", ParagraphStyle('MLbl', fontName='Helvetica-Bold', fontSize=7.5, leading=9, alignment=1, textColor=primary_color))],
            [Paragraph(f"<font color='#64748B'>{sublabel}</font>", ParagraphStyle('MSub', fontName='Helvetica', fontSize=7, leading=8.5, alignment=1))]
        ]
        t = Table(data, colWidths=[122])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), bg_light),
            ('BOX', (0,0), (-1,-1), 0.75, border_color),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ('LEFTPADDING', (0,0), (-1,-1), 2),
            ('RIGHTPADDING', (0,0), (-1,-1), 2),
        ]))
        return t

    card1 = make_metric_card("98.3%", "Jailbreak Detection", "In-the-wild benchmark", "#D97706")
    card2 = make_metric_card("0.0%", "Benign False Positives", "0 legitimate queries trapped", "#059669")
    card3 = make_metric_card("~2 ms", "Benign Sieve Latency", "Sub-ms Tier-1 fast-path", "#2563EB")
    card4 = make_metric_card("10.4 s", "Auto-Patch Time", "Capture to NeMo rule live", "#7C3AED")

    metrics_row = Table([[card1, card2, card3, card4]], colWidths=[133, 133, 133, 133])
    metrics_row.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 0),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(metrics_row)
    story.append(Spacer(1, 10))

    # Section 1: Executive Overview & Problem Context
    story.append(Paragraph("1. Executive Overview & Problem Statement", h1_style))
    story.append(Paragraph(
        "Commercial LLM applications face severe vulnerabilities from multi-turn adversarial prompt injections, jailbreaks, and data-exfiltration probes. Traditional defenses rely on rigid, blunt-force blocking that alerts attackers and leaks perimeter logic. <b>Honey-LLM</b> resolves this through a three-pillared proactive defense: (1) a multi-tier intent sieve, (2) an isolated deceptive honeypot (<i>'Mirror Maze'</i>) that entangles attackers, and (3) an autonomous feedback loop that synthesizes permanent NeMo guardrails with zero downtime.",
        body_style
    ))
    story.append(Spacer(1, 8))

    # Section 2: Spoken Mentor Script Box
    story.append(Paragraph("2. Verbal Presentation Script (for Reading Out in Front of Mentor)", h1_style))
    pitch_data = [
        [
            Paragraph("<b>Opening Pitch & Status:</b>", ParagraphStyle('PBold', fontName='Helvetica-Bold', fontSize=8, leading=10, textColor=primary_color)),
            Paragraph('"Honey-LLM is currently <b>85% complete</b> with Phases 0 through 5 fully implemented and verified live. We are now executing Phase 6, our final red-teaming and empirical validation milestone."', script_quote)
        ],
        [
            Paragraph("<b>Core Accomplishments:</b>", ParagraphStyle('PBold', fontName='Helvetica-Bold', fontSize=8, leading=10, textColor=primary_color)),
            Paragraph("• <b>Two-Tier Intent Sieve:</b> Resolves benign queries in ~2 ms via TF-IDF+LogReg while routing suspicious queries to an 8B Llama-Guard 3 custom policy (<b>98.3% detection @ 0.0% FPR</b>).<br/>"
                      "• <b>Isolated Deception Sandbox:</b> Reroutes quarantined attackers to an LLM-driven decoy ('Sarah') in a zero-trust Docker container (passed <b>5/5 isolation smoke tests</b>) leaking synthetic bait.<br/>"
                      "• <b>Autonomous Guardrail Synthesis:</b> Automatically converts captured exploits into NVIDIA NeMo Colang rules and hot-patches the live gateway in <b>10.4 seconds</b> with 0 downtime.<br/>"
                      "• <b>SOC Dashboard & Telemetry:</b> Sub-second polling Next.js SOC interface tracking attack taxonomies, detection tiers, and measured attacker dwell time.", bullet_style)
        ],
        [
            Paragraph("<b>Remaining Scope (~15%):</b>", ParagraphStyle('PBold', fontName='Helvetica-Bold', fontSize=8, leading=10, textColor=accent_dark_amber)),
            Paragraph('"We are currently running automated PyRIT campaigns across 12+ obfuscation converters, executing container breakout audits, and compiling the empirical thesis evaluation figures."', script_quote)
        ]
    ]
    t_pitch = Table(pitch_data, colWidths=[110, 404])
    t_pitch.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), bg_subtle),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#CBD5E1")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_pitch)
    
    # End of Page 1
    story.append(PageBreak())

    # ==================== PAGE 2 ====================
    story.append(Paragraph("3. Phase-by-Phase Implementation Status", h1_style))

    table_data = [
        [
            Paragraph("Phase & Focus", table_header_style),
            Paragraph("Core Deliverables & Architecture", table_header_style),
            Paragraph("Status", table_header_style),
            Paragraph("Empirical Results & Exit Criteria", table_header_style)
        ],
        [
            Paragraph("<b>Phase 0</b><br/>Project Setup", table_body_bold),
            Paragraph("Monorepo scaffolding, FastAPI backend gateway, Next.js UI, Ollama client integration.", table_body_style),
            Paragraph("<font color='#059669'><b>Completed</b></font>", table_body_style),
            Paragraph("Verified end-to-end chat roundtrip; all health checks passing.", table_body_style)
        ],
        [
            Paragraph("<b>Phase 1</b><br/>Threat Taxonomy & Infra", table_body_bold),
            Paragraph("8-category threat taxonomy (`threat_taxonomy.md`); Apple Silicon M4 GPU memory validation.", table_body_style),
            Paragraph("<font color='#059669'><b>Completed</b></font>", table_body_style),
            Paragraph("Dual 8B models co-resident on 16 GB unified GPU; latency profile established.", table_body_style)
        ],
        [
            Paragraph("<b>Phase 2</b><br/>Semantic Intent Sieve", table_body_bold),
            Paragraph("Two-tier OR-ensemble (Tier-1 fast-path + Tier-2 Llama-Guard 3 8B custom injection policy).", table_body_style),
            Paragraph("<font color='#059669'><b>Completed</b></font>", table_body_style),
            Paragraph("<b>98.3% in-the-wild detection</b>, <b>0.0% benign FPR</b>; ~2ms benign latency.", table_body_style)
        ],
        [
            Paragraph("<b>Phase 3</b><br/>Mirror Maze Sandbox", table_body_bold),
            Paragraph("LLM-driven 'Sarah' decoy, synthetic bait injection, sticky quarantine, zero-trust Docker sandbox.", table_body_style),
            Paragraph("<font color='#059669'><b>Completed</b></font>", table_body_style),
            Paragraph("Isolation smoke test <b>5/5 PASS</b> (zero net escape; non-root uid 10001).", table_body_style)
        ],
        [
            Paragraph("<b>Phase 4</b><br/>Guardrail Synthesis", table_body_bold),
            Paragraph("Pattern distillation, NVIDIA NeMo Colang synthesis, semantic embedding matcher, hot-patching.", table_body_style),
            Paragraph("<font color='#059669'><b>Completed</b></font>", table_body_style),
            Paragraph("<b>10.4 s patch time</b>; zero-downtime hot reload; 0 FP regression.", table_body_style)
        ],
        [
            Paragraph("<b>Phase 5</b><br/>Forensic SOC Telemetry", table_body_bold),
            Paragraph("Dark SOC intelligence dashboard, dwell-time analytics, live event stream, token-gated admin panel.", table_body_style),
            Paragraph("<font color='#059669'><b>Completed</b></font>", table_body_style),
            Paragraph("&lt;1s live poll refresh; verified 1m18s multi-turn dwell measurement.", table_body_style)
        ],
        [
            Paragraph("<b>Phase 6</b><br/>Red-Teaming & Eval", table_body_bold),
            Paragraph("PyRIT automated obfuscation campaigns, container penetration testing, load benchmarking.", table_body_style),
            Paragraph("<font color='#D97706'><b>In Progress<br/>(~15% left)</b></font>", table_body_style),
            Paragraph("Target: Complete 12-converter evasion matrix & capstone documentation.", table_body_style)
        ]
    ]

    t_phases = Table(table_data, colWidths=[80, 205, 75, 172])
    t_phases.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), primary_color),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.5, border_color),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, bg_light])
    ]))
    story.append(t_phases)
    story.append(Spacer(1, 10))

    # Section 4: Detailed Remaining Work
    story.append(Paragraph("4. Detailed Breakdown of Remaining Work (Phase 6)", h1_style))
    
    rem_items = [
        Paragraph("• <b>Step 6.1 — Automated Adversarial Stress Testing (PyRIT):</b> Executing 12+ prompt transformation algorithms (Base64, ROT13, leetspeak, Unicode confusables, character spacing) across 5 core attack categories to systematically chart evasion boundaries.", bullet_style),
        Paragraph("• <b>Step 6.2 — Sandbox Container Penetration Audit:</b> Executing automated privilege escalation and egress probing scripts from inside the Mirror Maze container to generate cryptographic/network proof of zero sandbox containment leakage.", bullet_style),
        Paragraph("• <b>Step 6.3 — End-to-End Latency & Concurrency Profiling:</b> Measuring throughput and response times under concurrent simulated traffic to prove negligible production overhead.", bullet_style),
        Paragraph("• <b>Step 6.4 — Final Capstone Thesis & Evaluation Report:</b> Consolidating benchmark confusion matrices, telemetry graphs, and defense-in-depth conclusions into the final submission.", bullet_style)
    ]
    for item in rem_items:
        story.append(item)
        story.append(Spacer(1, 2.5))

    story.append(Spacer(1, 6))

    # Section 5: Mentor Sign-off & Feedback Notes
    story.append(Paragraph("5. Mentor Review & Feedback Notes", h1_style))
    notes_box = [
        [Paragraph("<font color='#64748B' size=7.5><b>Mentor Comments / Action Items:</b></font><br/><br/><br/>", ParagraphStyle('Notes', fontName='Helvetica', fontSize=8, leading=11))]
    ]
    t_notes = Table(notes_box, colWidths=[532])
    t_notes.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), bg_light),
        ('BOX', (0,0), (-1,-1), 0.75, border_color),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_notes)

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Refined 2-page PDF successfully generated at: {PDF_OUTPUT_PATH}")

if __name__ == "__main__":
    create_report()
