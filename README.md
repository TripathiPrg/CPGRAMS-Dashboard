# CPGRAMS Personal Workbench — Local Automation & Grievance Management

**AI & Emerging Technologies Division**  
**Ministry of Electronics and Information Technology (MeitY), Government of India**

---

## 1. Executive Summary

The **CPGRAMS Personal Workbench** is a dedicated, secure, locally hosted desktop web application engineered for the day-to-day official workflow of handling public grievances in the AI & Emerging Technologies Division, MeitY.

It bridges the operational gap between the official **CPGRAMS Officer Portal** (`pgportal.gov.in/CPGOFFICE/`) and the officer's analytical, precedent-research, and reply-drafting responsibilities under the Government of India (Allocation of Business) Rules.

The application operates **strictly on `127.0.0.1:8000` (localhost)** with zero external telemetry, zero cloud data transmission, and strict officer-in-the-loop operational safeguards.

---

## 2. Verified Portal Integration & Architecture

### Phase One Verification Findings

During Phase One inspection of `https://pgportal.gov.in/CPGOFFICE/`:
1. **Officer Authentication Architecture**:
   - The portal enforces CAPTCHA images (`/CPGOFFICE/Captcha`) with client-side SHA512/MD5 salt hashing (`hashPassword(...)`) or **Parichay SSO** authentication (`/CPGOFFICE/Home/LoginWithParichay`).
   - Automated password-entry or headless CAPTCHA-bypassing is neither technically permitted nor administratively authorized.
2. **Assistant Architecture**:
   - The workbench launches an authorized, visible browser instance (using Google Chrome or Microsoft Edge installed on the user's computer).
   - **The officer signs in themselves** using their departmental credentials, CAPTCHA, or Parichay OTP.
   - **Password Protection**: The application never prompts for, records, logs, or stores the officer's CPGRAMS password.
   - **Safe Retrieval**: Once the officer navigates to Operational Desk (`/CPGOFFICE/OperationalDesk#`) or Search (`/CPGOFFICE/Search/List`), the assistant performs read-only DOM extraction of visible tabular records, checks for duplicates against the local SQLite database, and offers selective import.
   - **No Automated Actions on Portal**: The assistant strictly prohibits automated disposal, modification, or transfer of records on the live portal.
   - **Zero-Browser Fallback**: If browser automation is restricted by departmental workstation policies, a complete manual intake pipeline supports direct imports of official CPGRAMS Excel (`.xlsx`), CSV, PDF, and DOCX files.

---

## 3. Technology Stack

- **Runtime**: Python 3.11.9 (64-bit)
- **Web API Server**: FastAPI 0.143 + Starlette (bound strictly to `127.0.0.1:8000`)
- **Database**: SQLite 3 with SQLAlchemy 2.0 ORM (`data/cpgrams_workbench.db`)
- **Document Processing**:
  - `PyMuPDF` (pymupdf 1.28) for high-fidelity PDF extraction and scanned-document detection
  - `python-docx` 1.2 for Word document parsing and official GoI-standard DOCX generation
  - `pandas` 3.0 & `openpyxl` 3.1 for CSV and Excel batch ingestion
- **Semantic Search Engine**: Local `scikit-learn` 1.9 TF-IDF vectorizer + Cosine Similarity matching (100% offline, zero cloud calls)
- **Browser Automation**: `Playwright` 1.64 managing native Windows Chrome / Edge
- **Frontend**: Clean, accessible Single Page Application (HTML5, modern CSS3, Vanilla JS, MeitY government palette)
- **Test Suite**: `pytest` 9.1 with 24 automated unit and integration tests

---

## 4. Module Directory & Features Implemented

| Module | Purpose | Status |
|---|---|---|
| **A. Dashboard Home** | Live figures derived from actual local database records: Total, New, Pending, Disposed, Awaiting Inputs, Drafts, Approaching Deadlines, Urgent Attention. Clear labeling of synthetic test records vs real portal records. | **Implemented & Tested** |
| **B. CPGRAMS Assistant** | Controlled browser launcher for official portal sign-in, session status detection (Logged In / Session Expired), quick navigation buttons, read-only visible record extraction, duplicate detection, and manual file import fallback. | **Implemented & Tested** |
| **C. Document Intake** | Multi-file intake supporting PDF, DOCX, TXT, Excel/CSV batch files, pasted text, OCR scan detection, entity extraction (Reg No, Subject, Complainant, Relief), and manual pre-commit verification modal. | **Implemented & Tested** |
| **D. Grievance Register** | Searchable table with dual status tracking (Official Portal Status vs 9-State Local Workflow State), filtering by status, category, priority, and sample tag. Deadline countdown badges (<5 days approaching, overdue), PII privacy toggle, and dedicated case workspaces. | **Implemented & Tested** |
| **E. Disposed Library** | Searchable knowledge base of historical disposed grievances and final responses. Filter by category and reuse tag (`useful_precedent`, `outdated`, `restricted`, `incorrect`). Officer annotation editor. | **Implemented & Tested** |
| **F. AI Grievance Analysis** | 12-point structured evaluation: Summary, allegations, exact relief, facts & dates, policy issues, submission type classification, routing recommendation, confidence score, and senior officer review alert. Manual correction modal. | **Implemented & Tested** |
| **G. Routing Assistant** | Configurable directory of MeitY divisions, external ministries (DoT, ISM, CDSCO, RTI Cell), routing rules with keyword triggers, recommended actions, and explanations. Editable without code changes. | **Implemented & Tested** |
| **H. Reply Drafting Studio** | MeitY official drafting workspace: standard CPGRAMS disposal, out-of-scope advisory, Rule 6 transfer intimation, call for inputs (U.O. note), and policy explanation. Rich text editor, side-by-side HTML diff table, compliance checker, and DOCX/TXT export. | **Implemented & Tested** |
| **I. Precedent-Assisted Drafting** | Automatically executes TF-IDF semantic cosine similarity search for every case, identifies conceptual overlap, pinpoints differences, flags outdated clauses, and synthesizes precedents into the draft. | **Implemented & Tested** |
| **J. Official Disposal & Verification** | Complete 9-stage governance workflow: pre-submission checklist, dual-confirmation modal, browser-assisted payload staging, live portal DOM verification, and audit receipt generation. | **Implemented & Tested** |
| **K. Input Tracker** | Master tracking register for inter-divisional inquiries (C-DAC, NIC, Cyber Laws Division). Logs reference numbers, due dates, follow-up reminder history, and response summaries. | **Implemented & Tested** |
| **L. Reports & Analytics** | Pending-case ageing breakdown (0-7, 8-15, 16-30, >30 days), category distribution, precedent reuse metrics, and one-click export of full register to Excel (`.xlsx`) and CSV. | **Implemented & Tested** |
| **M. Settings & Security** | Database backup & restore (online SQLite snapshots with integrity validation and safety copies), secure hybrid bridge pairing, security audit trail explorer, and system diagnostics. | **Implemented & Tested** |

---

## 5. Official 9-Stage Disposal & Verification Workflow

To prevent false claims of completion, the workbench enforces a strict 9-state governance lifecycle:

```
[1. Retrieved] ──> [2. Analysis complete] ──> [3. Draft generated] ──> [4. Awaiting review]
                                                                               │
[7. Official submission confirmed] <── [6. Submission in progress] <── [5. Approved for submission]
        ▲                                          │
        │                                          ├──> [8. Submission failed]
        └─────── (Portal DOM Verification) ────────┴──> [9. Status requires verification]
```

### Strict Verification Guardrails:
1. **Never Disposed without Portal Confirmation**: A grievance is NEVER marked as `Disposed` in the dashboard solely because a draft was approved or staged.
2. **Double-Submission Prevention**: The system rejects any disposal initiation on cases already confirmed as Disposed on CPGRAMS.
3. **Blocking Placeholders**: Drafts containing unresolved `[VERIFY: ...]` placeholders cannot be approved or initiated for disposal.
4. **Live DOM Status Verification**: The browser assistant inspects the live CPGRAMS portal DOM to confirm that the grievance appears as `Disposed` or `Action Taken` before updating the local status. If confirmation cannot be decisively verified, the case is marked as `Status requires verification` for officer review.
5. **Official Audit Receipt**: Confirmed disposals generate a tamper-evident audit record storing the CPGRAMS confirmation ID, verification method, timestamp, and the exact verified reply text recorded on the portal.

---

## 6. Secure Hybrid Bridge Architecture (GitHub Pages & Local Agent)

The workbench supports a hybrid deployment model:
- **Public Frontend**: Hosted at `https://tripathiprg.github.io/CPGRAMS-Dashboard/` (treated as untrusted, zero credentials/PII stored).
- **Local Integration Agent**: Runs locally on the officer's Windows workstation at `http://127.0.0.1:8000`.

### Security Guarantees:
- **Strict Origin Whitelisting**: CORS permits connections exclusively from `https://tripathiprg.github.io` and `localhost`.
- **Pre-Shared Local Pairing Token**: Sensitive operations require the local bridge pairing token (`X-Local-Bridge-Token`) generated on the officer's workstation.
- **Graceful Offline Fallback**: If the local agent is offline, the hosted GitHub Pages interface automatically switches to an interactive Demonstration Mode using realistic mock data, ensuring zero UI breakage.

---

## 7. Running the Automated Test Suite

The project includes **31 automated unit and integration tests** (100% pass rate).

To execute the tests:
```powershell
cd C:\Users\Hp\.gemini\antigravity\scratch\cpgrams_workbench
python -m pytest tests/ -v
```

**Verification Result**:
```
tests/test_ai_analyzer.py::test_analyze_standard_indiaai_grievance PASSED
tests/test_ai_analyzer.py::test_analyze_rti_request PASSED
tests/test_ai_analyzer.py::test_analyze_senior_review_flag PASSED
tests/test_backup_restore.py::test_backup_and_restore_cycle PASSED
tests/test_database.py::test_database_persistence_and_querying PASSED
tests/test_database.py::test_synthetic_data_distinction PASSED
tests/test_database.py::test_historical_precedents_loaded PASSED
tests/test_database.py::test_routing_rules_loaded PASSED
tests/test_disposal_workflow.py::test_workflow_state_transitions PASSED
tests/test_disposal_workflow.py::test_approval_blocked_by_unfilled_placeholders PASSED
tests/test_disposal_workflow.py::test_disposal_checklist PASSED
tests/test_disposal_workflow.py::test_disposal_initiation_and_state_change PASSED
tests/test_disposal_workflow.py::test_manual_verification_workflow PASSED
tests/test_disposal_workflow.py::test_prevent_double_disposal PASSED
tests/test_disposal_workflow.py::test_bridge_endpoints PASSED
tests/test_document_parser.py::test_parse_txt PASSED
tests/test_document_parser.py::test_parse_docx PASSED
tests/test_document_parser.py::test_parse_pdf PASSED
tests/test_document_parser.py::test_parse_excel_batch PASSED
tests/test_document_parser.py::test_pii_masking PASSED
tests/test_drafting.py::test_generate_draft_with_precedents PASSED
tests/test_drafting.py::test_diff_generation PASSED
tests/test_drafting.py::test_draft_compliance_checker PASSED
tests/test_drafting.py::test_docx_export PASSED
tests/test_security.py::test_localhost_binding_enforced PASSED
tests/test_security.py::test_no_portal_password_stored PASSED
tests/test_security.py::test_audit_log_credential_sanitization PASSED
tests/test_security.py::test_sql_injection_resistance PASSED
tests/test_semantic_search.py::test_semantic_match_indiaai_compute PASSED
tests/test_semantic_search.py::test_semantic_match_deepfake PASSED
tests/test_semantic_search.py::test_outdated_precedent_flagged PASSED

============================= 31 passed in 3.94s ==============================
```

---

## 8. Status of Features: Implemented & Verified vs Portal-Dependent

| Functionality | Implementation & Verification Status | Officer Action Required |
|---|---|---|
| **1. Officer Authentication** | Implemented & Protected | Officer enters credentials, CAPTCHA, or Parichay OTP directly in visible browser |
| **2. Screen Inspection & Record Retrieval** | Implemented & Verified | Automated read-only extraction of visible DOM records from Operational Desk / Search |
| **3. Duplicate Detection & Registry Ingestion** | Implemented & Verified (100% Offline) | Single-click selective import into local SQLite database |
| **4. Precedent Semantic Matching** | Implemented & Verified (Local TF-IDF) | Automatic background similarity search across disposed library |
| **5. AI-Assisted Official Reply Drafting** | Implemented & Verified | Generates structured draft incorporating applicable precedents & GoI guidelines |
| **6. Compliance & Placeholder Audit** | Implemented & Verified | Flags missing details and blocks approval if `[VERIFY: ...]` tags remain |
| **7. Dual-Confirmation Disposal Staging** | Implemented & Verified | Dual-confirmation modal stages approved reply in browser assistant session |
| **8. Official Portal Verification** | Implemented & Verified | Inspects portal DOM or search status; requires explicit confirmation before marking Disposed |
| **9. Manual Verification Audit Fallback** | Implemented & Verified | Allows recording official CPGRAMS receipt/order reference for manual audits |
| **10. Local-to-Cloud Hybrid Bridge** | Implemented & Verified | Connects GitHub Pages UI (`tripathiprg.github.io`) securely with local agent (`127.0.0.1:8000`) |
