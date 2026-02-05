# Backend - Sistema de Facturación Electrónica

##  Inicio Rápido

### 1. Requisitos Previos
- Python 3.11+
- PostgreSQL 15+
- Base de datos `richard_db` creada

### 2. Instalación

```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

### 3. Configurar Variables de Entorno

Crear archivo `.env` basado en `.env.example`:

```env
FLASK_ENV=development
SECRET_KEY=tu-clave-secreta-aqui
JWT_SECRET_KEY=tu-jwt-secret-key-aqui

POSTGRES_USER=postgres
POSTGRES_PASSWORD=admin
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=richard_db

# Generar con: python -c "import base64, os; print(base64.b64encode(os.urandom(32)).decode())"
AES_MASTER_KEY=tu-clave-aes-base64-aqui
```

### 4. Inicializar Base de Datos

```bash
python init_db.py
```

Esto creará:
-  Todas las tablas
-  Usuario admin (username: `admin`, password: `Admin123!`)
-  Configuraciones iniciales

### 5. Ejecutar Servidor

```bash
python app.py
```

Servidor corriendo en: http://localhost:5000

---

##  Documentación de la API

### Autenticación (`/api/v1/auth`)

#### POST /api/v1/auth/login
Iniciar sesión

**Request:**
```json
{
  "username": "admin",
  "password": "Admin123!"
}
```

**Response (200):**
```json
{
  "success": true,
  "message": "Login exitoso",
  "data": {
    "token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "user": {
      "id": 1,
      "username": "admin",
      "email": "admin@facturasegura.com",
      "nombres": "Administrador",
      "apellidos": "Sistema",
      "rol": "ADMIN",
      "activo": true
    }
  }
}
```

#### GET /api/v1/auth/me
Obtener usuario actual (requiere token)

**Headers:**
```
Authorization: Bearer <token>
```

#### POST /api/v1/auth/logout
Cerrar sesión (requiere token)

---

### Usuarios (`/api/v1/users`) - Solo ADMIN

#### GET /api/v1/users
Listar usuarios con paginación

**Query Params:**
- `rol`: Filtrar por rol
- `activo`: true/false
- `page`: Número de página (default: 1)
- `limit`: Registros por página (default: 10)

**Response (200):**
```json
{
  "success": true,
  "data": {
    "users": [...],
    "pagination": {
      "page": 1,
      "limit": 10,
      "total": 5,
      "pages": 1
    }
  }
}
```

#### POST /api/v1/users
Crear nuevo usuario

**Request:**
```json
{
  "username": "usuario1",
  "password": "Password123!",
  "nombres": "Juan",
  "apellidos": "Pérez",
  "email": "juan@example.com",
  "rol": "FACTURADOR"
}
```

**Roles disponibles:**
- `ADMIN`: Administrador del sistema
- `FACTURADOR`: Creación de facturas
- `CONTADOR`: Consultas y reportes
- `AUDITOR`: Solo lectura de auditoría

#### PUT /api/v1/users/:id
Actualizar usuario

**Request (todos opcionales):**
```json
{
  "email": "nuevo@email.com",
  "nombres": "Juan Carlos",
  "rol": "CONTADOR",
  "activo": false,
  "password": "NuevaPassword123!"
}
```

#### DELETE /api/v1/users/:id
Eliminar usuario (soft delete - solo desactiva)

---

### Clientes (`/api/v1/clientes`)

#### GET /api/v1/clientes
Listar clientes (datos descifrados)

**Response:**
```json
{
  "success": true,
  "data": {
    "clientes": [
      {
        "id": 1,
        "tipo_identificacion": "CEDULA",
        "identificacion": "1234567890",
        "nombres": "María",
        "apellidos": "González",
        "direccion": "Av. Principal 123",
        "telefono": "0998765432",
        "email": "maria@example.com",
        "activo": true
      }
    ],
    "pagination": {...}
  }
}
```

#### POST /api/v1/clientes
Crear cliente (cifra datos sensibles automáticamente)

**Request:**
```json
{
  "tipo_identificacion": "CEDULA",
  "identificacion": "1234567890",
  "nombres": "María",
  "apellidos": "González",
  "direccion": "Av. Principal 123",
  "telefono": "0998765432",
  "email": "maria@example.com"
}
```

**Tipos de identificación:**
- `CEDULA`: 10 dígitos
- `RUC`: 13 dígitos (incluir `razon_social`)
- `PASAPORTE`: Alfanumérico

#### PUT /api/v1/clientes/:id
Actualizar cliente

#### DELETE /api/v1/clientes/:id
Eliminar cliente (soft delete)

---

##  Seguridad

### Criptografía Implementada

1. **Bcrypt** - Contraseñas
   - 12 rounds
   - Salt automático

2. **AES-256-GCM** - Datos sensibles de clientes
   - Nombres, apellidos, dirección, teléfono, email
   - IV aleatorio por registro
   - Tag de autenticación

3. **RSA-2048** - Firmas digitales (facturas)
   - PSS padding
   - SHA-256

4. **SHA-256** - Integridad de documentos

5. **JWT** - Autenticación de sesiones
   - Expira en 8 horas
   - Incluye rol y datos básicos

### Auditoría

Todos los cambios se registran en `audit_log`:
- Usuario que realizó la acción
- Timestamp
- Tipo de acción (CREATE, UPDATE, DELETE, LOGIN, etc.)
- Datos antes y después
- IP y User-Agent
- Resultado (EXITO/ERROR)

---

##  Correcciones Aplicadas vs Proyecto Principal

### Problemas Identificados y Solucionados:

1. ** Usuarios no se listaban**
   - Causa: Estructura de respuesta inconsistente
   - Solución: `data.users` siempre devuelve array, nunca undefined

2. ** No se podían crear usuarios**
   - Causa: Validación incorrecta de campos requeridos
   - Solución: Validación explícita de todos los campos obligatorios

3. **  No se podían editar usuarios**
   - Causa: No se enviaban datos correctamente al backend
   - Solución: Endpoint PUT acepta campos parciales correctamente

4. ** No se podían eliminar usuarios**
   - Causa: Soft delete no implementado correctamente
   - Solución: `AuthService.delete_user()` hace soft delete apropiadamente

5. ** Respuestas inconsistentes**
   - Causa: Algunas rutas devolvían `{data: {...}}` y otras `{...}`
   - Solución: TODAS las rutas devuelven `{success, message, data}`

6. ** Errores no se mostraban**
   - Causa: Manejo de errores incompleto
   - Solución: Try-catch en todas las rutas con logs detallados

---

##  Pruebas

### Probar Login
```bash
curl -X POST http://localhost:5000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"Admin123!"}'
```

### Probar Crear Usuario (requiere token de admin)
```bash
curl -X POST http://localhost:5000/api/v1/users \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <TOKEN>" \
  -d '{
    "username": "usuario1",
    "password": "Pass123!",
    "nombres": "Juan",
    "apellidos": "Pérez",
    "email": "juan@example.com",
    "rol": "FACTURADOR"
  }'
```

---

##  Estructura del Proyecto

```
Semana3_Backend/
├── app.py                 # Aplicación principal
├── config.py              # Configuración
├── init_db.py            # Inicialización de BD
├── requirements.txt       # Dependencias
├── .env.example          # Ejemplo de variables de entorno
├── models/               # Modelos SQLAlchemy
│   ├── base.py
│   ├── user.py
│   ├── empresa.py
│   ├── cliente.py
│   ├── factura.py
│   ├── audit_log.py
│   └── configuracion.py
├── routes/               # Blueprints de rutas
│   ├── auth_routes.py
│   ├── user_routes.py
│   └── cliente_routes.py
└── services/             # Lógica de negocio
    ├── auth_service.py
    └── crypto_service.py
```

---

##  Troubleshooting

### Error: "AES master key debe ser de 32 bytes"
Generar clave válida:
```bash
python -c "import base64, os; print(base64.b64encode(os.urandom(32)).decode())"
```

### Error: "CORS policy"
Verificar que `CORS_ORIGINS` en `.env` incluye la URL del frontend

### Error: "Token inválido"
El token expira en 8 horas. Hacer login nuevamente.

### Error: "Usuario ya existe"
El username y email deben ser únicos

---
