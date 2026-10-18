"""
CPGRAMS Portal Assistant Router
Manages browser automation, navigation helpers, read-only visible record retrieval,
and selective import with duplicate verification.
"""

from datetime import datetime, date
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import Grievance
from backend.services.browser_assistant import BrowserAssistantManager
from backend.services.audit_logger import log_event
from backend.services.document_parser import mask_applicant_name

router = APIRouter(prefix="/api/portal", tags=["Portal Assistant"])

@router.post("/launch")
def launch_portal_browser(db: Session = Depends(get_db)):
    """Launches visible browser session directed to official CPGRAMS Officer Portal."""
    manager = BrowserAssistantManager.get_instance()
    try:
        res = manager.launch_session()
        log_event(
            db=db,
            event_type="SYNC_ATTEMPT",
            entity_type="System",
            details="Launched controlled browser session for officer login on CPGRAMS."
        )
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status")
def get_portal_status():
    """Returns current active status of browser session and page."""
    manager = BrowserAssistantManager.get_instance()
    return manager.get_session_status()

@router.post("/navigate")
def navigate_portal(destination: str = Body(..., embed=True), db: Session = Depends(get_db)):
    """Navigates open browser to authorized portal pages (operational_desk, search, etc.)."""
    manager = BrowserAssistantManager.get_instance()
    try:
        res = manager.navigate_to(destination)
        log_event(
            db=db,
            event_type="SYNC_ATTEMPT",
            entity_type="System",
            details=f"Navigated browser session to: {destination} ({res['url']})"
        )
        return res
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/inspect")
def inspect_portal_records(db: Session = Depends(get_db)):
    """
    Inspects visible records on current screen and flags duplicates against local database.
    Does not modify database. Read-only preview.
    """
    manager = BrowserAssistantManager.get_instance()
    try:
        records = manager.inspect_visible_records()
        
        # Check duplicates against DB
        existing_regs = set(r[0] for r in db.query(Grievance.registration_no).all())
        
        preview_list = []
        duplicate_count = 0
        new_count = 0

        for r in records:
            reg = r["registration_no"]
            is_dup = reg in existing_regs
            if is_dup:
                duplicate_count += 1
            else:
                new_count += 1
            preview_list.append({
                **r,
                "is_duplicate": is_dup,
                "applicant_masked": mask_applicant_name(r.get("applicant_name"))
            })

        return {
            "total_detected": len(records),
            "new_records": new_count,
            "duplicate_records": duplicate_count,
            "records": preview_list
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/import")
def import_selected_records(
    selected_records: List[Dict[str, Any]] = Body(...),
    db: Session = Depends(get_db)
):
    """
    Imports officer-selected records into local database.
    Skips duplicates.
    """
    imported = []
    skipped = []

    for item in selected_records:
        reg_no = item.get("registration_no", "").strip()
        if not reg_no:
            continue
        
        exists = db.query(Grievance).filter(Grievance.registration_no == reg_no).first()
        if exists:
            skipped.append(reg_no)
            continue

        try:
            date_val = datetime.strptime(item.get("date_received", ""), "%Y-%m-%d").date()
        except Exception:
            date_val = date.today()

        new_g = Grievance(
            registration_no=reg_no,
            subject=item.get("subject", "Imported CPGRAMS Record"),
            date_received=date_val,
            applicant_name=item.get("applicant_name", "Citizen"),
            applicant_masked=mask_applicant_name(item.get("applicant_name")),
            category=item.get("category", "AI & Emerging Technologies"),
            concerned_ministry="Ministry of Electronics and Information Technology",
            concerned_division="AI & Emerging Technologies Division",
            grievance_text=item.get("raw_row", item.get("subject", "Imported from portal view")),
            status=item.get("status", "New"),
            is_sample=False,
            source_type="portal_assisted"
        )
        db.add(new_g)
        imported.append(reg_no)

    db.commit()

    if imported:
        log_event(
            db=db,
            event_type="RECORD_IMPORT",
            entity_type="Grievance",
            details=f"Imported {len(imported)} records via CPGRAMS Browser Assistant: {', '.join(imported[:5])}..."
        )

    return {
        "imported_count": len(imported),
        "skipped_count": len(skipped),
        "imported_reg_nos": imported,
        "skipped_reg_nos": skipped
    }

@router.post("/close")
def close_portal_browser(db: Session = Depends(get_db)):
    """Closes the browser session."""
    manager = BrowserAssistantManager.get_instance()
    manager.close_session()
    log_event(
        db=db,
        event_type="SYNC_ATTEMPT",
        entity_type="System",
        details="Closed CPGRAMS Browser Assistant session."
    )
    return {"status": "closed"}
