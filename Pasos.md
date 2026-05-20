# Guía Práctica 2 — Backend Python con FastAPI
## De Node.js/Express + MongoDB → Python/FastAPI + SQLite (SQLAlchemy)

> **Objetivo**: Reemplazar el backend de la Práctica 1 (Express + Mongoose) por uno nuevo en Python con FastAPI, manteniendo exactamente el mismo contrato de API que ya consume el frontend en Svelte 5.

---

## Índice

1. [Estructura de carpetas objetivo](#1-estructura-de-carpetas-objetivo)
2. [Fase 0 — Configuración inicial del proyecto](#fase-0--configuración-inicial-del-proyecto)
3. [Fase 1 — Base de datos y modelos ORM](#fase-1--base-de-datos-y-modelos-orm)
4. [Fase 2 — Esquemas Pydantic (validación)](#fase-2--esquemas-pydantic-validación)
5. [Fase 3 — Capa de repositorios](#fase-3--capa-de-repositorios)
6. [Fase 4 — Capa de servicios](#fase-4--capa-de-servicios)
7. [Fase 5 — Autenticación JWT](#fase-5--autenticación-jwt)
8. [Fase 6 — Routers (controladores HTTP)](#fase-6--routers-controladores-http)
9. [Fase 7 — Manejo global de errores](#fase-7--manejo-global-de-errores)
10. [Fase 8 — Punto de entrada y CORS](#fase-8--punto-de-entrada-y-cors)
11. [Checklist final](#checklist-final)

---

## 1. Estructura de carpetas objetivo

```
backend_python/
├── app/
│   ├── __init__.py
│   ├── main.py                  # Punto de entrada FastAPI
│   ├── database.py              # Conexión SQLAlchemy + Base declarativa
│   ├── dependencies.py          # Dependencias reutilizables (get_db, get_current_user)
│   ├── exceptions.py            # Excepciones de dominio personalizadas
│   ├── error_handlers.py        # Manejador global de excepciones
│   │
│   ├── models/                  # Modelos ORM (tablas SQLAlchemy)
│   │   ├── __init__.py
│   │   ├── usuario.py
│   │   └── producto.py
│   │
│   ├── schemas/                 # Esquemas Pydantic (validación E/S)
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── usuario.py
│   │   └── producto.py
│   │
│   ├── repositories/            # Acceso a datos (patrón repositorio)
│   │   ├── __init__.py
│   │   ├── usuario_repository.py
│   │   └── producto_repository.py
│   │
│   ├── services/                # Lógica de negocio
│   │   ├── __init__.py
│   │   ├── auth_service.py
│   │   ├── usuario_service.py
│   │   └── producto_service.py
│   │
│   └── routers/                 # Controladores HTTP
│       ├── __init__.py
│       ├── auth.py
│       ├── usuarios.py
│       └── productos.py
│
├── uploads/                     # Imágenes subidas
├── .env
├── requirements.txt
└── README.md
```

---

## Fase 0 — Configuración inicial del proyecto

### Prompt 0.1 — Crear `requirements.txt` y `.env`

```
Estoy creando un backend en Python con FastAPI para una aplicación web.
Necesito que generes el archivo requirements.txt con las siguientes dependencias:
- FastAPI y uvicorn (servidor ASGI)
- SQLAlchemy (ORM) con soporte para SQLite
- Pydantic v2 con email-validator
- python-jose[cryptography] para JWT
- passlib[bcrypt] para hashing de contraseñas
- python-multipart para subida de archivos
- python-dotenv para variables de entorno

Añade también un archivo .env de ejemplo con:
- SECRET_KEY (para JWT, genera una cadena larga aleatoria de ejemplo)
- ALGORITHM=HS256
- ACCESS_TOKEN_EXPIRE_MINUTES=10080 (7 días en minutos)
- DATABASE_URL=sqlite:///./app.db
```

**Resultado esperado**: `requirements.txt` y `.env.example` listos para usar.

---

## Fase 1 — Base de datos y modelos ORM

### Prompt 1.1 — Conexión a la base de datos

```
Crea el archivo app/database.py para un proyecto FastAPI con SQLAlchemy y SQLite.
Debe contener:
1. El engine de SQLAlchemy usando la DATABASE_URL del .env con python-dotenv
2. SessionLocal (sessionmaker) para las sesiones de base de datos
3. Base (declarative_base) que importarán los modelos
4. Una función init_db() que crea todas las tablas si no existen, llamando a Base.metadata.create_all(bind=engine)
```

### Prompt 1.2 — Modelo Usuario

```
Crea el modelo ORM SQLAlchemy en app/models/usuario.py para una tabla "usuarios" con estas columnas:
- id: UUID generado automáticamente (como string), clave primaria
- username: String(50), único, no nulo
- email: String(100), único, no nulo
- hashed_password: String(255), no nulo
- role: String(20), no nulo, por defecto "usuario" (valores posibles: "usuario", "administrador")
- profile_picture: String(255), nullable, por defecto ""
- created_at: DateTime, por defecto datetime.utcnow
- updated_at: DateTime, por defecto datetime.utcnow, se actualiza en cada save (onupdate=datetime.utcnow)

El modelo debe importar Base desde app.database.
```

**⚠️ Error frecuente de la IA aquí**: La IA a veces genera `id = Column(Integer, primary_key=True)` en lugar de UUID. Verifica que usa `default=lambda: str(uuid.uuid4())` para compatibilidad con el frontend que espera IDs tipo MongoDB ObjectId (strings).

### Prompt 1.3 — Modelo Producto

```
Crea el modelo ORM SQLAlchemy en app/models/producto.py para una tabla "productos" con estas columnas:
- id: UUID string, clave primaria, generado automáticamente
- nombre: String(100), no nulo
- precio: Float, no nulo, mayor que 0
- descripcion: Text, no nulo
- imagen: String(255), nullable
- categoria: String(50), no nulo, por defecto "Otros"
- plataforma: String(50), por defecto "Otro"
- activo: Boolean, por defecto True
- created_at: DateTime, por defecto datetime.utcnow
- updated_at: DateTime, por defecto datetime.utcnow, onupdate=datetime.utcnow

Importa Base desde app.database.
```

---

## Fase 2 — Esquemas Pydantic (validación)

### Prompt 2.1 — Esquemas de autenticación

```
Crea app/schemas/auth.py con esquemas Pydantic v2 para autenticación:

1. LoginRequest: email (EmailStr), password (str, min 6 chars)
2. RegistroRequest: username (str, min 3 chars, max 50), email (EmailStr), password (str, min 6), role (Literal["usuario","administrador"], default "usuario")
3. TokenResponse: token (str), usuario (objeto con id, username, email, role), mensaje (str)
4. PerfilResponse: usuario (objeto con id, username, email, role, profile_picture, created_at)

El campo "id" en las respuestas debe ser str (no UUID nativo), serializado desde el campo "id" del modelo ORM.
Usa model_config = ConfigDict(from_attributes=True) en los esquemas de respuesta para que funcionen con ORM.
```

### Prompt 2.2 — Esquemas de Producto

```
Crea app/schemas/producto.py con esquemas Pydantic v2:

1. ProductoCreate: nombre (str, min 1, max 100), precio (float, gt=0), descripcion (str, min 1), 
   categoria (str, default="Otros"), plataforma (str, default="Otro"), activo (bool, default=True)
   
2. ProductoUpdate: todos los campos opcionales (Optional) con los mismos validadores

3. ProductoResponse: todos los campos del modelo más id (str), created_at (datetime), updated_at (datetime)
   - El campo "id" debe mapearse desde "id" del ORM
   - Añade model_config = ConfigDict(from_attributes=True)
   - El campo imagen debe ser Optional[str] = None

Los campos created_at y updated_at deben devolver strings ISO 8601 en la serialización JSON
para compatibilidad con el frontend Svelte que ya los procesa.
```

**Nota**: El frontend Svelte accede a `producto._id` (underscore), pero SQLAlchemy usará `id`. Necesitarás un alias o renombrar el campo en la respuesta. Usa `Field(alias="_id")` o añade un `@computed_field` que exponga `_id`. Ejemplo de prompt de refinamiento:

```
El frontend en Svelte accede a los productos como producto._id (con underscore delante).
Modifica ProductoResponse para que el campo id se serialice como "_id" en el JSON de respuesta.
Usa Field(serialization_alias="_id") y configura model_config con populate_by_name=True y from_attributes=True.
```

### Prompt 2.3 — Esquemas de Usuario

```
Crea app/schemas/usuario.py con esquemas Pydantic v2:

1. UsuarioCreate: username (str, 3-50 chars), email (EmailStr), password (str, min 6), 
   role (Literal["usuario","administrador"], default "usuario")
   
2. UsuarioUpdate: todos opcionales; si password está presente, debe tener min 6 chars

3. UsuarioResponse: id (str, serialization_alias="_id"), username, email, role, 
   profile_picture (Optional[str]), created_at (datetime), updated_at (datetime)
   model_config = ConfigDict(from_attributes=True, populate_by_name=True)
```

---

## Fase 3 — Capa de repositorios

### Prompt 3.1 — Repositorio de Usuario

```
Crea app/repositories/usuario_repository.py con una clase UsuarioRepository que recibe una 
sesión SQLAlchemy (Session) en su constructor y expone estos métodos:

- get_by_id(user_id: str) -> Optional[Usuario]
- get_by_email(email: str) -> Optional[Usuario]
- get_by_username(username: str) -> Optional[Usuario]
- get_all() -> list[Usuario]
- create(data: dict) -> Usuario  (data ya tiene hashed_password, no password en plano)
- update(user_id: str, data: dict) -> Optional[Usuario]
- delete(user_id: str) -> bool

No incluyas lógica de negocio (hashing, validaciones, JWT). Solo acceso a datos.
```

### Prompt 3.2 — Repositorio de Producto

```
Crea app/repositories/producto_repository.py con una clase ProductoRepository que recibe 
Session en su constructor y expone:

- get_all(solo_activos: bool = False) -> list[Producto]  (ordenados por created_at DESC)
- get_by_id(producto_id: str) -> Optional[Producto]
- create(data: dict) -> Producto
- update(producto_id: str, data: dict) -> Optional[Producto]
- delete(producto_id: str) -> bool

Solo acceso a datos, sin lógica de negocio.
```

---

## Fase 4 — Capa de servicios

### Prompt 4.1 — Servicio de autenticación

```
Crea app/services/auth_service.py con clase AuthService que recibe UsuarioRepository.
Dependencias: passlib[bcrypt] para hashing, python-jose para JWT.
Lee SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES del .env.

Métodos:
- hash_password(password: str) -> str
- verify_password(plain: str, hashed: str) -> bool  
- create_access_token(data: dict) -> str  (expira según ACCESS_TOKEN_EXPIRE_MINUTES)
- decode_token(token: str) -> dict  (lanza excepción personalizada si inválido o expirado)
- login(email: str, password: str) -> dict  (devuelve {token, usuario})
  - Lanza CredencialesInvalidasError si email no existe o contraseña incorrecta
- registro(username, email, password, role) -> dict
  - Lanza UsuarioDuplicadoError si email o username ya existen
```

### Prompt 4.2 — Servicio de Producto

```
Crea app/services/producto_service.py con clase ProductoService que recibe ProductoRepository.

Métodos:
- listar_productos() -> list[Producto]
- obtener_producto(producto_id: str) -> Producto  (lanza ProductoNoEncontradoError si no existe)
- crear_producto(data: ProductoCreate, imagen_url: Optional[str]) -> Producto
- actualizar_producto(producto_id: str, data: ProductoUpdate, imagen_url: Optional[str]) -> Producto
  (lanza ProductoNoEncontradoError si no existe)
- eliminar_producto(producto_id: str) -> bool
  (lanza ProductoNoEncontradoError si no existe)

No importes modelos HTTP (Request/Response de FastAPI) aquí. Solo lógica de negocio pura.
```

### Prompt 4.3 — Servicio de Usuario

```
Crea app/services/usuario_service.py con clase UsuarioService que recibe UsuarioRepository
y AuthService (para hashear passwords).

Métodos:
- listar_usuarios() -> list[Usuario]
- obtener_usuario(user_id: str) -> Usuario  (lanza UsuarioNoEncontradoError si no existe)
- crear_usuario(data: UsuarioCreate) -> Usuario
  (hashea password, lanza UsuarioDuplicadoError si email/username duplicados)
- actualizar_usuario(user_id: str, data: UsuarioUpdate) -> Usuario
  (hashea password si viene en data, lanza UsuarioNoEncontradoError si no existe)
- eliminar_usuario(user_id: str) -> bool
```

---

## Fase 5 — Autenticación JWT

### Prompt 5.1 — Excepciones de dominio

```
Crea app/exceptions.py con excepciones personalizadas para el dominio:

class AppError(Exception):
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(message)

class CredencialesInvalidasError(AppError):
    def __init__(self): super().__init__("Credenciales inválidas.", 401)

class TokenInvalidoError(AppError):
    def __init__(self): super().__init__("Token inválido o expirado.", 401)

class PermisoDenegadoError(AppError):
    def __init__(self): super().__init__("Acceso denegado. Permisos insuficientes.", 403)

class ProductoNoEncontradoError(AppError):
    def __init__(self): super().__init__("Producto no encontrado.", 404)

class UsuarioNoEncontradoError(AppError):
    def __init__(self): super().__init__("Usuario no encontrado.", 404)

class UsuarioDuplicadoError(AppError):
    def __init__(self): super().__init__("El usuario o email ya está registrado.", 400)
```

### Prompt 5.2 — Dependencias de FastAPI

```
Crea app/dependencies.py con:

1. get_db(): generador que abre y cierra sesión SQLAlchemy (yield SessionLocal())

2. get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> Usuario:
   - Extrae el token del header Authorization: Bearer <token>
   - Decodifica el JWT usando AuthService
   - Busca el usuario en DB por el "sub" del payload (que es el user_id)
   - Si no lo encuentra o el token es inválido, lanza TokenInvalidoError
   - Retorna el objeto Usuario ORM

3. require_admin(current_user: Usuario = Depends(get_current_user)) -> Usuario:
   - Si current_user.role != "administrador", lanza PermisoDenegadoError
   - Retorna current_user

Usa from fastapi.security import OAuth2PasswordBearer para el esquema del token.
El tokenUrl debe ser "/auth/login".
```

---

## Fase 6 — Routers (controladores HTTP)

### Prompt 6.1 — Router de autenticación

```
Crea app/routers/auth.py con un APIRouter(prefix="/auth", tags=["auth"]).

Endpoints a implementar (mismo contrato que el backend Express anterior):

POST /auth/login
  Body: LoginRequest  →  Response: TokenResponse (200)

POST /auth/registro  
  Body: RegistroRequest  →  Response: TokenResponse (201)

GET /auth/perfil
  Requires: Depends(get_current_user)  →  Response: PerfilResponse (200)

PUT /auth/perfil
  Requires: Depends(get_current_user)
  Body: multipart/form-data con campo "username" opcional y archivo "foto" opcional
  →  Response: PerfilResponse actualizado (200)
  Guarda la imagen en /uploads/ con nombre "profile-{timestamp}{ext}"
  Devuelve la URL como "/uploads/nombre_archivo"

POST /auth/direcciones
  Requires: Depends(get_current_user)
  Body: JSON con name, street, city, state, zip, lat, lng, isDefault
  →  Response: { "mensaje": "Dirección agregada", "addresses": [...] }

DELETE /auth/direcciones/{id}
  Requires: Depends(get_current_user)
  →  Response: { "mensaje": "Dirección eliminada", "addresses": [...] }

POST /auth/metodos-pago
  Requires: Depends(get_current_user)
  Body: JSON con type, last4, expiry, cardholder, isDefault
  →  Response: { "mensaje": "Método de pago agregado", "paymentMethods": [...] }

DELETE /auth/metodos-pago/{id}
  Requires: Depends(get_current_user)
  →  Response: { "mensaje": "Método de pago eliminado", "paymentMethods": [...] }

Inyecta AuthService y UsuarioService mediante Depends(get_db).
No pongas lógica de negocio aquí, solo llamadas a los servicios.
```

### Prompt 6.2 — Router de Productos

```
Crea app/routers/productos.py con APIRouter(prefix="/productos", tags=["productos"]).

Mismo contrato que el backend Express:

GET /productos           → lista todos (público, no requiere auth)
GET /productos/{id}      → obtiene uno (público)
POST /productos          → crea (require_admin), acepta multipart/form-data con campos:
                           nombre, precio (float), descripcion, categoria, plataforma, 
                           activo (bool), imagen (UploadFile opcional)
PUT /productos/{id}      → actualiza (require_admin), mismo formato multipart
DELETE /productos/{id}   → elimina (require_admin)

Para POST y PUT:
- Si viene imagen (UploadFile), guárdala en /uploads/{timestamp}{ext}
- Incluye la ruta "/uploads/nombre" en el campo imagen del producto

Respuestas de error esperadas: 401 si no hay token, 403 si no es admin, 404 si no existe.
Inyecta ProductoService mediante Depends(get_db).
```

### Prompt 6.3 — Router de Usuarios

```
Crea app/routers/usuarios.py con APIRouter(prefix="/usuarios", tags=["usuarios"]).
Todos los endpoints requieren Depends(require_admin).

GET /usuarios            → lista todos (sin passwords)
GET /usuarios/{id}       → obtiene uno
POST /usuarios           → crea usuario (body: UsuarioCreate)
PUT /usuarios/{id}       → actualiza (body: UsuarioUpdate)
DELETE /usuarios/{id}    → elimina

Inyecta UsuarioService mediante Depends(get_db).
```

---

## Fase 7 — Manejo global de excepciones

### Prompt 7.1 — Error handlers

```
Crea app/error_handlers.py con una función register_error_handlers(app: FastAPI) que registre:

1. Handler para AppError (y subclases): devuelve JSONResponse con 
   {"error": exception.message} y el status_code de la excepción.

2. Handler para RequestValidationError (Pydantic): devuelve status 422 con formato:
   {"error": "Datos de entrada inválidos", "detalles": [lista de errores formateados]}

3. Handler para Exception genérica: devuelve status 500 con {"error": "Error interno del servidor"}
   (en producción no exponer detalles; en desarrollo sí)

Importa y llama esta función desde main.py.
```

---

## Fase 8 — Punto de entrada y CORS

### Prompt 8.1 — main.py

```
Crea app/main.py como punto de entrada de FastAPI:

1. Instancia FastAPI con title="API Práctica 2", version="1.0.0"

2. Configura CORS con CORSMiddleware:
   - allow_origins=["http://localhost:5173", "http://localhost:4173"]  (Svelte dev y preview)
   - allow_credentials=True
   - allow_methods=["*"]
   - allow_headers=["*"]

3. Monta la carpeta /uploads como archivos estáticos en /uploads 
   (StaticFiles de Starlette) para que el frontend pueda cargar las imágenes

4. Incluye los routers: auth, productos, usuarios

5. Llama a register_error_handlers(app)

6. En un evento @app.on_event("startup"), llama a init_db() para crear las tablas

7. Añade un endpoint GET / que devuelva {"status": "ok", "mensaje": "API Práctica 2 funcionando"}
```

### Prompt 8.2 — README

```
Genera un README.md para el backend Python con:

## Instalación y ejecución

1. Requisitos: Python 3.11+
2. Crear entorno virtual: python -m venv venv && source venv/bin/activate (Linux/Mac) o venv\Scripts\activate (Windows)
3. Instalar dependencias: pip install -r requirements.txt
4. Copiar .env.example a .env y configurar SECRET_KEY
5. Ejecutar: uvicorn app.main:app --reload --port 3000

## Endpoints principales
(tabla con todos los endpoints, método, autenticación requerida y descripción)

## Roles
- usuario: puede ver productos y su propio perfil
- administrador: CRUD completo de productos y usuarios
```

---

## Checklist final

Antes de entregar, verifica cada punto del rubric:

| Criterio | Check |
|---|---|
| ✅ Estructura en capas: routers / services / repositories / models | |
| ✅ JWT generado y validado en Python (python-jose) | |
| ✅ Contraseñas hasheadas con bcrypt (passlib) | |
| ✅ Endpoints con mismo contrato URL+método que Express | |
| ✅ Respuesta JSON compatible con el frontend Svelte (campo `_id`) | |
| ✅ Validación con Pydantic (422 en datos inválidos) | |
| ✅ Manejador global de excepciones registrado | |
| ✅ Persistencia en SQLite con SQLAlchemy (no arrays en memoria) | |
| ✅ Patrón repositorio (la lógica de negocio no importa Session directamente) | |
| ✅ CORS configurado para el puerto 5173 de Svelte | |
| ✅ Imágenes servidas como archivos estáticos en /uploads | |
| ✅ Documento de prompts e IA incluido | |
| ✅ README con instrucciones de instalación | |

---

## Notas de compatibilidad con el frontend Svelte

El frontend accede a:
- `producto._id` → serializa el `id` del ORM como `_id`  
- `usuario._id` → idem  
- `response.token` y `response.usuario` en login/registro  
- `response.usuario` en GET /auth/perfil  
- Header `Authorization: Bearer <token>` en todas las rutas protegidas  
- Imágenes en `/uploads/<filename>` como URLs relativas  

El frontend **no necesita modificarse** si se mantiene este contrato.