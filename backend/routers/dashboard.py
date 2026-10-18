"""
Dashboard Router
Serves live statistics and activity derived directly from local database records.
"""

from datetime import date, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.database import get_db
from backend.models import Grievance, ReplyDraft, Correspondence, AuditLog, HistoricalPrecedent
from backend.schemas import DashboardStats, AuditLogResponse

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])

@router.get("/stats", response_model=DashboardStats)
def get_dashboard_stats(db: Session = Depends(get_db)):
    today = date.today()
    approaching_date = today + timedelta(days=5)

    total_grievances = db.query(Grievance).count()
    new_grievances = db.query(Grievance).filter(Grievance.status == "New").count()
    pending_grievances = db.query(Grievance).filter(Grievance.status.in_(["New", "Under Examination", "Awaiting Inputs", "Draft Prepared"])).count()
    disposed_grievances = db.query(Grievance).filter(Grievance.status.in_(["Approved for Disposal", "Disposed"])).count()
    
    awaiting_inputs = db.query(Correspondence).filter(Correspondence.status.in_(["Sent", "Reminder Sent", "Overdue"])).count()
    drafts_awaiting_review = db.query(ReplyDraft).filter(ReplyDraft.approval_status.in_(["draft", "under_review"])).count()

    approaching_deadlines = db.query(Grievance).filter(
        Grievance.status.notin_(["Approved for Disposal", "Disposed"]),
        Grievance.target_disposal_date != None,
        Grievance.target_disposal_date <= approaching_date
    ).count()

    urgent_attention = db.query(Grievance).filter(
        Grievance.status.notin_(["Approved for Disposal", "Disposed"]),
        (Grievance.priority.in_(["Urgent", "High"])) | 
        ((Grievance.target_disposal_date != None) & (Grievance.target_disposal_date < today))
    ).count()

    sample_count = db.query(Grievance).filter(Grievance.is_sample == True).count()
    real_count = db.query(Grievance).filter(Grievance.is_sample == False).count()

    recent_logs = db.query(AuditLog).order_by(AuditLog.timestamp.desc()).limit(8).all()

    return DashboardStats(
        total_grievances=total_grievances,
        new_grievances=new_grievances,
        pending_grievances=pending_grievances,
        disposed_grievances=disposed_grievances,
        awaiting_inputs=awaiting_inputs,
        drafts_awaiting_review=drafts_awaiting_review,
        approaching_deadlines=approaching_deadlines,
        urgent_attention=urgent_attention,
        sample_records_count=sample_count,
        real_records_count=real_count,
        last_sync_time=None,
        recent_activities=[AuditLogResponse.from_orm(l) for l in recent_logs]
    )
