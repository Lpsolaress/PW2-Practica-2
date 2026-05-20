from app.repositories.usuario_repository import UsuarioRepository
from app.models.usuario import Usuario
from app.schemas.usuario import UsuarioCreate, UsuarioUpdate
from app.exceptions import UsuarioNoEncontradoError, UsuarioYaExisteError
from app.services.security import get_password_hash

class UsuarioService:
    def __init__(self, usuario_repo: UsuarioRepository):
        self.usuario_repo = usuario_repo

    def obtener_todos(self) -> list[Usuario]:
        return self.usuario_repo.get_all()

    def obtener_por_id(self, usuario_id: str) -> Usuario:
        usuario = self.usuario_repo.get_by_id(usuario_id)
        if not usuario:
            raise UsuarioNoEncontradoError(f"Usuario con ID {usuario_id} no encontrado")
        return usuario

    def crear_usuario(self, usuario_data: UsuarioCreate) -> Usuario:
        if self.usuario_repo.get_by_email(usuario_data.email):
            raise UsuarioYaExisteError(f"El email {usuario_data.email} ya está registrado")
        
        if self.usuario_repo.get_by_username(usuario_data.username):
            raise UsuarioYaExisteError(f"El nombre de usuario {usuario_data.username} ya está en uso")

        nuevo_usuario = Usuario(
            username=usuario_data.username,
            email=usuario_data.email,
            hashed_password=get_password_hash(usuario_data.password),
            role=usuario_data.role
        )
        return self.usuario_repo.create(nuevo_usuario)

    def actualizar_usuario(self, usuario_id: str, usuario_data: UsuarioUpdate) -> Usuario:
        usuario = self.obtener_por_id(usuario_id)
        
        update_data = usuario_data.model_dump(exclude_unset=True)
        
        # Si se actualiza el password, hay que hashearlo
        if "password" in update_data:
            password = update_data.pop("password")
            usuario.hashed_password = get_password_hash(password)
            
        for key, value in update_data.items():
            setattr(usuario, key, value)
        
        self.usuario_repo.update()
        return usuario

    def eliminar_usuario(self, usuario_id: str) -> None:
        usuario = self.obtener_por_id(usuario_id)
        self.usuario_repo.delete(usuario)
