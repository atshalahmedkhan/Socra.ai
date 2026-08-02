/* js/auth.js — Client-side mock credentials (localStorage overrides) */

const AUTH_LOGIN_IDS = {
  owner: 'PD01',
  tejas: 'TG05',
  atshal: 'AK03',
};

const AUTH_DEFAULT_PASSWORDS = {
  PD01: '0202',
  TG05: '1515',
  AK03: '0909',
};

const AUTH_UID_BY_LOGIN = {
  PD01: 'owner',
  TG05: 'tejas',
  AK03: 'atshal',
};

function getPasswordForLogin(loginId) {
  const id = String(loginId || '').toUpperCase();
  const overrides = loadData('passwords', {});
  if (overrides[id]) return overrides[id];
  return AUTH_DEFAULT_PASSWORDS[id] || null;
}

function setPasswordForLogin(loginId, newPassword) {
  const id = String(loginId || '').toUpperCase();
  const overrides = loadData('passwords', {});
  overrides[id] = String(newPassword);
  saveData('passwords', overrides);
}

function verifyLogin(loginId, password) {
  const expected = getPasswordForLogin(loginId);
  return expected !== null && expected === String(password);
}

function loginIdForUid(uid) {
  return AUTH_LOGIN_IDS[uid] || null;
}

window.getPasswordForLogin = getPasswordForLogin;
window.setPasswordForLogin = setPasswordForLogin;
window.verifyLogin = verifyLogin;
window.loginIdForUid = loginIdForUid;
