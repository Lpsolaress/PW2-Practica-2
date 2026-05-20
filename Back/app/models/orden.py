import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text, Float, ForeignKey
from app.database import Base

class Orden(Base):
    __tablename__ = "ordenes"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("usuarios.id"), nullable=False)
    
    # Almacenamos el detalle de la orden como JSON string
    items_data = Column(Text, nullable=False) # List of {productId, quantity, price, name}
    
    total = Column(Float, nullable=False)
    status = Column(String(20), nullable=False, default="pendiente")
    
    # Datos de envío y pago en el momento de la compra
    address_data = Column(Text, nullable=False) # JSON of the selected address
    payment_data = Column(Text, nullable=False) # JSON of the selected payment method
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Orden(id={self.id}, user_id={self.user_id}, total={self.total}, status={self.status})>"
