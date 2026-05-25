<script>
  import { auth, clearAuth } from '../store/auth.svelte.js';
  import { cart, getCartTotals, removeFromCart, clearCart } from '../store/cart.svelte.js';
  import { buyCromo } from '../services/api.js';
  import { success, error as showError } from '../store/toast.svelte.js';

  let { currentPage = '/', navigate, onPurchaseComplete = () => {} } = $props();
  let showCart = $state(false);
  let checkingOut = $state(false);
  let totals = $derived(getCartTotals());

  function handleLogout() {
    clearAuth();
    navigate('/login');
  }

  async function handleCheckout() {
    if (cart.items.length === 0 || checkingOut) return;
    if (!auth.user) { showError('Inicia sesión para comprar'); navigate('/login'); return; }
    checkingOut = true;
    try {
      for (const item of cart.items) await buyCromo(item._id, auth.user.username);
      success(`¡Compra realizada! ${totals.count} cromo(s) por ${totals.total}€`);
      clearCart();
      showCart = false;
      onPurchaseComplete();
    } catch (err) { showError('Error: ' + err.message); }
    finally { checkingOut = false; }
  }

  const links = [
    { path: '/', label: 'Mercado', icon: '🏪', showFor: 'all' },
    { path: '/publicar', label: 'Vender', icon: '📤', showFor: 'user' },
    { path: '/perfil', label: 'Perfil', icon: '👤', showFor: 'user' },
  ];
  
  let visibleLinks = $derived(links.filter(l => l.showFor === 'all' || (l.showFor === 'user' && auth.user?.role !== 'admin')));
</script>

<nav class="navbar">
  <button class="nav-brand" onclick={() => navigate('/')}>
    <span class="brand-dot"></span>
    <span class="brand-text">Cromos<strong>Market</strong></span>
  </button>

  <div class="nav-links">
    {#each visibleLinks as link}
      <button class="nav-link" class:active={currentPage === link.path} onclick={() => navigate(link.path)}>
        <span class="link-icon">{link.icon}</span> {link.label}
      </button>
    {/each}
    {#if auth.user?.role === 'admin'}
      <button class="nav-link" class:active={currentPage === '/admin'} onclick={() => navigate('/admin')}>
        <span class="link-icon">⚙️</span> Admin
      </button>
    {/if}
  </div>

  <div class="nav-actions">
    {#if auth.user?.role !== 'admin'}
      <button class="cart-btn" onclick={() => showCart = !showCart}>
        🛒
        {#if totals.count > 0}<span class="badge">{totals.count}</span>{/if}
      </button>
    {/if}
    {#if auth.user}
      <div class="user-pill">
        <span class="user-avatar">{auth.user.username[0].toUpperCase()}</span>
        <span class="user-name">{auth.user.username}</span>
      </div>
      <button class="btn btn-secondary btn-sm" onclick={handleLogout}>Salir</button>
    {:else}
      <button class="btn btn-primary btn-sm" onclick={() => navigate('/login')}>Entrar</button>
    {/if}
  </div>
</nav>

{#if showCart}
  <!-- svelte-ignore a11y_click_events_have_key_events -->
  <!-- svelte-ignore a11y_no_static_element_interactions -->
  <div class="cart-overlay" onclick={() => showCart = false}></div>
  <aside class="cart-panel">
    <h3>Tu carrito</h3>
    {#if cart.items.length === 0}
      <p class="empty-msg">Aún no has añadido cromos.</p>
    {:else}
      <ul class="cart-list">
        {#each cart.items as item (item._id)}
          <li>
            <span class="item-name">{item.nombre}</span>
            <span class="item-price">{parseFloat(item.precio).toFixed(2)}€</span>
            <button class="remove-btn" onclick={() => removeFromCart(item._id)}>✕</button>
          </li>
        {/each}
      </ul>
      <div class="cart-summary">
        <div class="row"><span>Subtotal</span><span>{totals.subtotal}€</span></div>
        <div class="row fee"><span>Comisión plataforma (1%)</span><span>+{totals.fee}€</span></div>
        <hr />
        <div class="row total"><span>Total</span><span>{totals.total}€</span></div>
      </div>
      <button class="btn btn-primary w-full" onclick={handleCheckout} disabled={checkingOut || !auth.user}>
        {checkingOut ? 'Procesando...' : `💳 Pagar ${totals.total}€`}
      </button>
    {/if}
  </aside>
{/if}

<style>
  .navbar {
    display: flex; align-items: center; justify-content: space-between;
    padding: 0.6rem 1.5rem; position: sticky; top: 0; z-index: 50;
    background: var(--bg-nav); backdrop-filter: blur(12px);
    border-bottom: 1px solid var(--border); margin-bottom: 1.5rem;
  }
  .nav-brand { display: flex; align-items: center; gap: 0.6rem; background: none; border: none; cursor: pointer; color: var(--text); }
  .brand-dot { width: 10px; height: 10px; border-radius: 50%; background: var(--primary); }
  .brand-text { font-family: 'Space Grotesk', sans-serif; font-size: 1.2rem; font-weight: 400; }
  .brand-text strong { font-weight: 800; color: var(--primary); }
  .nav-links { display: flex; gap: 0.2rem; }
  .nav-link {
    background: none; border: none; color: var(--text-secondary);
    font-family: 'Inter', sans-serif; font-weight: 600; font-size: 0.85rem;
    padding: 0.5rem 0.9rem; border-radius: 8px; cursor: pointer; transition: var(--transition);
  }
  .nav-link:hover { color: var(--text); background: var(--primary-bg); }
  .nav-link.active { color: var(--primary); background: var(--primary-bg); }
  .link-icon { font-size: 0.9rem; }
  .nav-actions { display: flex; align-items: center; gap: 0.75rem; }
  .cart-btn {
    position: relative; background: var(--bg); border: 1.5px solid var(--border);
    font-size: 1.1rem; padding: 0.4rem 0.65rem; border-radius: 10px;
    cursor: pointer; transition: var(--transition);
  }
  .cart-btn:hover { border-color: var(--primary); }
  .badge {
    position: absolute; top: -5px; right: -5px;
    background: var(--primary); color: white; font-size: 0.65rem;
    width: 17px; height: 17px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-weight: 800; font-family: 'Inter', sans-serif;
  }
  .user-pill { display: flex; align-items: center; gap: 0.4rem; }
  .user-avatar {
    width: 28px; height: 28px; border-radius: 50%;
    background: linear-gradient(135deg, var(--primary), var(--accent));
    display: flex; align-items: center; justify-content: center;
    font-size: 0.7rem; font-weight: 800; color: white;
  }
  .user-name { font-weight: 600; font-size: 0.85rem; color: var(--text); }
  .btn-sm { padding: 0.4rem 0.9rem; font-size: 0.8rem; }
  .cart-overlay { position: fixed; inset: 0; background: var(--bg-overlay); z-index: 90; }
  .cart-panel {
    position: fixed; top: 0; right: 0; bottom: 0; width: 380px; max-width: 90vw;
    background: white; padding: 2rem 1.5rem; z-index: 100;
    box-shadow: -10px 0 40px rgba(0,0,0,0.1);
    animation: slideRight 0.25s ease; display: flex; flex-direction: column; gap: 1rem;
  }
  .cart-panel h3 { font-size: 1.2rem; border-bottom: 1px solid var(--border); padding-bottom: 0.75rem; }
  .empty-msg { color: var(--text-muted); text-align: center; padding: 3rem 0; }
  .cart-list { list-style: none; display: flex; flex-direction: column; gap: 0.3rem; }
  .cart-list li { display: flex; align-items: center; gap: 0.75rem; padding: 0.6rem 0; border-bottom: 1px solid var(--border); }
  .item-name { flex: 1; font-weight: 600; font-size: 0.9rem; }
  .item-price { color: var(--primary); font-weight: 700; }
  .remove-btn { background: none; border: none; color: var(--danger); cursor: pointer; font-size: 0.85rem; }
  .cart-summary { margin-top: auto; }
  .row { display: flex; justify-content: space-between; padding: 0.25rem 0; color: var(--text-secondary); font-size: 0.9rem; }
  .fee { color: var(--danger); font-size: 0.8rem; }
  hr { border: 0; border-top: 1px solid var(--border); margin: 0.4rem 0; }
  .total { font-size: 1.1rem; font-weight: 800; color: var(--text); }
  .w-full { width: 100%; margin-top: 0.75rem; }
  @keyframes slideRight { from { transform: translateX(100%); } to { transform: translateX(0); } }
  @media (max-width: 768px) { .nav-links { display: none; } }
</style>
