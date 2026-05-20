import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Text, Boolean, DateTime
from app.database import Base

class Producto(Base):
    __tablename__ = "productos"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    nombre = Column(String(100), nullable=False)
    precio = Column(Float, nullable=False)
    descripcion = Column(Text, nullable=False)
    imagen = Column(String(255), nullable=True)
    categoria = Column(String(50), nullable=False, default="Otros")
    plataforma = Column(String(50), nullable=False, default="Otro")
    activo = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Producto(nombre={self.nombre}, precio={self.precio})>"
