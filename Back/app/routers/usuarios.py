from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.dependencies import get_db, get_admin_user
from app.schemas.usuario import UsuarioCreate, UsuarioUpdate, UsuarioResponse
from app.services.usuario_service import UsuarioService
from app.repositories.usuario_repository import UsuarioRepository
from app.models.usuario import Usuario

router = APIRouter(prefix="/usuarios", tags=["usuarios"])

@router.get("", response_model=List[UsuarioResponse])
def get_usuarios(
    db: Session = Depends(get_db),
    admin: Usuario = Depends(get_admin_user)
):
    repo = UsuarioRepository(db)
    service = UsuarioService(repo)
    return service.obtener_todos()

@router.get("/{usuario_id}", response_model=UsuarioResponse)
def get_usuario(
    usuario_id: str,
    db: Session = Depends(get_db),
    admin: Usuario = Depends(get_admin_user)
):
    repo = UsuarioRepository(db)
    service = UsuarioService(repo)
    return service.obtener_por_id(usuario_id)

@router.post("", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
def create_usuario(
    usuario_in: UsuarioCreate,
    db: Session = Depends(get_db),
    admin: Usuario = Depends(get_admin_user)
):
    repo = UsuarioRepository(db)
    service = UsuarioService(repo)
    return service.crear_usuario(usuario_in)

@router.put("/{usuario_id}", response_model=UsuarioResponse)
def update_usuario(
    usuario_id: str,
    usuario_in: UsuarioUpdate,
    db: Session = Depends(get_db),
    admin: Usuario = Depends(get_admin_user)
):
    repo = UsuarioRepository(db)
    service = UsuarioService(repo)
    return service.actualizar_usuario(usuario_id, usuario_in)

@router.delete("/{usuario_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_usuario(
    usuario_id: str,
    db: Session = Depends(get_db),
    admin: Usuario = Depends(get_admin_user)
):
    repo = UsuarioRepository(db)
    service = UsuarioService(repo)
    service.eliminar_usuario(usuario_id)
    return None
