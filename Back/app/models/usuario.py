import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text
from app.database import Base

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default="usuario")
    profile_picture = Column(String(255), nullable=True, default="")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Campo para almacenar el carrito como JSON string
    cart_data = Column(Text, nullable=True, default="[]")
    
    # Campos para direcciones y métodos de pago
    addresses_data = Column(Text, nullable=True, default="[]")
    payment_methods_data = Column(Text, nullable=True, default="[]")

    def __repr__(self):
        return f"<Usuario(username={self.username}, email={self.email}, role={self.role})>"
