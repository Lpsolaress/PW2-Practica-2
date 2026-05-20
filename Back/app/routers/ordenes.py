from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.dependencies import get_db, get_current_user, get_admin_user
from app.models.usuario import Usuario

router = APIRouter(prefix="/ordenes", tags=["ordenes"])

@router.get("")
def get_all_orders(admin: Usuario = Depends(get_admin_user)):
    return []

@router.get("/mis-ordenes")
def get_my_orders(current_user: Usuario = Depends(get_current_user)):
    return []

@router.post("")
def checkout(current_user: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    # Simular la creación de una orden real vaciando el carrito
    current_user.cart_data = "[]"
    db.commit()
    
    # Devolver un ID de orden ficticio con el formato que espera el front (_id)
    import uuid
    return {
        "_id": str(uuid.uuid4()),
        "mensaje": "Orden creada con éxito"
    }

@router.patch("/{order_id}/status")
def update_order_status(order_id: str, admin: Usuario = Depends(get_admin_user)):
    return {"mensaje": "Estado de orden actualizado"}
