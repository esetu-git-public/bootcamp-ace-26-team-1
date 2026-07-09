(function () {
  const { api } = window.ReAdmitIQ;

  const actionColors = {
    login: 'badge-low', signup: 'badge-low', predict: 'badge-medium',
    predict_batch: 'badge-medium', create_patient: 'badge-low',
    upload_csv: 'badge-low', export_patients_csv: 'badge-no', export_predictions_csv: 'badge-no',
  };

  async function loadLogs() {
    const res = await api('/api/audit/logs?limit=200');
    if (!res || !res.ok) return;
    const rows = await res.json();
    const tbody = document.getElementById('auditBody');
    const empty = document.getElementById('auditEmpty');

    if (!rows.length) {
      document.querySelector('.table-wrap').style.display = 'none';
      empty.style.display = 'block';
      return;
    }
    document.querySelector('.table-wrap').style.display = '';
    empty.style.display = 'none';

    tbody.innerHTML = rows.map(r => {
      const cls = actionColors[r.action] || 'badge-no';
      const when = new Date(r.created_at * 1000).toLocaleString();
      return `<tr>
        <td>${r.actor}</td>
        <td><span class="badge ${cls}">${r.action.replace('_', ' ')}</span></td>
        <td>${r.details || '—'}</td>
        <td>${when}</td>
      </tr>`;
    }).join('');
  }

  document.getElementById('refreshBtn').addEventListener('click', loadLogs);
  loadLogs();
})();
