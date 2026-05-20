<script>
  let { initial, onSave, onCancel, saving = false } = $props();

  let form = $state({
    nombre: '',
    precio: '',
    descripcion: '',
    categoria: 'Otros',
    plataforma: 'Nintendo',
    activo: true,
    imagen: null
  });

  let previewUrl = $state('');
  let fileInput;
  let error = $state('');

  $effect(() => {
    form = {
      nombre: initial?.nombre ?? '',
      precio: initial?.precio ?? '',
      descripcion: initial?.descripcion ?? '',
      categoria: initial?.categoria ?? 'Otros',
      plataforma: initial?.plataforma ?? 'Nintendo',
      activo: initial?.activo ?? true,
      imagen: null
    };
    previewUrl = initial?.imagen ? initial.imagen : '';
    error = '';
  });

  function handleFileChange(e) {
    const file = e.target.files[0];
    if (file) {
      if (!file.type.startsWith('image/')) {
        error = 'Por favor selecciona un archivo de imagen';
        return;
      }
      form.imagen = file;
      previewUrl = URL.createObjectURL(file);
      error = '';
    }
  }

  function validate() {
    if (!form.nombre.trim()) return 'El nombre es obligatorio';
    if (form.precio === '' || Number.isNaN(Number(form.precio))) return 'El precio debe ser un número';
    if (!form.descripcion.trim()) return 'La descripción es obligatoria';
    return '';
  }

  async function submit(e) {
    e.preventDefault();
    error = validate();
    if (error) return;

    const formData = new FormData();
    formData.append('nombre', form.nombre.trim());
    formData.append('precio', String(form.precio));
    formData.append('descripcion', form.descripcion.trim());
    formData.append('categoria', form.categoria);
    formData.append('plataforma', form.plataforma);
    formData.append('activo', String(form.activo));
    if (form.imagen) {
      formData.append('imagen', form.imagen);
    }

    await onSave?.(formData);
  }
</script>

<form class="form" onsubmit={submit}>
  <div class="form__grid">
    <label class="field">
      <span class="field__label">Nombre</span>
      <input class="input" bind:value={form.nombre} placeholder="Producto" disabled={saving} />
    </label>

    <label class="field">
      <span class="field__label">Precio</span>
      <input class="input" bind:value={form.precio} inputmode="decimal" placeholder="0.00" disabled={saving} />
    </label>

    <label class="field field--full">
      <span class="field__label">Descripción</span>
      <textarea class="textarea" bind:value={form.descripcion} rows="3" placeholder="Descripción" disabled={saving}></textarea>
    </label>

    <label class="field field--full">
      <span class="field__label">Categoría</span>
      <select class="input" bind:value={form.categoria} disabled={saving}>
        <option value="Consolas">Consolas</option>
        <option value="Videojuegos">Videojuegos</option>
        <option value="Accesorios">Accesorios</option>
        <option value="Otros">Otros</option>
      </select>
    </label>

    <label class="field field--full">
      <span class="field__label">Plataforma</span>
      <select class="input" bind:value={form.plataforma} disabled={saving}>
        <option value="Nintendo">Nintendo</option>
        <option value="Playstation">Playstation</option>
        <option value="Xbox">Xbox</option>
        <option value="Otro">Otro</option>
      </select>
    </label>

    <div class="field field--full">
      <span class="field__label">Imagen del Producto</span>
      <div class="image-upload">
        {#if previewUrl}
          <div class="preview">
            <img src={previewUrl} alt="Vista previa" />
            <button type="button" class="btn-remove" onclick={() => { form.imagen = null; previewUrl = ''; if(fileInput) fileInput.value = ''; }} disabled={saving}>×</button>
          </div>
        {/if}
        <input 
          type="file" 
          accept="image/*" 
          onchange={handleFileChange} 
          bind:this={fileInput}
          class="file-input"
          disabled={saving}
        />
      </div>
    </div>

    <label class="check field--full">
      <input type="checkbox" bind:checked={form.activo} disabled={saving} />
      <span>Activo</span>
    </label>
  </div>

  {#if error}
    <div class="error" role="alert">{error}</div>
  {/if}

  <div class="actions">
    <button class="btn btn--ghost" type="button" onclick={onCancel} disabled={saving}>Cancelar</button>
    <button class="btn btn--primary" type="submit" disabled={saving}>
      {saving ? 'Guardando…' : 'Guardar'}
    </button>
  </div>
</form>

<style>
  .form {
    display: grid;
    gap: 14px;
  }

  .form__grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;
  }

  .field {
    display: grid;
    gap: 6px;
  }

  .field--full {
    grid-column: 1 / -1;
  }

  .field__label {
    font-size: 12px;
    color: var(--text);
  }

  .input,
  .textarea {
    width: 100%;
    box-sizing: border-box;
    padding: 10px 12px;
    border-radius: 12px;
    border: 1px solid var(--border);
    background: var(--panel);
    color: var(--text-strong);
    font-size: 14px;
  }

  .textarea {
    resize: vertical;
  }

  .check {
    display: flex;
    gap: 10px;
    align-items: center;
    font-size: 14px;
    color: var(--text-strong);
  }

  .error {
    font-size: 13px;
    color: var(--danger);
  }

  .actions {
    display: flex;
    justify-content: flex-end;
    gap: 10px;
  }

  .image-upload {
    display: grid;
    gap: 10px;
  }

  .preview {
    position: relative;
    width: 100px;
    height: 100px;
    border-radius: 8px;
    overflow: hidden;
    border: 1px solid var(--border);
  }

  .preview img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }

  .btn-remove {
    position: absolute;
    top: 4px;
    right: 4px;
    width: 20px;
    height: 20px;
    border-radius: 50%;
    background: rgba(0,0,0,0.5);
    color: white;
    border: none;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 14px;
  }

  .file-input {
    font-size: 13px;
    color: var(--text);
  }

  .btn {
    appearance: none;
    border: 1px solid var(--border);
    background: var(--panel);
    color: var(--text-strong);
    border-radius: 12px;
    padding: 10px 12px;
    font-size: 14px;
    cursor: pointer;
  }

  .btn:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

  .btn--ghost {
    background: transparent;
  }

  .btn--primary {
    background: color-mix(in oklab, var(--accent) 18%, var(--panel));
    border-color: color-mix(in oklab, var(--accent) 55%, var(--border));
  }

  @media (max-width: 720px) {
    .form__grid {
      grid-template-columns: 1fr;
    }
  }
</style>
