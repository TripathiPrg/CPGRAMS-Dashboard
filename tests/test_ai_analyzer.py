"""
Automated Test Suite: AI Grievance Analysis & Routing
Verifies 12-point structured evaluation, submission classification,
departmental routing recommendations, and senior officer review flagging.
"""

import pytest
from backend.database import SessionLocal, init_db
from backend.services.ai_analyzer import analyze_grievance

@pytest.fixture(scope="module")
def db_session():
    init_db()
    db = SessionLocal()
    yield db
    db.close()

def test_analyze_standard_indiaai_grievance(db_session):
    res = analyze_grievance(
        db=db_session,
        subject="Delay in GPU voucher release under IndiaAI portal",
        grievance_text="We applied on 01/10/2026 for 64 GPUs under application IA-COMP-0891. We seek expedited compute credits.",
        requested_relief="Release compute credits."
    )
    assert res["submission_type"] == "Public Grievance"
    assert "AI & Emerging Technologies Division" in res["concerned_entity"]
    assert res["confidence_score"] >= 0.70
    assert "IA-COMP-0891" in res["relevant_facts_dates"]
    assert res["requires_senior_review"] is False

def test_analyze_rti_request(db_session):
    res = analyze_grievance(
        db=db_session,
        subject="Request for file notings under RTI Act",
        grievance_text="Under Section 6(1) of the RTI Act 2005, please supply certified copies of committee minutes."
    )
    assert "RTI Query" in res["submission_type"]
    assert "rtionline.gov.in" in res["recommended_next_action"].lower() or "cpi" in res["concerned_entity"].lower() or "rti" in res["concerned_entity"].lower()

def test_analyze_senior_review_flag(db_session):
    """Grievance referencing Union Minister or High Court contempt must flag senior review."""
    res = analyze_grievance(
        db=db_session,
        subject="High Court contempt notice regarding deepfake takedown inaction",
        grievance_text="Take notice that a writ petition has been filed before the High Court and Union Minister regarding this platform."
    )
    assert res["requires_senior_review"] is True
    assert len(res["senior_review_reason"]) > 10
