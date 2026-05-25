// Store global de notificaciones toast con Svelte 5 Runes
export const toasts = $state({ list: [] });

let nextId = 0;

export function addToast(message, type = 'info', duration = 3500) {
  const id = nextId++;
  toasts.list.push({ id, message, type });
  setTimeout(() => {
    const idx = toasts.list.findIndex(t => t.id === id);
    if (idx !== -1) toasts.list.splice(idx, 1);
  }, duration);
}

export function success(msg) { addToast(msg, 'success'); }
export function error(msg)   { addToast(msg, 'error'); }
export function info(msg)    { addToast(msg, 'info'); }
