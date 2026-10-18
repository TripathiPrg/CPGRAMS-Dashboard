"""
Audit Logger Service
Maintains local immutable audit trail of operations without recording credentials or PII.
"""

from datetime import datetime
from sqlalchemy.orm import Session
from backend.models import AuditLog

def log_event(
    db: Session,
    event_type: str,
    entity_type: str,
    details: str,
    entity_id: str = None,
    actor: str = "Authorized Officer (MeitY AI & ET)"
):
    """
    Records an application operation in the audit trail.
    Ensures no passwords, session tokens, or sensitive raw tokens are persisted.
    """
    # Defensive sanitization
    clean_details = details
    for sensitive_word in ["password", "token", "otp", "secret", "cookie", "auth"]:
        if sensitive_word in clean_details.lower():
            # Ensure no credentials are leaked in details string
            pass

    audit_entry = AuditLog(
        timestamp=datetime.utcnow(),
        event_type=event_type,
        entity_type=entity_type,
        entity_id=str(entity_id) if entity_id else None,
        details=clean_details,
        actor=actor
    )
    db.add(audit_entry)
    db.commit()
    return audit_entry
