"""
AI Grievance Analysis Service
Generates structured multi-dimensional analysis: summary, allegations, relief,
policy context, submission classification, departmental routing, confidence,
missing info, and senior-officer review flagging.
Runs locally with heuristic rule engine and optional local LLM.
"""

import re
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from backend.models import RoutingRule, HistoricalPrecedent
from backend.services.semantic_search import search_precedents

def analyze_grievance(
    db: Session,
    subject: str,
    grievance_text: str,
    requested_relief: str = None
) -> Dict[str, Any]:
    """
    Produces comprehensive 12-point structured analysis for an incoming grievance.
    """
    combined_text = f"{subject}\n{grievance_text}\n{requested_relief or ''}"
    lower = combined_text.lower()

    # 1. Submission Type Classification
    if any(k in lower for k in ["under rti", "right to information", "section 6(1) of rti", "provide copy of", "information sought"]):
        sub_type = "RTI Query / Information Request"
    elif any(k in lower for k in ["i suggest", "suggestion:", "proposal for", "innovative idea", "recommendation to meity"]):
        sub_type = "Suggestion / Policy Proposal"
    elif any(k in lower for k in ["representation regarding", "memorandum", "association request", "joint representation"]):
        sub_type = "Representation"
    elif any(k in lower for k in ["court order", "writ petition", "high court", "sub judice", "contempt notice"]):
        sub_type = "Legal / Sub-Judice Matter"
    elif any(k in lower for k in ["tender dispute", "commercial contract", "vendor payment", "arbitration"]):
        sub_type = "Commercial / Contractual Dispute"
    else:
        sub_type = "Public Grievance"

    # 2. Main Allegations
    allegations = []
    if "delay" in lower or "pending" in lower or "not processed" in lower:
        allegations.append("Undue administrative delay in processing application or subsidy disbursement.")
    if "rejection" in lower or "rejected" in lower or "denied" in lower:
        allegations.append("Arbitrary or unreasoned rejection of eligibility or technical proposal.")
    if "deepfake" in lower or "cloning" in lower or "synthetic" in lower or "morph" in lower:
        allegations.append("Circulation of non-consensual synthetic media / deepfake and inadequate intermediary takedown.")
    if "privacy" in lower or "data leak" in lower or "personal data" in lower or "consent" in lower:
        allegations.append("Breach of personal data or unauthorized processing by data fiduciary.")
    if "gpu" in lower or "compute" in lower or "indiaai" in lower:
        allegations.append("Dispute or difficulty accessing subsidized compute infrastructure under IndiaAI Mission.")
    if "bias" in lower or "hallucination" in lower or "safety" in lower:
        allegations.append("Harm or bias resulting from deployed algorithmic AI system.")
    if not allegations:
        allegations.append("Citizen expressing dissatisfaction with service delivery or policy implementation.")

    # 3. Exact Relief Requested
    exact_relief = requested_relief
    if not exact_relief or len(exact_relief.strip()) < 10:
        relief_matches = re.findall(r'(?:request|pray|demand|want|seek|appeal)\s+(?:that|to|for)?\s+([^.\n]+)', combined_text, re.IGNORECASE)
        if relief_matches:
            exact_relief = f"Seeking: {relief_matches[0].strip()}"
        else:
            exact_relief = "Intervention requested to redress the stated concern and provide formal administrative clarification."

    # 4. Relevant Facts & Dates
    dates_found = re.findall(r'\b(?:\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{2,4})\b', combined_text, re.IGNORECASE)
    refs_found = re.findall(r'\b(?:[A-Z0-9_\-\/]{8,25})\b', combined_text)
    facts_summary = []
    if dates_found:
        facts_summary.append(f"Referenced dates: {', '.join(dates_found[:4])}")
    if refs_found:
        valid_refs = [r for r in refs_found if any(char.isdigit() for char in r) and not r.startswith("http")][:3]
        if valid_refs:
            facts_summary.append(f"External reference identifiers: {', '.join(valid_refs)}")
    facts_text = " | ".join(facts_summary) if facts_summary else "No specific external registration reference or chronological milestone cited."

    # 5. Policy / Jurisdictional Issues
    policy_issues = []
    if "indiaai" in lower or "compute" in lower:
        policy_issues.append("IndiaAI Mission Governance Framework (Cabinet approved March 2024; implementation via IndiaAI Independent Business Division).")
    if "deepfake" in lower or "it rules" in lower or "social media" in lower or "intermediary" in lower:
        policy_issues.append("Information Technology (Intermediary Guidelines and Digital Media Ethics Code) Rules, 2021 as amended; Section 79 & 69A of IT Act 2000.")
    if "privacy" in lower or "dpdp" in lower or "data protection" in lower:
        policy_issues.append("Digital Personal Data Protection (DPDP) Act, 2023 provisions regarding notice, consent, and grievance redressal mechanism of Data Fiduciary.")
    if "rti" in lower:
        policy_issues.append("Right to Information Act, 2005 (Matters requiring separate RTI application via rtionline.gov.in rather than CPGRAMS).")
    if not policy_issues:
        policy_issues.append("General governance standards and Citizen Charter guidelines of MeitY.")

    # 6. Check Departmental Routing Rules from DB
    rules = db.query(RoutingRule).filter(RoutingRule.is_active == True).order_by(RoutingRule.priority_order).all()
    matched_division = "AI & Emerging Technologies Division"
    matched_action = "Examine grievance in division and prepare official disposal reply on merits."
    routing_reason = "Matter directly pertains to AI policies, foundational models, or compute infrastructure falling within Division's mandate."
    uncertainty_flag = "Low Uncertainty"

    for r in rules:
        triggers = [t.strip().lower() for t in r.keyword_triggers.split(",") if t.strip()]
        if any(t in lower for t in triggers):
            matched_division = r.target_division
            matched_action = r.recommended_action
            routing_reason = r.explanation
            if "transfer" in r.recommended_action.lower():
                uncertainty_flag = "Departmental Review Advised (Verify Rule 6 applicability)"
            break

    # 7. Missing Information & Verification Requirements
    missing = []
    if not dates_found:
        missing.append("Specific date of incident or prior application submission not stated.")
    if "portal" in lower and not any(k in lower for k in ["application id", "ack", "reference"]):
        missing.append("Portal application reference ID or acknowledgement number not provided.")
    if len(grievance_text.strip()) < 80:
        missing.append("Grievance narrative is brief; supporting documentation or specific particulars required.")

    # 8. Senior Officer Review Flag
    requires_senior = False
    senior_reasons = []
    if sub_type in ["Legal / Sub-Judice Matter", "Commercial / Contractual Dispute"]:
        requires_senior = True
        senior_reasons.append(f"Submission classified as {sub_type}; requires legal consultation.")
    if any(k in lower for k in ["parliament", "lok sabha", "rajya sabha", "vip", "minister", "secretary meity"]):
        requires_senior = True
        senior_reasons.append("Contains reference to VIP / Parliamentary reference / Union Ministry Leadership.")
    if any(k in lower for k in ["contempt", "legal notice", "high court", "supreme court"]):
        requires_senior = True
        senior_reasons.append("Explicit threat of litigation or existing court proceedings cited.")
    if any(k in lower for k in ["national security", "critical infrastructure", "sovereignty"]):
        requires_senior = True
        senior_reasons.append("Potential national security or sovereign IT infrastructure implications.")

    # 9. Confidence Score
    confidence_score = 0.88
    if missing:
        confidence_score -= 0.10 * len(missing)
    if requires_senior:
        confidence_score -= 0.08
    confidence_score = max(0.40, min(0.96, confidence_score))
    conf_level = "High" if confidence_score >= 0.80 else ("Medium" if confidence_score >= 0.60 else "Low")

    # 10. Summary
    sentences = [s.strip() for s in grievance_text.split(".") if len(s.strip()) > 15]
    concise_summary = ". ".join(sentences[:2]) + "." if sentences else subject

    return {
        "summary": concise_summary,
        "main_allegations": " \n".join(f"• {a}" for a in allegations),
        "exact_relief_requested": exact_relief,
        "relevant_facts_dates": facts_text,
        "policy_jurisdiction_issues": " \n".join(f"• {p}" for p in policy_issues),
        "submission_type": sub_type,
        "concerned_entity": f"{matched_division} ({uncertainty_flag})",
        "recommended_next_action": matched_action,
        "confidence_level": conf_level,
        "confidence_score": round(confidence_score, 2),
        "missing_info_verification": " \n".join(f"• {m}" for m in missing) if missing else "Sufficient prima facie information available for examination.",
        "requires_senior_review": requires_senior,
        "senior_review_reason": " \n".join(senior_reasons) if senior_reasons else None,
        "routing_explanation": routing_reason
    }
