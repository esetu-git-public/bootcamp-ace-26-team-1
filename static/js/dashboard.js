(async function () {
  const { api } = window.ReAdmitIQ;
  const palette = ['#3FBFAD', '#F2B138', '#F2545B', '#5E7291', '#6C7CFF', '#2CA58D'];

  async function loadStats() {
    const res = await api('/api/patients/stats');
    if (!res || !res.ok) return;
    const stats = await res.json();

    document.getElementById('statTotal').textContent = stats.total_patients.toLocaleString();
    document.getElementById('statRate').textContent = `${stats.readmission_rate}%`;
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
    const entries = Object.entries(importances || {});
    if (!entries.length) {
      list.innerHTML = '<p class="hint">Model not trained yet.</p>';
      return;
    }
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
    const container = document.getElementById('destinationChart');
    if (!container) return;

    const entries = Object.entries(byDestination || {});
    if (!entries.length) {
      container.innerHTML = '<div class="chart-empty">No discharge data yet.</div>';
      return;
    }

    const total = entries.reduce((sum, [, value]) => sum + value, 0);
    const radius = 54;
    const circumference = 2 * Math.PI * radius;
    let offset = 0;
    const segments = entries.map(([label, value], index) => {
      const dash = (value / total) * circumference;
      const segment = `<circle cx="70" cy="70" r="${radius}" fill="none" stroke="${palette[index % palette.length]}" stroke-width="18" stroke-linecap="round" stroke-dasharray="${dash} ${circumference - dash}" stroke-dashoffset="${-offset}" transform="rotate(-90 70 70)"></circle>`;
      offset += dash;
      return segment;
    }).join('');

    const legend = entries.map(([label, value], index) => `
      <div class="item">
        <span class="dot" style="background:${palette[index % palette.length]}"></span>
        <span>${label} (${value})</span>
      </div>
    `).join('');

    container.innerHTML = `
      <div class="chart-donut-wrap">
        <svg viewBox="0 0 140 140" class="chart-donut">
          <circle cx="70" cy="70" r="${radius}" fill="none" stroke="rgba(255,255,255,0.08)" stroke-width="18"></circle>
          ${segments}
        </svg>
        <div class="chart-donut-center">
          <div class="chart-donut-total">${total}</div>
          <div class="chart-donut-label">patients</div>
        </div>
      </div>
      <div class="mini-legend">${legend}</div>
    `;
  }

  function renderGenderChart(byGender) {
    const container = document.getElementById('genderChart');
    if (!container) return;

    const entries = Object.entries(byGender || {});
    if (!entries.length) {
      container.innerHTML = '<div class="chart-empty">No gender data yet.</div>';
      return;
    }

    const max = Math.max(...entries.map(([, value]) => value), 1);
    const colorMap = {
      Male: '#0096FF',
      Female: '#DE3163',
      Unknown: '#3FBFAD',
    };
    container.innerHTML = `
      <div class="bar-chart">
        ${entries.map(([label, value]) => `
          <div class="bar-column">
            <div class="bar-track">
              <div class="bar-fill" style="height:${(value / max) * 100}%; background:${colorMap[label] || '#3FBFAD'}"></div>
            </div>
            <div class="bar-label">${label}</div>
            <div class="bar-value">${value}</div>
          </div>
        `).join('')}
      </div>
    `;
  }

  loadStats();
  loadReportSummary();
  loadFeatureImportance();
  loadRecentPredictions();
})();
