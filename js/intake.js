/**
 * Document Intake & Processing Controller
 * Handles document parsing, OCR scan detection, text extraction,
 * and manual pre-commit verification.
 */

const IntakeManager = {
  currentExtracted: null,
  currentFilename: null,

  setMode(mode) {
    const fileContainer = document.getElementById("intake-file-container");
    const textContainer = document.getElementById("intake-text-container");
    const btnFile = document.getElementById("tab-btn-file");
    const btnText = document.getElementById("tab-btn-text");

    if (mode === "file") {
      fileContainer.style.display = "block";
      textContainer.style.display = "none";
      btnFile.className = "btn btn-primary";
      btnText.className = "btn btn-outline";
    } else {
      fileContainer.style.display = "none";
      textContainer.style.display = "block";
      btnFile.className = "btn btn-outline";
      btnText.className = "btn btn-primary";
    }
  },

  async handleFileSelect(input) {
    if (!input.files || input.files.length === 0) return;
    const file = input.files[0];
    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch("/api/intake/upload", {
        method: "POST",
        body: formData
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Upload failed");

      if (data.is_batch) {
        alert(`Detected tabular batch with ${data.batch_count} records. Importing batch into register...`);
        // Batch auto-import
        await fetch("/api/portal/import", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(data.batch_records)
        });
        alert("Batch imported successfully!");
        App.switchView("register");
        return;
      }

      this.currentExtracted = data.extracted;
      this.currentFilename = data.filename;
      this.populatePreview(data.extracted, data.is_duplicate);

    } catch (e) {
      alert(`File processing error: ${e.message}`);
    } finally {
      input.value = "";
    }
  },

  async parsePastedText() {
    const text = document.getElementById("intake-pasted-text").value.strip ? document.getElementById("intake-pasted-text").value.trim() : document.getElementById("intake-pasted-text").value;
    if (!text) {
      alert("Please paste grievance text first.");
      return;
    }

    try {
      const res = await fetch("/api/intake/parse-text", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text })
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Parse failed");

      this.currentExtracted = data.extracted;
      this.currentFilename = "Pasted_Text_Intake.txt";
      this.populatePreview(data.extracted, data.is_duplicate);
    } catch (e) {
      alert(`Parsing error: ${e.message}`);
    }
  },

  populatePreview(ext, isDuplicate) {
    const card = document.getElementById("intake-preview-card");
    const dupBadge = document.getElementById("intake-dup-badge");

    card.style.display = "block";

    if (isDuplicate) {
      dupBadge.className = "badge badge-urgent";
      dupBadge.innerText = "DUPLICATE: Reg No already in Database";
    } else {
      dupBadge.className = "badge badge-approved";
      dupBadge.innerText = "NEW UNIQUE RECORD";
    }

    if (ext.is_scanned) {
      alert("NOTICE: Document appears to be a scanned image or non-selectable PDF. Text layer extracted may be limited. Please verify fields manually.");
    }

    document.getElementById("intake-field-reg").value = ext.registration_no || "";
    document.getElementById("intake-field-date").value = ext.date_received || new Date().toISOString().split("T")[0];
    document.getElementById("intake-field-name").value = ext.applicant_name || "";
    document.getElementById("intake-field-contact").value = ext.applicant_contact || "";
    document.getElementById("intake-field-subject").value = ext.subject || "";
    document.getElementById("intake-field-category").value = ext.category || "AI & Emerging Technologies";
    document.getElementById("intake-field-priority").value = "Normal";
    document.getElementById("intake-field-relief").value = ext.requested_relief || "";
    document.getElementById("intake-field-text").value = ext.grievance_text || "";

    card.scrollIntoView({ behavior: "smooth" });
  },

  cancelPreview() {
    document.getElementById("intake-preview-card").style.display = "none";
    this.currentExtracted = null;
  },

  async confirmIntake() {
    const payload = {
      registration_no: document.getElementById("intake-field-reg").value.trim(),
      date_received: document.getElementById("intake-field-date").value,
      applicant_name: document.getElementById("intake-field-name").value.trim(),
      applicant_contact: document.getElementById("intake-field-contact").value.trim(),
      subject: document.getElementById("intake-field-subject").value.trim(),
      category: document.getElementById("intake-field-category").value,
      priority: document.getElementById("intake-field-priority").value,
      requested_relief: document.getElementById("intake-field-relief").value.trim(),
      grievance_text: document.getElementById("intake-field-text").value.trim(),
      source_type: "manual_upload",
      source_filename: this.currentFilename
    };

    if (!payload.registration_no) {
      alert("Registration number is mandatory.");
      return;
    }

    try {
      const res = await fetch("/api/intake/confirm", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Confirmation failed");

      alert(`Grievance ${data.registration_no} successfully saved and analyzed! Opening case workspace...`);
      this.cancelPreview();
      CaseWorkspace.openCase(data.id);
    } catch (e) {
      alert(`Error saving grievance: ${e.message}`);
    }
  }
};
