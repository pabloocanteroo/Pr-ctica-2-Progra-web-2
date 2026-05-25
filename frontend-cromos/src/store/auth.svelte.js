// Store global de autenticación con Svelte 5 Runes ($state)
// Persistencia en localStorage para sobrevivir recargas

export const auth = $state({
  user: null,    // { username, role, _id }
  token: null,
  ready: false   // true cuando ya leímos de localStorage
});

export function initAuth() {
  if (auth.ready) return;
  try {
    const t = localStorage.getItem('token');
    const u = localStorage.getItem('user');
    if (t && u) {
      auth.token = t;
      auth.user = JSON.parse(u);
    }
  } catch { /* corrupt data, ignorar */ }
  auth.ready = true;
}

export function setAuth(user, token) {
  auth.user = user;
  auth.token = token;
  localStorage.setItem('token', token);
  localStorage.setItem('user', JSON.stringify(user));
}

export function clearAuth() {
  auth.user = null;
  auth.token = null;
  localStorage.removeItem('token');
  localStorage.removeItem('user');
}
