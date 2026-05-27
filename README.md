# Practica 2 - Gestion de Productos y Carrito (Python FastAPI)

Este proyecto consiste en una aplicacion web con un frontend desarrollado en Svelte 5 y un backend migrado a Python utilizando el framework FastAPI. El sistema permite la gestion de usuarios, autenticacion mediante JWT, administracion de productos y procesamiento de ordenes de compra.

---

## Instalacion y Ejecucion

### Requisitos Previos
* Python 3.11 o superior
* Node.js (version LTS recomendada)
* Entorno virtual de Python (recomendado)

### Pasos para la Instalacion

1. Configurar el Backend:
   Acceder a la carpeta del servidor y configurar el entorno:
   ```bash
   cd Back
   python3 -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. Configurar Variables de Entorno (Backend):
   Crear un archivo .env dentro de la carpeta Back/ con la siguiente configuracion basica:
   ```dotenv
   SECRET_KEY=una_clave_secreta_muy_larga_y_segura
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=10080
   DATABASE_URL=sqlite:///./app.db
   ```

3. Configurar el Frontend:
   Desde la raiz del proyecto, instalar las dependencias de la interfaz:
   ```bash
   cd frontend
   npm install
   ```

### Ejecucion de la Aplicacion

Para ejecutar el sistema completo, se deben iniciar ambos servicios:

1. Iniciar el Backend (desde la carpeta Back):
   ```bash
   uvicorn app.main:app --reload --port 3000
   ```
   El servidor estara disponible en http://localhost:3000 y la documentacion interactiva en http://localhost:3000/docs

2. Iniciar el Frontend (desde la carpeta frontend):
   ```bash
   npm run dev
   ```
   La aplicacion estara disponible en la direccion indicada por Vite (usualmente http://localhost:5173).

---

## Arquitectura del Sistema

El backend sigue una arquitectura limpia dividida en capas para facilitar el mantenimiento y la escalabilidad:

* Routers: Gestion de endpoints HTTP y validacion de entrada mediante Pydantic.
* Services: Logica de negocio pura, independiente del framework web.
* Repositories: Unica capa con acceso directo a la base de datos (SQLAlchemy).
* Models: Definicion de tablas y esquemas de base de datos.
* Schemas: Modelos de Pydantic para la serializacion y validacion de datos.

---

## Funcionalidades Principales

### Autenticacion y Usuarios
* Registro e inicio de sesion con hashing de contraseñas (bcrypt).
* Gestion de perfiles y autorizacion basada en roles (usuario y administrador).
* Proteccion de rutas mediante tokens JWT.

### Gestion de Productos
* CRUD completo de productos para administradores.
* Subida y almacenamiento de imagenes en el servidor.
* Listado y filtrado de productos para todos los usuarios.

### Carrito y Ordenes
* Gestion de persistencia del carrito de compras.
* Procesamiento de pedidos y almacenamiento en base de datos SQLite.
* Notificaciones en tiempo real mediante WebSockets (Socket.io).

---

## Notas de Desarrollo
* La base de datos se inicializa automaticamente al arrancar el servidor backend por primera vez.
* Se ha incluido un manejador global de errores para asegurar respuestas unificadas en formato JSON.
* La documentacion del uso de IA y analisis critico se encuentra en el archivo uso_ia.md.
