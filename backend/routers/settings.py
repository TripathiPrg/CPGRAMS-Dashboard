"""
Settings & Knowledge Management Router
Manages routing directory rules, correspondence templates, database backup/restore,
security audit trail, and local environment diagnostics.
"""

import sys
import platform
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Body, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from backend.database import get_db
from backend.models import RoutingRule, ResponseTemplate, AuditLog
from backend.schemas import (
    RoutingRuleResponse,
    RoutingRuleCreate,
    ResponseTemplateResponse,
    ResponseTemplateCreate,
    AuditLogResponse
)
from backend.config import HOST, PORT, ALLOW_EXTERNAL_REQUESTS, get_installed_browser
from backend.services.backup_service import create_backup, list_backups, restore_backup
from backend.services.audit_logger import log_event

router = APIRouter(prefix="/api/settings", tags=["Settings & Knowledge Management"])

# 1. Routing Rules
@router.get("/routing-rules", response_model=List[RoutingRuleResponse])
def get_routing_rules(db: Session = Depends(get_db)):
    """Lists all configurable departmental routing rules."""
    return db.query(RoutingRule).order_by(RoutingRule.priority_order).all()

@router.post("/routing-rules", response_model=RoutingRuleResponse)
def create_routing_rule(data: RoutingRuleCreate, db: Session = Depends(get_db)):
    """Creates a new routing rule without code modifications."""
    rule = RoutingRule(**data.dict())
    db.add(rule)
    db.commit()
    db.refresh(rule)

    log_event(
        db=db,
        event_type="RECORD_MODIFIED",
        entity_type="System",
        details=f"Created routing rule: '{rule.rule_name}' -> {rule.target_division}."
    )
    return rule

@router.put("/routing-rules/{id}")
def update_routing_rule(
    id: int,
    data: Dict[str, Any] = Body(...),
    db: Session = Depends(get_db)
):
    """Updates an existing routing rule."""
    rule = db.query(RoutingRule).filter(RoutingRule.id == id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Routing rule not found.")

    for k, v in data.items():
        if hasattr(rule, k):
            setattr(rule, k, v)
    db.commit()

    log_event(
        db=db,
        event_type="RECORD_MODIFIED",
        entity_type="System",
        details=f"Updated routing rule {rule.rule_name}."
    )
    return {"status": "success", "message": "Routing rule updated."}

@router.delete("/routing-rules/{id}")
def delete_routing_rule(id: int, db: Session = Depends(get_db)):
    """Deletes a routing rule."""
    rule = db.query(RoutingRule).filter(RoutingRule.id == id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Routing rule not found.")

    name = rule.rule_name
    db.delete(rule)
    db.commit()

    log_event(
        db=db,
        event_type="RECORD_DELETED",
        entity_type="System",
        details=f"Deleted routing rule '{name}'."
    )
    return {"status": "success", "message": "Rule deleted."}

# 2. Templates
@router.get("/templates", response_model=List[ResponseTemplateResponse])
def get_templates(db: Session = Depends(get_db)):
    """Lists approved correspondence and disposal templates."""
    return db.query(ResponseTemplate).order_by(ResponseTemplate.id).all()

@router.post("/templates", response_model=ResponseTemplateResponse)
def create_template(data: ResponseTemplateCreate, db: Session = Depends(get_db)):
    """Creates a new response template."""
    tmpl = ResponseTemplate(**data.dict())
    db.add(tmpl)
    db.commit()
    db.refresh(tmpl)
    return tmpl

# 3. Backup and Restore
@router.get("/backups")
def get_backups_list():
    """Lists available local database snapshots."""
    return list_backups()

@router.post("/backups/create")
def trigger_backup(db: Session = Depends(get_db)):
    """Creates an instant snapshot of the SQLite database."""
    try:
        res = create_backup()
        log_event(
            db=db,
            event_type="BACKUP_CREATED",
            entity_type="System",
            details=f"Created database snapshot '{res['filename']}' ({res['size_kb']} KB)."
        )
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/backups/restore")
def trigger_restore(
    filename: str = Body(..., embed=True),
    db: Session = Depends(get_db)
):
    """
    Restores the database from a verified snapshot.
    Performs integrity validation and creates pre-restore safety copy.
    """
    try:
        res = restore_backup(filename)
        log_event(
            db=db,
            event_type="BACKUP_RESTORED",
            entity_type="System",
            details=f"Restored database from snapshot '{filename}'."
        )
        return res
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# 4. Security Audit Logs
@router.get("/audit-logs", response_model=List[AuditLogResponse])
def get_audit_trail(
    limit: int = Query(50, ge=1, le=200),
    event_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Returns application operations audit log."""
    q = db.query(AuditLog)
    if event_type and event_type != "All":
        q = q.filter(AuditLog.event_type == event_type)
    return q.order_by(desc(AuditLog.timestamp)).limit(limit).all()

# 5. System Diagnostics & Info
@router.get("/system-info")
def get_system_info():
    """Returns local runtime diagnostics and security parameters."""
    browser = get_installed_browser()
    return {
        "operating_system": platform.system(),
        "os_release": platform.release(),
        "python_version": sys.version.split()[0],
        "binding_host": HOST,
        "binding_port": PORT,
        "external_network_calls_blocked": not ALLOW_EXTERNAL_REQUESTS,
        "installed_browser": browser["name"] if browser else "None detected",
        "browser_path": browser["path"] if browser else "N/A",
        "application_version": "1.0.0 (MeitY CPGRAMS Workbench)",
        "security_profile": "Local-Only Enforced (Zero Cloud Telemetry)"
    }
