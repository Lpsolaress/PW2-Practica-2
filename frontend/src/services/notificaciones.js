import { apiFetch } from './api.js';

export async function listarNotificaciones() {
  return await apiFetch('/notificaciones', { method: 'GET' });
}

export async function marcarLeida(id) {
  return await apiFetch(`/notificaciones/${id}/leida`, { method: 'PATCH' });
}

export async function leerTodas() {
  return await apiFetch('/notificaciones/leer-todas', { method: 'PATCH' });
}

export async function eliminarNotificacion(id) {
  return await apiFetch(`/notificaciones/${id}`, { method: 'DELETE' });
}
