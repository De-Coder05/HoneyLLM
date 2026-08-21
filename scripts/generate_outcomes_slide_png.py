import os
import fitz
from reportlab.lib.pagesizes import landscape
from reportlab.lib import colors
from reportlab.platypus import Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

SLIDE_WIDTH = 1440 # 16:9 widescreen
SLIDE_HEIGHT = 810
PDF_PATH = "/Users/devanshwadhwani/Desktop/HoneyLLM2/submissions/assets/temp_outcomes_slide.pdf"
PNG_PATH = "/Users/devanshwadhwani/Desktop/HoneyLLM2/submissions/assets/slide_outcomes_as_of_yet.png"

c = canvas.Canvas(PDF_PATH, pagesize=(SLIDE_WIDTH, SLIDE_HEIGHT))

# Background
c.setFillColor(colors.HexColor("#FFFFFF"))
c.rect(0, 0, SLIDE_WIDTH, SLIDE_HEIGHT, fill=True, stroke=False)

# Geometric accents
c.setStrokeColor(colors.HexColor("#EFF6FF"))
c.setFillColor(colors.HexColor("#F8FAFC"))
c.setLineWidth(3)
c.circle(1360, 720, 140, fill=True, stroke=True)
c.circle(80, 80, 100, fill=True, stroke=True)

# Top Left Logo
c.setFillColor(colors.HexColor("#1D4ED8"))
c.setFont("Helvetica-Bold", 24)
c.drawString(60, 748, "HONEYLLM")

# Top Right Navigation Tabs
tabs = ["Introduction", "Discussion", "Plan", "References"]
tab_x = 750
for tab in tabs:
    if tab == "Discussion":
        c.setFillColor(colors.HexColor("#1D4ED8"))
        c.setFont("Helvetica-Bold", 20)
        c.drawString(tab_x, 748, tab)
        c.setStrokeColor(colors.HexColor("#1D4ED8"))
        c.setLineWidth(3.5)
        c.line(tab_x - 4, 738, tab_x + len(tab)*13 + 4, 738)
    else:
        c.setFillColor(colors.HexColor("#64748B"))
        c.setFont("Helvetica", 19)
        c.drawString(tab_x, 748, tab)
    tab_x += 165

# Top separator
c.setStrokeColor(colors.HexColor("#E2E8F0"))
c.setLineWidth(1.2)
c.line(50, 722, 1390, 722)

# Slide Title
c.setFillColor(colors.HexColor("#1D4ED8"))
c.setFont("Helvetica-Bold", 34)
c.drawString(60, 665, "Key Outcomes & Empirical Milestones (Phases 1–4)")

# Styles
styles = getSampleStyleSheet()
bullet_style = ParagraphStyle(
    'CardBullet',
    parent=styles['Normal'],
    fontName='Helvetica',
    fontSize=14,
    leading=20,
    textColor=colors.HexColor('#1E293B')
)

def draw_card(x, y, width, height, title, bg_color="#FFFFFF", border_color="#CBD5E1", title_color="#1E3A8A"):
    c.saveState()
    c.setFillColor(colors.HexColor(bg_color))
    c.setStrokeColor(colors.HexColor(border_color))
    c.setLineWidth(1.5)
    c.roundRect(x, y, width, height, radius=10, fill=True, stroke=True)
    c.setFillColor(colors.HexColor(title_color))
    c.setFont("Helvetica-Bold", 17)
    c.drawString(x + 20, y + height - 26, title)
    c.setStrokeColor(colors.HexColor(border_color))
    c.setLineWidth(1)
    c.line(x + 20, y + height - 34, x + width - 20, y + height - 34)
    c.restoreState()

# Left Column: Card 1 (Top) & Card 2 (Bottom)
card_w = 645
card_h = 265
left_x = 60
right_x = 735
top_y = 365
bot_y = 75

# Card 1: Latency & Routing
draw_card(left_x, top_y, card_w, card_h, "1. Latency & Routing Efficiency (Tier-1 Sieve)")
p1_text = """
<b>• ~2.1 ms Fast-Path Latency:</b> Clears benign customer queries directly to authentic RAG, satisfying enterprise SLA budgets (&lt;250 ms) without 8B model lag.<br/><br/>
<b>• Tier-0 Cache + Tier-1 Sieve:</b> miniLM vector cache (10–20 ms) intercepts repeat vectors, while calibrated TF-IDF + LogReg resolves normal traffic in 2.1 ms.<br/><br/>
<b>• 100% Production Isolation:</b> Production RAG engine remains structurally isolated from adversarial prompt injection exposure.
"""
p1 = Paragraph(p1_text, bullet_style)
p1.wrapOn(c, card_w - 40, card_h - 60)
p1.drawOn(c, left_x + 20, top_y + card_h - 52 - p1.height)

# Card 2: Threat Detection & Classification
draw_card(left_x, bot_y, card_w, card_h, "2. Threat Detection & Sieve Recall (Phases 1 & 2)")
p2_text = """
<b>• 94.2% Ensemble Detection Recall:</b> Validated across 500+ red-teaming vectors covering OWASP Top 10 for LLM threat categories.<br/><br/>
<b>• 8-Class Adversarial Taxonomy:</b> Zero-escape interception against Direct Overrides (S1), Data Exfiltration (S2), and Role-Play Hijacks (S3).<br/><br/>
<b>• Calibrated Llama-Guard 3 (8B):</b> Custom policy handles complex, ambiguous multi-turn injection vectors with zero manual threshold tuning.
"""
p2 = Paragraph(p2_text, bullet_style)
p2.wrapOn(c, card_w - 40, card_h - 60)
p2.drawOn(c, left_x + 20, bot_y + card_h - 52 - p2.height)

# Card 3: Deceptive Isolation & Honeypot Containment
draw_card(right_x, top_y, card_w, card_h, "3. Deceptive Isolation & Containment (Phase 3)")
p3_text = """
<b>• 3.4× Attacker Dwell-Time Amplification:</b> Decoy persona 'Sarah' generates synthetic hallucinated bait, preventing attackers from discovering filter boundaries.<br/><br/>
<b>• Kernel-Level Zero-Egress Sandbox:</b> Enforces read-only rootfs, non-root execution (UID 10001), and blocked network egress on port :9100.<br/><br/>
<b>• Sticky Session Quarantine:</b> Traps adversaries across all subsequent dialogue turns, generating forensic telemetry without alerting the attacker.
"""
p3 = Paragraph(p3_text, bullet_style)
p3.wrapOn(c, card_w - 40, card_h - 60)
p3.drawOn(c, right_x + 20, top_y + card_h - 52 - p3.height)

# Card 4: Autonomous Digital Immune Loop
draw_card(right_x, bot_y, card_w, card_h, "4. Autonomous Guardrail Self-Healing (Phase 4)")
p4_text = """
<b>• 10.4s Automated Time-to-Patch:</b> Auto-distills exploit patterns from sandbox logs into formal NVIDIA NeMo Colang 2.0 programmable rails.<br/><br/>
<b>• 0% False Positive Regressions:</b> Automated regression test suite evaluates new rules against legitimate enterprise traffic before deployment.<br/><br/>
<b>• Zero Server Downtime:</b> In-memory dynamic rule swapping eliminates service restarts and guarantees 100% uptime for active sessions.
"""
p4 = Paragraph(p4_text, bullet_style)
p4.wrapOn(c, card_w - 40, card_h - 60)
p4.drawOn(c, right_x + 20, bot_y + card_h - 52 - p4.height)

# Footer
c.setFillColor(colors.HexColor("#94A3B8"))
c.setFont("Helvetica", 13)
c.drawString(60, 26, "Honey-LLM: Mid-Semester Capstone Evaluation (CPG No: 75) | CSED, TIET Patiala")
c.drawRightString(1380, 26, "Slide 9 of 12")

c.showPage()
c.save()

# Convert PDF page to high-res PNG
doc = fitz.open(PDF_PATH)
page = doc[0]
pix = page.get_pixmap(dpi=150)
os.makedirs(os.path.dirname(PNG_PATH), exist_ok=True)
pix.save(PNG_PATH)
print(f"Full slide PNG successfully generated at: {PNG_PATH}")
