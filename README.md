# 🃏 CromosMarket - Marketplace de Cromos

**Práctica 1 - Programación Web 2**  
*Desarrollo de un SPA con Svelte 5 y Node.js + Express + MongoDB*

---

## 📋 Descripción

CromosMarket es un marketplace fullstack para compra y venta de cromos digitales. Los usuarios pueden:
- 🔐 Autenticarse con JWT
- 📸 Publicar cromos para vender
- 🛒 Comprar cromos de otros usuarios
- 👤 Gestionar su perfil y estadísticas
- ⚙️ (Admin) Administrar usuarios y comisiones

---



## 🚀 Instalación y Ejecución

### Requisitos Previos
- Node.js 16+ 
- npm o yarn
- MongoDB local o remota
- Puerto 3000 disponible (backend y frontend)

### 1. Backend (Express + MongoDB)

```bash
# Navegar a la carpeta backend
cd backend

# Instalar dependencias
npm install

# Configurar variables de entorno (opcional)
# Crear archivo .env:
# DATABASE_URL=mongodb://localhost:27017/cromos
# JWT_SECRET=tu_forma_secreta_aqui
# PORT=3000
# NODE_ENV=development

# Iniciar servidor
npm start
# O en desarrollo con auto-reload:
npm run dev

# Para popular BDD de prueba:
npm run seed
```

**Servidor en:** http://localhost:3000  
**Swagger API Docs:** http://localhost:3000/api-docs

#### Usuarios de Prueba (después de seed)
| Usuario | Contraseña | Rol |
|---------|-----------|-----|
| `admin` | `admin123` | Admin |
| `user` | `user123` | Usuario |

### 2. Frontend (Svelte 5 + Vite)

```bash
# Navegar a la carpeta frontend-cromos
cd frontend-cromos

# Instalar dependencias
npm install

# Iniciar servidor de desarrollo
npm run dev
# La app se abre en: http://localhost:5173

# Para compilar producción:
npm run build
```

**Frontend ejecutándose en:** http://localhost:5173

---

## 📱 Pantallas del Aplicación

| Ruta | Nombre | Tipo | Rol Requerido |
|------|--------|------|---------------|
| `/` | Home - Mercado | Pública | Ninguno |
| `/login` | Login / Registro | Pública | Ninguno |
| `/publicar` | Publicar Cromo | Privada | Usuario |
| `/perfil` | Mi Perfil | Privada | Usuario |
| `/admin` | Panel Admin | Privada | Admin |

---

## 🧬 Runes de Svelte 5 Utilizados

### 1️⃣ `$state()` - Estado Reactivo
**Archivos donde se usa:**
- `src/store/auth.svelte.js` → `auth.user`, `auth.token`, `auth.ready`
- `src/store/cart.svelte.js` → `cart.items`
- `src/store/toast.svelte.js` → `toasts.list`
- `src/pages/Home.svelte` → `cromos`, `search`, `sortBy`, `selectedCromo`
- `src/pages/Profile.svelte` → `allCromos`, `editingCromo`, `detailCromo`
- `src/pages/Admin.svelte` → `users`, `cromos`, `activeTab`, form inputs
- `src/components/ProductForm.svelte` → `nombre`, `precio`, `descripcion`, `saving`
- `src/components/Navbar.svelte` → `showCart`, `checkingOut`
- Y muchos más...

**Ejemplo:**
```javascript
// Autenticación global
export const auth = $state({
  user: null,
  token: null,
  ready: false
});

// Formulario
let username = $state('');
let password = $state('');
let loading = $state(false);
```

### 2️⃣ `$derived()` - Valores Derivados
**Archivos donde se usa:**
- `src/pages/Home.svelte`
  - `filtered` → cromos filtrados por búsqueda y ordenamiento
  - `totalDisponibles` → contador de cromos disponibles
  - `totalVendidos` → contador de cromos vendidos

- `src/pages/Profile.svelte`
  - `misCromosVenta` → cromos que he vendido
  - `misCompras` → cromos que he comprado
  - `totalPublicados`, `totalVendidos`, `ingresosBrutos`, `gastoTotal` → estadísticas

- `src/pages/Admin.svelte`
  - `cromosVendidos`, `volumenVentas`, `gananciaAdmin` → KPIs
  - `userStats` → estadísticas de cada usuario (complejos)
  - `selectedStats` → stats del usuario seleccionado

- `src/components/CromoCard.svelte`
  - `precio` → formateado a 2 decimales
  - `foto` → URL con fallback
  - `isSold` → si el cromo está vendido

- `src/components/ProductForm.svelte`
  - `isEdit` → detecta si estamos editando o creando
  - `errors` → validaciones reactivas del formulario
  - `formValid` → si el form es válido

- `src/components/Navbar.svelte`
  - `totals` → suma de carrito
  - `visibleLinks` → links según rol del usuario

**Ejemplo:**
```javascript
// Filtrado reactivo sin recalcular innecesariamente
let filtered = $derived.by(() => {
  let list = cromos;
  if (!showSold) list = list.filter(c => c.estado_venta !== 'vendido');
  if (search) {
    const q = search.toLowerCase();
    list = list.filter(c => c.nombre?.toLowerCase().includes(q));
  }
  if (sortBy === 'barato') list = [...list].sort((a, b) => a.precio - b.precio);
  return list;
});

let totalDisponibles = $derived(cromos.filter(c => c.estado_venta !== 'vendido').length);
```

### 3️⃣ `$effect()` - Side Effects
**Archivos donde se usa:**
- `src/App.svelte` → Inicializar auth e iniciar listener de hash router
- `src/pages/Home.svelte` → Cargar cromos al montar
- `src/pages/Login.svelte` → Redirigir si ya está autenticado
- `src/pages/Publish.svelte` → Proteger acceso (solo usuarios no-admin)
- `src/pages/Profile.svelte` → Cargar datos y proteger acceso
- `src/pages/Admin.svelte` → Cargar datos de usuarios y cromos si es admin

**Ejemplo:**
```javascript
// Sincronización de estado con backend
$effect(() => {
  if (auth.ready && !auth.user) {
    navigate('/login');
    return;
  }
  if (auth.user) {
    getCromos().then(data => { cromos = data; });
  }
});

// Setup/Teardown de listeners
$effect(() => {
  initAuth();
  function onHash() { path = window.location.hash.slice(1) || '/'; }
  window.addEventListener('hashchange', onHash);
  return () => window.removeEventListener('hashchange', onHash);
});
```

### 4️⃣ `$props()` - Props de Componentes
**Archivos donde se usa:**
- `src/components/CromoCard.svelte`
  ```javascript
  let { cromo, onBuy, onDelete, onDetail, showDelete = false, isOwner = false, isAdmin = false } = $props();
  ```

- `src/components/ProductForm.svelte`
  ```javascript
  let { cromo = null, onSave, onCancel } = $props();
  ```

- `src/components/Navbar.svelte`
  ```javascript
  let { currentPage = '/', navigate, onPurchaseComplete = () => {} } = $props();
  ```

---

## 🔌 Endpoints de la API

### Autenticación
```
POST /api/login
POST /api/register
```

### Productos (Cromos)
```
GET    /api/productos           # Listado público
POST   /api/productos           # Crear (autenticado)
PUT    /api/productos/{id}      # Actualizar (dueño/admin)
DELETE /api/productos/{id}      # Eliminar (dueño/admin)
```

### Usuarios (Solo Admin)
```
GET    /api/users               # Listar (admin)
POST   /api/users               # Crear (admin)
PUT    /api/users/{id}          # Actualizar (admin)
DELETE /api/users/{id}          # Eliminar (admin)
```

**Documentación completa con Swagger:**  
http://localhost:3000/api-docs (cuando backend esté ejecutándose)

---

## 🏗️ Estructura del Proyecto

```
Practica 1 Progra web 2/
├── backend/                          # API Express + MongoDB
│   ├── src/
│   │   ├── app.js                   # Aplicación Express
│   │   ├── config/
│   │   │   ├── db.js                # Conexión MongoDB
│   │   │   ├── redis.js             # Conexión Redis (caching)
│   │   │   └── swagger.js           # Documentación API
│   │   ├── controllers/             # Lógica de negocio
│   │   │   ├── authController.js
│   │   │   ├── productController.js
│   │   │   └── userController.js
│   │   ├── models/                  # Esquemas MongoDB
│   │   │   ├── User.js
│   │   │   └── Producto.js
│   │   ├── middleware/
│   │   │   ├── authMiddleware.js    # JWT verificación
│   │   │   └── rateLimiter.js       # Rate limiting
│   │   ├── routes/                  # Definición de endpoints
│   │   │   ├── authRoutes.js
│   │   │   ├── productRoutes.js
│   │   │   └── userRoutes.js
│   │   └── services/                # Lógica transversal
│   │       ├── authService.js
│   │       ├── productService.js
│   │       └── userService.js
│   ├── uploads/                     # Imágenes subidas
│   ├── package.json
│   ├── server.js                    # Entry point
│   └── .env (crear)                 # Variables de entorno
│
├── frontend-cromos/                 # App Svelte 5 + Vite
│   ├── src/
│   │   ├── App.svelte               # Componente raíz con router
│   │   ├── app.css                  # Design system global
│   │   ├── components/
│   │   │   ├── CromoCard.svelte     # Tarjeta de cromo
│   │   │   ├── CromoDetail.svelte   # Modal de detalle
│   │   │   ├── ProductForm.svelte   # Formulario crear/editar
│   │   │   ├── Navbar.svelte        # Barra de navegación
│   │   │   └── Toast.svelte         # Notificaciones
│   │   ├── pages/
│   │   │   ├── Home.svelte          # Mercado principal
│   │   │   ├── Login.svelte         # Login/Registro
│   │   │   ├── Publish.svelte       # Publicar cromo
│   │   │   ├── Profile.svelte       # Perfil usuario
│   │   │   └── Admin.svelte         # Panel administrativo
│   │   ├── services/
│   │   │   └── api.js               # Cliente HTTP
│   │   ├── store/
│   │   │   ├── auth.svelte.js       # Store autenticación
│   │   │   ├── cart.svelte.js       # Store carrito
│   │   │   └── toast.svelte.js      # Store notificaciones
│   │   └── main.js                  # Entry point
│   ├── package.json
│   ├── vite.config.js
│   └── index.html
│
├── docker-compose.yml               # Orquestación de servicios
├── docker-compose.prod.yml          # Configuración producción
├── AUDITORIA.md                     # Este archivo de auditoría
└── README.md                        # Este archivo
```

---

## 🎨 Características Visuales

### Design System
- **Colores:** Púrpura (#6C5CE7), Verde (#00B894), Rojo (#E17055)
- **Tipografía:** Inter (body), Space Grotesk (headings)
- **Componentes:** Cards con glass effect, inputs modernos, botones fluidos

### Responsividad
- ✅ Desktop (1200px+)
- ✅ Tablet (768px - 1199px)
- ✅ Móvil (< 768px)

### Experiencia de Usuario
- 🔄 Spinners de carga
- 🔔 Toast notifications (success/error/info)
- ✅ Modal de confirmación para acciones destructivas
- 📊 Estadísticas en tiempo real (Profile, Admin)
- 🔍 Búsqueda y filtros activos
- 💾 Carrito persistente en sesión
- 🚫 Estados vacíos amigables

---

## 🔐 Autenticación y Autorización

### JWT Flow
1. Usuario entra username + password en `/login`
2. Backend valida credenciales, genera JWT
3. Frontend almacena token en localStorage
4. Requests posteriores incluyen: `Authorization: Bearer {token}`
5. Al logout, se limpia localStorage

### Roles
- **user** → Puede ver mercado, comprar, publicar, editar sus cromos
- **admin** → Tiene acceso completo, CRUD de usuarios, ver analytics

### Protección de Rutas
- `/publicar` → Redirige si no está autenticado o es admin
- `/perfil` → Solo usuarios autenticados
- `/admin` → Solo admins

---

## 🧪 Pruebas

```bash
# Backend
cd backend
npm test

# Frontend (con vitest)
cd frontend-cromos
npm test
```

---

## 📦 Dependencias Principales

### Backend
- **express** - Framework web
- **mongodb/mongoose** - Base de datos
- **jsonwebtoken** - Autenticación JWT
- **bcryptjs** - Hash de contraseñas
- **multer** - Carga de archivos
- **express-rate-limit** - Rate limiting
- **swagger-ui-express** - Documentación API

### Frontend
- **svelte** v5.0.0 - Framework UI
- **vite** - Build tool
- **lucide-svelte** - Iconos SVG

---

## 🚀 Despliegue

### Con Docker Compose
```bash
# Producción
docker-compose -f docker-compose.prod.yml up -d

# Desarrollo
docker-compose up -d
```

### Manualmente
1. Compilar frontend: `cd frontend-cromos && npm run build`
2. Servir desde backend o servidor estático
3. Configurar variables de entorno en `.env`
4. Iniciar servidor Node

---

## 📝 Notas de Implementación

### Decisiones Técnicas
- **Router SPA basado en hash** - Más simple que alternativas, no requiere SvelteKit
- **localStorage para JWT** - Suficiente para MVP, considerar httpOnly cookies en producción
- **Svelte 5 Runes** - Uso extensivo de `$state()`, `$derived()`, `$effect()` para reactividad moderna
- **API REST** - Simple y directa, documentada con Swagger
- **MongoDB** - Base de datos NoSQL flexible para cromos con metadata variable

### Mejoras Futuras
- [ ] Implementar paginación en endpoints
- [ ] Agregar tests automatizados (Jest, Vitest)
- [ ] Cacheo con Redis
- [ ] WebSockets para actualizaciones en tiempo real
- [ ] Sistema de recomendaciones
- [ ] Pagos reales con Stripe
- [ ] AWS S3 para imágenes
- [ ] GraphQL como alternativa a REST

---

## 📞 Soporte

**Problemas comunes:**

**"Error: enoent: no such file or directory"**
→ Ejecutar `npm install` en la carpeta del proyecto

**"Connection refused: localhost:3000"**
→ Asegurar que backend está ejecutándose con `npm start`

**"CORS error"**
→ Backend debe tener CORS habilitado (check `src/app.js`)

**"MongoDB connection failed"**
→ Verificar que MongoDB está ejecutándose o usar MongoDB Atlas

---

## 📄 Licencia

MIT License - Proyecto académico

---

## 👨‍💻 Autor

Pablo Cantero - Práctica 1 Programación Web 2

---

**Última actualización:** 26 de Marzo de 2026
