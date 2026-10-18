/**
 * Grievance Register Controller
 * Search, filter, pagination, and case navigation.
 */

const RegisterManager = {
  currentPage: 1,
  pageSize: 12,
  searchTimer: null,

  async loadRegister() {
    const tbody = document.getElementById("register-tbody");
    if (!tbody) return;
    tbody.innerHTML = `<tr><td colspan="9" style="text-align: center;">Loading cases...</td></tr>`;

    try {
      const search = document.getElementById("reg-search-input") ? document.getElementById("reg-search-input").value.trim() : "";
      const status = document.getElementById("reg-filter-status") ? document.getElementById("reg-filter-status").value : "All";
      const category = document.getElementById("reg-filter-category") ? document.getElementById("reg-filter-category").value : "All";
      const priority = document.getElementById("reg-filter-priority") ? document.getElementById("reg-filter-priority").value : "All";
      const sample = document.getElementById("reg-filter-sample") ? document.getElementById("reg-filter-sample").value : "All";

      const params = new URLSearchParams({
        page: this.currentPage,
        page_size: this.pageSize,
        unmask_pii: !App.maskPII
      });

    if (search) params.append("search", search);
    if (status !== "All") params.append("status", status);
    if (category !== "All") params.append("category", category);
    if (priority !== "All") params.append("priority", priority);
    if (sample !== "All") params.append("is_sample", sample);

    let data = null;
    try {
      if (!window.MockStore || !MockStore.isStaticMode) {
        const url = App.getApiUrl(`/api/grievances?${params.toString()}`);
        const res = await fetch(url, { headers: App.getAuthHeaders() });
        if (res.ok) data = await res.json();
      }
    } catch (e) {
      console.warn("API not reachable, using static mock grievances");
    }

    if (!data && window.MockStore) {
      data = {
        total: MockStore.grievances.length,
        page: 1,
        items: MockStore.grievances
      };
    }

    if (!data || data.items.length === 0) {
      tbody.innerHTML = `<tr><td colspan="10" style="text-align:center; color: var(--text-muted);">No matching grievance records found.</td></tr>`;
      return;
    }

    document.getElementById("register-count-label").innerText = `Showing ${data.items.length} of ${data.total} records (Page ${data.page})`;

      tbody.innerHTML = data.items.map(g => {
        // Status Badge
        let statusBadgeClass = "badge-new";
        if (g.status === "Under Examination") statusBadgeClass = "badge-exam";
        else if (g.status === "Awaiting Inputs") statusBadgeClass = "badge-inputs";
        else if (g.status === "Draft Prepared") statusBadgeClass = "badge-draft";
        else if (g.status === "Approved for Disposal") statusBadgeClass = "badge-approved";
        else if (g.status === "Disposed") statusBadgeClass = "badge-disposed";

        // 9-Stage Workflow State Badge
        const wfState = g.workflow_state || "Retrieved";
        let wfBadgeClass = "badge-draft";
        if (wfState === "Official submission confirmed") wfBadgeClass = "badge-approved";
        else if (wfState === "Approved for submission") wfBadgeClass = "badge-inputs";
        else if (wfState === "Submission in progress") wfBadgeClass = "badge-exam";
        else if (wfState === "Status requires verification") wfBadgeClass = "badge-approaching";
        else if (wfState === "Submission failed") wfBadgeClass = "badge-urgent";

        // Deadline Badge
        let deadlineHtml = "";
        if (g.deadline_status === "OVERDUE") {
          deadlineHtml = `<span class="badge badge-overdue">OVERDUE (${Math.abs(g.days_remaining)}d)</span>`;
        } else if (g.deadline_status === "APPROACHING") {
          deadlineHtml = `<span class="badge badge-approaching">${g.days_remaining}d Left</span>`;
        } else if (g.deadline_status === "DISPOSED") {
          deadlineHtml = `<span class="badge badge-disposed">Disposed</span>`;
        } else {
          deadlineHtml = `<span class="badge badge-new">${g.days_remaining ? g.days_remaining + 'd Left' : '21d Norm'}</span>`;
        }

        // Sample data badge
        const sampleTag = g.is_sample ? `<span class="badge badge-sample" title="Synthetic Test Record">Sample</span>` : "";

        return `
          <tr>
            <td>
              <strong style="color: var(--meity-blue); font-size: 12px;">${g.registration_no}</strong>
              ${sampleTag}
            </td>
            <td>
              <div style="font-weight: 600; max-width: 250px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;" title="${g.subject}">
                ${g.subject}
              </div>
            </td>
            <td style="white-space: nowrap; font-size: 12px;">${g.date_received}</td>
            <td style="font-size: 12px;">${g.applicant_name}</td>
            <td style="font-size: 11.5px; color: var(--text-muted);">${g.category}</td>
            <td><span class="badge ${statusBadgeClass}">${g.status}</span></td>
            <td><span class="badge ${wfBadgeClass}" style="font-size: 10px;">${wfState}</span></td>
            <td>${deadlineHtml}</td>
            <td>
              <button class="btn btn-primary" style="padding: 3px 8px; font-size: 11.5px;" onclick="CaseWorkspace.openCase(${g.id})">
                Open Case
              </button>
            </td>
          </tr>
        `;
      }).join("");

    } catch (e) {
      tbody.innerHTML = `<tr><td colspan="9" style="text-align:center; color: var(--meity-red);">Error loading records: ${e.message}</td></tr>`;
    }
  },

  handleSearch() {
    clearTimeout(this.searchTimer);
    this.searchTimer = setTimeout(() => {
      this.currentPage = 1;
      this.loadRegister();
    }, 300);
  },

  prevPage() {
    if (this.currentPage > 1) {
      this.currentPage--;
      this.loadRegister();
    }
  },

  nextPage() {
    this.currentPage++;
    this.loadRegister();
  }
};
