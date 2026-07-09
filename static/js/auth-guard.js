// Shared across every authenticated page: verifies a token exists, fills in
// the sidebar user chip, highlights the active nav item, and wires logout.
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

  window.ReAdmitIQ = {
    token,
    user,
    authHeaders(isFormData) {
      const headers = { 'Authorization': `Bearer ${token}` };
      if (!isFormData) headers['Content-Type'] = 'application/json';
      return headers;
    },
    async api(path, options = {}) {
      const isFormData = options.body instanceof FormData;
      const res = await fetch(path, {
        ...options,
        headers: { ...this.authHeaders(isFormData), ...(options.headers || {}) },
      });
      if (res.status === 401) {
        localStorage.removeItem('readmitiq_token');
        localStorage.removeItem('readmitiq_user');
        window.location.href = '/login';
        return null;
      }
      return res;
    },
  };
})();
