<script>
  import { app, displayName, isAdmin, cartCount, clearAuth, navigate, isAuthenticated } from '../state/app.svelte.js';

  let { currentPath } = $props();

  function logout() {
    clearAuth();
    navigate('/login');
  }

  function goLogin() {
    sessionStorage.setItem('loginMode', 'login');
    navigate('/login');
  }

  function goRegister() {
    sessionStorage.setItem('loginMode', 'register');
    navigate('/login');
  }
</script>

<header class="header">
  <div class="header__inner">
    <div class="brand">
      <span class="brand__title">Nuba</span>
    </div>

    <nav class="nav" aria-label="Principal">
      <a class:active={currentPath === '/productos'} href="#/productos">Productos</a>
      <a
        class:active={currentPath === '/carrito'}
        href="#/carrito"
        onclick={(e) => {
          if (!isAuthenticated()) {
            e.preventDefault();
            goLogin();
          }
        }}
      >
        Carrito
        {#if cartCount() > 0}
          <span class="count">{cartCount()}</span>
        {/if}
      </a>
      <a
        class:active={currentPath === '/perfil'}
        href="#/perfil"
        onclick={(e) => {
          if (!isAuthenticated()) {
            e.preventDefault();
            goLogin();
          }
        }}
      >
        Perfil
      </a>

      {#if isAuthenticated() && (isAdmin() || app.ui.hasChatHistory === true)}
        <a 
          class:active={currentPath === '/soporte'} 
          href="#/soporte"
          title="Soporte Técnico"
        >
          <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 1 1-7.6-11.7 8.38 8.38 0 0 1 3.8.9L21 3z"/>
          </svg>
          Soporte
        </a>
      {/if}
    </nav>

    <div class="user">
      {#if isAuthenticated()}
        <span class="user__name">{displayName() || app.auth.user?.email || '—'}</span>
        {#if isAdmin()}
          <span class="badge">admin</span>
        {/if}
        <button class="btn btn--ghost" type="button" onclick={logout}>Salir</button>
      {:else}
        <button class="btn btn--ghost" type="button" onclick={goLogin}>Iniciar sesión</button>
        <button class="btn btn--primary" type="button" onclick={goRegister}>Crear cuenta</button>
      {/if}
    </div>
  </div>
</header>

<style>
  .header {
    position: sticky;
    top: 0;
    z-index: 10;
    background: color-mix(in oklab, var(--bg) 90%, transparent);
    backdrop-filter: blur(10px);
    border-bottom: 1px solid var(--border);
  }

  .header__inner {
    max-width: 1100px;
    margin: 0 auto;
    padding: 12px 16px;
    display: grid;
    grid-template-columns: 1fr auto 1fr;
    align-items: center;
    gap: 12px;
  }

  .brand__title {
    font-weight: 700;
    letter-spacing: 0.2px;
    color: var(--text-strong);
  }

  .nav {
    display: flex;
    gap: 10px;
    justify-content: center;
  }

  .nav a {
    text-decoration: none;
    color: var(--text);
    padding: 8px 10px;
    border-radius: 10px;
    border: 1px solid transparent;
    font-size: 14px;
    display: inline-flex;
    align-items: center;
    gap: 8px;
  }

  .nav a.active {
    border-color: var(--border);
    background: var(--panel);
    color: var(--text-strong);
  }

  .count {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    min-width: 20px;
    height: 20px;
    padding: 0 6px;
    border-radius: 999px;
    font-size: 12px;
    line-height: 1;
    background: color-mix(in oklab, var(--danger) 25%, var(--panel));
    border: 1px solid color-mix(in oklab, var(--danger) 55%, var(--border));
    color: var(--text-strong);
  }

  .user {
    display: flex;
    justify-content: flex-end;
    align-items: center;
    gap: 10px;
    min-width: 0;
  }

  .user__name {
    font-size: 13px;
    color: var(--text);
    max-width: 240px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .badge {
    font-size: 12px;
    padding: 2px 8px;
    border-radius: 999px;
    background: color-mix(in oklab, var(--accent) 14%, var(--panel));
    border: 1px solid color-mix(in oklab, var(--accent) 50%, var(--border));
    color: var(--text-strong);
  }

  .btn {
    appearance: none;
    border: 1px solid var(--border);
    background: var(--panel);
    color: var(--text-strong);
    border-radius: 10px;
    padding: 8px 10px;
    font-size: 14px;
    cursor: pointer;
  }

  .btn--ghost {
    background: transparent;
  }

  .btn--primary {
    background: color-mix(in oklab, var(--accent) 18%, var(--panel));
    border-color: color-mix(in oklab, var(--accent) 55%, var(--border));
  }

  @media (max-width: 720px) {
    .header__inner {
      grid-template-columns: 1fr auto;
      grid-template-areas:
        'brand user'
        'nav nav';
    }

    .brand {
      grid-area: brand;
    }

    .nav {
      grid-area: nav;
      justify-content: flex-start;
      flex-wrap: wrap;
    }

    .user {
      grid-area: user;
    }
  }
</style>
