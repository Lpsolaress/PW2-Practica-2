from sqlalchemy.orm import Session
from app.models.usuario import Usuario

class UsuarioRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, usuario_id: str) -> Usuario | None:
        return self.db.query(Usuario).filter(Usuario.id == usuario_id).first()

    def get_by_email(self, email: str) -> Usuario | None:
        return self.db.query(Usuario).filter(Usuario.email == email).first()

    def get_by_username(self, username: str) -> Usuario | None:
        return self.db.query(Usuario).filter(Usuario.username == username).first()

    def get_all(self) -> list[Usuario]:
        return self.db.query(Usuario).all()

    def create(self, usuario: Usuario) -> Usuario:
        self.db.add(usuario)
        self.db.commit()
        self.db.refresh(usuario)
        return usuario

    def update(self) -> None:
        self.db.commit()

    def delete(self, usuario: Usuario) -> None:
        self.db.delete(usuario)
        self.db.commit()
