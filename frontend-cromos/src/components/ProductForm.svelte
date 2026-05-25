<script>
  import { auth } from '../store/auth.svelte.js';
  import { publishCromo, updateCromo } from '../services/api.js';
  import { success, error as showError } from '../store/toast.svelte.js';

  // $props + callbacks — comunicación hijo→padre
  let { cromo = null, onSave, onCancel } = $props();

  // Si cromo viene definido => modo edición; si no => modo creación
  let isEdit = $derived(!!cromo);

  let initName = cromo?.nombre || '';
  let initPrice = cromo?.precio?.toString() || '';
  let initDesc = cromo?.descripcion || '';

  let nombre = $state(initName);
  let precio = $state(initPrice);
  let descripcion = $state(initDesc);
  let imageFile = $state(null);
  let imagePreview = $state(null);
  let saving = $state(false);

  // Validaciones reactivas con $derived
  let errors = $derived.by(() => {
    const e = {};
    if (!nombre.trim()) e.nombre = 'El nombre es obligatorio';
    else if (nombre.trim().length < 2) e.nombre = 'Mínimo 2 caracteres';
    if (!precio || parseFloat(precio) <= 0) e.precio = 'El precio debe ser mayor que 0';
    else if (parseFloat(precio) > 99999) e.precio = 'Precio demasiado alto';
    return e;
  });
  let formValid = $derived(Object.keys(errors).length === 0);

  function handleFileChange(e) {
    const file = e.target.files?.[0];
    if (file) {
      if (file.size > 5 * 1024 * 1024) {
        showError('La imagen no puede superar los 5MB');
        return;
      }
      imageFile = file;
      const reader = new FileReader();
      reader.onload = (ev) => { imagePreview = ev.target.result; };
      reader.readAsDataURL(file);
    }
  }

  async function handleSubmit(e) {
    e.preventDefault();
    if (!formValid || saving) return;
    saving = true;

    try {
      let result;
      if (isEdit) {
        // Modo edición: PUT con JSON
        result = await updateCromo(cromo._id, {
          nombre: nombre.trim(),
          precio: parseFloat(precio),
          descripcion: descripcion.trim()
        });
        success(`"${nombre}" actualizado con éxito ✏️`);
      } else {
        // Modo creación: POST con FormData (multer)
        const fd = new FormData();
        fd.append('nombre', nombre.trim());
        fd.append('precio', parseFloat(precio));
        fd.append('vendedor', auth.user.username);
        fd.append('descripcion', descripcion.trim());
        if (imageFile) fd.append('imagen', imageFile);
        result = await publishCromo(fd);
        success(`"${nombre}" publicado con éxito 🎉`);
      }
      onSave(result);
    } catch (err) {
      showError(err.message);
    } finally {
      saving = false;
    }
  }
</script>

<form class="product-form glass-panel" onsubmit={handleSubmit}>
  <h3>{isEdit ? '✏️ Editar cromo' : '📤 Publicar cromo'}</h3>

  <!-- Zona de imagen (solo en modo creación) -->
  {#if !isEdit}
    <!-- svelte-ignore a11y_click_events_have_key_events -->
    <!-- svelte-ignore a11y_no_static_element_interactions -->
    <div class="image-upload" role="button" tabindex="0" onclick={() => document.getElementById('form-file').click()} onkeydown={(e) => e.key === 'Enter' && document.getElementById('form-file').click()}>
      {#if imagePreview}
        <img src={imagePreview} alt="Preview" />
      {:else}
        <div class="placeholder">
          <span>📷</span>
          <p>Click para subir foto</p>
          <small>Máx. 5MB</small>
        </div>
      {/if}
      <input id="form-file" type="file" accept="image/*" onchange={handleFileChange} hidden />
    </div>
  {/if}

  <!-- Campos -->
  <div class="fields">
    <div class="field" class:field-error={errors.nombre}>
      <label for="pf-name">Nombre del cromo *</label>
      <input id="pf-name" class="input-glass" bind:value={nombre} placeholder="Ej: Messi Topps Gold 2024" />
      {#if errors.nombre}<span class="error-msg">{errors.nombre}</span>{/if}
    </div>

    <div class="field" class:field-error={errors.precio}>
      <label for="pf-price">Precio (€) *</label>
      <input id="pf-price" class="input-glass" type="number" step="0.01" min="0.01" bind:value={precio} placeholder="15.00" />
      {#if errors.precio}<span class="error-msg">{errors.precio}</span>{/if}
    </div>

    <div class="field">
      <label for="pf-desc">Descripción</label>
      <textarea id="pf-desc" class="input-glass" rows="3" bind:value={descripcion} placeholder="Estado del cromo, edición especial, rarezas..."></textarea>
    </div>

    <div class="form-actions">
      <button type="submit" class="btn btn-primary flex-1" disabled={!formValid || saving}>
        {saving ? 'Guardando...' : (isEdit ? '💾 Guardar cambios' : '📤 Publicar')}
      </button>
      {#if onCancel}
        <button type="button" class="btn btn-secondary" onclick={onCancel}>Cancelar</button>
      {/if}
    </div>
  </div>
</form>

<style>
  .product-form { padding: 2rem; display: flex; gap: 2rem; flex-wrap: wrap; }
  .product-form h3 { width: 100%; margin: 0; font-size: 1.4rem; }
  .image-upload {
    width: 200px; height: 260px; border-radius: 12px; overflow: hidden;
    border: 2px dashed rgba(255,255,255,0.15); cursor: pointer;
    display: flex; align-items: center; justify-content: center;
    transition: var(--transition); flex-shrink: 0;
  }
  .image-upload:hover { border-color: var(--primary); }
  .image-upload img { width: 100%; height: 100%; object-fit: cover; }
  .placeholder { text-align: center; color: var(--text-muted); }
  .placeholder span { font-size: 2.5rem; }
  .placeholder small { font-size: 0.7rem; }
  .fields { flex: 1; display: flex; flex-direction: column; gap: 1rem; min-width: 250px; }
  .field { display: flex; flex-direction: column; gap: 0.3rem; }
  .field label { font-size: 0.8rem; color: var(--text-muted); font-weight: 700; text-transform: uppercase; }
  .field-error input, .field-error textarea { border-color: #ff3b30; }
  .error-msg { font-size: 0.75rem; color: #ff3b30; font-weight: 600; }
  textarea.input-glass { resize: vertical; }
  .form-actions { display: flex; gap: 0.75rem; margin-top: 0.5rem; }
  .flex-1 { flex: 1; }
  @media (max-width: 600px) { .product-form { flex-direction: column; align-items: center; } .image-upload { width: 100%; height: 180px; } }
</style>
