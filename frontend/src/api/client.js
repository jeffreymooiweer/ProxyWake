const API_BASE = '';

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
      ...(options.headers || {}),
    },
    ...options,
  });

  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(data.error || 'Er is iets misgegaan.');
  }
  return data;
}

export const api = {
  authStatus: () => request('/api/auth/status'),
  login: (password) => request('/api/auth/login', { method: 'POST', body: JSON.stringify({ password }) }),
  logout: () => request('/api/auth/logout', { method: 'POST' }),
  getDevices: (withStatus = true) => request(`/api/devices?status=${withStatus}`),
  createDevice: (device) => request('/api/devices', { method: 'POST', body: JSON.stringify(device) }),
  updateDevice: (id, device) => request(`/api/devices/${id}`, { method: 'PUT', body: JSON.stringify(device) }),
  deleteDevice: (id) => request(`/api/devices/${id}`, { method: 'DELETE' }),
  wakeDevice: (id) => request(`/api/devices/${id}/wake`, { method: 'POST' }),
  getSettings: () => request('/api/settings'),
  getNpmConfig: (baseUrl) => request(`/api/npm/config${baseUrl ? `?base_url=${encodeURIComponent(baseUrl)}` : ''}`),
  getNpmConfigForDevice: (id, baseUrl) => request(`/api/npm/config/${id}${baseUrl ? `?base_url=${encodeURIComponent(baseUrl)}` : ''}`),
  getLogs: (lines = 100) => request(`/api/logs?lines=${lines}`),
};
