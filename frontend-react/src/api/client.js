// API base URL configured via VITE_API_URL environment variable.
// Fallback is localhost:8000 for local development.
// For production, ensure VITE_API_URL is set to your actual API domain.
const API_BASE = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api';

function getAccessToken() {
  return localStorage.getItem('access');
}

function getRefreshToken() {
  return localStorage.getItem('refresh');
}

function humanizeFieldName(field) {
  if (field === 'non_field_errors') return '';
  return field.replaceAll('_', ' ').replace(/\b\w/g, (char) => char.toUpperCase());
}

function formatApiError(error) {
  if (!error) return 'Request failed';
  if (typeof error === 'string') return error;
  if (error.error || error.detail || error.message) {
    return error.error || error.detail || error.message;
  }

  if (Array.isArray(error)) {
    return error.map(formatApiError).join(' ');
  }

  if (typeof error === 'object') {
    const messages = Object.entries(error).flatMap(([field, value]) => {
      const text = Array.isArray(value)
        ? value.map(formatApiError).join(' ')
        : formatApiError(value);
      const label = humanizeFieldName(field);
      return text ? [`${label ? `${label}: ` : ''}${text}`] : [];
    });

    return messages.join(' ');
  }

  return 'Request failed';
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

async function apiFetch(endpoint, options = {}, retries = 3) {
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

  try {
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

    // Auto-retry for 5xx server errors or timeouts
    if (res.status >= 500 && retries > 0) {
      console.warn(`API Error ${res.status} on ${endpoint}. Retrying... (${retries} left)`);
      await new Promise(r => setTimeout(r, 1000 * (4 - retries))); // Exponential backoff
      return apiFetch(endpoint, options, retries - 1);
    }

    if (!res.ok && res.status !== 204) {
      const error = await res.json().catch(() => ({ error: `Server Error (${res.status})` }));
      throw new Error(formatApiError(error) || `Request failed with status ${res.status}`);
    }

    if (res.status === 204) return null;

    return res.json();
  } catch (error) {
    // Network errors (fetch throws TypeError on network failure)
    if (retries > 0 && error.name === 'TypeError') {
      console.warn(`Network Error on ${endpoint}. Retrying... (${retries} left)`);
      await new Promise(r => setTimeout(r, 1000 * (4 - retries)));
      return apiFetch(endpoint, options, retries - 1);
    }
    throw error;
  }
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
