from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.exceptions import (
    BaseAppException,
    AuthError,
    PermisoDenegadoError,
    UsuarioNoEncontradoError,
    ProductoNoEncontradoError,
    UsuarioYaExisteError,
    CredencialesInvalidasError
)
import logging

logger = logging.getLogger(__name__)

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

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Manejador para errores de validación de Pydantic (422)."""
    errors = []
    for error in exc.errors():
        # Simplificar el formato del error para el frontend
        loc = " -> ".join(str(x) for x in error["loc"])
        msg = error["msg"]
        errors.append(f"{loc}: {msg}")
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Datos de entrada inválidos",
            "detalles": errors
        }
    )

async def generic_exception_handler(request: Request, exc: Exception):
    """Manejador para cualquier otra excepción no capturada (500)."""
    logger.error(f"Error no controlado: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": "Error interno del servidor"}
    )

def register_error_handlers(app):
    app.add_exception_handler(BaseAppException, app_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)
