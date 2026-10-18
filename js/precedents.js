/**
 * Historical Disposed Grievance Library Controller
 * Full-text search, precedent tagging, provenance display, and officer annotations.
 */

const PrecedentManager = {
  async loadLibrary() {
    const container = document.getElementById("precedents-container");
    if (!container) return;
    container.innerHTML = `<div style="text-align:center; padding: 20px;">Loading historical precedent knowledge base...</div>`;

    try {
      const search = document.getElementById("prec-search-input") ? document.getElementById("prec-search-input").value.trim() : "";
      const category = document.getElementById("prec-filter-category") ? document.getElementById("prec-filter-category").value : "All";
      const reuse = document.getElementById("prec-filter-reuse") ? document.getElementById("prec-filter-reuse").value : "All";

      const params = new URLSearchParams();
      if (search) params.append("search", search);
      if (category !== "All") params.append("category", category);
      if (reuse !== "All") params.append("reuse", reuse);

      let data = null;
    try {
      if (!window.MockStore || !MockStore.isStaticMode) {
        const url = App.getApiUrl(`/api/precedents?${params.toString()}`);
        const res = await fetch(url, { headers: App.getAuthHeaders() });
        if (res.ok) data = await res.json();
      }
    } catch (e) {
      console.warn("Precedents API not reachable, falling back to mock precedents");
    }

    if (!data && window.MockStore) {
      data = MockStore.precedents || [];
    }

    if (!data || data.length === 0) {
      container.innerHTML = `<div style="text-align:center; padding: 30px; color: var(--text-muted);">No historical precedents match your search filters.</div>`;
      return;
    }

      container.innerHTML = data.map(p => {
        let tagClass = "badge-approved";
        if (p.reuse_recommendation === "outdated") tagClass = "badge-approaching";
        else if (p.reuse_recommendation === "restricted") tagClass = "badge-exam";
        else if (p.reuse_recommendation === "incorrect") tagClass = "badge-urgent";

        return `
          <div class="card" style="border-left: 4px solid var(--meity-blue); margin-bottom: 16px;">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 8px; margin-bottom: 8px;">
              <div>
                <strong style="font-size: 14.5px; color: var(--meity-navy);">${p.registration_no}</strong>
                <span class="badge ${tagClass}" style="margin-left: 8px;">${p.reuse_recommendation.toUpperCase()}</span>
                <span class="badge badge-sample" style="margin-left: 4px;">${p.status_tag}</span>
                <h4 style="font-size: 15px; font-weight: 700; margin-top: 4px; color: var(--meity-navy);">${p.subject}</h4>
              </div>
              <div style="text-align: right; font-size: 12px; color: var(--text-muted);">
                <div>Disposed: <strong>${p.disposal_date}</strong></div>
                <div>Outcome: <strong>${p.disposal_type}</strong></div>
              </div>
            </div>

            <div style="font-size: 12.5px; color: var(--text-muted); margin-bottom: 10px;">
              <span>Category: <strong>${p.category}</strong></span> • 
              <span>Policy Reference: <strong>${p.policy_reference || 'General MeitY Norms'}</strong></span> • 
              <span>Provenance: <em>${p.provenance}</em></span>
            </div>

            <!-- Grievance Summary -->
            <div style="background: #f8fafc; padding: 10px 14px; border-radius: 5px; font-size: 13px; margin-bottom: 12px; border: 1px solid #edf0f5;">
              <strong>Historical Grievance:</strong> ${p.full_grievance_text}
            </div>

            <!-- Official Final Reply -->
            <div style="background: #eef7ee; padding: 12px 14px; border-radius: 5px; font-size: 13.5px; margin-bottom: 14px; border: 1px solid #c8e6c9; color: #1b5e20;">
              <strong>Official Issued Reply:</strong><br>
              <div style="margin-top: 4px; line-height: 1.5; white-space: pre-wrap;">${p.final_reply}</div>
            </div>

            <!-- Officer Reuse Tagging Control -->
            <div style="display: flex; justify-content: space-between; align-items: center; border-top: 1px solid #edf0f5; padding-top: 10px; font-size: 12px;">
              <div style="display: flex; gap: 8px; align-items: center;">
                <span style="font-weight: 600;">Officer Precedent Guidance:</span>
                <select class="form-control" style="width: 170px; padding: 3px 6px; font-size: 12px;" onchange="PrecedentManager.updateReuseTag(${p.id}, this.value)">
                  <option value="useful_precedent" ${p.reuse_recommendation === 'useful_precedent' ? 'selected' : ''}>Useful Precedent (Approved)</option>
                  <option value="outdated" ${p.reuse_recommendation === 'outdated' ? 'selected' : ''}>Outdated (Policy Superseded)</option>
                  <option value="restricted" ${p.reuse_recommendation === 'restricted' ? 'selected' : ''}>Restricted (Case Specific)</option>
                  <option value="incorrect" ${p.reuse_recommendation === 'incorrect' ? 'selected' : ''}>Incorrect / Inapplicable</option>
                </select>
              </div>
              <span style="color: var(--text-muted);">${p.officer_notes || ''}</span>
            </div>
          </div>
        `;
      }).join("");

    } catch (e) {
      container.innerHTML = `<div style="text-align:center; padding: 20px; color: var(--meity-red);">Error loading precedents: ${e.message}</div>`;
    }
  },

  async updateReuseTag(precedentId, newTag) {
    try {
      const url = App.getApiUrl(`/api/precedents/${precedentId}/reuse`);
      const res = await fetch(url, {
        method: "PUT",
        headers: App.getAuthHeaders({ "Content-Type": "application/json" }),
        body: JSON.stringify({ reuse_recommendation: newTag })
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Update failed");
      App.toast(`Precedent marked as ${newTag}`);
      this.loadLibrary();
    } catch (e) {
      alert(`Error updating precedent: ${e.message}`);
    }
  },

  openAddModal() {
    document.getElementById("add-precedent-modal").classList.add("active");
  },

  closeAddModal() {
    document.getElementById("add-precedent-modal").classList.remove("active");
  },

  async savePrecedent() {
    const payload = {
      registration_no: document.getElementById("add-p-reg").value.trim(),
      subject: document.getElementById("add-p-subject").value.trim(),
      category: document.getElementById("add-p-category").value,
      disposal_date: document.getElementById("add-p-date").value || new Date().toISOString().split("T")[0],
      disposal_type: "Closed with reply",
      full_grievance_text: document.getElementById("add-p-grievance").value.trim(),
      final_reply: document.getElementById("add-p-reply").value.trim(),
      department: "Ministry of Electronics and Information Technology",
      division: "AI & Emerging Technologies Division",
      status_tag: "confirmed_issued",
      reuse_recommendation: "useful_precedent",
      provenance: "Manually Added by Officer",
      is_sample: false
    };

    if (!payload.registration_no || !payload.subject || !payload.final_reply) {
      alert("Registration number, subject, and final reply are required.");
      return;
    }

    try {
      const url = App.getApiUrl("/api/precedents");
      const res = await fetch(url, {
        method: "POST",
        headers: App.getAuthHeaders({ "Content-Type": "application/json" }),
        body: JSON.stringify(payload)
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Save failed");

      this.closeAddModal();
      this.loadLibrary();
      alert("Precedent added to library!");
    } catch (e) {
      alert(`Error adding precedent: ${e.message}`);
    }
  }
};
