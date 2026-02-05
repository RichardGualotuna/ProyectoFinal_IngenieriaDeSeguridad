# Frontend - Sistema de Facturación Electrónica

## 🚀 Inicio Rápido

### 1. Requisitos Previos
- Node.js 18+ y npm
- Backend corriendo en http://localhost:5000

### 2. Instalación

```bash
# Instalar dependencias
npm install
```

### 3. Ejecutar en Desarrollo

```bash
npm run dev
```

Aplicación corriendo en: http://localhost:5173

### 4. Construir para Producción

```bash
npm run build
npm run preview
```

---

## 🔐 Credenciales por Defecto

- **Usuario:** admin
- **Contraseña:** Admin123!

---

## 📱 Funcionalidades

### Módulo de Usuarios (Solo ADMIN)
- ✅ **Listar usuarios** con paginación
- ✅ **Crear usuarios** con validación de campos
- ✅ **Editar usuarios** (actualizar datos parcialmente)
- ✅ **Eliminar usuarios** (soft delete - desactivar)
- ✅ **Cambiar estado** (activar/desactivar)
- ✅ Roles: ADMIN, FACTURADOR, CONTADOR, AUDITOR

### Módulo de Clientes
- ✅ **Listar clientes** con datos descifrados automáticamente
- ✅ **Crear clientes** con cifrado automático de datos sensibles
- ✅ **Editar clientes** preservando cifrado
- ✅ **Eliminar clientes** (soft delete)
- ✅ Tipos de identificación: CEDULA, RUC, PASAPORTE
- ✅ Cifrado AES-256-GCM de datos sensibles

---

## ✅ Correcciones Aplicadas vs Proyecto Principal

### Problemas Identificados y Solucionados:

1. **✅ Lista de usuarios no se mostraba**
   ```javascript
   // ANTES (proyecto principal):
   const data = await userService.getAll()
   setUsers(data.users)  // ❌ Fallaba si data.users era undefined
   
   // AHORA (corregido):
   const data = await userService.getAll()
   if (Array.isArray(data)) {
     setUsers(data)
   } else {
     setUsers([])  // ✅ Siempre un array válido
   }
   ```

2. **✅ No se podían crear usuarios**
   ```javascript
   // ANTES:
   required_fields = ['username', 'password', 'rol', 'nombre']  // ❌ Campo 'nombre' no existe
   
   // AHORA:
   required_fields = ['username', 'password', 'rol', 'nombres', 'apellidos', 'email']  // ✅ Campos correctos
   ```

3. **✅ No se podían editar usuarios**
   ```javascript
   // ANTES:
   await userService.update(id, formData)  // ❌ Enviaba username (no editable)
   
   // AHORA:
   const updateData = { ...formData }
   delete updateData.username  // ✅ No envía campos no editables
   if (!updateData.password) delete updateData.password  // ✅ No envía password vacío
   await userService.update(id, updateData)
   ```

4. **✅ No se podían eliminar usuarios**
   ```javascript
   // ANTES:
   await userService.delete(id)  // ❌ Backend no implementaba soft delete correctamente
   
   // AHORA:
   // Backend: AuthService.delete_user() hace soft delete apropiadamente
   // Frontend: Confirmación antes de eliminar
   if (window.confirm(`¿Está seguro...?`)) {
     await userService.delete(id)  // ✅ Funciona correctamente
   }
   ```

5. **✅ Respuestas del backend inconsistentes**
   ```javascript
   // ANTES:
   return response.data.data.users  // ❌ Fallaba si estructura cambiaba
   
   // AHORA:
   if (response.data.success && response.data.data) {
     return response.data.data.users || []  // ✅ Manejo robusto
   }
   return response.data.users || []
   ```

6. **✅ Errores no se mostraban al usuario**
   ```javascript
   // ANTES:
   catch (err) {
     console.error(err)  // ❌ Solo en consola
   }
   
   // AHORA:
   catch (err) {
     console.error('Error:', err)
     setError('Error: ' + err.message)  // ✅ Muestra al usuario
   }
   ```

---

## 🎨 Componentes

### Páginas
- **Login.jsx**: Autenticación con JWT
- **Dashboard.jsx**: Panel principal con resumen
- **Usuarios.jsx**: CRUD completo de usuarios (solo ADMIN)
- **Clientes.jsx**: CRUD completo de clientes con cifrado

### Componentes
- **Navbar.jsx**: Barra de navegación con menú de usuario
- **PrivateRoute.jsx**: Protección de rutas con autenticación

### Contextos
- **AuthContext.jsx**: Manejo global de autenticación y sesión

### Servicios
- **api.js**: Configuración de Axios con interceptores
- **services.js**: Servicios para auth, users, clientes

---

## 🔒 Seguridad Implementada

### Autenticación
- JWT Bearer Token con expiración de 8 horas
- Interceptor que agrega automáticamente el token a todas las peticiones
- Redirección automática a login si el token expira o es inválido
- Almacenamiento seguro en localStorage

### Protección de Rutas
- Rutas privadas requieren autenticación
- Rutas de administración requieren rol ADMIN
- Redirección automática si no se cumplen los requisitos

### Manejo de Errores
- Interceptor global de errores en Axios
- Mensajes de error consistentes y amigables
- Rollback automático en caso de error
- Logs detallados en consola para debugging

---

## 📁 Estructura del Proyecto

```
Semana4_Frontend/
├── index.html
├── package.json
├── vite.config.js
└── src/
    ├── App.jsx              # Aplicación principal con rutas
    ├── main.jsx             # Punto de entrada
    ├── index.css            # Estilos globales
    ├── components/          # Componentes reutilizables
    │   ├── Navbar.jsx
    │   └── PrivateRoute.jsx
    ├── contexts/            # Contextos de React
    │   └── AuthContext.jsx
    ├── pages/               # Páginas principales
    │   ├── Login.jsx
    │   ├── Dashboard.jsx
    │   ├── Usuarios.jsx
    │   └── Clientes.jsx
    └── services/            # Servicios de API
        ├── api.js
        └── services.js
```

---

## 🧪 Guía de Pruebas

### Probar Módulo de Usuarios (como ADMIN)

1. **Login como admin**
   - Usuario: `admin`
   - Password: `Admin123!`

2. **Listar usuarios**
   - Ir a "Usuarios" en navbar
   - Verificar que se muestran los usuarios existentes

3. **Crear nuevo usuario**
   - Click en "Nuevo Usuario"
   - Llenar todos los campos:
     - Username: `usuario1`
     - Password: `Test123!`
     - Nombres: `Juan`
     - Apellidos: `Pérez`
     - Email: `juan@test.com`
     - Rol: `FACTURADOR`
   - Click en "Crear"
   - Verificar mensaje de éxito
   - Verificar que aparece en la lista

4. **Editar usuario**
   - Click en ícono de lápiz del usuario creado
   - Cambiar email a: `juan.nuevo@test.com`
   - Click en "Actualizar"
   - Verificar cambios

5. **Desactivar usuario**
   - Click en ícono de "X" (cambiar estado)
   - Verificar que estado cambia a "Inactivo"

6. **Eliminar usuario**
   - Click en ícono de basura
   - Confirmar eliminación
   - Verificar que se elimina de la lista

### Probar Módulo de Clientes

1. **Crear cliente persona natural**
   - Click en "Nuevo Cliente"
   - Tipo: `CEDULA`
   - Identificación: `1234567890`
   - Nombres: `María`
   - Apellidos: `González`
   - Dirección: `Av. Principal 123`
   - Teléfono: `0998765432`
   - Email: `maria@test.com`
   - Click en "Crear"

2. **Crear cliente empresa (RUC)**
   - Tipo: `RUC`
   - Identificación: `1234567890001`
   - Razón Social: `Empresa Test S.A.`
   - Datos sensibles...

3. **Editar cliente**
   - Modificar cualquier campo
   - Verificar que se actualiza correctamente

4. **Verificar cifrado**
   - Abrir pgAdmin
   - Consultar tabla `cliente`
   - Verificar que campos sensibles están en binario (BYTEA)

---

## 🐛 Troubleshooting

### Error: "Cannot read property 'users' of undefined"
**Causa:** Backend devuelve estructura diferente  
**Solución:** Verificar que el backend esté corriendo y devolviendo `{success: true, data: {users: [...]}}`

### Error: "Failed to fetch"
**Causa:** Backend no está corriendo  
**Solución:** Iniciar backend con `python app.py`

### Error: "CORS policy"
**Causa:** CORS no configurado en backend  
**Solución:** Verificar que `.env` del backend incluye `CORS_ORIGINS=http://localhost:5173`

### Error: "Token inválido"
**Causa:** Token expirado o inválido  
**Solución:** Cerrar sesión y volver a iniciar sesión

---

## 📦 Tecnologías Utilizadas

- **React 18**: Biblioteca de UI
- **React Router DOM 6**: Enrutamiento
- **Axios**: Cliente HTTP
- **Bootstrap 5**: Framework CSS
- **React Bootstrap**: Componentes de Bootstrap para React
- **Vite**: Build tool y dev server
- **Bootstrap Icons**: Iconografía

---

## 📞 Soporte

Para problemas o preguntas:

1. Revisar la consola del navegador (F12)
2. Verificar que el backend está corriendo
3. Verificar los logs del backend (terminal donde corre `python app.py`)
4. Verificar estructura de respuestas del backend

---

## ✨ Características Destacadas

- ✅ **100% funcional** - Todas las operaciones CRUD probadas
- ✅ **Responsive** - Funciona en desktop, tablet y móvil
- ✅ **Seguro** - Autenticación JWT, protección de rutas, roles
- ✅ **Robusto** - Manejo de errores en todos los niveles
- ✅ **Intuitivo** - UI amigable con Bootstrap 5
- ✅ **Rápido** - Vite para desarrollo y build optimizado
