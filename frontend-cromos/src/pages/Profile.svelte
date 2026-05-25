<script>
  import { auth } from '../store/auth.svelte.js';
  import { getCromos, deleteCromo } from '../services/api.js';
  import CromoCard from '../components/CromoCard.svelte';
  import CromoDetail from '../components/CromoDetail.svelte';
  import ProductForm from '../components/ProductForm.svelte';
  import { addToCart } from '../store/cart.svelte.js';
  import { success, error as showError } from '../store/toast.svelte.js';

  let { navigate } = $props();
  let allCromos = $state([]);
  let loading = $state(true);
  let editingCromo = $state(null);
  let detailCromo = $state(null);

  let misCromosVenta = $derived(allCromos.filter(c => c.vendedor === auth.user?.username));
  let misCompras = $derived(allCromos.filter(c => c.comprador === auth.user?.username));
  let totalPublicados = $derived(misCromosVenta.length);
  let totalVendidos = $derived(misCromosVenta.filter(c => c.estado_venta === 'vendido').length);
  let ingresosBrutos = $derived(misCromosVenta.filter(c => c.estado_venta === 'vendido').reduce((s, c) => s + (parseFloat(c.precio) || 0), 0).toFixed(2));
  let totalCompras = $derived(misCompras.length);
  let gastoTotal = $derived(misCompras.reduce((s, c) => s + (parseFloat(c.precio) || 0) * 1.01, 0).toFixed(2));

  function loadData() {
    loading = true;
    getCromos().then(data => { allCromos = data; }).catch(err => showError(err.message)).finally(() => { loading = false; });
  }

  $effect(() => {
    if (auth.ready && !auth.user) { navigate('/login'); return; }
    if (auth.user) loadData();
  });

  async function handleDelete(id) {
    if (!confirm('¿Eliminar este cromo?')) return;
    try { await deleteCromo(id); allCromos = allCromos.filter(c => c._id !== id); success('Eliminado'); } catch (err) { showError(err.message); }
  }
  function handleEditSave() { editingCromo = null; loadData(); }
</script>

<section class="profile">
  {#if auth.user}
    <div class="header glass-panel">
      <div class="avatar">{auth.user.username[0].toUpperCase()}</div>
      <div class="info">
        <h2>{auth.user.username}</h2>
        <span class="role">{auth.user.role === 'admin' ? '👑 Admin' : '🃏 Coleccionista'}</span>
      </div>
      <div class="stats">
        <div class="stat"><span class="sv">{totalPublicados}</span><span class="sl">Publicados</span></div>
        <div class="stat"><span class="sv">{totalVendidos}</span><span class="sl">Vendidos</span></div>
        <div class="stat"><span class="sv green">{ingresosBrutos}€</span><span class="sl">Ingresos</span></div>
        <div class="stat"><span class="sv">{totalCompras}</span><span class="sl">Compras</span></div>
        <div class="stat"><span class="sv orange">{gastoTotal}€</span><span class="sl">Gastado</span></div>
      </div>
    </div>

    {#if editingCromo}
      <h3 class="stitle">✏️ Editando "{editingCromo.nombre}"</h3>
      <ProductForm cromo={editingCromo} onSave={handleEditSave} onCancel={() => editingCromo = null} />
    {/if}

    {#if misCompras.length > 0}
      <h3 class="stitle">🛍️ Mis compras ({totalCompras})</h3>
      <div class="grid">
        {#each misCompras as cromo (cromo._id)}<CromoCard {cromo} onBuy={() => {}} onDelete={() => {}} onDetail={(c) => detailCromo = c} />{/each}
      </div>
    {/if}

    <h3 class="stitle">📤 Mis publicaciones ({totalPublicados})</h3>
    {#if loading}
      <div class="center"><div class="spinner"></div></div>
    {:else if misCromosVenta.length === 0}
      <div class="center"><p class="text-muted">No has publicado cromos.</p><button class="btn btn-primary" onclick={() => navigate('/publicar')}>Publicar</button></div>
    {:else}
      <div class="grid">
        {#each misCromosVenta as cromo (cromo._id)}
          <div class="card-wrap">
            <CromoCard {cromo} onBuy={(c) => addToCart(c)} onDelete={handleDelete} onDetail={(c) => detailCromo = c} showDelete={cromo.estado_venta !== 'vendido'} isOwner={true} />
            {#if cromo.estado_venta !== 'vendido'}
              <button class="btn btn-secondary edit-btn" onclick={() => editingCromo = cromo}>✏️ Editar</button>
            {/if}
          </div>
        {/each}
      </div>
    {/if}
  {/if}
</section>

{#if detailCromo}<CromoDetail cromo={detailCromo} onClose={() => detailCromo = null} />{/if}

<style>
  .profile { max-width: 1000px; margin: 0 auto; }
  .header { display: flex; align-items: center; gap: 1.5rem; padding: 1.5rem; flex-wrap: wrap; }
  .avatar { width: 56px; height: 56px; border-radius: 50%; background: linear-gradient(135deg, var(--primary), var(--accent)); display: flex; align-items: center; justify-content: center; font-size: 1.6rem; font-weight: 800; color: white; flex-shrink: 0; }
  .info h2 { margin: 0; font-size: 1.3rem; }
  .role { font-size: 0.8rem; color: var(--text-secondary); }
  .stats { display: flex; gap: 1.25rem; flex-wrap: wrap; margin-left: auto; }
  .stat { text-align: center; }
  .sv { display: block; font-size: 1.2rem; font-weight: 800; color: var(--text); font-family: 'Space Grotesk'; }
  .sl { font-size: 0.65rem; color: var(--text-muted); text-transform: uppercase; font-weight: 600; }
  .green { color: var(--accent); }
  .orange { color: var(--danger); }
  .stitle { margin: 1.5rem 0 0.75rem; font-size: 1.15rem; }
  .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 1rem; margin-bottom: 1.5rem; }
  .card-wrap { display: flex; flex-direction: column; }
  .edit-btn { width: 100%; margin-top: 0.4rem; font-size: 0.8rem; padding: 0.35rem; }
  .center { display: flex; flex-direction: column; align-items: center; gap: 0.75rem; padding: 2rem; }
  .spinner { width: 36px; height: 36px; border: 3px solid var(--border); border-left-color: var(--primary); border-radius: 50%; animation: spin 0.8s linear infinite; }
  @keyframes spin { to { transform: rotate(360deg); } }
</style>
