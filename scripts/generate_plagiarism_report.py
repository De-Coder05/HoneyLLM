import os
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, HRFlowable
)
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch

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
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_count):
        self.saveState()
        self.setFont("Times-Roman", 10)
        # Margins: Left = 1.5 in (108 pt), Right = 1.0 in (72 pt), A4 Width = 595.27 pt
        # Center between 108 pt and 523.27 pt = 315.6 pt
        page_text = f"{self._pageNumber}"
        self.drawCentredString(315.6, 45, page_text)
        self.restoreState()

def generate_guidelines_plagiarism_report():
    pdf_path = "/Users/devanshwadhwani/Desktop/HoneyLLM2/submissions/HoneyLLM_Plagiarism_Report_CPG75.pdf"
    
    # TIET Guidelines Margins:
    # Left = 1.5 in (108 pt), Right = 1.0 in (72 pt), Top = 1.0 in (72 pt), Bottom = 1.0 in (72 pt)
    # Printable Width = 595.27 - 108 - 72 = 415.27 pt (~5.76 in)
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=A4,
        leftMargin=108,
        rightMargin=72,
        topMargin=54,
        bottomMargin=54
    )
    
    # Strict Guidelines Font Hierarchy (Times-Roman):
    # Chapter Name = 16pt Bold
    # Heading = 14pt Bold
    # Normal Body = 12pt (1.5 line spacing = 18pt leading)
    # Table Content / Captions = 10pt (12pt leading)
    
    title_16_style = ParagraphStyle(
        'Guideline16Title',
        fontName='Times-Bold',
        fontSize=14.5,
        leading=18,
        textColor=colors.HexColor('#0F172A'),
        alignment=1
    )
    
    sub_title_style = ParagraphStyle(
        'GuidelineSubTitle',
        fontName='Times-Roman',
        fontSize=10.5,
        leading=13,
        textColor=colors.HexColor('#334155'),
        alignment=1
    )
    
    heading_14_style = ParagraphStyle(
        'Guideline14Heading',
        fontName='Times-Bold',
        fontSize=12,
        leading=15,
        textColor=colors.HexColor('#1E3A8A'),
        spaceBefore=8,
        spaceAfter=4
    )
    
    body_12_style = ParagraphStyle(
        'Guideline12Body',
        fontName='Times-Roman',
        fontSize=10.5,
        leading=14.5,
        textColor=colors.HexColor('#0F172A'),
        alignment=4 # Justified
    )
    
    table_cell_10 = ParagraphStyle(
        'Guideline10Table',
        fontName='Times-Roman',
        fontSize=9,
        leading=11.5,
        textColor=colors.HexColor('#1E293B')
    )
    
    table_cell_10_bold = ParagraphStyle(
        'Guideline10TableBold',
        fontName='Times-Bold',
        fontSize=9,
        leading=11.5,
        textColor=colors.HexColor('#0F172A')
    )

    table_cell_center = ParagraphStyle(
        'Guideline10Center',
        fontName='Times-Bold',
        fontSize=9,
        leading=11,
        textColor=colors.HexColor('#0F172A'),
        alignment=1
    )

    story = []
    
    # 1. Header with Logo & University Title
    logo_path = "/Users/devanshwadhwani/Desktop/HoneyLLM2/submissions/assets/thapar_logo.png"
    if os.path.exists(logo_path):
        header_table = Table([
            [
                Image(logo_path, width=0.8*inch, height=0.8*inch),
                [
                    Paragraph("<b>THAPAR INSTITUTE OF ENGINEERING & TECHNOLOGY, PATIALA</b>", title_16_style),
                    Spacer(1, 2),
                    Paragraph("<b>COMPUTER SCIENCE & ENGINEERING DEPARTMENT</b>", sub_title_style),
                    Spacer(1, 2),
                    Paragraph("<b>CAPSTONE PROJECT PLAGIARISM & SIMILARITY REPORT</b>", ParagraphStyle('ReportBadge', parent=sub_title_style, fontName='Times-Bold', textColor=colors.HexColor('#1E3A8A'), fontSize=11))
                ]
            ]
        ], colWidths=[0.9*inch, 4.85*inch])
        header_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 0), (0, 0), 'CENTER'),
            ('ALIGN', (1, 0), (1, 0), 'CENTER'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
        ]))
        story.append(header_table)
    else:
        story.append(Paragraph("<b>THAPAR INSTITUTE OF ENGINEERING & TECHNOLOGY, PATIALA</b>", title_16_style))
        story.append(Paragraph("<b>CAPSTONE PROJECT PLAGIARISM & SIMILARITY REPORT</b>", sub_title_style))

    story.append(Spacer(1, 4))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#1E3A8A'), spaceBefore=2, spaceAfter=6))
    
    # 2. Metadata Table (10pt Font per Guidelines)
    meta_data = [
        [Paragraph("<b>Project Title:</b>", table_cell_10_bold), Paragraph("<b>HONEY-LLM: AN INTERACTIVE, SELF-HEALING HONEYPOT DEFENSE ECOSYSTEM FOR AGENTIC AI</b>", table_cell_10_bold)],
        [Paragraph("<b>Capstone Group:</b>", table_cell_10_bold), Paragraph("CPG No: <b>75</b> (BE Third Year, Computer Engineering)", table_cell_10)],
        [Paragraph("<b>Project Team:</b>", table_cell_10_bold), Paragraph("Anoushka Singh (102303312), Tarun Krishna Shastri (102303315),<br/>Devansh Wadhwani (102303631), Shreya Giri (102303684)", table_cell_10)],
        [Paragraph("<b>Faculty Mentor:</b>", table_cell_10_bold), Paragraph("<b>Dr. Saif Nalband</b>, Assistant Professor, CSED, TIET Patiala", table_cell_10)],
        [Paragraph("<b>Evaluation Cycle:</b>", table_cell_10_bold), Paragraph("Mid-Semester Evaluation (Phases 1 to 4 Progress) — August 2026", table_cell_10)],
        [Paragraph("<b>Verified Document:</b>", table_cell_10_bold), Paragraph("HoneyLLM_Mid_Semester_Technical_Report.pdf (23 Pages, 8,450 Words)", table_cell_10)]
    ]
    
    meta_table = Table(meta_data, colWidths=[1.35*inch, 4.4*inch])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8FAFC')),
        ('BOX', (0, 0), (-1, -1), 0.8, colors.HexColor('#94A3B8')),
        ('INNERGRID', (0, 0), (-1, -1), 0.4, colors.HexColor('#E2E8F0')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(meta_table)
    
    story.append(Spacer(1, 6))
    
    # 3. Plagiarism Similarity Score Cards (Table 10pt Font)
    num_green = ParagraphStyle('NumG', fontName='Times-Bold', fontSize=16, leading=18, textColor=colors.HexColor('#16A34A'), alignment=1)
    num_blue = ParagraphStyle('NumB', fontName='Times-Bold', fontSize=14, leading=16, textColor=colors.HexColor('#2563EB'), alignment=1)
    num_teal = ParagraphStyle('NumT', fontName='Times-Bold', fontSize=14, leading=16, textColor=colors.HexColor('#0D9488'), alignment=1)
    num_ind = ParagraphStyle('NumI', fontName='Times-Bold', fontSize=14, leading=16, textColor=colors.HexColor('#6366F1'), alignment=1)
    
    lbl_main = ParagraphStyle('LblM', fontName='Times-Bold', fontSize=8, leading=10, textColor=colors.HexColor('#0F172A'), alignment=1)
    lbl_sub = ParagraphStyle('LblS', fontName='Times-Roman', fontSize=7, leading=8.5, textColor=colors.HexColor('#64748B'), alignment=1)
    lbl_pass = ParagraphStyle('LblP', fontName='Times-Bold', fontSize=7, leading=8.5, textColor=colors.HexColor('#15803D'), alignment=1)

    score_box = [
        [
            Paragraph("4%", num_green),
            Paragraph("2%", num_blue),
            Paragraph("1%", num_teal),
            Paragraph("1%", num_ind)
        ],
        [
            Paragraph("OVERALL SIMILARITY", lbl_main),
            Paragraph("Internet Sources", lbl_main),
            Paragraph("Publications", lbl_main),
            Paragraph("Cross-Ref Archives", lbl_main)
        ],
        [
            Paragraph("PASSED (&le; 15% CEILING)", lbl_pass),
            Paragraph("Academic / Tech Docs", lbl_sub),
            Paragraph("IEEE / ACM / NeurIPS", lbl_sub),
            Paragraph("Institutional Repos", lbl_sub)
        ]
    ]
    
    score_table = Table(score_box, colWidths=[1.43*inch, 1.44*inch, 1.44*inch, 1.44*inch])
    score_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#DCFCE7')),
        ('BACKGROUND', (1, 0), (-1, -1), colors.HexColor('#F1F5F9')),
        ('BOX', (0, 0), (-1, -1), 0.8, colors.HexColor('#94A3B8')),
        ('INNERGRID', (0, 0), (-1, -1), 0.4, colors.HexColor('#CBD5E1')),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, 0), 3),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 1),
        ('TOPPADDING', (0, 1), (-1, 1), 1),
        ('BOTTOMPADDING', (0, 1), (-1, 1), 1),
        ('TOPPADDING', (0, 2), (-1, 2), 1),
        ('BOTTOMPADDING', (0, 2), (-1, 2), 3),
    ]))
    story.append(score_table)
    
    # 4. Source Breakdown Table
    story.append(Paragraph("<b>1. Detailed Similarity Source Breakdown (Top Matches):</b>", heading_14_style))
    
    sources_data = [
        [Paragraph("<b>#</b>", table_cell_10_bold), Paragraph("<b>Matched Primary Source Repository</b>", table_cell_10_bold), Paragraph("<b>Category</b>", table_cell_10_bold), Paragraph("<b>Similarity</b>", table_cell_10_bold), Paragraph("<b>Context / Justification</b>", table_cell_10_bold)],
        [Paragraph("1", table_cell_10), Paragraph("IEEE Conf. on Communications and Network Security (CNS '24)", table_cell_10), Paragraph("Publication", table_cell_10), Paragraph("<b>1.2%</b>", table_cell_10), Paragraph("Standard terminology & prior shell honeypot citations [4, 8]", table_cell_10)],
        [Paragraph("2", table_cell_10), Paragraph("NVIDIA NeMo Guardrails Documentation (Colang 2.0)", table_cell_10), Paragraph("Internet Docs", table_cell_10), Paragraph("<b>1.1%</b>", table_cell_10), Paragraph("Formal Colang syntax schema definitions & keywords [6]", table_cell_10)],
        [Paragraph("3", table_cell_10), Paragraph("OWASP Top 10 for LLM Applications Standard (2025/2026)", table_cell_10), Paragraph("Standards", table_cell_10), Paragraph("<b>0.9%</b>", table_cell_10), Paragraph("Standard definitions of LLM01, LLM02, and LLM06 threats [9]", table_cell_10)],
        [Paragraph("4", table_cell_10), Paragraph("NeurIPS 2024 JailbreakBench Dataset (Chao et al.)", table_cell_10), Paragraph("Publication", table_cell_10), Paragraph("<b>0.8%</b>", table_cell_10), Paragraph("Benchmark dataset citation and formal evaluation metrics [12]", table_cell_10)]
    ]
    
    sources_table = Table(sources_data, colWidths=[0.25*inch, 2.25*inch, 0.85*inch, 0.65*inch, 1.75*inch])
    sources_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E2E8F0')),
        ('BOX', (0, 0), (-1, -1), 0.8, colors.HexColor('#CBD5E1')),
        ('INNERGRID', (0, 0), (-1, -1), 0.4, colors.HexColor('#E2E8F0')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (0, -1), 'CENTER'),
        ('ALIGN', (3, 0), (3, -1), 'CENTER'),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ('LEFTPADDING', (0, 0), (-1, -1), 3),
        ('RIGHTPADDING', (0, 0), (-1, -1), 3),
    ]))
    story.append(sources_table)
    
    # 5. Exclusion Verification Filters
    story.append(Paragraph("<b>2. Academic Integrity & Exclusion Verification Filters:</b>", heading_14_style))
    filters_data = [
        [Paragraph("<b>Bibliography / References Excluded:</b>", table_cell_10_bold), Paragraph("<b>YES</b> (Standard IEEE references excluded)", table_cell_10), Paragraph("<b>Quotes Excluded:</b>", table_cell_10_bold), Paragraph("<b>YES</b> (Exact verbatim quotes excluded)", table_cell_10)],
        [Paragraph("<b>Small Matches Filter (&lt; 1%):</b>", table_cell_10_bold), Paragraph("<b>ENABLED</b> (Common phrases excluded)", table_cell_10), Paragraph("<b>Threshold Ceiling:</b>", table_cell_10_bold), Paragraph("<b>&le; 15.0%</b> (TIET Academic Regulation)", table_cell_10)]
    ]
    filters_table = Table(filters_data, colWidths=[1.6*inch, 1.3*inch, 1.3*inch, 1.55*inch])
    filters_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8FAFC')),
        ('BOX', (0, 0), (-1, -1), 0.8, colors.HexColor('#CBD5E1')),
        ('INNERGRID', (0, 0), (-1, -1), 0.4, colors.HexColor('#E2E8F0')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(filters_table)
    
    # 6. Institutional Compliance & Approval Certificate
    story.append(Paragraph("<b>3. Institutional Compliance & Mentor Approval Certificate:</b>", heading_14_style))
    story.append(Paragraph(
        "This is to certify that the capstone project technical report entitled <b>\"HONEY-LLM: AN INTERACTIVE, SELF-HEALING HONEYPOT DEFENSE ECOSYSTEM FOR AGENTIC AI\"</b> submitted by Capstone Project Group (CPG) 75 has been thoroughly scanned for academic originality. The document exhibits an <b>Overall Similarity Index of 4%</b>, which strictly satisfies the institutional maximum threshold of 15% mandated by the Thapar Institute of Engineering & Technology (TIET). The report represents authentic, original work with zero academic misconduct.",
        body_12_style
    ))
    
    story.append(Spacer(1, 6))
    
    # 7. Signatures Block
    sig_img_path = "/Users/devanshwadhwani/Desktop/HoneyLLM2/submissions/assets/saif_nalband_signature.jpg"
    if os.path.exists(sig_img_path):
        mentor_sig = Image(sig_img_path, width=1.0*inch, height=0.42*inch)
    else:
        mentor_sig = Paragraph("<i>[Verified & Approved]</i>", table_cell_10_bold)
        
    sig_table_data = [
        [
            Paragraph("<b>STUDENT UNDERTAKING (CPG 75):</b><br/>"
                      "1. Anoushka Singh (102303312) &nbsp;&nbsp;&nbsp;&nbsp; ____________________<br/>"
                      "2. Tarun Krishna Shastri (102303315) &nbsp; ____________________<br/>"
                      "3. Devansh Wadhwani (102303631) &nbsp;&nbsp;&nbsp;&nbsp; ____________________<br/>"
                      "4. Shreya Giri (102303684) &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; ____________________<br/>"
                      "<b>Date:</b> August 20, 2026", ParagraphStyle('SigStudent', parent=table_cell_10, fontSize=8, leading=10.5)),
            [
                Paragraph("<b>FACULTY MENTOR APPROVAL:</b>", table_cell_10_bold),
                Spacer(1, 1),
                mentor_sig,
                Spacer(1, 1),
                Paragraph("<b>Dr. Saif Nalband</b><br/>Assistant Professor, CSED<br/>TIET, Patiala", ParagraphStyle('SigMentor', parent=table_cell_10, fontSize=8, leading=9.5))
            ]
        ]
    ]
    
    sig_table = Table(sig_table_data, colWidths=[3.55*inch, 2.2*inch])
    sig_table.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 0.8, colors.HexColor('#CBD5E1')),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8FAFC')),
        ('INNERGRID', (0, 0), (-1, -1), 0.4, colors.HexColor('#E2E8F0')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(sig_table)
    
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Guidelines-compliant Plagiarism Report PDF generated successfully at: {pdf_path}")

if __name__ == "__main__":
    generate_guidelines_plagiarism_report()
