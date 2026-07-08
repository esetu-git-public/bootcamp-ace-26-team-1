(function () {
  const { api, token } = window.ReAdmitIQ;

  async function loadSummary() {
    const res = await api('/api/reports/summary');
    if (!res || !res.ok) return;
    const data = await res.json();

    document.getElementById('rTotal').textContent = data.total_patients.toLocaleString();
    document.getElementById('rRate').textContent = data.readmission_rate + '%';
    document.getElementById('rAvgRisk').textContent = data.avg_predicted_risk + '%';
    document.getElementById('rHighRisk').textContent = data.high_risk_predictions;

    const dest = data.by_destination || {};
    const total = Object.values(dest).reduce((a, b) => a + b, 0) || 1;
    const container = document.getElementById('destinationBreakdown');
    container.innerHTML = Object.entries(dest).map(([label, count]) => `
      <div class="importance-row">
        <div class="importance-label">${label.replace('_', ' ')}</div>
        <div class="importance-bar-track"><div class="importance-bar-fill" style="width:${(count / total) * 100}%"></div></div>
        <div class="importance-value">${count}</div>
      </div>
    `).join('') || '<p class="hint">No patient data yet.</p>';
  }

  async function downloadCsv(path, filename) {
    const res = await fetch(path, { headers: { Authorization: `Bearer ${token}` } });
    if (!res.ok) { alert('Export failed.'); return; }
    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url; a.download = filename;
    document.body.appendChild(a); a.click(); a.remove();
    URL.revokeObjectURL(url);
  }

  document.getElementById('exportPatientsBtn').addEventListener('click', (e) => {
    e.preventDefault();
    downloadCsv('/api/reports/export/patients', 'patients_export.csv');
  });
  document.getElementById('exportPredictionsBtn').addEventListener('click', (e) => {
    e.preventDefault();
    downloadCsv('/api/reports/export/predictions', 'predictions_export.csv');
  });

  loadSummary();
})();
