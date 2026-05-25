<script>
  import './app.css';
  import Navbar from './components/Navbar.svelte';
  import Toast from './components/Toast.svelte';
  import Home from './pages/Home.svelte';
  import Login from './pages/Login.svelte';
  import Publish from './pages/Publish.svelte';
  import Profile from './pages/Profile.svelte';
  import Admin from './pages/Admin.svelte';
  import { auth, initAuth } from './store/auth.svelte.js';

  // Router SPA basado en hash
  let path = $state(window.location.hash.slice(1) || '/');
  let refreshKey = $state(0); // Para forzar recarga tras compra

  $effect(() => {
    initAuth();
    function onHash() { path = window.location.hash.slice(1) || '/'; }
    window.addEventListener('hashchange', onHash);
    return () => window.removeEventListener('hashchange', onHash);
  });

  function navigate(to) { window.location.hash = to; }

  // Cuando se completa una compra, forzar recarga del mercado
  function handlePurchaseComplete() {
    refreshKey++;
  }
</script>

<Toast />

{#if auth.ready}
  <Navbar currentPage={path} {navigate} onPurchaseComplete={handlePurchaseComplete} />

  <main class="container">
    {#key refreshKey}
      {#if path === '/login'}
        <Login {navigate} />
      {:else if path === '/publicar'}
        <Publish {navigate} />
      {:else if path === '/perfil'}
        <Profile {navigate} />
      {:else if path === '/admin'}
        <Admin {navigate} />
      {:else}
        <Home {navigate} />
      {/if}
    {/key}
  </main>
{/if}

<style>
  main { padding-bottom: 3rem; }
</style>
