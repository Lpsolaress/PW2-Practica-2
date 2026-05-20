import { apiFetch } from './api.js';

export async function listarMisOrdenes() {
  return await apiFetch('/ordenes/mis-ordenes', { method: 'GET' });
}

export async function checkout() {
  return await apiFetch('/ordenes', { method: 'POST' });
}

export async function listarTodasLasOrdenes() {
  return await apiFetch('/ordenes', { method: 'GET' });
}

export async function actualizarEstadoOrden(id, status) {
  return await apiFetch(`/ordenes/${id}/status`, {
    method: 'PATCH',
    body: JSON.stringify({ status })
  });
}
