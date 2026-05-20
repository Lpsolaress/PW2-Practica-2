import { apiFetch } from './api.js';

export async function listarProductos() {
  return await apiFetch('/productos', { method: 'GET' });
}

export async function crearProducto(producto) {
  return await apiFetch('/productos', {
    method: 'POST',
    body: producto instanceof FormData ? producto : JSON.stringify(producto)
  });
}

export async function actualizarProducto(id, producto) {
  return await apiFetch(`/productos/${id}`, {
    method: 'PUT',
    body: producto instanceof FormData ? producto : JSON.stringify(producto)
  });
}

export async function eliminarProducto(id) {
  return await apiFetch(`/productos/${id}`, { method: 'DELETE' });
}
