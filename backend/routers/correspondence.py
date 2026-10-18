"""
Correspondence & Input Tracker Router
Tracks requests for inputs sent to other divisions, departments, or external agencies.
Maintains follow-up logs and approaching deadline reminders.
"""

from datetime import date
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from sqlalchemy import desc
from backend.database import get_db
from backend.models import Correspondence, Grievance
from backend.schemas import CorrespondenceResponse, CorrespondenceCreate, CorrespondenceUpdate
from backend.services.audit_logger import log_event

router = APIRouter(prefix="/api/correspondence", tags=["Correspondence Tracker"])

@router.get("", response_model=List[CorrespondenceResponse])
def list_correspondence(
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Lists all tracked input requests."""
    query = db.query(Correspondence)
    if status and status != "All":
        query = query.filter(Correspondence.status == status)
    return query.order_by(desc(Correspondence.date_sent)).all()

@router.post("", response_model=CorrespondenceResponse)
def create_correspondence(
    data: CorrespondenceCreate,
    db: Session = Depends(get_db)
):
    """Creates a new input request tracker."""
    new_c = Correspondence(**data.dict())
    db.add(new_c)

    # If linked to a grievance, update grievance status to 'Awaiting Inputs'
    if data.grievance_id:
        g = db.query(Grievance).filter(Grievance.id == data.grievance_id).first()
        if g and g.status in ["New", "Under Examination"]:
            g.status = "Awaiting Inputs"

    db.commit()
    db.refresh(new_c)

    log_event(
        db=db,
        event_type="RECORD_IMPORT",
        entity_type="Correspondence",
        entity_id=str(new_c.id),
        details=f"Issued call for inputs {new_c.reference_no} to {new_c.recipient_office}."
    )

    return new_c

@router.put("/{id}", response_model=CorrespondenceResponse)
def update_correspondence(
    id: int,
    data: CorrespondenceUpdate,
    db: Session = Depends(get_db)
):
    """Updates status, logs responses received, or adds reminder."""
    c = db.query(Correspondence).filter(Correspondence.id == id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Correspondence record not found.")

    for k, v in data.dict(exclude_unset=True).items():
        setattr(c, k, v)

    db.commit()
    db.refresh(c)

    log_event(
        db=db,
        event_type="RECORD_MODIFIED",
        entity_type="Correspondence",
        entity_id=str(c.id),
        details=f"Updated correspondence {c.reference_no} status to '{c.status}'."
    )

    return c

@router.post("/{id}/reminder")
def log_reminder(
    id: int,
    reminder_note: str = Body(..., embed=True),
    db: Session = Depends(get_db)
):
    """Logs an internal follow-up reminder note."""
    c = db.query(Correspondence).filter(Correspondence.id == id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Correspondence record not found.")

    today_str = date.today().strftime("%d/%m/%Y")
    entry = f"[{today_str}] Reminder: {reminder_note}"
    c.follow_up_history = f"{c.follow_up_history}\n{entry}" if c.follow_up_history else entry
    c.status = "Reminder Sent"

    db.commit()

    log_event(
        db=db,
        event_type="RECORD_MODIFIED",
        entity_type="Correspondence",
        entity_id=str(c.id),
        details=f"Logged follow-up reminder for {c.reference_no}."
    )

    return {"status": "success", "message": "Reminder recorded."}
