"""
Historical Disposed Grievance Library Router
Provides local full-text and semantic search, precedent tagging, provenance tracking,
and officer reuse recommendations.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session
from sqlalchemy import desc, or_
from backend.database import get_db
from backend.models import HistoricalPrecedent
from backend.schemas import (
    PrecedentResponse,
    PrecedentCreate,
    PrecedentSearchRequest,
    PrecedentMatchResult
)
from backend.services.semantic_search import search_precedents
from backend.services.audit_logger import log_event

router = APIRouter(prefix="/api/precedents", tags=["Precedent Library"])

@router.get("", response_model=List[PrecedentResponse])
def list_precedents(
    category: Optional[str] = None,
    reuse: Optional[str] = None,
    status_tag: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Lists historical disposed grievances in the library with filters."""
    query = db.query(HistoricalPrecedent)

    if category and category != "All":
        query = query.filter(HistoricalPrecedent.category == category)
    if reuse and reuse != "All":
        query = query.filter(HistoricalPrecedent.reuse_recommendation == reuse)
    if status_tag and status_tag != "All":
        query = query.filter(HistoricalPrecedent.status_tag == status_tag)
    if search:
        search_fmt = f"%{search.strip()}%"
        query = query.filter(
            or_(
                HistoricalPrecedent.registration_no.ilike(search_fmt),
                HistoricalPrecedent.subject.ilike(search_fmt),
                HistoricalPrecedent.full_grievance_text.ilike(search_fmt),
                HistoricalPrecedent.final_reply.ilike(search_fmt),
                HistoricalPrecedent.policy_reference.ilike(search_fmt)
            )
        )

    return query.order_by(desc(HistoricalPrecedent.disposal_date)).all()

@router.post("/search", response_model=List[PrecedentMatchResult])
def semantic_search(
    req: PrecedentSearchRequest,
    db: Session = Depends(get_db)
):
    """
    Executes local TF-IDF semantic vector search against historical library.
    Returns ranked matches with similarity score, match %, explanations, and differences.
    """
    results = search_precedents(
        db=db,
        query_text=req.query,
        category=req.category,
        reuse_filter=req.reuse_recommendation,
        min_similarity=req.min_similarity,
        top_k=req.limit
    )
    return results

@router.post("", response_model=PrecedentResponse)
def add_precedent(
    data: PrecedentCreate,
    db: Session = Depends(get_db)
):
    """Adds a new disposed grievance record to the historical library."""
    existing = db.query(HistoricalPrecedent).filter(HistoricalPrecedent.registration_no == data.registration_no).first()
    if existing:
        raise HTTPException(status_code=409, detail=f"Precedent {data.registration_no} already exists.")

    new_p = HistoricalPrecedent(**data.dict())
    db.add(new_p)
    db.commit()
    db.refresh(new_p)

    log_event(
        db=db,
        event_type="RECORD_IMPORT",
        entity_type="Precedent",
        entity_id=str(new_p.id),
        details=f"Added historical precedent {new_p.registration_no}: '{new_p.subject}'."
    )

    return new_p

@router.put("/{id}/reuse")
def update_reuse_recommendation(
    id: int,
    reuse_recommendation: str = Body(..., embed=True),
    officer_notes: Optional[str] = Body(None, embed=True),
    db: Session = Depends(get_db)
):
    """
    Allows officer to mark precedent as:
    'useful_precedent', 'outdated', 'incorrect', or 'restricted'.
    """
    valid_tags = ["useful_precedent", "outdated", "incorrect", "restricted"]
    if reuse_recommendation not in valid_tags:
        raise HTTPException(status_code=400, detail=f"Invalid tag. Valid options: {valid_tags}")

    p = db.query(HistoricalPrecedent).filter(HistoricalPrecedent.id == id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Precedent not found.")

    p.reuse_recommendation = reuse_recommendation
    if officer_notes is not None:
        p.officer_notes = officer_notes
    db.commit()

    log_event(
        db=db,
        event_type="PRECEDENT_SELECTED",
        entity_type="Precedent",
        entity_id=str(id),
        details=f"Officer marked precedent {p.registration_no} as '{reuse_recommendation}'."
    )

    return {"status": "success", "message": f"Precedent marked as {reuse_recommendation}."}
