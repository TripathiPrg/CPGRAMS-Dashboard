"""
Automated Test Suite: Local Semantic Search & Precedent Ranking
Verifies that incoming grievances retrieve the most relevant historical precedents,
explain matching concepts, and identify outdated guidance.
"""

import pytest
from backend.database import SessionLocal, init_db
from backend.services.semantic_search import search_precedents

@pytest.fixture(scope="module")
def db_session():
    init_db()
    db = SessionLocal()
    yield db
    db.close()

def test_semantic_match_indiaai_compute(db_session):
    """Query on GPU compute vouchers should rank IndiaAI precedent highest."""
    query = "We need subsidized GPU compute cluster vouchers under IndiaAI Mission for LLM training."
    matches = search_precedents(db=db_session, query_text=query, top_k=3)
    assert len(matches) > 0
    top = matches[0]
    assert top["precedent"]["registration_no"] == "MEITY/E/2024/0018921"
    assert top["similarity_score"] > 0.20
    assert top["is_recommended"] is True
    assert "IndiaAI" in top["relevance_explanation"] or "compute" in top["relevance_explanation"].lower()

def test_semantic_match_deepfake(db_session):
    """Query on deepfakes should rank IT Rules 2021 precedent highest."""
    query = "Malicious deepfake video impersonating me on social media platform; intermediary failed to delete."
    matches = search_precedents(db=db_session, query_text=query, top_k=3)
    assert len(matches) > 0
    top = matches[0]
    assert top["precedent"]["registration_no"] == "MEITY/E/2024/0023419"
    assert "IT" in top["precedent"]["policy_reference"] and "Rules" in top["precedent"]["policy_reference"]

def test_outdated_precedent_flagged(db_session):
    """Precedent marked outdated must not be recommended for reuse."""
    query = "2018 draft National AI Strategy policy committees"
    matches = search_precedents(db=db_session, query_text=query, top_k=5)
    for m in matches:
        if m["precedent"]["registration_no"] == "MEITY/E/2022/0004112":
            assert m["is_recommended"] is False
            assert any("OUTDATED" in diff for diff in m["key_differences"])
