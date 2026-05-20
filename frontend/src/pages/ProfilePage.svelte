<script>
  import { app, clearAuth, navigate, showToast } from '../state/app.svelte.js';
  import { perfil, actualizarPerfil, agregarDireccion, eliminarDireccion, agregarMetodoPago, eliminarMetodoPago } from '../services/auth.js';
  import { listarProductos } from '../services/productos.js';
  import { obtenerCarrito } from '../services/carrito.js';
  import { listarMisOrdenes, listarTodasLasOrdenes, actualizarEstadoOrden } from '../services/ordenes.js';
  import { listarNotificaciones, marcarLeida, leerTodas, eliminarNotificacion } from '../services/notificaciones.js';
  import { listarUsuarios } from '../services/usuarios.js';
  import { io } from 'socket.io-client';
  import { onMount, onDestroy, untrack } from 'svelte';

  let loadingProfile = $state(false);
  let loadingNotifs = $state(false);
  let loadingOrders = $state(false);
  
  // Vista activa: main, personal, payments, addresses, notifications
  let currentView = $state(untrack(() => app.ui.profileView || 'main'));
  $effect(() => {
    app.ui.profileView = currentView;
  });

  // Formularios
  let editForm = $state({ username: '' });
  let paymentForm = $state({ type: 'visa', last4: '', expiry: '', cardholder: '', isDefault: false });
  let addressForm = $state({ name: '', street: '', city: '', state: '', zip: '', lat: 0, lng: 0, isDefault: false });
  let fileInput = $state();
  let profilePhotoFile = $state(null);

  // Datos
  let ordersList = $state([]);
  let notificationsList = $state([]);
  let selectedOrder = $state(null);
  let changingStatus = $state(false);
  let usersList = $state([]);
  let loadingUsers = $state(false);
  let map; // Leaflet instance
  let marker;

  async function recargar() {
    loadingProfile = true;
    try {
      const data = await perfil();
      app.auth.user = data.usuario;
      editForm.username = app.auth.user.username;
    } catch (err) {
      showToast(err?.message || 'No se pudo cargar el perfil', 'error');
    } finally {
      loadingProfile = false;
    }
  }

  async function cargarOrdenes() {
    loadingOrders = true;
    try {
      if (app.auth.user.role === 'administrador') {
        ordersList = await listarTodasLasOrdenes();
      } else {
        ordersList = await listarMisOrdenes();
      }
    } catch (err) {
      console.error(err);
    } finally {
      loadingOrders = false;
    }
  }

  async function cargarNotificaciones() {
    loadingNotifs = true;
    try {
      notificationsList = await listarNotificaciones();
      app.ui.notifications = notificationsList;
    } catch (err) {
      console.error(err);
    } finally {
      loadingNotifs = false;
    }
  }

  async function cargarUsuarios() {
    loadingUsers = true;
    try {
      usersList = await listarUsuarios();
    } catch (err) {
      console.error(err);
    } finally {
      loadingUsers = false;
    }
  }

  async function handleUpdateProfile() {
    loadingProfile = true;
    try {
      const formData = new FormData();
      formData.append('username', editForm.username);
      if (profilePhotoFile) {
        formData.append('foto', profilePhotoFile);
      }
      
      const res = await actualizarPerfil(formData);
      app.auth.user = res.usuario;
      showToast('Perfil actualizado con éxito', 'success');
      currentView = 'main';
    } catch (err) {
      showToast(err?.message || 'Error al actualizar perfil', 'error');
    } finally {
      loadingProfile = false;
    }
  }

  async function handleSaveAddress() {
    try {
      const res = await agregarDireccion(addressForm);
      app.auth.user.addresses = res.addresses;
      showToast('Dirección guardada', 'success');
      addressForm = { name: '', street: '', city: '', state: '', zip: '', lat: 0, lng: 0, isDefault: false };
    } catch (err) {
      showToast(err?.message || 'Error al guardar dirección', 'error');
    }
  }

  async function handleRemoveAddress(id) {
    try {
      const res = await eliminarDireccion(id);
      app.auth.user.addresses = res.addresses;
      showToast('Dirección eliminada', 'info');
    } catch (err) {
      showToast(err?.message || 'Error al eliminar', 'error');
    }
  }

  async function handleSavePayment() {
    try {
      const res = await agregarMetodoPago(paymentForm);
      app.auth.user.paymentMethods = res.paymentMethods;
      showToast('Método de pago guardado', 'success');
      paymentForm = { type: 'visa', last4: '', expiry: '', cardholder: '', isDefault: false };
    } catch (err) {
      showToast(err?.message || 'Error al guardar pago', 'error');
    }
  }

  async function handleRemovePayment(id) {
    try {
      const res = await eliminarMetodoPago(id);
      app.auth.user.paymentMethods = res.paymentMethods;
      showToast('Método de pago eliminado', 'info');
    } catch (err) {
      showToast(err?.message || 'Error al eliminar', 'error');
    }
  }

  const nubaStores = [
    { name: 'Nuba Madrid (Gran Vía)', lat: 40.4200, lng: -3.7019 },
    { name: 'Nuba Barcelona (Gràcia)', lat: 41.3996, lng: 2.1587 },
    { name: 'Nuba Valencia (Ruzafa)', lat: 39.4623, lng: -0.3732 },
    { name: 'Nuba Sevilla (Centro)', lat: 37.3891, lng: -5.9845 },
    { name: 'Nuba Bilbao (Abando)', lat: 43.2630, lng: -2.9350 },
    { name: 'Nuba Zaragoza', lat: 41.6488, lng: -0.8891 },
    { name: 'Nuba Málaga', lat: 36.7213, lng: -4.4213 },
    { name: 'Nuba A Coruña', lat: 43.3623, lng: -8.4115 },
    { name: 'Nuba Mallorca', lat: 39.5696, lng: 2.6502 }
  ];

  function initMap() {
    if (!window.L) return;
    const defaultPos = [40.4168, -3.7038]; // Madrid, Spain
    map = window.L.map('map').setView(defaultPos, 6);
    
    window.L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
      attribution: '&copy; OpenStreetMap contributors &copy; CARTO'
    }).addTo(map);
    
    marker = window.L.marker(defaultPos, { draggable: true }).addTo(map);
    marker.bindPopup('<b>Tú</b><br>Arrastrame a tu ubicación', { autoClose: false }).openPopup();
    
    marker.on('dragend', () => {
      const pos = marker.getLatLng();
      addressForm.lat = pos.lat;
      addressForm.lng = pos.lng;
    });
    
    map.on('click', (e) => {
      marker.setLatLng(e.latlng);
      addressForm.lat = e.latlng.lat;
      addressForm.lng = e.latlng.lng;
    });

    const storeIcon = window.L.divIcon({
      html: `<div style="background: #ff0028; color: white; border-radius: 50%; width: 22px; height: 22px; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 11px; border: 2px solid white; box-shadow: 0 0 5px rgba(0,0,0,0.5);">N</div>`,
      className: '',
      iconSize: [22, 22],
      iconAnchor: [11, 11]
    });

    nubaStores.forEach(s => {
      const m = window.L.marker([s.lat, s.lng], { icon: storeIcon }).addTo(map);
      m.bindPopup(`<b style="color: #000;">${s.name}</b><br><span style="font-size: 11px; color:#555;">Tienda Oficial Nuba</span>`);
      m.on('click', () => {
        addressForm.street = `Recoger en: ${s.name}`;
        addressForm.lat = s.lat;
        addressForm.lng = s.lng;
        marker.setLatLng([s.lat, s.lng]);
        showToast(`Seleccionaste ${s.name}`, 'success');
      });
    });
  }

  function closestNubaStore() {
    if (!map || !marker) return;
    const userLatlng = marker.getLatLng();
    let minStore = null;
    let minDist = Infinity;

    nubaStores.forEach(s => {
      const dist = map.distance(userLatlng, [s.lat, s.lng]);
      if (dist < minDist) {
        minDist = dist;
        minStore = s;
      }
    });

    if (minStore) {
      addressForm.street = `Recoger en: ${minStore.name}`;
      addressForm.lat = minStore.lat;
      addressForm.lng = minStore.lng;
      marker.setLatLng([minStore.lat, minStore.lng]);
      map.setView([minStore.lat, minStore.lng], 13);
      showToast(`Localizada: ${minStore.name} (A aprox. ${(minDist/1000).toFixed(1)} km)`, 'success');
    }
  }

  $effect(() => {
    if (currentView === 'addresses') {
      setTimeout(initMap, 200);
    }
  });

  async function handleMarcarLeida(id) {
    try {
      await marcarLeida(id);
      cargarNotificaciones();
    } catch (err) { console.error(err); }
  }

  async function handleLeerTodas() {
    try {
      await leerTodas();
      cargarNotificaciones();
    } catch (err) { console.error(err); }
  }

  function logout() {
    clearAuth();
    navigate('/login');
  }

  function nubaName() {
    const u = app.auth.user;
    const name = u?.username || u?.email || 'Nuba Member';
    return String(name).replace(/@.*/, '').replace(/[_-]+/g, ' ').trim() || 'Nuba Member';
  }

  function initial() {
    const s = nubaName().trim();
    return (s[0] || 'N').toUpperCase();
  }

  function hashOf(value) {
    const str = String(value ?? '');
    let h = 0;
    for (let i = 0; i < str.length; i++) h = (h * 31 + str.charCodeAt(i)) >>> 0;
    return h;
  }

  const profileKey = $derived(app.auth.user?.id || app.auth.user?._id || app.auth.user?.email || app.auth.token || 'nuba');
  const points = $derived(500 + (hashOf(profileKey) % 2500));
  const tier = $derived(points >= 2000 ? 'ELITE' : points >= 1200 ? 'PRO' : 'MVP');
  const nextTier = $derived(tier === 'MVP' ? 'PRO' : tier === 'PRO' ? 'ELITE' : 'HALL OF FAME');
  const nextTarget = $derived(tier === 'MVP' ? 1200 : tier === 'PRO' ? 2000 : 3000);
  const remaining = $derived(Math.max(0, nextTarget - points));

  const memberSince = $derived.by(() => {
    const h = hashOf(profileKey);
    const d = new Date(Date.UTC(2021 + (h % 5), (h >> 3) % 12, 1));
    return new Intl.DateTimeFormat('es', { month: 'long', year: 'numeric' }).format(d);
  });

  function soon(msg) { showToast(msg || 'Próximamente', 'info'); }

  // --- Soporte Administrativo ---
  let adminSocket = $state(null);
  let conversations = $state([]);
  let activeConversation = $state(null);
  let adminReply = $state('');
  let chatScroll = $state(null);

  function selectConversation(conv) {
    activeConversation = { userId: conv._id, username: conv.username, messages: [] };
    adminSocket.emit('get_conversation', conv._id);
  }

  function connectAdmin() {
    if (!app.auth.user || app.auth.user.role !== 'administrador') return;
    adminSocket = io('http://localhost:3000', { auth: { token: app.auth.token } });
    adminSocket.on('conversations_list', (l) => conversations = l);
    adminSocket.on('message_history', (d) => {
      if (activeConversation?.userId === d.userId) activeConversation.messages = d.messages;
      scrollChat();
    });
    adminSocket.on('chat_message', (m) => {
      if (activeConversation?.userId === m.roomId) activeConversation.messages = [...activeConversation.messages, m];
      adminSocket.emit('get_conversations_list');
      scrollChat();
    });
    adminSocket.emit('get_conversations_list');
  }

  function sendReply(e) {
    e?.preventDefault();
    if (!adminReply.trim() || !activeConversation) return;
    adminSocket.emit('chat_message', { text: adminReply.trim(), targetUserId: activeConversation.userId });
    adminReply = '';
  }

  function scrollChat() { setTimeout(() => { if (chatScroll) chatScroll.scrollTop = chatScroll.scrollHeight; }, 50); }

  async function handleUpdateOrderStatus(orderId, newStatus) {
    changingStatus = true;
    try {
      await actualizarEstadoOrden(orderId, newStatus);
      showToast(`Pedido marcado como ${newStatus}`, 'success');
      if (selectedOrder) selectedOrder.status = newStatus;
      await cargarOrdenes();
    } catch (err) {
      showToast('Error al actualizar el estado', 'error');
    } finally {
      changingStatus = false;
    }
  }

  onMount(() => {
    if (app.auth.user?.role === 'administrador') connectAdmin();
    recargar();
    cargarOrdenes();
    cargarNotificaciones();
  });
  onDestroy(() => adminSocket?.disconnect());
</script>

<main class="page">
  <div class="wrap">
    <!-- Encabezado de Perfil -->
    <section class="profile">
      <div class="avatar">
        {#if app.auth.user?.profilePicture}
          <img src={app.auth.user.profilePicture.startsWith('http') ? app.auth.user.profilePicture : `http://localhost:3000${app.auth.user.profilePicture}`} alt="Avatar" class="avatar__img" />
        {:else}
          <div class="avatar__circle">{initial()}</div>
        {/if}
        <button class="avatar__edit" onclick={() => currentView = 'personal'} aria-label="Editar Perfil">
          <svg viewBox="0 0 24 24" width="16" height="16" fill="none"><path d="M4 20h4l10.5-10.5a1.9 1.9 0 0 0 0-2.7l-1.3-1.3a1.9 1.9 0 0 0-2.7 0L4 16v4Z" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/></svg>
        </button>
      </div>

      <div class="profile__meta">
        <h1 class="profile__name">{nubaName()}</h1>
        <div class="profile__since">Miembro desde {memberSince}</div>
        <div class="profile__badges">
          <span class="pill">{points} PUNTOS</span>
          <span class="pill">{tier}</span>
        </div>
      </div>

      <div class="profile__actions">
        {#if currentView !== 'main'}
          <button class="btn btn--ghost" onclick={() => currentView = 'main'}>Volver</button>
        {/if}
        <button class="btn btn--danger" onclick={logout}>Salir</button>
      </div>
    </section>

    {#if currentView === 'main'}
      {#if app.auth.user?.role === 'administrador'}
        <section class="panel">
          <header class="panel__head"><h2 class="panel__title">CHAT DE SOPORTE</h2></header>
          <div class="support-grid">
            <div class="support-list">
              {#each conversations as conv}
                <button class="conv-btn" class:active={activeConversation?.userId === conv._id} onclick={() => selectConversation(conv)}>
                  {conv.username}
                </button>
              {/each}
            </div>
            <div class="support-chat">
              {#if activeConversation}
                <div class="support-chat__messages" bind:this={chatScroll}>
                  {#each activeConversation.messages as msg}
                    <div class="msg" class:msg--me={msg.userId === app.auth.user?._id}>
                      <div class="msg__bubble">{msg.text}</div>
                    </div>
                  {/each}
                </div>
                <form class="support-chat__input" onsubmit={sendReply}>
                  <input type="text" bind:value={adminReply} />
                  <button type="submit">OK</button>
                </form>
              {:else}
                <div class="empty">Selecciona un chat</div>
              {/if}
            </div>
          </div>
        </section>
      {/if}

      <section class="membership">
        <div class="membership__text">
          <div class="kicker">ESTADO NUBA</div>
          <h2 class="membership__title">{tier}</h2>
          <p class="membership__desc">Faltan {remaining} puntos para {nextTier}.</p>
        </div>
      </section>

      <div class="grid2">
        <section class="panel">
          <header class="panel__head"><h2 class="panel__title">PEDIDOS</h2></header>
          <div class="list">
            {#each ordersList as order}
              <button class="rowitem" style="width: 100%; text-align: left; cursor: pointer; border: none; background: transparent;" onclick={() => selectedOrder = order}>
                <div class="rowitem__body">
                  <!-- <div class="rowitem__meta">{new Date(order.createdAt).toLocaleDateString()}</div> -->
                  <div class="rowitem__name">#{order._id.slice(-6).toUpperCase()}</div>
                  <div class="rowitem__meta" style="color: {order.status === 'Completado' ? '#00ff88' : (order.status === 'Cancelado' ? '#ff0028' : '#888')}">{order.status} • ${order.totalPrice.toFixed(2)}</div>
                </div>
              </button>
            {/each}
          </div>
        </section>

        <section class="panel">
          <header class="panel__head"><h2 class="panel__title">ACCESOS</h2></header>
          <div class="settings__grid">
            <button class="setting" onclick={() => currentView = 'personal'}>Personal</button>
            <button class="setting" onclick={() => currentView = 'payments'}>Pagos</button>
            <button class="setting" onclick={() => currentView = 'addresses'}>Direcciones</button>
            <button class="setting" onclick={() => currentView = 'notifications'}>Avisos</button>
            {#if app.auth.user?.role === 'administrador'}
              <button class="setting" style="border-color: #ff0028; background: rgba(255,0,40,0.05)" onclick={() => { currentView = 'users'; cargarUsuarios(); }}>Ver Usuarios</button>
            {/if}
          </div>
        </section>
      </div>

    {:else if currentView === 'personal'}
      <section class="panel">
        <header class="panel__head"><h2 class="panel__title">EDITAR PERFIL</h2></header>
        <div class="form-container">
          <input type="text" bind:value={editForm.username} placeholder="Nombre" />
          <input type="file" bind:this={fileInput} onchange={(e) => profilePhotoFile = e.target.files[0]} />
          <button class="btn" onclick={handleUpdateProfile}>Guardar</button>
        </div>
      </section>

    {:else if currentView === 'payments'}
      <section class="panel">
        <header class="panel__head"><h2 class="panel__title">MÉTODOS DE PAGO</h2></header>
        
        <div class="list" style="margin-bottom: 24px;">
          {#each app.auth.user?.paymentMethods || [] as pay}
            <div class="rowitem" style="display: flex; gap: 15px;">
              <div class="pay-icon">
                {#if pay.type === 'paypal'}
                  <svg viewBox="0 0 24 24" width="24" height="24" fill="currentColor"><path d="M7 2h10a5 5 0 0 1 5 5c0 3-2.5 5.5-5.5 5.5H14l-1 6h-3l1.5-8.5H10L8 2z"/></svg>
                {:else if pay.type === 'visa'}
                  <svg viewBox="0 0 24 24" width="24" height="24" fill="currentColor"><path d="M22 6H2a2 2 0 0 0-2 2v8a2 2 0 0 0 2 2h20a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2zm-3 8h-3l-1-4-1 4h-3l1-6h2.5l.5 3 .5-3H19l-1 6z"/></svg>
                {:else if pay.type === 'otro' && pay.cardholder === 'Apple Pay'}
                  <svg viewBox="0 0 384 512" width="24" height="24" fill="currentColor"><path d="M318.7 268.7c-.2-36.7 16.4-64.4 50-84.8-18.8-26.9-47.2-41.7-84.7-44.6-35.5-2.8-74.3 20.7-88.5 20.7-15 0-49.4-19.7-76.4-19.7C63.3 141.2 4 184.8 4 273.5q0 39.3 14.4 81.2c12.8 36.7 59 126.7 107.2 125.2 25.2-.6 43-17.9 75.8-17.9 31.8 0 48.3 17.9 76.4 17.9 48.6-.7 90.4-82.5 102.6-119.3-65.2-30.7-61.7-90-61.7-91.9zm-56.6-164.2c27.3-32.4 24.8-61.9 24-72.5-24.1 1.4-52 16.4-67.9 34.9-17.5 19.8-27.8 44.3-25.6 71.9 26.1 2 49.9-11.4 69.5-34.3z"/></svg>
                {:else}
                  <svg viewBox="0 0 24 24" width="24" height="24" fill="currentColor"><path d="M21 4H3a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h18a2 2 0 0 0 2-2V6a2 2 0 0 0-2-2zM3 18V9h18v9H3zM3 6h18v1H3V6z"/></svg>
                {/if}
              </div>
              <div class="rowitem__body" style="flex: 1;">
                <div class="rowitem__name">
                  {pay.type === 'paypal' ? 'PayPal' : (pay.type === 'otro' && pay.cardholder === 'Apple Pay' ? 'Apple Pay' : (pay.type === 'visa' ? 'Visa' : 'Mastercard'))} 
                  {pay.last4 ? `terminada en ${pay.last4}` : ''}
                </div>
                <div class="rowitem__meta">{pay.cardholder || ''} {pay.expiry ? ` • Expira: ${pay.expiry}` : ''}</div>
              </div>
              <button class="btn btn--danger" style="padding: 6px 12px;" onclick={() => handleRemovePayment(pay._id)}>Eliminar</button>
            </div>
          {:else}
            <div class="empty">No tienes métodos de pago guardados</div>
          {/each}
        </div>

        <div class="add-payment">
          <h3 style="font-size: 14px; margin-bottom: 16px; opacity: 0.9;">Agregar Nuevo Método</h3>
          
          <div class="pay-tabs">
            <button class="pay-tab" class:active={paymentForm.type !== 'paypal' && paymentForm.type !== 'otro'} onclick={() => paymentForm.type = 'visa'}>Tarjeta Crédito/Débito</button>
            <button class="pay-tab" class:active={paymentForm.type === 'paypal'} onclick={() => paymentForm.type = 'paypal'}>PayPal</button>
            <button class="pay-tab" class:active={paymentForm.type === 'otro'} onclick={() => { paymentForm.type = 'otro'; paymentForm.cardholder = 'Apple Pay'; paymentForm.last4 = ''; paymentForm.expiry = ''; }}>Apple Pay</button>
          </div>

          <div class="form-container" style="background: #161616; padding: 20px; border-radius: 8px;">
            {#if paymentForm.type === 'paypal'}
              <div class="field-wrap">
                <label>Correo de PayPal</label>
                <input type="email" placeholder="ejemplo@paypal.com" bind:value={paymentForm.cardholder} />
              </div>
            {:else if paymentForm.type === 'otro'}
              <div style="text-align: center; padding: 20px 0;">
                <svg viewBox="0 0 384 512" width="48" height="48" fill="white" style="margin-bottom: 15px;">
                  <path d="M318.7 268.7c-.2-36.7 16.4-64.4 50-84.8-18.8-26.9-47.2-41.7-84.7-44.6-35.5-2.8-74.3 20.7-88.5 20.7-15 0-49.4-19.7-76.4-19.7C63.3 141.2 4 184.8 4 273.5q0 39.3 14.4 81.2c12.8 36.7 59 126.7 107.2 125.2 25.2-.6 43-17.9 75.8-17.9 31.8 0 48.3 17.9 76.4 17.9 48.6-.7 90.4-82.5 102.6-119.3-65.2-30.7-61.7-90-61.7-91.9zm-56.6-164.2c27.3-32.4 24.8-61.9 24-72.5-24.1 1.4-52 16.4-67.9 34.9-17.5 19.8-27.8 44.3-25.6 71.9 26.1 2 49.9-11.4 69.5-34.3z"/>
                </svg>
                <p style="font-size: 14px; opacity: 0.8; margin-bottom: 5px;">Vincula tu cuenta de Apple Pay para pagos inmediatos y seguros.</p>
              </div>
            {:else}
              <div class="field-wrap">
                <label>Nombre en la tarjeta</label>
                <input type="text" placeholder="Ej. Juan Pérez" bind:value={paymentForm.cardholder} />
              </div>
              <div class="field-wrap">
                <label>Número de Tarjeta</label>
                <input type="text" placeholder="**** **** **** ****" oninput={(e) => {
                  const val = e.target.value.replace(/\D/g, '');
                  paymentForm.last4 = val.slice(-4);
                  if (val.startsWith('4')) paymentForm.type = 'visa';
                  else if (val.startsWith('5')) paymentForm.type = 'mastercard';
                }} />
              </div>
              <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                <div class="field-wrap">
                  <label>Fecha de Expiración</label>
                  <input type="text" placeholder="MM/AA" bind:value={paymentForm.expiry} />
                </div>
                <div class="field-wrap">
                  <label>CVC</label>
                  <input type="password" placeholder="***" maxlength="4" />
                </div>
              </div>
            {/if}
            <button class="btn" style="margin-top: 10px; background: #fff; color: #000; font-weight: bold; justify-self: center; border-radius: 8px; padding: 12px; width: 100%;" onclick={handleSavePayment}>
              Guardar Método de Pago
            </button>
          </div>
        </div>
      </section>

    {:else if currentView === 'addresses'}
      <section class="panel">
        <header class="panel__head"><h2 class="panel__title">DIRECCIONES Y TIENDAS NUBA</h2></header>
        <p style="font-size: 12px; margin-bottom: 15px; opacity: 0.8; line-height: 1.4;">
          📍 Arrastra el marcador azul a tu código postal o ciudad. Haz clic en las iniciales <strong>N</strong> rojas para retirar tu pedido en una de nuestras tiendas físicas en España.
        </p>
        <div id="map" style="height: 350px; border-radius: 8px; border: 1px solid #333; margin-bottom: 20px;"></div>
        
        <div class="form-container" style="background: #151515; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
          <button class="btn btn--danger" style="margin-bottom: 12px; font-weight: bold; width: 100%; border-radius: 8px; padding: 12px;" onclick={closestNubaStore}>
            🏠 Seleccionar tienda Nuba más cercana
          </button>
          <div class="field-wrap">
            <label>Dirección elegida</label>
            <input type="text" placeholder="Avenida Ejemplo 123" bind:value={addressForm.street} />
          </div>
          <button class="btn" style="background: #fff; color: #000; font-weight: bold; margin-top: 10px; border-radius: 8px; padding: 12px;" onclick={handleSaveAddress}>Guardar Dirección</button>
        </div>
        
        <h3 style="font-size: 14px; opacity: 0.8; margin-bottom: 15px; border-top: 1px solid #333; padding-top: 15px;">Tus Direcciones Guardadas</h3>
        <div class="list">
          {#each app.auth.user?.addresses || [] as addr}
            <div class="rowitem" style="display: flex; gap: 10px; align-items: center;">
              <div class="rowitem__body" style="flex: 1; font-size: 13px;">
                <b style="display:block; font-size: 11px; opacity: 0.6; margin-bottom: 3px;">{addr.street?.includes('Recoger en') ? 'SUCURSAL NUBA' : 'ENTREGA A DOMICILIO'}</b>
                {addr.street}
              </div>
              <button class="btn btn--danger" style="padding: 6px 10px;" onclick={() => handleRemoveAddress(addr._id)}>Eliminar</button>
            </div>
          {:else}
            <div class="empty">Aún no hay direcciones registradas</div>
          {/each}
        </div>
      </section>

    {:else if currentView === 'notifications'}
      <section class="panel">
        <header class="panel__head"><h2 class="panel__title">NOTIFICACIONES</h2></header>
        <div class="list">
          {#each notificationsList as notif}
            <div class="rowitem" class:unread={!notif.read} onclick={() => handleMarcarLeida(notif._id)} role="button" tabindex="0" onkeydown={(e) => e.key === 'Enter' && handleMarcarLeida(notif._id)}>
              <div class="rowitem__body">
                <div>{notif.title}</div>
                <div style="font-size: 12px; opacity: 0.7;">{notif.message}</div>
              </div>
            </div>
          {/each}
        </div>
      </section>

    {:else if currentView === 'users'}
      <section class="panel">
        <header class="panel__head">
          <h2 class="panel__title">USUARIOS REGISTRADOS ({usersList.length})</h2>
        </header>
        {#if loadingUsers}
          <div class="empty">Cargando usuarios...</div>
        {:else}
          <div class="list">
            {#each usersList as u}
              <div class="rowitem" style="display: flex; gap: 12px; align-items: center;">
                <div class="avatar avatar--sm" style="width: 32px; height: 32px; font-size: 11px; background: #222; border-color: #333;">
                  {u.username?.[0]?.toUpperCase() || 'U'}
                </div>
                <div class="rowitem__body" style="flex: 1;">
                  <div class="rowitem__name" style="display: flex; align-items: center; gap: 6px;">
                    {u.username}
                    {#if u.role === 'administrador'}
                      <span style="background: rgba(0, 255, 136, 0.1); color: #00ff88; font-size: 9px; padding: 2px 6px; border-radius: 4px; font-weight: bold; text-transform: uppercase;">Admin</span>
                    {/if}
                  </div>
                  <div class="rowitem__meta">{u.email}</div>
                </div>
              </div>
            {:else}
              <div class="empty">No hay usuarios registrados</div>
            {/each}
          </div>
        {/if}
      </section>
    {/if}
  </div>
</main>

{#if selectedOrder}
  <div class="modal" onclick={() => selectedOrder = null}>
    <div class="modal__content" onclick={e => e.stopPropagation()}>
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
        <h2 style="font-size: 20px; font-weight: 900;">DETALLE DE ORDEN</h2>
        <button class="btn btn--danger" style="width: auto; padding: 4px 12px;" onclick={() => selectedOrder = null}>X</button>
      </div>
      
      <div style="margin-bottom: 20px;">
        <p style="margin-bottom: 5px;"><strong>ID:</strong> #{selectedOrder._id.slice(-6).toUpperCase()}</p>
        <p style="margin-bottom: 5px;"><strong>Fecha:</strong> {new Date(selectedOrder.createdAt).toLocaleString()}</p>
        <p style="margin-bottom: 5px;"><strong>Total:</strong> ${selectedOrder.totalPrice.toFixed(2)}</p>
        <p style="margin-bottom: 5px;"><strong>Estado:</strong> <span style="color: {selectedOrder.status === 'Completado' ? '#00ff88' : (selectedOrder.status === 'Cancelado' ? '#ff0028' : '#fff')}">{selectedOrder.status}</span></p>
        {#if app.auth.user?.role === 'administrador' && selectedOrder.userId}
          <p style="margin-bottom: 5px; margin-top: 15px;"><strong>Cliente:</strong> {selectedOrder.userId.username} ({selectedOrder.userId.email})</p>
        {/if}
      </div>

      <h3 style="font-size: 16px; font-weight: bold; margin-bottom: 10px; border-bottom: 1px solid #333; padding-bottom: 5px;">Productos</h3>
      <div style="max-height: 200px; overflow-y: auto; margin-bottom: 20px;">
        {#each selectedOrder.items as item}
          <div style="display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #222;">
            <div>
              <div>{item.quantity}x {item.productId?.nombre || 'Producto Desconocido'}</div>
            </div>
            <div>${((item.productId?.precio || 0) * item.quantity).toFixed(2)}</div>
          </div>
        {/each}
      </div>

      {#if app.auth.user?.role === 'administrador'}
        <div style="margin-top: 25px;">
          <h3 style="font-size: 12px; color: #888; margin-bottom: 10px; text-transform: uppercase;">Acciones de Administrador</h3>
          <div style="display: flex; gap: 10px;">
            <button class="btn" style="flex: 1; background: #00ff88; color: #000; font-weight: bold; border:none;" disabled={selectedOrder.status === 'Completado' || changingStatus} onclick={() => handleUpdateOrderStatus(selectedOrder._id, 'Completado')}>
              {changingStatus ? '...' : 'Completado'}
            </button>
            <button class="btn btn--danger" style="flex: 1;" disabled={selectedOrder.status === 'Cancelado' || changingStatus} onclick={() => handleUpdateOrderStatus(selectedOrder._id, 'Cancelado')}>
               {changingStatus ? '...' : 'Cancelar'}
            </button>
          </div>
        </div>
      {/if}
    </div>
  </div>
{/if}

<style>
  .page { min-height: 100vh; background: #000; color: #fff; padding: 20px; }
  .wrap { max-width: 1000px; margin: 0 auto; display: grid; gap: 20px; }
  .profile { display: flex; align-items: center; gap: 20px; padding: 20px; background: #111; border-radius: 12px; }
  .avatar { position: relative; }
  .avatar__circle, .avatar__img { width: 80px; height: 80px; border-radius: 50%; background: #333; display: flex; align-items: center; justify-content: center; font-size: 32px; font-weight: bold; object-fit: cover; }
  .avatar__edit { position: absolute; bottom: 0; right: 0; background: #ff0028; border: none; border-radius: 50%; width: 24px; height: 24px; display: flex; align-items: center; justify-content: center; cursor: pointer; color: #fff; }
  .profile__meta { flex: 1; }
  .profile__name { font-size: 24px; margin: 0; }
  .profile__since { font-size: 12px; opacity: 0.6; }
  .profile__badges { display: flex; gap: 8px; margin-top: 8px; }
  .pill { background: #222; padding: 4px 10px; border-radius: 20px; font-size: 10px; font-weight: bold; }
  .panel { background: #111; border-radius: 12px; padding: 20px; }
  .panel__head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; }
  .panel__title { font-size: 14px; margin: 0; opacity: 0.8; letter-spacing: 1px; }
  .btn { background: #222; color: #fff; border: 1px solid #333; padding: 8px 16px; border-radius: 6px; cursor: pointer; font-size: 12px; }
  .btn--danger { background: rgba(255, 0, 40, 0.2); border-color: #ff0028; }
  .grid2 { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
  .list { display: grid; gap: 10px; }
  .rowitem { background: #1a1a1a; padding: 12px; border-radius: 8px; display: flex; justify-content: space-between; align-items: center; }
  .rowitem__name { font-weight: bold; font-size: 13px; }
  .rowitem__meta { font-size: 11px; opacity: 0.6; }
  .settings__grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
  .setting { background: #1a1a1a; border: none; padding: 15px; border-radius: 8px; color: #fff; cursor: pointer; text-align: left; }
  .form-container { display: grid; gap: 15px; }
  .form-container input { background: #000; border: 1px solid #333; padding: 10px; border-radius: 6px; color: #fff; }
  .membership { background: linear-gradient(135deg, #2a0306, #000); padding: 20px; border-radius: 12px; }
  .support-grid { display: grid; grid-template-columns: 150px 1fr; gap: 10px; height: 300px; }
  .support-list { background: #080808; overflow-y: auto; }
  .conv-btn { width: 100%; padding: 10px; background: transparent; border: none; color: #fff; text-align: left; cursor: pointer; font-size: 12px; }
  .conv-btn.active { background: #ff0028; }
  .support-chat { display: flex; flex-direction: column; background: #080808; }
  .support-chat__messages { flex: 1; overflow-y: auto; padding: 10px; display: flex; flex-direction: column; gap: 8px; }
  .msg { max-width: 80%; padding: 8px 12px; border-radius: 12px; background: #222; font-size: 12px; }
  .msg--me { align-self: flex-end; background: #ff0028; }
  .support-chat__input { display: flex; gap: 5px; padding: 10px; }
  .support-chat__input input { flex: 1; background: #000; border: 1px solid #333; color: #fff; padding: 5px; }
  .unread { border-left: 3px solid #ff0028; }
  .empty { opacity: 0.5; font-size: 12px; text-align: center; margin: 20px; }
  .pay-tabs { display: flex; gap: 10px; margin-bottom: 20px; }
  .pay-tab { flex: 1; padding: 12px; background: #222; border: 1px solid #333; color: #fff; border-radius: 8px; cursor: pointer; opacity: 0.6; transition: 0.2s; font-weight: 500; font-size: 12px; }
  .pay-tab.active { background: #ff0028; border-color: #ff0028; opacity: 1; }
  .pay-icon { width: 44px; height: 44px; background: #222; border-radius: 8px; display: flex; align-items: center; justify-content: center; }
  .field-wrap { display: flex; flex-direction: column; gap: 6px; }
  .field-wrap label { font-size: 11px; opacity: 0.7; text-transform: uppercase; font-weight: bold; letter-spacing: 0.5px; }

  /* Modal de detalles de orden */
  .modal {
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    background: rgba(0,0,0,0.85);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
    backdrop-filter: blur(4px);
  }
  .modal__content {
    background: #111;
    border: 1px solid #222;
    padding: 25px;
    border-radius: 12px;
    width: 90%;
    max-width: 450px;
    box-shadow: 0 20px 40px rgba(0,0,0,0.8);
    position: relative;
    animation: modalIn 0.3s ease-out;
  }
  @keyframes modalIn {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
  }
</style>
