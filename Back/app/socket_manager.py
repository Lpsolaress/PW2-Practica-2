import socketio

# Instancia global de Socket.io
sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')

async def emit_cart_update(user_id: str, cart_count: int):
    """
    Emite un evento de actualización de carrito a un usuario específico.
    """
    await sio.emit('cart_update', {"count": cart_count}, room=f"user_{user_id}")

async def emit_notification(user_id: str, message: str):
    """
    Emite una notificación a un usuario específico.
    """
    await sio.emit('notification', {"message": message}, room=f"user_{user_id}")
