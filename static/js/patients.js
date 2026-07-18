console.log("Updated patients.js loaded");

(function () {
  const { api, formatApiError } = window.ReAdmitIQ;

  let currentPage = 1;
  const pageSize = 15;
  let searchTimer = null;

  const tbody = document.getElementById('patientsBody');
  const empty = document.getElementById('patientsEmpty');
  const pageInfo = document.getElementById('pageInfo');
  const resultCount = document.getElementById('resultCount');

  function badge(value, positiveClass = 'badge-yes', negativeClass = 'badge-no') {
    if (value == null) return '<span class="badge badge-no">—</span>';
    const cls = value === 'Yes' ? positiveClass : negativeClass;
    return `<span class="badge ${cls}">${value}</span>`;
  }

  // ===========================
  // Delete Patient
  // ===========================
  async function deletePatient(patientId) {

    if (!confirm(`Delete patient ${patientId}?`))
      return;

    const res = await api(`/api/patients/${patientId}`, {
      method: "DELETE"
    });

    if (!res)
      return;

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      alert(formatApiError(err.detail));
      return;
    }

    loadPatients();
  }

  // ===========================
  // Load Patients
  // ===========================
  async function loadPatients() {

    const search = document.getElementById('searchInput').value.trim();

    const res = await api(
      `/api/patients/?page=${currentPage}&page_size=${pageSize}&search=${encodeURIComponent(search)}`
    );

    if (!res || !res.ok) {

      empty.style.display = 'block';
      tbody.innerHTML = '';

      pageInfo.textContent = 'Unable to load patients.';
      resultCount.textContent = '';

      return;
    }

    const data = await res.json();

    const items = Array.isArray(data.items)
      ? data.items
      : (Array.isArray(data.data) ? data.data : []);

    const total = Number(data.total ?? data.count ?? 0);
    const totalPages = Number(data.total_pages ?? 1);

    const tableWrap = document.querySelector('.table-wrap');

    if (!items.length) {

      if (tableWrap)
        tableWrap.style.display = 'none';

      empty.style.display = 'block';
      tbody.innerHTML = '';

    } else {

      if (tableWrap)
        tableWrap.style.display = '';

      empty.style.display = 'none';
    }

    tbody.innerHTML = items.map(p => `
      <tr>
        <td class="mono">${p.patient_id ?? '—'}</td>
        <td>${p.age ?? '—'}</td>
        <td>${p.gender ?? '—'}</td>
        <td class="mono">${p.blood_pressure ?? '—'}</td>
        <td>${p.cholesterol ?? '—'}</td>
        <td>${p.bmi ?? '—'}</td>
        <td>${badge(p.diabetes)}</td>
        <td>${badge(p.hypertension)}</td>
        <td>${p.medication_count ?? '—'}</td>
        <td>${p.length_of_stay ?? '—'}</td>
        <td>${(p.discharge_destination || '').replace('_', ' ')}</td>
        <td>${badge(p.readmitted_30_days)}</td>

        <td>
          <button
            class="delete-btn"
            data-id="${p.patient_id}">
            Delete
          </button>
        </td>

      </tr>
    `).join('');

    // Register Delete button events
    document.querySelectorAll(".delete-btn").forEach(btn => {

      btn.addEventListener("click", () => {

        deletePatient(btn.dataset.id);

      });

    });

    pageInfo.textContent = `Page ${Number(data.page ?? currentPage)} of ${totalPages}`;
    resultCount.textContent = `${total.toLocaleString()} patients`;

    document.getElementById('prevPageBtn').disabled =
      Number(data.page ?? currentPage) <= 1;

    document.getElementById('nextPageBtn').disabled =
      Number(data.page ?? currentPage) >= totalPages;
  }

  // ===========================
  // Search
  // ===========================
  document.getElementById('searchInput').addEventListener('input', () => {

    clearTimeout(searchTimer);

    searchTimer = setTimeout(() => {

      currentPage = 1;
      loadPatients();

    }, 350);

  });

  // ===========================
  // Pagination
  // ===========================
  document.getElementById('prevPageBtn').addEventListener('click', () => {

    currentPage--;
    loadPatients();

  });

  document.getElementById('nextPageBtn').addEventListener('click', () => {

    currentPage++;
    loadPatients();

  });

  // ===========================
  // Upload CSV
  // ===========================
  const uploadBtn = document.getElementById('uploadBtn');
  const uploadPanel = document.getElementById('uploadPanel');

  uploadBtn.addEventListener('click', () => {

    uploadPanel.style.display =
      uploadPanel.style.display === 'none'
        ? 'flex'
        : 'none';

  });

  document.getElementById('csvSubmitBtn').addEventListener('click', async () => {

    const input = document.getElementById('csvInput');
    const resultEl = document.getElementById('uploadResult');

    if (!input.files.length) {

      resultEl.textContent = 'Choose a CSV file first.';
      return;

    }

    const formData = new FormData();

    formData.append('file', input.files[0]);

    resultEl.textContent = 'Uploading…';

    const res = await api('/api/patients/upload-csv', {

      method: 'POST',
      body: formData,
      headers: {},

    });

    if (!res)
      return;

    if (!res.ok) {

      const err = await res.json().catch(() => ({}));

      resultEl.textContent = `Error: ${formatApiError(err.detail)}`;

      return;
    }

    const data = await res.json();

    resultEl.textContent =
      `Imported ${data.inserted} rows.${data.warnings.length ? ' ' + data.warnings.join(' ') : ''}`;

    currentPage = 1;

    loadPatients();

  });

  // ===========================
  // Add Patient Modal
  // ===========================
  const modal = document.getElementById('addModal');

  document.getElementById('addPatientBtn').addEventListener('click', () => {

    modal.classList.add('show');

  });

  document.getElementById('closeModalBtn').addEventListener('click', () => {

    modal.classList.remove('show');

  });

  modal.addEventListener('click', (e) => {

    if (e.target === modal)
      modal.classList.remove('show');

  });

  document.getElementById('addPatientForm').addEventListener('submit', async (e) => {

    e.preventDefault();

    const errorEl = document.getElementById('addError');

    errorEl.classList.remove('show');

    const payload = {

      patient_id: document.getElementById('f_patient_id').value
        ? Number(document.getElementById('f_patient_id').value)
        : 0,

      age: Number(document.getElementById('f_age').value),

      gender: document.getElementById('f_gender').value,

      blood_pressure: document.getElementById('f_bp').value.trim(),

      cholesterol: Number(document.getElementById('f_cholesterol').value),

      bmi: Number(document.getElementById('f_bmi').value),

      diabetes: document.getElementById('f_diabetes').value,

      hypertension: document.getElementById('f_hypertension').value,

      medication_count: Number(document.getElementById('f_meds').value),

      length_of_stay: Number(document.getElementById('f_los').value),

      discharge_destination: document.getElementById('f_destination').value,

      readmitted_30_days: 'No',

    };

    const res = await api('/api/patients/', {

      method: 'POST',

      body: JSON.stringify(payload)

    });

    if (!res)
      return;

    if (!res.ok) {

      const err = await res.json().catch(() => ({}));

      errorEl.textContent = formatApiError(err.detail);

      errorEl.classList.add('show');

      return;

    }

    modal.classList.remove('show');

    e.target.reset();

    currentPage = 1;

    await loadPatients();

  });

  // ===========================
  // Initial Load
  // ===========================
  loadPatients();

})();