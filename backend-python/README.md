# CromosMarket — Backend Python (FastAPI)

Reemplazo del backend Node.js/Express con FastAPI + SQLAlchemy + SQLite.

## Instalación

```bash
cd backend-python
pip install -r requirements.txt
```

## Arranque

```bash
python seed.py && uvicorn app.main:app --reload --port 3000
```

El servidor queda disponible en `http://localhost:3000`.  
Usuarios creados por el seed: `admin / admin123` (role: admin) y `user / user123` (role: user).

## Endpoints

| Método | Ruta | Auth | Descripción |
|--------|------|------|-------------|
| POST | `/api/login` | — | Iniciar sesión |
| POST | `/api/register` | — | Registrar usuario |
| GET | `/api/productos` | — | Listar cromos |
| POST | `/api/productos` | Usuario | Publicar cromo (multipart/form-data) |
| PUT | `/api/productos/:id` | Usuario | Actualizar cromo |
| DELETE | `/api/productos/:id` | Usuario | Eliminar cromo |
| GET | `/api/cart` | Usuario | Ver carrito |
| POST | `/api/cart/add` | Usuario | Añadir al carrito |
| POST | `/api/cart/checkout` | Usuario | Comprar carrito completo |
| DELETE | `/api/cart/:id` | Usuario | Quitar del carrito |
| GET | `/api/users` | Admin | Listar usuarios |
| POST | `/api/users` | Admin | Crear usuario |
| PUT | `/api/users/:id` | Admin | Actualizar usuario |
| DELETE | `/api/users/:id` | Admin | Eliminar usuario |

Las imágenes se sirven en `GET /uploads/:filename`.

## Estructura

```
backend-python/
├── app/
│   ├── main.py           # FastAPI app, CORS, routers, exception handlers
│   ├── config.py         # Settings (pydantic-settings)
│   ├── database.py       # SQLAlchemy engine + SessionLocal + Base
│   ├── dependencies.py   # get_db, get_current_user, require_admin
│   ├── models/           # SQLAlchemy ORM models
│   ├── schemas/          # Pydantic v2 schemas
│   ├── repositories/     # Acceso a DB
│   ├── services/         # Lógica de negocio
│   └── routers/          # Endpoints FastAPI
├── uploads/              # Imágenes subidas
├── requirements.txt
└── seed.py
```
