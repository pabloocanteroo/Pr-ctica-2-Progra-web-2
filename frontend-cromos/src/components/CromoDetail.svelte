<script>
  import { imageUrl } from '../services/api.js';
  let { cromo, onClose } = $props();
  let precio = $derived(parseFloat(cromo.precio || 0).toFixed(2));
  let foto = $derived(imageUrl(cromo.imagen) || 'https://images.unsplash.com/photo-1613589417855-46747f43391b?auto=format&fit=crop&w=600&q=80');
  let isSold = $derived(cromo.estado_venta === 'vendido');
</script>

<!-- svelte-ignore a11y_click_events_have_key_events -->
<!-- svelte-ignore a11y_no_static_element_interactions -->
<div class="modal-overlay" onclick={onClose}>
  <div class="modal" onclick={(e) => e.stopPropagation()} role="dialog" aria-modal="true">
    <button class="close-btn" onclick={onClose}>✕</button>
    <div class="detail-img" style="background-image: url('{foto}')">
      {#if isSold}<div class="sold-ov"><span class="sold-stamp">VENDIDO</span></div>{/if}
    </div>
    <div class="detail-info">
      <h2>{cromo.nombre}</h2>
      <div class="price-row">
        <span class="price" class:sold-price={isSold}>{precio}€</span>
        <span class="status-badge" class:sold-badge={isSold}>{isSold ? 'Vendido' : 'Disponible'}</span>
      </div>
      <div class="meta">
        <div class="meta-item"><span class="label">Vendedor</span><span>{cromo.vendedor || 'Oficial'}</span></div>
        {#if cromo.comprador}<div class="meta-item"><span class="label">Comprador</span><span>{cromo.comprador}</span></div>{/if}
        {#if cromo.fecha_venta}<div class="meta-item"><span class="label">Fecha</span><span>{new Date(cromo.fecha_venta).toLocaleDateString('es-ES')}</span></div>{/if}
      </div>
      {#if cromo.descripcion}<div class="desc-block"><span class="label">Descripción</span><p>{cromo.descripcion}</p></div>{/if}
      {#if isSold}
        <div class="commission-box">
          <span>Comisión plataforma:</span><strong>{(parseFloat(cromo.precio) * 0.01).toFixed(2)}€</strong>
        </div>
      {/if}
    </div>
  </div>
</div>

<style>
  .modal-overlay { position: fixed; inset: 0; background: var(--bg-overlay); z-index: 200; display: flex; align-items: center; justify-content: center; padding: 1rem; animation: fadeIn 0.2s; }
  .modal { position: relative; max-width: 650px; width: 100%; max-height: 90vh; overflow-y: auto; background: white; border-radius: 16px; box-shadow: 0 20px 60px rgba(0,0,0,0.15); animation: scaleIn 0.25s; }
  .close-btn { position: absolute; top: 0.8rem; right: 0.8rem; z-index: 10; background: white; border: none; width: 32px; height: 32px; border-radius: 50%; font-size: 0.9rem; cursor: pointer; box-shadow: var(--shadow-sm); color: var(--text-secondary); }
  .detail-img { height: 280px; background-size: cover; background-position: center; position: relative; border-radius: 16px 16px 0 0; }
  .sold-ov { position: absolute; inset: 0; background: rgba(255,255,255,0.7); display: flex; align-items: center; justify-content: center; }
  .sold-stamp { font-size: 2rem; font-weight: 900; color: var(--danger); transform: rotate(-10deg); letter-spacing: 3px; border: 3px solid var(--danger); padding: 0.3rem 1rem; border-radius: 6px; }
  .detail-info { padding: 1.5rem; }
  .detail-info h2 { font-size: 1.5rem; margin-bottom: 0.5rem; }
  .price-row { display: flex; align-items: center; gap: 0.75rem; margin-bottom: 1.25rem; }
  .price { font-size: 1.8rem; font-weight: 800; color: var(--primary); font-family: 'Space Grotesk'; }
  .sold-price { text-decoration: line-through; color: var(--text-muted); }
  .status-badge { padding: 0.25rem 0.7rem; border-radius: 50px; font-size: 0.75rem; font-weight: 700; background: var(--accent-bg); color: var(--accent); }
  .sold-badge { background: var(--danger-bg); color: var(--danger); }
  .meta { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 0.75rem; margin-bottom: 1.25rem; }
  .meta-item { display: flex; flex-direction: column; gap: 0.15rem; }
  .label { font-size: 0.7rem; color: var(--text-muted); text-transform: uppercase; font-weight: 700; }
  .desc-block p { color: var(--text-secondary); line-height: 1.5; margin-top: 0.2rem; font-size: 0.9rem; }
  .commission-box { display: flex; justify-content: space-between; padding: 0.8rem 1rem; background: var(--accent-bg); border-radius: 10px; margin-top: 1rem; color: var(--accent); font-size: 0.9rem; }
  @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
  @keyframes scaleIn { from { opacity: 0; transform: scale(0.96); } to { opacity: 1; transform: scale(1); } }
  @media (max-width: 600px) { .meta { grid-template-columns: 1fr; } .detail-img { height: 200px; } }
</style>
