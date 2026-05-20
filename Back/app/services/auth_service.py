from app.repositories.usuario_repository import UsuarioRepository
from app.models.usuario import Usuario
from app.schemas.auth import LoginRequest, RegistroRequest, TokenResponse
from app.exceptions import CredencialesInvalidasError, UsuarioYaExisteError
from app.services.security import verify_password, get_password_hash, create_access_token

class AuthService:
    def __init__(self, usuario_repo: UsuarioRepository):
        self.usuario_repo = usuario_repo

    def login(self, login_data: LoginRequest) -> TokenResponse:
        usuario = self.usuario_repo.get_by_email(login_data.email)
        if not usuario or not verify_password(login_data.password, usuario.hashed_password):
            raise CredencialesInvalidasError()

        token = create_access_token(data={"sub": usuario.id})
        
        return TokenResponse(
            token=token,
            usuario=usuario, # Pydantic se encarga del mapeo a UsuarioSimpleResponse
            mensaje="Inicio de sesión exitoso"
        )

    def registro(self, registro_data: RegistroRequest) -> TokenResponse:
        if self.usuario_repo.get_by_email(registro_data.email):
            raise UsuarioYaExisteError(f"El email {registro_data.email} ya está registrado")
        
        if self.usuario_repo.get_by_username(registro_data.username):
            raise UsuarioYaExisteError(f"El nombre de usuario {registro_data.username} ya está en uso")

        nuevo_usuario = Usuario(
            username=registro_data.username,
            email=registro_data.email,
            hashed_password=get_password_hash(registro_data.password),
            role=registro_data.role
        )
        
        usuario_creado = self.usuario_repo.create(nuevo_usuario)
        token = create_access_token(data={"sub": usuario_creado.id})

        return TokenResponse(
            token=token,
            usuario=usuario_creado,
            mensaje="Usuario registrado exitosamente"
        )
