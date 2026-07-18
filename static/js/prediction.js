(function () {
  const { api, formatApiError } = window.ReAdmitIQ;
  const ARC_LENGTH = 314.16;

  const colors = { Low: '#3FBFAD', Medium: '#F2B138', High: '#F2545B' };
  const advice = {
    Low: 'Standard discharge follow-up is likely sufficient.',
    Medium: 'Consider a follow-up call within 7 days.',
    High: 'Recommend care-coordinator outreach before discharge and a follow-up visit within 72 hours.',
  };

  // Must match app/ml/predictor.py's FEATURE_LABELS exactly, since
  // renderFeatureImportance() looks up SHAP direction by this label text.
  const FEATURE_LABELS = {
    age: 'Age',
    gender_enc: 'Gender',
    systolic_bp: 'Systolic blood pressure',
    diastolic_bp: 'Diastolic blood pressure',
    cholesterol: 'Cholesterol',
    bmi: 'BMI',
    diabetes_enc: 'Diabetes',
    hypertension_enc: 'Hypertension',
    medication_count: 'Medication count',
    length_of_stay: 'Length of stay',
    discharge_enc: 'Discharge destination',
  };

  // The global feature-importance list doesn't change per-patient, so it's
  // fetched once on page load (not returned by /api/prediction/predict) and
  // re-rendered with fresh color-coding after each prediction.
  let cachedImportances = null;

  document.getElementById('predictForm').addEventListener('submit', submitPrediction);

  async function submitPrediction(e) {
    e.preventDefault();
    const errorEl = document.getElementById('predictError');
    errorEl.classList.remove('show');

    const btn = document.getElementById('predictBtn');
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner"></span> Scoring…';

    clearExplainability();

    const payload = {
      patient_id: document.getElementById('p_patient_id').value ? Number(document.getElementById('p_patient_id').value) : null,
      age: Number(document.getElementById('p_age').value),
      gender: document.getElementById('p_gender').value,
      blood_pressure: document.getElementById('p_bp').value,
      cholesterol: Number(document.getElementById('p_cholesterol').value),
      bmi: Number(document.getElementById('p_bmi').value),
      diabetes: document.getElementById('p_diabetes').value,
      hypertension: document.getElementById('p_hypertension').value,
      medication_count: Number(document.getElementById('p_meds').value),
      length_of_stay: Number(document.getElementById('p_los').value),
      discharge_destination: document.getElementById('p_destination').value,
    };

    try {
      const response = await api('/api/prediction/predict', { method: 'POST', body: JSON.stringify(payload) });
      if (!response) return;
      if (!response.ok) {
        const err = await response.json().catch(() => ({}));
        throw new Error(formatApiError(err.detail));
      }

      const result = await response.json();
      renderGauge(result);
      renderExplanation(result.explanation);

      if (!cachedImportances) {
        cachedImportances = await fetchFeatureImportance();
      }
      if (cachedImportances) {
        renderFeatureImportance(cachedImportances, result.explanation);
      }
    } catch (err) {
      errorEl.textContent = err.message;
      errorEl.classList.add('show');
    } finally {
      btn.disabled = false;
      btn.textContent = 'Calculate risk score';
    }
  }

  async function fetchFeatureImportance() {
    try {
      const res = await api('/api/prediction/feature-importance');
      if (!res || !res.ok) return null;
      return await res.json();
    } catch {
      return null;
    }
  }

  function renderGauge(result) {
    const arc = document.getElementById('gaugeArc');
    const score = document.getElementById('gaugeScore');
    const label = document.getElementById('gaugeLabel');
    const hint = document.getElementById('gaugeHint');
    const color = colors[result.risk_label] || '#3FBFAD';
    const dash = (result.risk_percent / 100) * ARC_LENGTH;

    arc.setAttribute('stroke', color);
    arc.style.transition = 'stroke-dasharray 0.6s ease';
    arc.setAttribute('stroke-dasharray', `${dash} ${ARC_LENGTH}`);

    score.textContent = `${result.risk_percent}%`;
    score.style.color = color;
    label.textContent = `${result.risk_label} risk of 30-day readmission`;
    hint.textContent = advice[result.risk_label] || '';
  }

  function renderExplanation(explanation) {
    const box = document.getElementById('explainBox');
    if (!box) return;
    box.classList.remove('hidden');

    const summaryEl = document.getElementById('explainSummary');
    const increasingEl = document.getElementById('riskIncreasingFactors');
    const decreasingEl = document.getElementById('riskDecreasingFactors');

    if (!explanation) {
      summaryEl.textContent = 'An explanation could not be generated for this prediction.';
      increasingEl.innerHTML = '';
      decreasingEl.innerHTML = '';
      return;
    }

    summaryEl.textContent = explanation.summary || '';

    const factors = explanation.top_factors || [];
    const increasing = factors.filter(f => f.direction === 'increases_risk');
    const decreasing = factors.filter(f => f.direction === 'decreases_risk');
    // Scale each card's impact bar relative to the single largest factor
    // across BOTH groups, so bar length is comparable at a glance.
    const maxImpact = Math.max(...factors.map(f => f.impact), 0.0001);

    increasingEl.innerHTML = renderFactorGroup('Factors increasing risk', increasing, 'up', maxImpact);
    decreasingEl.innerHTML = renderFactorGroup('Factors decreasing risk', decreasing, 'down', maxImpact);
  }

  function renderFactorGroup(heading, factors, dir, maxImpact) {
    if (!factors.length) return '';
    const icon = dir === 'up' ? '▲' : '▼';
    const dirClass = dir === 'up' ? 'risk-up' : 'risk-down';

    const cards = factors.map((f, idx) => `
      <div class="factor-card">
        <div class="factor-rank">${idx + 1}</div>
        <div class="factor-icon ${dirClass}">${icon}</div>
        <div class="factor-body">
          <div class="factor-title">${f.label}</div>
          <div class="factor-value">${f.value}</div>
        </div>
        <div class="factor-impact-wrap">
          <div class="factor-impact">${(f.impact * 100).toFixed(1)}%</div>
          <div class="factor-impact-track">
            <div class="factor-impact-fill ${dirClass}" style="width:${(f.impact / maxImpact) * 100}%"></div>
          </div>
        </div>
      </div>
    `).join('');

    return `<div class="factor-group-heading">${heading}</div>${cards}`;
  }

  function renderFeatureImportance(importances, explanation) {
    const container = document.getElementById('featureImportance');
    if (!container || !importances) return;
    container.innerHTML = '';

    const directions = {};
    if (explanation && explanation.top_factors) {
      explanation.top_factors.forEach(f => { directions[f.label] = f.direction; });
    }

    const entries = Object.entries(importances);
    const max = Math.max(...entries.map(e => e[1]), 0.0001);

    entries.slice(0, 8).forEach(([feature, value]) => {
      const label = formatLabel(feature);
      const direction = directions[label];
      let color = '#3FBFAD';
      if (direction === 'increases_risk') color = '#F2545B';
      if (direction === 'decreases_risk') color = '#47C97A';

      const row = document.createElement('div');
      row.className = 'importance-row';
      row.innerHTML = `
        <div class="importance-label">${label}</div>
        <div class="importance-bar-track">
          <div class="importance-bar-fill" style="width:${(value / max) * 100}%; background:${color};"></div>
        </div>
        <div class="importance-value">${value.toFixed(3)}</div>
      `;
      container.appendChild(row);
    });
  }

  function clearExplainability() {
    const box = document.getElementById('explainBox');
    if (box) box.classList.add('hidden');

    const summary = document.getElementById('explainSummary');
    if (summary) summary.textContent = '';

    const increasing = document.getElementById('riskIncreasingFactors');
    if (increasing) increasing.innerHTML = '';

    const decreasing = document.getElementById('riskDecreasingFactors');
    if (decreasing) decreasing.innerHTML = '';
  }

  function formatLabel(feature) {
    return FEATURE_LABELS[feature] || feature;
  }

  // Feature importance is a static property of the trained model, not
  // per-patient, so load it once up front rather than waiting on a prediction.
  (async function preloadFeatureImportance() {
    cachedImportances = await fetchFeatureImportance();
    if (cachedImportances) renderFeatureImportance(cachedImportances, null);
  })();
})();
