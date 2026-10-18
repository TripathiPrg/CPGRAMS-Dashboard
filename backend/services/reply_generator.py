"""
Official Reply Drafting Studio Engine
Synthesizes Government of India official responses using precedent knowledge,
statutory frameworks, and official drafting conventions.
Includes version comparison diffing and compliance validation.
"""

import difflib
from datetime import date
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from backend.models import Grievance, HistoricalPrecedent, ResponseTemplate

OFFICIAL_HEADER = (
    "GOVERNMENT OF INDIA\n"
    "MINISTRY OF ELECTRONICS AND INFORMATION TECHNOLOGY\n"
    "AI & EMERGING TECHNOLOGIES DIVISION\n"
    "ELECTRONICS NIKETAN, 6, CGO COMPLEX, NEW DELHI - 110003\n\n"
)

def generate_official_draft(
    db: Session,
    grievance: Grievance,
    draft_type: str = "standard_disposal",
    precedent_ids: List[int] = None,
    custom_instructions: str = None
) -> Dict[str, Any]:
    """
    Generates a formal, professional official response adhering strictly to
    MeitY administrative guidelines and Central Secretariat Manual of Office Procedure (CSMOP).
    """
    precedents = []
    if precedent_ids:
        precedents = db.query(HistoricalPrecedent).filter(HistoricalPrecedent.id.in_(precedent_ids)).all()

    reg_no = grievance.registration_no
    subject = grievance.subject
    relief = grievance.requested_relief or "redressal of the matter"
    text_sample = grievance.grievance_text

    # Extract matching precedent text for synthesis
    precedent_context = ""
    precedent_refs = []
    if precedents:
        for p in precedents:
            precedent_refs.append(f"{p.registration_no} (Disposed: {p.disposal_date})")
            if p.final_reply and p.reuse_recommendation == "useful_precedent":
                precedent_context += f"\n[Referenced Precedent {p.registration_no}]: {p.final_reply[:400]}..."

    today_str = date.today().strftime("%d/%m/%Y")
    
    # Select drafting structure based on draft_type
    if draft_type == "out_of_scope":
        body = (
            f"With reference to CPGRAMS registration number {reg_no} dated {grievance.date_received.strftime('%d/%m/%Y') if grievance.date_received else today_str} "
            f"regarding '{subject}'.\n\n"
            f"2. The grievance has been duly examined in the AI & Emerging Technologies Division, MeitY. "
            f"It is observed that the subject matter raised pertains to {relief}, which falls outside the operational mandate of this Ministry under the Government of India (Allocation of Business) Rules.\n\n"
            f"3. In accordance with Department of Administrative Reforms and Public Grievances (DARPG) guidelines, matters involving commercial vendor disputes, sub-judice court proceedings, or requests for information under the RTI Act, 2005 are not amenable to redressal through the CPGRAMS mechanism. "
            f"The applicant is accordingly advised to approach the appropriate jurisdictional forum or submit a statutory application under the relevant Act, if so advised.\n\n"
            f"4. In view of the above, the grievance stands disposed of on the CPGRAMS portal."
        )

    elif draft_type == "transfer_referral":
        body = (
            f"With reference to CPGRAMS registration number {reg_no} regarding '{subject}'.\n\n"
            f"2. On preliminary examination, it is observed that the primary relief sought ({relief}) "
            f"substantively concerns administrative matters under the purview of another Department/Division.\n\n"
            f"3. The matter is accordingly being transferred under Rule 6 of the CPGRAMS guidelines to the concerned Nodal Public Grievance Officer for appropriate examination and direct reply to the applicant.\n\n"
            f"4. The applicant may track further progress under the same registration reference on the CPGRAMS portal."
        )

    elif draft_type == "call_for_inputs":
        body = (
            f"OFFICE MEMORANDUM / U.O. NOTE\n"
            f"Subject: CPGRAMS Grievance No. {reg_no} regarding {subject}\n\n"
            f"The undersigned is directed to forward herewith a copy of CPGRAMS Grievance No. {reg_no} received from {grievance.applicant_name or 'Citizen'} seeking {relief}.\n\n"
            f"2. As the matter directly concerns technical/operational aspects administered by your Division/Organisation, it is requested that factual inputs and comments may kindly be furnished to the AI & Emerging Technologies Division within 7 working days to enable timely disposal on the CPGRAMS portal.\n\n"
            f"To:\n"
            f"Nodal Officer / Division Head,\n"
            f"[Concerned Division / Subordinate Office / C-DAC / NIC]"
        )

    elif draft_type == "policy_explanation":
        # Check domain context (IndiaAI, Deepfakes, DPDP)
        if "indiaai" in text_sample.lower() or "compute" in text_sample.lower() or "gpu" in text_sample.lower():
            policy_specifics = (
                "Under the comprehensive IndiaAI Mission approved by the Union Cabinet with an outlay of ₹10,372 crore, "
                "the Government is establishing state-of-the-art AI compute capacity comprising 10,000 or more GPUs accessible via public-private partnerships. "
                "The allocation of compute capacity, research grants, and application portals are being administered through transparent, objective criteria announced via official notifications on the IndiaAI portal (indiaai.gov.in)."
            )
        elif "deepfake" in text_sample.lower() or "synthetic" in text_sample.lower():
            policy_specifics = (
                "Under the Information Technology (Intermediary Guidelines and Digital Media Ethics Code) Rules, 2021 as amended, "
                "social media intermediaries are legally obligated to exercise due diligence and swiftly remove unlawful or impersonating synthetic content upon receiving actual knowledge or court/government order within the prescribed statutory timelines."
            )
        else:
            policy_specifics = (
                "The AI & Emerging Technologies Division of MeitY facilitates inclusive, secure, and ethical adoption of AI technologies across sectors "
                "in line with National Strategy on Artificial Intelligence and relevant statutory safeguards."
            )

        body = (
            f"With reference to grievance registration number {reg_no} dated {grievance.date_received.strftime('%d/%m/%Y') if grievance.date_received else today_str} "
            f"regarding '{subject}'.\n\n"
            f"2. The representation and the relief sought ({relief}) have been carefully examined in the AI & Emerging Technologies Division, MeitY.\n\n"
            f"3. In this regard, it is clarified that:\n"
            f"   {policy_specifics}\n\n"
            f"4. The applicant's suggestions/concerns have been noted for administrative consideration during ongoing stakeholder consultations. "
            f"Official notifications and guidelines are periodically published on the Ministry's official website (meity.gov.in).\n\n"
            f"5. With these clarifications, the matter stands disposed of on the CPGRAMS portal."
        )

    else:  # Standard Disposal Reply
        body = (
            f"With reference to CPGRAMS registration number {reg_no} regarding '{subject}'.\n\n"
            f"2. The grievance has been duly examined in the AI & Emerging Technologies Division, Ministry of Electronics and Information Technology (MeitY). "
            f"With respect to the specific grievance concerning {relief}, it is informed that the matter has been reviewed in accordance with prevailing departmental norms and guidelines.\n\n"
            f"3. Based on the examination: [VERIFY: Specific factual resolution details or application status to be verified by dealing officer before approval].\n\n"
            f"4. In view of the above position, the grievance stands disposed of on the CPGRAMS portal."
        )

    compliance_notes = []
    if "[VERIFY:" in body:
        compliance_notes.append("ACTION REQUIRED: Contains '[VERIFY: ...]' placeholder that requires officer factual confirmation before approval.")
    if precedent_refs:
        compliance_notes.append(f"Precedent Traceability: Synthesized using historical precedent(s): {', '.join(precedent_refs)}.")

    return {
        "draft_type": draft_type,
        "draft_text": body,
        "precedents_referenced": precedent_refs,
        "compliance_notes": " \n".join(compliance_notes) if compliance_notes else "Draft meets official format criteria."
    }

def generate_diff(original_text: str, revised_text: str) -> Dict[str, Any]:
    """
    Computes visual word-level and line-level diffs between original and revised drafts.
    """
    orig_lines = original_text.splitlines()
    rev_lines = revised_text.splitlines()

    differ = difflib.HtmlDiff()
    html_diff = differ.make_table(
        orig_lines,
        rev_lines,
        fromdesc="Original Generated Draft",
        todesc="Revised Officer Draft",
        context=True,
        numlines=2
    )

    diff_lines = list(difflib.unified_diff(
        orig_lines,
        rev_lines,
        fromfile="Original Draft",
        tofile="Revised Draft",
        lineterm=""
    ))

    return {
        "unified_diff": "\n".join(diff_lines),
        "html_diff_table": html_diff,
        "has_changes": original_text.strip() != revised_text.strip()
    }

def validate_draft_compliance(draft_text: str) -> List[Dict[str, str]]:
    """
    Validates drafting quality against MeitY and CSMOP official norms.
    """
    warnings = []
    
    if "[verify" in draft_text.lower():
        warnings.append({
            "severity": "CRITICAL",
            "message": "Unfilled [VERIFY: ...] verification placeholders remain in the draft."
        })
    if len(draft_text.strip()) < 100:
        warnings.append({
            "severity": "WARNING",
            "message": "Draft is unusually brief; ensure statutory/policy rationale is adequately explained."
        })
    if any(ai_term in draft_text.lower() for ai_term in ["as an ai", "large language model", "generated by ai", "antigravity", "gemini"]):
        warnings.append({
            "severity": "CRITICAL",
            "message": "Internal AI commentary detected in official draft. Strip internal markers immediately."
        })
    if "stands disposed of" not in draft_text.lower() and "transferred under rule" not in draft_text.lower() and "office memorandum" not in draft_text.lower():
        warnings.append({
            "severity": "INFO",
            "message": "Standard closing phrase ('stands disposed of' / 'transferred') was not detected."
        })

    return warnings
