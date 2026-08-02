/* js/index-page.js */
markActive('overview');
updateNavUser();

const today = new Date();
const demo = new Date(2026, 7, 20);
const daysLeft = Math.max(0, Math.ceil((demo - today) / 86400000));
document.getElementById('days-left').textContent = daysLeft;

const phaseList = document.getElementById('phase-list');
window.serverData = { phaseStatuses: {} };

function appendPhaseRow(el, dot, info, statusEl, actionBtn) {
  el.appendChild(dot);
  el.appendChild(info);
  el.appendChild(statusEl);
  if (actionBtn) el.appendChild(actionBtn);
  phaseList.appendChild(el);
}

function makePhaseBtn(className, label, onClick, options) {
  const btn = document.createElement('button');
  btn.type = 'button';
  btn.className = className;
  btn.style.cssText = 'margin-left:auto;padding:2px 8px;font-size:11px';
  btn.textContent = label;
  btn.addEventListener('click', onClick);
  if (options && options.hoverLabel) {
    btn.classList.add('phase-undo-btn');
    btn.dataset.defaultLabel = label;
    btn.dataset.hoverLabel = options.hoverLabel;
    btn.addEventListener('mouseenter', () => {
      btn.textContent = btn.dataset.hoverLabel;
    });
    btn.addEventListener('mouseleave', () => {
      btn.textContent = btn.dataset.defaultLabel;
    });
  }
  return btn;
}

function renderPhases() {
  phaseList.replaceChildren();
  const isOwner = currentUser() === 'owner';

  PHASES.forEach((p, i) => {
    const status = window.serverData.phaseStatuses[i] || 'pending';
    let statusText;
    let statusBg = 'var(--surface2)';
    let statusTx;

    const el = document.createElement('div');
    el.className = 'phase-item';

    const dot = document.createElement('div');
    dot.className = 'phase-dot';
    dot.style.background = p.border;

    const info = document.createElement('div');
    info.className = 'phase-info';
    const name = document.createElement('div');
    name.className = 'phase-name';
    name.textContent = p.label;
    const dates = document.createElement('div');
    dates.className = 'phase-dates';
    dates.textContent = fmtShort(p.start) + ' – ' + fmtShort(p.end);
    info.appendChild(name);
    info.appendChild(dates);

    const statusEl = document.createElement('div');
    statusEl.className = 'phase-status';

    let actionBtn = null;

    if (status === 'completed') {
      statusText = 'Complete';
      statusBg = '#EAF3DE';
      statusTx = '#27500A';
      actionBtn = makePhaseBtn(
        'btn btn-ghost btn-sm phase-undo-btn',
        'Undo',
        () => undoPhaseComplete(i),
        { hoverLabel: isOwner ? 'Mark Complete' : 'Request Completion' }
      );
    } else if (status === 'requested') {
      statusText = 'Review Pending';
      statusBg = '#FAEEDA';
      statusTx = '#BA7517';
      if (isOwner) {
        actionBtn = makePhaseBtn('btn btn-primary btn-sm', 'Approve', () => approvePhase(i));
      } else {
        actionBtn = makePhaseBtn(
          'btn btn-ghost btn-sm phase-undo-btn',
          'Undo',
          () => undoPhaseRequest(i),
          { hoverLabel: 'Request Completion' }
        );
      }
    } else {
      statusText = 'In progress';
      statusBg = p.bg;
      statusTx = p.text;
      if (isOwner) {
        actionBtn = makePhaseBtn('btn btn-ghost btn-sm', 'Mark Complete', () => markComplete(i));
      } else {
        actionBtn = makePhaseBtn('btn btn-ghost btn-sm', 'Request Completion', () => requestComplete(i));
      }
    }

    statusEl.style.background = statusBg;
    statusEl.style.color = statusTx;
    statusEl.textContent = statusText;
    appendPhaseRow(el, dot, info, statusEl, actionBtn);
  });
}

function requestComplete(idx) {
  dbUpdatePhaseStatus(idx, 'requested');
}
function markComplete(idx) {
  dbUpdatePhaseStatus(idx, 'completed');
}
function approvePhase(idx) {
  dbUpdatePhaseStatus(idx, 'completed');
}
function undoPhaseRequest(idx) {
  dbUpdatePhaseStatus(idx, 'pending');
}
function undoPhaseComplete(idx) {
  dbUpdatePhaseStatus(idx, 'pending');
}

document.addEventListener('DOMContentLoaded', async () => {
  document.getElementById('change-pwd-btn')?.addEventListener('click', openChangePassword);
  document.getElementById('pwd-save-btn')?.addEventListener('click', submitChangePassword);
  document.getElementById('pwd-cancel-btn')?.addEventListener('click', closeChangePassword);

  const statuses = await dbGetPhaseStatuses();
  window.serverData = { phaseStatuses: statuses };
  renderPhases();
  subscribeToPhaseStatuses(() => {
    dbGetPhaseStatuses().then((s) => {
      window.serverData = { phaseStatuses: s };
      renderPhases();
    });
  });
});

const upcoming = MEETINGS.filter((m) => m >= today);
const nextM = upcoming[0];
document.getElementById('next-meeting-date').textContent = nextM ? fmtDate(nextM) : 'No more sessions';

function openChangePassword() {
  document.getElementById('pwd-modal').style.display = 'flex';
  document.getElementById('pwd-err').style.display = 'none';
  document.getElementById('old-pwd').value = '';
  document.getElementById('new-pwd').value = '';
}
function closeChangePassword() {
  document.getElementById('pwd-modal').style.display = 'none';
}
function submitChangePassword() {
  const oldPassword = document.getElementById('old-pwd').value;
  const newPassword = document.getElementById('new-pwd').value;
  const err = document.getElementById('pwd-err');
  const loginId = loginIdForUid(currentUser());

  err.style.display = 'none';
  err.textContent = '';

  if (!oldPassword || !newPassword) {
    err.textContent = 'Enter both old and new password.';
    err.style.display = 'block';
    return;
  }
  if (newPassword.length < 4) {
    err.textContent = 'New password must be at least 4 characters.';
    err.style.display = 'block';
    return;
  }
  if (!loginId) {
    err.textContent = 'Could not identify your account.';
    err.style.display = 'block';
    return;
  }
  if (!verifyLogin(loginId, oldPassword)) {
    err.textContent = 'Current password is incorrect.';
    err.style.display = 'block';
    return;
  }
  if (oldPassword === newPassword) {
    err.textContent = 'Choose a different new password.';
    err.style.display = 'block';
    return;
  }

  setPasswordForLogin(loginId, newPassword);
  alert('Password changed successfully. Please sign in again.');
  closeChangePassword();
  logout();
}

window.openChangePassword = openChangePassword;
window.closeChangePassword = closeChangePassword;
window.submitChangePassword = submitChangePassword;
