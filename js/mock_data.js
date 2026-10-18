/**
 * Static Demonstration Mock Store for GitHub Pages Hosting
 * Provides full interactive fallback when backend is not running on localhost.
 */

const MockStore = window.MockStore = {
  isStaticMode: window.location.hostname.includes("github.io") || window.location.protocol === "file:",

  stats: {
    total_grievances: 4,
    new_grievances: 1,
    pending_grievances: 4,
    disposed_grievances: 0,
    awaiting_inputs: 1,
    drafts_awaiting_review: 1,
    approaching_deadlines: 1,
    urgent_attention: 2,
    sample_records_count: 4,
    real_records_count: 0,
    recent_activities: [
      {
        timestamp: new Date().toISOString(),
        event_type: "RECORD_IMPORT",
        entity_type: "Grievance",
        details: "Synthesized 4 realistic test grievances for AI & Emerging Technologies Division.",
        actor: "Authorized Officer (MeitY AI & ET)"
      },
      {
        timestamp: new Date(Date.now() - 3600000).toISOString(),
        event_type: "DRAFT_GENERATED",
        entity_type: "Draft",
        details: "Generated official policy explanation draft for Indic LLM proposal MEITY/E/2026/0005512.",
        actor: "Authorized Officer (MeitY AI & ET)"
      }
    ]
  },

  grievances: [
    {
      id: 1,
      registration_no: "MEITY/E/2026/0003189",
      subject: "Application for IndiaAI Mission GPU Compute Voucher pending technical evaluation for over 45 days",
      date_received: "2026-10-01",
      applicant_name: "Arjun Varma",
      applicant_masked: "A**** V****",
      applicant_contact: "arjun.varma@indictech.in | 9845012345",
      category: "IndiaAI Mission & Compute Capacity",
      concerned_ministry: "Ministry of Electronics and Information Technology",
      concerned_division: "AI & Emerging Technologies Division",
      grievance_text: "Sir, our DPIIT-recognized AI startup IndicTech Solutions Pvt Ltd submitted an application for 64 NVIDIA H100 GPU compute allocation on the IndiaAI portal (Application Ref: IA-COMP-2026-0891) on 1st October 2026. As per guidelines, evaluation was to be completed within 21 days. We have not received any communication or compute credits. Our LLM training runs are stalled. We request urgent intervention to expedite evaluation and award compute vouchers.",
      requested_relief: "Expedited technical evaluation and release of IndiaAI GPU compute voucher for Application IA-COMP-2026-0891.",
      status: "Under Examination",
      workflow_state: "Awaiting review",
      recommended_action: "Seek factual status from IndiaAI Independent Business Division / CDAC technical committee.",
      priority: "Urgent",
      target_disposal_date: "2026-10-22",
      days_remaining: 3,
      deadline_status: "APPROACHING",
      is_sample: true,
      source_type: "synthetic_test"
    },
    {
      id: 2,
      registration_no: "MEITY/E/2026/0004210",
      subject: "Deepfake audio clone of company CEO used in attempted financial fraud; intermediary inaction",
      date_received: "2026-10-12",
      applicant_name: "Dr. Sneha Pillai",
      applicant_masked: "D**** P****",
      applicant_contact: "snehapillai@innovate.org | 9711098765",
      category: "Deepfake & Synthetic Media",
      concerned_ministry: "Ministry of Electronics and Information Technology",
      concerned_division: "AI & Emerging Technologies Division",
      grievance_text: "An unauthorized AI-generated voice clone replicating the voice of our Managing Director was circulated via messaging channels and audio-sharing links to solicit unauthorized banking transfers from staff. We served takedown notices to the hosting intermediary on 12th October 2026 under IT Rules 2021, but no action has been taken. We request MeitY to initiate compliance proceedings against the platform and provide official guidance on enforcement.",
      requested_relief: "Regulatory intervention against non-compliant intermediary under IT Rules 2021 and advisory on legal recourse.",
      status: "New",
      workflow_state: "Retrieved",
      recommended_action: "Examine under IT Rules 2021; advise filing on Cybercrime Portal and GAC appeal.",
      priority: "High",
      target_disposal_date: "2026-11-02",
      days_remaining: 15,
      deadline_status: "NORMAL",
      is_sample: true,
      source_type: "synthetic_test"
    },
    {
      id: 3,
      registration_no: "MEITY/E/2026/0001945",
      subject: "Request for information regarding minutes and members of MeitY Ethical AI Advisory Committee",
      date_received: "2026-09-23",
      applicant_name: "Rohan Deshmukh",
      applicant_masked: "R**** D****",
      applicant_contact: "rohan.deshmukh@lawpolicy.in",
      category: "AI Governance & Policy",
      concerned_ministry: "Ministry of Electronics and Information Technology",
      concerned_division: "AI & Emerging Technologies Division",
      grievance_text: "Under the provisions of transparency, kindly provide certified copies of all meeting minutes, member attendance, and internal file notings of the MeitY Ethical AI Advisory Committee meetings held in calendar year 2026.",
      requested_relief: "Supply of certified copies of committee meeting records and file notings.",
      status: "Awaiting Inputs",
      workflow_state: "Analysis complete",
      recommended_action: "Dispose as outside CPGRAMS scope with advice to submit statutory application via rtionline.gov.in.",
      priority: "Normal",
      target_disposal_date: "2026-10-14",
      days_remaining: -4,
      deadline_status: "OVERDUE",
      is_sample: true,
      source_type: "synthetic_test"
    },
    {
      id: 4,
      registration_no: "MEITY/E/2026/0005512",
      subject: "Proposal for National Sanskrit Indic LLM Foundation Model collaboration with CDAC",
      date_received: "2026-10-14",
      applicant_name: "Prof. K. Ramaswamy",
      applicant_masked: "P**** R****",
      applicant_contact: "kramaswamy@iituniv.ac.in | 9444055555",
      category: "Startups & R&D Innovation",
      concerned_ministry: "Ministry of Electronics and Information Technology",
      concerned_division: "AI & Emerging Technologies Division",
      grievance_text: "We submit a comprehensive academic proposal to build an open-source Sanskrit Indic LLM with 70 billion parameters in collaboration with CDAC. We seek technical sponsorship and compute credits under the IndiaAI Mission dataset initiative.",
      requested_relief: "Consideration of collaborative research proposal under IndiaAI datasets initiative.",
      status: "Draft Prepared",
      workflow_state: "Approved for submission",
      recommended_action: "Issue policy explanation draft explaining IndiaAI Datasets Platform and EoI application channel.",
      priority: "Normal",
      target_disposal_date: "2026-11-04",
      days_remaining: 17,
      deadline_status: "NORMAL",
      is_sample: true,
      source_type: "synthetic_test"
    }
  ],

  precedents: [
    {
      id: 1,
      registration_no: "MEITY/E/2024/0018921",
      subject: "Delay in announcement of subsidized GPU compute allocation for AI startups under IndiaAI Mission",
      category: "IndiaAI Mission & Compute Capacity",
      grievance_summary: "AI startup founder requesting expedited access to GPU clusters and clarity on compute voucher eligibility criteria under the IndiaAI Mission.",
      full_grievance_text: "Sir, our Bangalore-based deeptech startup is training an Indic language LLM. We applied for computing support under the announced IndiaAI Mission but have received no clarity on when the 10,000 GPUs will be available for allocation. Commercial cloud prices are unaffordable. Kindly expedite the subsidized compute portal and clarify eligibility.",
      final_reply: "With reference to CPGRAMS registration number MEITY/E/2024/0018921. The matter was examined in the AI & Emerging Technologies Division, MeitY. It is informed that under the IndiaAI Compute Capacity pillar, the procurement tender for empanelment of GPU cloud service providers was floated in August 2024. Subsidized compute vouchers will be disbursed through the IndiaAI Portal (indiaai.gov.in) to DPIIT-recognized AI startups upon technical evaluation by the Expert Committee. The applicant is advised to register on the portal and monitor official announcements. The grievance stands disposed of.",
      disposal_date: "2024-11-14",
      disposal_type: "Closed with reply",
      department: "Ministry of Electronics and Information Technology",
      division: "AI & Emerging Technologies Division",
      policy_reference: "Cabinet approval of IndiaAI Mission (Cabinet Decision dated 07.03.2024; Allocation ₹10,372 Cr)",
      status_tag: "confirmed_issued",
      reuse_recommendation: "useful_precedent",
      provenance: "CPGRAMS Official Export Q3-2024"
    },
    {
      id: 2,
      registration_no: "MEITY/E/2024/0023419",
      subject: "Deepfake video circulating on social media platform; failure of platform to take down within 24 hours",
      category: "Deepfake & Synthetic Media",
      grievance_summary: "Citizen complaining about non-consensual synthetic video altering their likeness on an intermediary platform and seeking regulatory enforcement.",
      full_grievance_text: "Respected Officers, a maliciously morphed video using my photographs has been uploaded on an online platform. Despite reporting to the platform's Grievance Officer on 12th October 2024, the video has not been deleted after 4 days. Kindly initiate action against the intermediary under IT Rules 2021 and direct immediate takedown.",
      final_reply: "With reference to CPGRAMS registration MEITY/E/2024/0023419. The grievance has been examined. Under Rule 3(2)(b) of the Information Technology (Intermediary Guidelines and Digital Media Ethics Code) Rules, 2021, intermediaries are legally mandated to remove content in the nature of impersonation, non-consensual nudity or sexual content within 24 hours of receipt of complaint. The applicant is informed that if the intermediary fails to comply, an appeal may be preferred before the Grievance Appellate Committee (GAC) at gac.gov.in. Furthermore, criminal complaints regarding impersonation and cyber stalking may be registered on the National Cyber Crime Reporting Portal (cybercrime.gov.in) for law enforcement action. With these directions, the grievance stands disposed of.",
      disposal_date: "2024-10-22",
      disposal_type: "Closed with reply",
      department: "Ministry of Electronics and Information Technology",
      division: "AI & Emerging Technologies Division",
      policy_reference: "IT (Intermediary Guidelines and Digital Media Ethics Code) Rules, 2021 - Rule 3(2)(b) and MeitY Deepfake Advisory",
      status_tag: "confirmed_issued",
      reuse_recommendation: "useful_precedent",
      provenance: "CPGRAMS Official Export Q4-2024"
    }
  ],

  routingRules: [
    {
      id: 1,
      rule_name: "IndiaAI Mission & Compute Infrastructure",
      keyword_triggers: "indiaai, gpu, compute capacity, supercomputer, cluster",
      target_division: "AI & Emerging Technologies Division",
      recommended_action: "Examine grievance in division; provide status of IndiaAI compute allocation portal.",
      explanation: "Compute allocation and GPU subsidies fall squarely within the mandate of the AI & Emerging Technologies Division.",
      is_active: true
    },
    {
      id: 2,
      rule_name: "Deepfake & Synthetic Media Grievance",
      keyword_triggers: "deepfake, synthetic media, face swap, voice clone, impersonation",
      target_division: "AI & Emerging Technologies Division / Cyber Laws Division",
      recommended_action: "Verify intermediary takedown compliance under IT Rules 2021; advise cyber crime reporting portal.",
      explanation: "Content removal falls under Rule 3(1)(b) of IT Rules 2021. Criminal reporting pertains to National Cyber Crime Portal.",
      is_active: true
    }
  ]
};
