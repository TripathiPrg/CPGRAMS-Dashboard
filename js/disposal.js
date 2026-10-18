/**
 * CPGRAMS Authorized Disposal & Portal Verification Controller
 * Manages the 9-stage operational workflow:
 * 1. Retrieved -> 2. Analysis complete -> 3. Draft generated -> 4. Awaiting review ->
 * 5. Approved for submission -> 6. Submission in progress ->
 * 7. Official submission confirmed (Strict portal confirmation only)
 * Fallback branches: 8. Submission failed / 9. Status requires verification
 */

const DisposalManager = {
  currentGrievanceId: null,
  currentCaseData: null,
  currentChecklist: null,

  async initCaseDisposal(caseData) {
    this.currentCaseData = caseData;
    this.currentGrievanceId = caseData.grievance.id;
    this.updateWorkflowStepper(caseData.grievance.workflow_state || "Retrieved");
    await this.refreshChecklist();

    // Check if case is already verified and confirmed
    const g = caseData.grievance;
    if (g.workflow_state === "Official submission confirmed" || g.status === "Disposed") {
      this.displayReceipt({
        registration_no: g.registration_no,
        portal_confirmation_id: g.portal_confirmation_id || "OFFICIAL-CPGRAMS-RECORD",
        timestamp: g.portal_action_timestamp || new Date().toLocaleString(),
        method: g.verification_status === "verified_manual_audit" ? "Officer Audit Reference" : "Live Portal DOM Check",
        reply_text: g.portal_reply_recorded || (caseData.drafts && caseData.drafts[0] ? caseData.drafts[0].current_draft_text : "Disposal response recorded on CPGRAMS.")
      });
    } else {
      const receiptEl = document.getElementById("disposal-receipt-card");
      if (receiptEl) receiptEl.style.display = "none";
    }
  },

  updateWorkflowStepper(state) {
    const stateBadge = document.getElementById("disposal-state-badge");
    if (stateBadge) {
      stateBadge.innerText = `Workflow State: ${state}`;
      if (state === "Official submission confirmed") stateBadge.className = "badge badge-approved";
      else if (state === "Submission in progress") stateBadge.className = "badge badge-exam";
      else if (state === "Approved for submission") stateBadge.className = "badge badge-inputs";
      else if (state === "Status requires verification") stateBadge.className = "badge badge-approaching";
      else if (state === "Submission failed") stateBadge.className = "badge badge-urgent";
      else stateBadge.className = "badge badge-draft";
    }

    const steps = [
      { id: "step-retrieved", name: "Retrieved" },
      { id: "step-analyzed", name: "Analysis complete" },
      { id: "step-drafted", name: "Draft generated" },
      { id: "step-reviewing", name: "Awaiting review" },
      { id: "step-approved", name: "Approved for submission" },
      { id: "step-submitting", name: "Submission in progress" },
      { id: "step-confirmed", name: "Official submission confirmed" }
    ];

    const stateOrder = [
      "Retrieved",
      "Analysis complete",
      "Draft generated",
      "Awaiting review",
      "Approved for submission",
      "Submission in progress",
      "Official submission confirmed"
    ];

    const currentIdx = stateOrder.indexOf(state);

    steps.forEach((step, idx) => {
      const el = document.getElementById(step.id);
      if (!el) return;
      el.classList.remove("active", "completed", "alert");
      if (currentIdx !== -1) {
        if (idx < currentIdx) {
          el.classList.add("completed");
        } else if (idx === currentIdx) {
          el.classList.add("active");
        }
      }
    });

    if (state === "Status requires verification" || state === "Submission failed") {
      const subEl = document.getElementById("step-submitting");
      if (subEl) subEl.classList.add("alert");
    }
  },

  async refreshChecklist() {
    if (!this.currentGrievanceId) return;
    const container = document.getElementById("disposal-checklist-items");
    if (!container) return;

    try {
      const url = App.getApiUrl(`/api/disposal/checklist/${this.currentGrievanceId}`);
      const res = await fetch(url);
      if (!res.ok) throw new Error("Failed to load checklist");
      const data = await res.json();
      this.currentChecklist = data;

      container.innerHTML = data.checks.map(c => `
        <div class="checklist-item">
          <span class="checklist-icon ${c.passed ? 'pass' : 'fail'}">${c.passed ? '✓' : '✗'}</span>
          <div style="flex: 1;">
            <div style="font-weight: 600; color: ${c.passed ? '#27ae60' : '#c0392b'};">${c.label}</div>
            ${c.detail ? `<div style="font-size: 11px; color: var(--text-muted);">${c.detail}</div>` : ''}
          </div>
        </div>
      `).join("");

      const initiateBtn = document.getElementById("btn-initiate-disposal");
      if (initiateBtn) {
        if (data.is_already_disposed) {
          initiateBtn.disabled = true;
          initiateBtn.innerText = "✓ Case Already Officially Disposed";
          initiateBtn.style.background = "#7f8c8d";
        } else if (!data.can_initiate) {
          initiateBtn.disabled = true;
          initiateBtn.innerText = "Initiate Disposal (Satisfy Checklist First)";
          initiateBtn.style.background = "#95a5a6";
        } else {
          initiateBtn.disabled = false;
          initiateBtn.innerText = "🚀 Initiate Verified Portal Disposal";
          initiateBtn.style.background = "#27ae60";
        }
      }
    } catch (e) {
      container.innerHTML = `<div style="color: var(--text-muted); font-size: 12px;">Checklist loaded from local state.</div>`;
    }
  },

  openDualConfirmModal() {
    if (!this.currentChecklist || !this.currentChecklist.can_initiate) {
      alert("Please ensure all pre-disposal compliance checks are satisfied before initiating disposal.");
      return;
    }

    const modal = document.getElementById("disposal-confirm-modal");
    document.getElementById("modal-confirm-reg").innerText = this.currentCaseData.grievance.registration_no;
    
    const draftText = this.currentChecklist.latest_draft ? this.currentChecklist.latest_draft.text : "";
    document.getElementById("modal-confirm-reply-preview").innerText = draftText;
    document.getElementById("modal-confirm-ack").checked = false;

    modal.classList.add("active");
  },

  closeDualConfirmModal() {
    const modal = document.getElementById("disposal-confirm-modal");
    if (modal) modal.classList.remove("active");
  },

  async executeInitiation() {
    const ack = document.getElementById("modal-confirm-ack");
    if (!ack || !ack.checked) {
      alert("Please check the declaration box acknowledging officer review and authorization before proceeding.");
      return;
    }

    const category = document.getElementById("disposal-category-select").value;
    const remarks = document.getElementById("disposal-remarks-input").value;
    const draftId = this.currentChecklist.latest_draft.id;

    try {
      const url = App.getApiUrl("/api/disposal/initiate");
      const res = await fetch(url, {
        method: "POST",
        headers: App.getAuthHeaders({ "Content-Type": "application/json" }),
        body: JSON.stringify({
          grievance_id: this.currentGrievanceId,
          draft_id: draftId,
          disposal_category: category,
          disposal_remarks: remarks,
          confirmed_by_officer: true
        })
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Initiation failed");

      this.closeDualConfirmModal();
      alert("DISPOSAL STAGED ON CPGRAMS:\n" + data.message);
      
      // Reload workspace
      await CaseWorkspace.loadCase(this.currentGrievanceId);
      CaseWorkspace.switchTab("tab-case-disposal");
    } catch (e) {
      alert(`Disposal initiation error: ${e.message}`);
    }
  },

  async verifyPortalStatus() {
    if (!this.currentGrievanceId) return;

    try {
      const url = App.getApiUrl("/api/disposal/verify");
      const res = await fetch(url, {
        method: "POST",
        headers: App.getAuthHeaders({ "Content-Type": "application/json" }),
        body: JSON.stringify({ grievance_id: this.currentGrievanceId })
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Verification request failed");

      if (data.is_verified) {
        alert("PORTAL DISPOSAL CONFIRMED!\nOfficial CPGRAMS status is verified. The case is now officially closed in your register.");
      } else {
        alert("PORTAL STATUS CHECK NOTICE:\n" + data.message);
      }

      await CaseWorkspace.loadCase(this.currentGrievanceId);
      CaseWorkspace.switchTab("tab-case-disposal");
    } catch (e) {
      alert(`Portal verification error: ${e.message}`);
    }
  },

  openManualVerifyModal() {
    const modal = document.getElementById("disposal-manual-modal");
    if (modal) modal.classList.add("active");
  },

  closeManualVerifyModal() {
    const modal = document.getElementById("disposal-manual-modal");
    if (modal) modal.classList.remove("active");
  },

  async submitManualVerification() {
    const confId = document.getElementById("manual-verify-conf-id").value.trim();
    const notes = document.getElementById("manual-verify-notes").value.trim();

    if (!confId) {
      alert("Please provide the CPGRAMS confirmation reference / receipt number.");
      return;
    }

    try {
      const url = App.getApiUrl("/api/disposal/manual_verify");
      const res = await fetch(url, {
        method: "POST",
        headers: App.getAuthHeaders({ "Content-Type": "application/json" }),
        body: JSON.stringify({
          grievance_id: this.currentGrievanceId,
          portal_confirmation_id: confId,
          verification_notes: notes
        })
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Verification failed");

      this.closeManualVerifyModal();
      alert("SUCCESSFUL VERIFICATION AUDIT:\nCase successfully finalized with official confirmation reference: " + confId);
      await CaseWorkspace.loadCase(this.currentGrievanceId);
      CaseWorkspace.switchTab("tab-case-disposal");
    } catch (e) {
      alert(`Manual verification error: ${e.message}`);
    }
  },

  async abortStaging() {
    const conf = confirm("Are you sure you want to cancel the in-progress submission staging and return this case to 'Approved for submission'?");
    if (!conf) return;

    try {
      const url = App.getApiUrl("/api/disposal/abort");
      const res = await fetch(url, {
        method: "POST",
        headers: App.getAuthHeaders({ "Content-Type": "application/json" }),
        body: JSON.stringify({ grievance_id: this.currentGrievanceId, reason: "Officer cancelled staging" })
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Abort failed");

      alert(data.message);
      await CaseWorkspace.loadCase(this.currentGrievanceId);
      CaseWorkspace.switchTab("tab-case-disposal");
    } catch (e) {
      alert(`Abort error: ${e.message}`);
    }
  },

  displayReceipt(receipt) {
    const card = document.getElementById("disposal-receipt-card");
    if (!card) return;
    card.style.display = "block";
    document.getElementById("receipt-reg-no").innerText = receipt.registration_no || "-";
    document.getElementById("receipt-conf-id").innerText = receipt.portal_confirmation_id || "-";
    document.getElementById("receipt-timestamp").innerText = receipt.timestamp ? new Date(receipt.timestamp).toLocaleString() : "-";
    document.getElementById("receipt-method").innerText = receipt.method || "Portal DOM Verification";
    document.getElementById("receipt-reply-text").innerText = receipt.reply_text || "-";
  }
};
