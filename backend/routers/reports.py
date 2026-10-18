"""
Reports and Analytics Router
Computes operational performance metrics: intake vs disposal, case ageing,
category distribution, precedent utilization, and CSV/Excel exports.
"""

import io
from datetime import date, timedelta
from typing import Dict, Any, List
from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
import pandas as pd
from backend.database import get_db
from backend.models import Grievance, HistoricalPrecedent, ReplyDraft, Correspondence

router = APIRouter(prefix="/api/reports", tags=["Reports & Analytics"])

@router.get("/summary")
def get_reports_summary(db: Session = Depends(get_db)):
    """Computes comprehensive analytics and breakdown metrics."""
    today = date.today()
    
    # 1. Ageing breakdown for pending cases
    pending_grievances = db.query(Grievance).filter(
        Grievance.status.notin_(["Approved for Disposal", "Disposed"])
    ).all()

    ageing = {
        "0_to_7_days": 0,
        "8_to_15_days": 0,
        "16_to_30_days": 0,
        "over_30_days": 0
    }

    for g in pending_grievances:
        age_days = (today - g.date_received).days
        if age_days <= 7:
            ageing["0_to_7_days"] += 1
        elif age_days <= 15:
            ageing["8_to_15_days"] += 1
        elif age_days <= 30:
            ageing["16_to_30_days"] += 1
        else:
            ageing["over_30_days"] += 1

    # 2. Category distribution
    cat_counts = db.query(Grievance.category, func.count(Grievance.id))\
                   .group_by(Grievance.category).all()
    categories_breakdown = [{"category": c or "Unspecified", "count": count} for c, count in cat_counts]

    # 3. Status distribution
    status_counts = db.query(Grievance.status, func.count(Grievance.id))\
                      .group_by(Grievance.status).all()
    status_breakdown = [{"status": s, "count": count} for s, count in status_counts]

    # 4. Precedent usage metrics
    total_precedents = db.query(HistoricalPrecedent).count()
    useful_precedents = db.query(HistoricalPrecedent).filter(HistoricalPrecedent.reuse_recommendation == "useful_precedent").count()
    outdated_precedents = db.query(HistoricalPrecedent).filter(HistoricalPrecedent.reuse_recommendation == "outdated").count()
    total_drafts = db.query(ReplyDraft).count()

    return {
        "generated_date": today.isoformat(),
        "ageing_breakdown": ageing,
        "categories_breakdown": categories_breakdown,
        "status_breakdown": status_breakdown,
        "precedent_metrics": {
            "total_precedents_in_library": total_precedents,
            "approved_useful_precedents": useful_precedents,
            "outdated_flagged_precedents": outdated_precedents,
            "drafts_generated": total_drafts
        }
    }

@router.get("/export/{fmt}")
def export_grievances_dataset(
    fmt: str,
    mask_pii: bool = Query(True),
    db: Session = Depends(get_db)
):
    """Exports full grievances dataset as CSV or Excel."""
    items = db.query(Grievance).order_by(Grievance.id).all()
    
    rows = []
    for g in items:
        app_name = g.applicant_masked if mask_pii else (g.applicant_name or "Citizen")
        rows.append({
            "Registration No": g.registration_no,
            "Subject": g.subject,
            "Date Received": g.date_received.isoformat(),
            "Applicant": app_name,
            "Category": g.category,
            "Division": g.concerned_division,
            "Status": g.status,
            "Priority": g.priority,
            "Target Disposal Date": g.target_disposal_date.isoformat() if g.target_disposal_date else "",
            "Recommended Action": g.recommended_action or "",
            "Is Sample Data": "Yes" if g.is_sample else "No"
        })

    df = pd.DataFrame(rows)
    fmt_lower = fmt.lower()

    if fmt_lower == "csv":
        stream = io.StringIO()
        df.to_csv(stream, index=False)
        response = StreamingResponse(
            iter([stream.getvalue()]),
            media_type="text/csv"
        )
        response.headers["Content-Disposition"] = "attachment; filename=CPGRAMS_Grievances_Export.csv"
        return response

    elif fmt_lower in ["xlsx", "excel"]:
        stream = io.BytesIO()
        with pd.ExcelWriter(stream, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Grievances")
        stream.seek(0)
        response = StreamingResponse(
            stream,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        response.headers["Content-Disposition"] = "attachment; filename=CPGRAMS_Grievances_Export.xlsx"
        return response

    else:
        raise HTTPException(status_code=400, detail="Supported export formats: csv, xlsx")
