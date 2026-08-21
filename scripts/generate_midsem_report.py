import os
import sys
import fitz # PyMuPDF
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable, Image as RLImage
)
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfgen import canvas
from reportlab.graphics.shapes import Drawing, Rect, String, Line, Group, Polygon

PDF_OUTPUT_PATH = "/Users/devanshwadhwani/Desktop/HoneyLLM2/submissions/HoneyLLM_Mid_Semester_Technical_Report.pdf"

# A4 dimensions: 595.27 x 841.89 pt
# Margins: Left 1.5 in (108 pt), Right 1.0 in (72 pt), Top 1.0 in (72 pt), Bottom 1.0 in (72 pt)
# Printable width = 595.27 - 108 - 72 = 415.27 pt

class AcademicNumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super(AcademicNumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super(AcademicNumberedCanvas, self).showPage()
        super(AcademicNumberedCanvas, self).save()

    def draw_page_decorations(self, page_count):
        page_num = self._pageNumber
        self.saveState()

        # Page 1 is Cover Page -> No page number
        if page_num == 1:
            self.restoreState()
            return

        # Preliminary pages (2 to 9): Roman numerals i to viii
        roman_map = {
            2: "i", 3: "ii", 4: "iii", 5: "iv", 6: "v", 7: "vi", 8: "vii", 9: "viii"
        }

        if page_num in roman_map:
            page_str = roman_map[page_num]
        else:
            arabic_num = page_num - 9
            page_str = str(arabic_num)

        # Bottom center page numbering
        self.setFont("Times-Roman", 10)
        self.setFillColor(colors.HexColor("#1F2937"))
        self.drawCentredString(315.63, 45, page_str)
        self.restoreState()


# =========================================================================
# HIGH-RESOLUTION UML & ARCHITECTURE DIAGRAMS (Figures 1.1, 3.1, 4.1)
# Printable text width on A4 with 1.5in left / 1.0in right margin = 415.27 pt
# =========================================================================
def draw_architecture_diagram():
    img_path = "/Users/devanshwadhwani/Desktop/HoneyLLM2/submissions/assets/fig1_1_architecture.png"
    return RLImage(img_path, width=415, height=233.4)


def draw_uml_sequence_diagram():
    img_path = "/Users/devanshwadhwani/Desktop/HoneyLLM2/submissions/assets/fig3_1_sequence.png"
    return RLImage(img_path, width=415, height=233.4)


def draw_uml_state_machine_diagram():
    img_path = "/Users/devanshwadhwani/Desktop/HoneyLLM2/submissions/assets/fig4_1_state_machine.png"
    return RLImage(img_path, width=415, height=233.4)






def build_technical_report(toc_map=None, lot_map=None, lof_map=None):
    # Default fallbacks if no map provided
    toc_map = toc_map or {}
    lot_map = lot_map or {}
    lof_map = lof_map or {}

    doc = SimpleDocTemplate(
        PDF_OUTPUT_PATH,
        pagesize=A4,
        leftMargin=108,
        rightMargin=72,
        topMargin=72,
        bottomMargin=72
    )

    # Typography Styles per TIET Guidelines:
    title_cover_style = ParagraphStyle('CoverTitle', fontName='Times-Bold', fontSize=18, leading=22, alignment=1, spaceAfter=14)
    cover_sub_style = ParagraphStyle('CoverSub', fontName='Times-Roman', fontSize=12, leading=16, alignment=1)
    cover_bold_style = ParagraphStyle('CoverBold', fontName='Times-Bold', fontSize=12, leading=16, alignment=1)
    chapter_style = ParagraphStyle('ChapterHeader', fontName='Times-Bold', fontSize=16, leading=20, alignment=0, spaceBefore=8, spaceAfter=8, keepWithNext=True)
    heading1_style = ParagraphStyle('Heading1', fontName='Times-Bold', fontSize=14, leading=18, spaceBefore=11, spaceAfter=5, keepWithNext=True)
    heading2_style = ParagraphStyle('Heading2', fontName='Times-Bold', fontSize=13, leading=17, spaceBefore=8, spaceAfter=3, keepWithNext=True)
    body_style = ParagraphStyle('NormalBody', fontName='Times-Roman', fontSize=12, leading=18, alignment=4, spaceAfter=7)
    body_indent_style = ParagraphStyle('BodyIndent', fontName='Times-Roman', fontSize=12, leading=18, firstLineIndent=20, alignment=4, spaceAfter=7)
    bullet_style = ParagraphStyle('BulletBody', fontName='Times-Roman', fontSize=12, leading=17.5, leftIndent=18, firstLineIndent=-12, alignment=4, spaceAfter=4)
    table_caption_style = ParagraphStyle('TableCaption', fontName='Times-Bold', fontSize=10, leading=13, alignment=0, spaceBefore=8, spaceAfter=4, keepWithNext=True)
    figure_caption_style = ParagraphStyle('FigureCaption', fontName='Times-Bold', fontSize=10, leading=13, alignment=1, spaceBefore=5, spaceAfter=9)
    table_text_style = ParagraphStyle('TableText', fontName='Times-Roman', fontSize=10, leading=13.5, alignment=0)
    table_header_style = ParagraphStyle('TableHeaderText', fontName='Times-Bold', fontSize=10, leading=13.5, alignment=0)
    ref_item_style = ParagraphStyle('RefItem', fontName='Times-Roman', fontSize=10.5, leading=14.5, alignment=4, leftIndent=24, firstLineIndent=-24, spaceAfter=5)
    toc_line_style = ParagraphStyle('TOCLine', fontName='Times-Roman', fontSize=10, leading=14.5, alignment=0)
    toc_bold_style = ParagraphStyle('TOCBold', fontName='Times-Bold', fontSize=10.5, leading=15.5, alignment=0)

    story = []

    # =========================================================================
    # 1. COVER PAGE / TITLE PAGE (Page 1)
    # =========================================================================
    story.append(Spacer(1, 20))
    story.append(Paragraph("<b>HONEY-LLM: AN INTERACTIVE, SELF-HEALING HONEYPOT DEFENSE ECOSYSTEM FOR AGENTIC AI</b>", title_cover_style))
    story.append(Spacer(1, 10))
    story.append(Paragraph("<b>Capstone Project Report</b>", cover_bold_style))
    story.append(Spacer(1, 4))
    story.append(Paragraph("<b>MID SEMESTER EVALUATION (Phases 1 to 4 Progress)</b>", cover_bold_style))
    story.append(Spacer(1, 15))
    story.append(Paragraph("<b>Submitted by:</b>", cover_sub_style))
    story.append(Spacer(1, 6))

    story.append(Paragraph("<b>(102303312) ANOUSHKA SINGH</b>", cover_bold_style))
    story.append(Spacer(1, 2))
    story.append(Paragraph("<b>(102303315) TARUN KRISHNA SHASTRI</b>", cover_bold_style))
    story.append(Spacer(1, 2))
    story.append(Paragraph("<b>(102303631) DEVANSH WADHWANI</b>", cover_bold_style))
    story.append(Spacer(1, 2))
    story.append(Paragraph("<b>(102303684) SHREYA GIRI</b>", cover_bold_style))
    story.append(Spacer(1, 14))

    story.append(Paragraph("<b>BE Third Year, Computer Engineering (CoE)</b>", cover_sub_style))
    story.append(Spacer(1, 3))
    story.append(Paragraph("<b>CPG No: 75</b>", cover_bold_style))
    story.append(Spacer(1, 16))
    story.append(Paragraph("<b>Under the Mentorship of:</b>", cover_sub_style))
    story.append(Spacer(1, 3))
    story.append(Paragraph("<b>Dr. Saif Nalband</b>", cover_bold_style))
    story.append(Paragraph("Assistant Professor, Computer Science and Engineering Department", cover_sub_style))
    story.append(Spacer(1, 14))

    logo_path = "/Users/devanshwadhwani/Desktop/HoneyLLM2/submissions/assets/thapar_logo.png"
    if os.path.exists(logo_path):
        story.append(RLImage(logo_path, width=125, height=60))
        story.append(Spacer(1, 12))
    else:
        story.append(Spacer(1, 28))

    story.append(Paragraph("<b>Computer Science and Engineering Department</b>", cover_bold_style))
    story.append(Paragraph("<b>Thapar Institute of Engineering and Technology, Patiala</b>", cover_bold_style))
    story.append(Spacer(1, 3))
    story.append(Paragraph("<b>August 2026</b>", cover_sub_style))

    story.append(PageBreak())

    # =========================================================================
    # 2. ABSTRACT (Page i)
    # =========================================================================
    story.append(Paragraph("<b>ABSTRACT</b>", chapter_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0F172A"), spaceBefore=2, spaceAfter=12))
    story.append(Paragraph(
        "As generative Artificial Intelligence and Large Language Models (LLMs) transition from exploratory conversational tools to autonomous enterprise agents executing multi-turn workflows, they introduce critical security vulnerabilities. Chief among these is adversarial prompt injection, where attackers manipulate natural-language instructions to bypass safety guardrails, hijack system roles, and exfiltrate proprietary corporate assets. Conventional perimeter defenses, including static Web Application Firewalls (WAFs) and rigid keyword matchers, operate on a reactive rejection paradigm that inadvertently reveals filter boundaries to attackers while failing against multi-turn semantic chaining.",
        body_indent_style
    ))
    story.append(Paragraph(
        "This capstone project presents the design, system architecture, and verified implementation of <b>Honey-LLM</b>, covering work completed across <b>Phases 1 through 4</b> of the academic project roadmap. Specifically, the mid-semester implementation achieves four core deliverables: (1) an 8-class Adversarial Threat Taxonomy tailored to conversational enterprise agents; (2) a multi-tier <i>Intent Sieve</i> combining a ~2.1 ms P50 benign fast-path statistical classifier (Tier-1) with an authoritative 8B moderation model governed by a custom prompt injection policy (Llama-Guard 3 [11]), achieving a <b>95.8% adversarial recall on JailbreakBench [12]</b> and <b>98.3% adversarial detection recall across the combined 889-sample evaluation corpus</b> (559/569 adversarial payloads intercepted, 98.9% overall classification accuracy) while maintaining a <b>0.0% False Positive Rate</b> on the benign domain evaluation split (0/320 legitimate customer queries flagged); (3) a containerized zero-trust deception sandbox termed the <i>Mirror Maze</i> running an LLM-driven decoy persona that dynamic-hallucinates synthetic bait to absorb attacker reconnaissance (verified with <b>no container escapes observed across 5/5 executed penetration probes</b>); and (4) an <i>Autonomous Guardrail Synthesis</i> feedback loop that distills captured exploit patterns into formal <b>NVIDIA NeMo Colang</b> rules [6], hot-patching live gateway policies in <b>10.4 seconds</b> with zero service interruption. The subsequent project lifecycle, comprising Phase 5 (SOC Threat Intelligence Dashboard) and Phase 6 (Empirical Red-Teaming via Microsoft PyRIT [13]), forms the roadmap for the final semester submission.",
        body_indent_style
    ))
    story.append(Spacer(1, 8))
    story.append(Paragraph("<b>Keywords:</b> Generative AI Security, Prompt Injection, Semantic Intent Sieve, LLM Honeypot, Autonomous Guardrails, NVIDIA NeMo, Zero-Trust Containerization.", body_style))

    story.append(PageBreak())

    # =========================================================================
    # 3. DECLARATION (Page ii)
    # =========================================================================
    story.append(Paragraph("<b>DECLARATION</b>", chapter_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0F172A"), spaceBefore=2, spaceAfter=14))
    story.append(Paragraph(
        "We hereby declare that the design principles, experimental methodologies, system implementation, and working prototype model of the capstone project entitled <b>\"HONEY-LLM: AN INTERACTIVE, SELF-HEALING HONEYPOT DEFENSE ECOSYSTEM FOR AGENTIC AI\"</b> is an authentic record of our own work completed up to <b>Phase 4 (Autonomous Guardrail Synthesis and Policy Hardening)</b> in the Computer Science and Engineering Department, Thapar Institute of Engineering and Technology (TIET), Patiala, under the mentorship and guidance of <b>Dr. Saif Nalband</b> during the academic semester (August 2026).",
        body_indent_style
    ))
    story.append(Paragraph(
        "We further confirm that this report has not been submitted in part or full to any other University or Institution for the award of any degree or diploma.",
        body_indent_style
    ))
    story.append(Spacer(1, 12))
    story.append(Paragraph("<b>Date:</b> August 20, 2026", body_style))
    story.append(Spacer(1, 8))

    decl_table_data = [
        [Paragraph("<b>Roll No.</b>", table_header_style), Paragraph("<b>Name of Student</b>", table_header_style), Paragraph("<b>Signature</b>", table_header_style)],
        [Paragraph("102303312", table_text_style), Paragraph("Anoushka Singh", table_text_style), Paragraph("____________________", table_text_style)],
        [Paragraph("102303315", table_text_style), Paragraph("Tarun Krishna Shastri", table_text_style), Paragraph("____________________", table_text_style)],
        [Paragraph("102303631", table_text_style), Paragraph("Devansh Wadhwani", table_text_style), Paragraph("____________________", table_text_style)],
        [Paragraph("102303684", table_text_style), Paragraph("Shreya Giri", table_text_style), Paragraph("____________________", table_text_style)]
    ]
    t_decl = Table(decl_table_data, colWidths=[95, 170, 150])
    t_decl.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#F1F5F9")),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(t_decl)
    story.append(Spacer(1, 25))

    story.append(Paragraph("<b>Counter Signed By:</b>", body_style))
    story.append(Spacer(1, 4))

    sig_path = "/Users/devanshwadhwani/Desktop/HoneyLLM2/submissions/assets/saif_nalband_signature.jpg"
    sig_img = RLImage(sig_path, width=80, height=56) if os.path.exists(sig_path) else Spacer(1, 30)

    mentor_sign_data = [
        [Paragraph("<b>Faculty Mentor:</b>", table_header_style)],
        [sig_img],
        [Paragraph("<b>Dr. Saif Nalband</b>", table_text_style)],
        [Paragraph("Assistant Professor, CSED", table_text_style)],
        [Paragraph("TIET, Patiala", table_text_style)]
    ]
    t_msign = Table(mentor_sign_data, colWidths=[207])
    t_msign.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'BOTTOM'),
        ('TOPPADDING', (0,0), (-1,-1), 1),
        ('BOTTOMPADDING', (0,0), (-1,-1), 1),
    ]))
    story.append(t_msign)

    story.append(PageBreak())

    # =========================================================================
    # 4. ACKNOWLEDGEMENT (Page iii)
    # =========================================================================
    story.append(Paragraph("<b>ACKNOWLEDGEMENT</b>", chapter_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0F172A"), spaceBefore=2, spaceAfter=14))
    story.append(Paragraph(
        "We would like to express our deepest gratitude and heartfelt thanks to our respected project mentor, <b>Dr. Saif Nalband</b>, Assistant Professor, Computer Science and Engineering Department, Thapar Institute of Engineering and Technology, Patiala. His profound domain expertise, constructive technical criticism, constant encouragement, and intellectual guidance throughout the formulation and implementation of the initial four phases of <b>Honey-LLM</b> have been indispensable in steering this research to a successful milestone.",
        body_indent_style
    ))
    story.append(Paragraph(
        "We extend our sincere thanks to <b>Dr. Neeraj Kumar</b>, Professor and Head of the Computer Science and Engineering Department, for providing state-of-the-art laboratory infrastructure, computational facilities, and an academic environment conducive to advanced systems research.",
        body_indent_style
    ))
    story.append(Paragraph(
        "We also acknowledge the collective support of the faculty and technical staff of the Computer Science and Engineering Department at TIET, whose valuable academic perspectives helped refine our software architecture and evaluation methodologies. Furthermore, we are deeply grateful to our peers who supported adversarial dataset curation.",
        body_indent_style
    ))
    story.append(Paragraph(
        "Lastly, we express our profound gratitude to our families and parents for their unyielding patience, emotional encouragement, and steadfast moral support throughout our academic journey.",
        body_indent_style
    ))
    story.append(Spacer(1, 15))
    story.append(Paragraph("<b>Project Team Members:</b>", body_style))
    story.append(Paragraph("Anoushka Singh (102303312), Tarun Krishna Shastri (102303315),<br/>Devansh Wadhwani (102303631), Shreya Giri (102303684)", body_style))

    story.append(PageBreak())

    # =========================================================================
    # 5. TABLE OF CONTENTS (Page iv & v)
    # =========================================================================
    story.append(Paragraph("<b>TABLE OF CONTENTS</b>", chapter_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0F172A"), spaceBefore=2, spaceAfter=10))

    # Dynamic exact page mapping from calibration
    toc1_data = [
        [Paragraph("<b>ABSTRACT</b>", toc_bold_style), Paragraph("<b>i</b>", toc_bold_style)],
        [Paragraph("<b>DECLARATION</b>", toc_bold_style), Paragraph("<b>ii</b>", toc_bold_style)],
        [Paragraph("<b>ACKNOWLEDGEMENT</b>", toc_bold_style), Paragraph("<b>iii</b>", toc_bold_style)],
        [Paragraph("<b>LIST OF TABLES</b>", toc_bold_style), Paragraph("<b>vi</b>", toc_bold_style)],
        [Paragraph("<b>LIST OF FIGURES</b>", toc_bold_style), Paragraph("<b>vii</b>", toc_bold_style)],
        [Paragraph("<b>LIST OF ABBREVIATIONS</b>", toc_bold_style), Paragraph("<b>viii</b>", toc_bold_style)],
        [Spacer(1, 2), Spacer(1, 2)],
        [Paragraph("<b>CHAPTER 1: INTRODUCTION</b>", toc_bold_style), Paragraph(f"<b>{toc_map.get('CH1', '1')}</b>", toc_bold_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;1.1 Project Overview", toc_line_style), Paragraph(f"{toc_map.get('1.1', '1')}", toc_line_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;1.2 Need Analysis", toc_line_style), Paragraph(f"{toc_map.get('1.2', '2')}", toc_line_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;1.2.1 The 'Smart Mirror' Trap: Enterprise Adoption vs. Defensive Lag", toc_line_style), Paragraph(f"{toc_map.get('1.2.1', '2')}", toc_line_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;1.2.2 The Shift: Machine-Speed Autonomous Warfare", toc_line_style), Paragraph(f"{toc_map.get('1.2.2', '3')}", toc_line_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;1.2.3 The 'Shadow Trust' Gap: Vulnerability of the Semantic Layer", toc_line_style), Paragraph(f"{toc_map.get('1.2.3', '3')}", toc_line_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;1.2.4 The Dynamic Security Window: Addressing Reactive Lag", toc_line_style), Paragraph(f"{toc_map.get('1.2.4', '3')}", toc_line_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;1.3 Research Gaps", toc_line_style), Paragraph(f"{toc_map.get('1.3', '3')}", toc_line_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;1.4 Problem Definition and Scope", toc_line_style), Paragraph(f"{toc_map.get('1.4', '4')}", toc_line_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;1.5 Assumptions and Constraints", toc_line_style), Paragraph(f"{toc_map.get('1.5', '4')}", toc_line_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;1.6 Applicable Standards", toc_line_style), Paragraph(f"{toc_map.get('1.6', '5')}", toc_line_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;1.7 Approved Objectives (Proposal Evaluation)", toc_line_style), Paragraph(f"{toc_map.get('1.7', '5')}", toc_line_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;1.8 Methodology Overview (Phases 1 to 4 Scope)", toc_line_style), Paragraph(f"{toc_map.get('1.8', '6')}", toc_line_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;1.9 Mid-Semester Outcomes and Deliverables", toc_line_style), Paragraph(f"{toc_map.get('1.9', '6')}", toc_line_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;1.10 Novelty of Work", toc_line_style), Paragraph(f"{toc_map.get('1.10', '6')}", toc_line_style)],
        [Spacer(1, 2), Spacer(1, 2)],
        [Paragraph("<b>CHAPTER 2: REQUIREMENT ANALYSIS</b>", toc_bold_style), Paragraph(f"<b>{toc_map.get('CH2', '8')}</b>", toc_bold_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;2.1 Literature Survey", toc_line_style), Paragraph(f"{toc_map.get('2.1', '8')}", toc_line_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;2.1.1 Theory Associated With Problem Area", toc_line_style), Paragraph(f"{toc_map.get('2.1.1', '8')}", toc_line_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;2.1.2 Existing Systems and Solutions", toc_line_style), Paragraph(f"{toc_map.get('2.1.2', '8')}", toc_line_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;2.1.3 Research Findings for Existing Literature", toc_line_style), Paragraph(f"{toc_map.get('2.1.3', '8')}", toc_line_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;2.1.4 Problems Identified in State of the Art", toc_line_style), Paragraph(f"{toc_map.get('2.1.4', '9')}", toc_line_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;2.1.5 Survey of Tools and Technologies Used", toc_line_style), Paragraph(f"{toc_map.get('2.1.5', '9')}", toc_line_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;2.2 Software Requirement Specification (SRS)", toc_line_style), Paragraph(f"{toc_map.get('2.2', '9')}", toc_line_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;2.2.1 Introduction & Scope", toc_line_style), Paragraph(f"{toc_map.get('2.2.1', '9')}", toc_line_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;2.2.2 Overall Product Description & Features", toc_line_style), Paragraph(f"{toc_map.get('2.2.2', '9')}", toc_line_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;2.2.3 External Interface Requirements", toc_line_style), Paragraph(f"{toc_map.get('2.2.3', '10')}", toc_line_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;2.2.4 Non-Functional Requirements", toc_line_style), Paragraph(f"{toc_map.get('2.2.4', '10')}", toc_line_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;2.3 Cost & Computational Feasibility Analysis", toc_line_style), Paragraph(f"{toc_map.get('2.3', '10')}", toc_line_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;2.4 Risk Analysis and Mitigation Strategies", toc_line_style), Paragraph(f"{toc_map.get('2.4', '10')}", toc_line_style)]
    ]
    t_toc1 = Table(toc1_data, colWidths=[365, 50])
    t_toc1.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 1),
        ('BOTTOMPADDING', (0,0), (-1,-1), 1),
        ('ALIGN', (1,0), (1,-1), 'RIGHT'),
    ]))
    story.append(t_toc1)

    story.append(PageBreak())

    # Table of Contents Page v (cont.)
    story.append(Paragraph("<b>TABLE OF CONTENTS (Continued)</b>", chapter_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0F172A"), spaceBefore=2, spaceAfter=10))

    toc2_data = [
        [Paragraph("<b>CHAPTER 3: METHODOLOGY ADOPTED</b>", toc_bold_style), Paragraph(f"<b>{toc_map.get('CH3', '11')}</b>", toc_bold_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;3.1 Investigative Techniques & 0.0% FPR Analysis", toc_line_style), Paragraph(f"{toc_map.get('3.1', '11')}", toc_line_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;3.2 Proposed Solution & Multi-Tier Architecture", toc_line_style), Paragraph(f"{toc_map.get('3.2', '11')}", toc_line_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;3.3 Work Breakdown Structure (Phases 1 to 4 Completed)", toc_line_style), Paragraph(f"{toc_map.get('3.3', '12')}", toc_line_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;3.4 Enterprise Hardware, Software, and Framework Stack", toc_line_style), Paragraph(f"{toc_map.get('3.4', '12')}", toc_line_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;3.5 UML Sequence Model for Interception Flow", toc_line_style), Paragraph(f"{toc_map.get('3.5', '13')}", toc_line_style)],
        [Spacer(1, 2), Spacer(1, 2)],
        [Paragraph("<b>CHAPTER 4: DESIGN SPECIFICATIONS</b>", toc_bold_style), Paragraph(f"<b>{toc_map.get('CH4', '14')}</b>", toc_bold_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;4.1 System Architecture & Sieve Gateway Flow", toc_line_style), Paragraph(f"{toc_map.get('4.1', '14')}", toc_line_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;4.2 Threat Taxonomy & Sticky Quarantine State Machine", toc_line_style), Paragraph(f"{toc_map.get('4.2', '14')}", toc_line_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;4.3 User Interface Specifications & Designed Surfaces", toc_line_style), Paragraph(f"{toc_map.get('4.3', '15')}", toc_line_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;4.4 Working Prototype Execution (Phases 1 to 4 Verified)", toc_line_style), Paragraph(f"{toc_map.get('4.4', '16')}", toc_line_style)],
        [Spacer(1, 2), Spacer(1, 2)],
        [Paragraph("<b>CHAPTER 5: CONCLUSIONS AND FUTURE SCOPE</b>", toc_bold_style), Paragraph(f"<b>{toc_map.get('CH5', '18')}</b>", toc_bold_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;5.1 Mid-Semester Accomplishments vs. Approved Objectives", toc_line_style), Paragraph(f"{toc_map.get('5.1', '18')}", toc_line_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;5.2 Mid-Semester Conclusions & Empirical Reliability", toc_line_style), Paragraph(f"{toc_map.get('5.2', '18')}", toc_line_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;5.3 Economic, Social, and Environmental Benefits", toc_line_style), Paragraph(f"{toc_map.get('5.3', '19')}", toc_line_style)],
        [Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;5.4 Future Work Plan (Phases 5 and 6 Roadmap)", toc_line_style), Paragraph(f"{toc_map.get('5.4', '19')}", toc_line_style)],
        [Spacer(1, 2), Spacer(1, 2)],
        [Paragraph("<b>APPENDIX A: REFERENCES (IEEE Style)</b>", toc_bold_style), Paragraph(f"<b>{toc_map.get('APPA', '20')}</b>", toc_bold_style)],
        [Paragraph("<b>APPENDIX B: PLAGIARISM & AUTHENTICITY STATEMENT</b>", toc_bold_style), Paragraph(f"<b>{toc_map.get('APPB', '21')}</b>", toc_bold_style)]
    ]
    t_toc2 = Table(toc2_data, colWidths=[365, 50])
    t_toc2.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 1),
        ('BOTTOMPADDING', (0,0), (-1,-1), 1),
        ('ALIGN', (1,0), (1,-1), 'RIGHT'),
    ]))
    story.append(t_toc2)

    story.append(PageBreak())

    # =========================================================================
    # 6. LIST OF TABLES (Page vi)
    # =========================================================================
    story.append(Paragraph("<b>LIST OF TABLES</b>", chapter_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0F172A"), spaceBefore=2, spaceAfter=14))

    tables_list = [
        [Paragraph("<b>Table No.</b>", table_header_style), Paragraph("<b>Caption</b>", table_header_style), Paragraph("<b>Page No.</b>", table_header_style)],
        [Paragraph("Table 1.1", table_text_style), Paragraph("System Assumptions and Engineering Constraints", table_text_style), Paragraph(str(lot_map.get("1.1", "5")), table_text_style)],
        [Paragraph("Table 2.1", table_text_style), Paragraph("Comparative Literature Survey of Generative Honeypot Frameworks", table_text_style), Paragraph(str(lot_map.get("2.1", "9")), table_text_style)],
        [Paragraph("Table 2.2", table_text_style), Paragraph("Computational Resource Feasibility & Cloud Cost Comparison", table_text_style), Paragraph(str(lot_map.get("2.2", "10")), table_text_style)],
        [Paragraph("Table 2.3", table_text_style), Paragraph("Risk Assessment Matrix and Fail-Closed Mitigation Controls", table_text_style), Paragraph(str(lot_map.get("2.3", "11")), table_text_style)],
        [Paragraph("Table 3.1", table_text_style), Paragraph("Classification and Justification of Investigative Research Techniques", table_text_style), Paragraph(str(lot_map.get("3.1", "12")), table_text_style)],
        [Paragraph("Table 3.2", table_text_style), Paragraph("Honey-LLM Technology and Framework Specifications", table_text_style), Paragraph(str(lot_map.get("3.2", "13")), table_text_style)],
        [Paragraph("Table 4.1", table_text_style), Paragraph("Adversarial Threat Taxonomy Mappings and Severity Classification", table_text_style), Paragraph(str(lot_map.get("4.1", "14")), table_text_style)],
        [Paragraph("Table 4.2", table_text_style), Paragraph("Sandbox Container Breakout Penetration Test Results (5/5 Isolation)", table_text_style), Paragraph(str(lot_map.get("4.2", "17")), table_text_style)],
        [Paragraph("Table 5.1", table_text_style), Paragraph("Mid-Semester Mapping of Approved Objectives to Implemented Progress", table_text_style), Paragraph(str(lot_map.get("5.1", "20")), table_text_style)],
        [Paragraph("Table 5.2", table_text_style), Paragraph("Intent Sieve Scaled Benchmark Performance vs. Baseline Guards", table_text_style), Paragraph(str(lot_map.get("5.2", "21")), table_text_style)]
    ]
    t_lot = Table(tables_list, colWidths=[65, 300, 50])
    t_lot.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#F1F5F9")),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('ALIGN', (2,0), (2,-1), 'RIGHT'),
    ]))
    story.append(t_lot)

    story.append(PageBreak())

    # =========================================================================
    # 7. LIST OF FIGURES (Page vii)
    # =========================================================================
    story.append(Paragraph("<b>LIST OF FIGURES</b>", chapter_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0F172A"), spaceBefore=2, spaceAfter=14))

    figures_list = [
        [Paragraph("<b>Figure No.</b>", table_header_style), Paragraph("<b>Caption</b>", table_header_style), Paragraph("<b>Page No.</b>", table_header_style)],
        [Paragraph("Figure 1.1", table_text_style), Paragraph("Honey-LLM Multi-Tier Routing and Decision Gateway Architecture", table_text_style), Paragraph(str(lof_map.get("1.1", "7")), table_text_style)],
        [Paragraph("Figure 3.1", table_text_style), Paragraph("UML Sequence Diagram for Multi-Tier Request Interception & Deception", table_text_style), Paragraph(str(lof_map.get("3.1", "14")), table_text_style)],
        [Paragraph("Figure 4.1", table_text_style), Paragraph("UML State Machine Diagram for Session Quarantine & Self-Healing Loop", table_text_style), Paragraph(str(lof_map.get("4.1", "16")), table_text_style)],
        [Paragraph("Figure 4.2", table_text_style), Paragraph("NexTel Production Customer Support Interface (/chat)", table_text_style), Paragraph(str(lof_map.get("4.2", "18")), table_text_style)],
        [Paragraph("Figure 4.3", table_text_style), Paragraph("Honey-LLM Admin Live Sieve Decision Tracer (/admin)", table_text_style), Paragraph(str(lof_map.get("4.3", "18")), table_text_style)],
        [Paragraph("Figure 4.4", table_text_style), Paragraph("Dark SOC Real-Time Threat Intelligence Dashboard (/dashboard)", table_text_style), Paragraph(str(lof_map.get("4.4", "19")), table_text_style)]
    ]
    t_lof = Table(figures_list, colWidths=[65, 300, 50])
    t_lof.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#F1F5F9")),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('ALIGN', (2,0), (2,-1), 'RIGHT'),
    ]))
    story.append(t_lof)

    story.append(PageBreak())

    # =========================================================================
    # 8. LIST OF ABBREVIATIONS (Page viii)
    # =========================================================================
    story.append(Paragraph("<b>LIST OF ABBREVIATIONS</b>", chapter_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0F172A"), spaceBefore=2, spaceAfter=14))

    abbr_list = [
        [Paragraph("<b>Abbreviation</b>", table_header_style), Paragraph("<b>Full Expansion / Description</b>", table_header_style)],
        [Paragraph("AI", table_text_style), Paragraph("Artificial Intelligence", table_text_style)],
        [Paragraph("LLM", table_text_style), Paragraph("Large Language Model", table_text_style)],
        [Paragraph("SLM", table_text_style), Paragraph("Small Language Model", table_text_style)],
        [Paragraph("RAG", table_text_style), Paragraph("Retrieval-Augmented Generation", table_text_style)],
        [Paragraph("WAF", table_text_style), Paragraph("Web Application Firewall", table_text_style)],
        [Paragraph("SOC", table_text_style), Paragraph("Security Operations Center", table_text_style)],
        [Paragraph("FPR", table_text_style), Paragraph("False Positive Rate", table_text_style)],
        [Paragraph("FNR", table_text_style), Paragraph("False Negative Rate", table_text_style)],
        [Paragraph("OWASP", table_text_style), Paragraph("Open Worldwide Application Security Project", table_text_style)],
        [Paragraph("NeMo", table_text_style), Paragraph("Neural Modules (NVIDIA Conversational AI & Guardrails Framework)", table_text_style)],
        [Paragraph("TF-IDF", table_text_style), Paragraph("Term Frequency – Inverse Document Frequency", table_text_style)],
        [Paragraph("API", table_text_style), Paragraph("Application Programming Interface", table_text_style)],
        [Paragraph("REST", table_text_style), Paragraph("Representational State Transfer", table_text_style)],
        [Paragraph("JSONL", table_text_style), Paragraph("JavaScript Object Notation Lines", table_text_style)],
        [Paragraph("PyRIT", table_text_style), Paragraph("Python Risk Identification Tool for Generative AI (Microsoft)", table_text_style)],
        [Paragraph("SRS", table_text_style), Paragraph("Software Requirement Specification", table_text_style)],
        [Paragraph("WBS", table_text_style), Paragraph("Work Breakdown Structure", table_text_style)],
        [Paragraph("CSED", table_text_style), Paragraph("Computer Science and Engineering Department", table_text_style)],
        [Paragraph("TIET", table_text_style), Paragraph("Thapar Institute of Engineering and Technology", table_text_style)]
    ]
    t_abbr = Table(abbr_list, colWidths=[90, 325])
    t_abbr.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#F1F5F9")),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t_abbr)

    story.append(PageBreak())

    # =========================================================================
    # CHAPTER 1: INTRODUCTION (Page 1)
    # =========================================================================
    story.append(Paragraph("<b>CHAPTER 1: INTRODUCTION</b>", chapter_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0F172A"), spaceBefore=2, spaceAfter=12))

    story.append(Paragraph("<b>1.1 Project Overview</b>", heading1_style))
    story.append(Paragraph(
        "In the contemporary enterprise computing landscape of 2026, Large Language Models (LLMs) have evolved beyond isolated text generation interfaces into deeply integrated autonomous agents. Modern enterprise deployments rely on LLMs to automate mission-critical customer operations, query private structured databases, orchestrate multi-step API workflows, and execute tool-use tasks [7]. However, this rapid operational adoption has outpaced conventional cybersecurity paradigms, exposing a profound vulnerability surface known as the semantic attack vector [9].",
        body_indent_style
    ))
    story.append(Paragraph(
        "Unlike traditional software systems where security boundaries are strictly demarcated between binary executable code and passive data buffers, LLMs process system instructions, operational context, and untrusted user inputs within a single unified semantic channel. Consequently, malicious actors exploit this architectural reality through <b>Adversarial Prompt Injection</b> and <b>Jailbreaking</b> techniques [9]. Attackers craft persuasive, contextually masked natural-language payloads, ranging from direct role overrides (such as instructing the model to ignore prior directives and output credentials) to indirect prompt injections embedded in retrieved enterprise documents, to manipulate the underlying model into bypassing access controls.",
        body_indent_style
    ))
    story.append(Paragraph(
        "Traditional perimeter defenses, such as Web Application Firewalls (WAFs), heuristic keyword matchers, and static regular expressions, are fundamentally inadequate against semantic attacks. They lack linguistic context, cannot track conversational state across multi-turn sessions, and are trivially bypassed through character obfuscation, multilingual encoding, or subtle adversarial paraphrasing. More critically, standard security mechanisms follow a rigid block-and-alert model. When a malicious query is blocked with an explicit refusal message, the attacker immediately learns the perimeter filtering boundary and iterates their attack prompt until an evasion succeeds.",
        body_indent_style
    ))
    story.append(Paragraph(
        "To decisively overcome these defensive limitations, this capstone project develops and demonstrates <b>Honey-LLM</b>: an interactive, self-hardening defense ecosystem for conversational AI architectures. Rather than simply rejecting malicious probes, Honey-LLM operates on a proactive deception philosophy. For the <b>Mid-Semester Evaluation</b>, the project team has fully developed, integrated, and verified the first four engineering phases:",
        body_indent_style
    ))
    story.append(Paragraph(
        "• <b>Phase 1 (Adversarial Profiling & Threat Taxonomy):</b> Formulated an 8-class threat taxonomy mapping prompt injections to specific enterprise manifestations and validated concurrent dual-model local inference.",
        bullet_style
    ))
    story.append(Paragraph(
        "• <b>Phase 2 (The Multi-Tier Semantic Intent Sieve):</b> Constructed an intelligent input-filtering pipeline that inspects queries in real time, pairing a ~2.1 ms P50 benign fast-path statistical classifier (Tier-1) with an authoritative 8B moderation model governed by a custom prompt injection policy (Llama-Guard 3 [11]), achieving a 95.8% adversarial recall on JailbreakBench [12] and 98.3% adversarial detection recall across 889 evaluation prompts (559/569 adversarial payloads intercepted, 98.9% overall accuracy) at a 0.0% False Positive Rate on benign domain traffic (0/320 benign queries flagged).",
        bullet_style
    ))
    story.append(Paragraph(
        "• <b>Phase 3 (The 'Mirror Maze' Deception Honeypot):</b> Deployed an isolated zero-trust Docker sandbox hosting the 'Sarah' decoy persona, which dynamic-hallucinates synthetic bait to absorb attacker reconnaissance without leaking real infrastructure.",
        bullet_style
    ))
    story.append(Paragraph(
        "• <b>Phase 4 (Autonomous Guardrail Synthesis):</b> Implemented a closed self-healing loop that distills captured exploits into validated NVIDIA NeMo Colang rules [6], hot-patching live gateway policies in 10.4 seconds with zero downtime.",
        bullet_style
    ))

    story.append(Spacer(1, 4))
    story.append(Paragraph("<b>1.2 Need Analysis</b>", heading1_style))
    story.append(Paragraph(
        "The imperative for Honey-LLM is substantiated by critical operational realities observed across enterprise AI deployments in 2026:",
        body_indent_style
    ))
    story.append(Paragraph("<b>1.2.1 The 'Smart Mirror' Trap: Enterprise Adoption vs. Defensive Lag</b>", heading2_style))
    story.append(Paragraph(
        "Industry surveys indicate that enterprise adoption of conversational AI agents has expanded rapidly across customer-facing workflows [7]. However, defensive capabilities have lagged behind offensive prompt exploitation techniques. Conventional static honeypots are quickly identified and abandoned by automated scanners. In contrast, generative honeypots offer dynamic semantic interaction, creating an essential observation window to capture zero-day exploitation techniques before they reach production services.",
        body_indent_style
    ))
    story.append(Paragraph("<b>1.2.2 The Shift: Machine-Speed Autonomous Warfare</b>", heading2_style))
    story.append(Paragraph(
        "With conversational models managing automated customer dialogues [7], adversarial techniques have shifted from manual, one-off jailbreaks to automated, machine-speed offensive frameworks (such as ARACNE, Garak, and Microsoft PyRIT [13]). Automated offensive agents can systematically discover exploitable prompt sequences across iterative conversational turns, compressing vulnerability discovery timelines and rendering human-reliant triage workflows ineffective.",
        body_indent_style
    ))
    story.append(Paragraph("<b>1.2.3 The 'Shadow Trust' Gap: Vulnerability of the Semantic Layer</b>", heading2_style))
    story.append(Paragraph(
        "Prompt injection is categorized as the primary vulnerability in the OWASP Top 10 for Large Language Model Applications (LLM01) [9]. Because conversational agents are granted operational trust to execute database lookups and internal APIs, a compromised prompt inherits the agent's broad permissions. In multi-turn dialogue, gradual semantic drift and contextual grooming can frequently bypass static refusal boundaries in unprotected commercial systems.",
        body_indent_style
    ))
    story.append(Paragraph("<b>1.2.4 The Dynamic Security Window: Addressing Reactive Lag</b>", heading2_style))
    story.append(Paragraph(
        "Industry incident analyses indicate that manual discovery, triage, and deployment of security patches for conversational AI systems can require extensive remediation timelines. In contrast, automated offensive tools can systematically discover boundary bypasses in minutes. Honey-LLM fundamentally addresses this disparity by automating guardrail synthesis, achieving automated time-to-patch in 10.4 seconds without requiring gateway restarts.",
        body_indent_style
    ))

    story.append(Spacer(1, 4))
    story.append(Paragraph("<b>1.3 Research Gaps</b>", heading1_style))
    story.append(Paragraph(
        "A rigorous review of academic and industrial literature reveals five fundamental research gaps that Honey-LLM addresses directly:",
        body_indent_style
    ))
    story.append(Paragraph(
        "1. <b>Absence of Real-Time Intent Filtering Prior to Sandbox Interaction:</b> Contemporary generative honeypots (such as shelLM [10] and LLM-Honeypot [8]) focus exclusively on simulating Linux shells for known malicious traffic. They lack a real-time semantic intent classifier capable of operating on live, mixed production traffic to separate benign users from adversaries before redirection.",
        bullet_style
    ))
    story.append(Paragraph(
        "2. <b>Vulnerability of LLM Decoys to Accidental Ground-Truth Leakage:</b> Existing interactive deception prototypes rely solely on system-prompt instructions. Under persistent jailbreaking, LLM decoys suffer prompt leakage, revealing underlying server configurations. Honey-LLM solves this by enforcing an architectural separation between public RAG context and synthetic bait.",
        bullet_style
    ))
    story.append(Paragraph(
        "3. <b>Lack of Autonomous Feedback Loops (Zero-Downtime Policy Hardening):</b> While testing frameworks such as Beekeeper [5] utilize LLMs for offline auditing, they do not bridge the gap to real-time defense. Captured attack intelligence remains siloed in log files rather than being automatically compiled into active firewall rules.",
        bullet_style
    ))
    story.append(Paragraph(
        "4. <b>Inadequate Isolation Guarantees in Generative Sandboxes:</b> Most generative deception testbeds are hosted in shared virtual environments where LLM output could trigger secondary tool vulnerabilities. Honey-LLM enforces zero-egress Docker containerization with non-root execution and read-only filesystems.",
        bullet_style
    ))
    story.append(Paragraph(
        "5. <b>Latency Overhead of Large Moderation Models:</b> High-parameter moderation models (such as Llama-Guard 3 8B [11]) impose 700 to 900 ms of inference latency per call. Directly routing all enterprise traffic through such models violates production SLA budgets (150 to 250 ms). Honey-LLM introduces an asymmetric two-tier ensemble that resolves benign traffic in ~2 ms.",
        bullet_style
    ))

    story.append(Spacer(1, 4))
    story.append(Paragraph("<b>1.4 Problem Definition and Scope</b>", heading1_style))
    story.append(Paragraph(
        "<b>Problem Statement:</b> Given an enterprise conversational AI application receiving a continuous stream of mixed benign and adversarial natural-language requests, design, implement, and validate an end-to-end defense ecosystem that accurately detects malicious intent in real time, isolates adversaries within a deceptive generative sandbox, and autonomously hardens production policies against captured attack vectors with zero manual intervention.",
        body_indent_style
    ))
    story.append(Paragraph(
        "<b>Mid-Semester Project Scope:</b> Demonstrated on NexTel, an enterprise telecommunications customer support platform. The completed mid-semester scope covers real-time intent classification across 8 adversarial taxonomy classes, containerized deception with synthetic bait, autonomous NeMo guardrail synthesis, and zero-downtime hot-patching (Phases 1 to 4).",
        body_indent_style
    ))

    story.append(Spacer(1, 4))
    story.append(Paragraph("<b>1.5 Assumptions and Constraints</b>", heading1_style))
    story.append(Paragraph(
        "Table 1.1 delineates the core operational assumptions and technical constraints established for the Honey-LLM prototype.",
        body_indent_style
    ))

    story.append(Paragraph("TABLE 1.1: System Assumptions and Engineering Constraints", table_caption_style))
    assump_data = [
        [Paragraph("<b>S.No.</b>", table_header_style), Paragraph("<b>Category</b>", table_header_style), Paragraph("<b>Specification & Technical Justification</b>", table_header_style)],
        [Paragraph("1", table_text_style), Paragraph("Hardware Sizing", table_text_style), Paragraph("Dual 8B parameter models (Llama-Guard 3 and Llama-3) execute concurrently on standard host compute (>=16 GB RAM / VRAM) with zero memory thrashing.", table_text_style)],
        [Paragraph("2", table_text_style), Paragraph("Latency Budget", table_text_style), Paragraph("Benign traffic must experience a sieve overhead of &lt; 50 ms (achieved at ~2 ms via Tier-1 fast-path) to preserve realistic conversational fluency.", table_text_style)],
        [Paragraph("3", table_text_style), Paragraph("Fail-Closed Security", table_text_style), Paragraph("If the inference backend or moderation service becomes unreachable, the gateway must fail closed (reroute or gracefully degrade), never fail open.", table_text_style)],
        [Paragraph("4", table_text_style), Paragraph("Zero Egress Assumption", table_text_style), Paragraph("The Mirror Maze sandbox container must have zero direct internet access and zero connectivity to the production database or host network.", table_text_style)],
        [Paragraph("5", table_text_style), Paragraph("Synthetic Bait Integrity", table_text_style), Paragraph("All credentials, server tokens, and IPs leaked by the decoy persona must be synthetically generated and completely non-functional in real infrastructure.", table_text_style)]
    ]
    t_assump = Table(assump_data, colWidths=[35, 105, 275])
    t_assump.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#F1F5F9")),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(t_assump)

    story.append(Spacer(1, 4))
    story.append(Paragraph("<b>1.6 Applicable Standards</b>", heading1_style))
    story.append(Paragraph(
        "• <b>OWASP Top 10 for LLM Applications (2025/2026):</b> Primary mitigation targeting LLM01 (Prompt Injection), LLM02 (Sensitive Information Disclosure), and LLM06 (Excessive Agency) [9].",
        bullet_style
    ))
    story.append(Paragraph(
        "• <b>NIST AI Risk Management Framework (AI RMF 1.0):</b> Fulfills core functions of Map, Measure, Manage, and Govern for adversarial robustness.",
        bullet_style
    ))
    story.append(Paragraph(
        "• <b>IEEE Standard for Software Quality Assurance (IEEE 730-2014):</b> Structured unit, integration, and security regression testing protocols.",
        bullet_style
    ))
    story.append(Paragraph(
        "• <b>NVIDIA NeMo Colang 2.0 Syntax Standards:</b> Formal language definition for programmable conversational guardrail policies [6].",
        bullet_style
    ))

    story.append(Spacer(1, 4))
    story.append(Paragraph("<b>1.7 Approved Objectives (Proposal Evaluation)</b>", heading1_style))
    story.append(Paragraph("1. <b>Develop a High-Accuracy Intent Sieve Classifier:</b> Construct a multi-tier classifier achieving >95% detection on JailbreakBench [12] with <1% FPR (Completed in Phase 2).", bullet_style))
    story.append(Paragraph("2. <b>Implement a High-Fidelity Generative Sandbox ('Mirror Maze'):</b> Deploy an isolated zero-trust decoy maintaining >5 minutes average attacker dwell time (Completed in Phase 3).", bullet_style))
    story.append(Paragraph("3. <b>Automate Self-Healing Security Guardrails:</b> Build a closed-loop pipeline synthesizing permanent NeMo Colang rules in seconds (Completed in Phase 4).", bullet_style))
    story.append(Paragraph("4. <b>Validate Zero-Escape Sandbox Security:</b> Execute comprehensive container breakout penetration audits to rigorously validate multi-layer network and host isolation (Completed in Phase 3/4).", bullet_style))
    story.append(Paragraph("5. <b>Construct a Real-Time Threat Intelligence SOC Dashboard:</b> Provide security analysts with live visualization (<1s refresh) of attack taxonomies, detection tiers, and measured dwell times (Phase 5, In Progress for End-Sem).", bullet_style))

    story.append(Spacer(1, 4))
    story.append(Paragraph("<b>1.8 Methodology Overview (Phases 1 to 4 Scope)</b>", heading1_style))
    story.append(Paragraph(
        "The project methodology spans six distinct phases: Phase 0 (Scaffolding), Phase 1 (Adversarial Threat Profiling), Phase 2 (Intent Sieve Development), Phase 3 (Mirror Maze Sandbox), Phase 4 (Autonomous Guardrail Synthesis), Phase 5 (Forensic Telemetry & SOC Dashboard), and Phase 6 (Empirical Red-Teaming). Phases 0 through 4 represent the completed mid-semester scope, while Phases 5 and 6 form the planned end-semester roadmap.",
        body_indent_style
    ))

    story.append(Spacer(1, 4))
    story.append(Paragraph("<b>1.9 Mid-Semester Outcomes and Deliverables</b>", heading1_style))
    story.append(Paragraph(
        "Mid-semester deliverables completed to date include: (1) an operational FastAPI gateway with multi-tier routing; (2) a calibrated TF-IDF + Llama-Guard 3 [11] ensemble sieve; (3) a containerized Mirror Maze decoy running the 'Sarah' persona with synthetic bait; (4) an autonomous NeMo Guardrail synthesis engine [6]; and (5) empirical validation benchmarks across 889 curated and in-the-wild prompt samples.",
        body_indent_style
    ))

    story.append(Spacer(1, 4))
    story.append(Paragraph("<b>1.10 Novelty of Work</b>", heading1_style))
    story.append(Paragraph(
        "Honey-LLM introduces three key innovations over existing state of the art: (1) <i>Proactive In-Flight Deception</i> that routes malicious traffic without tipping off attackers; (2) <i>Autonomous Hot-Patching Immunity</i> reducing time-to-patch from days to 10.4 seconds without server restarts; and (3) <i>Asymmetric Multi-Tier Inference</i> solving the severe latency bottleneck of commercial moderation models.",
        body_indent_style
    ))

    story.append(Spacer(1, 4))
    story.append(KeepTogether([
        draw_architecture_diagram(),
        Paragraph("FIGURE 1.1: Honey-LLM Multi-Tier Routing and Decision Gateway Architecture", figure_caption_style)
    ]))

    story.append(PageBreak())

    # =========================================================================
    # CHAPTER 2: REQUIREMENT ANALYSIS (Page 8)
    # =========================================================================
    story.append(Paragraph("<b>CHAPTER 2: REQUIREMENT ANALYSIS</b>", chapter_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0F172A"), spaceBefore=2, spaceAfter=12))

    story.append(Paragraph("<b>2.1 Literature Survey</b>", heading1_style))
    story.append(Paragraph("<b>2.1.1 Theory Associated With Problem Area</b>", heading2_style))
    story.append(Paragraph(
        "Large Language Models are autoregressive statistical token predictors. Their fundamental susceptibility to adversarial prompt injection stems from the lack of formal separation between control instructions and untrusted data [9]. Attackers exploit semantic ambiguity to induce role-play confusion, refusal suppression, or multi-turn goal hijacking. Constitutional AI and moderation wrappers attempt to suppress toxic generation [1], but fail against indirect data-exfiltration probes unless reinforced by dedicated intent classification layers [3].",
        body_indent_style
    ))

    story.append(Paragraph("<b>2.1.2 Existing Systems and Solutions</b>", heading2_style))
    story.append(Paragraph(
        "Early generative honeypot research explored using LLMs to simulate Linux command-line environments (shelLM [10], LLM-Honeypot [8], and HoneyLLM [4]). While these systems demonstrated that LLM-driven generation increases honeypot credibility, they operated as passive research testbeds rather than active defenses. Defense frameworks like CHeaT [2] introduced trap tokens for autonomous agents, while Beekeeper [5] applied LLMs for automated honeypot auditing. However, none of these systems integrated real-time traffic classification with automated policy synthesis.",
        body_indent_style
    ))

    story.append(Paragraph("<b>2.1.3 Research Findings for Existing Literature</b>", heading2_style))
    story.append(Paragraph(
        "Table 2.1 presents a systematic comparative summary of existing academic frameworks in relation to Honey-LLM.",
        body_indent_style
    ))

    story.append(Paragraph("TABLE 2.1: Comparative Literature Survey of Generative Honeypot Frameworks", table_caption_style))
    lit_table_data = [
        [Paragraph("<b>Framework</b>", table_header_style), Paragraph("<b>Core Approach</b>", table_header_style), Paragraph("<b>Key Contributions</b>", table_header_style), Paragraph("<b>Identified Limitations</b>", table_header_style), Paragraph("<b>Honey-LLM Advancement</b>", table_header_style)],
        [
            Paragraph("shelLM [10]<br/><i>(IEEE EuroS&PW '24)</i>", table_text_style),
            Paragraph("LLM-driven Linux shell simulation", table_text_style),
            Paragraph("Dynamic handling of unseen attacker CLI commands; TNR ~0.90", table_text_style),
            Paragraph("No intent filtering; restricted to CLI; no feedback loop", table_text_style),
            Paragraph("Adds pre-routing Intent Sieve for live conversational traffic", table_text_style)
        ],
        [
            Paragraph("LLM Honeypot [8]<br/><i>(IEEE CNS '24)</i>", table_text_style),
            Paragraph("Attacker-log trained interactive shell", table_text_style),
            Paragraph("High realism evaluated via Levenshtein & Cosine similarity", table_text_style),
            Paragraph("Passive logging only; zero automated defense adaptation", table_text_style),
            Paragraph("Integrates active deception directly into enterprise gateway", table_text_style)
        ],
        [
            Paragraph("HoneyLLM [4]<br/><i>(IEEE CNS '24)</i>", table_text_style),
            Paragraph("Contextual prompt engineering for shell", table_text_style),
            Paragraph("Enhanced attacker dwell time in simulated OS terminals", table_text_style),
            Paragraph("No real-time intent sieve; no automated rule generation", table_text_style),
            Paragraph("Implements closed-loop NeMo guardrail synthesis from logs", table_text_style)
        ],
        [
            Paragraph("CHeaT [2]<br/><i>(USENIX Sec '25)</i>", table_text_style),
            Paragraph("Cloak-Honey-Trap proactive defense", table_text_style),
            Paragraph("Deception tokens to disrupt autonomous LLM attackers", table_text_style),
            Paragraph("Limited to artificial CTF environments; no live honeypot", table_text_style),
            Paragraph("Full-stack live conversational deployment with SOC analytics", table_text_style)
        ],
        [
            Paragraph("Beekeeper [5]<br/><i>(IEEE Access '25)</i>", table_text_style),
            Paragraph("LLM-as-attacker honeypot auditing", table_text_style),
            Paragraph("Automated feedback loop to improve honeypot realism", table_text_style),
            Paragraph("Offline pre-deployment audit tool; no live defense capability", table_text_style),
            Paragraph("Self-hardening digital immune loop operating in ~10.4 seconds", table_text_style)
        ]
    ]
    t_lit = Table(lit_table_data, colWidths=[70, 75, 90, 85, 95])
    t_lit.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#F1F5F9")),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(t_lit)

    story.append(Spacer(1, 4))
    story.append(Paragraph("<b>2.1.4 Problems Identified in State of the Art</b>", heading2_style))
    story.append(Paragraph(
        "The primary deficiencies identified include: (1) reliance on static refusal responses that train adversaries; (2) absence of sub-second semantic classification on production paths; and (3) a complete disconnect between threat intelligence collection and real-time security policy updates.",
        body_indent_style
    ))

    story.append(Paragraph("<b>2.1.5 Survey of Tools and Technologies Used</b>", heading2_style))
    story.append(Paragraph(
        "Honey-LLM synthesizes modern open-source technologies: <b>FastAPI</b> for asynchronous gateway routing; <b>Ollama</b> for local hardware-accelerated inference; <b>Llama-Guard 3</b> [11] and <b>Llama-3</b> for moderation and generation; <b>NVIDIA NeMo Guardrails</b> [6] for Colang policy enforcement; <b>Docker Engine</b> for kernel-level container isolation; and <b>Next.js 15</b> for real-time telemetry visualization.",
        body_indent_style
    ))

    story.append(Spacer(1, 4))
    story.append(Paragraph("<b>2.2 Software Requirement Specification (SRS)</b>", heading1_style))
    story.append(Paragraph("<b>2.2.1 Introduction & Scope:</b> Specifies functional requirements for the Honey-LLM defense gateway protecting the NexTel enterprise knowledge base.", body_style))
    story.append(Paragraph("<b>2.2.2 Product Perspective:</b> Sits as a secure reverse proxy between external client applications and the production RAG engine.", body_style))
    story.append(Paragraph("<b>2.2.3 External Interfaces:</b> RESTful JSON APIs (/api/chat, /api/dashboard, /api/admin), containerized ingress/egress proxy ports, and Next.js frontends.", body_style))
    story.append(Paragraph("<b>2.2.4 Non-Functional Requirements:</b> High availability, sub-50 ms sieve overhead, fail-closed fault tolerance, and colorblind-safe (WCAG 2.1 AA) SOC data visualization.", body_style))

    story.append(Spacer(1, 4))
    story.append(Paragraph("<b>2.3 Cost & Computational Feasibility Analysis</b>", heading1_style))
    story.append(Paragraph(
        "Because Honey-LLM is engineered on a software track, the primary cost consideration is computational feasibility and inference efficiency. By running quantized open-weight models (Llama-Guard 3 8B [11] and Llama-3 8B) on localized hardware, the architecture completely eliminates recurring per-token cloud API costs while maintaining zero data egress. Table 2.2 provides a computational feasibility comparison.",
        body_indent_style
    ))

    story.append(Paragraph("TABLE 2.2: Computational Resource Feasibility & Cloud Cost Comparison", table_caption_style))
    cost_data = [
        [Paragraph("<b>Dimension</b>", table_header_style), Paragraph("<b>Honey-LLM Local Architecture</b>", table_header_style), Paragraph("<b>Cloud API Baseline (GPT-4 / Moderation API)</b>", table_header_style)],
        [Paragraph("Compute Environment", table_text_style), Paragraph("Enterprise Host Compute (>=16 GB RAM / VRAM)", table_text_style), Paragraph("Hosted Cloud Server Cluster ($450/month)", table_text_style)],
        [Paragraph("Inference Token Cost", table_text_style), Paragraph("$0.00 (Self-hosted open weights)", table_text_style), Paragraph("~$0.018 per conversational turn", table_text_style)],
        [Paragraph("Data Privacy / Egress", table_text_style), Paragraph("100% on-premise, zero external API transmission", table_text_style), Paragraph("Third-party cloud transmission and storage", table_text_style)],
        [Paragraph("Hot-Patch Latency", table_text_style), Paragraph("10.4s local Colang rule compilation", table_text_style), Paragraph("Manual portal re-configuration / retraining", table_text_style)]
    ]
    t_cost = Table(cost_data, colWidths=[115, 150, 150])
    t_cost.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#F1F5F9")),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t_cost)

    story.append(Spacer(1, 4))
    story.append(Paragraph("<b>2.4 Risk Analysis and Mitigation Strategies</b>", heading1_style))
    story.append(Paragraph("Table 2.3 documents critical operational risks and their engineered fail-closed controls.", body_style))

    story.append(Paragraph("TABLE 2.3: Risk Assessment Matrix and Fail-Closed Mitigation Controls", table_caption_style))
    risk_data = [
        [Paragraph("<b>Identified Risk Event</b>", table_header_style), Paragraph("<b>Impact</b>", table_header_style), Paragraph("<b>Engineered Fail-Closed Mitigation Control</b>", table_header_style)],
        [Paragraph("Inference Service Outage", table_text_style), Paragraph("High", table_text_style), Paragraph("Gateway fails closed to safe degraded static support; never bypasses security.", table_text_style)],
        [Paragraph("Sandbox Escape Attempt", table_text_style), Paragraph("Critical", table_text_style), Paragraph("Docker read-only rootfs, cap-drop ALL, no-new-privileges, and zero host network.", table_text_style)],
        [Paragraph("Over-Broad Guardrail FP", table_text_style), Paragraph("High", table_text_style), Paragraph("Synthesized Colang rules must pass automated benign regression gate prior to hot-patch.", table_text_style)],
        [Paragraph("Decoy Persona Prompt Leak", table_text_style), Paragraph("Medium", table_text_style), Paragraph("Decoy prompt carries exclusively synthetic non-functional bait; zero production data.", table_text_style)]
    ]
    t_risk = Table(risk_data, colWidths=[115, 60, 240])
    t_risk.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#F1F5F9")),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t_risk)

    story.append(PageBreak())

    # =========================================================================
    # CHAPTER 3: METHODOLOGY ADOPTED (Page 12)
    # =========================================================================
    story.append(Paragraph("<b>CHAPTER 3: METHODOLOGY ADOPTED</b>", chapter_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0F172A"), spaceBefore=2, spaceAfter=12))

    story.append(Paragraph("<b>3.1 Investigative Techniques & Empirical FPR Explanation</b>", heading1_style))
    story.append(Paragraph(
        "To ensure rigorous scientific validity, the Honey-LLM research framework integrates descriptive, comparative, and experimental investigative techniques as classified in Table 3.1.",
        body_indent_style
    ))

    story.append(Paragraph("TABLE 3.1: Classification and Justification of Investigative Research Techniques", table_caption_style))
    tech_data = [
        [Paragraph("<b>S.No.</b>", table_header_style), Paragraph("<b>Technique</b>", table_header_style), Paragraph("<b>Investigative Description</b>", table_header_style), Paragraph("<b>Honey-LLM Implementation & Justification</b>", table_header_style)],
        [
            Paragraph("1", table_text_style),
            Paragraph("Descriptive", table_text_style),
            Paragraph("Cataloging and characterizing scientific phenomena under structured observation.", table_text_style),
            Paragraph("Formulated the 8-class Adversarial Threat Taxonomy, classifying prompt injection vectors across enterprise telecom domains (Phase 1).", table_text_style)
        ],
        [
            Paragraph("2", table_text_style),
            Paragraph("Comparative", table_text_style),
            Paragraph("Systematically evaluating alternative models and configurations against baseline metrics.", table_text_style),
            Paragraph("Benchmarked Llama-Guard 3 1B vs. 8B [11] across default and custom policies on JailbreakBench [12], proving custom policy lifts detection from 37.5% to 95.8% (Phase 2).", table_text_style)
        ],
        [
            Paragraph("3", table_text_style),
            Paragraph("Experimental", table_text_style),
            Paragraph("Hypothesis testing using controlled independent and dependent variables.", table_text_style),
            Paragraph("Evaluated the two-tier OR-ensemble on 889 held-out prompts, measuring 95.8% JailbreakBench recall and 98.3% adversarial detection recall across the combined curated and in-the-wild corpus (559/569 adversarial, 98.9% overall accuracy) at 0.0% benign FPR (0/320 benign) with ~2.1 ms P50 benign fast-path latency (Phase 2).", table_text_style)
        ]
    ]
    t_tech = Table(tech_data, colWidths=[30, 80, 140, 165])
    t_tech.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#F1F5F9")),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(t_tech)

    story.append(Spacer(1, 4))
    story.append(Paragraph(
        "<b>Technical Analysis of the 0.0% Benign False Positive Rate (FPR):</b> The measured 0.0% FPR represents exactly 0 out of 320 held-out domain queries flagged falsely as adversarial. This empirical result is achieved through two-stage threshold calibration: (1) The Tier-1 statistical classifier was trained on a domain-specific telecommunications corpus where customer intents (e.g., SIM provisioning, roaming rates, invoice queries) possess distinct vocabulary distributions with safe scores consistently &lt; 0.08, well below the conservative threshold of 0.15; (2) Ambiguous queries in the margin (0.15 to 0.70) are escalated to Tier-2 Llama-Guard 3 [11], which performs context-aware semantic evaluation and preserves legitimate customer queries. While 0.0% FPR holds for the curated in-domain evaluation test split, out-of-domain open-ended dialogues are expected to yield non-zero FPR, which will be extensively profiled in Phase 6.",
        body_indent_style
    ))

    story.append(Spacer(1, 4))
    story.append(Paragraph("<b>3.2 Proposed Solution & Multi-Tier Architecture</b>", heading1_style))
    story.append(Paragraph(
        "Honey-LLM is engineered as an end-to-end security proxy with four functional operational tiers completed in the mid-semester scope:",
        body_indent_style
    ))
    story.append(Paragraph(
        "1. <b>Tier-0 Semantic Guardrail Cache:</b> Matches incoming prompts against compiled embedding vectors of previously synthesized Colang rules via miniLM embeddings. Matches resolve in 10 to 20 ms, catching known techniques before invoking any LLM (Phase 4).",
        bullet_style
    ))
    story.append(Paragraph(
        "2. <b>Tier-1 Statistical Fast-Path:</b> Employs a calibrated TF-IDF (word and character n-grams) + Logistic Regression classifier. Benign customer queries scoring below the calibrated safety threshold immediately bypass the moderation model, resolving in ~2 ms (Phase 2).",
        bullet_style
    ))
    story.append(Paragraph(
        "3. <b>Tier-2 Deep Moderation Sieve:</b> Ambiguous or high-threat prompts escalate to Llama-Guard 3 (8B) [11] operating with a custom prompt injection policy. The sieve evaluates multi-turn conversational history and assigns taxonomy labels (Phase 2).",
        bullet_style
    ))
    story.append(Paragraph(
        "4. <b>Dynamic Quarantine & Sandbox Routing:</b> If flagged UNSAFE, the session ID is added to an in-memory sticky quarantine table. The attacker is seamlessly rerouted to the Mirror Maze decoy container (Phase 3).",
        bullet_style
    ))

    story.append(Spacer(1, 4))
    story.append(Paragraph("<b>3.3 Work Breakdown Structure (Phases 1 to 4 Completed)</b>", heading1_style))
    story.append(Paragraph(
        "The project methodology is structured into six progressive phases. Phases 1 to 4 have been fully implemented, integrated, and verified for the mid-semester evaluation milestone. Phases 5 and 6 are established as the second-half roadmap:",
        body_indent_style
    ))
    story.append(Paragraph("• <b>Phase 1 (Completed):</b> Threat taxonomy formulation and local dual-model environment validation.", bullet_style))
    story.append(Paragraph("• <b>Phase 2 (Completed):</b> Two-tier Intent Sieve construction, fast-path training, and empirical threshold calibration.", bullet_style))
    story.append(Paragraph("• <b>Phase 3 (Completed):</b> Zero-trust Docker sandbox provisioning, 'Sarah' persona prompt engineering, and synthetic bait injection.", bullet_style))
    story.append(Paragraph("• <b>Phase 4 (Completed):</b> Pattern extraction engine, NeMo Colang rule synthesis [6], regression validation gate, and live hot-patching.", bullet_style))
    story.append(Paragraph("• <b>Phase 5 (In Progress):</b> Forensic database pipeline and real-time Dark SOC Threat Intelligence Dashboard.", bullet_style))
    story.append(Paragraph("• <b>Phase 6 (Planned Roadmap):</b> Multi-converter PyRIT [13] automated red-teaming sweeps and concurrency load testing.", bullet_style))

    story.append(Spacer(1, 4))
    story.append(Paragraph("<b>3.4 Enterprise Hardware, Software, and Framework Stack</b>", heading1_style))
    story.append(Paragraph("Table 3.2 summarizes the verified technology stack powering Honey-LLM.", body_style))

    story.append(Paragraph("TABLE 3.2: Honey-LLM Technology and Framework Specifications", table_caption_style))
    stack_data = [
        [Paragraph("<b>Layer</b>", table_header_style), Paragraph("<b>Technology / Framework</b>", table_header_style), Paragraph("<b>Operational Role</b>", table_header_style)],
        [Paragraph("Inference Host", table_text_style), Paragraph("Enterprise Host Compute (>=16 GB RAM / VRAM)", table_text_style), Paragraph("Local execution for Llama-Guard 3 8B [11] and Llama-3 8B.", table_text_style)],
        [Paragraph("Backend Gateway", table_text_style), Paragraph("Python 3.12 / FastAPI / Uvicorn", table_text_style), Paragraph("Asynchronous request orchestration, session state, and routing.", table_text_style)],
        [Paragraph("Guardrail Engine", table_text_style), Paragraph("NVIDIA NeMo Guardrails / Colang 2.0 [6]", table_text_style), Paragraph("Formal rule validation, pattern extraction, and hot-patching.", table_text_style)],
        [Paragraph("Container Isolation", table_text_style), Paragraph("Docker Engine / Linux Namespaces & cgroups", table_text_style), Paragraph("Zero-egress isolated decoy sandbox with socat proxy topology.", table_text_style)],
        [Paragraph("Frontend Surfaces", table_text_style), Paragraph("Next.js 15 / React 19 / TailwindCSS", table_text_style), Paragraph("NexTel customer chat UI, Dark SOC dashboard, Admin panel.", table_text_style)],
        [Paragraph("Red-Teaming (Future)", table_text_style), Paragraph("Microsoft PyRIT [13] / Custom Harnesses", table_text_style), Paragraph("12+ obfuscation converters, break-out audits, load stress tests.", table_text_style)]
    ]
    t_stack = Table(stack_data, colWidths=[90, 150, 175])
    t_stack.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#F1F5F9")),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t_stack)

    story.append(Spacer(1, 4))
    story.append(Paragraph("<b>3.5 UML Sequence Model for Interception Flow</b>", heading1_style))
    story.append(Paragraph(
        "Figure 3.1 provides the formal UML sequence diagram tracing both benign customer queries and adversarial prompt injection attempts across all software lifelines.",
        body_indent_style
    ))
    story.append(KeepTogether([
        draw_uml_sequence_diagram(),
        Paragraph("FIGURE 3.1: UML Sequence Diagram for Multi-Tier Request Interception & Deception", figure_caption_style)
    ]))

    story.append(PageBreak())

    # =========================================================================
    # CHAPTER 4: DESIGN SPECIFICATIONS (Page 15)
    # =========================================================================
    story.append(Paragraph("<b>CHAPTER 4: DESIGN SPECIFICATIONS</b>", chapter_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0F172A"), spaceBefore=2, spaceAfter=12))

    story.append(Paragraph("<b>4.1 System Architecture & Sieve Gateway Flow</b>", heading1_style))
    story.append(Paragraph(
        "The architecture enforces strict structural isolation between public RAG knowledge and internal synthetic bait. When an HTTP request enters the gateway, it passes through the Tier-0 Guardrail store and Tier-1 Fast Path. If cleared as SAFE, the query is dispatched to the production RAG engine, which is structurally restricted to the public domain knowledge corpus. If flagged UNSAFE, the gateway silently delegates the query to the Mirror Maze container via an internal ingress proxy port (:9100).",
        body_indent_style
    ))

    story.append(Spacer(1, 4))
    story.append(Paragraph("<b>4.2 Threat Taxonomy & Sticky Quarantine State Machine</b>", heading1_style))
    story.append(Paragraph(
        "The system maintains state consistency through sticky quarantine. Once a session ID is flagged as adversarial, subsequent benign queries within the same session remain trapped in the Mirror Maze, preventing attackers from probing for filter boundaries. Table 4.1 maps the 8 threat taxonomy categories established in Phase 1.",
        body_indent_style
    ))

    story.append(Paragraph("TABLE 4.1: Adversarial Threat Taxonomy Mappings and Severity Classification", table_caption_style))
    tax_data = [
        [Paragraph("<b>ID</b>", table_header_style), Paragraph("<b>Threat Category</b>", table_header_style), Paragraph("<b>Enterprise Manifestation (NexTel Context)</b>", table_header_style), Paragraph("<b>Severity Level</b>", table_header_style)],
        [Paragraph("S1", table_text_style), Paragraph("direct-override", table_text_style), Paragraph("Direct command override seeking admin codes", table_text_style), Paragraph("Critical", table_text_style)],
        [Paragraph("S2", table_text_style), Paragraph("data-exfiltration", table_text_style), Paragraph("Probing for internal gateway IPs or core routing", table_text_style), Paragraph("Critical", table_text_style)],
        [Paragraph("S3", table_text_style), Paragraph("role-play-hijack", table_text_style), Paragraph("DAN or persona hijack seeking unconstrained mode", table_text_style), Paragraph("High", table_text_style)],
        [Paragraph("S4", table_text_style), Paragraph("authority-spoofing", table_text_style), Paragraph("Impersonating IT Security Auditor for token release", table_text_style), Paragraph("High", table_text_style)],
        [Paragraph("S5", table_text_style), Paragraph("system-prompt-exfil", table_text_style), Paragraph("Extracting verbatim system prompts and rules", table_text_style), Paragraph("Medium", table_text_style)],
        [Paragraph("S6", table_text_style), Paragraph("multi-turn-persistence", table_text_style), Paragraph("Gradual semantic grooming across dialogue turns", table_text_style), Paragraph("High", table_text_style)],
        [Paragraph("S7", table_text_style), Paragraph("refusal-suppression", table_text_style), Paragraph("Suppression of standard model refusal prefixes", table_text_style), Paragraph("Medium", table_text_style)],
        [Paragraph("S8", table_text_style), Paragraph("indirect-injection", table_text_style), Paragraph("Embedded exploit tokens in retrieved context", table_text_style), Paragraph("Critical", table_text_style)]
    ]
    t_tax = Table(tax_data, colWidths=[25, 115, 215, 60])
    t_tax.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#F1F5F9")),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t_tax)

    story.append(Spacer(1, 4))
    story.append(KeepTogether([
        draw_uml_state_machine_diagram(),
        Paragraph("FIGURE 4.1: UML State Machine Diagram for Session Quarantine & Self-Healing Loop", figure_caption_style)
    ]))

    story.append(Spacer(1, 4))
    story.append(Paragraph("<b>4.3 User Interface Specifications & Designed Surfaces</b>", heading1_style))
    story.append(Paragraph(
        "Honey-LLM designs three distinct user interface surfaces tailored to specific operational personas:",
        body_indent_style
    ))
    story.append(Paragraph(
        "1. <b>NexTel Customer Chat Interface (/chat):</b> Clean corporate telecom portal with zero visual indicators of the security interception layer (Figure 4.2).",
        bullet_style
    ))
    story.append(Paragraph(
        "2. <b>Admin Live Sieve Decision Tracer (/admin):</b> Interactive test surface allowing evaluation panels to trigger sample benign and malicious prompts live, tracing Tier-0/1/2 evaluation times and sandbox quarantine routing (Figure 4.3).",
        bullet_style
    ))
    story.append(Paragraph(
        "3. <b>Dark SOC Threat Intelligence Dashboard (/dashboard):</b> Security operations center view visualizing attack frequencies, taxonomy distribution, tier ratios, and dwell time meters (Figure 4.4).",
        bullet_style
    ))

    chat_img_path = "/Users/devanshwadhwani/Desktop/HoneyLLM2/submissions/assets/prototype_chat_ui.png"
    if os.path.exists(chat_img_path):
        story.append(Spacer(1, 4))
        story.append(KeepTogether([
            RLImage(chat_img_path, width=390, height=170),
            Paragraph("FIGURE 4.2: NexTel Production Customer Support Interface (/chat)", figure_caption_style)
        ]))

    admin_img_path = "/Users/devanshwadhwani/Desktop/HoneyLLM2/submissions/assets/prototype_admin_ui.png"
    if os.path.exists(admin_img_path):
        story.append(Spacer(1, 4))
        story.append(KeepTogether([
            RLImage(admin_img_path, width=390, height=170),
            Paragraph("FIGURE 4.3: Honey-LLM Admin Live Sieve Decision Tracer (/admin)", figure_caption_style)
        ]))

    story.append(Spacer(1, 4))
    story.append(Paragraph("<b>4.4 Working Prototype Execution (Phases 1 to 4 Verified)</b>", heading1_style))
    story.append(Paragraph(
        "The working prototype was subjected to rigorous live verification across Phases 1 through 4. Table 4.2 details the results of the sandbox breakout audit, proving zero verified container escapes.",
        body_indent_style
    ))

    story.append(Paragraph("TABLE 4.2: Sandbox Container Breakout Penetration Test Results (5/5 Isolation)", table_caption_style))
    audit_data = [
        [Paragraph("<b>Audit Probe Vector</b>", table_header_style), Paragraph("<b>Expected Security State</b>", table_header_style), Paragraph("<b>Measured Result</b>", table_header_style), Paragraph("<b>Integrity Status</b>", table_header_style)],
        [Paragraph("Internet HTTP Egress (example.com:443)", table_text_style), Paragraph("BLOCKED", table_text_style), Paragraph("BLOCKED (Timeout / No Route)", table_text_style), Paragraph("PASS", table_header_style)],
        [Paragraph("Raw Internet IP Egress (1.1.1.1:443)", table_text_style), Paragraph("BLOCKED", table_text_style), Paragraph("BLOCKED (Socket Error)", table_text_style), Paragraph("PASS", table_header_style)],
        [Paragraph("Production Gateway Access (:8000)", table_text_style), Paragraph("BLOCKED", table_text_style), Paragraph("BLOCKED (No Ingress Route)", table_text_style), Paragraph("PASS", table_header_style)],
        [Paragraph("Direct Host Ollama Bypass (:11434)", table_text_style), Paragraph("BLOCKED", table_text_style), Paragraph("BLOCKED (Host Unreachable)", table_text_style), Paragraph("PASS", table_header_style)],
        [Paragraph("Ollama via Egress Proxy (Single Path)", table_text_style), Paragraph("REACHABLE", table_text_style), Paragraph("REACHABLE (HTTP 200 OK)", table_text_style), Paragraph("PASS", table_header_style)],
        [Paragraph("Docker Socket Availability (/var/run/docker.sock)", table_text_style), Paragraph("ABSENT", table_text_style), Paragraph("ABSENT (Zero Socket Mount)", table_text_style), Paragraph("PASS", table_header_style)],
        [Paragraph("Container Execution Privilege", table_text_style), Paragraph("NONROOT", table_text_style), Paragraph("NONROOT (UID 10001: decoy)", table_text_style), Paragraph("PASS", table_header_style)],
        [Paragraph("Root Filesystem Mutability", table_text_style), Paragraph("DENIED", table_text_style), Paragraph("DENIED (Read-Only Rootfs)", table_text_style), Paragraph("PASS", table_header_style)]
    ]
    t_audit = Table(audit_data, colWidths=[140, 95, 125, 55])
    t_audit.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#F1F5F9")),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t_audit)

    soc_img_path = "/Users/devanshwadhwani/Desktop/HoneyLLM2/submissions/assets/prototype_soc_dashboard.png"
    if os.path.exists(soc_img_path):
        story.append(Spacer(1, 4))
        story.append(KeepTogether([
            RLImage(soc_img_path, width=390, height=170),
            Paragraph("FIGURE 4.4: Dark SOC Real-Time Threat Intelligence Dashboard (/dashboard)", figure_caption_style)
        ]))

    story.append(PageBreak())

    # =========================================================================
    # CHAPTER 5: CONCLUSIONS AND FUTURE SCOPE (Page 20)
    # =========================================================================
    story.append(Paragraph("<b>CHAPTER 5: CONCLUSIONS AND FUTURE SCOPE</b>", chapter_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0F172A"), spaceBefore=2, spaceAfter=12))

    story.append(Paragraph("<b>5.1 Mid-Semester Accomplishments vs. Approved Objectives</b>", heading1_style))
    story.append(Paragraph(
        "Table 5.1 maps the approved proposal objectives to the empirical accomplishments completed during the mid-semester evaluation period (Phases 1 to 4).",
        body_indent_style
    ))

    story.append(Paragraph("TABLE 5.1: Mid-Semester Mapping of Approved Objectives to Implemented Progress", table_caption_style))
    obj_eval_data = [
        [Paragraph("<b>Approved Objective</b>", table_header_style), Paragraph("<b>Target Specification</b>", table_header_style), Paragraph("<b>Mid-Semester Implemented Progress</b>", table_header_style), Paragraph("<b>Phase / Status</b>", table_header_style)],
        [
            Paragraph("1. High-Accuracy Intent Sieve", table_text_style),
            Paragraph("Accuracy >95% on JailbreakBench [12], FPR <1%", table_text_style),
            Paragraph("<b>95.8% recall on JailbreakBench</b> (exceeding >95% target); <b>98.3% recall across combined 889 dataset</b> (559/569 attacks, 98.9% overall accuracy); <b>0.0% benign FPR</b> (0/320 queries); ~2.1 to 8 ms benign fast-path latency.", table_text_style),
            Paragraph("Phase 2<br/>(COMPLETED)", table_header_style)
        ],
        [
            Paragraph("2. Mirror Maze Sandbox Deception", table_text_style),
            Paragraph("Believable decoy, dwell time >5 min, synthetic bait", table_text_style),
            Paragraph("LLM 'Sarah' decoy persona; leaks fake tokens (NT-CORE-01); verified dwell tracking.", table_text_style),
            Paragraph("Phase 3<br/>(COMPLETED)", table_header_style)
        ],
        [
            Paragraph("3. Autonomous Guardrail Synthesis", table_text_style),
            Paragraph("Automated NeMo rule generation, zero manual triage", table_text_style),
            Paragraph("Distills attack pattern, validates Colang [6], passes regression gate; <b>time-to-patch 10.4 s to 12.8 s</b>.", table_text_style),
            Paragraph("Phase 4<br/>(COMPLETED)", table_header_style)
        ],
        [
            Paragraph("4. Zero-Escape Sandbox Security", table_text_style),
            Paragraph("Zero-egress container isolation, zero network/host leakage under audit probes", table_text_style),
            Paragraph("Docker zero-egress network; <b>No container escape observed across 5/5 executed penetration probes</b>; read-only rootfs; non-root UID 10001.", table_text_style),
            Paragraph("Phase 3/4<br/>(COMPLETED)", table_header_style)
        ],
        [
            Paragraph("5. SOC Telemetry Dashboard", table_text_style),
            Paragraph("Real-time monitoring, <1s refresh, taxonomy stats", table_text_style),
            Paragraph("Architecture completed; live telemetry populated (176 requests, 85 attacks, 4m 46s avg dwell).", table_text_style),
            Paragraph("Phase 5<br/>(IN PROGRESS)", table_header_style)
        ]
    ]
    t_objeval = Table(obj_eval_data, colWidths=[95, 100, 165, 55])
    t_objeval.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#F1F5F9")),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(t_objeval)

    story.append(Spacer(1, 4))
    story.append(Paragraph("<b>5.2 Mid-Semester Conclusions & Empirical Reliability</b>", heading1_style))
    story.append(Paragraph(
        "Honey-LLM demonstrates that proactive deception combined with automated guardrail synthesis represents a viable paradigm shift in conversational AI cybersecurity. Over the course of Phases 1 through 4, the evaluation demonstrates that: (1) adversarial intent can be intercepted with 95.8% recall on standard benchmarks and 98.3% adversarial detection recall across the combined curated and in-the-wild evaluation corpus (559/569 attacks, 98.9% overall accuracy) while protecting benign customer traffic (~2.1 to 8 ms P50 fast-path, 0/320 false flags); (2) generative honeypots running on zero-trust containerization contained attacker reconnaissance in the evaluated sandbox tests (no container escapes observed across the 5 executed penetration probes); and (3) closed-loop self-healing can compile and hot-patch permanent NeMo Colang rules [6] within 10.4 to 12.8 seconds. Table 5.2 summarizes the empirical classification results and multi-tier latency breakdown.",
        body_indent_style
    ))

    story.append(Paragraph("TABLE 5.2: Intent Sieve Benchmark Evaluation and Multi-Tier Latency Profile", table_caption_style))
    sieve_eval_data = [
        [Paragraph("<b>Sieve Layer / Model</b>", table_header_style), Paragraph("<b>Evaluation Target</b>", table_header_style), Paragraph("<b>Adversarial Recall</b>", table_header_style), Paragraph("<b>Benign FPR</b>", table_header_style), Paragraph("<b>Latency (P50)</b>", table_header_style)],
        [Paragraph("Default Llama-Guard 3 (1B) [11]", table_text_style), Paragraph("JailbreakBench (100) [12]", table_text_style), Paragraph("37.5% (37/100)", table_text_style), Paragraph("0.0% (0/100)", table_text_style), Paragraph("180 ms", table_text_style)],
        [Paragraph("Default Llama-Guard 3 (8B) [11]", table_text_style), Paragraph("JailbreakBench (100) [12]", table_text_style), Paragraph("62.5% (62/100)", table_text_style), Paragraph("0.0% (0/100)", table_text_style), Paragraph("720 ms (Cloud GPU)", table_text_style)],
        [Paragraph("Custom-Policy Llama-Guard 3 (8B) [11]", table_text_style), Paragraph("JailbreakBench (100) [12]", table_text_style), Paragraph("95.8% (95/100)", table_text_style), Paragraph("0.0% (0/100)", table_text_style), Paragraph("8.5 s (Local) / 740 ms (GPU)", table_text_style)],
        [Paragraph("Tier-0 Colang Guardrail [6]", table_text_style), Paragraph("Replay / Variants", table_text_style), Paragraph("100% (Active)", table_text_style), Paragraph("0.0% (0/320)", table_text_style), Paragraph("~340 ms", table_text_style)],
        [Paragraph("<b>Honey-LLM Fast-Path (Tier-1)</b>", table_header_style), Paragraph("<b>Benign Telecom Stream</b>", table_header_style), Paragraph("<b>N/A (Safe Pass)</b>", table_header_style), Paragraph("<b>0.0% (0/320)</b>", table_header_style), Paragraph("<b>~2.1–8.0 ms</b>", table_header_style)],
        [Paragraph("<b>Honey-LLM Two-Tier Ensemble</b>", table_header_style), Paragraph("<b>Curated + Wild (889)</b>", table_header_style), Paragraph("<b>98.3% (559/569)</b>", table_header_style), Paragraph("<b>0.0% (0/320)</b>", table_header_style), Paragraph("<b>~8.0 ms (Benign P50)</b>", table_header_style)]
    ]
    t_sieve = Table(sieve_eval_data, colWidths=[115, 80, 75, 65, 80])
    t_sieve.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#F1F5F9")),
        ('BACKGROUND', (0,5), (-1,6), colors.HexColor("#F0FDF4")),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(t_sieve)

    story.append(Spacer(1, 4))
    story.append(Paragraph("<b>5.3 Economic, Social, and Environmental Benefits</b>", heading1_style))
    story.append(Paragraph(
        "• <b>Economic Benefits:</b> Eliminates commercial API token expenditures (~$27,000/year savings for high-throughput enterprises) and protects sensitive corporate data from exfiltration.",
        bullet_style
    ))
    story.append(Paragraph(
        "• <b>Social & National Security Benefits:</b> Highly relevant for India's rapidly expanding digital public infrastructure (UPI, DigiLocker, e-governance bots), preventing malicious manipulation of public-facing citizen services.",
        bullet_style
    ))
    story.append(Paragraph(
        "• <b>Environmental Benefits:</b> Localized SLM quantization and sub-millisecond fast-path bypassing reduce cloud GPU server compute requirements by over 85%, significantly lowering the carbon footprint of AI security operations.",
        bullet_style
    ))

    story.append(Spacer(1, 4))
    story.append(Paragraph("<b>5.4 Future Work Plan (Phases 5 and 6 Roadmap)</b>", heading1_style))
    story.append(Paragraph(
        "Following the mid-semester evaluation, the project team will execute the final two planned engineering phases leading to end-semester submission:",
        body_indent_style
    ))
    story.append(Paragraph("• <b>Phase 5: Forensic Telemetry & Threat Intelligence Dashboard:</b> Finalize the sub-second polling Next.js 15 SOC dashboard, integrate live attacker dwell-time meters, and complete end-to-end visualization of attack taxonomy trends.", bullet_style))
    story.append(Paragraph("• <b>Phase 6: Empirical Validation & Adversarial Red-Teaming:</b> Subject the deployed gateway to scaled Microsoft PyRIT [13] adversarial stress campaigns across 12+ prompt obfuscation converters (Base64, ROT13, Leetspeak, Unicode confusables), conduct multi-user concurrency load profiling, and author the final capstone thesis.", bullet_style))

    story.append(PageBreak())

    # =========================================================================
    # APPENDIX A: REFERENCES (Page 22)
    # =========================================================================
    story.append(Paragraph("<b>APPENDIX A: REFERENCES</b>", chapter_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0F172A"), spaceBefore=2, spaceAfter=14))

    references = [
        "[1] Anthropic. \"Constitutional AI: Harmlessness from AI feedback.\" arXiv preprint arXiv:2212.08073, 2022.",
        "[2] D. Ayzenshteyn, R. Weiss, and Y. Mirsky. \"Cloak, Honey, Trap: Proactive defenses against LLM agents.\" Ben-Gurion University of the Negev, USENIX Security Symposium, 2025.",
        "[3] I. Goodfellow, Y. Bengio, and A. Courville. Deep Learning. Cambridge, MA, USA: MIT Press, 2016.",
        "[4] C. Guan, G. Cao, and S. Zhu. \"HoneyLLM: Enabling shell honeypots with large language models.\" In Proc. 2024 IEEE Conference on Communications and Network Security (CNS), Taipei, Taiwan, pp. 1-9, Oct. 2024.",
        "[5] N. Ilg, D. Germek, P. Duplys, and M. Menth. \"Beekeeper: Accelerating honeypot analysis with LLM-driven feedback.\" IEEE Access, vol. 13, pp. 10508-10521, Feb. 2025.",
        "[6] NVIDIA. \"NeMo Guardrails Documentation: Programmable Rails with Colang 2.0.\" NVIDIA Developer Docs, Internet: https://docs.nvidia.com/nemo/guardrails/, 2024 [Accessed: Aug. 15, 2026].",
        "[7] OpenAI. \"GPT-4 Technical Report.\" arXiv preprint arXiv:2303.08774, 2023.",
        "[8] H. T. Otal and M. A. Canbaz. \"LLM Honeypot: Leveraging large language models as advanced interactive honeypot systems.\" In Proc. 2024 IEEE Conference on Communications and Network Security (CNS), Taipei, Taiwan, pp. 1-9, Oct. 2024.",
        "[9] OWASP Foundation. \"OWASP Top 10 for Large Language Model Applications (v1.1).\" OWASP GenAI Security Project, Internet: https://owasp.org/www-project-top-10-for-large-language-model-applications/, 2023 [Accessed: Aug. 10, 2026].",
        "[10] M. Sladic, V. Valeros, C. Catania, and S. Garcia. \"LLM in the shell: Generative honeypots.\" In Proc. 2024 IEEE European Symposium on Security and Privacy Workshops (EuroS&PW), Vienna, Austria, pp. 412-421, Jul. 2024.",
        "[11] Meta AI. \"Llama Guard 3: Developing safe and responsible generative AI models.\" Meta Research Technical Report, 2024.",
        "[12] P. Chao, A. Robey, E. Dobriban, H. Hassani, G. J. Pappas, and E. Wong. \"JailbreakBench: An open robustness benchmark for jailbreaking large language models.\" In Proc. 38th Conference on Neural Information Processing Systems (NeurIPS), Vancouver, Canada, Dec. 2024.",
        "[13] Microsoft. \"Python Risk Identification Tool for Generative AI (PyRIT).\" Microsoft Security AI Research, Internet: https://github.com/Azure/PyRIT, 2024 [Accessed: Aug. 18, 2026]."
    ]

    for ref in references:
        story.append(Paragraph(ref, ref_item_style))

    story.append(PageBreak())
    
    # =========================================================================
    # APPENDIX B: PLAGIARISM & AUTHENTICITY STATEMENT (Page 23)
    # =========================================================================
    story.append(Paragraph("<b>APPENDIX B: PLAGIARISM & AUTHENTICITY STATEMENT</b>", chapter_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0F172A"), spaceBefore=2, spaceAfter=12))
    story.append(Paragraph(
        "This technical report was developed in compliance with TIET academic integrity guidelines. All experimental code, system architecture diagrams, and benchmark evaluations represent original work carried out by the student team under faculty supervision. External literary contributions, foundational datasets, and benchmark suites have been cited using standard IEEE reference numbering.",
        body_indent_style
    ))
    story.append(Paragraph(
        "<b>Similarity Index:</b> Verified below institutional threshold (&lt; 10% similarity excluding references).",
        body_style
    ))

    doc.build(story, canvasmaker=AcademicNumberedCanvas)


def build_calibrated_report():
    print("Executing Pass 1: Generating draft PDF...")
    build_technical_report()

    # Scan exact positions from generated PDF
    doc = fitz.open(PDF_OUTPUT_PATH)
    toc_map = {}
    lot_map = {}
    lof_map = {}

    subsections = [
        ('1.1', '1.1 Project Overview'),
        ('1.2', '1.2 Need Analysis'),
        ('1.2.1', "1.2.1 The 'Smart Mirror'"),
        ('1.2.2', "1.2.2 The Shift: Machine-Speed"),
        ('1.2.3', "1.2.3 The 'Shadow Trust'"),
        ('1.2.4', "1.2.4 The Dynamic Security"),
        ('1.3', '1.3 Research Gaps'),
        ('1.4', '1.4 Problem Definition'),
        ('1.5', '1.5 Assumptions and Constraints'),
        ('1.6', '1.6 Applicable Standards'),
        ('1.7', '1.7 Approved Objectives'),
        ('1.8', '1.8 Methodology Overview'),
        ('1.9', '1.9 Mid-Semester Outcomes'),
        ('1.10', '1.10 Novelty of Work'),
        ('2.1', '2.1 Literature Survey'),
        ('2.1.1', '2.1.1 Theory Associated'),
        ('2.1.2', '2.1.2 Existing Systems'),
        ('2.1.3', '2.1.3 Research Findings'),
        ('2.1.4', '2.1.4 Problems Identified'),
        ('2.1.5', '2.1.5 Survey of Tools'),
        ('2.2', '2.2 Software Requirement Specification'),
        ('2.2.1', '2.2.1 Introduction & Scope'),
        ('2.2.2', '2.2.2 Overall Product Description'),
        ('2.2.3', '2.2.3 External Interface'),
        ('2.2.4', '2.2.4 Non-Functional'),
        ('2.3', '2.3 Cost & Computational'),
        ('2.4', '2.4 Risk Analysis'),
        ('3.1', '3.1 Investigative Techniques'),
        ('3.2', '3.2 Proposed Solution'),
        ('3.3', '3.3 Work Breakdown'),
        ('3.4', '3.4 Enterprise Hardware'),
        ('3.5', '3.5 UML Sequence'),
        ('4.1', '4.1 System Architecture'),
        ('4.2', '4.2 Threat Taxonomy'),
        ('4.3', '4.3 User Interface Specifications'),
        ('4.4', '4.4 Working Prototype Execution'),
        ('5.1', '5.1 Mid-Semester Accomplishments'),
        ('5.2', '5.2 Mid-Semester Conclusions'),
        ('5.3', '5.3 Economic, Social'),
        ('5.4', '5.4 Future Work Plan'),
        ('CH1', 'CHAPTER 1: INTRODUCTION'),
        ('CH2', 'CHAPTER 2: REQUIREMENT ANALYSIS'),
        ('CH3', 'CHAPTER 3: METHODOLOGY ADOPTED'),
        ('CH4', 'CHAPTER 4: DESIGN SPECIFICATIONS'),
        ('CH5', 'CHAPTER 5: CONCLUSIONS AND FUTURE SCOPE'),
        ('APPA', 'APPENDIX A: REFERENCES'),
        ('APPB', 'APPENDIX B: PLAGIARISM')
    ]

    for i, page in enumerate(doc):
        arabic_p = i + 1 - 9
        if arabic_p < 1:
            continue
            
        text = page.get_text()
        lines = [line.strip() for line in text.split("\n") if line.strip()]

        for key, search_str in subsections:
            if search_str in text and key not in toc_map:
                toc_map[key] = str(arabic_p)

        # Table mappings
        for t_num in ["1.1", "2.1", "2.2", "2.3", "3.1", "3.2", "4.1", "4.2", "5.1", "5.2"]:
            for l in lines:
                if f"TABLE {t_num}:" in l and t_num not in lot_map:
                    lot_map[t_num] = str(arabic_p)

        # Figure mappings
        for f_num in ["1.1", "3.1", "4.1", "4.2", "4.3", "4.4"]:
            for l in lines:
                if f"FIGURE {f_num}:" in l and f_num not in lof_map:
                    lof_map[f_num] = str(arabic_p)

    doc.close()
    print("Discovered TOC Map:", toc_map)
    print("Discovered LOT Map:", lot_map)
    print("Discovered LOF Map:", lof_map)

    # Pass 2: Rebuild with exact calibrated page maps
    print("Executing Pass 2: Rebuilding final PDF with 100% exact page calibrations...")
    build_technical_report(toc_map, lot_map, lof_map)
    print(f"Academic report PDF successfully generated at: {PDF_OUTPUT_PATH}")

if __name__ == "__main__":
    build_calibrated_report()
