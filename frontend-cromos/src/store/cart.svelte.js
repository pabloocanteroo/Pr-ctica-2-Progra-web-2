// Store del carrito — al hacer checkout se llama a la API para marcar cada cromo como vendido

export const cart = $state({
  items: []
});

export function addToCart(cromo) {
  // No añadir si ya vendido
  if (cromo.estado_venta === 'vendido') return false;
  // No añadir duplicados
  if (cart.items.find(i => i._id === cromo._id)) return false;
  cart.items.push({ ...cromo });
  return true;
}

export function removeFromCart(id) {
  const idx = cart.items.findIndex(i => i._id === id);
  if (idx !== -1) cart.items.splice(idx, 1);
}

export function clearCart() {
  cart.items = [];
}

export function getCartTotals() {
  const subtotal = cart.items.reduce((s, i) => s + (parseFloat(i.precio) || 0), 0);
  const fee = subtotal * 0.01;
  const total = subtotal + fee;
  return {
    count: cart.items.length,
    subtotal: subtotal.toFixed(2),
    fee: fee.toFixed(2),
    total: total.toFixed(2)
  };
}
