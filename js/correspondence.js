/**
 * Master Correspondence & Input Tracker Controller
 */

const CorrespondenceManager = {
  async loadMaster() {
    const tbody = document.getElementById("master-corr-tbody");
    tbody.innerHTML = `<tr><td colspan="8" style="text-align: center;">Loading tracked calls for input...</td></tr>`;

    try {
      const url = App.getApiUrl("/api/correspondence");
      const res = await fetch(url, { headers: App.getAuthHeaders() });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const list = await res.json();

      if (list.length === 0) {
        tbody.innerHTML = `<tr><td colspan="8" style="text-align: center; color: var(--text-muted);">No inter-divisional inquiries recorded.</td></tr>`;
        return;
      }

      tbody.innerHTML = list.map(c => `
        <tr>
          <td><strong>${c.reference_no}</strong></td>
          <td>${c.recipient_office}</td>
          <td>${c.date_sent}</td>
          <td><div style="max-width: 260px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">${c.subject}</div></td>
          <td><strong>${c.target_due_date}</strong></td>
          <td><span class="badge ${c.status === 'Overdue' ? 'badge-urgent' : (c.status === 'Reminder Sent' ? 'badge-approaching' : 'badge-new')}">${c.status}</span></td>
          <td style="font-size: 11.5px; color: var(--text-muted);">${c.follow_up_history ? c.follow_up_history.replace(/\n/g, '<br>') : 'None'}</td>
          <td>
            <button class="btn btn-outline" style="font-size: 11px; padding: 3px 6px;" onclick="CorrespondenceManager.logFollowup(${c.id})">+ Reminder</button>
            <button class="btn btn-success" style="font-size: 11px; padding: 3px 6px;" onclick="CorrespondenceManager.markReceived(${c.id})">✓ Received</button>
          </td>
        </tr>
      `).join("");

    } catch (e) {
      tbody.innerHTML = `<tr><td colspan="8" style="text-align:center; color: var(--text-muted);">Local agent offline or no correspondence records found.</td></tr>`;
    }
  },

  async openAddModal() {
    const ref = prompt("Enter Reference Number (e.g. MeitY/AI/2026/INP-099):");
    if (!ref) return;
    const recipient = prompt("Enter Recipient Office (e.g. C-DAC / Cyber Security Division):");
    if (!recipient) return;
    const subject = prompt("Enter Subject:");
    if (!subject) return;

    const payload = {
      reference_no: ref,
      recipient_office: recipient,
      subject: subject,
      target_due_date: new Date(Date.now() + 7 * 86400000).toISOString().split("T")[0]
    };

    try {
      const url = App.getApiUrl("/api/correspondence");
      const res = await fetch(url, {
        method: "POST",
        headers: App.getAuthHeaders({ "Content-Type": "application/json" }),
        body: JSON.stringify(payload)
      });
      if (!res.ok) throw new Error("Failed to add inquiry");
      this.loadMaster();
    } catch (e) {
      alert(`Error: ${e.message}`);
    }
  },

  async logFollowup(id) {
    const note = prompt("Enter follow-up reminder note:");
    if (!note) return;
    try {
      const url = App.getApiUrl(`/api/correspondence/${id}/reminder`);
      await fetch(url, {
        method: "POST",
        headers: App.getAuthHeaders({ "Content-Type": "application/json" }),
        body: JSON.stringify({ reminder_note: note })
      });
      this.loadMaster();
    } catch (e) {
      alert(`Error: ${e.message}`);
    }
  },

  async markReceived(id) {
    const summary = prompt("Enter summary of comments/inputs received:");
    if (!summary) return;
    try {
      const url = App.getApiUrl(`/api/correspondence/${id}`);
      await fetch(url, {
        method: "PUT",
        headers: App.getAuthHeaders({ "Content-Type": "application/json" }),
        body: JSON.stringify({
          status: "Response Received",
          date_received: new Date().toISOString().split("T")[0],
          response_summary: summary
        })
      });
      this.loadMaster();
    } catch (e) {
      alert(`Error: ${e.message}`);
    }
  }
};
