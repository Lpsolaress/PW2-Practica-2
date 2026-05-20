import os
import time
import json
import uuid
from fastapi import APIRouter, Depends, UploadFile, File, Form, Body
from sqlalchemy.orm import Session
from app.dependencies import get_db, get_current_user
from app.schemas.auth import LoginRequest, RegistroRequest, TokenResponse, PerfilResponse
from app.services.auth_service import AuthService
from app.services.usuario_service import UsuarioService
from app.repositories.usuario_repository import UsuarioRepository
from app.models.usuario import Usuario
from app.schemas.usuario import UsuarioUpdate

router = APIRouter(prefix="/auth", tags=["auth"])

# Directorio de subidas absoluto
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
UPLOADS_DIR = os.path.join(BASE_DIR, "uploads")

@router.post("/login", response_model=TokenResponse)
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    repo = UsuarioRepository(db)
    service = AuthService(repo)
    
    response = service.login(login_data)
    return response

@router.post("/registro", response_model=TokenResponse)
def registro(registro_data: RegistroRequest, db: Session = Depends(get_db)):
    repo = UsuarioRepository(db)
    service = AuthService(repo)
    response = service.registro(registro_data)
    
    return response

@router.get("/perfil", response_model=PerfilResponse)
def get_perfil(current_user: Usuario = Depends(get_current_user)):
    return {"usuario": current_user}

@router.post("/direcciones")
async def add_address(
    data: dict = Body(...),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    addresses = json.loads(current_user.addresses_data or "[]")
    data["_id"] = str(uuid.uuid4())
    addresses.append(data)
    current_user.addresses_data = json.dumps(addresses)
    db.commit()
    return {"mensaje": "Dirección agregada", "addresses": addresses}

@router.delete("/direcciones/{address_id}")
async def delete_address(
    address_id: str,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    addresses = json.loads(current_user.addresses_data or "[]")
    addresses = [a for a in addresses if a.get("_id") != address_id]
    current_user.addresses_data = json.dumps(addresses)
    db.commit()
    return {"mensaje": "Dirección eliminada"}

@router.post("/metodos-pago")
async def add_payment_method(
    data: dict = Body(...),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    methods = json.loads(current_user.payment_methods_data or "[]")
    data["_id"] = str(uuid.uuid4())
    methods.append(data)
    current_user.payment_methods_data = json.dumps(methods)
    db.commit()
    return {"mensaje": "Método de pago agregado", "paymentMethods": methods}

@router.delete("/metodos-pago/{method_id}")
async def delete_payment_method(
    method_id: str,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    methods = json.loads(current_user.payment_methods_data or "[]")
    methods = [m for m in methods if m.get("_id") != method_id]
    current_user.payment_methods_data = json.dumps(methods)
    db.commit()
    return {"mensaje": "Método de pago eliminado"}

@router.put("/perfil", response_model=PerfilResponse)
async def update_perfil(
    username: str = Form(None),
    email: str = Form(None),
    foto: UploadFile = File(None),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    usuario_repo = UsuarioRepository(db)
    usuario_service = UsuarioService(usuario_repo)
    
    profile_picture = current_user.profile_picture
    
    if foto:
        if not os.path.exists(UPLOADS_DIR):
            os.makedirs(UPLOADS_DIR)
            
        ext = os.path.splitext(foto.filename)[1]
        # Formato: profile-{timestamp}{extension}
        filename = f"profile-{int(time.time() * 1000)}{ext}"
        file_path = os.path.join(UPLOADS_DIR, filename)
        
        with open(file_path, "wb") as buffer:
            content = await foto.read()
            buffer.write(content)
        
        profile_picture = f"/uploads/{filename}"

    update_data = UsuarioUpdate(
        username=username if username else current_user.username,
        email=email if email else current_user.email,
        profile_picture=profile_picture
    )
    
    updated_user = usuario_service.actualizar_usuario(current_user.id, update_data)
    return {"usuario": updated_user}
