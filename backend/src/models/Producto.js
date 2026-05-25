const mongoose = require('mongoose');

const productoSchema = new mongoose.Schema({
  nombre: String,
  precio: Number,
  vendedor: { type: String, default: 'Admin Oficial' },
  comprador: { type: String, default: null },
  descripcion: String,
  estado_venta: { type: String, default: 'disponible' },
  fecha_venta: { type: Date, default: null },
  imagen: String
});

module.exports = mongoose.model('Producto', productoSchema);
