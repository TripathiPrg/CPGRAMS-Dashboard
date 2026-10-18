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
| **D. Grievance Register** | Searchable table with filtering by status, category, priority, and sample tag. Deadline countdown badges (<5 days approaching, overdue), PII privacy toggle, and dedicated case workspaces. | **Implemented & Tested** |
| **E. Disposed Library** | Searchable knowledge base of historical disposed grievances and final responses. Filter by category and reuse tag (`useful_precedent`, `outdated`, `restricted`, `incorrect`). Officer annotation editor. | **Implemented & Tested** |
| **F. AI Grievance Analysis** | 12-point structured evaluation: Summary, allegations, exact relief, facts & dates, policy issues, submission type classification, routing recommendation, confidence score, and senior officer review alert. Manual correction modal. | **Implemented & Tested** |
| **G. Routing Assistant** | Configurable directory of MeitY divisions, external ministries (DoT, ISM, CDSCO, RTI Cell), routing rules with keyword triggers, recommended actions, and explanations. Editable without code changes. | **Implemented & Tested** |
| **H. Reply Drafting Studio** | MeitY official drafting workspace: standard CPGRAMS disposal, out-of-scope advisory, Rule 6 transfer intimation, call for inputs (U.O. note), and policy explanation. Rich text editor, side-by-side HTML diff table, compliance checker, and DOCX/TXT export. | **Implemented & Tested** |
| **I. Precedent-Assisted Drafting** | Automatically executes TF-IDF semantic cosine similarity search for every case, identifies conceptual overlap, pinpoints differences, flags outdated clauses, and synthesizes precedents into the draft. | **Implemented & Tested** |
| **J. Input Tracker** | Master tracking register for inter-divisional inquiries (C-DAC, NIC, Cyber Laws Division). Logs reference numbers, due dates, follow-up reminder history, and response summaries. | **Implemented & Tested** |
| **K. Reports & Analytics** | Pending-case ageing breakdown (0-7, 8-15, 16-30, >30 days), category distribution, precedent reuse metrics, and one-click export of full register to Excel (`.xlsx`) and CSV. | **Implemented & Tested** |
| **L. Settings & Security** | Database backup & restore (online SQLite snapshots with integrity validation and safety copies), security audit trail explorer, and system diagnostics. | **Implemented & Tested** |

---

## 5. Security & Privacy Architecture

### Data Privacy & Local Storage
- All database records, uploaded documents, generated drafts, and backups are stored locally in the application's `data/` folder.
- **Zero Cloud Calls**: No external AI APIs, advertising scripts, or third-party telemetry.
- **PII Protection**: Applicant names and contact details (email/phone) are masked by default (`R**** S****`, `******3210`) in all table views and dashboard widgets. An explicit officer toggle allows unmasking when required for case examination.

### Network Controls
- Application server strictly binds to `127.0.0.1:8000`.
- Does not expose ports to public or local networks.
- Outbound network requests are blocked in local-only mode.
- Security headers enforced: `X-Content-Type-Options: nosniff`, `X-Frame-Options: SAMEORIGIN`, `X-XSS-Protection: 1; mode=block`, `Referrer-Policy: no-referrer`.

### Password & Credential Policy
- **The CPGRAMS officer password is never requested, read, or stored.**
- The browser assistant lets the officer authenticate directly on `https://pgportal.gov.in/CPGOFFICE/`.
- Audit logs sanitize any sensitive keywords (`password`, `token`, `otp`, `cookie`) before recording.

### Human Approval & Operational Safeguards
- The dashboard is an assistant, not an autonomous officer.
- **Explicit confirmation** is required before marking drafts approved, deleting records, or restoring backups.
- No disposal or transfer actions are executed on the live CPGRAMS portal.

---

## 6. Installation & Launch Instructions (Windows)

### Prerequisites
- Windows 10 or 11 (64-bit)
- Python 3.11+ installed (already configured on this machine at `C:\Users\Hp\AppData\Local\Programs\Python\Python311\python.exe`)
- Google Chrome or Microsoft Edge installed

### Quick Start (One-Click)
Double-click either launcher script in the project root:
- `run_workbench.bat` (Standard Command Prompt launcher)
- `run_workbench.ps1` (PowerShell launcher)

### Manual Command-Line Launch
```powershell
cd C:\Users\Hp\.gemini\antigravity\scratch\cpgrams_workbench
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```
Open your browser and navigate to:
```
http://127.0.0.1:8000
```

---

## 7. Running the Automated Test Suite

The project includes 24 automated unit and integration tests covering database persistence, document parsing, semantic search, AI analysis, drafting compliance, security boundaries, and backup/restore.

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

============================= 24 passed in 2.95s ==============================
```

---

## 8. Backup and Restore Procedures

### Creating an Instant Backup
1. Navigate to **Settings & Audit** module in the sidebar.
2. In the "Local Database Backup & Restore" card, click **Create Instant Snapshot**.
3. A timestamped snapshot is created in `data/backups/cpgrams_backup_YYYYMMDD_HHMMSS.db`.

### Restoring from a Snapshot
1. Select the desired snapshot from the backup list in **Settings & Audit**.
2. Click **Restore Snapshot**.
3. The system automatically performs `PRAGMA integrity_check` on the backup file.
4. If integrity passes, a pre-restore safety copy (`pre_restore_safety_*.db`) is created before replacing the active database, preventing data loss in the event of an interruption.

---

## 9. Status of Features: Verified vs Portal-Dependent

### Fully Functional & Verified
1. Complete local web workbench running on `127.0.0.1:8000`.
2. Multi-format intake (PDF, DOCX, TXT, Excel/CSV) with OCR detection and entity extraction.
3. Searchable Grievance Register with sorting, multi-criteria filtering, and deadline norms.
4. Historical Disposed Grievance Library with full-text and local TF-IDF semantic vector search.
5. 12-point structured AI grievance analysis with manual correction capabilities.
6. Departmental Routing Assistant with configurable directory and rules.
7. Official Reply Drafting Studio with precedent synthesis, side-by-side diffing, drafting compliance checks, and formal GoI-layout DOCX/TXT export.
8. Departmental Correspondence & Input Tracker with reminder logging.
9. Operational Analytics & Ageing breakdown with Excel/CSV export.
10. Database Backup & Restore with verified integrity checks.
11. Security Audit Trail recording all operational events.
12. PII masking and unmasking toggles.

### Features Dependent on Live Officer Portal Authentication
1. **Live Browser Assistant Session**: Depends on the officer launching the session and entering valid credentials, CAPTCHA, or Parichay OTP.
2. **Screen Inspection & Record Retrieval**: Only functions when the officer has authenticated and navigated to a visible table on the Operational Desk or Search page.
3. **Portal-Side Disposal**: Disposing, forwarding, or issuing replies on `pgportal.gov.in` must be performed directly by the officer on the portal; the workbench does not alter portal records.
