import os
import time
from typing import List
from fastapi import APIRouter, Depends, UploadFile, File, Form, status
from sqlalchemy.orm import Session
from app.dependencies import get_db, get_admin_user
from app.schemas.producto import ProductoCreate, ProductoUpdate, ProductoResponse
from app.services.producto_service import ProductoService
from app.repositories.producto_repository import ProductoRepository
from app.models.usuario import Usuario

router = APIRouter(prefix="/productos", tags=["productos"])

# Directorio de subidas absoluto
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
UPLOADS_DIR = os.path.join(BASE_DIR, "uploads")

@router.get("", response_model=List[ProductoResponse])
def get_productos(db: Session = Depends(get_db)):
    repo = ProductoRepository(db)
    service = ProductoService(repo)
    return service.obtener_todos()

@router.get("/{producto_id}", response_model=ProductoResponse)
def get_producto(producto_id: str, db: Session = Depends(get_db)):
    repo = ProductoRepository(db)
    service = ProductoService(repo)
    return service.obtener_por_id(producto_id)

@router.post("", response_model=ProductoResponse, status_code=status.HTTP_201_CREATED)
async def create_producto(
    nombre: str = Form(...),
    precio: float = Form(...),
    descripcion: str = Form(...),
    categoria: str = Form("Otros"),
    plataforma: str = Form("Otro"),
    activo: bool = Form(True),
    imagen: UploadFile = File(None),
    db: Session = Depends(get_db),
    admin: Usuario = Depends(get_admin_user)
):
    repo = ProductoRepository(db)
    service = ProductoService(repo)
    
    imagen_url = None
    if imagen:
        if not os.path.exists(UPLOADS_DIR):
            os.makedirs(UPLOADS_DIR)
        
        ext = os.path.splitext(imagen.filename)[1]
        filename = f"{int(time.time() * 1000)}{ext}"
        file_path = os.path.join(UPLOADS_DIR, filename)
        
        with open(file_path, "wb") as buffer:
            content = await imagen.read()
            buffer.write(content)
        
        imagen_url = f"/uploads/{filename}"

    producto_in = ProductoCreate(
        nombre=nombre,
        precio=precio,
        descripcion=descripcion,
        categoria=categoria,
        plataforma=plataforma,
        activo=activo
    )
    
    return service.crear_producto(producto_in, imagen_url=imagen_url)

@router.put("/{producto_id}", response_model=ProductoResponse)
async def update_producto(
    producto_id: str,
    nombre: str = Form(None),
    precio: float = Form(None),
    descripcion: str = Form(None),
    categoria: str = Form(None),
    plataforma: str = Form(None),
    activo: bool = Form(None),
    imagen: UploadFile = File(None),
    db: Session = Depends(get_db),
    admin: Usuario = Depends(get_admin_user)
):
    repo = ProductoRepository(db)
    service = ProductoService(repo)
    
    producto = service.obtener_por_id(producto_id)
    imagen_url = producto.imagen
    
    if imagen:
        if not os.path.exists(UPLOADS_DIR):
            os.makedirs(UPLOADS_DIR)
            
        ext = os.path.splitext(imagen.filename)[1]
        filename = f"{int(time.time() * 1000)}{ext}"
        file_path = os.path.join(UPLOADS_DIR, filename)
        
        with open(file_path, "wb") as buffer:
            content = await imagen.read()
            buffer.write(content)
        
        imagen_url = f"/uploads/{filename}"

    producto_update = ProductoUpdate(
        nombre=nombre,
        precio=precio,
        descripcion=descripcion,
        categoria=categoria,
        plataforma=plataforma,
        activo=activo,
        imagen=imagen_url
    )
    
    return service.actualizar_producto(producto_id, producto_update)

@router.delete("/{producto_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_producto(
    producto_id: str, 
    db: Session = Depends(get_db),
    admin: Usuario = Depends(get_admin_user)
):
    repo = ProductoRepository(db)
    service = ProductoService(repo)
    service.eliminar_producto(producto_id)
    return None
