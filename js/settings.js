/**
 * Settings, Routing Rules, Backup & Security Controller
 */

const RoutingManager = {
  async loadRules() {
    const tbody = document.getElementById("routing-rules-tbody");
    tbody.innerHTML = `<tr><td colspan="7" style="text-align: center;">Loading routing rules...</td></tr>`;

    try {
      const url = App.getApiUrl("/api/settings/routing-rules");
      const res = await fetch(url, { headers: App.getAuthHeaders() });
      const rules = res.ok ? await res.json() : (window.MockStore ? MockStore.routingRules : []);

      tbody.innerHTML = rules.map(r => `
        <tr>
          <td><strong>${r.rule_name}</strong></td>
          <td><code style="background: #edf2f7; padding: 2px 6px; border-radius: 4px; font-size: 11.5px;">${r.keyword_triggers}</code></td>
          <td><strong>${r.target_division}</strong></td>
          <td>${r.recommended_action}</td>
          <td style="font-size: 12px; color: var(--text-muted);">${r.explanation}</td>
          <td><span class="badge ${r.is_active ? 'badge-approved' : 'badge-sample'}">${r.is_active ? 'Active' : 'Disabled'}</span></td>
          <td>
            <button class="btn btn-outline" style="font-size: 11px; padding: 2px 6px; color: var(--meity-red);" onclick="RoutingManager.deleteRule(${r.id})">Delete</button>
          </td>
        </tr>
      `).join("");
    } catch (e) {
      tbody.innerHTML = `<tr><td colspan="7" style="color: var(--meity-red);">Error: ${e.message}</td></tr>`;
    }
  },

  openAddRuleModal() {
    document.getElementById("add-rule-modal").classList.add("active");
  },

  closeAddRuleModal() {
    document.getElementById("add-rule-modal").classList.remove("active");
  },

  async saveRule() {
    const payload = {
      rule_name: document.getElementById("rule-name-input").value.trim(),
      keyword_triggers: document.getElementById("rule-keywords-input").value.trim(),
      target_ministry: "Ministry of Electronics and Information Technology",
      target_division: document.getElementById("rule-division-input").value.trim(),
      recommended_action: document.getElementById("rule-action-input").value.trim(),
      explanation: document.getElementById("rule-explanation-input").value.trim(),
      priority_order: 10,
      is_active: true
    };

    if (!payload.rule_name || !payload.keyword_triggers || !payload.target_division) {
      alert("Rule name, keywords, and target division are required.");
      return;
    }

    try {
      const url = App.getApiUrl("/api/settings/routing-rules");
      const res = await fetch(url, {
        method: "POST",
        headers: App.getAuthHeaders({ "Content-Type": "application/json" }),
        body: JSON.stringify(payload)
      });
      if (!res.ok) throw new Error("Failed to save rule");
      this.closeAddRuleModal();
      this.loadRules();
      alert("Routing rule created!");
    } catch (e) {
      alert(`Error saving rule: ${e.message}`);
    }
  },

  async deleteRule(id) {
    if (!confirm("Are you sure you want to delete this routing rule?")) return;
    try {
      const url = App.getApiUrl(`/api/settings/routing-rules/${id}`);
      await fetch(url, { method: "DELETE", headers: App.getAuthHeaders() });
      this.loadRules();
    } catch (e) {
      alert(`Error: ${e.message}`);
    }
  }
};

const SettingsManager = {
  loadSettings() {
    this.loadSystemDiagnostics();
    this.loadBackups();
    this.loadAuditLogs();
  },

  async loadSystemDiagnostics() {
    try {
      const url = App.getApiUrl("/api/settings/system-info");
      const res = await fetch(url, { headers: App.getAuthHeaders() });
      if (!res.ok) return;
      const info = await res.json();
      document.getElementById("diag-host").innerText = `${info.binding_host} (Local Only)`;
      document.getElementById("diag-port").innerText = info.binding_port;
      document.getElementById("diag-browser").innerText = info.installed_browser;
      document.getElementById("diag-os").innerText = `${info.operating_system} ${info.os_release}`;
      document.getElementById("diag-python").innerText = info.python_version;
    } catch (e) {
      console.error("Diagnostics load error", e);
    }
  },

  async loadBackups() {
    const tbody = document.getElementById("backups-tbody");
    tbody.innerHTML = `<tr><td colspan="4" style="text-align: center;">Loading backups...</td></tr>`;

    try {
      const url = App.getApiUrl("/api/settings/backups");
      const res = await fetch(url, { headers: App.getAuthHeaders() });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const backups = await res.json();

      if (backups.length === 0) {
        tbody.innerHTML = `<tr><td colspan="4" style="text-align: center; color: var(--text-muted);">No backup snapshots exist yet.</td></tr>`;
        return;
      }

      tbody.innerHTML = backups.map(b => `
        <tr>
          <td><strong>${b.filename}</strong></td>
          <td>${b.size_kb} KB</td>
          <td>${new Date(b.created_at).toLocaleString()}</td>
          <td>
            <button class="btn btn-outline" style="font-size: 11px; padding: 3px 8px;" onclick="SettingsManager.restoreSnapshot('${b.filename}')">Restore Snapshot</button>
          </td>
        </tr>
      `).join("");
    } catch (e) {
      tbody.innerHTML = `<tr><td colspan="4" style="text-align:center; color: var(--text-muted);">Local agent offline or no snapshots.</td></tr>`;
    }
  },

  async createBackup() {
    try {
      const url = App.getApiUrl("/api/settings/backups/create");
      const res = await fetch(url, { method: "POST", headers: App.getAuthHeaders() });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Backup failed");
      alert(`Snapshot '${data.filename}' created successfully (${data.size_kb} KB)!`);
      this.loadBackups();
    } catch (e) {
      alert(`Backup error: ${e.message}`);
    }
  },

  async restoreSnapshot(filename) {
    const conf = confirm(`CONFIRM RESTORE:\nAre you sure you want to restore database snapshot '${filename}'?\n\nA safety pre-restore backup will be created automatically before replacing active database.`);
    if (!conf) return;

    try {
      const url = App.getApiUrl("/api/settings/backups/restore");
      const res = await fetch(url, {
        method: "POST",
        headers: App.getAuthHeaders({ "Content-Type": "application/json" }),
        body: JSON.stringify({ filename })
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Restore failed");
      alert(`Database successfully restored from snapshot '${filename}'!`);
      location.reload();
    } catch (e) {
      alert(`Restore failed: ${e.message}`);
    }
  },

  async loadAuditLogs() {
    const tbody = document.getElementById("full-audit-tbody");
    const eventType = document.getElementById("audit-filter-type").value;
    
    tbody.innerHTML = `<tr><td colspan="5" style="text-align: center;">Loading audit logs...</td></tr>`;

    try {
      const url = App.getApiUrl(`/api/settings/audit-logs?event_type=${eventType}&limit=60`);
      const res = await fetch(url, { headers: App.getAuthHeaders() });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const logs = await res.json();

      if (logs.length === 0) {
        tbody.innerHTML = `<tr><td colspan="5" style="text-align: center; color: var(--text-muted);">No audit records found.</td></tr>`;
        return;
      }

      tbody.innerHTML = logs.map(l => `
        <tr>
          <td style="white-space: nowrap; font-size: 11.5px; color: var(--text-muted);">${new Date(l.timestamp).toLocaleString()}</td>
          <td><span class="badge badge-draft">${l.event_type}</span></td>
          <td><strong>${l.entity_type}</strong></td>
          <td>${l.details}</td>
          <td style="font-size: 11.5px; color: var(--text-muted);">${l.actor}</td>
        </tr>
      `).join("");
    } catch (e) {
      tbody.innerHTML = `<tr><td colspan="5" style="text-align:center; color: var(--text-muted);">Audit log viewing requires local agent connection.</td></tr>`;
    }
  }
};
