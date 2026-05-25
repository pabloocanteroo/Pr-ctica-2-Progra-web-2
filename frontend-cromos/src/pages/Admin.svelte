<script>
  import { auth } from '../store/auth.svelte.js';
  import { getUsers, createUser, updateUser, deleteUser, getCromos, deleteCromo } from '../services/api.js';
  import { success, error as showError } from '../store/toast.svelte.js';

  let { navigate } = $props();

  let users = $state([]);
  let cromos = $state([]);
  let loadingUsers = $state(true);
  let loadingCromos = $state(true);
  let activeTab = $state('users');

  // Formulario nuevo usuario
  let showCreateForm = $state(false);
  let newUsername = $state('');
  let newPassword = $state('');
  let newRole = $state('user');
  let creating = $state(false);

  // Edición de usuario
  let editingUser = $state(null);
  let editUsername = $state('');
  let editRole = $state('');
  let editPassword = $state('');
  let saving = $state(false);

  // Usuario seleccionado para ver perfil
  let selectedUser = $state(null);

  // $derived — datos cruzados
  let cromosVendidos = $derived(cromos.filter(c => c.estado_venta === 'vendido'));
  let volumenVentas = $derived(cromosVendidos.reduce((s, c) => s + (parseFloat(c.precio) || 0), 0));
  let gananciaAdmin = $derived((volumenVentas * 0.01).toFixed(2));

  // Stats por usuario
  let userStats = $derived.by(() => {
    return users.map(u => {
      const pubs = cromos.filter(c => c.vendedor === u.username);
      const sold = pubs.filter(c => c.estado_venta === 'vendido');
      const buys = cromos.filter(c => c.comprador === u.username);
      const income = sold.reduce((s, c) => s + (parseFloat(c.precio) || 0), 0);
      const spent = buys.reduce((s, c) => s + (parseFloat(c.precio) || 0) * 1.01, 0);
      return { ...u, pubs: pubs.length, sold: sold.length, onSale: pubs.length - sold.length, buys: buys.length, income: income.toFixed(2), spent: spent.toFixed(2), balance: (income - spent).toFixed(2), cromosPublicados: pubs, cromosComprados: buys };
    });
  });

  // Cromos del usuario seleccionado
  let selectedStats = $derived(selectedUser ? userStats.find(u => u._id === selectedUser._id) : null);

  // $effect
  $effect(() => {
    if (auth.ready && (!auth.user || auth.user.role !== 'admin')) {
      showError('Acceso restringido a administradores');
      navigate('/');
      return;
    }
    if (auth.user?.role === 'admin') {
      getUsers().then(d => { users = d; }).catch(e => showError(e.message)).finally(() => { loadingUsers = false; });
      getCromos().then(d => { cromos = d; }).catch(e => showError(e.message)).finally(() => { loadingCromos = false; });
    }
  });

  // CREATE
  async function handleCreate() {
    if (!newUsername.trim() || !newPassword.trim()) { showError('Rellena usuario y contraseña'); return; }
    creating = true;
    try {
      const res = await createUser({ username: newUsername.trim(), password: newPassword.trim(), role: newRole });
      users = [...users, res.user || res];
      success(`Usuario "${newUsername}" creado`);
      newUsername = ''; newPassword = ''; newRole = 'user'; showCreateForm = false;
    } catch (e) { showError(e.message); }
    finally { creating = false; }
  }

  // UPDATE
  function startEdit(user) {
    editingUser = user;
    editUsername = user.username;
    editRole = user.role;
    editPassword = '';
  }
  async function handleUpdate() {
    if (!editUsername.trim()) { showError('El nombre no puede estar vacío'); return; }
    saving = true;
    try {
      const data = { username: editUsername.trim(), role: editRole };
      if (editPassword.trim()) data.password = editPassword.trim();
      await updateUser(editingUser._id, data);
      // Actualizar localmente
      users = users.map(u => u._id === editingUser._id ? { ...u, username: editUsername.trim(), role: editRole } : u);
      success(`Usuario actualizado`);
      editingUser = null;
    } catch (e) { showError(e.message); }
    finally { saving = false; }
  }

  // DELETE
  async function handleDelete(id) {
    if (!confirm('¿Seguro? Se eliminará el usuario y no podrá iniciar sesión.')) return;
    try { await deleteUser(id); users = users.filter(u => u._id !== id); if (selectedUser?._id === id) selectedUser = null; success('Usuario eliminado'); } catch (e) { showError(e.message); }
  }

  // DELETE CROMO
  async function handleDeleteCromo(id) {
    if (!confirm('¿Eliminar este cromo?')) return;
    try { await deleteCromo(id); cromos = cromos.filter(c => c._id !== id); success('Cromo eliminado'); } catch (e) { showError(e.message); }
  }
</script>

<section class="admin">
  <div class="admin-header">
    <h2>Panel de Administración</h2>
    <p class="text-muted">CRUD de usuarios, gestión de ventas y comisiones</p>
  </div>

  <!-- KPIs -->
  <div class="kpi-row">
    <div class="kpi kpi-main">
      <span class="kpi-icon">💰</span>
      <div><span class="kpi-num">{gananciaAdmin}€</span><span class="kpi-label">Comisiones (1%)</span></div>
    </div>
    <div class="kpi">
      <span class="kpi-icon">📊</span>
      <div><span class="kpi-num">{volumenVentas.toFixed(2)}€</span><span class="kpi-label">Vol. vendido</span></div>
    </div>
    <div class="kpi">
      <span class="kpi-icon">✅</span>
      <div><span class="kpi-num">{cromosVendidos.length}</span><span class="kpi-label">Vendidos</span></div>
    </div>
    <div class="kpi">
      <span class="kpi-icon">🃏</span>
      <div><span class="kpi-num">{cromos.length}</span><span class="kpi-label">Total cromos</span></div>
    </div>
    <div class="kpi">
      <span class="kpi-icon">👥</span>
      <div><span class="kpi-num">{users.length}</span><span class="kpi-label">Usuarios</span></div>
    </div>
  </div>

  <!-- Tabs -->
  <div class="tabs">
    <button class="tab" class:active={activeTab === 'users'} onclick={() => { activeTab = 'users'; selectedUser = null; }}>👥 CRUD Usuarios</button>
    <button class="tab" class:active={activeTab === 'ventas'} onclick={() => activeTab = 'ventas'}>📊 Historial ventas</button>
    <button class="tab" class:active={activeTab === 'cromos'} onclick={() => activeTab = 'cromos'}>🃏 Cromos</button>
  </div>

  <!-- ══════ TAB: CRUD USUARIOS ══════ -->
  {#if activeTab === 'users'}
    <div class="section-bar">
      <h3>Gestión de usuarios</h3>
      <button class="btn btn-primary" onclick={() => showCreateForm = !showCreateForm}>
        {showCreateForm ? '✕ Cancelar' : '+ Crear usuario'}
      </button>
    </div>

    <!-- Formulario crear usuario -->
    {#if showCreateForm}
      <div class="form-card">
        <h4>Nuevo usuario</h4>
        <div class="form-row">
          <div class="field">
            <label for="new-user">Usuario</label>
            <input id="new-user" class="input-glass" bind:value={newUsername} placeholder="username" />
          </div>
          <div class="field">
            <label for="new-pass">Contraseña</label>
            <input id="new-pass" class="input-glass" type="password" bind:value={newPassword} placeholder="••••••" />
          </div>
          <div class="field">
            <label for="new-role">Rol</label>
            <select id="new-role" class="input-glass" bind:value={newRole}>
              <option value="user">user</option>
              <option value="admin">admin</option>
            </select>
          </div>
          <button class="btn btn-primary" onclick={handleCreate} disabled={creating}>
            {creating ? 'Creando...' : '✓ Crear'}
          </button>
        </div>
      </div>
    {/if}

    <!-- Modal editar usuario -->
    {#if editingUser}
      <!-- svelte-ignore a11y_click_events_have_key_events -->
      <!-- svelte-ignore a11y_no_static_element_interactions -->
      <div class="modal-overlay" onclick={() => editingUser = null}>
        <div class="modal-form" onclick={(e) => e.stopPropagation()}>
          <h4>Editar usuario: {editingUser.username}</h4>
          <div class="field">
            <label for="edit-user">Nombre</label>
            <input id="edit-user" class="input-glass" bind:value={editUsername} />
          </div>
          <div class="field">
            <label for="edit-role">Rol</label>
            <select id="edit-role" class="input-glass" bind:value={editRole}>
              <option value="user">user</option>
              <option value="admin">admin</option>
            </select>
          </div>
          <div class="field">
            <label for="edit-pass">Nueva contraseña (dejar vacía para no cambiar)</label>
            <input id="edit-pass" class="input-glass" type="password" bind:value={editPassword} placeholder="••••••" />
          </div>
          <div class="form-actions">
            <button class="btn btn-primary" onclick={handleUpdate} disabled={saving}>
              {saving ? 'Guardando...' : '💾 Guardar'}
            </button>
            <button class="btn btn-secondary" onclick={() => editingUser = null}>Cancelar</button>
          </div>
        </div>
      </div>
    {/if}

    <!-- Vista split: tabla + perfil detalle -->
    <div class="split-view">
      <!-- Lista usuarios -->
      <div class="users-list">
        {#if loadingUsers || loadingCromos}
          <div class="center"><div class="spinner"></div></div>
        {:else}
          {#each userStats as user (user._id)}
            <div class="user-row" class:selected={selectedUser?._id === user._id} >
              <!-- svelte-ignore a11y_click_events_have_key_events -->
              <!-- svelte-ignore a11y_no_static_element_interactions -->
              <div class="user-info" onclick={() => selectedUser = user}>
                <span class="avatar-sm">{user.username[0].toUpperCase()}</span>
                <div class="user-text">
                  <span class="uname">{user.username}</span>
                  <span class="urole" class:admin-role={user.role === 'admin'}>{user.role}</span>
                </div>
                <div class="user-quick-stats">
                  <span title="Publicados">📤 {user.pubs}</span>
                  <span title="Vendidos">✅ {user.sold}</span>
                  <span title="Compras">🛍 {user.buys}</span>
                </div>
              </div>
              <div class="user-actions">
                <button class="btn btn-secondary btn-xs" onclick={() => startEdit(user)}>✏️</button>
                <button class="btn btn-danger btn-xs" onclick={() => handleDelete(user._id)}>🗑</button>
              </div>
            </div>
          {/each}
        {/if}
      </div>

      <!-- Panel detalle de usuario seleccionado -->
      <div class="user-detail">
        {#if selectedStats}
          <div class="detail-header">
            <div class="avatar-lg">{selectedStats.username[0].toUpperCase()}</div>
            <div>
              <h3>{selectedStats.username}</h3>
              <span class="role-pill" class:admin-pill={selectedStats.role === 'admin'}>{selectedStats.role}</span>
            </div>
          </div>

          <div class="detail-stats">
            <div class="ds"><span class="ds-val">{selectedStats.pubs}</span><span class="ds-lbl">Publicados</span></div>
            <div class="ds"><span class="ds-val">{selectedStats.sold}</span><span class="ds-lbl">Vendidos</span></div>
            <div class="ds"><span class="ds-val">{selectedStats.onSale}</span><span class="ds-lbl">En venta</span></div>
            <div class="ds"><span class="ds-val">{selectedStats.buys}</span><span class="ds-lbl">Compras</span></div>
            <div class="ds"><span class="ds-val income">{selectedStats.income}€</span><span class="ds-lbl">Ingresos</span></div>
            <div class="ds"><span class="ds-val expense">{selectedStats.spent}€</span><span class="ds-lbl">Gastado</span></div>
            <div class="ds"><span class="ds-val" class:income={parseFloat(selectedStats.balance) >= 0} class:expense={parseFloat(selectedStats.balance) < 0}>{parseFloat(selectedStats.balance) >= 0 ? '+' : ''}{selectedStats.balance}€</span><span class="ds-lbl">Balance</span></div>
          </div>

          <!-- Cromos publicados por este usuario -->
          {#if selectedStats.cromosPublicados.length > 0}
            <h4 class="detail-section">📤 Cromos publicados</h4>
            <div class="mini-table">
              {#each selectedStats.cromosPublicados as c (c._id)}
                <div class="mini-row">
                  <span class="fw600">{c.nombre}</span>
                  <span class="price-tag">{parseFloat(c.precio).toFixed(2)}€</span>
                  <span class="status-chip" class:sold-chip={c.estado_venta === 'vendido'}>{c.estado_venta === 'vendido' ? '✓ Vendido' : '● Activo'}</span>
                </div>
              {/each}
            </div>
          {/if}

          <!-- Cromos comprados por este usuario -->
          {#if selectedStats.cromosComprados.length > 0}
            <h4 class="detail-section">🛍️ Compras realizadas</h4>
            <div class="mini-table">
              {#each selectedStats.cromosComprados as c (c._id)}
                <div class="mini-row">
                  <span class="fw600">{c.nombre}</span>
                  <span class="price-tag">{parseFloat(c.precio).toFixed(2)}€</span>
                  <span class="text-muted">de {c.vendedor}</span>
                </div>
              {/each}
            </div>
          {/if}

          <div class="detail-btns">
            <button class="btn btn-secondary" onclick={() => startEdit(selectedStats)}>✏️ Editar usuario</button>
            <button class="btn btn-danger" onclick={() => handleDelete(selectedStats._id)}>🗑 Eliminar</button>
          </div>
        {:else}
          <div class="empty-detail">
            <p style="font-size:2rem;">👈</p>
            <p class="text-muted">Selecciona un usuario para ver su perfil completo</p>
          </div>
        {/if}
      </div>
    </div>
  {/if}

  <!-- ══════ TAB: HISTORIAL VENTAS ══════ -->
  {#if activeTab === 'ventas'}
    {#if loadingCromos}
      <div class="center"><div class="spinner"></div></div>
    {:else if cromosVendidos.length === 0}
      <div class="center"><p class="text-muted">No hay ventas registradas.</p></div>
    {:else}
      <div class="table-card">
        <table>
          <thead><tr><th>Cromo</th><th>Precio</th><th>Vendedor</th><th>Comprador</th><th>Fecha</th><th>Comisión</th></tr></thead>
          <tbody>
            {#each cromosVendidos as c (c._id)}
              <tr>
                <td class="fw600">{c.nombre}</td>
                <td>{parseFloat(c.precio).toFixed(2)}€</td>
                <td>{c.vendedor}</td>
                <td>{c.comprador || '—'}</td>
                <td class="text-sm">{c.fecha_venta ? new Date(c.fecha_venta).toLocaleDateString('es-ES') : '—'}</td>
                <td class="commission">+{(parseFloat(c.precio) * 0.01).toFixed(2)}€</td>
              </tr>
            {/each}
          </tbody>
          <tfoot><tr><td colspan="5" class="totals-label">Total comisiones:</td><td class="commission fw800">{gananciaAdmin}€</td></tr></tfoot>
        </table>
      </div>
    {/if}
  {/if}

  <!-- ══════ TAB: CROMOS ══════ -->
  {#if activeTab === 'cromos'}
    {#if loadingCromos}
      <div class="center"><div class="spinner"></div></div>
    {:else}
      <div class="table-card">
        <table>
          <thead><tr><th>Nombre</th><th>Precio</th><th>Vendedor</th><th>Estado</th><th>Comprador</th><th>Acciones</th></tr></thead>
          <tbody>
            {#each cromos as cromo (cromo._id)}
              <tr>
                <td class="fw600">{cromo.nombre}</td>
                <td>{parseFloat(cromo.precio || 0).toFixed(2)}€</td>
                <td>{cromo.vendedor || '—'}</td>
                <td><span class="status-chip" class:sold-chip={cromo.estado_venta === 'vendido'}>{cromo.estado_venta === 'vendido' ? '✓ Vendido' : '● En venta'}</span></td>
                <td>{cromo.comprador || '—'}</td>
                <td><button class="btn btn-danger btn-xs" onclick={() => handleDeleteCromo(cromo._id)}>Eliminar</button></td>
              </tr>
            {/each}
          </tbody>
        </table>
      </div>
    {/if}
  {/if}
</section>

<style>
  .admin { max-width: 1200px; margin: 0 auto; }
  .admin-header h2 { font-size: 2rem; }
  .admin-header { margin-bottom: 1.5rem; }

  .kpi-row { display: grid; grid-template-columns: repeat(auto-fit, minmax(170px, 1fr)); gap: 0.75rem; margin-bottom: 2rem; }
  .kpi { display: flex; align-items: center; gap: 0.6rem; background: white; border-radius: var(--radius); padding: 1rem; border: 1px solid var(--border); box-shadow: var(--shadow-sm); }
  .kpi-main { border-color: rgba(0,184,148,0.3); }
  .kpi-main .kpi-num { color: var(--accent); }
  .kpi-icon { font-size: 1.3rem; }
  .kpi-num { display: block; font-size: 1.4rem; font-weight: 800; font-family: 'Space Grotesk'; }
  .kpi-label { font-size: 0.65rem; color: var(--text-muted); text-transform: uppercase; font-weight: 600; }

  .tabs { display: flex; gap: 0.3rem; margin-bottom: 1.25rem; border-bottom: 1px solid var(--border); padding-bottom: 0.5rem; }
  .tab { background: none; border: none; color: var(--text-secondary); font-family: 'Inter'; font-size: 0.9rem; font-weight: 600; padding: 0.5rem 1rem; border-radius: 8px; cursor: pointer; transition: var(--transition); }
  .tab:hover { color: var(--text); }
  .tab.active { background: var(--primary-bg); color: var(--primary); }

  .section-bar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; }
  .section-bar h3 { font-size: 1.1rem; margin: 0; }

  /* Formulario crear */
  .form-card { background: white; border: 1px solid var(--border); border-radius: var(--radius); padding: 1.25rem; margin-bottom: 1rem; box-shadow: var(--shadow-sm); }
  .form-card h4 { margin: 0 0 0.75rem; font-size: 0.95rem; }
  .form-row { display: flex; gap: 0.75rem; align-items: flex-end; flex-wrap: wrap; }
  .form-row .field { flex: 1; min-width: 140px; }
  .field { display: flex; flex-direction: column; gap: 0.2rem; }
  .field label { font-size: 0.7rem; color: var(--text-muted); font-weight: 700; text-transform: uppercase; }

  /* Modal editar  */
  .modal-overlay { position: fixed; inset: 0; background: var(--bg-overlay); z-index: 200; display: flex; align-items: center; justify-content: center; padding: 1rem; }
  .modal-form { background: white; border-radius: 16px; padding: 2rem; max-width: 400px; width: 100%; box-shadow: 0 20px 60px rgba(0,0,0,0.15); display: flex; flex-direction: column; gap: 1rem; animation: scaleIn 0.2s; }
  .modal-form h4 { margin: 0; }
  .form-actions { display: flex; gap: 0.5rem; }

  /* Split view */
  .split-view { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; min-height: 400px; }
  .users-list { background: white; border: 1px solid var(--border); border-radius: var(--radius); overflow-y: auto; max-height: 600px; }
  .user-row { display: flex; align-items: center; justify-content: space-between; padding: 0.65rem 1rem; border-bottom: 1px solid var(--border); transition: var(--transition); }
  .user-row:hover { background: var(--bg); }
  .user-row.selected { background: var(--primary-bg); border-left: 3px solid var(--primary); }
  .user-info { display: flex; align-items: center; gap: 0.6rem; flex: 1; cursor: pointer; }
  .avatar-sm { width: 30px; height: 30px; border-radius: 50%; background: linear-gradient(135deg, var(--primary), var(--accent)); display: flex; align-items: center; justify-content: center; font-size: 0.7rem; font-weight: 800; color: white; flex-shrink: 0; }
  .user-text { display: flex; flex-direction: column; }
  .uname { font-weight: 600; font-size: 0.9rem; }
  .urole { font-size: 0.7rem; color: var(--text-muted); }
  .admin-role { color: var(--primary); }
  .user-quick-stats { display: flex; gap: 0.5rem; font-size: 0.7rem; color: var(--text-secondary); margin-left: auto; margin-right: 0.5rem; }
  .user-actions { display: flex; gap: 0.3rem; }
  .btn-xs { padding: 0.25rem 0.5rem; font-size: 0.7rem; }

  /* Detalle usuario */
  .user-detail { background: white; border: 1px solid var(--border); border-radius: var(--radius); padding: 1.5rem; overflow-y: auto; max-height: 600px; }
  .detail-header { display: flex; align-items: center; gap: 1rem; margin-bottom: 1.25rem; }
  .avatar-lg { width: 52px; height: 52px; border-radius: 50%; background: linear-gradient(135deg, var(--primary), var(--accent)); display: flex; align-items: center; justify-content: center; font-size: 1.4rem; font-weight: 800; color: white; }
  .detail-header h3 { margin: 0; font-size: 1.3rem; }
  .role-pill { padding: 0.15rem 0.6rem; border-radius: 50px; font-size: 0.7rem; font-weight: 700; background: var(--bg); color: var(--text-secondary); }
  .admin-pill { background: var(--primary-bg); color: var(--primary); }

  .detail-stats { display: grid; grid-template-columns: repeat(auto-fill, minmax(80px, 1fr)); gap: 0.5rem; margin-bottom: 1.5rem; }
  .ds { text-align: center; background: var(--bg); border-radius: 8px; padding: 0.5rem 0.25rem; }
  .ds-val { display: block; font-size: 1.1rem; font-weight: 800; font-family: 'Space Grotesk'; }
  .ds-lbl { font-size: 0.6rem; color: var(--text-muted); text-transform: uppercase; font-weight: 600; }
  .income { color: var(--accent); }
  .expense { color: var(--danger); }

  .detail-section { font-size: 0.9rem; margin: 1rem 0 0.5rem; }
  .mini-table { display: flex; flex-direction: column; gap: 0.25rem; margin-bottom: 0.75rem; }
  .mini-row { display: flex; align-items: center; gap: 0.5rem; padding: 0.4rem 0.6rem; background: var(--bg); border-radius: 6px; font-size: 0.8rem; }
  .fw600 { font-weight: 600; }
  .price-tag { color: var(--primary); font-weight: 700; margin-left: auto; }
  .status-chip { font-size: 0.7rem; font-weight: 700; color: var(--accent); }
  .sold-chip { color: var(--danger); }
  .detail-btns { display: flex; gap: 0.5rem; margin-top: 1.5rem; border-top: 1px solid var(--border); padding-top: 1rem; }

  .empty-detail { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; text-align: center; }

  /* Tables */
  .table-card { background: white; border-radius: var(--radius); border: 1px solid var(--border); overflow-x: auto; box-shadow: var(--shadow-sm); }
  table { width: 100%; border-collapse: collapse; font-size: 0.85rem; }
  th { text-align: left; padding: 0.75rem 1rem; color: var(--text-muted); font-size: 0.7rem; text-transform: uppercase; font-weight: 700; border-bottom: 1px solid var(--border); background: var(--bg); }
  td { padding: 0.65rem 1rem; border-bottom: 1px solid var(--border); }
  tfoot td { border-bottom: none; background: var(--bg); }
  .totals-label { text-align: right; font-weight: 800; }
  .fw800 { font-weight: 800; }
  .text-sm { font-size: 0.8rem; color: var(--text-secondary); }
  .commission { color: var(--accent); font-weight: 700; }
  .center { display: flex; justify-content: center; padding: 3rem; }
  .spinner { width: 36px; height: 36px; border: 3px solid var(--border); border-left-color: var(--primary); border-radius: 50%; animation: spin 0.8s linear infinite; }
  @keyframes spin { to { transform: rotate(360deg); } }
  @keyframes scaleIn { from { opacity: 0; transform: scale(0.96); } to { opacity: 1; transform: scale(1); } }

  @media (max-width: 768px) {
    .split-view { grid-template-columns: 1fr; }
    .form-row { flex-direction: column; }
    .user-quick-stats { display: none; }
  }
</style>
