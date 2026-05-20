# Nuba Store Backend (FastAPI)

Este es el backend desarrollado en Python con FastAPI para la Práctica 2, que reemplaza al backend original en Node.js/Express.

## Instalación y ejecución

1. **Requisitos**: Python 3.11+
2. **Crear entorno virtual**:
   ```bash
   # Linux/Mac
   python3 -m venv venv && source venv/bin/activate
   # Windows
   python -m venv venv && venv\Scripts\activate
   ```
3. **Instalar dependencias**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Configuración**:
   - Copia `.env.example` a `.env`.
   - Asegúrate de configurar una `SECRET_KEY` segura.
5. **Ejecutar**:
   ```bash
   uvicorn app.main:app --reload --port 3000
   ```

## Endpoints principales

| Endpoint | Método | Autenticación | Descripción |
| :--- | :--- | :--- | :--- |
| `/auth/login` | `POST` | Pública | Iniciar sesión y obtener token JWT |
| `/auth/registro` | `POST` | Pública | Registrar un nuevo usuario |
| `/auth/perfil` | `GET` | Usuario | Obtener datos del perfil actual |
| `/auth/perfil` | `PUT` | Usuario | Actualizar perfil e imagen |
| `/productos` | `GET` | Pública | Listar todos los productos |
| `/productos/{id}` | `GET` | Pública | Ver detalle de un producto |
| `/productos` | `POST` | Administrador | Crear nuevo producto (multipart/form-data) |
| `/productos/{id}` | `PUT` | Administrador | Editar producto (multipart/form-data) |
| `/productos/{id}` | `DELETE` | Administrador | Eliminar un producto |
| `/usuarios` | `GET` | Administrador | Listar todos los usuarios |
| `/usuarios/{id}` | `GET` | Administrador | Ver detalle de un usuario |
| `/usuarios` | `POST` | Administrador | Crear usuario manualmente |
| `/usuarios/{id}` | `PUT` | Administrador | Editar datos de un usuario |
| `/usuarios/{id}` | `DELETE` | Administrador | Eliminar un usuario |

## Roles

- **usuario**: Puede ver productos, gestionar su carrito (próximamente) y ver/editar su propio perfil.
- **administrador**: Posee permisos totales para el CRUD de productos y la gestión de todos los usuarios del sistema.

## Documentación Interactiva

Una vez iniciado el servidor, puedes acceder a la documentación interactiva (Swagger UI) en:
[http://localhost:3000/docs](http://localhost:3000/docs)
