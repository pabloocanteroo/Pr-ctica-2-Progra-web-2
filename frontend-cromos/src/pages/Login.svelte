<script>
  import { login, register } from '../services/api.js';
  import { setAuth } from '../store/auth.svelte.js';
  import { success, error as showError } from '../store/toast.svelte.js';
  let { navigate } = $props();
  let username = $state('');
  let password = $state('');
  let errorMsg = $state('');
  let loading = $state(false);
  let isRegister = $state(false);

  async function handleSubmit(e) {
    e.preventDefault();
    if (!username.trim() || !password.trim()) { errorMsg = 'Rellena ambos campos'; return; }
    loading = true; errorMsg = '';
    try {
      if (isRegister) { await register(username, password); success('¡Cuenta creada!'); }
      const data = await login(username, password);
      const user = data.usuario || data.user || { username, role: 'user' };
      setAuth(user, data.token);
      success(`¡Bienvenido, ${user.username}!`);
      navigate('/');
    } catch (err) { errorMsg = err.message; showError(err.message); }
    finally { loading = false; }
  }
</script>

<div class="auth-wrap">
  <form class="auth-card" onsubmit={handleSubmit}>
    <div class="brand-header">
      <div class="brand-dot-lg"></div>
      <h2>{isRegister ? 'Crear cuenta' : 'Iniciar sesión'}</h2>
      <p class="text-muted">Accede al marketplace de cromos</p>
    </div>
    {#if errorMsg}<div class="error-alert">{errorMsg}</div>{/if}
    <div class="field">
      <label for="login-user">Usuario</label>
      <input id="login-user" type="text" class="input-glass" bind:value={username} required />
    </div>
    <div class="field">
      <label for="login-pass">Contraseña</label>
      <input id="login-pass" type="password" class="input-glass" bind:value={password} required />
    </div>
    <button type="submit" class="btn btn-primary w-full" disabled={loading}>
      {loading ? 'Cargando...' : (isRegister ? 'Registrarse' : 'Entrar')}
    </button>
    <div class="switch-row">
      <span class="text-muted">{isRegister ? '¿Ya tienes cuenta?' : '¿No tienes cuenta?'}</span>
      <button type="button" class="link-btn" onclick={() => { isRegister = !isRegister; errorMsg = ''; }}>
        {isRegister ? 'Inicia sesión' : 'Regístrate'}
      </button>
    </div>
  </form>
</div>

<style>
  .auth-wrap { display: flex; justify-content: center; align-items: center; min-height: 75vh; }
  .auth-card { width: 100%; max-width: 400px; padding: 2.5rem; display: flex; flex-direction: column; gap: 1rem; background: white; border-radius: var(--radius); box-shadow: var(--shadow-lg); }
  .brand-header { text-align: center; margin-bottom: 0.5rem; }
  .brand-dot-lg { width: 40px; height: 40px; border-radius: 50%; background: linear-gradient(135deg, var(--primary), var(--accent)); margin: 0 auto 1rem; }
  .field { display: flex; flex-direction: column; gap: 0.3rem; }
  .field label { font-size: 0.8rem; color: var(--text-secondary); font-weight: 700; text-transform: uppercase; }
  .error-alert { background: var(--danger-bg); border: 1px solid rgba(225,112,85,0.2); color: var(--danger); padding: 0.7rem; border-radius: 8px; text-align: center; font-weight: 600; font-size: 0.85rem; }
  .w-full { width: 100%; }
  .switch-row { text-align: center; border-top: 1px solid var(--border); padding-top: 1rem; }
  .link-btn { background: none; border: none; color: var(--primary); font-weight: 700; cursor: pointer; font-size: 0.9rem; margin-left: 0.2rem; }
  .link-btn:hover { text-decoration: underline; }
</style>
