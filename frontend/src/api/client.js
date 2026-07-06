import i18n from '../i18n';
import { translateApiPayload } from '../utils/translateApi';

const API_BASE = '';

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
      'Accept-Language': i18n.language || 'en',
      ...(options.headers || {}),
    },
    ...options,
  });

  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    translateApiPayload(data);
  }
  return translateApiPayload(data);
}

export const api = {
  authStatus: () => request('/api/auth/status'),
  login: (password) => request('/api/auth/login', { method: 'POST', body: JSON.stringify({ password }) }),
  logout: () => request('/api/auth/logout', { method: 'POST' }),
  setup: (payload) => request('/api/setup', { method: 'POST', body: JSON.stringify(payload) }),
  getSettings: () => request('/api/settings'),
  updateTheme: (theme) => request('/api/settings/theme', { method: 'PUT', body: JSON.stringify({ theme }) }),
  updateLanguage: (language) => request('/api/settings/language', { method: 'PUT', body: JSON.stringify({ language }) }),
  updatePassword: (password) => request('/api/settings/password', { method: 'PUT', body: JSON.stringify({ password }) }),
  rotateApiKey: () => request('/api/settings/rotate-api-key', { method: 'POST' }),
  getDevices: (withStatus = true) => request(`/api/devices?status=${withStatus}`),
  createDevice: (device) => request('/api/devices', { method: 'POST', body: JSON.stringify(device) }),
  updateDevice: (id, device) => request(`/api/devices/${id}`, { method: 'PUT', body: JSON.stringify(device) }),
  deleteDevice: (id) => request(`/api/devices/${id}`, { method: 'DELETE' }),
  wakeDevice: (id, force = false) => request(`/api/devices/${id}/wake?force=${force}`, { method: 'POST' }),
  wakeDeviceVerify: (id, force = false) => request(`/api/devices/${id}/wake?verify=true&force=${force}`, { method: 'POST' }),
  getWakeJob: (jobId) => request(`/api/wake/jobs/${jobId}`),
  exportDevices: (format = 'json') => request(`/api/devices/export?format=${format}`),
  importDevices: (devices, merge = true) => request('/api/devices/import', { method: 'POST', body: JSON.stringify({ devices, merge }) }),
  getGroups: () => request('/api/groups'),
  createGroup: (group) => request('/api/groups', { method: 'POST', body: JSON.stringify(group) }),
  updateGroup: (id, group) => request(`/api/groups/${id}`, { method: 'PUT', body: JSON.stringify(group) }),
  deleteGroup: (id) => request(`/api/groups/${id}`, { method: 'DELETE' }),
  wakeGroup: (id) => request(`/api/groups/${id}/wake`, { method: 'POST' }),
  getNpmHosts: () => request('/api/npm-hosts'),
  createNpmHost: (host) => request('/api/npm-hosts', { method: 'POST', body: JSON.stringify(host) }),
  deleteNpmHost: (id) => request(`/api/npm-hosts/${id}`, { method: 'DELETE' }),
  getNpmConfig: (baseUrl) => request(`/api/npm/config${baseUrl ? `?base_url=${encodeURIComponent(baseUrl)}` : ''}`),
  getNpmConfigForDevice: (id, baseUrl) => request(`/api/npm/config/${id}${baseUrl ? `?base_url=${encodeURIComponent(baseUrl)}` : ''}`),
  testNpm: (id) => request(`/api/npm/test/${id}`, { method: 'POST' }),
  getWebhooks: () => request('/api/webhooks'),
  createWebhook: (hook) => request('/api/webhooks', { method: 'POST', body: JSON.stringify(hook) }),
  updateWebhook: (id, hook) => request(`/api/webhooks/${id}`, { method: 'PUT', body: JSON.stringify(hook) }),
  deleteWebhook: (id) => request(`/api/webhooks/${id}`, { method: 'DELETE' }),
  getSchedules: () => request('/api/schedules'),
  createSchedule: (schedule) => request('/api/schedules', { method: 'POST', body: JSON.stringify(schedule) }),
  deleteSchedule: (id) => request(`/api/schedules/${id}`, { method: 'DELETE' }),
  getStats: () => request('/api/stats'),
  getWakeEvents: (limit = 50) => request(`/api/wake-events?limit=${limit}`),
  getAuditLogs: (limit = 100) => request(`/api/audit?limit=${limit}`),
  scanNetwork: (payload) => request('/api/scan', { method: 'POST', body: JSON.stringify(payload) }),
  getLogs: (lines = 100) => request(`/api/logs?lines=${lines}`),
  publicStatus: (domain) => request(`/api/public/status/${encodeURIComponent(domain)}`),
  publicWake: (domain) => request(`/api/public/wake/${encodeURIComponent(domain)}`, { method: 'POST' }),
};
