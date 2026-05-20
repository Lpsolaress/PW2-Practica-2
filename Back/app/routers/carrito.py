import json
from fastapi import APIRouter, Depends, status, Body
from sqlalchemy.orm import Session
from app.dependencies import get_db, get_current_user
from app.models.usuario import Usuario
from app.models.producto import Producto
from app.repositories.usuario_repository import UsuarioRepository
from app.repositories.producto_repository import ProductoRepository
from app.schemas.carrito import CarritoResponse
from app.socket_manager import emit_cart_update

router = APIRouter(prefix="/carrito", tags=["carrito"])

@router.get("", response_model=CarritoResponse)
def get_carrito(current_user: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    # Parsear el carrito del usuario
    cart_items = json.loads(current_user.cart_data or "[]")
    
    # Enriquecer con datos de productos reales
    enriched_cart = []
    prod_repo = ProductoRepository(db)
    
    for item in cart_items:
        producto = prod_repo.get_by_id(item["productId"])
        if producto:
            enriched_cart.append({
                "product": producto,
                "quantity": item["quantity"]
            })
            
    return {"items": enriched_cart}

@router.post("/add")
async def add_to_cart(
    payload: dict = Body(...), 
    current_user: Usuario = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    product_id = payload.get("productId")
    quantity = payload.get("quantity", 1)
    
    if not product_id:
        return {"error": "Falta productId"}

    cart_items = json.loads(current_user.cart_data or "[]")
    
    # Ver si ya está en el carrito
    found = False
    for item in cart_items:
        if item["productId"] == product_id:
            item["quantity"] += quantity
            found = True
            break
    
    if not found:
        cart_items.append({"productId": product_id, "quantity": quantity})
    
    current_user.cart_data = json.dumps(cart_items)
    db.commit()
    
    # Emitir actualización en tiempo real
    total_items = sum(item["quantity"] for item in cart_items)
    await emit_cart_update(current_user.id, total_items)
    
    return {"mensaje": "Producto añadido", "count": len(cart_items)}

@router.patch("/item/{product_id}")
async def update_cart_item(
    product_id: str, 
    payload: dict = Body(...), 
    current_user: Usuario = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    quantity = payload.get("quantity")
    if quantity is None:
        return {"error": "Falta quantity"}

    cart_items = json.loads(current_user.cart_data or "[]")
    
    # Aseguramos que product_id sea string para la comparación
    product_id_str = str(product_id)
    
    new_cart = []
    found = False
    for item in cart_items:
        # Comparamos como strings para evitar fallos de tipos
        if str(item.get("productId")) == product_id_str:
            found = True
            if quantity > 0:
                item["quantity"] = int(quantity)
                new_cart.append(item)
            # Si quantity <= 0, no lo añadimos (se elimina)
        else:
            new_cart.append(item)
            
    if not found:
        # Si no se encontró el producto, no hacemos nada o devolvemos error
        return {"error": "Producto no encontrado en el carrito"}

    current_user.cart_data = json.dumps(new_cart)
    db.commit()
    
    # Emitir actualización en tiempo real
    total_items = sum(item["quantity"] for item in new_cart)
    await emit_cart_update(current_user.id, total_items)
    
    return {"mensaje": "Cantidad actualizada", "items": new_cart}

@router.delete("/item/{product_id}")
async def remove_from_cart(
    product_id: str, 
    current_user: Usuario = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    cart_items = json.loads(current_user.cart_data or "[]")
    product_id_str = str(product_id)
    
    new_cart = [item for item in cart_items if str(item.get("productId")) != product_id_str]
    
    current_user.cart_data = json.dumps(new_cart)
    db.commit()
    
    # Emitir actualización en tiempo real
    total_items = sum(item["quantity"] for item in new_cart)
    await emit_cart_update(current_user.id, total_items)
    
    return {"mensaje": "Producto eliminado", "items": new_cart}

@router.delete("")
async def clear_cart(current_user: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    current_user.cart_data = "[]"
    db.commit()
    
    # Emitir actualización en tiempo real
    await emit_cart_update(current_user.id, 0)
    
    return {"mensaje": "Carrito vaciado"}
