class BaseAppException(Exception):
    """Clase base para todas las excepciones de la aplicación."""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

class AuthError(BaseAppException):
    """Excepción para errores de autenticación."""
    pass

class PermisoDenegadoError(BaseAppException):
    """Excepción para errores de autorización (403)."""
    pass

class UsuarioYaExisteError(BaseAppException):
    """Excepción cuando el usuario o email ya están registrados."""
    pass

class UsuarioNoEncontradoError(BaseAppException):
    """Excepción cuando un usuario no existe."""
    pass

class ProductoNoEncontradoError(BaseAppException):
    """Excepción cuando un producto no existe."""
    pass

class CredencialesInvalidasError(AuthError):
    """Excepción para login fallido."""
    def __init__(self):
        super().__init__("Email o contraseña incorrectos")
