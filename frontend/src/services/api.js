import { app, clearAuth, showToast, navigate } from '../state/app.svelte.js';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || (import.meta.env.DEV ? 'http://localhost:3000' : '');

export async function apiFetch(path, options = {}) {
  const url = `${API_BASE_URL}${path.startsWith('/') ? path : `/${path}`}`;

  const headers = new Headers(options.headers || {});
  if (!headers.has('Content-Type') && options.body != null && !(options.body instanceof FormData)) {
    headers.set('Content-Type', 'application/json');
  }

  if (app.auth.token) {
    headers.set('Authorization', `Bearer ${app.auth.token}`);
  }

  let response;
  try {
    response = await fetch(url, { ...options, headers });
  } catch (error) {
    showToast('No se pudo conectar con el servidor', 'error');
    throw error;
  }

  const contentType = response.headers.get('content-type') || '';
  const isJson = contentType.includes('application/json');
  const data = isJson ? await response.json().catch(() => null) : await response.text().catch(() => null);

  if (response.status === 401) {
    clearAuth();
    navigate('/login');
  }

  if (!response.ok) {
    const message = typeof data === 'object' && data && 'error' in data ? data.error : `Error ${response.status}`;
    throw new ApiError(message, response.status, data);
  }

  return data;
}

export class ApiError extends Error {
  constructor(message, status, payload) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.payload = payload;
  }
}
