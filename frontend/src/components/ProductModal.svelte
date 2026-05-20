<script>
  let { product, onClose } = $props();
</script>

{#if product}
  <div
    class="backdrop"
    role="presentation"
    onclick={(e) => e.currentTarget === e.target && onClose?.()}
  >
    <div class="modal" role="dialog" aria-modal="true" tabindex="0" onkeydown={(e) => e.key === 'Escape' && onClose?.()}>
      <div class="modal__header">
        <h2 class="modal__title">{product.nombre}</h2>
        <button class="icon-btn" type="button" onclick={onClose} aria-label="Cerrar">×</button>
      </div>

      <div class="modal__body">
        {#if product.imagen}
          <div class="modal__image">
            <img src={product.imagen.startsWith('http') ? product.imagen : `http://localhost:3000${product.imagen}`} alt={product.nombre} />
          </div>
        {/if}
        <div class="row">
          <span class="label">Precio</span>
          <span class="value">${product.precio}</span>
        </div>
        <div class="row">
          <span class="label">Estado</span>
          <span class="value">
            <span class="pill" data-active={product.activo !== false ? 'true' : 'false'}>
              {product.activo !== false ? 'Activo' : 'No activo'}
            </span>
          </span>
        </div>
        <div class="row row--stack">
          <span class="label">Descripción</span>
          <p class="value value--wrap">{product.descripcion}</p>
        </div>
      </div>

      <div class="modal__footer">
        <button class="btn" type="button" onclick={onClose}>Cerrar</button>
      </div>
    </div>
  </div>
{/if}

<style>
  .backdrop {
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.45);
    display: grid;
    place-items: center;
    padding: 18px;
    z-index: 20;
  }

  .modal {
    width: min(560px, 100%);
    border-radius: 16px;
    border: 1px solid var(--border);
    background: var(--panel);
    box-shadow: var(--shadow);
    overflow: hidden;
  }

  .modal__header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 14px 16px;
    border-bottom: 1px solid var(--border);
  }

  .modal__title {
    margin: 0;
    font-size: 18px;
    color: var(--text-strong);
  }

  .icon-btn {
    appearance: none;
    border: 0;
    background: transparent;
    color: var(--text);
    font-size: 22px;
    cursor: pointer;
    padding: 2px 8px;
  }

  .modal__body {
    padding: 16px;
    display: grid;
    gap: 14px;
  }

  .modal__image {
    width: 100%;
    aspect-ratio: 16 / 9;
    background: rgba(255, 255, 255, 0.03);
    border-radius: 12px;
    overflow: hidden;
    margin-bottom: 8px;
  }

  .modal__image img {
    width: 100%;
    height: 100%;
    object-fit: contain;
    padding: 12px;
  }

  .row {
    display: grid;
    grid-template-columns: 120px 1fr;
    gap: 12px;
    align-items: start;
  }

  .row--stack {
    grid-template-columns: 1fr;
  }

  .label {
    font-size: 12px;
    color: var(--text);
  }

  .value {
    font-size: 14px;
    color: var(--text-strong);
  }

  .value--wrap {
    margin: 0;
    white-space: pre-wrap;
    word-break: break-word;
  }

  .pill {
    display: inline-flex;
    align-items: center;
    padding: 3px 10px;
    border-radius: 999px;
    font-size: 12px;
    border: 1px solid var(--border);
    background: color-mix(in oklab, var(--text-strong) 4%, var(--panel));
  }

  .pill[data-active='true'] {
    border-color: color-mix(in oklab, var(--success) 60%, var(--border));
    background: color-mix(in oklab, var(--success) 12%, var(--panel));
  }

  .pill[data-active='false'] {
    border-color: color-mix(in oklab, var(--danger) 60%, var(--border));
    background: color-mix(in oklab, var(--danger) 10%, var(--panel));
  }

  .modal__footer {
    padding: 14px 16px;
    border-top: 1px solid var(--border);
    display: flex;
    justify-content: flex-end;
  }

  .btn {
    appearance: none;
    border: 1px solid var(--border);
    background: transparent;
    color: var(--text-strong);
    border-radius: 12px;
    padding: 10px 12px;
    font-size: 14px;
    cursor: pointer;
  }
</style>
