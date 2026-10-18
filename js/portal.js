/**
 * CPGRAMS Portal Assistant Controller
 * Manages controlled browser launching, session monitoring, navigation,
 * read-only screen inspection, and selective record import.
 */

const PortalManager = {
  inspectedRecords: [],

  async launch() {
    const detailsBox = document.getElementById("portal-status-details");
    detailsBox.innerHTML = `<em>Launching controlled browser session for official login... Please wait.</em>`;
    
    try {
      const res = await fetch("/api/portal/launch", { method: "POST" });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Launch failed");

      detailsBox.innerHTML = `
        <strong>Browser Launched (${data.browser}):</strong> ${data.instructions}<br>
        <span style="font-size: 11.5px; color: var(--text-muted);">Current URL: ${data.current_url}</span>
      `;
      this.checkStatus();
    } catch (e) {
      detailsBox.innerHTML = `<span style="color: var(--meity-red);">Error: ${e.message}</span>`;
    }
  },

  async checkStatus() {
    try {
      const res = await fetch("/api/portal/status");
      const data = await res.json();
      
      const badge = document.getElementById("portal-session-badge");
      const details = document.getElementById("portal-status-details");

      if (!data.is_running) {
        badge.className = "badge badge-sample";
        badge.innerText = "SESSION INACTIVE";
        details.innerHTML = `No active browser session. Click "Launch Controlled Browser" to begin.`;
        return;
      }

      if (data.is_logged_in) {
        badge.className = "badge badge-approved";
        badge.innerText = "OFFICER AUTHENTICATED";
        details.innerHTML = `
          <strong>Status:</strong> Authenticated as Officer on CPGRAMS.<br>
          <strong>Active View:</strong> ${data.current_view} (${data.current_url})<br>
          <span style="font-size: 11.5px; color: var(--text-muted);">Ready to inspect visible search or desk records.</span>
        `;
      } else if (data.is_session_expired) {
        badge.className = "badge badge-urgent";
        badge.innerText = "SESSION EXPIRED";
        details.innerHTML = `<strong style="color: var(--meity-red);">Portal Session Expired:</strong> Please re-authenticate directly in the open browser window.`;
      } else {
        badge.className = "badge badge-exam";
        badge.innerText = "AWAITING OFFICER LOGIN";
        details.innerHTML = `Browser is open on official login page. Please enter your credentials and CAPTCHA / Parichay OTP.`;
      }
    } catch (e) {
      console.error("Status check failed", e);
    }
  },

  async navigate(destination) {
    try {
      const res = await fetch("/api/portal/navigate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ destination })
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Navigation failed");
      this.checkStatus();
    } catch (e) {
      alert(`Navigation failed: ${e.message}`);
    }
  },

  async inspectScreen() {
    const previewBox = document.getElementById("portal-records-preview");
    const summary = document.getElementById("portal-records-summary");
    const tbody = document.getElementById("portal-records-tbody");

    summary.innerText = "Inspecting active screen DOM... Please wait.";
    previewBox.style.display = "block";
    tbody.innerHTML = `<tr><td colspan="7" style="text-align:center;">Extracting visible records from browser table...</td></tr>`;

    try {
      const res = await fetch("/api/portal/inspect", { method: "POST" });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Inspection failed");

      this.inspectedRecords = data.records;
      summary.innerHTML = `Found <strong>${data.total_detected}</strong> visible records (${data.new_records} new, ${data.duplicate_records} already in workbench).`;

      if (data.records.length === 0) {
        tbody.innerHTML = `<tr><td colspan="7" style="text-align:center; color: var(--text-muted);">No tabular grievance rows detected on current screen. Please ensure search results or desk table is visible.</td></tr>`;
        return;
      }

      tbody.innerHTML = data.records.map((r, idx) => `
        <tr style="${r.is_duplicate ? 'opacity: 0.6;' : ''}">
          <td>
            <input type="checkbox" class="portal-row-check" data-idx="${idx}" ${r.is_duplicate ? 'disabled' : 'checked'}>
          </td>
          <td><strong>${r.registration_no}</strong></td>
          <td>${r.subject}</td>
          <td>${r.applicant_masked || r.applicant_name}</td>
          <td>${r.date_received}</td>
          <td><span class="badge badge-exam">${r.status}</span></td>
          <td>
            ${r.is_duplicate 
              ? '<span class="badge badge-sample">Duplicate (In DB)</span>' 
              : '<span class="badge badge-approved">New Record</span>'}
          </td>
        </tr>
      `).join("");
    } catch (e) {
      summary.innerHTML = `<span style="color: var(--meity-red);">Inspection Error: ${e.message}</span>`;
      tbody.innerHTML = `<tr><td colspan="7" style="text-align:center; color: var(--meity-red);">${e.message}</td></tr>`;
    }
  },

  toggleSelectAll(masterCheckbox) {
    document.querySelectorAll(".portal-row-check:not(:disabled)").forEach(cb => {
      cb.checked = masterCheckbox.checked;
    });
  },

  async importSelected() {
    const selected = [];
    document.querySelectorAll(".portal-row-check:checked").forEach(cb => {
      const idx = parseInt(cb.getAttribute("data-idx"));
      selected.push(this.inspectedRecords[idx]);
    });

    if (selected.length === 0) {
      alert("Please select at least one record to import.");
      return;
    }

    try {
      const res = await fetch("/api/portal/import", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(selected)
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Import failed");

      alert(`Successfully imported ${data.imported_count} records into local workbench register!`);
      App.switchView("register");
    } catch (e) {
      alert(`Import error: ${e.message}`);
    }
  },

  async closeSession() {
    try {
      await fetch("/api/portal/close", { method: "POST" });
      this.checkStatus();
    } catch (e) {
      console.error("Close session error", e);
    }
  }
};
