from app.repositories.producto_repository import ProductoRepository
from app.models.producto import Producto
from app.schemas.producto import ProductoCreate, ProductoUpdate
from app.exceptions import ProductoNoEncontradoError

class ProductoService:
    def __init__(self, producto_repo: ProductoRepository):
        self.producto_repo = producto_repo

    def obtener_todos(self) -> list[Producto]:
        return self.producto_repo.get_all()

    def obtener_por_id(self, producto_id: str) -> Producto:
        producto = self.producto_repo.get_by_id(producto_id)
        if not producto:
            raise ProductoNoEncontradoError(f"Producto con ID {producto_id} no encontrado")
        return producto

    def crear_producto(self, producto_data: ProductoCreate, imagen_url: str | None = None) -> Producto:
        nuevo_producto = Producto(
            nombre=producto_data.nombre,
            precio=producto_data.precio,
            descripcion=producto_data.descripcion,
            categoria=producto_data.categoria,
            plataforma=producto_data.plataforma,
            activo=producto_data.activo,
            imagen=imagen_url
        )
        return self.producto_repo.create(nuevo_producto)

    def actualizar_producto(self, producto_id: str, producto_data: ProductoUpdate) -> Producto:
        producto = self.obtener_por_id(producto_id)
        
        update_data = producto_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(producto, key, value)
        
        self.producto_repo.update()
        return producto

    def eliminar_producto(self, producto_id: str) -> None:
        producto = self.obtener_por_id(producto_id)
        self.producto_repo.delete(producto)
