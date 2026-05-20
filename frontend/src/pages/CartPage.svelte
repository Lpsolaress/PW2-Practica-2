<script>
  import { app, showToast } from '../state/app.svelte.js';
  import { obtenerCarrito, actualizarCantidad, eliminarDelCarrito, vaciarCarrito } from '../services/carrito.js';
  import { checkout } from '../services/ordenes.js';
  import { listarProductos } from '../services/productos.js';

  let promo = $state('');
  let applyingPromo = $state(false);

  const cartItems = $derived.by(() => {
    return app.cart.items
      .map((item) => {
        const product = item.product || item.productId || item.producto;
        const quantity = Number(item.quantity || 0);
        if (!product) return null;
        return { product, quantity };
      })
      .filter(Boolean);
  });

  const cartCount = $derived(cartItems.reduce((sum, i) => sum + i.quantity, 0));
  const subtotal = $derived(
    cartItems.reduce((sum, i) => sum + Number(i.product.precio || 0) * i.quantity, 0)
  );
  const shipping = $derived(0);
  const taxRate = 0.0825;
  const tax = $derived(Math.round(subtotal * taxRate * 100) / 100);
  const total = $derived(Math.round((subtotal + shipping + tax) * 100) / 100);

  const youMightAlsoLike = $derived.by(() => {
    const inCart = new Set(cartItems.map((i) => i.product?._id));
    return (app.products.items || []).filter((p) => !inCart.has(p._id)).slice(0, 2);
  });

  let loadedForToken = $state(null);
  $effect(() => {
    if (!app.auth.token) return;
    if (loadedForToken === app.auth.token) return;
    loadedForToken = app.auth.token;
    cargar();
  });

  async function cargar() {
    app.cart.loading = true;
    app.cart.error = null;
    try {
      const data = await obtenerCarrito();
      app.cart.items = Array.isArray(data) ? data : data.items || [];
      if ((app.products.items || []).length === 0) {
        app.products.items = await listarProductos();
      }
    } catch (err) {
      app.cart.error = err?.message || 'No se pudo cargar el carrito';
      showToast(app.cart.error, 'error');
    } finally {
      app.cart.loading = false;
    }
  }

  async function setQty(productId, nextQty) {
    const qty = Number(nextQty);
    if (!productId) return;
    if (Number.isNaN(qty)) return;

    try {
      if (qty <= 0) {
        await eliminarDelCarrito(productId);
      } else {
        await actualizarCantidad(productId, qty);
      }
      await cargar();
    } catch (err) {
      showToast(err?.message || 'No se pudo actualizar el carrito', 'error');
    }
  }

  async function remove(productId) {
    try {
      await eliminarDelCarrito(productId);
      await cargar();
      showToast('Producto eliminado del carrito', 'success');
    } catch (err) {
      showToast(err?.message || 'No se pudo eliminar', 'error');
    }
  }

  async function clear() {
    const ok = confirm('¿Vaciar carrito?');
    if (!ok) return;
    try {
      await vaciarCarrito();
      await cargar();
      showToast('Carrito vacío', 'success');
    } catch (err) {
      showToast(err?.message || 'No se pudo vaciar', 'error');
    }
  }

  async function applyPromo() {
    applyingPromo = true;
    try {
      showToast('Código aplicado (demo)', 'success');
    } finally {
      applyingPromo = false;
    }
  }

  function money(value) {
    return Number(value || 0).toFixed(2);
  }

  let isCheckout = $state(false);
  let selectedAddress = $state(null);
  let selectedPayment = $state(null);
  let orderComplete = $state(false);
  let createdOrderId = $state(null);

  function startCheckout() {
    if (!app.auth.user) {
      showToast('Inicia sesión en tu perfil para tramitar el pedido', 'error');
      return;
    }
    const addrs = app.auth.user.addresses || [];
    const pays = app.auth.user.paymentMethods || [];
    
    if (addrs.length > 0) selectedAddress = addrs[0];
    if (pays.length > 0) selectedPayment = pays[0];
    
    isCheckout = true;
  }

  async function completeOrder() {
    if (!selectedAddress) return showToast('Selecciona una dirección o tienda de entrega', 'error');
    if (!selectedPayment) return showToast('Selecciona un método de pago', 'error');
    
    app.cart.loading = true;
    try {
      await new Promise(r => setTimeout(r, 1500)); // Simular retraso de pasarela de pago
      const orden = await checkout();
      createdOrderId = orden._id;
      await cargar(); // re-fetch cart (now empty from backend side)
      isCheckout = false;
      orderComplete = true;
    } catch(err) {
      showToast('Error procesando el pedido', 'error');
    } finally {
      app.cart.loading = false;
    }
  }
</script>

<main class="bag">
  <div class="bag__inner">
    {#if orderComplete}
      <div class="panel" style="text-align: center; padding: 60px 20px; margin-top: 40px;">
        <svg viewBox="0 0 24 24" width="64" height="64" fill="#00ff88" style="margin-bottom: 20px;"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/></svg>
        <h2 style="font-size: 32px; font-weight: 900; margin-bottom: 10px; color: #fff;">¡PAGO COMPLETADO!</h2>
        <div style="font-size: 14px; color: #ff0028; font-weight: bold; margin-bottom: 15px;">ORDEN #{createdOrderId ? createdOrderId.slice(-6).toUpperCase() : ''}</div>
        <p style="font-size: 16px; opacity: 0.8; max-width: 500px; margin: 0 auto 30px; line-height: 1.5;">
          Tu pedido ha sido procesado exitosamente usando <strong>{selectedPayment?.cardholder === 'Apple Pay' ? 'Apple Pay' : (selectedPayment?.type === 'paypal' ? 'PayPal' : 'Tarjeta')}</strong>.
        </p>

        {#if selectedAddress?.street?.includes('Recoger en')}
          <div style="display: inline-block; text-align: left; padding: 20px; background: rgba(0,0,0,0.3); border: 1px solid #333; border-radius: 12px; margin-bottom: 30px;">
            <div style="font-size: 12px; opacity: 0.6; margin-bottom: 5px; font-weight: bold;">📍 RECOGIDA EN SUCURSAL NUBA</div>
            <div style="font-size: 16px; color: #fff;">{selectedAddress.street.replace('Recoger en: ', '')}</div>
            <div style="font-size: 13px; opacity: 0.7; margin-top: 8px;">Te avisaremos cuando tu orden esté lista para recoger.</div>
          </div>
        {:else}
          <div style="display: inline-block; text-align: left; padding: 20px; background: rgba(0,0,0,0.3); border: 1px solid #333; border-radius: 12px; margin-bottom: 30px;">
            <div style="font-size: 12px; opacity: 0.6; margin-bottom: 5px; font-weight: bold;">🚚 ENVÍO A DOMICILIO</div>
            <div style="font-size: 16px; color: #fff;">{selectedAddress?.street}</div>
            <div style="font-size: 13px; opacity: 0.7; margin-top: 8px;">El paquete va en camino hacia tu ubicación.</div>
          </div>
        {/if}
        
        <br>
        <button class="checkout" style="max-width: 300px;" onclick={() => { orderComplete = false; }}>VOLVER AL CARRITO</button>
      </div>

    {:else if isCheckout}
      <div class="bag__top">
        <div class="bag__title">
          <span class="logo">A</span>
          <span class="title-text">CHECKOUT</span>
        </div>
        <button class="link-btn" onclick={() => isCheckout = false}>← Volver a Cesta</button>
      </div>

      <div class="bag__grid">
        <div style="display: flex; flex-direction: column; gap: 20px;">
          <section class="panel">
            <h2 style="font-size: 16px; margin-bottom: 15px; border-bottom: 1px solid #333; padding-bottom: 10px;">1. Dirección de Entrega o Recogida</h2>
            <p style="font-size: 12px; margin-bottom: 15px; opacity: 0.7;">Elije si quieres que lo enviemos a tu domicilio o prefieres recoger de una de nuestras tiendas físicas.</p>
            {#if (app.auth.user?.addresses || []).length === 0}
              <div class="empty" style="text-align: left; padding: 0;">No tienes direcciones guardadas. Ve a tu perfil para agregar una.</div>
            {:else}
              <div style="display:flex; flex-direction:column; gap: 10px;">
                {#each app.auth.user.addresses as addr}
                  <label style="display: flex; align-items: flex-start; gap: 12px; padding: 15px; border: 1px solid {selectedAddress?._id === addr._id ? '#ff0028' : '#333'}; background: {selectedAddress?._id === addr._id ? 'rgba(255,0,40,0.1)' : 'rgba(0,0,0,0.2)'}; border-radius: 12px; cursor: pointer; transition: 0.2s;">
                    <input type="radio" name="checkout_addr" value={addr} bind:group={selectedAddress} style="margin-top: 2px;" />
                    <div>
                      <b style="font-size: 11px; opacity: 0.7; display: block; margin-bottom: 4px;">{addr.street.includes('Recoger en') ? 'SUCURSAL NUBA' : 'DOMICILIO'}</b>
                      <span style="font-size: 14px;">{addr.street}</span>
                    </div>
                  </label>
                {/each}
              </div>
            {/if}
          </section>

          <section class="panel">
            <h2 style="font-size: 16px; margin-bottom: 15px; border-bottom: 1px solid #333; padding-bottom: 10px;">2. Método de Pago</h2>
            {#if (app.auth.user?.paymentMethods || []).length === 0}
              <div class="empty" style="text-align: left; padding: 0;">No tienes métodos de pago guardados. Ve a tu perfil para agregar uno.</div>
            {:else}
              <div style="display:flex; flex-direction:column; gap: 10px;">
                {#each app.auth.user.paymentMethods as pay}
                  <label style="display: flex; align-items: center; gap: 12px; padding: 15px; border: 1px solid {selectedPayment?._id === pay._id ? '#ff0028' : '#333'}; background: {selectedPayment?._id === pay._id ? 'rgba(255,0,40,0.1)' : 'rgba(0,0,0,0.2)'}; border-radius: 12px; cursor: pointer; transition: 0.2s;">
                    <input type="radio" name="checkout_pay" value={pay} bind:group={selectedPayment} />
                    <div style="font-size: 14px; display: flex; align-items: center; gap: 10px;">
                      {#if pay.type === 'paypal'}
                        <svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor"><path d="M7 2h10a5 5 0 0 1 5 5c0 3-2.5 5.5-5.5 5.5H14l-1 6h-3l1.5-8.5H10L8 2z"/></svg>
                        PayPal ({pay.cardholder})
                       {:else if pay.type === 'otro' && pay.cardholder === 'Apple Pay'}
                        <svg viewBox="0 0 384 512" width="20" height="20" fill="currentColor"><path d="M318.7 268.7c-.2-36.7 16.4-64.4 50-84.8-18.8-26.9-47.2-41.7-84.7-44.6-35.5-2.8-74.3 20.7-88.5 20.7-15 0-49.4-19.7-76.4-19.7C63.3 141.2 4 184.8 4 273.5q0 39.3 14.4 81.2c12.8 36.7 59 126.7 107.2 125.2 25.2-.6 43-17.9 75.8-17.9 31.8 0 48.3 17.9 76.4 17.9 48.6-.7 90.4-82.5 102.6-119.3-65.2-30.7-61.7-90-61.7-91.9zm-56.6-164.2c27.3-32.4 24.8-61.9 24-72.5-24.1 1.4-52 16.4-67.9 34.9-17.5 19.8-27.8 44.3-25.6 71.9 26.1 2 49.9-11.4 69.5-34.3z"/></svg>
                        Apple Pay
                      {:else}
                        <svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor"><path d="M22 6H2a2 2 0 0 0-2 2v8a2 2 0 0 0 2 2h20a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2zm-3 8h-3l-1-4-1 4h-3l1-6h2.5l.5 3 .5-3H19l-1 6z"/></svg>
                        Tarjeta ({pay.last4})
                      {/if}
                    </div>
                  </label>
                {/each}
              </div>
            {/if}
          </section>
        </div>

        <aside class="summary">
          <h2 class="summary__title">RESUMEN DEL PEDIDO</h2>
          <div class="totals">
             <div class="line">
              <span class="muted">Subtotal</span>
              <span>${money(subtotal)}</span>
            </div>
            <div class="line">
              <span class="muted">Envío</span>
              <span>{selectedAddress?.street?.includes('Recoger en') ? 'GRATIS (Tienda)' : '$' + money(shipping)}</span>
            </div>
            <div class="line">
              <span class="muted">Impuesto</span>
              <span>${money(tax)}</span>
            </div>
            <div class="divider"></div>
            <div class="line line--total">
              <span>TOTAL AL COBRO</span>
              <span>${money(total)}</span>
            </div>
          </div>
          
          {#if selectedPayment?.cardholder === 'Apple Pay'}
            <button class="checkout" style="background:#000; border: 1px solid #fff; display: flex; align-items: center; justify-content: center; gap: 8px;" type="button" onclick={completeOrder} disabled={!selectedAddress || !selectedPayment || app.cart.loading}>
              <svg viewBox="0 0 384 512" width="20" height="20" fill="white"><path d="M318.7 268.7c-.2-36.7 16.4-64.4 50-84.8-18.8-26.9-47.2-41.7-84.7-44.6-35.5-2.8-74.3 20.7-88.5 20.7-15 0-49.4-19.7-76.4-19.7C63.3 141.2 4 184.8 4 273.5q0 39.3 14.4 81.2c12.8 36.7 59 126.7 107.2 125.2 25.2-.6 43-17.9 75.8-17.9 31.8 0 48.3 17.9 76.4 17.9 48.6-.7 90.4-82.5 102.6-119.3-65.2-30.7-61.7-90-61.7-91.9zm-56.6-164.2c27.3-32.4 24.8-61.9 24-72.5-24.1 1.4-52 16.4-67.9 34.9-17.5 19.8-27.8 44.3-25.6 71.9 26.1 2 49.9-11.4 69.5-34.3z"/></svg> 
              {app.cart.loading ? '...' : 'Pagar'}
            </button>
          {:else}
            <button class="checkout" type="button" onclick={completeOrder} disabled={!selectedAddress || !selectedPayment || app.cart.loading}>
              {app.cart.loading ? 'Procesando...' : 'CONFIRMAR Y PAGAR'}
            </button>
          {/if}
        </aside>
      </div>

    {:else}
      <div class="bag__top">
      <div class="bag__title">
        <span class="logo">A</span>
        <span class="title-text">CESTA</span>
      </div>
    </div>

    <div class="bag__grid">
      <section class="panel">
        <div class="panel__header">
          <h1>Revisa tus productos</h1>
          <div class="panel__meta">
            <span class="muted">{cartCount} productos</span>
            <button class="link-btn" type="button" onclick={cargar} disabled={app.cart.loading}>
              {app.cart.loading ? 'Cargando…' : 'Recargar'}
            </button>
            {#if cartCount > 0}
              <button class="link-btn link-btn--danger" type="button" onclick={clear}>Vaciar</button>
            {/if}
          </div>
        </div>

        {#if app.cart.error}
          <div class="error" role="alert">{app.cart.error}</div>
        {/if}

        {#if app.cart.loading && cartItems.length === 0}
          <div class="empty">Cargando…</div>
        {:else if cartItems.length === 0}
          <div class="empty">Tu carrito está vacío</div>
        {:else}
          <div class="items">
            {#each cartItems as item (item.product._id)}
              <article class="item">
                <div class="item__img">
                  {#if item.product.imagen}
                    <img src={item.product.imagen.startsWith('http') ? item.product.imagen : `http://localhost:3000${item.product.imagen}`} alt={item.product.nombre} />
                  {:else}
                    <div class="img-placeholder"></div>
                  {/if}
                </div>

                <div class="item__main">
                  <div class="item__row">
                    <div class="item__title">{item.product.nombre}</div>
                    <div class="item__price">${money(item.product.precio)}</div>
                  </div>

                  <div class="item__sub">
                    <span class="muted">Productos</span>
                    <span class="dot">•</span>
                    <span class="muted">{item.product.activo !== false ? 'Activo' : 'No activo'}</span>
                  </div>

                  <div class="item__controls">
                    <div class="qty">
                      <button class="qty__btn" type="button" onclick={() => setQty(item.product._id, item.quantity - 1)} aria-label="Disminuir">−</button>
                      <span class="qty__value">Cant: {item.quantity}</span>
                      <button class="qty__btn" type="button" onclick={() => setQty(item.product._id, item.quantity + 1)} aria-label="Aumentar">+</button>
                    </div>

                    <div class="actions">
                      <button class="icon" type="button" aria-label="Favorito">♡</button>
                      <button class="icon icon--danger" type="button" onclick={() => remove(item.product._id)} aria-label="Eliminar">🗑</button>
                    </div>
                  </div>
                </div>
              </article>
            {/each}
          </div>
        {/if}
      </section>

      <aside class="summary">
        <h2 class="summary__title">RESUMEN</h2>

        <div class="promo">
          <div class="promo__label">¿TIENES UN CÓDIGO PROMOCIONAL?</div>
          <div class="promo__row">
            <input class="promo__input" placeholder="INTRODUCIR CÓDIGO" bind:value={promo} />
            <button class="promo__btn" type="button" onclick={applyPromo} disabled={applyingPromo}>
              {applyingPromo ? '…' : 'APLICAR'}
            </button>
          </div>
        </div>

        <div class="totals">
           <div class="line">
            <span class="muted">Subtotal</span>
            <span>${money(subtotal)}</span>
          </div>
          <div class="line">
            <span class="muted">Envío y gestión estimado</span>
            <span>${money(shipping)}</span>
          </div>
          <div class="line">
            <span class="muted">Impuesto estimado</span>
            <span>${money(tax)}</span>
          </div>
          <div class="divider"></div>
          <div class="line line--total">
            <span>TOTAL</span>
            <span>${money(total)}</span>
          </div>
        </div>

        <button class="checkout" type="button" disabled={cartCount === 0} onclick={startCheckout}>TRAMITAR PEDIDO</button>
        <button class="paypal" type="button" disabled={cartCount === 0} onclick={startCheckout}>PAYPAL</button>

        <div class="ship">
          <div class="ship__title">ENVÍO GRATUITO</div>
          <div class="ship__text">Los miembros obtienen envío gratuito en pedidos de $50 o más. <span class="ship__link">Únete</span></div>
        </div>
      </aside>
    </div>

    {#if !orderComplete && !isCheckout}
      <section class="like">
        <h2 class="like__title">TAMBIÉN TE PODRÍA GUSTAR</h2>
        <div class="like__grid">
          {#each youMightAlsoLike as p (p._id)}
            <div class="like__card">
              <div class="like__img" aria-hidden="true"></div>
              <div class="like__name">{p.nombre}</div>
              <div class="like__price">${money(p.precio)}</div>
            </div>
          {/each}
          {#if youMightAlsoLike.length === 0}
            <div class="muted">—</div>
          {/if}
        </div>
      </section>
    {/if}
    
    {/if} <!-- End of main blocks -->
  </div>
</main>

<style>
  .bag {
    min-height: 100svh;
    background: radial-gradient(1000px 600px at 20% 0%, rgba(255, 0, 60, 0.22), transparent 55%),
      radial-gradient(900px 520px at 80% 10%, rgba(255, 50, 0, 0.14), transparent 60%),
      linear-gradient(180deg, #0c0b0f 0%, #09080b 100%);
    color: var(--text-strong);
  }

  .bag__inner {
    max-width: 1200px;
    margin: 0 auto;
    padding: 22px 16px 54px;
  }

  .bag__top {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 18px;
  }

  .bag__title {
    display: inline-flex;
    align-items: center;
    gap: 10px;
    font-weight: 800;
    letter-spacing: 0.6px;
  }

  .logo {
    width: 28px;
    height: 28px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    border-radius: 8px;
    background: rgba(255, 0, 60, 0.22);
    border: 1px solid rgba(255, 0, 60, 0.35);
  }

  .title-text {
    opacity: 0.9;
  }

  .bag__grid {
    display: grid;
    grid-template-columns: 1.4fr 0.9fr;
    gap: 26px;
    align-items: start;
  }

  .panel {
    padding: 18px;
    border-radius: 18px;
    border: 1px solid rgba(255, 255, 255, 0.08);
    background: rgba(0, 0, 0, 0.18);
    backdrop-filter: blur(10px);
    box-shadow: rgba(0, 0, 0, 0.35) 0 22px 48px;
  }

  .panel__header {
    display: flex;
    justify-content: space-between;
    gap: 12px;
    flex-wrap: wrap;
    margin-bottom: 10px;
    align-items: end;
  }

  h1 {
    font-size: 16px;
    letter-spacing: 0.2px;
  }

  .panel__meta {
    display: inline-flex;
    gap: 12px;
    align-items: center;
  }

  .muted {
    color: rgba(255, 255, 255, 0.62);
  }

  .link-btn {
    appearance: none;
    border: 0;
    background: transparent;
    color: rgba(255, 255, 255, 0.8);
    cursor: pointer;
    font-size: 13px;
    padding: 4px 6px;
    border-radius: 10px;
  }

  .link-btn:hover {
    background: rgba(255, 255, 255, 0.06);
  }

  .link-btn--danger:hover {
    background: rgba(255, 0, 60, 0.12);
  }

  .error {
    color: #ff879c;
    font-size: 13px;
    margin: 10px 0;
  }

  .empty {
    padding: 18px 6px;
    color: rgba(255, 255, 255, 0.62);
    font-size: 14px;
  }

  .items {
    display: grid;
    gap: 18px;
    margin-top: 12px;
  }

  .item {
    display: grid;
    grid-template-columns: 110px 1fr;
    gap: 16px;
    padding: 14px;
    border-radius: 16px;
    border: 1px solid rgba(255, 255, 255, 0.08);
    background: rgba(0, 0, 0, 0.14);
  }

  .item__img {
    width: 110px;
    height: 110px;
    border-radius: 14px;
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(255, 255, 255, 0.08);
    display: grid;
    place-items: center;
    overflow: hidden;
  }

  .item__img img {
    width: 100%;
    height: 100%;
    object-fit: contain;
    padding: 8px;
  }

  .img-placeholder {
    width: 78%;
    height: 58%;
    border-radius: 12px;
    background: linear-gradient(135deg, rgba(255, 255, 255, 0.22), rgba(255, 255, 255, 0.06));
    transform: rotate(-10deg);
  }

  .item__row {
    display: flex;
    justify-content: space-between;
    gap: 12px;
    align-items: baseline;
  }

  .item__title {
    font-weight: 800;
    letter-spacing: 0.3px;
    font-size: 14px;
    text-transform: uppercase;
  }

  .item__price {
    font-weight: 800;
    font-size: 14px;
    color: rgba(255, 255, 255, 0.9);
  }

  .item__sub {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    margin-top: 6px;
    font-size: 12px;
  }

  .dot {
    opacity: 0.35;
  }

  .item__controls {
    margin-top: 12px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 12px;
    flex-wrap: wrap;
  }

  .qty {
    display: inline-flex;
    align-items: center;
    gap: 10px;
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 999px;
    padding: 8px 10px;
    background: rgba(0, 0, 0, 0.18);
  }

  .qty__btn {
    width: 28px;
    height: 28px;
    border-radius: 999px;
    border: 1px solid rgba(255, 255, 255, 0.12);
    background: rgba(255, 255, 255, 0.04);
    color: rgba(255, 255, 255, 0.9);
    cursor: pointer;
  }

  .qty__btn:hover {
    background: rgba(255, 255, 255, 0.08);
  }

  .qty__value {
    font-size: 13px;
    color: rgba(255, 255, 255, 0.78);
    min-width: 70px;
    text-align: center;
  }

  .actions {
    display: inline-flex;
    gap: 10px;
    align-items: center;
  }

  .icon {
    width: 34px;
    height: 34px;
    border-radius: 999px;
    border: 1px solid rgba(255, 255, 255, 0.12);
    background: rgba(255, 255, 255, 0.04);
    color: rgba(255, 255, 255, 0.82);
    cursor: pointer;
    display: grid;
    place-items: center;
    font-size: 14px;
  }

  .icon:hover {
    background: rgba(255, 255, 255, 0.08);
  }

  .icon--danger:hover {
    background: rgba(255, 0, 60, 0.12);
    border-color: rgba(255, 0, 60, 0.24);
  }

  .summary {
    padding: 18px;
    border-radius: 18px;
    border: 1px solid rgba(255, 255, 255, 0.08);
    background: rgba(0, 0, 0, 0.22);
    box-shadow: rgba(0, 0, 0, 0.35) 0 22px 48px;
  }

  .summary__title {
    font-size: 16px;
    margin-bottom: 16px;
    letter-spacing: 0.4px;
  }

  .promo__label {
    font-size: 11px;
    letter-spacing: 0.5px;
    color: rgba(255, 255, 255, 0.62);
    margin-bottom: 10px;
  }

  .promo__row {
    display: grid;
    grid-template-columns: 1fr auto;
    gap: 10px;
    margin-bottom: 16px;
  }

  .promo__input {
    width: 100%;
    padding: 12px 12px;
    border-radius: 10px;
    border: 1px solid rgba(255, 255, 255, 0.14);
    background: rgba(0, 0, 0, 0.18);
    color: rgba(255, 255, 255, 0.88);
    outline: none;
  }

  .promo__btn {
    padding: 12px 14px;
    border-radius: 10px;
    border: 1px solid rgba(255, 255, 255, 0.14);
    background: rgba(255, 255, 255, 0.06);
    color: rgba(255, 255, 255, 0.9);
    cursor: pointer;
    letter-spacing: 0.3px;
    font-weight: 700;
  }

  .promo__btn:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

  .totals {
    display: grid;
    gap: 10px;
    margin: 14px 0 18px;
    font-size: 13px;
  }

  .line {
    display: flex;
    justify-content: space-between;
    gap: 12px;
  }

  .divider {
    height: 1px;
    background: rgba(255, 255, 255, 0.12);
    margin: 6px 0;
  }

  .line--total {
    font-weight: 900;
    letter-spacing: 0.3px;
  }

  .checkout {
    width: 100%;
    border: 0;
    border-radius: 12px;
    padding: 14px 14px;
    background: #ff0028;
    color: white;
    font-weight: 900;
    letter-spacing: 0.4px;
    cursor: pointer;
    margin-bottom: 10px;
  }

  .checkout:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .paypal {
    width: 100%;
    border: 1px solid rgba(255, 255, 255, 0.14);
    border-radius: 12px;
    padding: 14px 14px;
    background: rgba(255, 255, 255, 0.06);
    color: rgba(255, 255, 255, 0.9);
    font-weight: 900;
    cursor: pointer;
    margin-bottom: 14px;
  }

  .paypal:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .ship {
    border-radius: 14px;
    padding: 12px;
    border: 1px solid rgba(255, 255, 255, 0.08);
    background: rgba(255, 255, 255, 0.03);
  }

  .ship__title {
    font-size: 12px;
    font-weight: 900;
    letter-spacing: 0.4px;
    margin-bottom: 6px;
  }

  .ship__text {
    font-size: 12px;
    color: rgba(255, 255, 255, 0.68);
  }

  .ship__link {
    color: rgba(255, 255, 255, 0.9);
    text-decoration: underline;
    cursor: pointer;
  }

  .like {
    margin-top: 34px;
  }

  .like__title {
    font-size: 16px;
    margin: 0 0 14px;
    letter-spacing: 0.4px;
  }

  .like__grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 18px;
  }

  .like__card {
    border-radius: 18px;
    border: 1px solid rgba(255, 255, 255, 0.08);
    background: rgba(0, 0, 0, 0.18);
    padding: 14px;
  }

  .like__img {
    height: 140px;
    border-radius: 14px;
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(255, 255, 255, 0.08);
    margin-bottom: 12px;
  }

  .like__name {
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.25px;
    font-size: 13px;
    margin-bottom: 6px;
  }

  .like__price {
    color: rgba(255, 255, 255, 0.76);
    font-size: 12px;
  }

  @media (max-width: 980px) {
    .bag__grid {
      grid-template-columns: 1fr;
    }

    .like__grid {
      grid-template-columns: 1fr;
    }
  }
</style>
