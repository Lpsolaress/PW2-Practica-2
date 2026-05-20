import { apiFetch } from './api.js';

export async function listarUsuarios() {
  return await apiFetch('/usuarios', { method: 'GET' });
}

export async function obtenerUsuario(id) {
  return await apiFetch(`/usuarios/${id}`, { method: 'GET' });
}

export async function crearUsuario(data) {
  return await apiFetch('/usuarios', {
    method: 'POST',
    body: JSON.stringify(data)
  });
}

export async function actualizarUsuario(id, data) {
  return await apiFetch(`/usuarios/${id}`, {
    method: 'PUT',
    body: JSON.stringify(data)
  });
}

export async function eliminarUsuario(id) {
  return await apiFetch(`/usuarios/${id}`, { method: 'DELETE' });
}
