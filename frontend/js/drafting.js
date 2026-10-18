/**
 * Case Workspace & Official Reply Drafting Studio Controller
 * Manages detailed case view, AI analysis, semantic precedent matching,
 * drafting versioning, diff comparisons, approvals, and DOCX/TXT export.
 */

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
    try {
      const url = App.getApiUrl(`/api/grievances/${id}?unmask_pii=${!App.maskPII}`);
      const res = await fetch(url, { headers: App.getAuthHeaders() });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Failed to load case");

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

    } catch (e) {
      alert(`Error loading case: ${e.message}`);
    }
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
      const res = await fetch(`/api/grievances/${App.currentCaseId}/analyze`, { method: "POST" });
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
      const res = await fetch(`/api/grievances/${App.currentCaseId}/analysis`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
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
      const res = await fetch("/api/precedents/search", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
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
      const res = await fetch(`/api/correspondence/${corrId}/reminder`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
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
        body: JSON.stringify({ approver: "Public Grievance Officer (MeitY AI & ET)" })
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Approval failed");

      alert("Draft approved! Grievance status updated to 'Approved for Disposal'.");
      CaseWorkspace.loadCase(App.currentCaseId);
    } catch (e) {
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
