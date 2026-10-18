"""
Automated Test Suite: Official Reply Drafting Studio & Document Export
Verifies precedent-assisted draft generation, versioning, diff calculations,
compliance safeguards, approval guardrails, and GoI-standard DOCX export.
"""

import os
import pytest
from backend.database import SessionLocal, init_db
from backend.models import Grievance, HistoricalPrecedent, ReplyDraft
from backend.services.reply_generator import (
    generate_official_draft,
    generate_diff,
    validate_draft_compliance
)
from backend.services.docx_exporter import export_reply_to_docx

@pytest.fixture(scope="module")
def db_session():
    init_db()
    db = SessionLocal()
    yield db
    db.close()

def test_generate_draft_with_precedents(db_session):
    g = db_session.query(Grievance).filter(Grievance.registration_no == "MEITY/E/2026/0003189").first()
    p = db_session.query(HistoricalPrecedent).filter(HistoricalPrecedent.registration_no == "MEITY/E/2024/0018921").first()
    
    res = generate_official_draft(
        db=db_session,
        grievance=g,
        draft_type="policy_explanation",
        precedent_ids=[p.id]
    )

    assert "MEITY/E/2026/0003189" in res["draft_text"]
    assert "IndiaAI Mission" in res["draft_text"]
    assert "stands disposed of" in res["draft_text"]

def test_diff_generation():
    orig = "Paragraph 1: Original text.\nParagraph 2: Common text."
    rev = "Paragraph 1: Revised officer text.\nParagraph 2: Common text."

    diff = generate_diff(orig, rev)
    assert diff["has_changes"] is True
    assert "table" in diff["html_diff_table"]
    assert "Revised officer text" in diff["unified_diff"]

def test_draft_compliance_checker():
    # 1. Draft with unfilled placeholder
    bad_draft = "This is reply with [VERIFY: Date of dispatch] placeholder."
    issues = validate_draft_compliance(bad_draft)
    assert any(i["severity"] == "CRITICAL" for i in issues)

    # 2. Draft with internal AI leakage
    ai_draft = "As an AI large language model, I advise that the matter stands disposed of."
    issues_ai = validate_draft_compliance(ai_draft)
    assert any("AI commentary" in i["message"] for i in issues_ai)

    # 3. Clean compliant draft
    clean_draft = (
        "With reference to CPGRAMS registration number MEITY/E/2026/000123.\n\n"
        "2. The grievance has been examined in the AI & Emerging Technologies Division. "
        "The applicant's concern has been resolved according to departmental norms.\n\n"
        "3. In view of the above position, the grievance stands disposed of on the CPGRAMS portal."
    )
    clean_issues = validate_draft_compliance(clean_draft)
    assert len([i for i in clean_issues if i["severity"] == "CRITICAL"]) == 0

def test_docx_export():
    out_file = export_reply_to_docx(
        registration_no="MEITY/E/2026/TEST001",
        subject="Test Case on AI Startup Vouchers",
        reply_text="The matter has been reviewed and stands disposed of on CPGRAMS.",
        applicant_name="Test Citizen",
        mask_pii=True
    )
    assert os.path.exists(out_file)
    assert out_file.endswith(".docx")
    assert os.path.getsize(out_file) > 1000  # Valid docx file
