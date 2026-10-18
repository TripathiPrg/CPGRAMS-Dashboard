"""
Document Export Service
Generates official Government of India / MeitY formatted DOCX and TXT documents.
Strictly free of AI branding, metadata leaks, or extraneous commentary.
"""

import os
from pathlib import Path
from datetime import datetime
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.style import WD_STYLE_TYPE
from backend.config import EXPORTS_DIR

def export_reply_to_docx(
    registration_no: str,
    subject: str,
    reply_text: str,
    applicant_name: str = None,
    officer_title: str = "Public Grievance Officer\nAI & Emerging Technologies Division\nMinistry of Electronics & Information Technology",
    mask_pii: bool = False
) -> str:
    """
    Creates a formal .docx file formatted to Government of India correspondence standards.
    Returns the absolute path to the generated file.
    """
    doc = Document()

    # Set 1-inch margins
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.right_margin = Inches(1)

    # Header Paragraph: Government of India / MeitY
    header_para = doc.add_paragraph()
    header_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run1 = header_para.add_run("GOVERNMENT OF INDIA\n")
    run1.bold = True
    run1.font.name = "Arial"
    run1.font.size = Pt(12)

    run2 = header_para.add_run("MINISTRY OF ELECTRONICS AND INFORMATION TECHNOLOGY\n")
    run2.bold = True
    run2.font.name = "Arial"
    run2.font.size = Pt(11)

    run3 = header_para.add_run("AI & EMERGING TECHNOLOGIES DIVISION\n")
    run3.font.name = "Arial"
    run3.font.size = Pt(10)

    run4 = header_para.add_run("Electronics Niketan, 6, CGO Complex, Lodhi Road, New Delhi - 110003\n")
    run4.font.name = "Arial"
    run4.font.size = Pt(9)
    run4.font.color.rgb = RGBColor(100, 100, 100)

    # Dividing Line
    doc.add_paragraph("―" * 45).alignment = WD_ALIGN_PARAGRAPH.CENTER

    # Reference & Date Table/Block
    ref_para = doc.add_paragraph()
    ref_run = ref_para.add_run(f"CPGRAMS Registration No.: {registration_no}\n")
    ref_run.bold = True
    ref_run.font.name = "Arial"
    ref_run.font.size = Pt(10)
    
    date_run = ref_para.add_run(f"Date of Disposal/Issuance: {datetime.now().strftime('%d/%m/%Y')}\n")
    date_run.font.name = "Arial"
    date_run.font.size = Pt(10)

    # Applicant Name (with privacy option)
    app_display = "Citizen"
    if applicant_name:
        if mask_pii:
            parts = applicant_name.split()
            app_display = f"{parts[0][0]}****" if parts else "Citizen"
        else:
            app_display = applicant_name
    app_run = ref_para.add_run(f"Applicant: {app_display}\n")
    app_run.font.name = "Arial"
    app_run.font.size = Pt(10)

    # Subject
    sub_para = doc.add_paragraph()
    sub_run = sub_para.add_run(f"Subject: {subject}\n")
    sub_run.bold = True
    sub_run.font.name = "Arial"
    sub_run.font.size = Pt(10.5)

    doc.add_paragraph()  # Spacing

    # Reply Body Paragraphs
    clean_paragraphs = [p.strip() for p in reply_text.splitlines() if p.strip()]
    for p_text in clean_paragraphs:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        r = p.add_run(p_text)
        r.font.name = "Arial"
        r.font.size = Pt(10.5)
        p.paragraph_format.line_spacing = 1.15
        p.paragraph_format.space_after = Pt(6)

    doc.add_paragraph()  # Spacing

    # Official Sign-off Block (Right-aligned)
    sign_para = doc.add_paragraph()
    sign_para.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    sign_run = sign_para.add_run(f"\n\n\n(Signed)\n{officer_title}\nGovernment of India")
    sign_run.font.name = "Arial"
    sign_run.font.size = Pt(10)

    # Sanitize filename
    clean_reg = registration_no.replace("/", "_").replace("\\", "_")
    filename = f"CPGRAMS_Reply_{clean_reg}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"
    output_path = EXPORTS_DIR / filename
    doc.save(str(output_path))
    return str(output_path)

def export_reply_to_txt(
    registration_no: str,
    subject: str,
    reply_text: str
) -> str:
    """Exports reply as clean plain text."""
    clean_reg = registration_no.replace("/", "_").replace("\\", "_")
    filename = f"CPGRAMS_Reply_{clean_reg}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    output_path = EXPORTS_DIR / filename
    
    content = (
        f"CPGRAMS OFFICIAL REPLY\n"
        f"Registration No: {registration_no}\n"
        f"Date: {datetime.now().strftime('%d/%m/%Y')}\n"
        f"Subject: {subject}\n\n"
        f"{reply_text}\n\n"
        f"AI & Emerging Technologies Division\n"
        f"Ministry of Electronics and Information Technology (MeitY)\n"
    )
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)
    return str(output_path)
