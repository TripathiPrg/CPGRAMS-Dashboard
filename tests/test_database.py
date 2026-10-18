"""
Automated Test Suite: Database Persistence & Models
Verifies that database persists records across sessions, models enforce schemas,
and synthetic records are clearly distinguishable.
"""

import pytest
from datetime import date
from backend.database import SessionLocal, init_db
from backend.models import Grievance, HistoricalPrecedent, ReplyDraft, Correspondence, RoutingRule

@pytest.fixture(scope="module")
def db_session():
    init_db()
    db = SessionLocal()
    yield db
    db.close()

def test_database_persistence_and_querying(db_session):
    """Verifies SQLite persistence and querying."""
    count = db_session.query(Grievance).count()
    assert count >= 4, f"Expected at least 4 seeded grievances, got {count}"

def test_synthetic_data_distinction(db_session):
    """Verifies that synthetic sample records are explicitly labeled with is_sample=True."""
    sample_records = db_session.query(Grievance).filter(Grievance.is_sample == True).all()
    assert len(sample_records) >= 4
    for r in sample_records:
        assert r.is_sample is True
        assert "MEITY/E/" in r.registration_no

def test_historical_precedents_loaded(db_session):
    """Verifies historical disposed library contains valid records with status tags."""
    precedents = db_session.query(HistoricalPrecedent).all()
    assert len(precedents) >= 5
    for p in precedents:
        assert p.status_tag in ["confirmed_issued", "marked_approved", "draft_response", "status_unverified"]
        assert p.reuse_recommendation in ["useful_precedent", "outdated", "incorrect", "restricted"]
        assert len(p.final_reply) > 20

def test_routing_rules_loaded(db_session):
    """Verifies departmental routing rules are configured."""
    rules = db_session.query(RoutingRule).filter(RoutingRule.is_active == True).all()
    assert len(rules) >= 6
    divisions = [r.target_division for r in rules]
    assert "AI & Emerging Technologies Division" in divisions
