from fastapi import APIRouter, Depends
from app.dependencies import get_current_user
from app.models.usuario import Usuario

router = APIRouter(prefix="/notificaciones", tags=["notificaciones"])

@router.get("")
def get_notifications(current_user: Usuario = Depends(get_current_user)):
    return []

@router.patch("/{notif_id}/leida")
def mark_as_read(notif_id: str, current_user: Usuario = Depends(get_current_user)):
    return {"mensaje": "Notificación marcada como leída"}

@router.patch("/leer-todas")
def read_all(current_user: Usuario = Depends(get_current_user)):
    return {"mensaje": "Todas las notificaciones leídas"}

@router.delete("/{notif_id}")
def delete_notification(notif_id: str, current_user: Usuario = Depends(get_current_user)):
    return {"mensaje": "Notificación eliminada"}
