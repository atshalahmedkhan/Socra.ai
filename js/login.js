/* js/login.js — Mock sign-in (requires js/data.js + js/auth.js) */

document.addEventListener('DOMContentLoaded', () => {
  localStorage.removeItem('token');
  sessionStorage.removeItem('token');

  if (localStorage.getItem('currentUser') || sessionStorage.getItem('currentUser')) {
    window.location.href = 'index.html';
    return;
  }

  const saved = localStorage.getItem('savedUserId');
  if (saved) document.getElementById('userId').value = saved;

  document.getElementById('login-form').addEventListener('submit', (e) => {
    e.preventDefault();
    const userId = document.getElementById('userId').value.trim().toUpperCase();
    const password = document.getElementById('password').value.trim();
    const remember = document.getElementById('rememberMe').checked;
    const errorMsg = document.getElementById('error-msg');

    const uid = AUTH_UID_BY_LOGIN[userId];
    if (uid && verifyLogin(userId, password)) {
      if (remember) {
        localStorage.setItem('currentUser', uid);
        sessionStorage.removeItem('currentUser');
      } else {
        sessionStorage.setItem('currentUser', uid);
        localStorage.removeItem('currentUser');
      }
      localStorage.setItem('savedUserId', userId);
      window.location.href = 'index.html';
    } else {
      errorMsg.textContent = 'Invalid User ID or Password';
      errorMsg.style.display = 'block';
    }
  });
});
