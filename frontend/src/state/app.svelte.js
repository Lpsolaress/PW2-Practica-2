const initialRoute = parseHashToRoute(window.location.hash);

export const app = $state({
  route: initialRoute,
  auth: {
    token: null,
    user: null
  },
  products: {
    items: [],
    loading: false,
    error: null
  },
  cart: {
    items: [],
    loading: false,
    error: null
  },
  ui: {
    toast: null,
    hasChatHistory: false,
    notifications: [],
    profileView: 'main' // 'main', 'personal', 'payments', 'addresses', 'notifications'
  }
});

export function isAuthenticated() {
  return Boolean(app.auth.token);
}

export function isAdmin() {
  return app.auth.user?.role === 'administrador';
}

export function displayName() {
  return app.auth.user?.username ?? '';
}

export function cartCount() {
  return app.cart.items.reduce((sum, item) => sum + (item.quantity || 0), 0);
}

export function navigate(path) {
  if (!path.startsWith('/')) path = `/${path}`;
  const nextHash = `#${path}`;
  if (window.location.hash !== nextHash) {
    window.location.hash = nextHash;
  } else {
    app.route = parseHashToRoute(nextHash);
  }
}

export function syncRouteFromLocation() {
  app.route = parseHashToRoute(window.location.hash);
}

export function setAuth({ token, user }) {
  app.auth.token = token;
  app.auth.user = user;
}

export function clearAuth() {
  app.auth.token = null;
  app.auth.user = null;
}

export function showToast(message, type = 'info') {
  app.ui.toast = { message, type, id: crypto.randomUUID() };
}

export function clearToast(id) {
  if (!app.ui.toast) return;
  if (id && app.ui.toast.id !== id) return;
  app.ui.toast = null;
}

function parseHashToRoute(hash) {
  const raw = typeof hash === 'string' ? hash : '';
  const cleaned = raw.startsWith('#') ? raw.slice(1) : raw;
  const path = cleaned.trim() || '/productos';
  return { path };
}
