<script>
  import { imageUrl } from '../services/api.js';
  let { cromo, onBuy, onDelete, onDetail, showDelete = false, isOwner = false, isAdmin = false } = $props();
  let precio = $derived(parseFloat(cromo.precio || 0).toFixed(2));
  let foto = $derived(imageUrl(cromo.imagen) || 'https://images.unsplash.com/photo-1613589417855-46747f43391b?auto=format&fit=crop&w=400&q=80');
  let isSold = $derived(cromo.estado_venta === 'vendido');
</script>

<article class="card" class:sold={isSold}>
  <!-- svelte-ignore a11y_click_events_have_key_events -->
  <!-- svelte-ignore a11y_no_static_element_interactions -->
  <div class="card-img" onclick={() => onDetail && onDetail(cromo)} style="background-image: url('{foto}')">
    <span class="seller-chip">{cromo.vendedor || 'Oficial'}</span>
    {#if isSold}
      <div class="sold-overlay">
        <span class="sold-stamp">VENDIDO</span>
        {#if cromo.comprador}<span class="buyer-info">→ {cromo.comprador}</span>{/if}
      </div>
    {/if}
  </div>

  <div class="card-body">
    <div class="card-top">
      <h3>{cromo.nombre}</h3>
      <span class="price" class:sold-price={isSold}>{precio}€</span>
    </div>
    {#if cromo.descripcion}<p class="desc">{cromo.descripcion}</p>{/if}
    <div class="card-actions">
      {#if isSold}
        <button class="btn btn-sold flex-1" disabled>Vendido ✓</button>
      {:else if isOwner}
        <span class="own-chip">Tu cromo</span>
        {#if showDelete}
          <button class="btn btn-danger btn-sm" onclick={() => onDelete(cromo._id)}>🗑</button>
        {/if}
      {:else if isAdmin}
        <button class="btn btn-secondary flex-1" disabled>Solo usuarios</button>
      {:else}
        <button class="btn btn-primary flex-1" onclick={() => onBuy(cromo)}>🛒 Comprar</button>
      {/if}
    </div>
  </div>
</article>

<style>
  .card {
    background: white; border-radius: var(--radius); overflow: hidden;
    border: 1px solid var(--border); transition: var(--transition);
    display: flex; flex-direction: column;
  }
  .card:hover { box-shadow: var(--shadow-hover); transform: translateY(-4px); }
  .card.sold { opacity: 0.65; }
  .card.sold:hover { transform: none; box-shadow: var(--shadow-sm); }
  .card-img { height: 200px; background-size: cover; background-position: center; position: relative; cursor: pointer; }
  .seller-chip {
    position: absolute; top: 0.6rem; left: 0.6rem;
    background: white; padding: 0.2rem 0.6rem; border-radius: 50px;
    font-size: 0.7rem; font-weight: 700; color: var(--primary);
    box-shadow: var(--shadow-sm);
  }
  .sold-overlay {
    position: absolute; inset: 0; background: rgba(255,255,255,0.8);
    display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 0.3rem;
  }
  .sold-stamp {
    font-size: 1.5rem; font-weight: 900; color: var(--danger);
    transform: rotate(-10deg); letter-spacing: 3px;
    border: 3px solid var(--danger); padding: 0.2rem 0.8rem; border-radius: 6px;
  }
  .buyer-info { font-size: 0.75rem; color: var(--text-secondary); }
  .card-body { padding: 1rem; display: flex; flex-direction: column; flex: 1; }
  .card-top { display: flex; justify-content: space-between; align-items: flex-start; gap: 0.5rem; margin-bottom: 0.4rem; }
  .card-top h3 { font-size: 1rem; font-weight: 700; }
  .price { font-family: 'Space Grotesk'; font-size: 1.1rem; font-weight: 800; color: var(--primary); white-space: nowrap; }
  .sold-price { text-decoration: line-through; color: var(--text-muted); }
  .desc { color: var(--text-secondary); font-size: 0.8rem; line-height: 1.4; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; margin-bottom: 0.75rem; }
  .card-actions { margin-top: auto; display: flex; gap: 0.5rem; align-items: center; }
  .flex-1 { flex: 1; }
  .own-chip { font-size: 0.75rem; color: var(--accent); font-weight: 700; flex: 1; background: var(--accent-bg); padding: 0.25rem 0.6rem; border-radius: 50px; }
  .btn-sold { background: var(--bg); color: var(--text-muted); border: 1px solid var(--border); cursor: default; }
</style>
