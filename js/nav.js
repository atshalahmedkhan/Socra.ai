/* js/nav.js — Shared nav actions (CSP-safe, no inline handlers) */

document.addEventListener('DOMContentLoaded', () => {
  const avatar = document.getElementById('nav-avatar');
  if (avatar) avatar.addEventListener('click', logout);
  const logoutBtn = document.getElementById('logout-btn');
  if (logoutBtn) logoutBtn.addEventListener('click', logout);
});
