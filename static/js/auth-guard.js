(function () {
  const token = localStorage.getItem('readmitiq_token');
  if (!token) {
    window.location.href = '/login';
    return;
  }

  const userRaw = localStorage.getItem('readmitiq_user');
  const user = userRaw ? JSON.parse(userRaw) : null;

  if (user) {
    const nameEl = document.getElementById('userName');
    const roleEl = document.getElementById('userRole');
    const avatarEl = document.getElementById('userAvatar');
    if (nameEl) nameEl.textContent = user.full_name || user.email;
    if (roleEl) roleEl.textContent = (user.role || 'clinician').replace('_', ' ');
    if (avatarEl) {
      const initials = (user.full_name || user.email || '?')
        .split(' ').map(w => w[0]).slice(0, 2).join('').toUpperCase();
      avatarEl.textContent = initials;
    }
  }

  const path = window.location.pathname.replace('/', '') || 'dashboard';
  document.querySelectorAll('.nav-item').forEach(el => {
    if (el.dataset.page === path) el.classList.add('active');
  });

  const logoutBtn = document.getElementById('logoutBtn');
  if (logoutBtn) {
    logoutBtn.addEventListener('click', () => {
      localStorage.removeItem('readmitiq_token');
      localStorage.removeItem('readmitiq_user');
      window.location.href = '/login';
    });
  }

  function authHeaders(isFormData) {
    const headers = { 'Authorization': `Bearer ${token}` };
    if (!isFormData) headers['Content-Type'] = 'application/json';
    return headers;
  }

  async function api(path, options = {}) {
    const isFormData = options.body instanceof FormData;
    const res = await fetch(path, {
      ...options,
      headers: { ...authHeaders(isFormData), ...(options.headers || {}) },
    });
    if (res.status === 401) {
      localStorage.removeItem('readmitiq_token');
      localStorage.removeItem('readmitiq_user');
      window.location.href = '/login';
      return null;
    }
    return res;
  }

  function formatApiError(detail) {
    if (!detail) return 'Something went wrong. Please try again.';
    if (typeof detail === 'string') return detail;
    if (Array.isArray(detail)) {
      return detail.map(d => {
        if (typeof d === 'string') return d;
        const loc = Array.isArray(d.loc) ? d.loc.filter(x => x !== 'body').join('.') : '';
        return loc ? `${loc}: ${d.msg}` : (d.msg || JSON.stringify(d));
      }).join('; ');
    }
    if (typeof detail === 'object') return detail.msg || JSON.stringify(detail);
    return String(detail);
  }

  window.ReAdmitIQ = { token, user, authHeaders, api, formatApiError };
})();