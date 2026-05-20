# Proyecto 2 - Gestión de Productos y Carrito

Este proyecto consiste en una aplicación web con un **Frontend** desarrollado en **Svelte 5** (con Vite) y un **Backend** construido con **Express.js** y **MongoDB**.

---

## 🚀 Instalación y Ejecución

### Requisitos Previos
*   [Node.js](https://nodejs.org/) (versión LTS recomendada)
*   [MongoDB](https://www.mongodb.com/) (Local o MongoDB Atlas)

### Pasos para la Instalación

1.  **Clonar el repositorio**:
    ```bash
    git clone https://github.com/Lpsolaress/PW2-Practica-1.git
    cd "PW-Proyecto 2"
    ```

2.  **Configurar Variables de Entorno (Backend)**:
    Crea un archivo `.env` dentro de la carpeta `backend/` con las siguientes configuraciones:
    ```dotenv
    PORT=3000
    MONGO_URI=mongodb://127.0.0.1:27017/productos
    JWT_SECRET=tu_secreto_seguro
    ```

3.  **Instalar dependencias globales/coordinador**:
    En la raíz del proyecto, ejecuta:
    ```bash
    npm install
    ```
    *(Instalará `concurrently` para ejecutar Frontend y Backend a la vez).*

4.  **Instalar dependencias del Backend**:
    ```bash
    cd backend && npm install
    ```

5.  **Instalar dependencias del Frontend**:
    ```bash
    cd ../frontend && npm install
    ```

### ▶️ Ejecución de la Aplicación

Para ejecutar ambos servidores (Backend y Frontend) simultáneamente con un solo comando:

1.  Asegúrate de estar en la **raíz del proyecto**.
2.  Ejecuta:
    ```bash
    npm run dev
    ```
    *   **Backend**: Correrá en el puerto configurado (usualmente 3000 o según `.env`).
    *   **Frontend**: Correrá en un entorno Vite (ej: `http://localhost:5173`).

---

## 🧩 Svelte 5 Runes

La aplicación utiliza las nuevas **Runes** de **Svelte 5** para la reactividad y gestión de datos. A continuación se detallan los runes empleados y sus casos de uso principales:

*   **`$state`**: define el estado reactivo.
    *   `frontend/src/state/app.svelte.js` (Estado global `app`).
    *   `SupportHubPage.svelte` y `ChatWidget.svelte` (Mensajes, conexiones socket).
    *   `ProductsPage.svelte` (Filtros, modales, estado de carga).
    *   `CartPage.svelte` (Promociones, procesos de pago).

*   **`$derived` / `$derived.by`**: reactividad basada en otros estados.
    *   `CartPage.svelte`: Cálculo de totales (`subtotal`, `tax`, `total`), conteo de ítems (`cartCount`), y sugerencias de productos.
    *   `ProductsPage.svelte`: Lista filtrada de productos (`productosFiltrados`) y límite de visualización.

*   **`$effect`**: manejo de efectos secundarios (side-effects).
    *   `App.svelte`: Verificación de tokens y carga inicial.
    *   `CartPage.svelte` y `ProductsPage.svelte`: Bloques para cargar datos desde la API cuando cambian ciertos parámetros o al montar el componente.

*   **`$props`**: paso de propiedades entre componentes.
    *   `NavBar.svelte`: Recibe la ruta actual (`currentPath`).
    *   `ProductModal.svelte`: Recibe el producto a visualizar/editar y la función de cierre (`onClose`).

---

## 🔌 Backend Endpoints y Roles

El Backend se organiza por módulos con rutas diferenciadas. Requieren autenticación mediante **JWT** (Header: `Authorization: Bearer <token>`).

### 🔑 Autenticación (`/auth`)
| Método | Endpoint | Rol Necesario | Descripción |
| :--- | :--- | :--- | :--- |
| `POST` | `/auth/registro` | **Público** | Registro de nuevos usuarios |
| `POST` | `/auth/login` | **Público** | Inicio de sesión |
| `GET` | `/auth/perfil` | Autenticado | Obtener datos del perfil actual |
| `PUT` | `/auth/perfil` | Autenticado | Actualizar perfil/imagen |
| `POST` | `/auth/direcciones` | Autenticado | Añadir dirección de envío |

### 📦 Productos (`/productos`)
| Método | Endpoint | Rol Necesario | Descripción |
| :--- | :--- | :--- | :--- |
| `GET` | `/productos` | **Público** | Listar todos los productos |
| `GET` | `/productos/:id`| **Público** | Ver detalle de un producto |
| `POST` | `/productos` | `administrador` | Crear un nuevo producto |
| `PUT` | `/productos/:id`| `administrador` | Editar un producto existente |
| `DELETE`| `/productos/:id`| `administrador` | Eliminar un producto |

### 🛒 Carrito o Cesta (`/carrito`)
*(Requieren Autenticación general)*
*   `GET /`: Obtener el carrito del usuario.
*   `POST /add`: Añadir producto.
*   `PATCH /item/:productId`: Cambiar cantidad.
*   `DELETE /item/:productId`: Quitar ítem.

### 🧾 Órdenes/Pedidos (`/ordenes`)
| Método | Endpoint | Rol Necesario | Descripción |
| :--- | :--- | :--- | :--- |
| `GET` | `/ordenes` | `administrador` | Listar todas las órdenes del sistema |
| `GET` | `/ordenes/mis-ordenes`| Autenticado | Listar historial propio de órdenes |
| `POST` | `/ordenes` | Autenticado | Checkout (Crear orden del carrito) |
| `PATCH`| `/ordenes/:id/status`| `administrador` | Actualizar estado (Pendiente, etc.) |

### 👥 Usuarios (`/usuarios`)
*   **Rol Requerido:** `administrador` para todos los endpoints.
*   `GET /`, `POST /`, `PUT /:id`, `DELETE /:id` para gestión administrativa de cuentas de usuario.

---

## 📌 Notas Adicionales
- Para consultar o previsualizar la base de datos de manera visual, se recomienda utilizar **MongoDB Compass**.
- El puerto `3000` debe estar libre para que el Chat y la API interactúen sin errores de CORS bloqueados.

---

## 🔗 Repositorio
- [PW2-Practica-1](https://github.com/Lpsolaress/PW2-Practica-1.git)
