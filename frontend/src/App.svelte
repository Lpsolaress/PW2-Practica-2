<script>
  import { app, isAuthenticated, syncRouteFromLocation, navigate } from './state/app.svelte.js';
  import NavBar from './components/NavBar.svelte';
  import { fade } from 'svelte/transition';
  import Toast from './components/Toast.svelte';
  import LoginPage from './pages/LoginPage.svelte';
  import ProductsPage from './pages/ProductsPage.svelte';
  import ProfilePage from './pages/ProfilePage.svelte';
  import CartPage from './pages/CartPage.svelte';
  import SupportHubPage from './pages/SupportHubPage.svelte';
  import ChatWidget from './components/ChatWidget.svelte';

  $effect(() => {
    const onHashChange = () => syncRouteFromLocation();
    window.addEventListener('hashchange', onHashChange);
    syncRouteFromLocation();
    return () => window.removeEventListener('hashchange', onHashChange);
  });

  $effect(() => {
    const path = app.route.path;
    if (!path.startsWith('/')) {
      navigate('/productos');
      return;
    }

    if (path === '/') {
      navigate('/productos');
      return;
    }

    if (!isAuthenticated() && path !== '/login' && path !== '/productos') {
      navigate('/login');
      return;
    }

    if (isAuthenticated() && path === '/login') {
      navigate('/productos');
      return;
    }

    if (path !== '/login' && path !== '/productos' && path !== '/perfil' && path !== '/carrito' && path !== '/soporte') {
      navigate('/productos');
    }
  });
</script>

<svelte:head>
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY=" crossorigin=""/>
  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js" integrity="sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo=" crossorigin=""></script>
</svelte:head>

{#if app.route.path !== '/login'}
  <NavBar currentPath={app.route.path} />
{/if}

{#key app.route.path}
  <div in:fade={{ duration: 180 }} style="width: 100%; height: 100%; display: flex; flex-direction: column; flex: 1;">
    {#if app.route.path === '/login'}
      <LoginPage />
    {:else if app.route.path === '/productos'}
      <ProductsPage />
    {:else if app.route.path === '/perfil'}
      <ProfilePage />
    {:else if app.route.path === '/carrito'}
      <CartPage />
    {:else if app.route.path === '/soporte'}
      <SupportHubPage />
    {/if}
  </div>
{/key}

<Toast />
<ChatWidget />
