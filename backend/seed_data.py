"""
Synthetic Seed Data Module
Pre-populates the local database with realistic, high-fidelity test records
specifically tailored to the AI & Emerging Technologies Division, MeitY.
All synthetic records are explicitly labeled with is_sample=True.
"""

from datetime import date, datetime, timedelta
from sqlalchemy.orm import Session
from backend.models import (
    Grievance,
    HistoricalPrecedent,
    RoutingRule,
    ResponseTemplate,
    Correspondence,
    ReplyDraft,
    GrievanceAnalysis
)
from backend.services.document_parser import mask_applicant_name

def seed_database(db: Session):
    """Populates the database with realistic MeitY AI & ET cases if empty."""
    
    # Check if already seeded
    if db.query(Grievance).count() > 0:
        return

    # 1. Routing Rules (Configurable directory)
    routing_rules_data = [
        {
            "rule_name": "IndiaAI Mission & Compute Infrastructure",
            "keyword_triggers": "indiaai, gpu, compute capacity, supercomputer, cluster, data center, ai mission",
            "match_category": "AI Infrastructure",
            "target_ministry": "Ministry of Electronics and Information Technology",
            "target_division": "AI & Emerging Technologies Division",
            "recommended_action": "Examine grievance in division; provide status of IndiaAI compute allocation portal.",
            "explanation": "Compute allocation and GPU subsidies fall squarely within the mandate of the AI & Emerging Technologies Division.",
            "priority_order": 1
        },
        {
            "rule_name": "Deepfake & Synthetic Media Grievance",
            "keyword_triggers": "deepfake, synthetic media, face swap, voice clone, impersonation, morphed video",
            "match_category": "AI Safety & Ethics",
            "target_ministry": "Ministry of Electronics and Information Technology",
            "target_division": "AI & Emerging Technologies Division / Cyber Laws Division",
            "recommended_action": "Verify intermediary takedown compliance under IT Rules 2021; advise cyber crime reporting portal.",
            "explanation": "Content removal falls under Rule 3(1)(b) of IT Rules 2021. Criminal reporting pertains to National Cyber Crime Portal.",
            "priority_order": 2
        },
        {
            "rule_name": "Semiconductor & Chip Fabrication",
            "keyword_triggers": "semiconductor, fabrication, fab, chip design, dli scheme, ism",
            "match_category": "Hardware & Manufacturing",
            "target_ministry": "Ministry of Electronics and Information Technology",
            "target_division": "India Semiconductor Mission (ISM)",
            "recommended_action": "Transfer to India Semiconductor Mission (ISM) under Rule 6.",
            "explanation": "Matters regarding semiconductor fabs, assembly testing (ATMP), and Design Linked Incentive (DLI) fall under ISM.",
            "priority_order": 3
        },
        {
            "rule_name": "Telecom Towers & Spectrum Allocation",
            "keyword_triggers": "telecom tower, spectrum, 5g radiation, sim card, trai, mobile network",
            "match_category": "Telecommunications",
            "target_ministry": "Ministry of Communications",
            "target_division": "Department of Telecommunications (DoT)",
            "recommended_action": "Transfer to Department of Telecommunications (DoT) under Rule 6.",
            "explanation": "Telecom service providers, spectrum allocation, and radiation norms are under Department of Telecommunications.",
            "priority_order": 4
        },
        {
            "rule_name": "RTI Query / Information Demand",
            "keyword_triggers": "under rti, right to information, certified copies, section 6(1), file notings",
            "match_category": "Statutory RTI",
            "target_ministry": "Ministry of Electronics and Information Technology",
            "target_division": "RTI Cell / CPIO MeitY",
            "recommended_action": "Dispose with advice to file statutory RTI application at rtionline.gov.in.",
            "explanation": "CPGRAMS cannot be utilized as a substitute for the statutory RTI mechanism under the RTI Act, 2005.",
            "priority_order": 5
        },
        {
            "rule_name": "AI in Healthcare & Medical Devices",
            "keyword_triggers": "medical ai, clinical trial, diagnostic algorithm, medical device, patient scan ai",
            "match_category": "Healthcare AI",
            "target_ministry": "Ministry of Health and Family Welfare",
            "target_division": "CDSCO / e-Health Division, MoHFW",
            "recommended_action": "Seek comments from CDSCO or transfer to Ministry of Health & Family Welfare.",
            "explanation": "Validation of medical AI diagnostic software falls under Central Drugs Standard Control Organisation (CDSCO).",
            "priority_order": 6
        }
    ]

    for r in routing_rules_data:
        db.add(RoutingRule(**r))

    # 2. Response Templates
    templates_data = [
        {
            "template_code": "TMPL_STD_DISPOSAL",
            "title": "Standard CPGRAMS Disposal Reply",
            "template_type": "standard_disposal",
            "concerned_division": "AI & Emerging Technologies Division",
            "template_body": (
                "With reference to CPGRAMS registration number {registration_no} regarding '{subject}'.\n\n"
                "2. The grievance has been duly examined in the AI & Emerging Technologies Division, Ministry of Electronics and Information Technology (MeitY). "
                "With respect to the grievance concerning {requested_relief}, it is informed that {specific_reply_content}\n\n"
                "3. In view of the above position, the grievance stands disposed of on the CPGRAMS portal."
            ),
            "placeholders": "{registration_no}, {subject}, {requested_relief}, {specific_reply_content}",
            "is_default": True
        },
        {
            "template_code": "TMPL_INDIAAI_COMPUTE",
            "title": "IndiaAI Mission Compute Capacity Guidance",
            "template_type": "policy_explanation",
            "concerned_division": "AI & Emerging Technologies Division",
            "template_body": (
                "With reference to CPGRAMS registration number {registration_no} regarding '{subject}'.\n\n"
                "2. The grievance has been examined in the AI & Emerging Technologies Division, MeitY. "
                "Under the Pillar of 'IndiaAI Compute Capacity' sanctioned under the IndiaAI Mission, the Government has finalized the empanelment framework for AI compute infrastructure providers (10,000+ GPUs) to provide subsidized compute access to Indian startups, academia, and researchers.\n\n"
                "3. The onboarding portal for eligibility verification and compute voucher allocation is hosted at indiaai.gov.in. "
                "Eligible Indian entities may submit their technical requirements against active Expression of Interest (EoI) calls published on the portal.\n\n"
                "4. In view of the above clarification, the matter stands disposed of on CPGRAMS."
            ),
            "placeholders": "{registration_no}, {subject}",
            "is_default": False
        },
        {
            "template_code": "TMPL_OUT_OF_SCOPE",
            "title": "Outside Operational Mandate Advisory",
            "template_type": "out_of_scope",
            "concerned_division": "AI & Emerging Technologies Division",
            "template_body": (
                "With reference to CPGRAMS registration number {registration_no} regarding '{subject}'.\n\n"
                "2. The matter has been perused in the AI & Emerging Technologies Division, MeitY. "
                "It is observed that the subject matter and relief sought ({requested_relief}) fall outside the administrative mandate of this Ministry under the Allocation of Business Rules.\n\n"
                "3. As per DARPG guidelines, grievances involving sub-judice matters, RTI queries, or commercial disputes between private parties cannot be redressed under CPGRAMS. "
                "The applicant is advised to seek redressal through the competent regulatory or judicial forum.\n\n"
                "4. The grievance stands disposed of accordingly."
            ),
            "placeholders": "{registration_no}, {subject}, {requested_relief}",
            "is_default": False
        }
    ]

    for t in templates_data:
        db.add(ResponseTemplate(**t))

    # 3. Historical Precedent Library (Realistic Disposed MeitY Cases)
    precedents_data = [
        {
            "registration_no": "MEITY/E/2024/0018921",
            "subject": "Delay in announcement of subsidized GPU compute allocation for AI startups under IndiaAI Mission",
            "category": "IndiaAI Mission & Compute Capacity",
            "grievance_summary": "AI startup founder requesting expedited access to GPU clusters and clarity on compute voucher eligibility criteria under the IndiaAI Mission.",
            "full_grievance_text": (
                "Sir, our Bangalore-based deeptech startup is training an Indic language LLM. We applied for computing support under the announced IndiaAI Mission but have received no clarity on when the 10,000 GPUs will be available for allocation. Commercial cloud prices are unaffordable. Kindly expedite the subsidized compute portal and clarify eligibility."
            ),
            "final_reply": (
                "With reference to CPGRAMS registration number MEITY/E/2024/0018921. The matter was examined in the AI & Emerging Technologies Division, MeitY. "
                "It is informed that under the IndiaAI Compute Capacity pillar, the procurement tender for empanelment of GPU cloud service providers was floated in August 2024. "
                "Subsidized compute vouchers will be disbursed through the IndiaAI Portal (indiaai.gov.in) to DPIIT-recognized AI startups upon technical evaluation by the Expert Committee. "
                "The applicant is advised to register on the portal and monitor official announcements. The grievance stands disposed of."
            ),
            "disposal_date": date(2024, 11, 14),
            "disposal_type": "Closed with reply",
            "department": "Ministry of Electronics and Information Technology",
            "division": "AI & Emerging Technologies Division",
            "policy_reference": "Cabinet approval of IndiaAI Mission (Cabinet Decision dated 07.03.2024; Allocation ₹10,372 Cr)",
            "status_tag": "confirmed_issued",
            "reuse_recommendation": "useful_precedent",
            "officer_notes": "Standard official position on IndiaAI GPU compute voucher rollout. Highly suitable for reuse.",
            "provenance": "CPGRAMS Official Export Q3-2024",
            "is_sample": True
        },
        {
            "registration_no": "MEITY/E/2024/0023419",
            "subject": "Deepfake video circulating on social media platform; failure of platform to take down within 24 hours",
            "category": "Deepfake & Synthetic Media",
            "grievance_summary": "Citizen complaining about non-consensual synthetic video altering their likeness on an intermediary platform and seeking regulatory enforcement.",
            "full_grievance_text": (
                "Respected Officers, a maliciously morphed video using my photographs has been uploaded on an online platform. Despite reporting to the platform's Grievance Officer on 12th October 2024, the video has not been deleted after 4 days. Kindly initiate action against the intermediary under IT Rules 2021 and direct immediate takedown."
            ),
            "final_reply": (
                "With reference to CPGRAMS registration MEITY/E/2024/0023419. The grievance has been examined. Under Rule 3(2)(b) of the Information Technology (Intermediary Guidelines and Digital Media Ethics Code) Rules, 2021, intermediaries are legally mandated to remove content in the nature of impersonation, non-consensual nudity or sexual content within 24 hours of receipt of complaint. "
                "The applicant is informed that if the intermediary fails to comply, an appeal may be preferred before the Grievance Appellate Committee (GAC) at gac.gov.in. Furthermore, criminal complaints regarding impersonation and cyber stalking may be registered on the National Cyber Crime Reporting Portal (cybercrime.gov.in) for law enforcement action. With these directions, the grievance stands disposed of."
            ),
            "disposal_date": date(2024, 10, 22),
            "disposal_type": "Closed with reply",
            "department": "Ministry of Electronics and Information Technology",
            "division": "AI & Emerging Technologies Division",
            "policy_reference": "IT (Intermediary Guidelines and Digital Media Ethics Code) Rules, 2021 - Rule 3(2)(b) and MeitY Deepfake Advisory",
            "status_tag": "confirmed_issued",
            "reuse_recommendation": "useful_precedent",
            "officer_notes": "Accurate guidance on Grievance Appellate Committee (GAC) and cybercrime.gov.in escalation path.",
            "provenance": "CPGRAMS Official Export Q4-2024",
            "is_sample": True
        },
        {
            "registration_no": "MEITY/E/2024/0010503",
            "subject": "Request for exemption under Digital Personal Data Protection Act 2023 for AI model pre-training on public data",
            "category": "Data Protection & Privacy",
            "grievance_summary": "AI research group seeking blanket administrative exemption from data fiduciary obligations when training LLMs on publicly available web content.",
            "full_grievance_text": (
                "We represent an AI consortium requesting MeitY to issue a clarification/exemption notification under Section 17 of the DPDP Act 2023, permitting academic and startup researchers to train generative AI models on publicly accessible data without individual consent requirements."
            ),
            "final_reply": (
                "With reference to registration MEITY/E/2024/0010503. The representation regarding exemptions under the Digital Personal Data Protection (DPDP) Act, 2023 was examined. "
                "It is informed that the DPDP Act was enacted by Parliament and notified on 11th August 2023. Subordinate rules and exemption notifications under Section 17 are formulated through stakeholder consultations in accordance with statutory procedures. "
                "Representations of this nature are considered during the rule-making process and cannot be adjudicated as an individual grievance under CPGRAMS. The suggestion is noted for stakeholder input. Grievance stands disposed of."
            ),
            "disposal_date": date(2024, 8, 19),
            "disposal_type": "Closed with reply",
            "department": "Ministry of Electronics and Information Technology",
            "division": "AI & Emerging Technologies Division",
            "policy_reference": "Digital Personal Data Protection Act, 2023 (Act No. 22 of 2023)",
            "status_tag": "confirmed_issued",
            "reuse_recommendation": "useful_precedent",
            "officer_notes": "Good precedent for handling policy suggestions that cannot be resolved as individual public grievances.",
            "provenance": "CPGRAMS Official Export Q3-2024",
            "is_sample": True
        },
        {
            "registration_no": "MEITY/E/2023/0008742",
            "subject": "Seeking funding for AI autonomous drone navigation research from MeitY R&D Division",
            "category": "Startups & R&D Innovation",
            "grievance_summary": "University professor seeking direct sanction of research grant through CPGRAMS portal for defense AI drone navigation algorithm.",
            "full_grievance_text": (
                "Respected Secretary MeitY, our university has developed an AI drone navigation system for GPS-denied environments. We submitted an R&D proposal to MeitY 6 months ago. Kindly approve our grant of ₹85 Lakhs through this grievance ticket as project is delayed."
            ),
            "final_reply": (
                "With reference to CPGRAMS registration MEITY/E/2023/0008742. The grievance has been examined. Direct sanction or financial approval of scientific research grants cannot be processed through the CPGRAMS public grievance redressal channel. "
                "R&D proposals in IT and AI are evaluated under established schemes through peer-review Project Review and Steering Groups (PRSG) against official Calls for Proposals published on meity.gov.in. "
                "The applicant is requested to track proposal status directly with the concerned R&D in IT division via the official portal. Grievance stands disposed of."
            ),
            "disposal_date": date(2023, 9, 12),
            "disposal_type": "Outside Mandate",
            "department": "Ministry of Electronics and Information Technology",
            "division": "AI & Emerging Technologies Division",
            "policy_reference": "MeitY Terms and Conditions Governing Research Grants in IT",
            "status_tag": "confirmed_issued",
            "reuse_recommendation": "useful_precedent",
            "officer_notes": "Clear articulation that financial grant sanctioning is outside CPGRAMS mandate.",
            "provenance": "CPGRAMS Official Export Q3-2023",
            "is_sample": True
        },
        {
            "registration_no": "MEITY/E/2022/0004112",
            "subject": "Old 2022 Draft National AI Strategy policy implementation queries",
            "category": "AI Governance & Policy",
            "grievance_summary": "Citizen seeking information on superseded NITI Aayog AI framework committees.",
            "full_grievance_text": "Kindly provide update on the 2018 National AI Strategy working groups setup by NITI Aayog and MeitY.",
            "final_reply": "Disposed with reference to superseded 2018 draft committees.",
            "disposal_date": date(2022, 5, 10),
            "disposal_type": "Closed with reply",
            "department": "Ministry of Electronics and Information Technology",
            "division": "AI & Emerging Technologies Division",
            "policy_reference": "National Strategy for Artificial Intelligence (NITI Aayog, June 2018)",
            "status_tag": "status_unverified",
            "reuse_recommendation": "outdated",
            "officer_notes": "SUPERSEDED by IndiaAI Mission 2024. Do not reuse wording.",
            "provenance": "Historical Archive 2022",
            "is_sample": True
        }
    ]

    for p in precedents_data:
        db.add(HistoricalPrecedent(**p))

    # 4. Active Grievances (Demonstration Records with realistic MeitY AI workflows)
    today = date.today()
    active_grievances = [
        {
            "registration_no": "MEITY/E/2026/0003189",
            "subject": "Application for IndiaAI Mission GPU Compute Voucher pending technical evaluation for over 45 days",
            "date_received": today - timedelta(days=18),
            "applicant_name": "Arjun Varma",
            "applicant_masked": mask_applicant_name("Arjun Varma"),
            "applicant_contact": "arjun.varma@indictech.in | 9845012345",
            "category": "IndiaAI Mission & Compute Capacity",
            "concerned_ministry": "Ministry of Electronics and Information Technology",
            "concerned_division": "AI & Emerging Technologies Division",
            "grievance_text": (
                "Sir, our DPIIT-recognized AI startup IndicTech Solutions Pvt Ltd submitted an application for 64 NVIDIA H100 GPU compute allocation on the IndiaAI portal (Application Ref: IA-COMP-2026-0891) on 1st October 2026. "
                "As per guidelines, evaluation was to be completed within 21 days. We have not received any communication or compute credits. "
                "Our LLM training runs are stalled. We request urgent intervention to expedite evaluation and award compute vouchers."
            ),
            "requested_relief": "Expedited technical evaluation and release of IndiaAI GPU compute voucher for Application IA-COMP-2026-0891.",
            "status": "Under Examination",
            "workflow_state": "Awaiting review",
            "recommended_action": "Seek factual status from IndiaAI Independent Business Division / CDAC technical committee.",
            "priority": "Urgent",
            "target_disposal_date": today + timedelta(days=3),  # Approaching deadline (<5 days)
            "is_sample": True,
            "source_type": "synthetic_test"
        },
        {
            "registration_no": "MEITY/E/2026/0004210",
            "subject": "Deepfake audio clone of company CEO used in attempted financial fraud; intermediary inaction",
            "date_received": today - timedelta(days=6),
            "applicant_name": "Dr. Sneha Pillai",
            "applicant_masked": mask_applicant_name("Dr. Sneha Pillai"),
            "applicant_contact": "snehapillai@innovate.org | 9711098765",
            "category": "Deepfake & Synthetic Media",
            "concerned_ministry": "Ministry of Electronics and Information Technology",
            "concerned_division": "AI & Emerging Technologies Division",
            "grievance_text": (
                "An unauthorized AI-generated voice clone replicating the voice of our Managing Director was circulated via messaging channels and audio-sharing links to solicit unauthorized banking transfers from staff. "
                "We served takedown notices to the hosting intermediary on 12th October 2026 under IT Rules 2021, but no action has been taken. "
                "We request MeitY to initiate compliance proceedings against the platform and provide official guidance on enforcement."
            ),
            "requested_relief": "Regulatory intervention against non-compliant intermediary under IT Rules 2021 and advisory on legal recourse.",
            "status": "New",
            "workflow_state": "Retrieved",
            "recommended_action": "Examine under IT Rules 2021; advise filing on Cybercrime Portal and GAC appeal.",
            "priority": "High",
            "target_disposal_date": today + timedelta(days=15),
            "is_sample": True,
            "source_type": "synthetic_test"
        },
        {
            "registration_no": "MEITY/E/2026/0001945",
            "subject": "Request for information regarding minutes and members of MeitY Ethical AI Advisory Committee",
            "date_received": today - timedelta(days=25),
            "applicant_name": "Rohan Deshmukh",
            "applicant_masked": mask_applicant_name("Rohan Deshmukh"),
            "applicant_contact": "rohan.deshmukh@lawpolicy.in",
            "category": "AI Governance & Policy",
            "concerned_ministry": "Ministry of Electronics and Information Technology",
            "concerned_division": "AI & Emerging Technologies Division",
            "grievance_text": (
                "Under the provisions of transparency, kindly provide certified copies of all meeting minutes, member attendance, and internal file notings of the MeitY Ethical AI Advisory Committee meetings held in calendar year 2026."
            ),
            "requested_relief": "Supply of certified copies of committee meeting records and file notings.",
            "status": "Awaiting Inputs",
            "workflow_state": "Analysis complete",
            "recommended_action": "Dispose as outside CPGRAMS scope with advice to submit statutory application via rtionline.gov.in.",
            "priority": "Normal",
            "target_disposal_date": today - timedelta(days=4),  # Overdue case (>21 days)
            "is_sample": True,
            "source_type": "synthetic_test"
        },
        {
            "registration_no": "MEITY/E/2026/0005512",
            "subject": "Proposal for National Sanskrit Indic LLM Foundation Model collaboration with CDAC",
            "date_received": today - timedelta(days=4),
            "applicant_name": "Prof. K. Ramaswamy",
            "applicant_masked": mask_applicant_name("Prof. K. Ramaswamy"),
            "applicant_contact": "kramaswamy@iituniv.ac.in | 9444055555",
            "category": "Startups & R&D Innovation",
            "concerned_ministry": "Ministry of Electronics and Information Technology",
            "concerned_division": "AI & Emerging Technologies Division",
            "grievance_text": (
                "We submit a comprehensive academic proposal to build an open-source Sanskrit Indic LLM with 70 billion parameters in collaboration with CDAC. We seek technical sponsorship and compute credits under the IndiaAI Mission dataset initiative."
            ),
            "requested_relief": "Consideration of collaborative research proposal under IndiaAI datasets initiative.",
            "status": "Draft Prepared",
            "workflow_state": "Approved for submission",
            "recommended_action": "Issue policy explanation draft explaining IndiaAI Datasets Platform and EoI application channel.",
            "priority": "Normal",
            "target_disposal_date": today + timedelta(days=17),
            "is_sample": True,
            "source_type": "synthetic_test"
        }
    ]

    for g_data in active_grievances:
        g = Grievance(**g_data)
        db.add(g)
        db.flush()

        # Add corresponding automated analysis
        if g.registration_no == "MEITY/E/2026/0003189":
            analysis = GrievanceAnalysis(
                grievance_id=g.id,
                summary="AI startup IndicTech Solutions reporting 45-day delay in processing GPU compute voucher application IA-COMP-2026-0891 on IndiaAI portal.",
                main_allegations="• Undue administrative delay beyond 21-day norm.\n• Stalled LLM research due to lack of subsidized compute allocation.",
                exact_relief_requested="Expedited technical evaluation and release of IndiaAI GPU compute voucher for Application IA-COMP-2026-0891.",
                relevant_facts_dates="Referenced application: IA-COMP-2026-0891 | Date submitted: 01/10/2026 | Hardware requested: 64 NVIDIA H100 GPUs.",
                policy_jurisdiction_issues="IndiaAI Mission Compute Capacity Pillar guidelines; eligibility limited to DPIIT-recognized startups and academic bodies.",
                submission_type="Public Grievance",
                concerned_entity="AI & Emerging Technologies Division (IndiaAI IBD)",
                recommended_next_action="Call for factual inputs from IndiaAI Compute Evaluation Committee / CDAC regarding Application IA-COMP-2026-0891.",
                confidence_level="High",
                confidence_score=0.92,
                missing_info_verification="Application reference cited; verify registration status on internal IndiaAI portal dashboard.",
                requires_senior_review=False
            )
            db.add(analysis)

            # Add correspondence tracking record
            corr = Correspondence(
                grievance_id=g.id,
                reference_no="MeitY/AI/2026/INP-089",
                recipient_office="IndiaAI Independent Business Division / C-DAC",
                date_sent=today - timedelta(days=5),
                subject="Factual report requested: IndiaAI Compute Application IA-COMP-2026-0891 (M/s IndicTech Solutions)",
                target_due_date=today + timedelta(days=2),
                status="Sent",
                notes="U.O. note issued to Director (IndiaAI) seeking evaluation timeline."
            )
            db.add(corr)

        elif g.registration_no == "MEITY/E/2026/0005512":
            draft = ReplyDraft(
                grievance_id=g.id,
                version_number=1,
                draft_type="policy_explanation",
                template_used="TMPL_INDIAAI_COMPUTE",
                original_draft_text=(
                    f"With reference to CPGRAMS registration number {g.registration_no} regarding '{g.subject}'.\n\n"
                    "2. The representation regarding collaborative Sanskrit Indic LLM development has been examined in the AI & Emerging Technologies Division, MeitY.\n\n"
                    "3. Under the IndiaAI Mission, the 'IndiaAI Datasets Platform' and 'IndiaAI Applications Development Initiative' periodically invite collaborative proposals from academic institutions through competitive calls. "
                    "Academic researchers are advised to submit formal proposals against the upcoming Indic Foundation Model challenge on the official portal (indiaai.gov.in).\n\n"
                    "4. The suggestion has been noted for administrative consideration. The grievance stands disposed of on the CPGRAMS portal."
                ),
                current_draft_text=(
                    f"With reference to CPGRAMS registration number {g.registration_no} regarding '{g.subject}'.\n\n"
                    "2. The representation regarding collaborative Sanskrit Indic LLM development has been examined in the AI & Emerging Technologies Division, MeitY.\n\n"
                    "3. Under the IndiaAI Mission, the 'IndiaAI Datasets Platform' and 'IndiaAI Applications Development Initiative' periodically invite collaborative proposals from academic institutions through competitive calls. "
                    "Academic researchers are advised to submit formal proposals against the upcoming Indic Foundation Model challenge on the official portal (indiaai.gov.in).\n\n"
                    "4. The suggestion has been noted for administrative consideration. The grievance stands disposed of on the CPGRAMS portal."
                ),
                approval_status="draft",
                compliance_notes="Draft complies with official policy guidance conventions."
            )
            db.add(draft)

    db.commit()
