const API_BASE = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api';

function getAccessToken() {
  return localStorage.getItem('access');
}

function getRefreshToken() {
  return localStorage.getItem('refresh');
}

async function refreshToken() {
  const refresh = getRefreshToken();
  if (!refresh) return false;

  try {
    const res = await fetch(`${API_BASE}/auth/token/refresh/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh }),
    });

    if (!res.ok) return false;

    const data = await res.json();
    localStorage.setItem('access', data.access);
    return true;
  } catch {
    return false;
  }
}

async function apiFetch(endpoint, options = {}) {
  const { headers = {}, ...rest } = options;
  const token = getAccessToken();

  const config = {
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...headers,
    },
    ...rest,
  };

  let res = await fetch(`${API_BASE}${endpoint}`, config);

  if (res.status === 401 && token) {
    const refreshed = await refreshToken();
    if (refreshed) {
      const newToken = getAccessToken();
      config.headers.Authorization = `Bearer ${newToken}`;
      res = await fetch(`${API_BASE}${endpoint}`, config);
    } else {
      localStorage.removeItem('access');
      localStorage.removeItem('refresh');
      window.location.href = '/login';
      return null;
    }
  }

  if (!res.ok && res.status !== 204) {
    const error = await res.json().catch(() => ({ error: 'Request failed' }));
    throw new Error(error.error || error.detail || error.message || 'Request failed');
  }

  if (res.status === 204) return null;

  return res.json();
}

export const api = {
  get: (endpoint) => apiFetch(endpoint, { method: 'GET' }),
  post: (endpoint, data) => apiFetch(endpoint, { method: 'POST', body: JSON.stringify(data) }),
  put: (endpoint, data) => apiFetch(endpoint, { method: 'PUT', body: JSON.stringify(data) }),
  patch: (endpoint, data) => apiFetch(endpoint, { method: 'PATCH', body: JSON.stringify(data) }),
  delete: (endpoint) => apiFetch(endpoint, { method: 'DELETE' }),
  refresh: () => refreshToken(),
};

export { getAccessToken, getRefreshToken };
