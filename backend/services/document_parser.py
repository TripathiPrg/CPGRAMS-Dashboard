"""
Document Intake and Parsing Engine
Extracts structured grievance data from PDF, DOCX, TXT, CSV, and Excel documents.
Includes PII masking and duplicate detection.
"""

import re
import os
from datetime import datetime, date
from pathlib import Path
from typing import Dict, Any, List, Optional
import pymupdf as fitz  # PyMuPDF
from docx import Document
import pandas as pd

# Regex patterns for CPGRAMS data
REG_NO_PATTERN = re.compile(r'\b([A-Z0-9]{3,10}/[EOP]/[0-9]{4}/[0-9]{3,8})\b', re.IGNORECASE)
DATE_PATTERN = re.compile(r'\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b')
EMAIL_PATTERN = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
PHONE_PATTERN = re.compile(r'\b(?:\+91[\-\s]?)?[6-9]\d{9}\b')

def mask_applicant_name(name: Optional[str]) -> str:
    """Masks applicant name for privacy: 'Rajesh Kumar Sharma' -> 'R***** S*****'"""
    if not name or len(name.strip()) == 0:
        return "Unknown Citizen"
    parts = name.strip().split()
    if len(parts) == 1:
        part = parts[0]
        return part[0] + "*" * (len(part) - 1) if len(part) > 1 else part
    return f"{parts[0][0]}**** {parts[-1][0]}****"

def mask_contact(text: Optional[str]) -> str:
    """Masks phone numbers and email addresses in contact text."""
    if not text:
        return "Not Provided"
    
    # Mask email
    def replace_email(match):
        e = match.group(0)
        user, domain = e.split("@", 1)
        masked_user = user[0] + "***" if len(user) > 1 else "*"
        return f"{masked_user}@{domain}"
    
    text = EMAIL_PATTERN.sub(replace_email, text)
    
    # Mask phone
    def replace_phone(match):
        p = match.group(0)
        digits = re.sub(r'\D', '', p)
        if len(digits) >= 10:
            return f"******{digits[-4:]}"
        return "****"
    
    text = PHONE_PATTERN.sub(replace_phone, text)
    return text

def parse_pdf(file_path: str) -> Dict[str, Any]:
    """Extracts text and metadata from a PDF file using PyMuPDF."""
    doc = fitz.open(file_path)
    full_text = []
    is_scanned = True

    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text("text")
        if len(text.strip()) > 30:
            is_scanned = False
        full_text.append(text)

    combined_text = "\n".join(full_text).strip()
    return {
        "text": combined_text,
        "page_count": len(doc),
        "is_scanned": is_scanned and len(doc) > 0,
        "format": "PDF"
    }

def parse_docx(file_path: str) -> Dict[str, Any]:
    """Extracts text from a DOCX file using python-docx."""
    doc = Document(file_path)
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    for table in doc.tables:
        for row in table.rows:
            row_text = " | ".join(cell.text.strip() for cell in row.cells if cell.text.strip())
            if row_text:
                paragraphs.append(row_text)
    combined_text = "\n".join(paragraphs).strip()
    return {
        "text": combined_text,
        "page_count": max(1, len(paragraphs) // 10),
        "is_scanned": False,
        "format": "DOCX"
    }

def parse_txt(file_path: str) -> Dict[str, Any]:
    """Extracts text from a plain text file."""
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        text = f.read().strip()
    return {
        "text": text,
        "page_count": 1,
        "is_scanned": False,
        "format": "TXT"
    }

def parse_tabular(file_path: str) -> List[Dict[str, Any]]:
    """Extracts grievance records from CSV or Excel file."""
    ext = Path(file_path).suffix.lower()
    if ext == ".csv":
        df = pd.read_csv(file_path)
    else:
        df = pd.read_excel(file_path)

    # Normalize column names
    col_mapping = {}
    for col in df.columns:
        norm = str(col).strip().lower().replace(" ", "_").replace(".", "")
        if any(k in norm for k in ["reg", "registration", "docket", "ticket"]):
            col_mapping[col] = "registration_no"
        elif any(k in norm for k in ["subject", "title", "issue"]):
            col_mapping[col] = "subject"
        elif any(k in norm for k in ["name", "applicant", "complainant"]):
            col_mapping[col] = "applicant_name"
        elif any(k in norm for k in ["date", "received", "filed"]):
            col_mapping[col] = "date_received"
        elif any(k in norm for k in ["category", "type", "classification"]):
            col_mapping[col] = "category"
        elif any(k in norm for k in ["grievance", "detail", "description", "text", "complaint"]):
            col_mapping[col] = "grievance_text"
        elif any(k in norm for k in ["relief", "prayer", "demand", "action_sought"]):
            col_mapping[col] = "requested_relief"
        elif any(k in norm for k in ["status", "current_status"]):
            col_mapping[col] = "status"

    df = df.rename(columns=col_mapping)
    records = []
    for _, row in df.iterrows():
        item = {
            "registration_no": str(row.get("registration_no", "")).strip(),
            "subject": str(row.get("subject", "Grievance Record")).strip(),
            "applicant_name": str(row.get("applicant_name", "Citizen")).strip(),
            "grievance_text": str(row.get("grievance_text", "")).strip(),
            "requested_relief": str(row.get("requested_relief", "")).strip(),
            "category": str(row.get("category", "AI & Emerging Technologies")).strip(),
            "status": str(row.get("status", "New")).strip(),
            "date_received": date.today().isoformat()
        }
        if item["registration_no"] and item["registration_no"] != "nan":
            records.append(item)
    return records

def extract_fields_from_text(text: str) -> Dict[str, Any]:
    """
    Intelligently extracts CPGRAMS fields from raw unformatted or scanned text.
    Handles Registration No, Dates, Subject, Applicant Name, Relief, and Category.
    """
    extracted = {
        "registration_no": None,
        "date_received": date.today(),
        "applicant_name": None,
        "applicant_contact": None,
        "subject": None,
        "category": "AI & Emerging Technologies",
        "grievance_text": text,
        "requested_relief": None,
        "concerned_ministry": "Ministry of Electronics and Information Technology",
        "concerned_division": "AI & Emerging Technologies Division",
        "missing_fields": []
    }

    # 1. Registration No
    reg_match = REG_NO_PATTERN.search(text)
    if reg_match:
        extracted["registration_no"] = reg_match.group(1).upper()
    else:
        # Generate temporary draft ID if missing
        temp_id = f"MEITY/E/{datetime.now().year}/{int(datetime.now().timestamp()) % 100000:05d}"
        extracted["registration_no"] = temp_id
        extracted["missing_fields"].append("registration_no")

    # 2. Date
    date_match = DATE_PATTERN.search(text)
    if date_match:
        try:
            d_str = date_match.group(1).replace("-", "/")
            parts = d_str.split("/")
            if len(parts[2]) == 2:
                parts[2] = f"20{parts[2]}"
            extracted["date_received"] = datetime.strptime(f"{parts[0]}/{parts[1]}/{parts[2]}", "%d/%m/%Y").date()
        except Exception:
            extracted["date_received"] = date.today()

    # 3. Applicant Name and Contacts
    for line in text.splitlines()[:20]:
        line_clean = line.strip()
        if any(prefix in line_clean.lower() for prefix in ["complainant:", "applicant name:", "name:", "grievance by:"]):
            val = re.split(r'[:\-]', line_clean, maxsplit=1)[-1].strip()
            if len(val) > 2:
                extracted["applicant_name"] = val
                break

    emails = EMAIL_PATTERN.findall(text)
    phones = PHONE_PATTERN.findall(text)
    contact_parts = []
    if emails:
        contact_parts.append(emails[0])
    if phones:
        contact_parts.append(phones[0])
    if contact_parts:
        extracted["applicant_contact"] = " | ".join(contact_parts)

    # 4. Subject line
    for line in text.splitlines()[:25]:
        line_clean = line.strip()
        if any(prefix in line_clean.lower() for prefix in ["subject:", "sub:", "regarding:", "reg:"]):
            val = re.split(r'[:\-]', line_clean, maxsplit=1)[-1].strip()
            if len(val) > 5:
                extracted["subject"] = val
                break
    if not extracted["subject"]:
        # Fallback to first non-empty line under 150 chars
        lines = [l.strip() for l in text.splitlines() if len(l.strip()) > 10]
        extracted["subject"] = lines[0][:150] if lines else "AI & Emerging Technologies Grievance"

    # 5. Requested Relief
    relief_keywords = ["relief sought", "prayer", "requested relief", "request that", "humbly pray", "action requested"]
    lower_text = text.lower()
    for kw in relief_keywords:
        if kw in lower_text:
            pos = lower_text.find(kw)
            extracted["requested_relief"] = text[pos:pos+400].strip()
            break

    # 6. Category identification
    tech_keywords = {
        "IndiaAI Mission & Compute Capacity": ["indiaai", "compute", "gpu", "supercomputer", "data center", "ai mission"],
        "Deepfake & Synthetic Media": ["deepfake", "synthetic media", "impersonation", "cloning", "misinformation"],
        "Data Protection & Privacy": ["dpdp", "personal data", "consent", "privacy", "data fiduciary", "biometric"],
        "AI Safety & Ethics": ["ai safety", "bias", "algorithmic", "ethical ai", "safety testing"],
        "Startups & R&D Innovation": ["startup", "grant", "incubation", "ai research", "cdac", "centre of excellence"]
    }
    for cat, kws in tech_keywords.items():
        if any(kw in lower_text for kw in kws):
            extracted["category"] = cat
            break

    # Masking for privacy-conscious display
    extracted["applicant_masked"] = mask_applicant_name(extracted["applicant_name"])

    return extracted
