// API base — CromosMarket
const API_URL = 'http://localhost:3000/api';

function getToken() {
  return localStorage.getItem('token');
}

function authHeaders() {
  const h = { 'Content-Type': 'application/json' };
  const t = getToken();
  if (t) h['Authorization'] = `Bearer ${t}`;
  return h;
}

async function handleResponse(res) {
  if (res.status === 401) {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    throw new Error('Sesión expirada. Inicia sesión de nuevo.');
  }
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.error || body.message || `Error ${res.status}`);
  }
  return res.json();
}

// ——— AUTH ———
export async function login(username, password) {
  const res = await fetch(`${API_URL}/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password })
  });
  return handleResponse(res);
}

export async function register(username, password) {
  const res = await fetch(`${API_URL}/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password })
  });
  return handleResponse(res);
}

// ——— PRODUCTOS (CROMOS) ———
export async function getCromos() {
  const res = await fetch(`${API_URL}/productos`);
  return handleResponse(res);
}

export async function publishCromo(formData) {
  const res = await fetch(`${API_URL}/productos`, {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${getToken()}` },
    body: formData
  });
  return handleResponse(res);
}

export async function deleteCromo(id) {
  const res = await fetch(`${API_URL}/productos/${id}`, {
    method: 'DELETE',
    headers: authHeaders()
  });
  return handleResponse(res);
}

// ——— COMPRAR (marcar como vendido) ———
export async function buyCromo(id, comprador) {
  const res = await fetch(`${API_URL}/productos/${id}`, {
    method: 'PUT',
    headers: authHeaders(),
    body: JSON.stringify({
      estado_venta: 'vendido',
      comprador: comprador,
      fecha_venta: new Date().toISOString()
    })
  });
  return handleResponse(res);
}

// ——— EDITAR CROMO ———
export async function updateCromo(id, data) {
  const res = await fetch(`${API_URL}/productos/${id}`, {
    method: 'PUT',
    headers: authHeaders(),
    body: JSON.stringify(data)
  });
  return handleResponse(res);
}

// ——— USUARIOS (ADMIN) ———
export async function getUsers() {
  const res = await fetch(`${API_URL}/users`, { headers: authHeaders() });
  return handleResponse(res);
}

export async function createUser(userData) {
  const res = await fetch(`${API_URL}/users`, {
    method: 'POST',
    headers: authHeaders(),
    body: JSON.stringify(userData)
  });
  return handleResponse(res);
}

export async function updateUser(id, data) {
  const res = await fetch(`${API_URL}/users/${id}`, {
    method: 'PUT',
    headers: authHeaders(),
    body: JSON.stringify(data)
  });
  return handleResponse(res);
}

export async function deleteUser(id) {
  const res = await fetch(`${API_URL}/users/${id}`, {
    method: 'DELETE',
    headers: authHeaders()
  });
  return handleResponse(res);
}

// Helper para URL de imagen
export function imageUrl(filename) {
  if (!filename) return null;
  if (filename.startsWith('http')) return filename;
  return `http://localhost:3000/uploads/${filename}`;
}
