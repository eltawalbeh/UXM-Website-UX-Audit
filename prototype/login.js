const form = document.querySelector('.route-form');
const status = document.querySelector('#login-status');
const submit = form.querySelector('button[type="submit"]');

async function readJson(response) {
  try { return await response.json(); } catch { return {}; }
}

async function checkSession() {
  try {
    const response = await fetch('/api/auth/session', { credentials: 'same-origin' });
    const session = await readJson(response);
    if (session.authenticated) window.location.assign('/workspace.html');
  } catch {
    // The form remains usable when the local server is temporarily unavailable.
  }
}

form.addEventListener('submit', async event => {
  event.preventDefault();
  const credentials = Object.fromEntries(new FormData(form));
  submit.disabled = true;
  status.textContent = 'Signing in…';
  try {
    const response = await fetch('/api/auth/login', {
      method: 'POST',
      credentials: 'same-origin',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(credentials),
    });
    const body = await readJson(response);
    if (!response.ok || !body.authenticated) throw new Error(body.error || 'Login failed');
    window.location.assign('/workspace.html');
  } catch (error) {
    status.textContent = error.message || 'Unable to sign in.';
    form.querySelector('[name="password"]').value = '';
    submit.disabled = false;
  }
});

checkSession();
