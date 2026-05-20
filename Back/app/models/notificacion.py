import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text, Boolean, ForeignKey
from app.database import Base

class Notificacion(Base):
    __tablename__ = "notificaciones"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("usuarios.id"), nullable=False, index=True)
    
    titulo = Column(String(100), nullable=False)
    mensaje = Column(Text, nullable=False)
    leida = Column(Boolean, default=False)
    
    tipo = Column(String(20), default="info") # info, success, warning, error
    
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Notificacion(id={self.id}, user_id={self.user_id}, leida={self.leida})>"
