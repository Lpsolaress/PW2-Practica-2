import { apiFetch } from './api.js';

export async function obtenerCarrito() {
  return await apiFetch('/carrito', { method: 'GET' });
}

export async function agregarAlCarrito(productId, quantity = 1) {
  return await apiFetch('/carrito/add', {
    method: 'POST',
    body: JSON.stringify({ productId, quantity })
  });
}

export async function actualizarCantidad(productId, quantity) {
  return await apiFetch(`/carrito/item/${productId}`, {
    method: 'PATCH',
    body: JSON.stringify({ quantity })
  });
}

export async function eliminarDelCarrito(productId) {
  return await apiFetch(`/carrito/item/${productId}`, { method: 'DELETE' });
}

export async function vaciarCarrito() {
  return await apiFetch('/carrito', { method: 'DELETE' });
}
