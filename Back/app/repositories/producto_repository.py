from sqlalchemy.orm import Session
from app.models.producto import Producto

class ProductoRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, producto_id: str) -> Producto | None:
        return self.db.query(Producto).filter(Producto.id == producto_id).first()

    def get_all(self) -> list[Producto]:
        return self.db.query(Producto).all()

    def create(self, producto: Producto) -> Producto:
        self.db.add(producto)
        self.db.commit()
        self.db.refresh(producto)
        return producto

    def update(self) -> None:
        self.db.commit()

    def delete(self, producto: Producto) -> None:
        self.db.delete(producto)
        self.db.commit()
