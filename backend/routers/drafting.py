"""
Official Reply Drafting Studio Router
Supports precedent-assisted draft generation, versioning, side-by-side diffing,
official compliance checking, approval workflows, and DOCX/TXT export.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Body, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import desc
from backend.database import get_db
from backend.models import Grievance, ReplyDraft, HistoricalPrecedent
from backend.schemas import ReplyDraftResponse, ReplyDraftCreate, ReplyDraftUpdate
from backend.services.reply_generator import (
    generate_official_draft,
    generate_diff,
    validate_draft_compliance
)
from backend.services.docx_exporter import export_reply_to_docx, export_reply_to_txt
from backend.services.audit_logger import log_event

router = APIRouter(prefix="/api/drafting", tags=["Drafting Studio"])

@router.post("/generate")
def create_draft(
    grievance_id: int = Body(...),
    draft_type: str = Body("standard_disposal"),
    precedent_ids: Optional[List[int]] = Body(None),
    custom_instructions: Optional[str] = Body(None),
    db: Session = Depends(get_db)
):
    """Generates a structured, precedent-aware official draft for a case."""
    g = db.query(Grievance).filter(Grievance.id == grievance_id).first()
    if not g:
        raise HTTPException(status_code=404, detail="Grievance not found.")

    res = generate_official_draft(
        db=db,
        grievance=g,
        draft_type=draft_type,
        precedent_ids=precedent_ids,
        custom_instructions=custom_instructions
    )

    # Calculate version number
    prev_draft = db.query(ReplyDraft).filter(ReplyDraft.grievance_id == grievance_id).order_by(desc(ReplyDraft.version_number)).first()
    ver = (prev_draft.version_number + 1) if prev_draft else 1

    new_draft = ReplyDraft(
        grievance_id=grievance_id,
        version_number=ver,
        draft_type=draft_type,
        template_used=draft_type,
        selected_precedents=",".join(map(str, precedent_ids)) if precedent_ids else None,
        original_draft_text=res["draft_text"],
        current_draft_text=res["draft_text"],
        approval_status="draft",
        compliance_notes=res["compliance_notes"]
    )
    db.add(new_draft)

    # Update grievance status if it was New
    if g.status in ["New", "Under Examination"]:
        g.status = "Draft Prepared"

    db.commit()
    db.refresh(new_draft)

    log_event(
        db=db,
        event_type="DRAFT_GENERATED",
        entity_type="Draft",
        entity_id=str(new_draft.id),
        details=f"Generated version {ver} ({draft_type}) for {g.registration_no}."
    )

    return ReplyDraftResponse.from_orm(new_draft)

@router.get("/grievance/{grievance_id}", response_model=List[ReplyDraftResponse])
def get_grievance_drafts(grievance_id: int, db: Session = Depends(get_db)):
    """Lists all draft versions for a grievance."""
    drafts = db.query(ReplyDraft).filter(ReplyDraft.grievance_id == grievance_id).order_by(desc(ReplyDraft.version_number)).all()
    return drafts

@router.put("/{id}")
def update_draft(
    id: int,
    data: ReplyDraftUpdate,
    db: Session = Depends(get_db)
):
    """Saves officer revisions to a draft and evaluates compliance."""
    d = db.query(ReplyDraft).filter(ReplyDraft.id == id).first()
    if not d:
        raise HTTPException(status_code=404, detail="Draft not found.")

    d.current_draft_text = data.current_draft_text
    if data.approval_status:
        d.approval_status = data.approval_status
    if data.approved_by:
        d.approved_by = data.approved_by

    # Run compliance check
    compliance_issues = validate_draft_compliance(d.current_draft_text)
    if compliance_issues:
        notes = " | ".join(f"[{i['severity']}] {i['message']}" for i in compliance_issues)
        d.compliance_notes = notes

    db.commit()

    log_event(
        db=db,
        event_type="DRAFT_REVISED",
        entity_type="Draft",
        entity_id=str(d.id),
        details=f"Officer revised draft version {d.version_number}."
    )

    return {
        "status": "success",
        "compliance_issues": compliance_issues,
        "draft": ReplyDraftResponse.from_orm(d)
    }

@router.post("/{id}/diff")
def get_draft_diff(id: int, db: Session = Depends(get_db)):
    """Computes HTML table and unified text diff between original and revised drafts."""
    d = db.query(ReplyDraft).filter(ReplyDraft.id == id).first()
    if not d:
        raise HTTPException(status_code=404, detail="Draft not found.")

    diff_res = generate_diff(d.original_draft_text, d.current_draft_text)
    return diff_res

@router.post("/{id}/approve")
def approve_draft(
    id: int,
    approver: str = Body("Authorized Officer (MeitY AI & ET)", embed=True),
    db: Session = Depends(get_db)
):
    """
    Formally marks draft as approved for portal issuance.
    Requires explicit officer action.
    """
    d = db.query(ReplyDraft).filter(ReplyDraft.id == id).first()
    if not d:
        raise HTTPException(status_code=404, detail="Draft not found.")

    # Check for blocking compliance issues
    if "[verify" in d.current_draft_text.lower():
        raise HTTPException(
            status_code=400,
            detail="Cannot approve draft: Unfilled [VERIFY: ...] verification placeholders remain in text."
        )

    d.approval_status = "approved"
    d.approved_by = approver
    d.approval_timestamp = datetime.utcnow()

    # Update parent grievance status
    g = db.query(Grievance).filter(Grievance.id == d.grievance_id).first()
    if g:
        g.status = "Approved for Disposal"

    db.commit()

    log_event(
        db=db,
        event_type="APPROVAL_MARKED",
        entity_type="Draft",
        entity_id=str(d.id),
        details=f"Draft version {d.version_number} for {g.registration_no if g else id} approved by {approver}."
    )

    return {"status": "success", "message": "Draft marked as approved for official disposal."}

@router.get("/{id}/export/{fmt}")
def export_draft_document(
    id: int,
    fmt: str,
    mask_pii: bool = Query(False),
    db: Session = Depends(get_db)
):
    """Exports reply draft to official DOCX or TXT file."""
    d = db.query(ReplyDraft).filter(ReplyDraft.id == id).first()
    if not d:
        raise HTTPException(status_code=404, detail="Draft not found.")

    g = db.query(Grievance).filter(Grievance.id == d.grievance_id).first()
    reg_no = g.registration_no if g else "DRAFT"
    subject = g.subject if g else "CPGRAMS Disposal"
    app_name = g.applicant_name if g else "Citizen"

    fmt_lower = fmt.lower()
    if fmt_lower == "docx":
        file_path = export_reply_to_docx(
            registration_no=reg_no,
            subject=subject,
            reply_text=d.current_draft_text,
            applicant_name=app_name,
            mask_pii=mask_pii
        )
        media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    elif fmt_lower == "txt":
        file_path = export_reply_to_txt(
            registration_no=reg_no,
            subject=subject,
            reply_text=d.current_draft_text
        )
        media_type = "text/plain"
    else:
        raise HTTPException(status_code=400, detail="Supported export formats: docx, txt")

    log_event(
        db=db,
        event_type="EXPORT",
        entity_type="Draft",
        entity_id=str(d.id),
        details=f"Exported draft version {d.version_number} as {fmt.upper()} for {reg_no}."
    )

    return FileResponse(
        path=file_path,
        filename=f"CPGRAMS_Reply_{reg_no.replace('/', '_')}.{fmt_lower}",
        media_type=media_type
    )
