(async function () {
  const { api } = window.ReAdmitIQ;

  const chartTextColor = '#8FA3BC';
  const chartGridColor = 'rgba(38,58,86,0.6)';
  Chart.defaults.color = chartTextColor;
  Chart.defaults.font.family = "'IBM Plex Sans', sans-serif";

  async function loadStats() {
    const res = await api('/api/patients/stats');
    if (!res || !res.ok) return;
    const stats = await res.json();

    document.getElementById('statTotal').textContent = stats.total_patients.toLocaleString();
    document.getElementById('statRate').textContent = stats.readmission_rate + '%';
    document.getElementById('statRateDetail').textContent =
      `${stats.readmitted_count.toLocaleString()} of ${stats.total_patients.toLocaleString()} readmitted`;
    document.getElementById('statLos').textContent = stats.avg_length_of_stay;

    renderDestinationChart(stats.by_destination || {});
    renderGenderChart(stats.by_gender || {});
  }

  async function loadReportSummary() {
    const res = await api('/api/reports/summary');
    if (!res || !res.ok) return;
    const data = await res.json();
    document.getElementById('statPredictions').textContent = data.total_predictions_run.toLocaleString();
    document.getElementById('statPredictionsDetail').textContent =
      `${data.high_risk_predictions} flagged high risk`;
  }

  async function loadFeatureImportance() {
    const res = await api('/api/prediction/feature-importance');
    const list = document.getElementById('importanceList');
    if (!res || !res.ok) { list.innerHTML = '<p class="hint">Model not trained yet.</p>'; return; }
    const importances = await res.json();
    const labelMap = {
      discharge_enc: 'Discharge destination', bmi: 'BMI', cholesterol: 'Cholesterol',
      age: 'Age', systolic_bp: 'Systolic BP', diastolic_bp: 'Diastolic BP',
      medication_count: 'Medication count', length_of_stay: 'Length of stay',
      diabetes_enc: 'Diabetes', hypertension_enc: 'Hypertension', gender_enc: 'Gender',
    };
    const entries = Object.entries(importances);
    const max = Math.max(...entries.map(([, v]) => v), 0.0001);
    list.innerHTML = entries.map(([key, val]) => `
      <div class="importance-row">
        <div class="importance-label">${labelMap[key] || key}</div>
        <div class="importance-bar-track"><div class="importance-bar-fill" style="width:${(val / max) * 100}%"></div></div>
        <div class="importance-value">${(val * 100).toFixed(1)}%</div>
      </div>
    `).join('');
  }

  async function loadRecentPredictions() {
    const res = await api('/api/prediction/history?limit=8');
    const tbody = document.querySelector('#recentPredictionsTable tbody');
    const empty = document.getElementById('predictionsEmpty');
    if (!res || !res.ok) return;
    const rows = await res.json();
    if (!rows.length) {
      document.getElementById('recentPredictionsTable').style.display = 'none';
      empty.style.display = 'block';
      return;
    }
    tbody.innerHTML = rows.map(r => {
      const badge = r.risk_label === 'High' ? 'badge-high' : r.risk_label === 'Medium' ? 'badge-medium' : 'badge-low';
      const when = new Date(r.created_at * 1000).toLocaleString();
      return `<tr>
        <td>#${r.patient_ref ?? '—'}</td>
        <td><span class="badge ${badge}">${r.risk_label}</span></td>
        <td class="mono">${(r.risk_score * 100).toFixed(1)}%</td>
        <td>${when}</td>
      </tr>`;
    }).join('');
  }

  function renderDestinationChart(byDestination) {
    const ctx = document.getElementById('destinationChart');
    new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels: Object.keys(byDestination),
        datasets: [{
          data: Object.values(byDestination),
          backgroundColor: ['#3FBFAD', '#F2B138', '#F2545B', '#5E7291'],
          borderColor: '#16263D',
          borderWidth: 2,
        }],
      },
      options: {
        plugins: { legend: { position: 'bottom', labels: { boxWidth: 10, padding: 16 } } },
        cutout: '65%',
      },
    });
  }

  function renderGenderChart(byGender) {
    const ctx = document.getElementById('genderChart');
    new Chart(ctx, {
      type: 'bar',
      data: {
        labels: Object.keys(byGender),
        datasets: [{
          label: 'Patients',
          data: Object.values(byGender),
          backgroundColor: '#3FBFAD',
          borderRadius: 6,
          maxBarThickness: 56,
        }],
      },
      options: {
        plugins: { legend: { display: false } },
        scales: {
          x: { grid: { display: false } },
          y: { grid: { color: chartGridColor }, beginAtZero: true },
        },
      },
    });
  }

  loadStats();
  loadReportSummary();
  loadFeatureImportance();
  loadRecentPredictions();
})();
