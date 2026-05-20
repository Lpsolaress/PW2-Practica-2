import os
import json
import uuid
import socketio
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse

from app.database import init_db, SessionLocal
from app.models.usuario import Usuario
from app.services.security import get_password_hash
from app.routers import auth, productos, usuarios, carrito, ordenes, notificaciones
from app.error_handlers import register_error_handlers
from app.socket_manager import sio
from jose import jwt, JWTError
from app.dependencies import SECRET_KEY, ALGORITHM

# --- Inicialización de Base de Datos y Seed ---
init_db()

def seed_admin():
    db = SessionLocal()
    try:
        admin_email = "admin@nuba.com"
        admin_user = db.query(Usuario).filter(Usuario.email == admin_email).first()
        
        # Datos por defecto para que el admin pueda pagar de inmediato
        default_addresses = [
            {"_id": str(uuid.uuid4()), "street": "Calle Principal 123, Ciudad Central"},
            {"_id": str(uuid.uuid4()), "street": "Recoger en: Sucursal Nuba Norte"}
        ]
        default_payments = [
            {"_id": str(uuid.uuid4()), "type": "otro", "cardholder": "Apple Pay", "last4": "8888"},
            {"_id": str(uuid.uuid4()), "type": "visa", "cardholder": "Admin Card", "last4": "4242"}
        ]

        if not admin_user:
            admin = Usuario(
                username="admin",
                email=admin_email,
                hashed_password=get_password_hash("admin123password"),
                role="administrador",
                addresses_data=json.dumps(default_addresses),
                payment_methods_data=json.dumps(default_payments)
            )
            db.add(admin)
            db.commit()
            print("Admin user created with default data.")
        else:
            # Si el usuario existe pero no tiene direcciones/pagos, se los ponemos para el test
            if not admin_user.addresses_data or admin_user.addresses_data == "[]":
                admin_user.addresses_data = json.dumps(default_addresses)
            if not admin_user.payment_methods_data or admin_user.payment_methods_data == "[]":
                admin_user.payment_methods_data = json.dumps(default_payments)
            
            admin_user.role = "administrador"
            admin_user.hashed_password = get_password_hash("admin123password")
            db.commit()
            print("Admin user verified and updated with test data.")
    except Exception as e:
        print(f"Error seeding admin: {e}")
    finally:
        db.close()

seed_admin()

# --- Socket.io ---
sio_app = socketio.ASGIApp(sio, socketio_path='/socket.io')

# Montar Socket.io ANTES que cualquier otra cosa para evitar conflictos de rutas
app = FastAPI(
    title="Nuba Store API",
    description="Backend en Python con FastAPI",
    version="1.0.0"
)

# Montamos la app de socket.io en un path específico para que no interfiera con la raíz
app.mount("/socket.io", sio_app)

# --- Middleware ---
origins = [
    "http://localhost:5173",
    "http://localhost:4173",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:4173",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar manejadores de errores globales
register_error_handlers(app)

# --- Rutas de API ---
app.include_router(auth.router)
app.include_router(productos.router)
app.include_router(usuarios.router)
app.include_router(carrito.router)
app.include_router(ordenes.router)
app.include_router(notificaciones.router)

# --- Archivos Estáticos (Uploads) ---
# Asegurar que la ruta sea absoluta respecto a la raíz del proyecto
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
UPLOADS_DIR = os.path.join(BASE_DIR, "uploads")
if not os.path.exists(UPLOADS_DIR):
    os.makedirs(UPLOADS_DIR)
app.mount("/uploads", StaticFiles(directory=UPLOADS_DIR), name="uploads")

# --- Frontend SPA Serving ---
FRONTEND_DIST = os.path.abspath(os.path.join(BASE_DIR, "..", "frontend", "dist"))

# Servir assets del frontend si existen
if os.path.exists(os.path.join(FRONTEND_DIST, "assets")):
    app.mount("/assets", StaticFiles(directory=os.path.join(FRONTEND_DIST, "assets")), name="assets")

@app.get("/favicon.svg")
async def favicon():
    fav_path = os.path.join(FRONTEND_DIST, "favicon.svg")
    if os.path.exists(fav_path):
        return FileResponse(fav_path)
    return JSONResponse(status_code=404, content={"error": "Not Found"})

# Catch-all para SPA Svelte
@app.get("/{full_path:path}")
async def catch_all(full_path: str):
    # Ignorar rutas que deben ser manejadas por la API o Socket.io
    api_prefixes = ("auth/", "productos/", "usuarios/", "carrito/", "ordenes/", "notificaciones/", "uploads/")
    if any(full_path.startswith(prefix) for prefix in api_prefixes):
        return JSONResponse(status_code=404, content={"error": "Not Found"})

    # Intentar servir el archivo si existe físicamente
    file_path = os.path.join(FRONTEND_DIST, full_path)
    if os.path.isfile(file_path):
        return FileResponse(file_path)
    
    # De lo contrario, servir index.html para el router de Svelte
    index_path = os.path.join(FRONTEND_DIST, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    
    return JSONResponse(status_code=404, content={"error": "Not Found"})

# Eliminar el mount duplicado del final

# Eventos de Socket.io
@sio.event
async def connect(sid, environ, auth=None):
    print(f"Socket intentando conectar: {sid}")
    if auth and 'token' in auth:
        try:
            payload = jwt.decode(auth['token'], SECRET_KEY, algorithms=[ALGORITHM])
            user_id = payload.get("sub")
            if user_id:
                await sio.enter_room(sid, f"user_{user_id}")
                print(f"Socket {sid} unido a sala user_{user_id}")
                return True
        except JWTError:
            pass
    
    # Si no hay token o es inválido, permitimos la conexión pero no lo unimos a una sala privada
    # (El chat público o soporte podría necesitar la conexión)
    return True

@sio.event
async def disconnect(sid):
    print(f"Socket desconectado: {sid}")
