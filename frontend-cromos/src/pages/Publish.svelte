<script>
  import { auth } from '../store/auth.svelte.js';
  import ProductForm from '../components/ProductForm.svelte';
  import { error as showError } from '../store/toast.svelte.js';

  let { navigate } = $props();

  $effect(() => {
    if (auth.ready) {
      if (!auth.user) { showError('Inicia sesión para vender'); navigate('/login'); }
      else if (auth.user.role === 'admin') { showError('Los administradores no pueden vender cromos'); navigate('/'); }
    }
  });

  function handleSave() { navigate('/'); }
  function handleCancel() { navigate('/'); }
</script>

<section class="publish">
  <h2>Publicar un Cromo</h2>
  <p class="text-muted">Sube tu cromo al marketplace. La plataforma cobra un 1% de comisión al comprador.</p>
  {#if auth.user}
    <ProductForm onSave={handleSave} onCancel={handleCancel} />
  {/if}
</section>

<style>
  .publish { max-width: 650px; margin: 0 auto; }
  .publish h2 { font-size: 1.8rem; margin-bottom: 0.3rem; }
</style>
