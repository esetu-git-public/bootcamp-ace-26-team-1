(function () {
  const { api, formatApiError } = window.ReAdmitIQ;
  const ARC_LENGTH = 314.16;

  const colors = { Low: '#3FBFAD', Medium: '#F2B138', High: '#F2545B' };

  document.getElementById('predictForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const errorEl = document.getElementById('predictError');
    errorEl.classList.remove('show');

    const btn = document.getElementById('predictBtn');
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner"></span> Scoring…';

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
      const res = await api('/api/prediction/predict', { method: 'POST', body: JSON.stringify(payload) });
      if (!res) return;
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(formatApiError(err.detail));
      }
      const result = await res.json();
      renderGauge(result);
    } catch (err) {
      errorEl.textContent = err.message;
      errorEl.classList.add('show');
    } finally {
      btn.disabled = false;
      btn.textContent = 'Calculate risk score';
    }
  });

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

    const advice = {
      Low: 'Standard discharge follow-up is likely sufficient.',
      Medium: 'Consider a follow-up call within 7 days.',
      High: 'Recommend care-coordinator outreach before discharge and a follow-up visit within 72 hours.',
    };
    hint.textContent = advice[result.risk_label] || '';
  }
})();
