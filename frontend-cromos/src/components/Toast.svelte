<script>
  import { toasts } from '../store/toast.svelte.js';
</script>

{#if toasts.list.length > 0}
  <div class="toast-container">
    {#each toasts.list as toast (toast.id)}
      <div class="toast toast-{toast.type}">
        <span class="toast-icon">
          {#if toast.type === 'success'}✓
          {:else if toast.type === 'error'}✕
          {:else}ℹ
          {/if}
        </span>
        <span>{toast.message}</span>
      </div>
    {/each}
  </div>
{/if}

<style>
  .toast-container {
    position: fixed; top: 1rem; right: 1rem; z-index: 9999;
    display: flex; flex-direction: column; gap: 0.5rem; max-width: 380px;
  }
  .toast {
    padding: 0.85rem 1.2rem; border-radius: 10px;
    display: flex; align-items: center; gap: 0.6rem;
    font-weight: 600; font-size: 0.9rem;
    animation: toastIn 0.3s ease; box-shadow: var(--shadow-lg);
  }
  .toast-success { background: #D4EDDA; color: #155724; border: 1px solid #C3E6CB; }
  .toast-error { background: #F8D7DA; color: #721C24; border: 1px solid #F5C6CB; }
  .toast-info { background: #D1ECF1; color: #0C5460; border: 1px solid #BEE5EB; }
  .toast-icon { font-size: 1rem; }
  @keyframes toastIn { from { opacity: 0; transform: translateX(20px); } to { opacity: 1; transform: translateX(0); } }
</style>
