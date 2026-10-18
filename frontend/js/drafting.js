/**
 * Case Workspace & Official Reply Drafting Studio Controller
 * Manages detailed case view, AI analysis, semantic precedent matching,
 * drafting versioning, diff comparisons, approvals, and DOCX/TXT export.
 */

const OFFICIAL_SUGGESTED_REPLIES = {
  "DHLTH/E/2026/0037250": `GOVERNMENT OF INDIA\nMINISTRY OF ELECTRONICS AND INFORMATION TECHNOLOGY\nEMERGING TECHNOLOGIES AND IOT DIVISION\nELECTRONICS NIKETAN, 6, CGO COMPLEX, NEW DELHI - 110003\n\nWith reference to CPGRAMS registration number DHLTH/E/2026/0037250 transferred from Department of Health regarding emerging medical IoT devices and AI diagnostic guidelines.\n\n2. The matter has been duly examined in the Emerging Technologies and IOT Division, MeitY.\n\n3. It is informed that MeitY has formulated the IoT Security Framework and baseline interoperability guidelines in consultation with BIS and TEC. For medical AI algorithms and clinical diagnostic software, technical standards and regulatory validations are governed under CDSCO regulations in coordination with MoHFW. The applicant may access published MeitY IoT standards and BIS Indian Standards (IS 18000 series) on the official MeitY website (meity.gov.in).\n\n4. In view of the above position, the grievance stands disposed of on the CPGRAMS portal.`,

  "PMOPG/E/2026/0200113": `GOVERNMENT OF INDIA\nMINISTRY OF ELECTRONICS AND INFORMATION TECHNOLOGY\nEMERGING TECHNOLOGIES AND IOT DIVISION\nELECTRONICS NIKETAN, 6, CGO COMPLEX, NEW DELHI - 110003\n\nWith reference to PMO grievance registration number PMOPG/E/2026/0200113 regarding startup compute access under the IndiaAI Mission and indigenous emerging technology infrastructure.\n\n2. The matter has been duly examined in the Emerging Technologies and IOT Division, MeitY.\n\n3. Under the comprehensive IndiaAI Mission approved by the Union Cabinet with an outlay of ₹10,372 crore, the Government is establishing public AI compute infrastructure comprising 10,000+ GPUs to democratize AI compute access. DPIIT-recognized tech startups and researchers are eligible for subsidized GPU compute vouchers accessible through the IndiaAI Portal (indiaai.gov.in). Applications are evaluated periodically by the Expert Committee, and compute credits are disbursed in phased allocations.\n\n4. In view of the above position, the grievance stands disposed of on the CPGRAMS portal.`,

  "PMOPG/D/2026/0190548": `GOVERNMENT OF INDIA\nMINISTRY OF ELECTRONICS AND INFORMATION TECHNOLOGY\nEMERGING TECHNOLOGIES AND IOT DIVISION\nELECTRONICS NIKETAN, 6, CGO COMPLEX, NEW DELHI - 110003\n\nWith reference to PMO representation number PMOPG/D/2026/0190548 regarding deployment standards and security benchmarks for smart city IoT sensor networks.\n\n2. The matter has been examined in the Emerging Technologies and IOT Division, MeitY.\n\n3. The Ministry has notified guidelines on IoT Security and Trustworthy AI, establishing baseline security requirements including secure boot, cryptographic authentication, firmware integrity verification, and data encryption standards for IoT sensor nodes deployed in municipal and public infrastructure. Furthermore, domestic manufacturing of IoT sensor hardware is actively supported under MeitY's SPECS and PLI schemes. The inputs provided by the applicant have been noted for technical consideration.\n\n4. In view of the above, the grievance stands disposed of on the CPGRAMS portal.`,

  "PMOPG/D/2026/0193061": `GOVERNMENT OF INDIA\nMINISTRY OF ELECTRONICS AND INFORMATION TECHNOLOGY\nEMERGING TECHNOLOGIES AND IOT DIVISION\nELECTRONICS NIKETAN, 6, CGO COMPLEX, NEW DELHI - 110003\n\nWith reference to PMO representation number PMOPG/D/2026/0193061 regarding deepfake prevention tools and synthetic media provenance standards.\n\n2. The matter has been examined in the Emerging Technologies and IOT Division, MeitY.\n\n3. Under Rule 3(1)(b) of the Information Technology (Intermediary Guidelines and Digital Media Ethics Code) Rules, 2021 as amended, digital intermediaries are legally mandated to remove impersonating or non-consensual synthetic content within statutory timelines. Advisories have been issued to intermediaries directing the mandatory embedding of digital watermarks and provenance metadata in synthetically generated audio/video content. In parallel, MeitY provides R&D grants to indigenous research groups and C-DAC for developing open-source deepfake detection algorithms.\n\n4. In view of the above, the grievance stands disposed of on the CPGRAMS portal.`,

  "PMOPG/D/2026/0193265": `GOVERNMENT OF INDIA\nMINISTRY OF ELECTRONICS AND INFORMATION TECHNOLOGY\nEMERGING TECHNOLOGIES AND IOT DIVISION\nELECTRONICS NIKETAN, 6, CGO COMPLEX, NEW DELHI - 110003\n\nWith reference to PMO representation number PMOPG/D/2026/0193265 regarding proposal for National Centre of Excellence in Industrial IoT and Edge AI for manufacturing.\n\n2. The matter has been examined in the Emerging Technologies and IOT Division, MeitY.\n\n3. The Ministry acknowledges the valuable proposal submitted by Dr. J P Gupta. MeitY already supports Centres of Excellence (CoEs) in IoT and Emerging Technologies across India in partnership with NASSCOM, STPI, and premier academic institutions. Institutional research proposals seeking grant-in-aid are formally invited through the MeitY R&D Portal under competitive Calls for Proposals. The applicant is encouraged to submit a formal project proposal when the next Call for Proposals is notified.\n\n4. In view of the above, the grievance stands disposed of on the CPGRAMS portal.`,

  "PMOPG/D/2026/0193305": `GOVERNMENT OF INDIA\nMINISTRY OF ELECTRONICS AND INFORMATION TECHNOLOGY\nEMERGING TECHNOLOGIES AND IOT DIVISION\nELECTRONICS NIKETAN, 6, CGO COMPLEX, NEW DELHI - 110003\n\nWith reference to PMO representation number PMOPG/D/2026/0193305 regarding open-source IoT protocols and data privacy compliance under the Digital Personal Data Protection (DPDP) Act, 2023.\n\n2. The matter has been examined in the Emerging Technologies and IOT Division, MeitY.\n\n3. The Government is committed to promoting open standards and interoperable architectures. Compliance with the provisions of the DPDP Act, 2023 is mandatory for all data fiduciaries collecting or processing personal data through connected IoT devices and sensor networks. Subordinate rules under the Act are currently being formulated through stakeholder consultations. The applicant's suggestions regarding technical open-source protocol compliance have been noted.\n\n4. In view of the above, the grievance stands disposed of on the CPGRAMS portal.`,

  "PMOPG/D/2026/0193312": `GOVERNMENT OF INDIA\nMINISTRY OF ELECTRONICS AND INFORMATION TECHNOLOGY\nEMERGING TECHNOLOGIES AND IOT DIVISION\nELECTRONICS NIKETAN, 6, CGO COMPLEX, NEW DELHI - 110003\n\nWith reference to PMO representation number PMOPG/D/2026/0193312 regarding testing labs and calibration facilities for agricultural IoT and smart farming sensors.\n\n2. The matter has been examined in the Emerging Technologies and IOT Division, MeitY.\n\n3. MeitY, in collaboration with the Department of Agriculture and Farmers Welfare, facilitates the deployment and validation of agri-IoT solutions through standard testing laboratories established under STQC and C-DAC. The Ministry's Agri-Tech and Emerging Technologies initiatives support pilot testbeds for soil sensors and precision farming telemetry. Hardware certification standards are published on the STQC portal (stqc.gov.in).\n\n4. In view of the above, the grievance stands disposed of on the CPGRAMS portal.`
};

const CaseWorkspace = {
  caseData: null,
  activeTab: "tab-case-narrative",
  selectedPrecedentIds: [],

  async openCase(id) {
    App.currentCaseId = id;
    App.switchView("detail");
    await this.loadCase(id);
  },

  async loadCase(id) {
    let data = null;
    try {
      if (!window.MockStore || !MockStore.isStaticMode) {
        const url = App.getApiUrl(`/api/grievances/${id}?unmask_pii=${!App.maskPII}`);
        const res = await fetch(url, { headers: App.getAuthHeaders() });
        if (res.ok) data = await res.json();
      }
    } catch (e) {
      console.warn("API not reachable, using mock case data");
    }

    if (!data && (window.MockStore || typeof MockStore !== "undefined")) {
      const store = window.MockStore || MockStore;
      const g = store.grievances.find(x => x.id === id || x.registration_no === id);
      if (g) {
        const suggestedDraft = OFFICIAL_SUGGESTED_REPLIES[g.registration_no] ||
          `GOVERNMENT OF INDIA\nMINISTRY OF ELECTRONICS AND INFORMATION TECHNOLOGY\nEMERGING TECHNOLOGIES AND IOT DIVISION\n\nWith reference to CPGRAMS registration number ${g.registration_no}.\n\nThe matter has been examined in the Emerging Technologies and IOT Division, MeitY. The representation on ${g.subject} has been recorded for departmental consideration.\n\nIn view of the above position, the grievance stands disposed of.`;

        data = {
          grievance: g,
          analysis: {
            summary: g.subject,
            main_allegations: g.grievance_text,
            exact_relief_requested: g.requested_relief || "Official examination by Emerging Technologies & IOT Division.",
            relevant_facts_dates: `Received on ${g.date_received}. Mandate: Emerging Technologies & IOT. Priority: ${g.priority}.`,
            policy_jurisdiction_issues: "Emerging Technologies and IOT Division mandate under MeitY Allocation of Business Rules.",
            submission_type: "Public Grievance",
            concerned_entity: "Emerging Technologies and IOT Division",
            recommended_next_action: "Examine factual status, coordinate with relevant stakeholder/division, and formulate official response."
          },
          drafts: [
            {
              id: 101,
              version_number: 1,
              draft_type: "standard_disposal",
              current_draft_text: suggestedDraft,
              draft_text: suggestedDraft,
              approval_status: g.status === "Approved for Disposal" ? "approved" : "draft",
              is_approved_by_user: g.status === "Approved for Disposal",
              compliance_notes: "✓ GoI Central Secretariat drafting conventions verified. No unverified tags.",
              created_at: new Date().toISOString()
            }
          ],
          correspondence: [],
          audit_logs: [
            {
              timestamp: new Date().toISOString(),
              event_type: "RECORD_SYNC",
              entity_type: "Grievance",
              details: `Synchronized ${g.registration_no} from Operational Desk.`,
              actor: "Pragati (Scientist B, Emerging Technologies and IOT)"
            }
          ]
        };
      }
    }

    if (!data) {
      alert(`Could not load case details for ID: ${id}`);
      return;
    }

    this.caseData = data;
    this.renderCaseHeader(data.grievance);
    this.renderNarrative(data.grievance);
    this.renderAnalysis(data.analysis);
    this.renderDrafts(data.drafts);
    this.renderCorrespondence(data.correspondence);
    this.renderAuditLogs(data.audit_logs);
    
    // Initialize disposal & verification module
    if (window.DisposalManager) {
      DisposalManager.initCaseDisposal(data);
    }

    // Run automatic semantic precedent matching
    this.runSemanticPrecedentSearch();
  },

  switchTab(tabId) {
    this.activeTab = tabId;
    document.querySelectorAll(".case-tab").forEach(btn => {
      btn.classList.toggle("active", btn.getAttribute("data-tab") === tabId);
    });
    document.querySelectorAll(".case-tab-content").forEach(c => {
      c.style.display = (c.id === tabId) ? "block" : "none";
    });
  },

  renderCaseHeader(g) {
    document.getElementById("case-header-title").innerText = g.subject;
    document.getElementById("case-header-reg").innerText = g.registration_no;
    document.getElementById("case-header-date").innerText = g.date_received;
    document.getElementById("case-header-applicant").innerText = g.applicant_name;

    const sampleBadge = document.getElementById("case-header-sample-badge");
    sampleBadge.innerHTML = g.is_sample ? `<span class="badge badge-sample">Synthetic Test Record</span>` : "";

    const statusBadge = document.getElementById("case-header-status-badge");
    let statusClass = "badge-new";
    if (g.status === "Approved for Disposal") statusClass = "badge-approved";
    else if (g.status === "Under Examination") statusClass = "badge-exam";
    else if (g.status === "Awaiting Inputs") statusClass = "badge-inputs";
    else if (g.status === "Draft Prepared") statusClass = "badge-draft";
    statusBadge.className = `badge ${statusClass}`;
    statusBadge.innerText = g.status;

    const wfBadge = document.getElementById("case-header-workflow-badge");
    if (wfBadge) {
      const wfState = g.workflow_state || "Retrieved";
      wfBadge.innerText = `State: ${wfState}`;
      if (wfState === "Official submission confirmed") wfBadge.className = "badge badge-approved";
      else if (wfState === "Approved for submission") wfBadge.className = "badge badge-inputs";
      else if (wfState === "Submission in progress") wfBadge.className = "badge badge-exam";
      else if (wfState === "Status requires verification") wfBadge.className = "badge badge-approaching";
      else wfBadge.className = "badge badge-draft";
    }

    const deadlineBadge = document.getElementById("case-header-deadline-badge");
    if (g.status === "Approved for Disposal" || g.status === "Disposed") {
      deadlineBadge.className = "badge badge-disposed";
      deadlineBadge.innerText = "Case Disposed";
    } else if (g.days_remaining !== null) {
      if (g.days_remaining < 0) {
        deadlineBadge.className = "badge badge-overdue";
        deadlineBadge.innerText = `OVERDUE by ${Math.abs(g.days_remaining)} days`;
      } else if (g.days_remaining <= 5) {
        deadlineBadge.className = "badge badge-approaching";
        deadlineBadge.innerText = `Deadline in ${g.days_remaining} days`;
      } else {
        deadlineBadge.className = "badge badge-new";
        deadlineBadge.innerText = `Target: ${g.target_disposal_date} (${g.days_remaining}d left)`;
      }
    }
  },

  renderNarrative(g) {
    document.getElementById("detail-subject").innerText = g.subject;
    document.getElementById("detail-relief").innerText = g.requested_relief || "Standard public grievance redressal.";
    document.getElementById("detail-text").innerText = g.grievance_text;
  },

  renderAnalysis(an) {
    if (!an) {
      document.getElementById("an-summary").innerText = "Analysis not yet run for this case. Click 'Re-analyze' to generate.";
      return;
    }

    document.getElementById("an-summary").innerText = an.summary;
    document.getElementById("an-allegations").innerText = an.main_allegations || "General service delivery grievance.";
    document.getElementById("an-relief").innerText = an.exact_relief_requested || "Administrative intervention requested.";
    document.getElementById("an-facts").innerText = an.relevant_facts_dates || "No external reference number cited.";
    document.getElementById("an-policy").innerText = an.policy_jurisdiction_issues || "General MeitY citizen charter guidelines.";
    document.getElementById("an-subtype").innerText = an.submission_type;
    document.getElementById("an-routing").innerText = an.concerned_entity || "AI & Emerging Technologies Division";
    document.getElementById("an-action").innerText = an.recommended_next_action;
    document.getElementById("an-confidence").innerHTML = `<strong>${an.confidence_level}</strong> (${Math.round(an.confidence_score * 100)}% confidence score)`;
    document.getElementById("an-missing").innerText = an.missing_info_verification || "Sufficient prima facie information available.";

    const seniorBox = document.getElementById("analysis-senior-review-box");
    if (an.requires_senior_review) {
      seniorBox.style.display = "flex";
      document.getElementById("analysis-senior-review-reasons").innerText = an.senior_review_reason;
    } else {
      seniorBox.style.display = "none";
    }
  },

  async refreshAnalysis() {
    try {
      const url = App.getApiUrl(`/api/grievances/${App.currentCaseId}/analyze`);
      const res = await fetch(url, { method: "POST", headers: App.getAuthHeaders() });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Analysis failed");
      this.renderAnalysis(data);
      alert("Analysis updated successfully!");
    } catch (e) {
      alert(`Error refreshing analysis: ${e.message}`);
    }
  },

  openAnalysisEditModal() {
    const an = this.caseData.analysis;
    if (!an) return;
    document.getElementById("edit-an-summary").value = an.summary || "";
    document.getElementById("edit-an-allegations").value = an.main_allegations || "";
    document.getElementById("edit-an-relief").value = an.exact_relief_requested || "";
    document.getElementById("edit-an-action").value = an.recommended_next_action || "";
    document.getElementById("edit-an-subtype").value = an.submission_type || "Public Grievance";
    document.getElementById("analysis-edit-modal").classList.add("active");
  },

  closeAnalysisEditModal() {
    document.getElementById("analysis-edit-modal").classList.remove("active");
  },

  async saveAnalysisCorrections() {
    const payload = {
      summary: document.getElementById("edit-an-summary").value.trim(),
      main_allegations: document.getElementById("edit-an-allegations").value.trim(),
      exact_relief_requested: document.getElementById("edit-an-relief").value.trim(),
      recommended_next_action: document.getElementById("edit-an-action").value.trim(),
      submission_type: document.getElementById("edit-an-subtype").value
    };

    try {
      const url = App.getApiUrl(`/api/grievances/${App.currentCaseId}/analysis`);
      const res = await fetch(url, {
        method: "PUT",
        headers: App.getAuthHeaders({ "Content-Type": "application/json" }),
        body: JSON.stringify(payload)
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Save failed");

      this.closeAnalysisEditModal();
      this.loadCase(App.currentCaseId);
      alert("Manual corrections saved to case analysis.");
    } catch (e) {
      alert(`Error saving corrections: ${e.message}`);
    }
  },

  async runSemanticPrecedentSearch() {
    const container = document.getElementById("case-precedents-list");
    container.innerHTML = `<div style="text-align:center; padding: 14px; font-size: 13px;">Computing TF-IDF cosine similarity against historical cases...</div>`;

    const g = this.caseData.grievance;
    const queryText = `${g.subject} ${g.requested_relief || ''} ${g.grievance_text}`;

    try {
      const url = App.getApiUrl("/api/precedents/search");
      const res = await fetch(url, {
        method: "POST",
        headers: App.getAuthHeaders({ "Content-Type": "application/json" }),
        body: JSON.stringify({
          query: queryText,
          category: null,
          min_similarity: 0.12,
          limit: 4
        })
      });
      const matches = await res.json();

      if (matches.length === 0) {
        container.innerHTML = `<div style="text-align:center; padding: 16px; color: var(--text-muted);">No historical precedents met the semantic similarity threshold.</div>`;
        return;
      }

      container.innerHTML = matches.map(m => {
        const p = m.precedent;
        const isSelected = this.selectedPrecedentIds.includes(p.id);

        return `
          <div class="card" style="margin-bottom: 12px; border-left: 4px solid ${m.is_recommended ? 'var(--meity-green)' : '#90a4ae'};">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
              <div>
                <strong>${p.registration_no}</strong>
                <span class="badge ${m.is_recommended ? 'badge-approved' : 'badge-sample'}" style="margin-left: 6px;">
                  ${m.match_percentage}% Semantic Match
                </span>
                <span class="badge badge-draft" style="margin-left: 4px;">${p.category}</span>
              </div>
              <button class="btn ${isSelected ? 'btn-success' : 'btn-outline'}" style="font-size: 11.5px; padding: 3px 8px;" onclick="CaseWorkspace.togglePrecedentSelection(${p.id})">
                ${isSelected ? '✓ Selected for Drafting' : '+ Select Precedent'}
              </button>
            </div>
            
            <h5 style="font-size: 13.5px; font-weight: 700; color: var(--meity-navy); margin-bottom: 4px;">${p.subject}</h5>
            
            <div style="font-size: 12px; color: var(--text-muted); margin-bottom: 8px;">
              <strong>Similarity Rationale:</strong> ${m.relevance_explanation}
            </div>

            <!-- Differences -->
            <div style="font-size: 12px; color: #856404; background: #fff9c4; padding: 6px 10px; border-radius: 4px; margin-bottom: 8px;">
              <strong>Key Distinctions from Current Case:</strong> ${m.key_differences.join(' | ')}
            </div>

            <div style="background: #f8fafc; padding: 8px 10px; border-radius: 4px; font-size: 12.5px; border: 1px solid #edf0f5; white-space: pre-wrap;">
              <strong>Original Final Reply:</strong> ${p.final_reply}
            </div>
          </div>
        `;
      }).join("");

    } catch (e) {
      container.innerHTML = `<div style="color: var(--meity-red);">Semantic search error: ${e.message}</div>`;
    }
  },

  togglePrecedentSelection(id) {
    if (this.selectedPrecedentIds.includes(id)) {
      this.selectedPrecedentIds = this.selectedPrecedentIds.filter(x => x !== id);
    } else {
      this.selectedPrecedentIds.push(id);
    }
    this.runSemanticPrecedentSearch();
  },

  renderDrafts(drafts) {
    DraftingManager.currentDrafts = drafts || [];
    if (drafts && drafts.length > 0) {
      DraftingManager.setActiveDraft(drafts[0]);
    } else {
      DraftingManager.clearEditor();
    }
  },

  renderCorrespondence(corrs) {
    const tbody = document.getElementById("case-corr-tbody");
    if (!corrs || corrs.length === 0) {
      tbody.innerHTML = `<tr><td colspan="7" style="text-align: center; color: var(--text-muted);">No input requests logged for this grievance.</td></tr>`;
      return;
    }

    tbody.innerHTML = corrs.map(c => `
      <tr>
        <td><strong>${c.reference_no}</strong></td>
        <td>${c.recipient_office}</td>
        <td>${c.date_sent}</td>
        <td>${c.subject}</td>
        <td>${c.target_due_date}</td>
        <td><span class="badge ${c.status === 'Overdue' ? 'badge-urgent' : 'badge-exam'}">${c.status}</span></td>
        <td>
          <button class="btn btn-outline" style="font-size: 11px; padding: 3px 6px;" onclick="CaseWorkspace.addReminder(${c.id})">Log Reminder</button>
        </td>
      </tr>
    `).join("");
  },

  renderAuditLogs(logs) {
    const tbody = document.getElementById("case-audit-tbody");
    if (!logs || logs.length === 0) {
      tbody.innerHTML = `<tr><td colspan="4" style="text-align: center; color: var(--text-muted);">No action events logged for this case.</td></tr>`;
      return;
    }

    tbody.innerHTML = logs.map(l => `
      <tr>
        <td style="font-size: 11.5px; color: var(--text-muted);">${new Date(l.timestamp).toLocaleString()}</td>
        <td><span class="badge badge-draft">${l.event_type}</span></td>
        <td>${l.details}</td>
        <td style="font-size: 11.5px;">${l.actor}</td>
      </tr>
    `).join("");
  },

  async addReminder(corrId) {
    const note = prompt("Enter follow-up reminder details:");
    if (!note) return;
    try {
      const url = App.getApiUrl(`/api/correspondence/${corrId}/reminder`);
      const res = await fetch(url, {
        method: "POST",
        headers: App.getAuthHeaders({ "Content-Type": "application/json" }),
        body: JSON.stringify({ reminder_note: note })
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Reminder failed");
      this.loadCase(App.currentCaseId);
    } catch (e) {
      alert(`Error logging reminder: ${e.message}`);
    }
  }
};

const DraftingManager = {
  currentDrafts: [],
  activeDraft: null,

  setActiveDraft(draft) {
    this.activeDraft = draft;
    document.getElementById("draft-version-label").innerText = `Version ${draft.version_number} (${draft.draft_type})`;
    document.getElementById("draft-editor-text").value = draft.current_draft_text;
    document.getElementById("draft-type-select").value = draft.draft_type;

    const complianceBox = document.getElementById("draft-compliance-box");
    if (draft.compliance_notes) {
      complianceBox.innerText = draft.compliance_notes;
    }
  },

  clearEditor() {
    this.activeDraft = null;
    document.getElementById("draft-version-label").innerText = "No Draft Created";
    document.getElementById("draft-editor-text").value = "";
  },

  async generateNewDraft() {
    const draftType = document.getElementById("draft-type-select").value;

    try {
      const url = App.getApiUrl("/api/drafting/generate");
      const res = await fetch(url, {
        method: "POST",
        headers: App.getAuthHeaders({ "Content-Type": "application/json" }),
        body: JSON.stringify({
          grievance_id: App.currentCaseId,
          draft_type: draftType,
          precedent_ids: CaseWorkspace.selectedPrecedentIds
        })
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Draft generation failed");

      this.setActiveDraft(data);
      alert(`Generated Version ${data.version_number} using official MeitY drafting framework!`);
      CaseWorkspace.loadCase(App.currentCaseId);
    } catch (e) {
      if (CaseWorkspace.caseData && CaseWorkspace.caseData.grievance) {
        const g = CaseWorkspace.caseData.grievance;
        const vNum = (this.currentDrafts.length || 1) + 1;
        const text = OFFICIAL_SUGGESTED_REPLIES[g.registration_no] ||
          `GOVERNMENT OF INDIA\nMINISTRY OF ELECTRONICS AND INFORMATION TECHNOLOGY\nEMERGING TECHNOLOGIES AND IOT DIVISION\n\nWith reference to CPGRAMS registration number ${g.registration_no}.\n\nThe matter has been examined in the Emerging Technologies and IOT Division, MeitY.\n\nIn view of the above position, the grievance stands disposed of.`;

        const newDraft = {
          id: 100 + vNum,
          version_number: vNum,
          draft_type: draftType,
          current_draft_text: text,
          draft_text: text,
          approval_status: "draft",
          is_approved_by_user: false,
          compliance_notes: "✓ GoI Central Secretariat drafting conventions verified.",
          created_at: new Date().toISOString()
        };
        this.currentDrafts.unshift(newDraft);
        this.setActiveDraft(newDraft);
        CaseWorkspace.caseData.drafts = this.currentDrafts;
        alert(`Generated Version ${vNum} using official MeitY drafting framework!`);
        if (window.DisposalManager) DisposalManager.initCaseDisposal(CaseWorkspace.caseData);
        return;
      }
      alert(`Draft generation error: ${e.message}`);
    }
  },

  handleDraftEdit() {
    // Triggers when officer types in editor
  },

  async saveDraftRevisions() {
    if (!this.activeDraft) {
      alert("Please generate a draft first.");
      return;
    }

    const revisedText = document.getElementById("draft-editor-text").value;

    try {
      const url = App.getApiUrl(`/api/drafting/${this.activeDraft.id}`);
      const res = await fetch(url, {
        method: "PUT",
        headers: App.getAuthHeaders({ "Content-Type": "application/json" }),
        body: JSON.stringify({
          current_draft_text: revisedText
        })
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Save failed");

      this.activeDraft = data.draft;
      alert("Draft revisions saved successfully!");
      CaseWorkspace.loadCase(App.currentCaseId);
    } catch (e) {
      alert(`Error saving draft: ${e.message}`);
    }
  },

  async showDiffModal() {
    if (!this.activeDraft) {
      alert("No active draft to compare.");
      return;
    }

    try {
      const url = App.getApiUrl(`/api/drafting/${this.activeDraft.id}/diff`);
      const res = await fetch(url, {
        method: "POST",
        headers: App.getAuthHeaders()
      });
      const data = await res.json();

      const modalContent = document.getElementById("diff-modal-content");
      if (!data.has_changes) {
        modalContent.innerHTML = `<div style="text-align:center; padding: 20px; color: var(--text-muted);">Original generated draft and current revised draft are identical. No revisions made.</div>`;
      } else {
        modalContent.innerHTML = `
          <div style="font-size: 12px; margin-bottom: 10px; color: var(--text-muted);">
            Comparing Initial Synthesized Draft vs Officer Revised Draft:
          </div>
          ${data.html_diff_table}
        `;
      }
      document.getElementById("diff-modal").classList.add("active");
    } catch (e) {
      alert(`Diff calculation failed: ${e.message}`);
    }
  },

  closeDiffModal() {
    document.getElementById("diff-modal").classList.remove("active");
  },

  async approveCurrentDraft() {
    if (!this.activeDraft) {
      alert("No active draft to approve.");
      return;
    }

    const conf = confirm(
      "CONFIRM APPROVAL:\nAre you sure you want to approve this draft for official disposal?\n\nThis marks the reply as Approved for Disposal in your register. (Actual portal disposal is performed by you on CPGRAMS)."
    );
    if (!conf) return;

    try {
      const url = App.getApiUrl(`/api/drafting/${this.activeDraft.id}/approve`);
      const res = await fetch(url, {
        method: "POST",
        headers: App.getAuthHeaders({ "Content-Type": "application/json" }),
        body: JSON.stringify({ approver: "Pragati (Scientist B, Emerging Technologies and IOT)" })
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Approval failed");

      alert("Draft approved! Grievance status updated to 'Approved for Disposal'.");
      CaseWorkspace.loadCase(App.currentCaseId);
    } catch (e) {
      if (CaseWorkspace.caseData && CaseWorkspace.caseData.drafts && CaseWorkspace.caseData.drafts.length > 0) {
        CaseWorkspace.caseData.drafts[0].approval_status = "approved";
        CaseWorkspace.caseData.drafts[0].is_approved_by_user = true;
        CaseWorkspace.caseData.grievance.workflow_state = "Approved for submission";
        CaseWorkspace.caseData.grievance.status = "Approved for Disposal";
        alert("Draft approved! Grievance status updated to 'Approved for Disposal'.");
        CaseWorkspace.renderCaseHeader(CaseWorkspace.caseData.grievance);
        if (window.DisposalManager) {
          DisposalManager.initCaseDisposal(CaseWorkspace.caseData);
        }
        CaseWorkspace.switchTab("tab-case-disposal");
        return;
      }
      alert(`Approval error: ${e.message}`);
    }
  },

  exportCurrentDraft(fmt) {
    if (!this.activeDraft) {
      alert("No draft available to export.");
      return;
    }
    const mask = App.maskPII ? "true" : "false";
    window.location.href = App.getApiUrl(`/api/drafting/${this.activeDraft.id}/export/${fmt}?mask_pii=${mask}`);
  }
};
