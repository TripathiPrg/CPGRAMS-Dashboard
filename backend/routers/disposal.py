"""
CPGRAMS Authorized Disposal & Verification Router
Governs the 9-stage grievance disposal workflow:
1. Retrieved -> 2. Analysis complete -> 3. Draft generated -> 4. Awaiting review ->
5. Approved for submission -> 6. Submission in progress ->
7. Official submission confirmed (ONLY after portal verification)
OR 8. Submission failed / 9. Status requires verification

STRICT GOI RULE: A grievance is NEVER marked as 'Disposed' or 'Official submission confirmed'
until the official CPGRAMS portal explicitly confirms the update.
"""

from datetime import datetime
from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import Grievance, ReplyDraft, AuditLog
from backend.schemas import (
    DisposalInitiateRequest,
    DisposalVerifyRequest,
    DisposalResultResponse
)
from backend.services.browser_assistant import BrowserAssistantManager
from backend.services.audit_logger import log_event

router = APIRouter(prefix="/api/disposal", tags=["Official Disposal Workflow"])

@router.get("/checklist/{grievance_id}")
def get_disposal_checklist(grievance_id: int, db: Session = Depends(get_db)):
    """
    Evaluates pre-submission disposal checklist for an officer review.
    Ensures all administrative and compliance checks are satisfied before disposal.
    """
    g = db.query(Grievance).filter(Grievance.id == grievance_id).first()
    if not g:
        raise HTTPException(status_code=404, detail="Grievance not found.")

    latest_draft = db.query(ReplyDraft).filter(
        ReplyDraft.grievance_id == grievance_id
    ).order_by(ReplyDraft.version_number.desc()).first()

    has_unfilled_placeholders = False
    if latest_draft and "[verify" in latest_draft.current_draft_text.lower():
        has_unfilled_placeholders = True

    manager = BrowserAssistantManager.get_instance()
    portal_status = manager.get_session_status()

    is_already_disposed = (g.status == "Disposed" or g.workflow_state == "Official submission confirmed")

    checklist = {
        "grievance_id": g.id,
        "registration_no": g.registration_no,
        "workflow_state": g.workflow_state,
        "current_status": g.status,
        "is_already_disposed": is_already_disposed,
        "checks": [
            {
                "id": "valid_reg_no",
                "label": f"Registration No verified: {g.registration_no}",
                "passed": bool(g.registration_no and len(g.registration_no) > 5)
            },
            {
                "id": "draft_exists",
                "label": "Official reply draft generated",
                "passed": latest_draft is not None
            },
            {
                "id": "draft_approved",
                "label": "Draft formally approved by officer",
                "passed": latest_draft is not None and latest_draft.approval_status == "approved"
            },
            {
                "id": "no_placeholders",
                "label": "All [VERIFY: ...] placeholders resolved",
                "passed": not has_unfilled_placeholders
            },
            {
                "id": "portal_session",
                "label": "CPGRAMS Browser Assistant authenticated",
                "passed": portal_status.get("is_logged_in", False),
                "detail": portal_status.get("state", "CLOSED")
            }
        ],
        "can_initiate": (
            not is_already_disposed and
            latest_draft is not None and
            latest_draft.approval_status == "approved" and
            not has_unfilled_placeholders
        ),
        "latest_draft": {
            "id": latest_draft.id if latest_draft else None,
            "version": latest_draft.version_number if latest_draft else None,
            "text": latest_draft.current_draft_text if latest_draft else None,
            "approval_status": latest_draft.approval_status if latest_draft else None
        } if latest_draft else None
    }
    return checklist

@router.post("/initiate", response_model=DisposalResultResponse)
def initiate_disposal(
    req: DisposalInitiateRequest,
    db: Session = Depends(get_db)
):
    """
    Stages an authorized disposal for an approved grievance reply.
    Transitions workflow_state to 'Submission in progress'.
    Prepares the payload in the browser assistant session.
    DOES NOT mark as Disposed until portal confirms.
    """
    g = db.query(Grievance).filter(Grievance.id == req.grievance_id).first()
    if not g:
        raise HTTPException(status_code=404, detail="Grievance not found.")

    # Guardrail 1: Prevent double disposal
    if g.status == "Disposed" or g.workflow_state == "Official submission confirmed":
        raise HTTPException(
            status_code=400,
            detail=f"Double disposal prevented: Grievance {g.registration_no} is already officially confirmed as Disposed on CPGRAMS."
        )

    # Guardrail 2: Draft must exist
    draft = db.query(ReplyDraft).filter(
        ReplyDraft.id == req.draft_id,
        ReplyDraft.grievance_id == req.grievance_id
    ).first()
    if not draft:
        raise HTTPException(status_code=400, detail="Specified draft does not belong to this grievance.")

    # Guardrail 3: Must be approved
    if draft.approval_status != "approved":
        raise HTTPException(
            status_code=400,
            detail="Draft must be approved by officer before initiating portal disposal."
        )

    # Guardrail 4: No placeholders
    if "[verify" in draft.current_draft_text.lower():
        raise HTTPException(
            status_code=400,
            detail="Cannot initiate disposal: Unfilled [VERIFY: ...] verification tags remain in the draft."
        )

    # Transition state to 'Submission in progress'
    g.workflow_state = "Submission in progress"
    g.disposal_category = req.disposal_category
    g.disposal_remarks = req.disposal_remarks or "Disposal prepared via CPGRAMS Workbench"
    db.commit()

    # Browser assistant interaction
    manager = BrowserAssistantManager.get_instance()
    prep_res = manager.prepare_disposal(
        registration_no=g.registration_no,
        approved_text=draft.current_draft_text,
        disposal_type=req.disposal_category
    )

    log_event(
        db=db,
        event_type="DISPOSAL_INITIATED",
        entity_type="Grievance",
        entity_id=str(g.id),
        details=f"Disposal initiated for {g.registration_no}. Action category: '{req.disposal_category}'. Awaiting portal verification."
    )

    return DisposalResultResponse(
        grievance_id=g.id,
        registration_no=g.registration_no,
        workflow_state=g.workflow_state,
        is_verified=False,
        message="Disposal action staged in CPGRAMS session. Review in portal and execute verification check to confirm official update.",
        verification_details=prep_res
    )

@router.post("/verify", response_model=DisposalResultResponse)
def verify_portal_disposal(
    req: DisposalVerifyRequest,
    db: Session = Depends(get_db)
):
    """
    Independently inspects the official CPGRAMS portal DOM to confirm whether
    the grievance has ACTUALLY been updated to 'Disposed'.
    
    If confirmed:
        workflow_state -> 'Official submission confirmed'
        status -> 'Disposed'
        verification_status -> 'verified_by_portal'
    If unconfirmed:
        workflow_state -> 'Status requires verification'
        status remains unchanged!
    """
    g = db.query(Grievance).filter(Grievance.id == req.grievance_id).first()
    if not g:
        raise HTTPException(status_code=404, detail="Grievance not found.")

    manager = BrowserAssistantManager.get_instance()
    verify_res = manager.verify_portal_disposal(
        registration_no=g.registration_no
    )

    if verify_res.get("is_verified", False):
        # Portal confirmation confirmed
        now = datetime.utcnow()
        g.workflow_state = "Official submission confirmed"
        g.status = "Disposed"
        g.verification_status = "verified_by_portal"
        g.portal_action_timestamp = now
        g.portal_confirmation_id = verify_res.get("portal_confirmation_id") or req.portal_confirmation_id

        # Update latest draft status
        latest_draft = db.query(ReplyDraft).filter(
            ReplyDraft.grievance_id == g.id
        ).order_by(ReplyDraft.version_number.desc()).first()
        if latest_draft:
            latest_draft.approval_status = "issued_on_portal"
            g.portal_reply_recorded = latest_draft.current_draft_text

        db.commit()

        log_event(
            db=db,
            event_type="DISPOSAL_VERIFIED",
            entity_type="Grievance",
            entity_id=str(g.id),
            details=f"Portal confirmed disposal for {g.registration_no}. Confirmation ID: {g.portal_confirmation_id}."
        )

        return DisposalResultResponse(
            grievance_id=g.id,
            registration_no=g.registration_no,
            workflow_state=g.workflow_state,
            is_verified=True,
            portal_confirmation_id=g.portal_confirmation_id,
            portal_action_timestamp=g.portal_action_timestamp,
            message="Official CPGRAMS portal confirmed disposal successfully. Record status updated to 'Disposed'.",
            verification_details=verify_res
        )
    else:
        # Not confirmed yet
        g.workflow_state = "Status requires verification"
        g.verification_status = "status_requires_verification"
        db.commit()

        log_event(
            db=db,
            event_type="DISPOSAL_VERIFICATION_PENDING",
            entity_type="Grievance",
            entity_id=str(g.id),
            details=f"Portal verification check unconfirmed for {g.registration_no}. Status marked as 'Status requires verification'."
        )

        return DisposalResultResponse(
            grievance_id=g.id,
            registration_no=g.registration_no,
            workflow_state=g.workflow_state,
            is_verified=False,
            portal_confirmation_id=None,
            portal_action_timestamp=None,
            message="Official CPGRAMS portal has NOT confirmed disposal yet. Dashboard record remains pending. Please check portal window.",
            verification_details=verify_res
        )

@router.post("/manual_verify", response_model=DisposalResultResponse)
def manual_verify_disposal(
    grievance_id: int = Body(...),
    portal_confirmation_id: str = Body(...),
    verification_notes: Optional[str] = Body(None),
    db: Session = Depends(get_db)
):
    """
    Officer manual verification audit.
    When the officer completes the disposal directly on CPGRAMS in their browser
    and records the official portal receipt/order number into the workbench.
    """
    g = db.query(Grievance).filter(Grievance.id == grievance_id).first()
    if not g:
        raise HTTPException(status_code=404, detail="Grievance not found.")

    if not portal_confirmation_id or len(portal_confirmation_id.strip()) < 4:
        raise HTTPException(
            status_code=400,
            detail="Valid CPGRAMS confirmation ID or disposal reference number is required for manual verification."
        )

    now = datetime.utcnow()
    g.workflow_state = "Official submission confirmed"
    g.status = "Disposed"
    g.verification_status = "verified_manual_audit"
    g.portal_action_timestamp = now
    g.portal_confirmation_id = portal_confirmation_id.strip()
    if verification_notes:
        g.disposal_remarks = (g.disposal_remarks or "") + f" | Officer audit note: {verification_notes.strip()}"

    latest_draft = db.query(ReplyDraft).filter(
        ReplyDraft.grievance_id == g.id
    ).order_by(ReplyDraft.version_number.desc()).first()
    if latest_draft:
        latest_draft.approval_status = "issued_on_portal"
        g.portal_reply_recorded = latest_draft.current_draft_text

    db.commit()

    log_event(
        db=db,
        event_type="DISPOSAL_VERIFIED",
        entity_type="Grievance",
        entity_id=str(g.id),
        details=f"Officer manually verified portal disposal for {g.registration_no}. CPGRAMS Ref: {g.portal_confirmation_id}."
    )

    return DisposalResultResponse(
        grievance_id=g.id,
        registration_no=g.registration_no,
        workflow_state=g.workflow_state,
        is_verified=True,
        portal_confirmation_id=g.portal_confirmation_id,
        portal_action_timestamp=g.portal_action_timestamp,
        message=f"Disposal verified by officer audit with CPGRAMS reference {g.portal_confirmation_id}.",
        verification_details={"method": "manual_audit", "notes": verification_notes}
    )

@router.post("/abort")
def abort_disposal(
    grievance_id: int = Body(..., embed=True),
    reason: Optional[str] = Body(None, embed=True),
    db: Session = Depends(get_db)
):
    """
    Aborts in-progress submission staging and reverts state to 'Approved for submission'.
    """
    g = db.query(Grievance).filter(Grievance.id == grievance_id).first()
    if not g:
        raise HTTPException(status_code=404, detail="Grievance not found.")

    if g.status == "Disposed":
        raise HTTPException(status_code=400, detail="Cannot abort: Grievance is already officially disposed.")

    g.workflow_state = "Approved for submission"
    db.commit()

    log_event(
        db=db,
        event_type="DISPOSAL_ABORTED",
        entity_type="Grievance",
        entity_id=str(g.id),
        details=f"Disposal staging aborted for {g.registration_no}. Reason: {reason or 'Officer cancelled'}."
    )

    return {"status": "success", "message": "Disposal staging cancelled. Case returned to 'Approved for submission'."}
