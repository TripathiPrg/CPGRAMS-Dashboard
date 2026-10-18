/**
 * CPGRAMS Personal Workbench - Core SPA Application Engine
 * Ministry of Electronics and Information Technology (MeitY)
 */

const App = {
  currentView: "dashboard",
  maskPII: true,
  currentCaseId: null,
  isLocalAgentConnected: false,
  apiBase: (window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1") ? "" : "http://127.0.0.1:8000",
  bridgeToken: localStorage.getItem("cpgrams_bridge_token") || "",

  init() {
    this.setupNavigation();
    this.setupPIIToggle();
    this.checkBridgeConnection();
    this.loadDashboardData();
  },

  getApiUrl(path) {
    if (!path.startsWith("/")) path = "/" + path;
    return `${this.apiBase}${path}`;
  },

  getAuthHeaders(customHeaders = {}) {
    const headers = { ...customHeaders };
    if (this.bridgeToken) {
      headers["X-Local-Bridge-Token"] = this.bridgeToken;
    }
    return headers;
  },

  async checkBridgeConnection() {
    const pillText = document.getElementById("bridge-pill-text");
    const pillDot = document.getElementById("bridge-pill-dot");
    const sidebarStatus = document.getElementById("sidebar-status-text");

    try {
      const url = this.getApiUrl("/api/bridge/status");
      const res = await fetch(url, { method: "GET" });
      if (res.ok) {
        this.isLocalAgentConnected = true;
        if (pillText) pillText.innerText = "Local Agent: Connected (127.0.0.1:8000)";
        if (pillDot) {
          pillDot.style.background = "#27ae60";
          pillDot.style.boxShadow = "0 0 6px rgba(39, 174, 96, 0.6)";
        }
        if (sidebarStatus) {
          sidebarStatus.innerHTML = '<span style="color: #2ecc71;">●</span> 127.0.0.1:8000 • Live Agent';
        }
        return true;
      }
    } catch (e) {
      this.isLocalAgentConnected = false;
      if (pillText) pillText.innerText = "Local Agent: Offline (Demo Mode)";
      if (pillDot) {
        pillDot.style.background = "#e67e22";
        pillDot.style.boxShadow = "none";
      }
      if (sidebarStatus) {
        sidebarStatus.innerHTML = '<span style="color: #f39c12;">●</span> Standalone / Demo Mode';
      }
    }
    return false;
  },

  openBridgeModal() {
    const modal = document.getElementById("bridge-modal");
    if (!modal) return;
    const tokenInput = document.getElementById("bridge-token-input");
    if (tokenInput) tokenInput.value = this.bridgeToken;

    const title = document.getElementById("bridge-modal-status-title");
    const dot = document.getElementById("bridge-modal-status-dot");
    if (this.isLocalAgentConnected) {
      if (title) title.innerText = "Local Agent: Connected & Paired";
      if (dot) dot.style.background = "#27ae60";
    } else {
      if (title) title.innerText = "Local Agent: Not Reachable (Demo Mode Active)";
      if (dot) dot.style.background = "#e67e22";
    }
    modal.classList.add("active");
  },

  closeBridgeModal() {
    const modal = document.getElementById("bridge-modal");
    if (modal) modal.classList.remove("active");
  },

  async testBridgeConnection() {
    const connected = await this.checkBridgeConnection();
    if (connected) {
      alert("SUCCESS: Connected to Local Integration Agent on 127.0.0.1:8000!");
      this.closeBridgeModal();
      this.loadDashboardData();
    } else {
      alert("COULD NOT CONNECT:\nMake sure your local workbench server is running on 127.0.0.1:8000.\nRun: python -m backend.main");
    }
  },

  saveBridgeToken() {
    const tokenInput = document.getElementById("bridge-token-input");
    if (tokenInput) {
      this.bridgeToken = tokenInput.value.trim();
      localStorage.setItem("cpgrams_bridge_token", this.bridgeToken);
      alert("Local agent pairing token saved!");
      this.closeBridgeModal();
    }
  },

  setupNavigation() {
    document.querySelectorAll(".sidebar-nav .nav-item").forEach(item => {
      item.addEventListener("click", () => {
        const view = item.getAttribute("data-view");
        this.switchView(view);
      });
    });
  },

  switchView(viewName) {
    this.currentView = viewName;

    // Update sidebar active state
    document.querySelectorAll(".sidebar-nav .nav-item").forEach(item => {
      if (item.getAttribute("data-view") === viewName) {
        item.classList.add("active");
      } else {
        item.classList.remove("active");
      }
    });

    // Update main section views
    document.querySelectorAll(".view-section").forEach(sec => {
      sec.classList.remove("active-view");
    });
    const targetSec = document.getElementById(`view-${viewName}`);
    if (targetSec) {
      targetSec.classList.add("active-view");
    }

    // Set Top Header Title
    const titleMap = {
      dashboard: "Dashboard Overview",
      portal: "CPGRAMS Portal Assistant",
      intake: "Grievance Intake & Document Processing",
      register: "Grievance Register",
      detail: "Case Examination & Drafting Workspace",
      precedents: "Historical Disposed Grievance Library",
      routing: "Departmental Routing Assistant",
      correspondence: "Departmental Input Tracker",
      reports: "Operational Reports & Analytics",
      settings: "Settings, Security & Knowledge Management"
    };
    document.getElementById("current-view-title").innerText = titleMap[viewName] || "Workbench";

    // Trigger view-specific loads
    if (viewName === "dashboard") this.loadDashboardData();
    else if (viewName === "portal") PortalManager.checkStatus();
    else if (viewName === "register") RegisterManager.loadRegister();
    else if (viewName === "precedents") PrecedentManager.loadLibrary();
    else if (viewName === "routing") RoutingManager.loadRules();
    else if (viewName === "correspondence") CorrespondenceManager.loadMaster();
    else if (viewName === "reports") ReportsManager.loadReports();
    else if (viewName === "settings") SettingsManager.loadSettings();
  },

  setupPIIToggle() {
    const btn = document.getElementById("pii-toggle-btn");
    const label = document.getElementById("pii-toggle-text");
    btn.addEventListener("click", () => {
      this.maskPII = !this.maskPII;
      if (this.maskPII) {
        btn.classList.remove("active");
        label.innerText = "Mask PII: ON";
      } else {
        btn.classList.add("active");
        label.innerText = "Mask PII: OFF";
      }
      // Reload current register or detail if open
      if (this.currentView === "register") RegisterManager.loadRegister();
      else if (this.currentView === "detail" && this.currentCaseId) CaseWorkspace.loadCase(this.currentCaseId);
    });
  },

  async loadDashboardData() {
    let data = null;
    try {
      if (!window.MockStore || !MockStore.isStaticMode) {
        const res = await fetch(this.getApiUrl("/api/dashboard/stats"));
        if (res.ok) {
          data = await res.json();
        }
      }
    } catch (e) {
      console.warn("API not reachable, switching to static demo mode");
    }

    if (!data && window.MockStore) {
      data = MockStore.stats;
    }

    if (data) {
      document.getElementById("stat-total").innerText = data.total_grievances;
      document.getElementById("stat-new").innerText = data.new_grievances;
      document.getElementById("stat-pending").innerText = data.pending_grievances;
      document.getElementById("stat-disposed").innerText = data.disposed_grievances;
      document.getElementById("stat-inputs").innerText = data.awaiting_inputs;
      document.getElementById("stat-drafts").innerText = data.drafts_awaiting_review;
      document.getElementById("stat-approaching").innerText = data.approaching_deadlines;
      document.getElementById("stat-urgent").innerText = data.urgent_attention;

      document.getElementById("dash-sample-count").innerText = data.sample_records_count;
      document.getElementById("dash-real-count").innerText = data.real_records_count;

      const tbody = document.getElementById("dash-activity-tbody");
      if (!data.recent_activities || data.recent_activities.length === 0) {
        tbody.innerHTML = `<tr><td colspan="5" style="text-align:center; color: var(--text-muted);">No activity recorded yet.</td></tr>`;
      } else {
        tbody.innerHTML = data.recent_activities.map(a => `
          <tr>
            <td style="white-space: nowrap; font-size: 11.5px; color: var(--text-muted);">${new Date(a.timestamp).toLocaleString()}</td>
            <td><span class="badge badge-draft">${a.event_type}</span></td>
            <td><strong>${a.entity_type}</strong></td>
            <td>${a.details}</td>
            <td style="font-size: 11.5px; color: var(--text-muted);">${a.actor}</td>
          </tr>
        `).join("");
      }
    }
  },

  toast(message, type = "info") {
    // Standard subtle toast notice
    alert(message);
  }
};

window.addEventListener("DOMContentLoaded", () => {
  App.init();
});
