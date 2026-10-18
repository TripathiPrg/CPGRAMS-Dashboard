"""
Grievance Register Router
Manages the searchable registry, detailed case views, manual field editing,
analysis retrieval, and status updates.
"""

from datetime import date
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc, asc
from backend.database import get_db
from backend.models import Grievance, GrievanceAnalysis, ReplyDraft, Correspondence, AuditLog
from backend.schemas import (
    GrievanceResponse,
    GrievanceUpdate,
    GrievanceAnalysisResponse,
    GrievanceAnalysisUpdate,
    ReplyDraftResponse,
    CorrespondenceResponse,
    AuditLogResponse
)
from backend.services.ai_analyzer import analyze_grievance
from backend.services.audit_logger import log_event

router = APIRouter(prefix="/api/grievances", tags=["Grievance Register"])

@router.get("")
def list_grievances(
    search: Optional[str] = None,
    status: Optional[str] = None,
    category: Optional[str] = None,
    priority: Optional[str] = None,
    is_sample: Optional[bool] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(15, ge=1, le=100),
    unmask_pii: bool = False,
    db: Session = Depends(get_db)
):
    """
    Searchable, filterable, paginated register of grievances.
    Defaults to privacy-conscious masked applicant display.
    """
    query = db.query(Grievance)

    if search:
        search_fmt = f"%{search.strip()}%"
        query = query.filter(
            or_(
                Grievance.registration_no.ilike(search_fmt),
                Grievance.subject.ilike(search_fmt),
                Grievance.grievance_text.ilike(search_fmt),
                Grievance.applicant_name.ilike(search_fmt)
            )
        )

    if status and status != "All":
        query = query.filter(Grievance.status == status)

    if category and category != "All":
        query = query.filter(Grievance.category == category)

    if priority and priority != "All":
        query = query.filter(Grievance.priority == priority)

    if is_sample is not None:
        query = query.filter(Grievance.is_sample == is_sample)

    total_count = query.count()
    items = query.order_by(desc(Grievance.date_received), desc(Grievance.id))\
                 .offset((page - 1) * page_size)\
                 .limit(page_size)\
                 .all()

    today = date.today()
    results = []
    for g in items:
        # Determine deadline badge
        deadline_status = "NORMAL"
        days_remaining = None
        if g.status in ["Approved for Disposal", "Disposed"]:
            deadline_status = "DISPOSED"
        elif g.target_disposal_date:
            days_remaining = (g.target_disposal_date - today).days
            if days_remaining < 0:
                deadline_status = "OVERDUE"
            elif days_remaining <= 5:
                deadline_status = "APPROACHING"

        display_name = g.applicant_name if unmask_pii else (g.applicant_masked or "Citizen")

        results.append({
            "id": g.id,
            "registration_no": g.registration_no,
            "subject": g.subject,
            "date_received": g.date_received.isoformat(),
            "applicant_name": display_name,
            "applicant_masked": g.applicant_masked,
            "category": g.category,
            "concerned_ministry": g.concerned_ministry,
            "concerned_division": g.concerned_division,
            "grievance_text": g.grievance_text[:220] + "..." if len(g.grievance_text) > 220 else g.grievance_text,
            "requested_relief": g.requested_relief,
            "status": g.status,
            "recommended_action": g.recommended_action,
            "priority": g.priority,
            "target_disposal_date": g.target_disposal_date.isoformat() if g.target_disposal_date else None,
            "days_remaining": days_remaining,
            "deadline_status": deadline_status,
            "is_sample": g.is_sample,
            "source_type": g.source_type,
            "created_at": g.created_at.isoformat(),
            "updated_at": g.updated_at.isoformat()
        })

    return {
        "total": total_count,
        "page": page,
        "page_size": page_size,
        "items": results
    }

@router.get("/{id}")
def get_grievance_detail(
    id: int,
    unmask_pii: bool = False,
    db: Session = Depends(get_db)
):
    """
    Returns full details for a grievance case:
    original narrative, analysis, previous drafts, correspondence, and action history.
    """
    g = db.query(Grievance).filter(Grievance.id == id).first()
    if not g:
        raise HTTPException(status_code=404, detail="Grievance not found.")

    analysis = db.query(GrievanceAnalysis).filter(GrievanceAnalysis.grievance_id == id).first()
    drafts = db.query(ReplyDraft).filter(ReplyDraft.grievance_id == id).order_by(desc(ReplyDraft.version_number)).all()
    corrs = db.query(Correspondence).filter(Correspondence.grievance_id == id).all()
    logs = db.query(AuditLog).filter(
        AuditLog.entity_type == "Grievance",
        AuditLog.entity_id == str(id)
    ).order_by(desc(AuditLog.timestamp)).all()

    today = date.today()
    days_remaining = (g.target_disposal_date - today).days if g.target_disposal_date else None

    return {
        "grievance": {
            "id": g.id,
            "registration_no": g.registration_no,
            "subject": g.subject,
            "date_received": g.date_received.isoformat(),
            "applicant_name": g.applicant_name if unmask_pii else (g.applicant_masked or "Citizen"),
            "applicant_masked": g.applicant_masked,
            "applicant_contact": g.applicant_contact if unmask_pii else "Masked (Toggle PII to View)",
            "category": g.category,
            "concerned_ministry": g.concerned_ministry,
            "concerned_division": g.concerned_division,
            "grievance_text": g.grievance_text,
            "requested_relief": g.requested_relief,
            "status": g.status,
            "workflow_state": g.workflow_state or "Retrieved",
            "recommended_action": g.recommended_action,
            "priority": g.priority,
            "target_disposal_date": g.target_disposal_date.isoformat() if g.target_disposal_date else None,
            "days_remaining": days_remaining,
            "portal_action_timestamp": g.portal_action_timestamp.isoformat() if g.portal_action_timestamp else None,
            "portal_confirmation_id": g.portal_confirmation_id,
            "verification_status": g.verification_status or "unverified",
            "portal_reply_recorded": g.portal_reply_recorded,
            "disposal_category": g.disposal_category,
            "disposal_remarks": g.disposal_remarks,
            "is_sample": g.is_sample,
            "source_type": g.source_type,
            "created_at": g.created_at.isoformat(),
            "updated_at": g.updated_at.isoformat()
        },
        "analysis": GrievanceAnalysisResponse.from_orm(analysis) if analysis else None,
        "drafts": [ReplyDraftResponse.from_orm(d) for d in drafts],
        "correspondence": [CorrespondenceResponse.from_orm(c) for c in corrs],
        "audit_logs": [AuditLogResponse.from_orm(l) for l in logs]
    }

@router.put("/{id}")
def update_grievance(
    id: int,
    data: GrievanceUpdate,
    db: Session = Depends(get_db)
):
    """Updates editable grievance attributes."""
    g = db.query(Grievance).filter(Grievance.id == id).first()
    if not g:
        raise HTTPException(status_code=404, detail="Grievance not found.")

    update_dict = data.dict(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(g, key, value)

    db.commit()

    log_event(
        db=db,
        event_type="RECORD_MODIFIED",
        entity_type="Grievance",
        entity_id=str(g.id),
        details=f"Updated fields for {g.registration_no}: {', '.join(update_dict.keys())}."
    )

    return {"status": "success", "message": "Grievance updated successfully."}

@router.post("/{id}/analyze")
def trigger_analysis(id: int, db: Session = Depends(get_db)):
    """Runs or refreshes structured AI analysis for a case."""
    g = db.query(Grievance).filter(Grievance.id == id).first()
    if not g:
        raise HTTPException(status_code=404, detail="Grievance not found.")

    res = analyze_grievance(
        db=db,
        subject=g.subject,
        grievance_text=g.grievance_text,
        requested_relief=g.requested_relief
    )

    valid_data = {k: v for k, v in res.items() if hasattr(GrievanceAnalysis, k)}
    existing_analysis = db.query(GrievanceAnalysis).filter(GrievanceAnalysis.grievance_id == id).first()
    if existing_analysis:
        for k, v in valid_data.items():
            setattr(existing_analysis, k, v)
        existing_analysis.is_manually_corrected = False
        target_entry = existing_analysis
    else:
        target_entry = GrievanceAnalysis(grievance_id=id, **valid_data)
        db.add(target_entry)

    g.recommended_action = res["recommended_next_action"]
    if g.workflow_state in ["Retrieved", "New"]:
        g.workflow_state = "Analysis complete"
    db.commit()

    log_event(
        db=db,
        event_type="RECORD_MODIFIED",
        entity_type="Grievance",
        entity_id=str(g.id),
        details=f"Generated structured analysis for {g.registration_no}."
    )

    return GrievanceAnalysisResponse.from_orm(target_entry)

@router.put("/{id}/analysis")
def update_analysis_corrections(
    id: int,
    data: GrievanceAnalysisUpdate,
    db: Session = Depends(get_db)
):
    """Allows manual officer corrections to AI-generated analysis."""
    analysis = db.query(GrievanceAnalysis).filter(GrievanceAnalysis.grievance_id == id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis record not found.")

    for k, v in data.dict(exclude_unset=True).items():
        setattr(analysis, k, v)
    analysis.is_manually_corrected = True

    db.commit()

    log_event(
        db=db,
        event_type="RECORD_MODIFIED",
        entity_type="Grievance",
        entity_id=str(id),
        details=f"Officer manually modified AI analysis for grievance ID {id}."
    )

    return {"status": "success", "message": "Analysis updated with manual corrections."}

@router.delete("/{id}")
def delete_grievance(id: int, db: Session = Depends(get_db)):
    """Deletes a grievance record. Requires explicit officer action."""
    g = db.query(Grievance).filter(Grievance.id == id).first()
    if not g:
        raise HTTPException(status_code=404, detail="Grievance not found.")

    reg_no = g.registration_no
    db.delete(g)
    db.commit()

    log_event(
        db=db,
        event_type="RECORD_DELETED",
        entity_type="Grievance",
        entity_id=str(id),
        details=f"Deleted grievance record {reg_no}."
    )

    return {"status": "success", "message": f"Record {reg_no} deleted."}
