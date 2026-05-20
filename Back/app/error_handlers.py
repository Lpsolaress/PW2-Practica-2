from fastapi import Request, status
from fastapi.responses import JSONResponse
from app.exceptions import (
    BaseAppException,
    AuthError,
    PermisoDenegadoError,
    UsuarioNoEncontradoError,
    ProductoNoEncontradoError,
    UsuarioYaExisteError,
    CredencialesInvalidasError
)

async def app_exception_handler(request: Request, exc: BaseAppException):
    status_code = status.HTTP_400_BAD_REQUEST
    
    if isinstance(exc, CredencialesInvalidasError):
        status_code = status.HTTP_401_UNAUTHORIZED
    elif isinstance(exc, AuthError):
        status_code = status.HTTP_401_UNAUTHORIZED
    elif isinstance(exc, PermisoDenegadoError):
        status_code = status.HTTP_403_FORBIDDEN
    elif isinstance(exc, (UsuarioNoEncontradoError, ProductoNoEncontradoError)):
        status_code = status.HTTP_404_NOT_FOUND
    elif isinstance(exc, UsuarioYaExisteError):
        status_code = status.HTTP_409_CONFLICT
        
    return JSONResponse(
        status_code=status_code,
        content={"error": exc.message}
    )

def register_error_handlers(app):
    app.add_exception_handler(BaseAppException, app_exception_handler)
