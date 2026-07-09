(function () {
  const tabs = document.querySelectorAll('.tab-switch button');
  const panels = { login: document.getElementById('loginForm'), signup: document.getElementById('signupForm') };
  const heading = document.getElementById('formHeading');
  const sub = document.getElementById('formSub');
  const errorBanner = document.getElementById('errorBanner');
  const successBanner = document.getElementById('successBanner');

  const copy = {
    login: { h: 'Welcome back', s: 'Sign in to your clinical dashboard.' },
    signup: { h: 'Create your account', s: 'Set up access to the readmission dashboard.' },
  };

  function showTab(name) {
    tabs.forEach(t => t.classList.toggle('active', t.dataset.tab === name));
    Object.entries(panels).forEach(([k, el]) => el.classList.toggle('active', k === name));
    heading.textContent = copy[name].h;
    sub.textContent = copy[name].s;
    hideMessages();
  }

  tabs.forEach(t => t.addEventListener('click', () => showTab(t.dataset.tab)));

  function hideMessages() {
    errorBanner.classList.remove('show');
    successBanner.classList.remove('show');
  }
  function showError(msg) {
    errorBanner.textContent = msg;
    errorBanner.classList.add('show');
    successBanner.classList.remove('show');
  }
  function showSuccess(msg) {
    successBanner.textContent = msg;
    successBanner.classList.add('show');
    errorBanner.classList.remove('show');
  }

  async function callApi(path, body) {
    const res = await fetch(path, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(data.detail || 'Something went wrong. Please try again.');
    return data;
  }

  function completeAuth(data) {
    localStorage.setItem('readmitiq_token', data.access_token);
    localStorage.setItem('readmitiq_user', JSON.stringify(data.user));
    window.location.href = '/dashboard';
  }

  document.getElementById('loginForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    hideMessages();
    const btn = document.getElementById('loginBtn');
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner"></span> Signing in…';
    try {
      const data = await callApi('/api/auth/login', {
        email: document.getElementById('loginEmail').value.trim(),
        password: document.getElementById('loginPassword').value,
      });
      showSuccess('Signed in — redirecting…');
      setTimeout(() => completeAuth(data), 400);
    } catch (err) {
      showError(err.message);
      btn.disabled = false;
      btn.textContent = 'Sign in';
    }
  });

  document.getElementById('signupForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    hideMessages();
    const btn = document.getElementById('signupBtn');
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner"></span> Creating account…';
    try {
      const data = await callApi('/api/auth/signup', {
        email: document.getElementById('signupEmail').value.trim(),
        password: document.getElementById('signupPassword').value,
        full_name: document.getElementById('signupName').value.trim(),
        role: document.getElementById('signupRole').value,
      });
      showSuccess('Account created — redirecting…');
      setTimeout(() => completeAuth(data), 400);
    } catch (err) {
      showError(err.message);
      btn.disabled = false;
      btn.textContent = 'Create account';
    }
  });

  // If already logged in, skip straight to the dashboard.
  if (localStorage.getItem('readmitiq_token')) {
    window.location.href = '/dashboard';
  }
})();
