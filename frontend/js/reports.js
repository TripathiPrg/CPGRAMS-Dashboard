/**
 * Reports and Analytics Controller
 */

const ReportsManager = {
  async loadReports() {
    try {
      const res = await fetch("/api/reports/summary");
      const data = await res.json();

      // 1. Ageing breakdown
      const ageing = data.ageing_breakdown;
      document.getElementById("rep-age-7").innerText = ageing["0_to_7_days"];
      document.getElementById("rep-age-15").innerText = ageing["8_to_15_days"];
      document.getElementById("rep-age-30").innerText = ageing["16_to_30_days"];
      document.getElementById("rep-age-over30").innerText = ageing["over_30_days"];

      // 2. Categories
      const catTbody = document.getElementById("rep-cat-tbody");
      if (data.categories_breakdown && data.categories_breakdown.length > 0) {
        catTbody.innerHTML = data.categories_breakdown.map(c => `
          <tr>
            <td><strong>${c.category}</strong></td>
            <td style="font-weight: 700; color: var(--meity-blue);">${c.count}</td>
          </tr>
        `).join("");
      } else {
        catTbody.innerHTML = `<tr><td colspan="2" style="text-align:center;">No data available</td></tr>`;
      }

      // 3. Precedent metrics
      const p = data.precedent_metrics;
      document.getElementById("rep-prec-total").innerText = p.total_precedents_in_library;
      document.getElementById("rep-prec-useful").innerText = p.approved_useful_precedents;
      document.getElementById("rep-prec-outdated").innerText = p.outdated_flagged_precedents;
      document.getElementById("rep-drafts-total").innerText = p.drafts_generated;

    } catch (e) {
      console.error("Error loading reports", e);
    }
  }
};
