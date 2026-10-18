"""
Automated Test Suite: Document Parsing, Extraction & Privacy
Verifies PDF, DOCX, TXT, Excel intake, entity extraction, duplicate identification,
and privacy PII masking.
"""

import os
import pytest
from datetime import date
from docx import Document
import pandas as pd
import pymupdf as fitz
from backend.services.document_parser import (
    parse_pdf,
    parse_docx,
    parse_txt,
    parse_tabular,
    extract_fields_from_text,
    mask_applicant_name,
    mask_contact
)

@pytest.fixture
def sample_files(tmp_path):
    # 1. Text file
    txt_file = tmp_path / "grievance_sample.txt"
    txt_content = (
        "CPGRAMS Public Grievance Registration\n"
        "Registration No: MEITY/E/2026/0009988\n"
        "Date of Receipt: 15/10/2026\n"
        "Complainant: Rajesh Kumar Sharma\n"
        "Contact: rajesh.sharma@example.com | 9876543210\n"
        "Subject: Delay in approving GPU voucher application under IndiaAI Mission\n"
        "Grievance Detail: We applied for compute credits 30 days ago. No approval has been granted.\n"
        "Relief Sought: Kindly expedite technical approval and release 32 GPU cluster allocation."
    )
    txt_file.write_text(txt_content, encoding="utf-8")

    # 2. DOCX file
    docx_file = tmp_path / "grievance_sample.docx"
    doc = Document()
    doc.add_heading("Grievance Petition to MeitY", 0)
    doc.add_paragraph("Registration No: MEITY/E/2026/0007744")
    doc.add_paragraph("Applicant Name: Sneha Patel")
    doc.add_paragraph("Subject: Deepfake video takedown request under IT Rules")
    doc.add_paragraph("Grievance Detail: A manipulated deepfake video was uploaded on online platform.")
    doc.add_paragraph("Relief Sought: Direct the intermediary to remove the content within 24 hours.")
    doc.save(str(docx_file))

    # 3. PDF file
    pdf_file = tmp_path / "grievance_sample.pdf"
    pdf_doc = fitz.open()
    page = pdf_doc.new_page()
    page.insert_text((50, 50), "Registration No: MEITY/E/2026/0005522\nComplainant: Amit Verma\nSubject: DPDP Act Compliance query regarding AI model training data.\nRelief Sought: Clarification on consent exemptions.")
    pdf_doc.save(str(pdf_file))
    pdf_doc.close()

    # 4. Excel file
    excel_file = tmp_path / "grievance_batch.xlsx"
    df = pd.DataFrame([
        {
            "Registration Number": "MEITY/E/2026/0001111",
            "Subject": "Batch Grievance 1 on AI Ethics",
            "Applicant Name": "Vikram Singh",
            "Date Received": "2026-10-10",
            "Category": "AI Safety & Ethics",
            "Grievance Details": "Algorithm bias concern in financial scoring system.",
            "Relief Sought": "Guidelines on algorithmic audits.",
            "Status": "New"
        },
        {
            "Registration Number": "MEITY/E/2026/0002222",
            "Subject": "Batch Grievance 2 on Startup Incubation",
            "Applicant Name": "Pooja Nair",
            "Date Received": "2026-10-12",
            "Category": "Startups & R&D Innovation",
            "Grievance Details": "Status of CDAC AI incubation application.",
            "Relief Sought": "Expedited result announcement.",
            "Status": "New"
        }
    ])
    df.to_excel(str(excel_file), index=False)

    return {
        "txt": str(txt_file),
        "docx": str(docx_file),
        "pdf": str(pdf_file),
        "excel": str(excel_file)
    }

def test_parse_txt(sample_files):
    parsed = parse_txt(sample_files["txt"])
    assert "MEITY/E/2026/0009988" in parsed["text"]
    extracted = extract_fields_from_text(parsed["text"])
    assert extracted["registration_no"] == "MEITY/E/2026/0009988"
    assert extracted["applicant_name"] == "Rajesh Kumar Sharma"
    assert "IndiaAI Mission" in extracted["category"]

def test_parse_docx(sample_files):
    parsed = parse_docx(sample_files["docx"])
    assert "MEITY/E/2026/0007744" in parsed["text"]
    extracted = extract_fields_from_text(parsed["text"])
    assert extracted["registration_no"] == "MEITY/E/2026/0007744"
    assert extracted["applicant_name"] == "Sneha Patel"
    assert "Deepfake" in extracted["category"]

def test_parse_pdf(sample_files):
    parsed = parse_pdf(sample_files["pdf"])
    assert "MEITY/E/2026/0005522" in parsed["text"]
    assert parsed["is_scanned"] is False
    extracted = extract_fields_from_text(parsed["text"])
    assert extracted["registration_no"] == "MEITY/E/2026/0005522"

def test_parse_excel_batch(sample_files):
    records = parse_tabular(sample_files["excel"])
    assert len(records) == 2
    assert records[0]["registration_no"] == "MEITY/E/2026/0001111"
    assert records[1]["registration_no"] == "MEITY/E/2026/0002222"

def test_pii_masking():
    # Names
    assert mask_applicant_name("Rajesh Kumar Sharma") == "R**** S****"
    assert mask_applicant_name("Anjali") == "A*****"
    assert mask_applicant_name(None) == "Unknown Citizen"

    # Contacts
    contact = "reach me at applicant@example.com or 9876543210"
    masked = mask_contact(contact)
    assert "applicant@example.com" not in masked
    assert "a***@example.com" in masked
    assert "9876543210" not in masked
    assert "******3210" in masked
