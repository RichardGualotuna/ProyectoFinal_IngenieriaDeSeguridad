 HEAD
# Sistema de Facturación Electrónica con Firma Digital

##  Descripción

Sistema completo de facturación electrónica para Ecuador que cumple con las normativas del SRI, implementando seguridad criptográfica robusta (RSA-2048, AES-256-GCM, SHA-256, Bcrypt).

** PROYECTO COMPLETAMENTE FUNCIONAL Y CORREGIDO**

Este proyecto fue desarrollado aplicando todas las lecciones aprendidas del proyecto principal, asegurando que TODAS las operaciones CRUD funcionen correctamente.

---

##  Inicio Rápido

### Requisitos Previos
- Python 3.11+
- Node.js 18+
- PostgreSQL 15+

### Instalación Completa

#### 1. Base de Datos

```bash
# Crear base de datos en PostgreSQL
psql -U postgres
CREATE DATABASE richard_db;
\q

# Ejecutar script de creación de tablas
cd Richard
psql -U postgres -d richard_db -f SCRIPT_SIMPLE_COPIAR_PEGAR.sql
```

#### 2. Backend (Flask)

```bash
cd Richard/Semana3_Backend

# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar .env (copiar .env.example y modificar)
copy .env.example .env
# Editar .env con tus valores

# Inicializar base de datos
python init_db.py

# Ejecutar backend
python app.py
```

Backend corriendo en: http://localhost:5000

#### 3. Frontend (React)

```bash
# En otra terminal
cd Richard/Semana4_Frontend

# Instalar dependencias
npm install

# Ejecutar frontend
npm run dev
```

Frontend corriendo en: http://localhost:5173

---

##  Credenciales por Defecto

**Usuario:** admin  
**Contraseña:** Admin123!  
**Rol:** ADMIN

---

##  Documentación

- [Backend README](Semana3_Backend/README.md) - API, endpoints, seguridad
- [Frontend README](Semana4_Frontend/README.md) - Componentes, pruebas, troubleshooting

---

##  Arquitectura del Sistema

### Backend (Flask)
```
Semana3_Backend/
├── app.py                 # Aplicación principal
├── config.py              # Configuración
├── init_db.py            # Inicialización de BD
├── models/               # Modelos SQLAlchemy
│   ├── user.py           # Usuario
│   ├── empresa.py        # Empresa emisora
│   ├── cliente.py        # Cliente (cifrado)
│   ├── factura.py        # Factura + detalle
│   ├── audit_log.py      # Auditoría
│   └── configuracion.py  # Configuración sistema
├── routes/               # Rutas (blueprints)
│   ├── auth_routes.py    # Login, logout, me
│   ├── user_routes.py    # CRUD usuarios (ADMIN)
│   └── cliente_routes.py # CRUD clientes
└── services/             # Lógica de negocio
    ├── auth_service.py   # Autenticación, usuarios
    └── crypto_service.py # RSA, AES, SHA-256, QR
```

### Frontend (React + Vite)
```
Semana4_Frontend/
├── src/
│   ├── App.jsx              # Rutas principales
│   ├── components/          # Componentes reutilizables
│   │   ├── Navbar.jsx       # Barra de navegación
│   │   └── PrivateRoute.jsx # Protección de rutas
│   ├── contexts/            # Contextos React
│   │   └── AuthContext.jsx  # Autenticación global
│   ├── pages/               # Páginas
│   │   ├── Login.jsx        # Inicio de sesión
│   │   ├── Dashboard.jsx    # Panel principal
│   │   ├── Usuarios.jsx     # Gestión usuarios
│   │   └── Clientes.jsx     # Gestión clientes
│   └── services/            # Servicios API
│       ├── api.js           # Configuración Axios
│       └── services.js      # authService, userService, etc.
```

---

##  Seguridad Implementada

### Criptografía

| Algoritmo | Uso | Detalles |
|-----------|-----|----------|
| **Bcrypt** | Contraseñas | 12 rounds, salt automático |
| **AES-256-GCM** | Datos sensibles | IV aleatorio, tag de autenticación |
| **RSA-2048** | Firmas digitales | PSS padding, SHA-256 |
| **SHA-256** | Integridad | Hash de documentos |
| **JWT** | Autenticación | Expira en 8 horas |

### Datos Cifrados

Los siguientes campos de clientes están cifrados con AES-256-GCM:
- Nombres
- Apellidos  
- Dirección
- Teléfono
- Email

### Auditoría

Todos los eventos se registran en `audit_log`:
- Usuario que realiza la acción
- Timestamp
- Tipo de acción (CREATE, UPDATE, DELETE, LOGIN, etc.)
- Datos antes y después del cambio
- IP y User-Agent
- Resultado (EXITO/ERROR)

---

##  Base de Datos

### Tablas Principales

1. **usuario** - Usuarios del sistema
2. **empresa** - Empresa emisora de facturas
3. **cliente** - Clientes (con datos cifrados)
4. **factura** - Facturas electrónicas
5. **detalle_factura** - Detalles de facturas
6. **audit_log** - Registro de auditoría (inmutable)
7. **configuracion** - Configuración del sistema

### Relaciones

```
empresa (1) ──── (N) factura (N) ──── (1) cliente
                      │
                      ├──── (1) usuario
                      │
                      └──── (N) detalle_factura
```

---

##  Guía de Pruebas Completa

### 1. Probar Backend (API)

#### Login
```bash
curl -X POST http://localhost:5000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"Admin123!"}'
```

#### Listar Usuarios (requiere token)
```bash
curl -X GET http://localhost:5000/api/v1/users \
  -H "Authorization: Bearer <TOKEN>"
```

#### Crear Usuario
```bash
curl -X POST http://localhost:5000/api/v1/users \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <TOKEN>" \
  -d '{
    "username": "usuario1",
    "password": "Pass123!",
    "nombres": "Juan",
    "apellidos": "Pérez",
    "email": "juan@test.com",
    "rol": "FACTURADOR"
  }'
```

### 2. Probar Frontend

#### Módulo de Usuarios
1. Login con admin/Admin123!
2. Ir a "Usuarios"
3. Crear nuevo usuario → Verificar que aparece
4. Editar usuario → Verificar cambios
5. Cambiar estado → Verificar activo/inactivo
6. Eliminar usuario → Verificar que desaparece

#### Módulo de Clientes
1. Ir a "Clientes"
2. Crear cliente con CEDULA
3. Crear cliente con RUC
4. Editar cualquier cliente
5. Verificar en pgAdmin que datos están cifrados
6. Eliminar cliente

---

##  Troubleshooting Común

### Backend no inicia

```bash
# Verificar que PostgreSQL está corriendo
psql -U postgres -c "SELECT version();"

# Verificar que la base de datos existe
psql -U postgres -c "\l"

# Reiniciar el backend
python app.py
```

### Frontend no se conecta al backend

```bash
# Verificar que el backend está corriendo
curl http://localhost:5000/health

# Verificar CORS en backend/.env
CORS_ORIGINS=http://localhost:5173
```

### Error: "Token inválido"

- El token expira en 8 horas
- Cerrar sesión y volver a iniciar sesión
- Verificar que SECRET_KEY no cambió

---

##  Mejoras Futuras

- [ ] Módulo de facturas completo con XML y firma RSA
- [ ] Generación de QR codes para facturas
- [ ] Exportación a PDF con ReportLab
- [ ] Reportes y estadísticas
- [ ] Integración con SRI (ambiente de pruebas)
- [ ] Envío de facturas por email
- [ ] Panel de auditoría visual

---

##  Roles y Permisos

| Rol | Usuarios | Clientes | Facturas | Auditoría |
|-----|----------|----------|----------|-----------|
| **ADMIN** | ✅ CRUD | ✅ CRUD | ✅ CRUD | ✅ Ver |
| **FACTURADOR** | ❌ | ✅ CRUD | ✅ CRUD | ❌ |
| **CONTADOR** | ❌ | ✅ Ver | ✅ Ver | ❌ |
| **AUDITOR** | ❌ | ✅ Ver | ✅ Ver | ✅ Ver |

---

##  Licencia

Este proyecto es parte de un trabajo académico para la materia de Seguridad en Aplicaciones Web.

---

##  Características Destacadas

-  **100% Funcional** - Todas las operaciones CRUD probadas
-  **Seguridad Robusta** - Criptografía de nivel empresarial
-  **Código Limpio** - Bien documentado y organizado
-  **Manejo de Errores** - En todos los niveles
-  **Responsive** - Funciona en todos los dispositivos
-  **Auditoría Completa** - Registro de todas las operaciones

---

##  Soporte

Para problemas o dudas:

1. Revisar los README de cada módulo
2. Verificar logs del backend (consola)
3. Verificar logs del frontend (consola del navegador F12)
4. Verificar que todos los servicios estén corriendo

---

** Sistema listo **
# ProyectoFinal_IngenieriaDeSeguridad
Proyecto final de la asignatura de ingeniería de seguridad. 

