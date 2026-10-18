"""
Unit and Integration Tests for CPGRAMS 9-State Disposal & Verification Workflow
AI & Emerging Technologies Division, MeitY
"""

import pytest
from datetime import date
from fastapi.testclient import TestClient
from backend.main import app
from backend.database import SessionLocal
from backend.models import Grievance, ReplyDraft, GrievanceAnalysis

client = TestClient(app)

@pytest.fixture
def clean_test_case():
    """Creates a fresh test grievance in the database."""
    db = SessionLocal()
    unique_reg = f"TEST/E/2026/{int(date.today().strftime('%Y%m%d'))}999"
    # Remove if existing
    old = db.query(Grievance).filter(Grievance.registration_no == unique_reg).first()
    if old:
        db.delete(old)
        db.commit()

    g = Grievance(
        registration_no=unique_reg,
        subject="Request for allocation of AI compute under IndiaAI Mission for medical diagnostics",
        applicant_name="Dr. Test User",
        applicant_masked="D*r. T*** U***",
        category="AI & Emerging Technologies",
        concerned_ministry="Ministry of Electronics and Information Technology",
        concerned_division="AI & Emerging Technologies Division",
        grievance_text="We require 50 GPU hours from IndiaAI compute portal for AI healthcare research.",
        requested_relief="Access to subsidized compute resources under IndiaAI Mission.",
        status="New",
        workflow_state="Retrieved",
        is_sample=True,
        source_type="synthetic_test"
    )
    db.add(g)
    db.commit()
    db.refresh(g)
    g_id = g.id
    db.close()
    yield g_id

    # Teardown
    db = SessionLocal()
    g_del = db.query(Grievance).filter(Grievance.id == g_id).first()
    if g_del:
        db.delete(g_del)
        db.commit()
    db.close()

def test_workflow_state_transitions(clean_test_case):
    """Verifies state progression from Retrieved -> Analysis complete -> Draft generated -> Awaiting review -> Approved for submission."""
    g_id = clean_test_case

    # Step 1: Initial state is 'Retrieved'
    res = client.get(f"/api/grievances/{g_id}")
    assert res.status_code == 200
    assert res.json()["grievance"]["workflow_state"] == "Retrieved"

    # Step 2: Trigger AI Analysis -> transitions to 'Analysis complete'
    res = client.post(f"/api/grievances/{g_id}/analyze")
    assert res.status_code == 200
    res_g = client.get(f"/api/grievances/{g_id}").json()["grievance"]
    assert res_g["workflow_state"] == "Analysis complete"

    # Step 3: Generate Draft -> transitions to 'Draft generated'
    res = client.post(
        "/api/drafting/generate",
        json={"grievance_id": g_id, "draft_type": "standard_disposal"}
    )
    assert res.status_code == 200
    draft_id = res.json()["id"]
    res_g = client.get(f"/api/grievances/{g_id}").json()["grievance"]
    assert res_g["workflow_state"] == "Draft generated"

    # Step 4: Revise Draft -> transitions to 'Awaiting review'
    res = client.put(
        f"/api/drafting/{draft_id}",
        json={"current_draft_text": "Revised official draft text for testing."}
    )
    assert res.status_code == 200
    res_g = client.get(f"/api/grievances/{g_id}").json()["grievance"]
    assert res_g["workflow_state"] == "Awaiting review"

    # Step 5: Officer Approves Draft -> transitions to 'Approved for submission'
    res = client.post(
        f"/api/drafting/{draft_id}/approve",
        json={"approver": "Authorized Grievance Officer (MeitY AI & ET)"}
    )
    assert res.status_code == 200
    res_g = client.get(f"/api/grievances/{g_id}").json()["grievance"]
    assert res_g["workflow_state"] == "Approved for submission"
    assert res_g["status"] == "Approved for Disposal"

def test_approval_blocked_by_unfilled_placeholders(clean_test_case):
    """Ensures drafts with unresolved [VERIFY: ...] placeholders cannot be approved."""
    g_id = clean_test_case
    res = client.post(
        "/api/drafting/generate",
        json={"grievance_id": g_id, "draft_type": "standard_disposal"}
    )
    draft_id = res.json()["id"]

    # Put an unfilled placeholder
    client.put(
        f"/api/drafting/{draft_id}",
        json={"current_draft_text": "Sir, with reference to grievance, [VERIFY: insert sanction order date], the matter is disposed."}
    )

    # Attempt to approve
    res = client.post(
        f"/api/drafting/{draft_id}/approve",
        json={"approver": "Officer"}
    )
    assert res.status_code == 400
    assert "verification placeholders remain" in res.json()["detail"].lower()

def test_disposal_checklist(clean_test_case):
    """Tests the pre-submission checklist evaluation."""
    g_id = clean_test_case

    # Without draft: can_initiate should be False
    res = client.get(f"/api/disposal/checklist/{g_id}")
    assert res.status_code == 200
    assert res.json()["can_initiate"] is False

    # Generate and approve clean draft
    d_res = client.post(
        "/api/drafting/generate",
        json={"grievance_id": g_id, "draft_type": "standard_disposal"}
    )
    draft_id = d_res.json()["id"]
    client.put(
        f"/api/drafting/{draft_id}",
        json={"current_draft_text": "With reference to the grievance regarding IndiaAI compute, the application has been processed."}
    )
    client.post(
        f"/api/drafting/{draft_id}/approve",
        json={"approver": "Public Grievance Officer"}
    )

    res = client.get(f"/api/disposal/checklist/{g_id}")
    assert res.status_code == 200
    assert res.json()["can_initiate"] is True

def test_disposal_initiation_and_state_change(clean_test_case):
    """Verifies that initiating disposal transitions state to 'Submission in progress'."""
    g_id = clean_test_case
    d_res = client.post(
        "/api/drafting/generate",
        json={"grievance_id": g_id, "draft_type": "standard_disposal"}
    )
    draft_id = d_res.json()["id"]
    client.put(
        f"/api/drafting/{draft_id}",
        json={"current_draft_text": "Clean approved draft without any placeholders."}
    )
    client.post(
        f"/api/drafting/{draft_id}/approve",
        json={"approver": "Officer"}
    )

    # Initiate disposal
    init_res = client.post(
        "/api/disposal/initiate",
        json={
            "grievance_id": g_id,
            "draft_id": draft_id,
            "disposal_category": "Closed with reply",
            "confirmed_by_officer": True
        }
    )
    assert init_res.status_code == 200
    data = init_res.json()
    assert data["workflow_state"] == "Submission in progress"
    assert data["is_verified"] is False

    # Abort disposal
    abort_res = client.post("/api/disposal/abort", json={"grievance_id": g_id, "reason": "Officer review"})
    assert abort_res.status_code == 200
    g_after = client.get(f"/api/grievances/{g_id}").json()["grievance"]
    assert g_after["workflow_state"] == "Approved for submission"

def test_manual_verification_workflow(clean_test_case):
    """Verifies that officer manual confirmation audit updates status to Disposed."""
    g_id = clean_test_case
    d_res = client.post(
        "/api/drafting/generate",
        json={"grievance_id": g_id, "draft_type": "standard_disposal"}
    )
    draft_id = d_res.json()["id"]
    client.put(
        f"/api/drafting/{draft_id}",
        json={"current_draft_text": "Approved reply text."}
    )
    client.post(
        f"/api/drafting/{draft_id}/approve",
        json={"approver": "Officer"}
    )

    # Manual verification
    verify_res = client.post(
        "/api/disposal/manual_verify",
        json={
            "grievance_id": g_id,
            "portal_confirmation_id": "CPGRAMS-DISP-2026-98124",
            "verification_notes": "Verified by officer after submitting in operational desk."
        }
    )
    assert verify_res.status_code == 200
    data = verify_res.json()
    assert data["is_verified"] is True
    assert data["workflow_state"] == "Official submission confirmed"
    assert data["portal_confirmation_id"] == "CPGRAMS-DISP-2026-98124"

    # Verify that parent grievance is now Disposed
    g_final = client.get(f"/api/grievances/{g_id}").json()["grievance"]
    assert g_final["status"] == "Disposed"
    assert g_final["verification_status"] == "verified_manual_audit"

def test_prevent_double_disposal(clean_test_case):
    """Prevents submitting or initiating a disposal on an already disposed case."""
    g_id = clean_test_case
    d_res = client.post(
        "/api/drafting/generate",
        json={"grievance_id": g_id, "draft_type": "standard_disposal"}
    )
    draft_id = d_res.json()["id"]
    client.put(
        f"/api/drafting/{draft_id}",
        json={"current_draft_text": "Valid text."}
    )
    client.post(f"/api/drafting/{draft_id}/approve", json={"approver": "Officer"})

    # Mark disposed
    client.post(
        "/api/disposal/manual_verify",
        json={"grievance_id": g_id, "portal_confirmation_id": "CONF-11111"}
    )

    # Attempt to initiate again
    second_init = client.post(
        "/api/disposal/initiate",
        json={
            "grievance_id": g_id,
            "draft_id": draft_id,
            "disposal_category": "Closed with reply"
        }
    )
    assert second_init.status_code == 400
    assert "double disposal prevented" in second_init.json()["detail"].lower()

def test_bridge_endpoints():
    """Tests the secure hybrid bridge pairing endpoints."""
    # Status
    res = client.get("/api/bridge/status")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "online"
    assert "division" in data

    # Token
    token_res = client.get("/api/bridge/token")
    assert token_res.status_code == 200
    assert "token" in token_res.json()
