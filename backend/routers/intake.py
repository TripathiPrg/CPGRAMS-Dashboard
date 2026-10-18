"""
Grievance Intake Router
Handles single and batch file uploads (PDF, DOCX, TXT, CSV, Excel), OCR detection,
pasted text intake, entity extraction, and manual verification before commit.
"""

import os
import shutil
from pathlib import Path
from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Body
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.config import UPLOADS_DIR, ALLOWED_FILE_EXTENSIONS, MAX_UPLOAD_SIZE_MB
from backend.models import Grievance, GrievanceAnalysis
from backend.services.document_parser import (
    parse_pdf,
    parse_docx,
    parse_txt,
    parse_tabular,
    extract_fields_from_text,
    mask_applicant_name
)
from backend.services.ai_analyzer import analyze_grievance
from backend.services.audit_logger import log_event

router = APIRouter(prefix="/api/intake", tags=["Intake"])

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Accepts PDF, DOCX, TXT, CSV, or Excel file, extracts text and fields,
    and returns parsed preview for manual officer verification before commit.
    """
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_FILE_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format '{file_ext}'. Allowed formats: {', '.join(ALLOWED_FILE_EXTENSIONS)}"
        )

    # Save to uploads directory
    timestamp_prefix = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = f"{timestamp_prefix}_{file.filename.replace(' ', '_')}"
    save_path = UPLOADS_DIR / safe_name

    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    file_size_mb = os.path.getsize(str(save_path)) / (1024 * 1024)
    if file_size_mb > MAX_UPLOAD_SIZE_MB:
        os.remove(str(save_path))
        raise HTTPException(
            status_code=400,
            detail=f"File exceeds maximum permitted size of {MAX_UPLOAD_SIZE_MB}MB."
        )

    # Parse by extension
    try:
        if file_ext == ".pdf":
            parsed = parse_pdf(str(save_path))
            extracted = extract_fields_from_text(parsed["text"])
            extracted["is_scanned"] = parsed["is_scanned"]
            extracted["page_count"] = parsed["page_count"]
            batch_records = None
        elif file_ext == ".docx":
            parsed = parse_docx(str(save_path))
            extracted = extract_fields_from_text(parsed["text"])
            extracted["is_scanned"] = False
            extracted["page_count"] = parsed["page_count"]
            batch_records = None
        elif file_ext == ".txt":
            parsed = parse_txt(str(save_path))
            extracted = extract_fields_from_text(parsed["text"])
            extracted["is_scanned"] = False
            extracted["page_count"] = 1
            batch_records = None
        elif file_ext in [".csv", ".xlsx", ".xls"]:
            batch_records = parse_tabular(str(save_path))
            extracted = None
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Failed to parse document: {str(e)}")

    # Check for duplicate registration number
    is_duplicate = False
    if extracted and extracted.get("registration_no"):
        existing = db.query(Grievance).filter(Grievance.registration_no == extracted["registration_no"]).first()
        if existing:
            is_duplicate = True

    return {
        "filename": file.filename,
        "saved_path": str(save_path),
        "file_format": file_ext.upper(),
        "is_batch": batch_records is not None,
        "batch_count": len(batch_records) if batch_records else 0,
        "batch_records": batch_records,
        "extracted": extracted,
        "is_duplicate": is_duplicate
    }

@router.post("/parse-text")
def parse_raw_text(
    text: str = Body(..., embed=True),
    db: Session = Depends(get_db)
):
    """Parses pasted raw grievance text and returns structured fields."""
    if not text.strip():
        raise HTTPException(status_code=400, detail="Grievance text cannot be empty.")
    
    extracted = extract_fields_from_text(text)
    is_duplicate = False
    if extracted.get("registration_no"):
        existing = db.query(Grievance).filter(Grievance.registration_no == extracted["registration_no"]).first()
        if existing:
            is_duplicate = True

    return {
        "extracted": extracted,
        "is_duplicate": is_duplicate
    }

@router.post("/confirm")
def confirm_intake(
    data: Dict[str, Any] = Body(...),
    db: Session = Depends(get_db)
):
    """
    Commits verified or manually corrected grievance to the database
    and automatically executes initial AI classification.
    """
    reg_no = data.get("registration_no", "").strip()
    if not reg_no:
        raise HTTPException(status_code=400, detail="Registration number is required.")

    # Duplicate check
    existing = db.query(Grievance).filter(Grievance.registration_no == reg_no).first()
    if existing:
        raise HTTPException(status_code=409, detail=f"Grievance with registration number '{reg_no}' already exists.")

    try:
        date_str = str(data.get("date_received", ""))
        date_val = datetime.strptime(date_str, "%Y-%m-%d").date()
    except Exception:
        date_val = date.today()

    app_name = data.get("applicant_name", "Citizen")

    new_g = Grievance(
        registration_no=reg_no,
        subject=data.get("subject", "Public Grievance"),
        date_received=date_val,
        applicant_name=app_name,
        applicant_masked=mask_applicant_name(app_name),
        applicant_contact=data.get("applicant_contact"),
        category=data.get("category", "AI & Emerging Technologies"),
        concerned_ministry=data.get("concerned_ministry", "Ministry of Electronics and Information Technology"),
        concerned_division=data.get("concerned_division", "AI & Emerging Technologies Division"),
        grievance_text=data.get("grievance_text", ""),
        requested_relief=data.get("requested_relief"),
        status="New",
        priority=data.get("priority", "Normal"),
        target_disposal_date=date_val + timedelta(days=21),  # Standard 21-day norm
        is_sample=False,
        source_type=data.get("source_type", "manual_upload"),
        source_filename=data.get("source_filename")
    )
    db.add(new_g)
    db.flush()

    # Automatically generate structured AI analysis
    analysis_res = analyze_grievance(
        db=db,
        subject=new_g.subject,
        grievance_text=new_g.grievance_text,
        requested_relief=new_g.requested_relief
    )

    analysis_entry = GrievanceAnalysis(
        grievance_id=new_g.id,
        summary=analysis_res["summary"],
        main_allegations=analysis_res["main_allegations"],
        exact_relief_requested=analysis_res["exact_relief_requested"],
        relevant_facts_dates=analysis_res["relevant_facts_dates"],
        policy_jurisdiction_issues=analysis_res["policy_jurisdiction_issues"],
        submission_type=analysis_res["submission_type"],
        concerned_entity=analysis_res["concerned_entity"],
        recommended_next_action=analysis_res["recommended_next_action"],
        confidence_level=analysis_res["confidence_level"],
        confidence_score=analysis_res["confidence_score"],
        missing_info_verification=analysis_res["missing_info_verification"],
        requires_senior_review=analysis_res["requires_senior_review"],
        senior_review_reason=analysis_res["senior_review_reason"]
    )
    db.add(analysis_entry)

    new_g.recommended_action = analysis_res["recommended_next_action"]

    db.commit()

    log_event(
        db=db,
        event_type="RECORD_IMPORT",
        entity_type="Grievance",
        entity_id=str(new_g.id),
        details=f"Intake confirmed for {reg_no}: '{new_g.subject}' with AI classification '{analysis_res['submission_type']}'."
    )

    return {
        "status": "success",
        "id": new_g.id,
        "registration_no": new_g.registration_no,
        "message": "Grievance successfully recorded and analyzed."
    }
