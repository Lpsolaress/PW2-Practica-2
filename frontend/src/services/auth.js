import { apiFetch } from './api.js';

export async function login({ email, password }) {
  return await apiFetch('/auth/login', {
    method: 'POST',
    body: JSON.stringify({ email, password })
  });
}

export async function registro({ username, email, password, role = 'usuario' }) {
  return await apiFetch('/auth/registro', {
    method: 'POST',
    body: JSON.stringify({ username, email, password, role })
  });
}

export async function perfil() {
  return await apiFetch('/auth/perfil', { method: 'GET' });
}

export async function actualizarPerfil(formData) {
  // Recibe FormData para soportar imagen
  return await apiFetch('/auth/perfil', {
    method: 'PUT',
    body: formData
  });
}

export async function agregarDireccion(data) {
  return await apiFetch('/auth/direcciones', {
    method: 'POST',
    body: JSON.stringify(data)
  });
}

export async function eliminarDireccion(id) {
  return await apiFetch(`/auth/direcciones/${id}`, { method: 'DELETE' });
}

export async function agregarMetodoPago(data) {
  return await apiFetch('/auth/metodos-pago', {
    method: 'POST',
    body: JSON.stringify(data)
  });
}

export async function eliminarMetodoPago(id) {
  return await apiFetch(`/auth/metodos-pago/${id}`, { method: 'DELETE' });
}
