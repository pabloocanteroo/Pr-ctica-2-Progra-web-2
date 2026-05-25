# Memoria de uso de Inteligencia Artificial — Práctica 2

## 1. Registro de prompts e iteraciones

### Prompt 1 — Generación inicial del backend

Este fue el primer prompt utilizado para construir el backend completo en Python con FastAPI:

---

Necesito que construyas un backend Python (FastAPI) para reemplazar un backend Node.js/Express existente. El frontend en Svelte 5 debe seguir funcionando sin cambios. Te doy todo el contexto:

**CONTEXTO: API CONTRACT DEL BACKEND ANTERIOR (Node.js)**

Base URL: http://localhost:3000/api

Endpoints de Auth:
- POST /api/login → body: { username, password } → responde: { token, user: { _id, username, role } }
- POST /api/register → body: { username, password } → responde: { token, user: { _id, username, role } }

Endpoints de Productos (Cromos):
- GET /api/productos → público, responde array de productos
- POST /api/productos → auth requerida, multipart/form-data con campos: nombre, precio, descripcion, imagen (file)
- PUT /api/productos/:id → auth requerida (owner o admin), body JSON
- DELETE /api/productos/:id → auth requerida (owner o admin)

Estructura JSON de un producto:
```json
{
  "_id": "string",
  "nombre": "string",
  "precio": number,
  "vendedor": "string (username)",
  "comprador": null | "string",
  "descripcion": "string",
  "estado_venta": "disponible" | "vendido",
  "fecha_venta": null | "ISO date string",
  "imagen": "string (filename)"
}
```

Las imágenes se sirven como estático en: GET /uploads/:filename

Endpoints de Carrito:
- GET /api/cart → auth requerida → responde: { items: [...productos] }
- POST /api/cart/add → auth requerida → body: { productoId }
- POST /api/cart/checkout → auth requerida → compra todos los items, marca productos como vendidos, limpia carrito

Endpoints de Usuarios (solo admin):
- GET /api/users, POST /api/users, PUT /api/users/:id, DELETE /api/users/:id

Estructura JSON de un usuario:
```json
{ "_id": "string", "username": "string", "role": "user" | "admin" }
```
(NO devolver password)

JWT payload: { "userId": "string", "username": "string", "role": "user"|"admin" }

El frontend envía el token en header: Authorization: Bearer <token>. El frontend corre en puerto 5173 → el backend necesita CORS para ese origen.

**LO QUE TIENES QUE CONSTRUIR**

Crea un backend FastAPI en Python en la carpeta `backend-python/`. Arquitectura en capas obligatoria: routers, services, repositories, models, schemas y dependencies. Base de datos SQLite con SQLAlchemy. Pydantic v2 para validación. python-jose para JWT (HS256). passlib con bcrypt para contraseñas. Manejador global de excepciones. El campo `_id` en las respuestas debe ser string mapeado desde el id de SQLAlchemy. Incluir seed.py con usuarios admin/admin123 y user/user123, requirements.txt y README.

---

**Resultado del Prompt 1:** La IA generó la estructura completa del proyecto con todos los archivos. El servidor arrancó correctamente, pero tras revisar el código en detalle se detectaron varios fallos que se detallan en la sección de análisis crítico.

---

### Prompt 2 — Corrección de fallos detectados

Tras revisar manualmente el código generado, se identificaron cinco errores y se solicitó su corrección con el siguiente prompt:

---

Revisa el backend-python que generaste y corrige estos fallos que he detectado:

1. En `app/services/product_service.py`, el método checkout no valida si el producto ya tiene `estado_venta="vendido"` antes de marcarlo como vendido. Hay que añadir esa comprobación y lanzar HTTPException 400 si el producto ya está vendido.

2. En `app/routers/products.py`, el endpoint POST /api/productos acepta "vendedor" como parámetro del form y lo usa si no es None. Esto permite que cualquier usuario publique en nombre de otro. Elimina ese parámetro del form y usa siempre `current_user.username` como vendedor.

3. En `app/services/product_service.py`, el método get_cart devuelve objetos SQLAlchemy crudos dentro del dict items. Envuélvelos con `ProductOut.model_validate(item.product)` para que sean correctamente serializados.

4. En `app/routers/products.py`, la subida de imagen no valida la extensión. Añade una whitelist de extensiones permitidas (jpg, jpeg, png, gif, webp) y lanza HTTPException 400 si la extensión no está en la lista.

5. En `app/schemas/product.py`, el campo precio en ProductCreate y ProductUpdate no tiene validación. Usa `Field(gt=0)` para rechazar precios menores o iguales a cero.

No toques nada más, solo corrige exactamente estos cinco puntos.

---

**Resultado del Prompt 2:** La IA corrigió los cinco puntos indicados sin alterar el resto del código.

---

## 2. Análisis crítico: errores cometidos por la IA

### Error 1 — Fallo de lógica de negocio en el checkout (alta gravedad)

**Descripción del error:**

En `app/services/product_service.py`, el método `checkout` generado por la IA marcaba directamente todos los productos del carrito como vendidos sin comprobar previamente si ya estaban vendidos:

```python
# Código generado por la IA (incorrecto)
for item in items:
    product = item.product
    product.estado_venta = "vendido"  # Sin ninguna validación previa
    product.comprador = username
    product.fecha_venta = now
```

**Por qué es incorrecto:**

Este código permite una condición de carrera: si dos usuarios añaden el mismo producto a sus carritos y hacen checkout al mismo tiempo, el producto quedaría marcado como vendido dos veces, con dos compradores distintos. Esto rompe una regla fundamental de negocio: cada producto solo puede tener un comprador. La IA generó la lógica de escritura en base de datos sin tener en cuenta la validación del estado previo del recurso.

**Cómo se corrigió:**

Se añadió una comprobación explícita antes de actualizar el estado del producto:

```python
# Código corregido manualmente
for item in items:
    product = item.product
    if product.estado_venta == "vendido":
        raise HTTPException(status_code=400, detail=f"El producto '{product.nombre}' ya ha sido vendido")
    product.estado_venta = "vendido"
    product.comprador = username
    product.fecha_venta = now
```

---

### Error 2 — Vulnerabilidad de suplantación de vendedor (alta gravedad)

**Descripción del error:**

En `app/routers/products.py`, la IA generó el endpoint de creación de producto aceptando el campo `vendedor` como parámetro del formulario enviado por el cliente:

```python
# Código generado por la IA (incorrecto)
vendedor: Optional[str] = Form(None),
...
"vendedor": vendedor or current_user.username,
```

**Por qué es incorrecto:**

Esto es una vulnerabilidad de autorización. Cualquier usuario autenticado podría enviar `vendedor=admin` en el formulario y publicar un producto como si fuera el administrador u otro usuario. La regla de negocio es que el vendedor siempre debe ser el usuario que realiza la petición, no un valor que él mismo aporta. La IA no detectó que confiar en datos del cliente para identificar al autor de una acción es un fallo de seguridad básico (broken object level authorization).

**Cómo se corrigió:**

Se eliminó el parámetro `vendedor` del form y se usa siempre el usuario autenticado:

```python
# Código corregido manualmente
# (El parámetro vendedor desaparece del form completamente)
"vendedor": current_user.username,
```

---

### Error 3 — Serialización incorrecta en el carrito (gravedad media)

**Descripción del error:**

En `app/services/product_service.py`, el método `get_cart` devolvía objetos ORM de SQLAlchemy directamente dentro de un diccionario:

```python
# Código generado por la IA (incorrecto)
return {"items": [item.product for item in items]}
```

**Por qué es incorrecto:**

FastAPI no puede serializar a JSON objetos ORM de SQLAlchemy directamente. Cuando el router intenta convertir la respuesta, se producen errores de serialización o se devuelven campos internos que no deberían exponerse. Los objetos de base de datos deben pasarse siempre por el schema de Pydantic correspondiente antes de ser devueltos al cliente.

**Cómo se corrigió:**

```python
# Código corregido manualmente
return {"items": [ProductOut.model_validate(item.product) for item in items]}
```

---

### Conclusión

La IA fue útil para generar rápidamente la estructura del proyecto y el código base, ahorrando tiempo en la configuración inicial de capas, modelos y configuración de JWT. Sin embargo, demostró limitaciones claras en dos áreas importantes: la lógica de negocio con estados concurrentes (error en checkout) y la seguridad a nivel de autorización (suplantación de vendedor). Estos errores habrían pasado desapercibidos en una revisión superficial del código, lo que refuerza la necesidad de revisar siempre el código generado por IA antes de considerarlo correcto y seguro.
