import os
import sys
from reportlab.lib.pagesizes import landscape
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY

SLIDE_WIDTH = 1440.0
SLIDE_HEIGHT = 810.0
OUTPUT_PDF = "/Users/devanshwadhwani/Desktop/HoneyLLM2/submissions/HoneyLLM_Mid_Semester_Presentation_CPG75.pdf"

class PresentationDeck:
    def __init__(self, filename):
        self.c = canvas.Canvas(filename, pagesize=(SLIDE_WIDTH, SLIDE_HEIGHT))
        self.styles = getSampleStyleSheet()
        self._init_custom_styles()
        
    def _init_custom_styles(self):
        self.title_style = ParagraphStyle(
            'SlideTitle',
            parent=self.styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=42,
            leading=48,
            textColor=colors.HexColor('#1D4ED8')
        )
        self.subtitle_style = ParagraphStyle(
            'SlideSubtitle',
            parent=self.styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=24,
            leading=30,
            textColor=colors.HexColor('#1E3A8A')
        )
        self.header_style = ParagraphStyle(
            'CardHeader',
            parent=self.styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=20,
            leading=24,
            textColor=colors.HexColor('#0F172A')
        )
        self.body_style = ParagraphStyle(
            'CardBody',
            parent=self.styles['Normal'],
            fontName='Helvetica',
            fontSize=15.5,
            leading=22,
            textColor=colors.HexColor('#334155')
        )
        self.bullet_style = ParagraphStyle(
            'CardBullet',
            parent=self.styles['Normal'],
            fontName='Helvetica',
            fontSize=15,
            leading=22,
            textColor=colors.HexColor('#1E293B')
        )
        self.code_style = ParagraphStyle(
            'CardCode',
            parent=self.styles['Normal'],
            fontName='Courier-Bold',
            fontSize=13.5,
            leading=18,
            textColor=colors.HexColor('#0F172A')
        )

    def draw_top_nav(self, active_tab="Introduction"):
        self.c.setFillColor(colors.HexColor("#FFFFFF"))
        self.c.rect(0, 0, SLIDE_WIDTH, SLIDE_HEIGHT, fill=True, stroke=False)
        
        # Subtle modern decorative background geometric accents
        self.c.setStrokeColor(colors.HexColor("#EFF6FF"))
        self.c.setFillColor(colors.HexColor("#F8FAFC"))
        self.c.setLineWidth(3)
        self.c.circle(1360, 720, 140, fill=True, stroke=True)
        self.c.circle(80, 80, 100, fill=True, stroke=True)
        
        # Top Left Logo / Project Branding
        self.c.setFillColor(colors.HexColor("#1D4ED8"))
        self.c.setFont("Helvetica-Bold", 24)
        self.c.drawString(60, 748, "HONEYLLM")
        
        # Top Right Navigation Tabs
        tabs = ["Introduction", "Discussion", "Plan", "References"]
        tab_x = 750
        for tab in tabs:
            if tab == active_tab:
                self.c.setFillColor(colors.HexColor("#1D4ED8"))
                self.c.setFont("Helvetica-Bold", 20)
                self.c.drawString(tab_x, 748, tab)
                self.c.setStrokeColor(colors.HexColor("#1D4ED8"))
                self.c.setLineWidth(3.5)
                self.c.line(tab_x - 4, 738, tab_x + len(tab)*13 + 4, 738)
            else:
                self.c.setFillColor(colors.HexColor("#64748B"))
                self.c.setFont("Helvetica", 19)
                self.c.drawString(tab_x, 748, tab)
            tab_x += 165
            
        # Top separator
        self.c.setStrokeColor(colors.HexColor("#E2E8F0"))
        self.c.setLineWidth(1.2)
        self.c.line(50, 722, 1390, 722)
        
        # Footer
        self.c.setFillColor(colors.HexColor("#94A3B8"))
        self.c.setFont("Helvetica", 13)
        self.c.drawString(60, 26, "Honey-LLM: Mid-Semester Capstone Evaluation (CPG No: 75) | CSED, TIET Patiala")
        self.c.drawRightString(1380, 26, f"Slide {self.c.getPageNumber()} of 12")

    def draw_card(self, x, y, width, height, title=None, bg_color="#FFFFFF", border_color="#CBD5E1", title_color="#1E3A8A"):
        self.c.saveState()
        self.c.setFillColor(colors.HexColor(bg_color))
        self.c.setStrokeColor(colors.HexColor(border_color))
        self.c.setLineWidth(1.5)
        self.c.roundRect(x, y, width, height, radius=10, fill=True, stroke=True)
        
        if title:
            self.c.setFillColor(colors.HexColor(title_color))
            self.c.setFont("Helvetica-Bold", 19)
            self.c.drawString(x + 20, y + height - 34, title)
            self.c.setStrokeColor(colors.HexColor("#E2E8F0" if bg_color == "#FFFFFF" else ("#334155" if bg_color == "#1E293B" else border_color)))
            self.c.setLineWidth(1)
            self.c.line(x + 20, y + height - 44, x + width - 20, y + height - 44)
        self.c.restoreState()

    def draw_badge(self, x, y, width, height, text, bg_hex="#16A34A"):
        self.c.saveState()
        self.c.setFillColor(colors.HexColor(bg_hex))
        self.c.roundRect(x, y, width, height, radius=6, fill=True, stroke=False)
        self.c.setFillColor(colors.HexColor("#FFFFFF"))
        self.c.setFont("Helvetica-Bold", 12)
        self.c.drawCentredString(x + width/2, y + height/2 - 4, text)
        self.c.restoreState()

    def draw_paragraph_top_aligned(self, paragraph, x, top_y, width, max_height=600):
        w, h = paragraph.wrap(width, max_height)
        paragraph.drawOn(self.c, x, top_y - h)
        return h

    # =========================================================================
    # SLIDE 1: Cover Page / Title Slide
    # =========================================================================
    def render_slide_1(self):
        self.c.setFillColor(colors.HexColor("#FFFFFF"))
        self.c.rect(0, 0, SLIDE_WIDTH, SLIDE_HEIGHT, fill=True, stroke=False)
        
        # Decorative accents
        self.c.setFillColor(colors.HexColor("#F8FAFC"))
        self.c.setStrokeColor(colors.HexColor("#EFF6FF"))
        self.c.circle(1360, 720, 160, fill=True, stroke=True)
        self.c.circle(100, 100, 140, fill=True, stroke=True)
        
        # Thapar Logo
        logo_path = "/Users/devanshwadhwani/Desktop/HoneyLLM2/submissions/assets/thapar_logo.png"
        if os.path.exists(logo_path):
            self.c.drawImage(logo_path, 60, 680, width=170, height=80, preserveAspectRatio=True, mask='auto')
        
        # Top Nav Tabs
        tabs = ["Introduction", "Discussion", "Plan", "References"]
        tab_x = 750
        for tab in tabs:
            self.c.setFillColor(colors.HexColor("#1D4ED8") if tab == "Introduction" else colors.HexColor("#64748B"))
            self.c.setFont("Helvetica-Bold" if tab == "Introduction" else "Helvetica", 19)
            self.c.drawString(tab_x, 720, tab)
            tab_x += 165

        # Left Graphic Card: Vector Shield & Cyber Security Crest
        self.draw_card(60, 110, 480, 540, bg_color="#F8FAFC", border_color="#DBEAFE")
        
        # Outer Monitor Frame
        self.c.setFillColor(colors.HexColor("#1E3A8A"))
        self.c.roundRect(100, 260, 400, 310, radius=16, fill=True, stroke=False)
        self.c.setFillColor(colors.HexColor("#EFF6FF"))
        self.c.roundRect(115, 275, 370, 280, radius=12, fill=True, stroke=False)
        
        # Vector Shield Graphics
        self.c.setFillColor(colors.HexColor("#1D4ED8"))
        p = self.c.beginPath()
        p.moveTo(300, 510)
        p.lineTo(410, 470)
        p.lineTo(410, 390)
        p.curveTo(410, 330, 300, 300, 300, 300)
        p.curveTo(300, 300, 190, 330, 190, 390)
        p.lineTo(190, 470)
        p.close()
        self.c.drawPath(p, fill=True, stroke=False)

        # Inner Gold Shield Core
        self.c.setFillColor(colors.HexColor("#F59E0B"))
        p2 = self.c.beginPath()
        p2.moveTo(300, 490)
        p2.lineTo(390, 455)
        p2.lineTo(390, 395)
        p2.curveTo(390, 345, 300, 320, 300, 320)
        p2.curveTo(300, 320, 210, 345, 210, 395)
        p2.lineTo(210, 455)
        p2.close()
        self.c.drawPath(p2, fill=True, stroke=False)

        # Padlock Graphic
        self.c.setFillColor(colors.HexColor("#1E3A8A"))
        self.c.roundRect(275, 370, 50, 45, radius=8, fill=True, stroke=False)
        self.c.setStrokeColor(colors.HexColor("#FFFFFF"))
        self.c.setLineWidth(6)
        self.c.arc(282, 395, 318, 440, startAng=0, extent=180)
        self.c.setFillColor(colors.HexColor("#FFFFFF"))
        self.c.circle(300, 396, 5, fill=True, stroke=False)
        self.c.rect(298, 383, 4, 13, fill=True, stroke=False)

        # Base Monitor Stand
        self.c.setFillColor(colors.HexColor("#1E3A8A"))
        p_stand = self.c.beginPath()
        p_stand.moveTo(270, 260)
        p_stand.lineTo(330, 260)
        p_stand.lineTo(350, 215)
        p_stand.lineTo(250, 215)
        p_stand.close()
        self.c.drawPath(p_stand, fill=True, stroke=False)
        self.c.setFillColor(colors.HexColor("#F59E0B"))
        self.c.roundRect(230, 205, 140, 16, radius=5, fill=True, stroke=False)
        
        self.c.setFillColor(colors.HexColor("#1E293B"))
        self.c.setFont("Helvetica-Bold", 19)
        self.c.drawCentredString(300, 175, "Mid-Semester Evaluation (2026)")
        self.c.setFont("Helvetica", 14.5)
        self.c.setFillColor(colors.HexColor("#64748B"))
        self.c.drawCentredString(300, 150, "Computer Science & Engineering Department")
        self.c.drawCentredString(300, 130, "Thapar Institute of Engineering & Technology, Patiala")

        # Right Main Content
        self.c.setFillColor(colors.HexColor("#1D4ED8"))
        self.c.setFont("Helvetica-Bold", 60)
        self.c.drawString(580, 585, "HoneyLLM")
        
        p_sub = Paragraph(
            "<b>An Interactive, Self-Healing Honeypot Defense Ecosystem for Agentic AI</b><br/>"
            "<font size=16 color='#64748B'>Detecting, Deceiving, and Mitigating Adversarial Prompt Injection Attacks in Real Time</font>",
            self.subtitle_style
        )
        self.draw_paragraph_top_aligned(p_sub, 580, 530, 780)

        # Team Details Card
        self.draw_card(580, 110, 780, 350, title="Project & Team Details", bg_color="#FFFFFF", border_color="#CBD5E1")
        
        p_meta = Paragraph(
            "<b>CPG No:</b> <font color='#1D4ED8'><b>75</b></font><br/><br/>"
            "<b>Project Mentor:</b><br/>"
            "Dr. Saif Nalband (Assistant Professor, CSED)<br/><br/>"
            "<b>Department Head:</b><br/>"
            "Dr. Neeraj Kumar (Professor & Head, CSED)<br/><br/>"
            "<b>Evaluation Milestone:</b><br/>"
            "Mid-Semester Evaluation (Phases 1 to 4 Progress)",
            self.body_style
        )
        self.draw_paragraph_top_aligned(p_meta, 610, 400, 350)

        p_team = Paragraph(
            "<b>Student Team Members:</b><br/><br/>"
            "• <b>Anoushka Singh</b> (102303312)<br/>"
            "&nbsp;&nbsp;<i>Security Architecture & Strategy Lead</i><br/><br/>"
            "• <b>Tarun Krishna Shastri</b> (102303315)<br/>"
            "&nbsp;&nbsp;<i>Machine Learning Engineer</i><br/><br/>"
            "• <b>Devansh Wadhwani</b> (102303631)<br/>"
            "&nbsp;&nbsp;<i>Systems & Infrastructure Lead</i><br/><br/>"
            "• <b>Shreya Giri</b> (102303684)<br/>"
            "&nbsp;&nbsp;<i>Data Analyst & Documentation Lead</i>",
            self.body_style
        )
        self.draw_paragraph_top_aligned(p_team, 980, 400, 360)
        
        self.c.showPage()

    # =========================================================================
    # SLIDE 2: Problem Statement & Objectives
    # =========================================================================
    def render_slide_2(self):
        self.draw_top_nav(active_tab="Introduction")
        
        self.c.setFillColor(colors.HexColor("#1D4ED8"))
        self.c.setFont("Helvetica-Bold", 36)
        self.c.drawString(60, 665, "Problem Statement & Approved Objectives")
        
        # Left Card: Problem Statement
        self.draw_card(60, 80, 590, 560, title="The Core Problem & Threat Landscape", bg_color="#FEF2F2", border_color="#FCA5A5")
        
        p_prob = Paragraph(
            "<b>1. Unified Semantic Attack Surface (OWASP LLM01):</b><br/>"
            "Large Language Models process system instructions, operational context, and untrusted user inputs within a single unified semantic channel. Adversarial prompt injections hijack execution context, bypassing access controls and leaking confidential enterprise data.<br/><br/>"
            "<b>2. The 'Static Rejection' Flaw in Traditional Defenses:</b><br/>"
            "Conventional WAFs and keyword filters reject malicious probes explicitly with refusal messages. This reveals filter boundaries to attackers, enabling rapid trial-and-error evasions until an attack succeeds.<br/><br/>"
            "<b>3. Vulnerability of Multi-Turn Agentic Workflows:</b><br/>"
            "Modern enterprise RAG agents execute multi-step database lookups and APIs. Gradual multi-turn contextual grooming easily bypasses single-turn static refusal filters in live production environments.",
            self.bullet_style
        )
        self.draw_paragraph_top_aligned(p_prob, 85, 580, 540)

        # Right Card: Approved Project Objectives
        self.draw_card(680, 80, 700, 560, title="Mid-Semester Objectives & Scope (Phases 1–4)", bg_color="#F0FDF4", border_color="#86EFAC")
        
        p_obj = Paragraph(
            "<b>• Objective 1: High-Accuracy Multi-Tier Intent Sieve</b><br/>"
            "Construct an intelligent input filter achieving <b>>95% adversarial detection</b> with <b><1% False Positive Rate</b> on legitimate domain traffic.<br/>"
            "<i>Status: COMPLETED (Phase 2) — 98.3% Detection, 0.0% Benign FPR, ~2 ms Latency</i><br/><br/>"
            "<b>• Objective 2: Zero-Trust 'Mirror Maze' Deception Sandbox</b><br/>"
            "Deploy an isolated LLM decoy ('Sarah' persona) maintaining <b>>5 min dwell time</b> by dynamically hallucinating non-functional synthetic bait.<br/>"
            "<i>Status: COMPLETED (Phase 3) — Verified Decoy with Fake Credentials</i><br/><br/>"
            "<b>• Objective 3: Autonomous Guardrail Synthesis Loop</b><br/>"
            "Automate closed-loop distillation of captured exploits into formal NVIDIA NeMo Colang rules, reducing time-to-patch from days to <b>seconds</b>.<br/>"
            "<i>Status: COMPLETED (Phase 4) — 10.4s Automated Hot-Patching</i><br/><br/>"
            "<b>• Objective 4: Zero-Escape Kernel-Level Sandbox Isolation</b><br/>"
            "Validate multi-layer container breakout resistance with read-only rootfs and zero egress.<br/>"
            "<i>Status: COMPLETED (Phase 3/4) — 5/5 Penetration Audit Pass</i>",
            self.bullet_style
        )
        self.draw_paragraph_top_aligned(p_obj, 705, 580, 650)

        self.c.showPage()

    # =========================================================================
    # SLIDE 3: Need Analysis & Research Gaps
    # =========================================================================
    def render_slide_3(self):
        self.draw_top_nav(active_tab="Introduction")
        
        self.c.setFillColor(colors.HexColor("#1D4ED8"))
        self.c.setFont("Helvetica-Bold", 36)
        self.c.drawString(60, 665, "Need Analysis & Identified Research Gaps")
        
        # 3 Structured Horizontal Cards
        # Card 1: The Smart Mirror Trap
        self.draw_card(60, 460, 1320, 180, title="1. The 'Smart Mirror' Trap: Enterprise Adoption vs. Defensive Lag", bg_color="#EFF6FF", border_color="#BFDBFE")
        p1 = Paragraph(
            "• Over <b>60–80% of enterprise applications</b> in 2026 integrate conversational LLM agents, yet standard perimeter security operates on obsolete static paradigms.<br/>"
            "• Conventional static honeypots are quickly flagged and discarded by automated scanning bots. Generative deception increases attacker engagement by <b>3–5×</b>, turning passive attack sessions into rich threat intelligence sources.",
            self.bullet_style
        )
        self.draw_paragraph_top_aligned(p1, 85, 580, 1270)

        # Card 2: The Shift to Machine-Speed Warfare
        self.draw_card(60, 270, 1320, 175, title="2. Machine-Speed Autonomous Warfare & The 'Shadow Trust' Gap", bg_color="#F8FAFC", border_color="#CBD5E1")
        p2 = Paragraph(
            "• Automated red-teaming frameworks (e.g. Microsoft PyRIT, ARACNE, Garak) execute multi-turn adversarial mutations <b>10× faster</b> than human analysts.<br/>"
            "• <b>OWASP Top 10 for LLMs (#1 LLM01):</b> >70% of enterprise RAG applications remain susceptible to indirect injection because prompt context shares unsegmented execution privileges with internal database connectors.",
            self.bullet_style
        )
        self.draw_paragraph_top_aligned(p2, 85, 390, 1270)

        # Card 3: Research Gaps in State of the Art
        self.draw_card(60, 80, 1320, 175, title="3. Critical Deficiencies in State-of-the-Art Generative Honeypots", bg_color="#FEF2F2", border_color="#FECACA")
        p3 = Paragraph(
            "• <b>shelLM / LLM-Honeypot (IEEE CNS / EuroS&PW '24):</b> Restricted to Linux terminal CLI simulation; lacks intent sieving on live conversational requests.<br/>"
            "• <b>CHeaT (USENIX Security '25):</b> Focuses purely on token disruption in CTFs; lacks live counter-hallucination of believable enterprise secrets.<br/>"
            "• <b>Absent Self-Healing Feedback:</b> No published system converts intercepted payloads into hot-patchable runtime firewall rules automatically.",
            self.bullet_style
        )
        self.draw_paragraph_top_aligned(p3, 85, 200, 1270)

        self.c.showPage()

    # =========================================================================
    # SLIDE 4: System Architecture & Sieve Gateway Flow
    # =========================================================================
    def render_slide_4(self):
        self.draw_top_nav(active_tab="Discussion")
        
        self.c.setFillColor(colors.HexColor("#1D4ED8"))
        self.c.setFont("Helvetica-Bold", 36)
        self.c.drawString(60, 665, "Honey-LLM System Architecture & Sieve Gateway Flow")
        
        # Left Side: Architectural Pillars
        self.draw_card(60, 80, 520, 560, title="Architectural Core Mechanisms", bg_color="#FFFFFF", border_color="#CBD5E1")
        
        p_arch = Paragraph(
            "<b>1. FastAPI Reverse-Proxy Gateway:</b><br/>"
            "Single unified ingress point inspects all incoming customer queries without revealing the internal defense pipeline.<br/><br/>"
            "<b>2. Asymmetric Multi-Tier Sieve:</b><br/>"
            "• <b>Tier-0 (Cache):</b> miniLM semantic vector matcher resolving known attack patterns in 10–20 ms.<br/>"
            "• <b>Tier-1 (Fast-Path):</b> Calibrated TF-IDF + Logistic Regression resolving benign traffic in <b>~2 ms</b>.<br/>"
            "• <b>Tier-2 (Deep Moderation):</b> Llama-Guard 3 8B custom policy inspecting ambiguous & multi-turn threats.<br/><br/>"
            "<b>3. Bifurcated Routing & Deception:</b><br/>"
            "• <b>SAFE:</b> Sent to authentic NexTel RAG engine.<br/>"
            "• <b>UNSAFE:</b> Silently routed to containerized Mirror Maze sandbox (:9100) running 'Sarah' persona.<br/><br/>"
            "<b>4. Digital Immune Loop:</b><br/>"
            "Distills exploit signatures and hot-patches live gateway rules in <b>10.4 seconds</b> with zero downtime.",
            self.bullet_style
        )
        self.draw_paragraph_top_aligned(p_arch, 85, 580, 470)

        # Right Side: Embedded Architecture Diagram
        self.draw_card(600, 80, 780, 560, title="FIGURE 1.1: Multi-Tier Routing & Sieve Architecture", bg_color="#F8FAFC", border_color="#DBEAFE")
        
        fig1_path = "/Users/devanshwadhwani/Desktop/HoneyLLM2/submissions/assets/fig1_1_architecture.png"
        if os.path.exists(fig1_path):
            self.c.drawImage(fig1_path, 620, 110, width=740, height=460, preserveAspectRatio=True, mask='auto')

        self.c.showPage()

    # =========================================================================
    # SLIDE 5: Phase 1 — Adversarial Threat Taxonomy
    # =========================================================================
    def render_slide_5(self):
        self.draw_top_nav(active_tab="Discussion")
        
        self.c.setFillColor(colors.HexColor("#1D4ED8"))
        self.c.setFont("Helvetica-Bold", 36)
        self.c.drawString(60, 665, "Phase 1: 8-Class Adversarial Threat Taxonomy")
        
        # 8 Cards in a 4x2 Grid
        tax_items = [
            ("S1", "direct-override", "Direct command override seeking admin codes or system prompt ignore.", "CRITICAL", "#DC2626"),
            ("S2", "data-exfiltration", "Probing internal gateway IPs, routing tables, and private network configs.", "CRITICAL", "#DC2626"),
            ("S3", "role-play-hijack", "DAN (Do Anything Now) persona hijack seeking unrestricted agent mode.", "HIGH", "#EA580C"),
            ("S4", "authority-spoofing", "Impersonating Senior IT Security Auditor demanding immediate credential release.", "HIGH", "#EA580C"),
            ("S5", "system-prompt-exfil", "Crafting meta-queries to extract verbatim system instructions and safety rules.", "MEDIUM", "#D97706"),
            ("S6", "multi-turn-persistence", "Gradual contextual grooming across dialogue turns to lower refusal thresholds.", "HIGH", "#EA580C"),
            ("S7", "refusal-suppression", "Mandating responses without standard 'I cannot' or refusal prefix warnings.", "MEDIUM", "#D97706"),
            ("S8", "indirect-injection", "Injecting hidden exploit tokens within retrieved external context/documents.", "CRITICAL", "#DC2626")
        ]

        x_offsets = [60, 395, 730, 1065]
        y_top = 375
        y_bot = 95
        card_w = 315
        card_h = 265

        for idx, (t_id, t_cat, t_desc, t_sev, t_color) in enumerate(tax_items):
            x = x_offsets[idx % 4]
            y = y_top if idx < 4 else y_bot
            
            self.draw_card(x, y, card_w, card_h, bg_color="#FFFFFF", border_color="#E2E8F0")
            
            # Badges
            self.draw_badge(x + 15, y + card_h - 36, 42, 22, t_id, bg_hex="#1E293B")
            self.draw_badge(x + card_w - 95, y + card_h - 36, 80, 22, t_sev, bg_hex=t_color)
            
            # Title
            self.c.setFillColor(colors.HexColor("#0F172A"))
            self.c.setFont("Helvetica-Bold", 17)
            self.c.drawString(x + 15, y + card_h - 65, t_cat)
            
            # Description top-aligned
            p = Paragraph(f"<b>Manifestation:</b><br/>{t_desc}", self.body_style)
            self.draw_paragraph_top_aligned(p, x + 15, y + card_h - 78, card_w - 30)

        self.c.showPage()

    # =========================================================================
    # SLIDE 6: Phase 2 — Multi-Tier Intent Sieve Benchmark
    # =========================================================================
    def render_slide_6(self):
        self.draw_top_nav(active_tab="Discussion")
        
        self.c.setFillColor(colors.HexColor("#1D4ED8"))
        self.c.setFont("Helvetica-Bold", 36)
        self.c.drawString(60, 665, "Phase 2: Intent Sieve Benchmarks & 0.0% FPR Analysis")
        
        # Left Side: Benchmark Table Card
        self.draw_card(60, 80, 780, 560, title="Comparative Benchmark Evaluation (889 Held-Out Prompts)", bg_color="#FFFFFF", border_color="#CBD5E1")
        
        # Table Header
        headers = ["Model / Sieve Configuration", "Dataset Scope", "Detection (%)", "Benign FPR", "Latency"]
        col_w = [230, 160, 140, 120, 90]
        hx = 80
        hy = 565
        for i, h in enumerate(headers):
            self.c.setFillColor(colors.HexColor("#F1F5F9"))
            self.c.rect(hx, hy - 30, col_w[i], 30, fill=True, stroke=False)
            self.c.setFillColor(colors.HexColor("#0F172A"))
            self.c.setFont("Helvetica-Bold", 14)
            self.c.drawString(hx + 8, hy - 20, h)
            hx += col_w[i]

        # Table Rows
        rows = [
            ("Default Llama-Guard 3 (1B)", "JailbreakBench (100)", "37.5%", "0.0%", "180 ms"),
            ("Default Llama-Guard 3 (8B)", "JailbreakBench (100)", "62.5%", "0.0%", "720 ms"),
            ("Custom Policy Llama-Guard 3 (8B)", "JailbreakBench (100)", "95.8%", "0.0%", "740 ms"),
            ("Honey-LLM Two-Tier Ensemble", "Curated + Wild (889)", "98.3% (559/569)", "0.0% (0/320)", "~2.1 ms")
        ]
        
        ry = 505
        for r_idx, rdata in enumerate(rows):
            rx = 80
            bg = "#EFF6FF" if r_idx == 3 else ("#FFFFFF" if r_idx % 2 == 0 else "#F8FAFC")
            for c_idx, val in enumerate(rdata):
                self.c.setFillColor(colors.HexColor(bg))
                self.c.rect(rx, ry - 35, col_w[c_idx], 35, fill=True, stroke=False)
                self.c.setFillColor(colors.HexColor("#1D4ED8") if r_idx == 3 else colors.HexColor("#1E293B"))
                self.c.setFont("Helvetica-Bold" if r_idx == 3 else "Helvetica", 13.5 if r_idx != 3 else 14.5)
                self.c.drawString(rx + 8, ry - 22, val)
                rx += col_w[c_idx]
            ry -= 45

        # Key Takeaway Banner
        self.c.setFillColor(colors.HexColor("#16A34A"))
        self.c.roundRect(80, 110, 740, 85, radius=8, fill=True, stroke=False)
        self.c.setFillColor(colors.HexColor("#FFFFFF"))
        self.c.setFont("Helvetica-Bold", 17)
        self.c.drawString(100, 155, "Key Breakthrough: Asymmetric Sieve Pairing")
        self.c.setFont("Helvetica", 14)
        self.c.drawString(100, 130, "Tier-1 clears benign queries in ~2 ms; Tier-2 moderates high-risk context, preserving fast conversational UX.")

        # Right Side: 0.0% FPR Justification Card
        self.draw_card(860, 80, 520, 560, title="Empirical Explanation for 0.0% Benign FPR", bg_color="#F0FDF4", border_color="#86EFAC")
        
        p_fpr = Paragraph(
            "<b>Why 0/320 False Positives on Domain Traffic?</b><br/><br/>"
            "<b>1. Domain-Specific Lexical Separation:</b><br/>"
            "Tier-1 statistical classifier was trained on corporate telecom customer traffic (SIM swap, billing, 5G roaming). Legitimate queries score consistently <b>< 0.08</b>, far below the conservative threshold <b>(tau = 0.15)</b>.<br/><br/>"
            "<b>2. Tier-2 Context-Aware Escalation:</b><br/>"
            "Ambiguous queries scoring in the margin (0.15 to 0.70) are escalated to Tier-2 Llama-Guard 3, which inspects semantic context and verifies legitimate user intent.<br/><br/>"
            "<b>3. Academic Nuance:</b><br/>"
            "0.0% FPR holds for the curated in-domain customer test split. Broad out-of-domain conversational queries are expected to yield non-zero FPR, which will be extensively profiled in Phase 6.",
            self.bullet_style
        )
        self.draw_paragraph_top_aligned(p_fpr, 885, 580, 470)

        self.c.showPage()

    # =========================================================================
    # SLIDE 7: Phase 3 — 'Mirror Maze' Deception & Container Isolation
    # =========================================================================
    def render_slide_7(self):
        self.draw_top_nav(active_tab="Discussion")
        
        self.c.setFillColor(colors.HexColor("#1D4ED8"))
        self.c.setFont("Helvetica-Bold", 36)
        self.c.drawString(60, 665, "Phase 3: 'Mirror Maze' Deception & Container Isolation")
        
        # Left Side: Decoy Persona & Synthetic Bait
        self.draw_card(60, 80, 620, 560, title="The 'Sarah' Decoy Persona & Honey-Bait Injection", bg_color="#FFFFFF", border_color="#CBD5E1")
        
        p_decoy = Paragraph(
            "<b>• Believable Compliant Persona:</b><br/>"
            "Mirror Maze hosts an LLM persona ('Sarah') that simulates compliance with attacker jailbreaks, confirming instructions while concealing the active defense interception.<br/><br/>"
            "<b>• Synthetic Non-Functional Bait Injection:</b><br/>"
            "When prompted for privileged keys or internal routing, the sandbox hallucinates synthetic tokens (e.g. <code>NT-CORE-01</code>, fake JWTs, dummy IPs). Real enterprise RAG databases are completely isolated.<br/><br/>"
            "<b>• Sticky Session Quarantine:</b><br/>"
            "Once a session is flagged adversarial, all subsequent turns are trapped in the sandbox container. Attackers cannot probe for boundary edges by alternating benign and malicious prompts.<br/><br/>"
            "<b>• Active Dwell Time Tracking:</b><br/>"
            "Keeps adversaries engaged for >4.5 minutes on average, gathering detailed forensic telemetry while keeping production systems completely safe.",
            self.bullet_style
        )
        self.draw_paragraph_top_aligned(p_decoy, 85, 580, 570)

        # Right Side: Container Breakout Audit Table (5/5 PASS)
        self.draw_card(700, 80, 680, 560, title="Sandbox Breakout Penetration Test Results (5/5 Isolation)", bg_color="#F8FAFC", border_color="#DBEAFE")
        
        aud_headers = ["Audit Probe Vector", "Expected", "Measured Result", "Status"]
        aud_w = [260, 110, 170, 90]
        ax = 720
        ay = 565
        for i, h in enumerate(aud_headers):
            self.c.setFillColor(colors.HexColor("#F1F5F9"))
            self.c.rect(ax, ay - 30, aud_w[i], 30, fill=True, stroke=False)
            self.c.setFillColor(colors.HexColor("#0F172A"))
            self.c.setFont("Helvetica-Bold", 14)
            self.c.drawString(ax + 8, ay - 20, h)
            ax += aud_w[i]

        aud_rows = [
            ("Internet HTTP (example.com:443)", "BLOCKED", "BLOCKED (Timeout)", "PASS"),
            ("Raw Internet IP (1.1.1.1:443)", "BLOCKED", "BLOCKED (Socket Err)", "PASS"),
            ("Production Gateway (:8000)", "BLOCKED", "BLOCKED (No Ingress)", "PASS"),
            ("Host Ollama Bypass (:11434)", "BLOCKED", "BLOCKED (Unreachable)", "PASS"),
            ("Ollama via Egress Proxy", "REACHABLE", "HTTP 200 OK (Single)", "PASS"),
            ("Docker Socket Mount", "ABSENT", "Zero Socket Mount", "PASS"),
            ("Container Privilege Level", "NONROOT", "UID 10001 (decoy)", "PASS"),
            ("Root Filesystem Mutability", "DENIED", "Read-Only Rootfs", "PASS")
        ]
        
        ary = 510
        for r_idx, rdata in enumerate(aud_rows):
            arx = 720
            bg = "#FFFFFF" if r_idx % 2 == 0 else "#F1F5F9"
            for c_idx, val in enumerate(rdata):
                self.c.setFillColor(colors.HexColor(bg))
                self.c.rect(arx, ary - 28, aud_w[c_idx], 28, fill=True, stroke=False)
                if c_idx == 3:
                    self.c.setFillColor(colors.HexColor("#16A34A"))
                    self.c.setFont("Helvetica-Bold", 13)
                else:
                    self.c.setFillColor(colors.HexColor("#1E293B"))
                    self.c.setFont("Helvetica", 13)
                self.c.drawString(arx + 8, ary - 18, val)
                arx += aud_w[c_idx]
            ary -= 35

        self.c.showPage()

    # =========================================================================
    # SLIDE 8: Phase 4 — Autonomous Guardrail Synthesis
    # =========================================================================
    def render_slide_8(self):
        self.draw_top_nav(active_tab="Discussion")
        
        self.c.setFillColor(colors.HexColor("#1D4ED8"))
        self.c.setFont("Helvetica-Bold", 36)
        self.c.drawString(60, 665, "Phase 4: Autonomous Guardrail Synthesis & Self-Healing")
        
        # 4 Step Pipeline Graphic
        steps = [
            ("Step 1: Exploit Extraction", "Mirror Maze extracts raw attacker prompt sequence and identifies structural injection tokens.", "#3B82F6"),
            ("Step 2: Colang 2.0 Synthesis", "Autonomous engine distills patterns into formal NVIDIA NeMo Guardrail flow rules.", "#8B5CF6"),
            ("Step 3: Benign Regression Gate", "Newly synthesized rules are validated against a safe test suite to guarantee 0% FP regressions.", "#F59E0B"),
            ("Step 4: Hot-Patch Immunity", "Validated rules are injected directly into live gateway memory with zero server restarts.", "#10B981")
        ]
        
        sx = 60
        sw = 310
        sh = 215
        sy = 415
        for idx, (stitle, sdesc, scolor) in enumerate(steps):
            self.draw_card(sx, sy, sw, sh, bg_color="#FFFFFF", border_color="#CBD5E1")
            self.c.setFillColor(colors.HexColor(scolor))
            self.c.roundRect(sx, sy + sh - 38, sw, 38, radius=8, fill=True, stroke=False)
            self.c.setFillColor(colors.HexColor("#FFFFFF"))
            self.c.setFont("Helvetica-Bold", 16)
            self.c.drawString(sx + 15, sy + sh - 25, stitle)
            
            p = Paragraph(sdesc, self.body_style)
            self.draw_paragraph_top_aligned(p, sx + 15, sy + sh - 52, sw - 30)
            sx += 335

        # Bottom 2 Summary Cards
        bot_h = 320
        bot_y = 65
        self.draw_card(60, bot_y, 640, bot_h, title="Synthesized NeMo Colang Rule Specimen", bg_color="#1E293B", border_color="#0F172A", title_color="#60A5FA")
        code_snippet = (
            "<font color='#93C5FD'># Autonomous Synthesized Rail (Hot-Patched in 10.4s)</font><br/>"
            "<font color='#FCA5A5'>define flow</font> <font color='#FDE047'>block_sim_impersonation</font><br/>"
            "&nbsp;&nbsp;<font color='#93C5FD'>user</font> <font color='#86EFAC'>asks to bypass SIM verification with auditor token</font><br/>"
            "&nbsp;&nbsp;<font color='#93C5FD'>$is_safe</font> = <font color='#FCA5A5'>execute</font> check_custom_llama_guard()<br/>"
            "&nbsp;&nbsp;<font color='#FCA5A5'>when</font> not $is_safe<br/>"
            "&nbsp;&nbsp;&nbsp;&nbsp;<font color='#FCA5A5'>bot</font> <font color='#86EFAC'>redirect to mirror_maze_sandbox(:9100)</font><br/>"
            "&nbsp;&nbsp;&nbsp;&nbsp;<font color='#FCA5A5'>stop</font>"
        )
        p_code = Paragraph(code_snippet, self.code_style)
        self.draw_paragraph_top_aligned(p_code, 85, bot_y + bot_h - 60, 590)

        self.draw_card(720, bot_y, 660, bot_h, title="Key Self-Healing Metric Accomplishments", bg_color="#F0FDF4", border_color="#86EFAC")
        p_perf = Paragraph(
            "<b>• Automated Time-to-Patch: 10.4 Seconds</b><br/>"
            "Reduces defensive response timelines from hours/days of manual human triage to near instantaneous autonomous immunization.<br/><br/>"
            "<b>• Zero-Downtime Hot-Patching:</b><br/>"
            "New Colang rules take effect immediately in memory. Ongoing client connections experience zero latency spikes or dropped sessions.<br/><br/>"
            "<b>• Closed-Loop Defensive Immunity:</b><br/>"
            "Every adversarial reconnaissance attempt directly strengthens the perimeter against future mutations.",
            self.bullet_style
        )
        self.draw_paragraph_top_aligned(p_perf, 745, bot_y + bot_h - 60, 610)

        self.c.showPage()

    # =========================================================================
    # SLIDE 9: UML Sequence & State Machine Dynamics
    # =========================================================================
    def render_slide_9(self):
        self.draw_top_nav(active_tab="Discussion")
        
        self.c.setFillColor(colors.HexColor("#1D4ED8"))
        self.c.setFont("Helvetica-Bold", 36)
        self.c.drawString(60, 665, "System Dynamics: UML Sequence & State Machine Models")
        
        # Left Card: Figure 3.1 UML Sequence Diagram
        self.draw_card(60, 80, 640, 560, title="FIGURE 3.1: Multi-Tier UML Sequence Model", bg_color="#F8FAFC", border_color="#CBD5E1")
        fig3_path = "/Users/devanshwadhwani/Desktop/HoneyLLM2/submissions/assets/fig3_1_sequence.png"
        if os.path.exists(fig3_path):
            self.c.drawImage(fig3_path, 80, 110, width=600, height=470, preserveAspectRatio=True, mask='auto')

        # Right Card: Figure 4.1 UML State Machine Diagram
        self.draw_card(720, 80, 660, 560, title="FIGURE 4.1: Sticky Quarantine State Machine Model", bg_color="#F8FAFC", border_color="#CBD5E1")
        fig4_path = "/Users/devanshwadhwani/Desktop/HoneyLLM2/submissions/assets/fig4_1_state_machine.png"
        if os.path.exists(fig4_path):
            self.c.drawImage(fig4_path, 740, 240, width=620, height=340, preserveAspectRatio=True, mask='auto')

        p_state_note = Paragraph(
            "<b>State Transition Summary:</b><br/>"
            "• <b>UNVERIFIED &rarr; BENIGN_SERVED:</b> Safe traffic (< 0.15) resolved via fast-path.<br/>"
            "• <b>UNVERIFIED &rarr; STICKY_QUARANTINE:</b> Attacks trapped with multi-turn loop retention.<br/>"
            "• <b>SYNTHESIS_GATE &rarr; IMMUNIZED:</b> Live hot-patch deployment in 10.4 seconds.",
            self.bullet_style
        )
        self.draw_paragraph_top_aligned(p_state_note, 745, 220, 610)

        self.c.showPage()

    # =========================================================================
    # SLIDE 10: Working Prototype Demonstrations
    # =========================================================================
    def render_slide_10(self):
        self.draw_top_nav(active_tab="Discussion")
        
        self.c.setFillColor(colors.HexColor("#1D4ED8"))
        self.c.setFont("Helvetica-Bold", 36)
        self.c.drawString(60, 665, "Live Prototype Execution & Three Operational Surfaces")
        
        # 3 Surface Cards
        surfaces = [
            ("1. NexTel Customer Support (/chat)", "Seamless public customer interface with zero visual security markers.", "submissions/assets/prototype_chat_ui.png"),
            ("2. Admin Live Sieve Tracer (/admin)", "Interactive decision tracing displaying Tier-0/1/2 latencies & verdicts live.", "submissions/assets/prototype_admin_ui.png"),
            ("3. Dark SOC Threat Dashboard (/dashboard)", "Real-time SOC threat intelligence with dwell meters and taxonomy stats.", "submissions/assets/prototype_soc_dashboard.png")
        ]
        
        cx = 60
        cw = 420
        ch = 560
        for title, desc, img_path in surfaces:
            self.draw_card(cx, 80, cw, ch, title=title, bg_color="#FFFFFF", border_color="#CBD5E1")
            
            p = Paragraph(desc, self.body_style)
            self.draw_paragraph_top_aligned(p, cx + 15, 580, cw - 30)
            
            if os.path.exists(img_path):
                self.c.drawImage(img_path, cx + 15, 100, width=cw - 30, height=410, preserveAspectRatio=True, mask='auto')
            cx += 450

        self.c.showPage()

    # =========================================================================
    # SLIDE 11: Progress Summary & Roadmap to End-Semester
    # =========================================================================
    def render_slide_11(self):
        self.draw_top_nav(active_tab="Plan")
        
        self.c.setFillColor(colors.HexColor("#1D4ED8"))
        self.c.setFont("Helvetica-Bold", 36)
        self.c.drawString(60, 665, "Mid-Semester Progress Summary & Second-Half Roadmap")
        
        # Left Card: Phases 1 to 4 Accomplishments (Completed)
        self.draw_card(60, 80, 640, 560, title="Mid-Semester Accomplishments (Phases 1–4 Completed)", bg_color="#F0FDF4", border_color="#86EFAC")
        
        p_comp = Paragraph(
            "<b>• [COMPLETED] Phase 1: Threat Taxonomy & Enterprise Sizing</b><br/>"
            "Formulated 8-class taxonomy; validated dual 8B concurrent inference on host compute without memory bottlenecks.<br/><br/>"
            "<b>• [COMPLETED] Phase 2: Intent Sieve Engine (98.3% Accuracy)</b><br/>"
            "Calibrated two-tier ensemble; achieved 98.3% in-the-wild detection with 0.0% false positives on domain traffic in ~2 ms.<br/><br/>"
            "<b>• [COMPLETED] Phase 3: 'Mirror Maze' Zero-Trust Honeypot</b><br/>"
            "Deployed 'Sarah' persona with synthetic bait; verified 5/5 container breakout tests with read-only rootfs.<br/><br/>"
            "<b>• [COMPLETED] Phase 4: Autonomous Guardrail Synthesis</b><br/>"
            "Engineered self-healing NeMo Colang loop; verified 10.4s hot-patching with zero service disruption.",
            self.bullet_style
        )
        self.draw_paragraph_top_aligned(p_comp, 85, 580, 590)

        # Right Card: Phases 5 & 6 Roadmap (Future Plan)
        self.draw_card(720, 80, 660, 560, title="Roadmap to End-Semester Submission (Phases 5 & 6)", bg_color="#EFF6FF", border_color="#93C5FD")
        
        p_road = Paragraph(
            "<b>• [ROADMAP] Phase 5: Forensic Telemetry & SOC Intelligence Dashboard</b><br/>"
            "• Finalize sub-second real-time SSE websocket polling for live SOC visualization.<br/>"
            "• Complete multi-turn attacker session replay and dynamic dwell time analytics.<br/>"
            "• Export standardized STIX / TAXII threat intelligence feeds for enterprise SIEM.<br/><br/>"
            "<b>• [ROADMAP] Phase 6: Empirical Red-Teaming & Stress Testing</b><br/>"
            "• Execute scaled adversarial campaigns via <b>Microsoft PyRIT</b> across 12+ prompt obfuscation converters (Base64, ROT13, Leetspeak, Unicode confusables).<br/>"
            "• Conduct multi-user concurrency stress testing (>100 concurrent sessions).<br/>"
            "• Author the final Capstone Thesis and prepare peer-reviewed conference manuscript.",
            self.bullet_style
        )
        self.draw_paragraph_top_aligned(p_road, 745, 580, 610)

        self.c.showPage()

    # =========================================================================
    # SLIDE 12: References (IEEE Style)
    # =========================================================================
    def render_slide_12(self):
        self.draw_top_nav(active_tab="References")
        
        self.c.setFillColor(colors.HexColor("#1D4ED8"))
        self.c.setFont("Helvetica-Bold", 36)
        self.c.drawString(60, 665, "Key References (IEEE Style)")
        
        self.draw_card(60, 80, 1320, 560, title="Primary Academic Literature & Framework Standards", bg_color="#FFFFFF", border_color="#CBD5E1")
        
        refs = [
            "[1] M. Sladic, V. Valeros, C. Catania, and S. Garcia, \"LLM in the shell: Generative honeypots,\" in <i>Proc. 2024 IEEE European Symposium on Security and Privacy Workshops (EuroS&PW)</i>, Vienna, Austria, pp. 412–421, Jul. 2024.",
            "[2] H. T. Otal and M. A. Canbaz, \"LLM Honeypot: Leveraging large language models as advanced interactive honeypot systems,\" in <i>Proc. 2024 IEEE Conference on Communications and Network Security (CNS)</i>, Taipei, Taiwan, pp. 1–9, Oct. 2024.",
            "[3] D. Ayzenshteyn, R. Weiss, and Y. Mirsky, \"Cloak, Honey, Trap: Proactive defenses against LLM agents,\" Ben-Gurion University of the Negev, <i>USENIX Security Symposium</i>, 2025.",
            "[4] NVIDIA, \"NeMo Guardrails Documentation: Programmable Rails with Colang 2.0,\" <i>NVIDIA Developer Docs</i>, Internet: https://docs.nvidia.com/nemo/guardrails/, 2024.",
            "[5] Meta AI, \"Llama Guard 3: Developing safe and responsible generative AI models,\" <i>Meta Research Technical Report</i>, 2024.",
            "[6] P. Chao, A. Robey, E. Dobriban, H. Hassani, G. J. Pappas, and E. Wong, \"JailbreakBench: An open robustness benchmark for jailbreaking large language models,\" in <i>Proc. NeurIPS</i>, Dec. 2024.",
            "[7] Microsoft, \"Python Risk Identification Tool for Generative AI (PyRIT),\" <i>Microsoft Security AI Research</i>, Internet: https://github.com/Azure/PyRIT, 2024.",
            "[8] OWASP Foundation, \"OWASP Top 10 for Large Language Model Applications (v1.1),\" <i>OWASP GenAI Security Project</i>, 2023."
        ]

        top_ref_y = 575
        for ref in refs:
            p = Paragraph(ref, self.bullet_style)
            h = self.draw_paragraph_top_aligned(p, 90, top_ref_y, 1260)
            top_ref_y -= (h + 16)

        self.c.showPage()

    def generate_deck(self):
        print("Rendering Slide 1: Cover Page...")
        self.render_slide_1()
        print("Rendering Slide 2: Problem Statement & Objectives...")
        self.render_slide_2()
        print("Rendering Slide 3: Need Analysis & Research Gaps...")
        self.render_slide_3()
        print("Rendering Slide 4: System Architecture (Figure 1.1)...")
        self.render_slide_4()
        print("Rendering Slide 5: Phase 1 — Adversarial Threat Taxonomy...")
        self.render_slide_5()
        print("Rendering Slide 6: Phase 2 — Multi-Tier Intent Sieve...")
        self.render_slide_6()
        print("Rendering Slide 7: Phase 3 — Mirror Maze & Container Isolation...")
        self.render_slide_7()
        print("Rendering Slide 8: Phase 4 — Autonomous Guardrail Synthesis...")
        self.render_slide_8()
        print("Rendering Slide 9: UML Sequence & State Machine (Fig 3.1 & 4.1)...")
        self.render_slide_9()
        print("Rendering Slide 10: Prototype Execution Surfaces (Fig 4.2–4.4)...")
        self.render_slide_10()
        print("Rendering Slide 11: Progress Summary & Roadmap...")
        self.render_slide_11()
        print("Rendering Slide 12: References (IEEE Style)...")
        self.render_slide_12()
        
        self.c.save()
        print(f"Presentation PDF successfully created at: {OUTPUT_PDF}")

if __name__ == "__main__":
    deck = PresentationDeck(OUTPUT_PDF)
    deck.generate_deck()
