# Registro del Uso de IA en el Desarrollo

Este documento detalla el uso profesional y reflexivo de herramientas de IA durante la migración del backend de Node.js/Express a Python/FastAPI para la Práctica 2.

## 1. Registro de prompts e iteraciones

Para la construcción del backend, se utilizaron prompts estructurados que seguían la arquitectura de capas (Routers → Services → Repositories → Models).

### Prompts clave

**Configuración de la Arquitectura en Capas (Repositorio):**
> "Crea app/repositories/usuario_repository.py con una clase UsuarioRepository que recibe una sesión SQLAlchemy (Session) en su constructor y expone métodos CRUD básicos. No incluyas lógica de negocio, solo acceso a datos."

**Configuración de JWT y Seguridad:**
> "Crea app/services/auth_service.py con clase AuthService. Dependencias: passlib[bcrypt] para hashing y python-jose para JWT. Métodos para login, registro y validación de tokens. Los errores deben ser excepciones personalizadas del dominio."

### Refinamiento de Prompts

Cuando el primer resultado no cumplía con los requisitos técnicos o de compatibilidad, se procedió a refinar las instrucciones.

**Ejemplo de refinamiento (Serialización JSON):**
*   **Problema**: El primer esquema Pydantic generaba el campo `id`, pero el frontend Svelte esperaba `_id` y camelCase para las fechas (`createdAt`).
*   **Prompt de refinamiento**: 
    > "El frontend en Svelte accede a los productos como producto._id. Modifica ProductoResponse para que el campo id se serialice como '_id' en el JSON. Además, los campos created_at y updated_at deben salir como createdAt y updatedAt. Usa Field(serialization_alias=...) y ConfigDict(populate_by_name=True)."

---

## 2. Análisis Crítico

### Error/Alucinación Documentada: Identificadores Numéricos vs. UUID

Durante la generación de los **Modelos ORM**, la IA cometió un error común al sugerir claves primarias autoincrementales de tipo entero.

**Descripción del error:**
La IA propuso inicialmente:
```python
id = Column(Integer, primary_key=True)
```

**Por qué era incorrecto:**
1.  **Incompatibilidad con el Frontend**: El frontend ya estaba desarrollado esperando IDs de tipo string (compatibles con MongoDB ObjectId). Cambiar a enteros habría roto toda la lógica de navegación y tipado en Svelte.
2.  **Seguridad y Escalabilidad**: En sistemas distribuidos o APIs públicas, exponer IDs secuenciales (`/usuarios/1`, `/usuarios/2`) es una mala práctica de seguridad (Enumeración de Recursos).

**Corrección Manual:**
Se intervino manualmente para forzar el uso de UUIDs v4 como strings, asegurando la compatibilidad total sin modificar el frontend:
```python
import uuid
# ...
id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
```

### Hallucinación en la Separación de Responsabilidades

**Descripción del error:**
Al generar el **Router de Autenticación**, la IA intentó incluir la lógica de hashing de contraseñas y la firma del JWT directamente dentro de la función del endpoint del router.

**Por qué era incorrecto:**
Violaba el principio de **Arquitectura en Capas** definido en las reglas del proyecto. Los routers deben limitarse a gestionar la petición HTTP y delegar la lógica de negocio al `Service`. Mezclar estas responsabilidades dificulta las pruebas unitarias y el mantenimiento.

**Corrección Manual:**
Se refactorizó el código para mover toda la lógica criptográfica al `AuthService`, dejando el router como un simple mediador que inyecta el servicio mediante dependencias de FastAPI.

### Mejora en el Manejo de Errores Estructurados

**Descripción de la mejora:**
La IA inicialmente solo manejaba excepciones de negocio. Sin embargo, los errores de validación de Pydantic (422) y los errores internos (500) se devolvían con el formato por defecto del framework, rompiendo la uniformidad de la API.

**Corrección Manual:**
Se implementaron manejadores globales específicos en `error_handlers.py` para `RequestValidationError` y `Exception` genérica. Esto asegura que *todas* las respuestas de error de la API sigan el mismo esquema JSON: `{"error": "mensaje", "detalles": [...]}`, cumpliendo con los estándares de calidad profesional exigidos.
