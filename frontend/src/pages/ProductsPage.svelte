<script>
  import { app, isAdmin, isAuthenticated, navigate, showToast } from '../state/app.svelte.js';
  import { listarProductos, crearProducto, actualizarProducto, eliminarProducto } from '../services/productos.js';
  import { agregarAlCarrito, obtenerCarrito } from '../services/carrito.js';
  import ProductForm from '../components/ProductForm.svelte';
  import ProductModal from '../components/ProductModal.svelte';

  let query = $state('');
  let selected = $state(null);
  let formOpen = $state(false);
  let editing = $state(null);
  let saving = $state(false);
  let selectedCategories = $state([]);
  let selectedPlatforms = $state([]);
  let selectedPriceRanges = $state([]);
  let visibleCount = $state(6);

  const CATEGORIES = ['Consolas', 'Videojuegos', 'Accesorios', 'Otros'];
  const PLATFORMS = ['Nintendo', 'Playstation', 'Xbox', 'Otro'];
  const PRICE_RANGES = [
    { id: '0-50', label: '$0 - $50', min: 0, max: 50 },
    { id: '50-150', label: '$50 - $150', min: 50, max: 150 },
    { id: '150+', label: '$150+', min: 150, max: Infinity }
  ];

  const productosFiltrados = $derived.by(() => {
    const q = query.trim().toLowerCase();
    const items = app.products.items || [];
    const base = !q ? items : items.filter((p) => (p.nombre || '').toLowerCase().includes(q));
    return base.filter((p) => {
      const meta = metaFor(p);
      if (selectedCategories.length > 0 && !selectedCategories.includes(meta.category)) return false;
      if (selectedPlatforms.length > 0 && !selectedPlatforms.includes(meta.platform)) return false;
      if (selectedPriceRanges.length > 0 && !selectedPriceRanges.includes(meta.priceRangeId)) return false;
      return true;
    });
  });

  const contador = $derived(productosFiltrados.length);
  const productosVisibles = $derived(productosFiltrados.slice(0, visibleCount));

  let loadedForToken = $state(undefined);
  $effect(() => {
    const tokenKey = app.auth.token || null;
    if (loadedForToken === tokenKey) return;
    loadedForToken = tokenKey;
    cargar();
  });

  $effect(() => {
    query;
    selectedCategories;
    selectedPlatforms;
    selectedPriceRanges;
    visibleCount = 6;
  });

  async function cargar() {
    app.products.loading = true;
    app.products.error = null;
    try {
      app.products.items = await listarProductos();
    } catch (err) {
      app.products.error = err?.message || 'No se pudieron cargar productos';
      showToast(app.products.error, 'error');
    } finally {
      app.products.loading = false;
    }
  }

  function abrirCrear() {
    editing = null;
    formOpen = true;
  }

  function abrirEditar(p) {
    editing = { ...p, plataforma: p.plataforma || metaFor(p).platform, categoria: p.categoria || metaFor(p).category };
    formOpen = true;
  }

  async function guardar(payload) {
    saving = true;
    try {
      if (editing?._id) {
        await actualizarProducto(editing._id, payload);
      } else {
        await crearProducto(payload);
      }
      await cargar();
      clearFilters();
      formOpen = false;
      editing = null;
      showToast('Producto guardado', 'success');
    } catch (err) {
      showToast(err?.message || 'No se pudo guardar', 'error');
    } finally {
      saving = false;
    }
  }

  async function borrar(p) {
    if (!p?._id) return;
    const ok = confirm(`¿Borrar "${p.nombre}"?`);
    if (!ok) return;

    try {
      await eliminarProducto(p._id);
      await cargar();
      showToast('Producto eliminado', 'success');
    } catch (err) {
      showToast(err?.message || 'No se pudo borrar', 'error');
    }
  }

  function cerrarForm() {
    if (saving) return;
    formOpen = false;
    editing = null;
  }

  async function addToCart(p) {
    if (!isAuthenticated()) {
      showToast('Crea una cuenta o inicia sesión para comprar', 'info');
      navigate('/login');
      return;
    }
    try {
      await agregarAlCarrito(p._id, 1);
      const cart = await obtenerCarrito();
      app.cart.items = Array.isArray(cart) ? cart : cart.items || [];
      showToast('Añadido al carrito', 'success');
    } catch (err) {
      showToast(err?.message || 'No se pudo añadir al carrito', 'error');
    }
  }

  function toggleInArray(arr, value) {
    return arr.includes(value) ? arr.filter((v) => v !== value) : [...arr, value];
  }

  function toggleCategory(cat) {
    selectedCategories = toggleInArray(selectedCategories, cat);
  }

  function togglePlatform(g) {
    selectedPlatforms = toggleInArray(selectedPlatforms, g);
  }

  function togglePriceRange(id) {
    selectedPriceRanges = toggleInArray(selectedPriceRanges, id);
  }

  function clearFilters() {
    selectedCategories = [];
    selectedPlatforms = [];
    selectedPriceRanges = [];
    query = '';
  }

  function loadMore() {
    visibleCount = Math.min(visibleCount + 6, productosFiltrados.length);
  }

  function hashOf(value) {
    const str = String(value ?? '');
    let h = 0;
    for (let i = 0; i < str.length; i++) h = (h * 31 + str.charCodeAt(i)) >>> 0;
    return h;
  }

  function metaFor(p) {
    const key = p?._id || p?.nombre || '';
    const h = hashOf(key);
    
    // Si el producto tiene categoría real, usarla. De lo contrario, caer en el hash (compatibilidad)
    const category = p?.categoria || CATEGORIES[h % CATEGORIES.length];
    
    const platform = p?.plataforma || PLATFORMS[(h >> 3) % PLATFORMS.length];
    const badge = h % 5 === 0 ? 'MÁS VENDIDO' : h % 7 === 0 ? 'NOVEDAD' : '';
    const price = Number(p?.precio || 0);
    const range = PRICE_RANGES.find((r) => price >= r.min && price < r.max) || PRICE_RANGES[0];
    return { category, platform, badge, priceRangeId: range.id };
  }

  function mediaStyleFor(p) {
    const h = hashOf(p?._id || p?.nombre || '');
    const hue = h % 360;
    const hue2 = (hue + 40 + (h % 60)) % 360;
    return `background: linear-gradient(135deg, hsla(${hue}, 75%, 60%, 0.18), hsla(${hue2}, 75%, 52%, 0.08));`;
  }
</script>

<main class="page">
  <div class="shell">
    <aside class="sidebar">
      <div class="sidebar__section">
        <div class="sidebar__title">CATEGORÍA</div>
        <div class="checks">
          {#each CATEGORIES as cat (cat)}
            <label class="check">
              <input type="checkbox" checked={selectedCategories.includes(cat)} onchange={() => toggleCategory(cat)} />
              <span>{cat}</span>
            </label>
          {/each}
        </div>
      </div>

      <div class="sidebar__section">
        <div class="sidebar__title">PLATAFORMA</div>
        <div class="checks">
          {#each PLATFORMS as g (g)}
            <label class="check">
              <input type="checkbox" checked={selectedPlatforms.includes(g)} onchange={() => togglePlatform(g)} />
              <span>{g}</span>
            </label>
          {/each}
        </div>
      </div>

      <div class="sidebar__section">
        <div class="sidebar__title">RANGO DE PRECIO</div>
        <div class="checks">
          {#each PRICE_RANGES as r (r.id)}
            <label class="check">
              <input
                type="checkbox"
                checked={selectedPriceRanges.includes(r.id)}
                onchange={() => togglePriceRange(r.id)}
              />
              <span>{r.label}</span>
            </label>
          {/each}
        </div>
      </div>

      <div class="sidebar__actions">
        <button class="btn btn--ghost btn--full" type="button" onclick={clearFilters} disabled={app.products.loading}>
          Limpiar filtros
        </button>
      </div>
    </aside>

    <section class="content">
      <div class="topbar">
        <div class="brandline">
          <div class="brandline__title">NUBA</div>
          <div class="brandline__meta">{productosFiltrados.length} productos</div>
        </div>

        <div class="topbar__actions">
          <div class="search">
            <svg class="search__icon" viewBox="0 0 24 24" width="18" height="18" fill="none" aria-hidden="true">
              <path
                d="M10.5 18.5a8 8 0 1 1 0-16 8 8 0 0 1 0 16Z"
                stroke="currentColor"
                stroke-width="2"
              />
              <path d="M16.5 16.5 21 21" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
            </svg>
            <input class="search__input" placeholder="Buscar productos…" bind:value={query} />
          </div>

          {#if isAdmin()}
            <button class="btn btn--ghost" type="button" onclick={abrirCrear}>Nuevo</button>
          {/if}
          <button class="btn btn--ghost" type="button" onclick={cargar} disabled={app.products.loading}>
            {app.products.loading ? 'Cargando…' : 'Recargar'}
          </button>
        </div>
      </div>

      <div class="hero">
        <div>
          <h1 class="hero__title">DOMINA LA PARTIDA</h1>
          <p class="hero__text">
            El máximo rendimiento para tu consola. Encuentra las últimas innovaciones del gaming para jugadores de cualquier nivel.
          </p>
        </div>
      </div>

      {#if app.products.error}
        <div class="error" role="alert">{app.products.error}</div>
      {/if}

      <div class="grid">
        {#if app.products.loading && app.products.items.length === 0}
          {#each Array(6) as _, i (i)}
            <div class="card card--skeleton">
              <div class="card__media"></div>
              <div class="card__body">
                <div class="sk sk--title"></div>
                <div class="sk sk--meta"></div>
                <div class="sk sk--price"></div>
                <div class="sk sk--btn"></div>
              </div>
            </div>
          {/each}
        {:else if productosVisibles.length === 0}
          <div class="empty">No hay productos</div>
        {:else}
          {#each productosVisibles as p, i (p._id)}
            {@const meta = metaFor(p)}
            <article class="card" style="animation-delay: {i * 0.05}s">
              <button class="card__media" type="button" style={mediaStyleFor(p)} onclick={() => (selected = p)}>
                {#if meta.badge}
                  <span class="badge">{meta.badge}</span>
                {/if}
                {#if p.imagen}
                  <img src={p.imagen.startsWith('http') ? p.imagen : `http://localhost:3000${p.imagen}`} alt={p.nombre} class="card__img" />
                {:else}
                  <div class="mock" aria-hidden="true"></div>
                {/if}
              </button>

              <div class="card__body">
                <div class="card__name">{(p.nombre || 'Producto').toUpperCase()}</div>
                <div class="card__meta">
                  <span>{meta.platform}</span>
                  <span class="dot">•</span>
                  <span>{meta.category}</span>
                </div>
                <div class="card__price">${Number(p.precio || 0).toFixed(2)}</div>

                <div class="card__actions">
                  <button class="cta" type="button" onclick={() => addToCart(p)}>
                    <svg viewBox="0 0 24 24" width="18" height="18" fill="none" aria-hidden="true">
                      <path
                        d="M7 7h14l-1.7 8.5a2 2 0 0 1-2 1.6H9.2a2 2 0 0 1-2-1.6L5.5 3.5H3"
                        stroke="currentColor"
                        stroke-width="2"
                        stroke-linecap="round"
                        stroke-linejoin="round"
                      />
                      <path d="M9.5 21a1 1 0 1 0 0-2 1 1 0 0 0 0 2Z" fill="currentColor" />
                      <path d="M17.5 21a1 1 0 1 0 0-2 1 1 0 0 0 0 2Z" fill="currentColor" />
                    </svg>
                    <span>{isAuthenticated() ? 'AÑADIR AL CARRITO' : 'COMPRAR (ACCEDER)'}</span>
                  </button>

                  {#if isAdmin()}
                    <button class="icon" type="button" onclick={() => abrirEditar(p)} aria-label="Editar">✎</button>
                    <button class="icon icon--danger" type="button" onclick={() => borrar(p)} aria-label="Borrar">🗑</button>
                  {/if}
                </div>

                <div class="status">
                  <span class="pill" data-active={p.activo !== false ? 'true' : 'false'}>
                    {p.activo !== false ? 'Activo' : 'No activo'}
                  </span>
                </div>
              </div>
            </article>
          {/each}
        {/if}
      </div>

      {#if !app.products.loading && productosFiltrados.length > productosVisibles.length}
        <div class="load">
          <button class="load__btn" type="button" onclick={loadMore}>CARGAR MÁS</button>
        </div>
      {/if}
    </section>
  </div>

  {#if formOpen}
    <div class="sheet">
      <div class="sheet__panel">
        <div class="sheet__header">
          <h2 class="sheet__title">{editing ? 'Editar producto' : 'Nuevo producto'}</h2>
          <button class="btn btn--ghost" type="button" onclick={cerrarForm}>×</button>
        </div>
        <ProductForm initial={editing} onSave={guardar} onCancel={cerrarForm} saving={saving} />
      </div>
    </div>
  {/if}

  <ProductModal product={selected} onClose={() => (selected = null)} />
</main>

<style>
  .page {
    min-height: calc(100svh - 58px);
    padding: 22px 16px 50px;
    background: radial-gradient(1200px 800px at 20% 0%, rgba(255, 0, 40, 0.18), rgba(0, 0, 0, 0)),
      radial-gradient(1200px 900px at 10% 90%, rgba(124, 92, 255, 0.14), rgba(0, 0, 0, 0)),
      linear-gradient(180deg, rgba(10, 10, 14, 0.82), rgba(10, 10, 14, 0.92));
  }

  .shell {
    max-width: 1200px;
    margin: 0 auto;
    display: grid;
    grid-template-columns: 220px 1fr;
    gap: 26px;
    align-items: start;
  }

  .sidebar {
    position: sticky;
    top: 80px;
    border-radius: 18px;
    padding: 14px 14px 10px;
    border: 1px solid rgba(255, 255, 255, 0.08);
    background: rgba(0, 0, 0, 0.18);
    backdrop-filter: blur(10px);
    box-shadow: rgba(0, 0, 0, 0.35) 0 22px 48px;
  }

  .sidebar__section {
    padding: 10px 6px 12px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  }

  .sidebar__section:last-of-type {
    border-bottom: 0;
  }

  .sidebar__title {
    font-size: 12px;
    letter-spacing: 0.5px;
    font-weight: 850;
    color: rgba(255, 255, 255, 0.9);
    margin-bottom: 10px;
    text-transform: uppercase;
  }

  .checks {
    display: grid;
    gap: 10px;
  }

  .check {
    display: inline-flex;
    align-items: center;
    gap: 10px;
    font-size: 12px;
    color: rgba(255, 255, 255, 0.68);
    user-select: none;
  }

  .check input {
    width: 14px;
    height: 14px;
    accent-color: rgba(255, 255, 255, 0.9);
  }

  .sidebar__actions {
    padding: 10px 6px 6px;
  }

  .content {
    min-width: 0;
  }

  .topbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 14px;
    flex-wrap: wrap;
    margin-bottom: 14px;
  }

  .brandline__title {
    font-weight: 900;
    letter-spacing: 0.6px;
    color: rgba(255, 255, 255, 0.9);
    font-size: 12px;
  }

  .brandline__meta {
    margin-top: 4px;
    font-size: 12px;
    color: rgba(255, 255, 255, 0.55);
  }

  .topbar__actions {
    display: flex;
    gap: 10px;
    align-items: center;
    flex-wrap: wrap;
    justify-content: flex-end;
  }

  .error {
    color: var(--danger);
    font-size: 13px;
    margin: 10px 0;
  }

  .search {
    position: relative;
    display: inline-flex;
    align-items: center;
    width: min(360px, 100%);
    border-radius: 999px;
    border: 1px solid rgba(255, 255, 255, 0.12);
    background: rgba(0, 0, 0, 0.26);
    padding: 10px 12px;
    gap: 10px;
  }

  .search__icon {
    color: rgba(255, 255, 255, 0.6);
  }

  .search__input {
    width: 100%;
    border: 0;
    outline: none;
    background: transparent;
    color: rgba(255, 255, 255, 0.9);
    font-size: 14px;
  }

  .search__input::placeholder {
    color: rgba(255, 255, 255, 0.45);
  }

  .btn {
    appearance: none;
    border: 1px solid rgba(255, 255, 255, 0.12);
    background: rgba(255, 255, 255, 0.06);
    color: rgba(255, 255, 255, 0.88);
    border-radius: 12px;
    padding: 10px 12px;
    font-size: 13px;
    cursor: pointer;
  }

  .btn:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

  .btn--ghost {
    background: transparent;
  }

  .btn--full {
    width: 100%;
    justify-content: center;
  }

  .hero {
    border-radius: 18px;
    padding: 24px 22px;
    border: 1px solid rgba(255, 255, 255, 0.08);
    background: rgba(0, 0, 0, 0.12);
    backdrop-filter: blur(10px);
    box-shadow: rgba(0, 0, 0, 0.35) 0 22px 48px;
    margin-bottom: 18px;
  }

  .hero__title {
    margin: 0;
    font-size: 46px;
    line-height: 0.95;
    letter-spacing: 0.8px;
    font-weight: 950;
    color: rgba(255, 255, 255, 0.92);
  }

  .hero__text {
    margin-top: 10px;
    max-width: 56ch;
    font-size: 13px;
    color: rgba(255, 255, 255, 0.62);
  }

  .pill {
    display: inline-flex;
    align-items: center;
    padding: 3px 10px;
    border-radius: 999px;
    font-size: 12px;
    border: 1px solid var(--border);
    background: color-mix(in oklab, var(--text-strong) 4%, var(--panel));
    color: var(--text-strong);
  }

  .pill[data-active='true'] {
    border-color: color-mix(in oklab, var(--success) 60%, var(--border));
    background: color-mix(in oklab, var(--success) 12%, var(--panel));
  }

  .pill[data-active='false'] {
    border-color: color-mix(in oklab, var(--danger) 60%, var(--border));
    background: color-mix(in oklab, var(--danger) 10%, var(--panel));
  }

  .grid {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 18px;
  }

  .card {
    border-radius: 16px;
    border: 1px solid rgba(255, 255, 255, 0.08);
    background: rgba(0, 0, 0, 0.16);
    box-shadow: rgba(0, 0, 0, 0.35) 0 22px 48px;
    overflow: hidden;
    transition: transform 0.4s cubic-bezier(0.25, 1, 0.5, 1), box-shadow 0.4s ease, border-color 0.4s ease;
    animation: cardIn 0.6s cubic-bezier(0.22, 1, 0.36, 1) backwards;
  }

  .card:hover {
    transform: translateY(-6px);
    box-shadow: rgba(255, 0, 40, 0.14) 0 32px 55px, rgba(0, 0, 0, 0.45) 0 24px 48px;
    border-color: rgba(255, 0, 40, 0.32);
  }

  @keyframes cardIn {
    from { opacity: 0; transform: translateY(22px); }
    to { opacity: 1; transform: translateY(0); }
  }

  .card__media {
    width: 100%;
    border: 0;
    padding: 0;
    cursor: pointer;
    display: block;
    aspect-ratio: 1 / 1;
    position: relative;
    background: rgba(255, 255, 255, 0.04);
  }

  .card__img {
    width: 100%;
    height: 100%;
    object-fit: contain;
    padding: 18px;
    filter: drop-shadow(0 12px 24px rgba(0, 0, 0, 0.45));
    transition: transform 0.4s cubic-bezier(0.2, 0.8, 0.2, 1);
  }

  .card:hover .card__img {
    transform: scale(1.08) translateY(-4px) rotate(-4deg);
  }

  .mock {
    position: absolute;
    inset: 14% 10% 18%;
    border-radius: 18px;
    background: linear-gradient(135deg, rgba(255, 255, 255, 0.18), rgba(255, 255, 255, 0.04));
    transform: rotate(-10deg);
  }

  .badge {
    position: absolute;
    top: 10px;
    left: 10px;
    font-size: 10px;
    letter-spacing: 0.6px;
    font-weight: 900;
    padding: 4px 8px;
    border-radius: 999px;
    color: rgba(255, 255, 255, 0.95);
    background: rgba(0, 0, 0, 0.35);
    border: 1px solid rgba(255, 255, 255, 0.12);
    text-transform: uppercase;
  }

  .card__body {
    padding: 14px 14px 12px;
  }

  .card__name {
    font-weight: 900;
    letter-spacing: 0.3px;
    font-size: 13px;
    text-transform: uppercase;
    color: rgba(255, 255, 255, 0.92);
  }

  .card__meta {
    margin-top: 6px;
    display: inline-flex;
    align-items: center;
    gap: 8px;
    color: rgba(255, 255, 255, 0.62);
    font-size: 12px;
  }

  .dot {
    opacity: 0.35;
  }

  .card__price {
    margin-top: 8px;
    font-weight: 900;
    font-size: 13px;
    color: rgba(255, 255, 255, 0.9);
  }

  .card__actions {
    margin-top: 12px;
    display: flex;
    gap: 10px;
    align-items: center;
  }

  .cta {
    width: 100%;
    border: 0;
    border-radius: 10px;
    padding: 12px 12px;
    background: #ff0028;
    color: white;
    font-weight: 900;
    letter-spacing: 0.5px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
    cursor: pointer;
  }

  .cta:active {
    transform: translateY(1px);
  }

  .icon {
    width: 38px;
    height: 38px;
    border-radius: 10px;
    border: 1px solid rgba(255, 255, 255, 0.12);
    background: rgba(255, 255, 255, 0.06);
    color: rgba(255, 255, 255, 0.85);
    cursor: pointer;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-size: 14px;
  }

  .icon--danger {
    color: rgba(255, 135, 156, 0.95);
  }

  .status {
    margin-top: 12px;
  }

  .empty {
    padding: 26px 12px;
    text-align: center;
    color: rgba(255, 255, 255, 0.65);
    border: 1px dashed rgba(255, 255, 255, 0.18);
    border-radius: 16px;
  }

  .card--skeleton {
    background: rgba(255, 255, 255, 0.04);
  }

  .card--skeleton .card__media {
    background: rgba(255, 255, 255, 0.06);
    cursor: default;
  }

  .sk {
    height: 10px;
    border-radius: 999px;
    background: rgba(255, 255, 255, 0.08);
  }

  .sk--title {
    width: 68%;
    height: 12px;
  }

  .sk--meta {
    width: 54%;
    margin-top: 10px;
  }

  .sk--price {
    width: 36%;
    margin-top: 10px;
    height: 12px;
  }

  .sk--btn {
    width: 100%;
    margin-top: 12px;
    height: 38px;
    border-radius: 10px;
    background: rgba(255, 0, 40, 0.16);
  }

  .load {
    display: flex;
    justify-content: center;
    margin-top: 18px;
  }

  .load__btn {
    appearance: none;
    border: 1px solid rgba(255, 255, 255, 0.14);
    background: rgba(255, 255, 255, 0.06);
    color: rgba(255, 255, 255, 0.9);
    border-radius: 10px;
    padding: 12px 18px;
    font-size: 12px;
    font-weight: 900;
    letter-spacing: 0.5px;
    cursor: pointer;
  }

  .sheet {
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.35);
    display: grid;
    place-items: center;
    padding: 18px;
    z-index: 20;
  }

  .sheet__panel {
    width: min(640px, 100%);
    border-radius: 18px;
    border: 1px solid var(--border);
    background: var(--panel);
    box-shadow: var(--shadow);
    padding: 14px;
  }

  .sheet__header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 12px;
    margin-bottom: 10px;
  }

  .sheet__title {
    margin: 0;
    font-size: 16px;
    color: var(--text-strong);
  }

  @media (max-width: 980px) {
    .shell {
      grid-template-columns: 1fr;
    }

    .sidebar {
      position: static;
      top: auto;
    }

    .grid {
      grid-template-columns: repeat(2, minmax(0, 1fr));
    }

    .hero__title {
      font-size: 38px;
    }
  }

  @media (max-width: 640px) {
    .grid {
      grid-template-columns: 1fr;
    }

    .hero__title {
      font-size: 32px;
    }
  }
</style>
