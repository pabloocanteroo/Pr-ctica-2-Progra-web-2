const dotenv = require('dotenv');
const app = require('./src/app');
const connectDB = require('./src/config/db');
const client = require('./src/config/redis');

dotenv.config();

const User = require("./src/models/User");
const bcrypt = require("bcryptjs");

const Producto = require('./src/models/Producto');

async function seedDB() {
  try {
    // 1. Usuarios base
    const adminExists = await User.findOne({ username: 'admin' });
    if (!adminExists) {
      const adminPassword = await bcrypt.hash('admin123', 10);
      await User.create({ username: 'admin', password: adminPassword, role: 'admin' });
      console.log('✅ Usuario admin creado');
    } else if (adminExists.role !== 'admin') {
      adminExists.role = 'admin'; await adminExists.save();
    }

    const userExists = await User.findOne({ username: 'user' });
    if (!userExists) {
      const userPassword = await bcrypt.hash('user123', 10);
      await User.create({ username: 'user', password: userPassword, role: 'user' });
      console.log('✅ Usuario normal creado (user)');
    }



  } catch (err) {
    console.log('Error en seeder:', err.message);
  }
}

async function startServer() {
  await client.connect();
  await connectDB();
  await seedDB();

  const PORT = process.env.PORT || 3000;
  app.listen(PORT, () => console.log(`Servidor en http://localhost:${PORT}`));
}

if (require.main === module) {
  startServer();
}

module.exports = app;
