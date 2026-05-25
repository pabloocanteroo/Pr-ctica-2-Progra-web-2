<script>
  import { getCromos } from '../services/api.js';
  import CromoCard from '../components/CromoCard.svelte';
  import CromoDetail from '../components/CromoDetail.svelte';
  import { addToCart } from '../store/cart.svelte.js';
  import { auth } from '../store/auth.svelte.js';
  import { success, error as showError } from '../store/toast.svelte.js';

  let { navigate } = $props();

  let cromos = $state([]);
  let loading = $state(true);
  let fetchError = $state(null);
  let search = $state('');
  let sortBy = $state('reciente');
  let showSold = $state(false);
  let selectedCromo = $state(null);

  let filtered = $derived.by(() => {
    let list = cromos;
    if (!showSold) list = list.filter(c => c.estado_venta !== 'vendido');
    if (search) {
      const q = search.toLowerCase();
      list = list.filter(c => c.nombre?.toLowerCase().includes(q) || c.vendedor?.toLowerCase().includes(q) || c.descripcion?.toLowerCase().includes(q));
    }
    if (sortBy === 'barato') list = [...list].sort((a, b) => a.precio - b.precio);
    else if (sortBy === 'caro') list = [...list].sort((a, b) => b.precio - a.precio);
    else list = [...list].reverse();
    return list;
  });

  let totalDisponibles = $derived(cromos.filter(c => c.estado_venta !== 'vendido').length);
  let totalVendidos = $derived(cromos.filter(c => c.estado_venta === 'vendido').length);

  export function reloadCromos() {
    loading = true;
    getCromos().then(data => { cromos = data; }).catch(err => { fetchError = err.message; }).finally(() => { loading = false; });
  }

  $effect(() => { reloadCromos(); });

  function handleBuy(cromo) {
    if (auth.user && cromo.vendedor === auth.user.username) { showError('No puedes comprar tu propio cromo'); return; }
    if (!auth.user) { showError('Inicia sesión para comprar'); navigate('/login'); return; }
    const added = addToCart(cromo);
    if (added) success(`"${cromo.nombre}" añadido al carrito`);
    else showError('Ya está en tu carrito');
  }
</script>

<section class="market">
  <div class="market-header">
    <h2>Mercado de Cromos</h2>
    <p class="text-muted">Colecciona, compra y vende cromos · Comisión plataforma: 1%</p>
  </div>

  <div class="toolbar">
    <input type="search" class="input-glass search" placeholder="🔍 Buscar nombre, vendedor..." bind:value={search} />
    <select class="input-glass sort" bind:value={sortBy}>
      <option value="reciente">Más recientes</option>
      <option value="barato">Precio ↑</option>
      <option value="caro">Precio ↓</option>
    </select>
    <label class="toggle">
      <input type="checkbox" bind:checked={showSold} />
      <span>Vendidos ({totalVendidos})</span>
    </label>
  </div>

  {#if !loading}
    <p class="count">{filtered.length} cromo{filtered.length !== 1 ? 's' : ''} · {totalDisponibles} disponible{totalDisponibles !== 1 ? 's' : ''}</p>
  {/if}

  {#if loading}
    <div class="center"><div class="spinner"></div><p class="text-muted">Cargando...</p></div>
  {:else if fetchError}
    <div class="center error-box"><p>⚠ {fetchError}</p></div>
  {:else if filtered.length === 0}
    <div class="center">
      <p style="font-size:2.5rem;">🃏</p>
      <p class="text-muted">No hay cromos{search ? ` para "${search}"` : ''}.</p>
      <button class="btn btn-primary" onclick={() => navigate('/publicar')}>Publicar uno</button>
    </div>
  {:else}
    <div class="grid">
      {#each filtered as cromo (cromo._id)}
        <CromoCard {cromo} onBuy={handleBuy} onDelete={() => {}} onDetail={(c) => selectedCromo = c} isOwner={auth.user?.username === cromo.vendedor} isAdmin={auth.user?.role === 'admin'} />
      {/each}
    </div>
  {/if}
</section>

{#if selectedCromo}
  <CromoDetail cromo={selectedCromo} onClose={() => selectedCromo = null} />
{/if}

<style>
  .market-header { text-align: center; margin-bottom: 1.5rem; }
  .market-header h2 { font-size: 2.2rem; }
  .toolbar { display: flex; gap: 0.75rem; margin-bottom: 1rem; flex-wrap: wrap; align-items: center; }
  .search { flex: 1; min-width: 200px; }
  .sort { width: 170px; cursor: pointer; }
  .toggle { display: flex; align-items: center; gap: 0.4rem; color: var(--text-secondary); font-size: 0.85rem; cursor: pointer; }
  .toggle input { accent-color: var(--primary); }
  .count { color: var(--text-muted); font-size: 0.8rem; margin-bottom: 1rem; }
  .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: 1.25rem; }
  .center { display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 35vh; text-align: center; gap: 0.75rem; }
  .error-box { color: var(--danger); background: var(--danger-bg); padding: 1.5rem; border-radius: var(--radius); }
  .spinner { width: 40px; height: 40px; border: 3px solid var(--border); border-left-color: var(--primary); border-radius: 50%; animation: spin 0.8s linear infinite; }
  @keyframes spin { to { transform: rotate(360deg); } }
</style>
