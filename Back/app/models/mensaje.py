import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text, ForeignKey
from app.database import Base

class Mensaje(Base):
    __tablename__ = "mensajes"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # El user_id es el cliente (la "sala" de chat)
    user_id = Column(String(36), ForeignKey("usuarios.id"), nullable=False, index=True)
    
    # El sender_id es quien escribe (puede ser el cliente o un admin)
    sender_id = Column(String(36), ForeignKey("usuarios.id"), nullable=False)
    
    text = Column(Text, nullable=True)
    image_url = Column(String(255), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Mensaje(id={self.id}, user_id={self.user_id}, sender_id={self.sender_id})>"
