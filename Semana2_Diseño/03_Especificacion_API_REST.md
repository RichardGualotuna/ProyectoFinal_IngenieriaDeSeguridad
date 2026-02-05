# Especificación API REST - Sistema de Facturación Electrónica

## 1. Información General

**Base URL**: `https://api.facturasegura.com/v1`  
**Protocolo**: HTTPS (TLS 1.3)  
**Formato**: JSON  
**Autenticación**: JWT Bearer Token  
**Versión**: 1.0.0  

### Códigos de Estado HTTP

| Código | Significado | Uso |
|--------|-------------|-----|
| 200 | OK | Solicitud exitosa |
| 201 | Created | Recurso creado exitosamente |
| 204 | No Content | Eliminación exitosa |
| 400 | Bad Request | Datos de entrada inválidos |
| 401 | Unauthorized | Token faltante o inválido |
| 403 | Forbidden | Sin permisos suficientes |
| 404 | Not Found | Recurso no encontrado |
| 409 | Conflict | Conflicto (ej: duplicado) |
| 422 | Unprocessable Entity | Validación de negocio falla |
| 429 | Too Many Requests | Rate limit excedido |
| 500 | Internal Server Error | Error del servidor |

### Headers Comunes

**Request Headers**:
```
Content-Type: application/json
Authorization: Bearer <token>
Accept: application/json
User-Agent: FacturaSegura-Client/1.0
```

**Response Headers**:
```
Content-Type: application/json
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1673612400
```

## 2. Autenticación

### 2.1 POST /auth/register

**Descripción**: Registrar un nuevo usuario

**Permisos**: Público (con código de invitación) o ADMIN

**Request**:
```json
{
  "username": "jperez",
  "email": "jperez@example.com",
  "password": "SecurePass123!",
  "password_confirmation": "SecurePass123!",
  "nombres": "Juan",
  "apellidos": "Pérez",
  "rol": "FACTURADOR",
  "codigo_invitacion": "ABC123XYZ"
}
```

**Response** (201):
```json
{
  "success": true,
  "message": "Usuario registrado exitosamente",
  "data": {
    "id": 5,
    "username": "jperez",
    "email": "jperez@example.com",
    "nombres": "Juan",
    "apellidos": "Pérez",
    "rol": "FACTURADOR",
    "activo": true,
    "created_at": "2026-01-12T10:30:00Z"
  }
}
```

**Errores**:
- 400: Validación falla (contraseña débil, email inválido)
- 409: Username o email ya existe

---

### 2.2 POST /auth/login

**Descripción**: Iniciar sesión y obtener JWT token

**Permisos**: Público

**Request**:
```json
{
  "email": "jperez@example.com",
  "password": "SecurePass123!"
}
```

**Response** (200):
```json
{
  "success": true,
  "message": "Login exitoso",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "expires_in": 900,
    "user": {
      "id": 5,
      "username": "jperez",
      "email": "jperez@example.com",
      "nombres": "Juan",
      "apellidos": "Pérez",
      "rol": "FACTURADOR",
      "ultimo_login": "2026-01-12T10:30:00Z"
    }
  }
}
```

**Errores**:
- 401: Credenciales inválidas
- 403: Usuario inactivo

---

### 2.3 POST /auth/refresh

**Descripción**: Renovar token JWT usando refresh token

**Permisos**: Autenticado

**Request**:
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response** (200):
```json
{
  "success": true,
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "expires_in": 900
  }
}
```

---

### 2.4 POST /auth/logout

**Descripción**: Cerrar sesión (invalidar token)

**Permisos**: Autenticado

**Response** (200):
```json
{
  "success": true,
  "message": "Sesión cerrada exitosamente"
}
```

---

## 3. Gestión de Clientes

### 3.1 GET /clientes

**Descripción**: Listar todos los clientes

**Permisos**: ADMIN, FACTURADOR, CONTADOR

**Query Parameters**:
- `page` (integer): Número de página (default: 1)
- `per_page` (integer): Items por página (default: 20, max: 100)
- `search` (string): Buscar por identificación o razón social
- `tipo` (string): Filtrar por tipo (RUC, CEDULA, PASAPORTE)
- `activo` (boolean): Filtrar por estado activo

**Example**: `GET /clientes?page=1&per_page=20&search=1234&activo=true`

**Response** (200):
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": 10,
        "tipo_identificacion": "RUC",
        "identificacion": "1234567890001",
        "razon_social": "EMPRESA XYZ S.A.",
        "nombres": "Juan Antonio",
        "apellidos": "Pérez Gómez",
        "direccion": "Av. Principal 123",
        "telefono": "0999123456",
        "email": "contacto@empresa.com",
        "activo": true,
        "created_at": "2026-01-10T15:30:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "per_page": 20,
      "total": 150,
      "pages": 8
    }
  }
}
```

**Nota**: Los datos sensibles (direccion, telefono, email) se descifran automáticamente en el backend.

---

### 3.2 GET /clientes/:id

**Descripción**: Obtener detalles de un cliente específico

**Permisos**: ADMIN, FACTURADOR, CONTADOR

**Response** (200):
```json
{
  "success": true,
  "data": {
    "id": 10,
    "tipo_identificacion": "RUC",
    "identificacion": "1234567890001",
    "razon_social": "EMPRESA XYZ S.A.",
    "nombres": "Juan Antonio",
    "apellidos": "Pérez Gómez",
    "direccion": "Av. Principal 123 y Secundaria, Quito",
    "telefono": "0999123456",
    "email": "contacto@empresa.com",
    "activo": true,
    "created_at": "2026-01-10T15:30:00Z",
    "updated_at": "2026-01-10T15:30:00Z",
    "total_facturas": 45,
    "total_compras": 12500.50
  }
}
```

**Errores**:
- 404: Cliente no encontrado

---

### 3.3 POST /clientes

**Descripción**: Crear un nuevo cliente

**Permisos**: ADMIN, FACTURADOR

**Request**:
```json
{
  "tipo_identificacion": "RUC",
  "identificacion": "1234567890001",
  "razon_social": "EMPRESA XYZ S.A.",
  "nombres": "Juan Antonio",
  "apellidos": "Pérez Gómez",
  "direccion": "Av. Principal 123 y Secundaria, Quito",
  "telefono": "0999123456",
  "email": "contacto@empresa.com"
}
```

**Response** (201):
```json
{
  "success": true,
  "message": "Cliente creado exitosamente",
  "data": {
    "id": 15,
    "tipo_identificacion": "RUC",
    "identificacion": "1234567890001",
    "razon_social": "EMPRESA XYZ S.A.",
    "activo": true,
    "created_at": "2026-01-12T10:45:00Z"
  }
}
```

**Validaciones**:
- RUC válido (13 dígitos, módulo 11)
- Cédula válida (10 dígitos, módulo 10)
- Email formato válido
- Identificación única (no duplicada)

**Errores**:
- 400: Validación falla
- 409: Cliente ya existe

---

### 3.4 PUT /clientes/:id

**Descripción**: Actualizar un cliente existente

**Permisos**: ADMIN, FACTURADOR

**Request**:
```json
{
  "direccion": "Av. Nueva 456, Guayaquil",
  "telefono": "0987654321",
  "email": "nuevo@empresa.com",
  "activo": true
}
```

**Response** (200):
```json
{
  "success": true,
  "message": "Cliente actualizado exitosamente",
  "data": {
    "id": 15,
    "updated_at": "2026-01-12T11:00:00Z"
  }
}
```

---

### 3.5 DELETE /clientes/:id

**Descripción**: Eliminar un cliente (soft delete)

**Permisos**: ADMIN

**Response** (200):
```json
{
  "success": true,
  "message": "Cliente desactivado exitosamente"
}
```

**Nota**: No se elimina físicamente, solo se marca como `activo=false`

---

## 4. Gestión de Facturas

### 4.1 GET /facturas

**Descripción**: Listar facturas con filtros

**Permisos**: ADMIN (todas), FACTURADOR/CONTADOR (propias)

**Query Parameters**:
- `page`, `per_page`: Paginación
- `fecha_desde`, `fecha_hasta`: Rango de fechas (ISO 8601)
- `cliente_id`: Filtrar por cliente
- `estado`: AUTORIZADA, ANULADA, DEVUELTA
- `numero_factura`: Buscar por número exacto
- `min_total`, `max_total`: Rango de monto

**Example**: `GET /facturas?fecha_desde=2026-01-01&estado=AUTORIZADA&page=1`

**Response** (200):
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": 100,
        "numero_factura": "001-001-000000123",
        "fecha_emision": "2026-01-12T10:30:00Z",
        "cliente": {
          "id": 10,
          "identificacion": "1234567890001",
          "razon_social": "EMPRESA XYZ S.A."
        },
        "subtotal": 100.00,
        "iva": 15.00,
        "total": 115.00,
        "estado": "AUTORIZADA",
        "num_autorizacion": "1234567890123456789012345678901234567890123456789",
        "qr_code_url": "/static/qr/factura_100.png"
      }
    ],
    "pagination": {
      "page": 1,
      "per_page": 20,
      "total": 500,
      "pages": 25
    },
    "summary": {
      "total_facturas": 500,
      "suma_total": 57500.00,
      "suma_iva": 7500.00
    }
  }
}
```

---

### 4.2 GET /facturas/:id

**Descripción**: Obtener detalles completos de una factura

**Permisos**: ADMIN, FACTURADOR (propias), CONTADOR

**Response** (200):
```json
{
  "success": true,
  "data": {
    "id": 100,
    "numero_factura": "001-001-000000123",
    "fecha_emision": "2026-01-12T10:30:00Z",
    "cliente": {
      "id": 10,
      "identificacion": "1234567890001",
      "razon_social": "EMPRESA XYZ S.A.",
      "direccion": "Av. Principal 123",
      "email": "contacto@empresa.com"
    },
    "detalles": [
      {
        "id": 1,
        "codigo_principal": "PROD001",
        "descripcion": "Servicio de Consultoría",
        "cantidad": 1.0000,
        "precio_unitario": 100.0000,
        "descuento": 0.00,
        "tarifa_iva": 15,
        "valor_iva": 15.00,
        "total_linea": 115.00
      }
    ],
    "subtotal_sin_imp": 0.00,
    "subtotal_iva": 100.00,
    "subtotal_iva_0": 0.00,
    "iva": 15.00,
    "propina": 0.00,
    "total": 115.00,
    "forma_pago": "SIN UTILIZACION DEL SISTEMA FINANCIERO",
    "hash_sha256": "a3f5b8c2d4e6f8a0b1c3d5e7f9a1b3c5d7e9f1a3b5c7d9e1f3a5b7c9d1e3f5a7",
    "num_autorizacion": "1234567890123456789012345678901234567890123456789",
    "clave_acceso": "1201202601123456789000100100100000001231234567895",
    "fecha_autorizacion": "2026-01-12T10:30:05Z",
    "qr_code_url": "/static/qr/factura_100.png",
    "estado": "AUTORIZADA",
    "observaciones": null,
    "usuario_emisor": {
      "id": 5,
      "username": "jperez",
      "nombres": "Juan Pérez"
    },
    "created_at": "2026-01-12T10:30:00Z"
  }
}
```

---

### 4.3 POST /facturas

**Descripción**: Crear y firmar una nueva factura

**Permisos**: ADMIN, FACTURADOR

**Request**:
```json
{
  "cliente_id": 10,
  "fecha_emision": "2026-01-12T10:30:00Z",
  "forma_pago": "SIN UTILIZACION DEL SISTEMA FINANCIERO",
  "detalles": [
    {
      "codigo_principal": "PROD001",
      "descripcion": "Servicio de Consultoría",
      "cantidad": 1.0,
      "precio_unitario": 100.00,
      "descuento": 0.00,
      "tarifa_iva": 15
    },
    {
      "codigo_principal": "PROD002",
      "descripcion": "Producto de Prueba",
      "cantidad": 2.0,
      "precio_unitario": 50.00,
      "descuento": 10.00,
      "tarifa_iva": 15
    }
  ],
  "observaciones": "Factura de prueba"
}
```

**Response** (201):
```json
{
  "success": true,
  "message": "Factura creada y firmada exitosamente",
  "data": {
    "id": 101,
    "numero_factura": "001-001-000000124",
    "total": 230.00,
    "hash_sha256": "b4a6c9d3e5f7a9b1c3d5e7f9a1b3c5d7e9f1a3b5c7d9e1f3a5b7c9d1e3f5a8",
    "num_autorizacion": "1234567890123456789012345678901234567890123456790",
    "clave_acceso": "1201202601123456789000100100100000001241234567896",
    "qr_code_url": "/static/qr/factura_101.png",
    "estado": "AUTORIZADA",
    "pdf_url": "/api/facturas/101/pdf",
    "xml_url": "/api/facturas/101/xml"
  }
}
```

**Proceso interno**:
1. Validar datos de entrada
2. Validar que cliente existe y está activo
3. Generar número de factura secuencial
4. Calcular subtotales, IVA y total
5. Generar XML según esquema SRI
6. Calcular hash SHA-256 del XML
7. Firmar hash con clave privada RSA
8. Generar número de autorización y clave de acceso
9. Generar código QR con datos de verificación
10. Guardar en base de datos
11. Registrar en audit_log

**Validaciones**:
- Cliente existe y activo
- Fecha no posterior a hoy
- Al menos un detalle
- Cantidades y precios > 0
- Tarifa IVA válida (0, 8, 12, 15)
- Cálculos matemáticos correctos

**Errores**:
- 400: Validación falla
- 404: Cliente no encontrado
- 422: Error en cálculos o firma digital

---

### 4.4 GET /facturas/:id/pdf

**Descripción**: Descargar factura en formato PDF

**Permisos**: ADMIN, FACTURADOR (propias), CONTADOR

**Response**: Archivo PDF con Content-Type: application/pdf

**Headers**:
```
Content-Type: application/pdf
Content-Disposition: attachment; filename="factura_001-001-000000123.pdf"
```

---

### 4.5 GET /facturas/:id/xml

**Descripción**: Descargar factura en formato XML firmado

**Permisos**: ADMIN, FACTURADOR (propias), CONTADOR

**Response**: Archivo XML con Content-Type: application/xml

**Headers**:
```
Content-Type: application/xml
Content-Disposition: attachment; filename="factura_001-001-000000123.xml"
```

---

### 4.6 POST /facturas/:id/anular

**Descripción**: Anular una factura autorizada

**Permisos**: ADMIN

**Request**:
```json
{
  "motivo": "Error en monto, se emitirá factura correcta"
}
```

**Response** (200):
```json
{
  "success": true,
  "message": "Factura anulada exitosamente",
  "data": {
    "id": 100,
    "estado": "ANULADA",
    "fecha_anulacion": "2026-01-12T14:00:00Z"
  }
}
```

**Nota**: La anulación se registra en audit_log

---

### 4.7 POST /facturas/:id/enviar-email

**Descripción**: Enviar factura por email al cliente

**Permisos**: ADMIN, FACTURADOR (propias)

**Request**:
```json
{
  "destinatario": "cliente@example.com",
  "cc": ["contador@example.com"],
  "mensaje": "Adjunto encontrará su factura electrónica"
}
```

**Response** (200):
```json
{
  "success": true,
  "message": "Factura enviada por email exitosamente",
  "data": {
    "destinatarios": ["cliente@example.com", "contador@example.com"],
    "enviado_at": "2026-01-12T11:00:00Z"
  }
}
```

---

## 5. Verificación de Facturas

### 5.1 GET /verificar/:numero_autorizacion

**Descripción**: Verificar autenticidad de una factura (pública)

**Permisos**: Público (sin autenticación)

**Response** (200):
```json
{
  "success": true,
  "data": {
    "valida": true,
    "verificaciones": {
      "factura_existe": true,
      "hash_coincide": true,
      "firma_valida": true,
      "estado_activo": true
    },
    "factura": {
      "numero_factura": "001-001-000000123",
      "fecha_emision": "2026-01-12T10:30:00Z",
      "empresa_emisor": {
        "ruc": "1234567890001",
        "razon_social": "EMPRESA EMISORA S.A."
      },
      "cliente": {
        "identificacion": "9999999999",
        "razon_social": "CLIENTE EJEMPLO"
      },
      "total": 115.00,
      "estado": "AUTORIZADA",
      "fecha_autorizacion": "2026-01-12T10:30:05Z"
    },
    "timestamp_verificacion": "2026-01-12T15:00:00Z"
  }
}
```

**Errores**:
- 404: Factura no encontrada

---

### 5.2 POST /verificar/qr

**Descripción**: Verificar factura mediante datos del QR

**Permisos**: Público

**Request**:
```json
{
  "qr_data": {
    "num_autorizacion": "1234567890123456789012345678901234567890123456789",
    "hash_sha256": "a3f5b8c2d4e6f8a0b1c3d5e7f9a1b3c5d7e9f1a3b5c7d9e1f3a5b7c9d1e3f5a7"
  }
}
```

**Response** (200): Similar a 5.1

---

## 6. Reportes

### 6.1 GET /reportes/ventas

**Descripción**: Reporte de ventas por período

**Permisos**: ADMIN, CONTADOR

**Query Parameters**:
- `fecha_desde`, `fecha_hasta`: Rango de fechas (requerido)
- `agrupar_por`: day, week, month, year
- `formato`: json, pdf, excel

**Response** (200):
```json
{
  "success": true,
  "data": {
    "periodo": {
      "desde": "2026-01-01",
      "hasta": "2026-01-31"
    },
    "resumen": {
      "total_facturas": 150,
      "facturas_autorizadas": 145,
      "facturas_anuladas": 5,
      "subtotal": 15000.00,
      "iva": 1950.00,
      "total": 16950.00,
      "ticket_promedio": 113.00
    },
    "desglose_iva": [
      {"tarifa": 0, "base": 2000.00, "iva": 0.00},
      {"tarifa": 15, "base": 13000.00, "iva": 1950.00}
    ],
    "por_fecha": [
      {"fecha": "2026-01-01", "facturas": 5, "total": 575.00},
      {"fecha": "2026-01-02", "facturas": 7, "total": 805.00}
    ]
  }
}
```

---

### 6.2 POST /reportes/exportar-xml

**Descripción**: Exportar lote de facturas en XML para SRI

**Permisos**: ADMIN, CONTADOR

**Request**:
```json
{
  "fecha_desde": "2026-01-01",
  "fecha_hasta": "2026-01-31",
  "estado": "AUTORIZADA"
}
```

**Response** (200):
```json
{
  "success": true,
  "message": "Exportación generada exitosamente",
  "data": {
    "total_facturas": 145,
    "archivo_zip": "/exports/facturas_202601_abc123.zip",
    "tamaño_kb": 1250,
    "generado_at": "2026-01-12T15:30:00Z",
    "expira_at": "2026-01-13T15:30:00Z"
  }
}
```

---

### 6.3 GET /reportes/dashboard

**Descripción**: Métricas para dashboard principal

**Permisos**: Autenticado

**Response** (200):
```json
{
  "success": true,
  "data": {
    "hoy": {
      "facturas": 12,
      "total_ventas": 1380.00
    },
    "mes_actual": {
      "facturas": 145,
      "total_ventas": 16950.00,
      "comparacion_mes_anterior": "+15%"
    },
    "top_clientes": [
      {
        "cliente_id": 10,
        "razon_social": "EMPRESA XYZ S.A.",
        "total_compras": 5000.00,
        "facturas": 25
      }
    ],
    "grafico_ventas_7dias": [
      {"fecha": "2026-01-06", "total": 450.00},
      {"fecha": "2026-01-07", "total": 380.00}
    ]
  }
}
```

---

## 7. Auditoría

### 7.1 GET /audit-logs

**Descripción**: Consultar logs de auditoría

**Permisos**: ADMIN, AUDITOR

**Query Parameters**:
- `fecha_desde`, `fecha_hasta`: Rango
- `usuario_id`: Filtrar por usuario
- `accion`: LOGIN, CREATE, UPDATE, DELETE, etc.
- `entidad`: FACTURA, CLIENTE, USUARIO
- `resultado`: EXITO, FALLO

**Response** (200):
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": 1000,
        "timestamp": "2026-01-12T10:30:00Z",
        "usuario": {
          "id": 5,
          "username": "jperez"
        },
        "accion": "CREATE",
        "entidad": "FACTURA",
        "entidad_id": 100,
        "ip_address": "192.168.1.100",
        "resultado": "EXITO"
      }
    ],
    "pagination": {
      "page": 1,
      "per_page": 50,
      "total": 5000
    }
  }
}
```

---

## 8. Administración

### 8.1 GET /usuarios

**Descripción**: Listar usuarios del sistema

**Permisos**: ADMIN

**Response** (200):
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": 5,
        "username": "jperez",
        "email": "jperez@example.com",
        "nombres": "Juan",
        "apellidos": "Pérez",
        "rol": "FACTURADOR",
        "activo": true,
        "ultimo_login": "2026-01-12T10:30:00Z",
        "created_at": "2026-01-10T09:00:00Z"
      }
    ]
  }
}
```

---

### 8.2 PUT /usuarios/:id

**Descripción**: Actualizar usuario

**Permisos**: ADMIN (todos), Usuario (propio perfil)

**Request**:
```json
{
  "nombres": "Juan Carlos",
  "apellidos": "Pérez Gómez",
  "email": "jcperez@example.com",
  "rol": "ADMIN",
  "activo": true
}
```

---

### 8.3 GET /empresa

**Descripción**: Obtener configuración de la empresa

**Permisos**: Autenticado

**Response** (200):
```json
{
  "success": true,
  "data": {
    "id": 1,
    "ruc": "1234567890001",
    "razon_social": "MI EMPRESA S.A.",
    "nombre_comercial": "MiEmpresa",
    "direccion": "Av. Principal 123",
    "telefono": "023456789",
    "email": "contacto@miempresa.com",
    "establecimiento": "001",
    "punto_emision": "001",
    "ambiente": "PRODUCCION",
    "logo_url": "/static/logos/empresa.png"
  }
}
```

---

### 8.4 PUT /empresa

**Descripción**: Actualizar configuración de empresa

**Permisos**: ADMIN

---

## 9. Rate Limiting

| Endpoint | Límite |
|----------|--------|
| `/auth/login` | 10 req/min |
| `/auth/register` | 5 req/min |
| `/facturas` (POST) | 50 req/min |
| `/verificar/*` | 100 req/min |
| Otros | 100 req/min |

**Response** cuando se excede (429):
```json
{
  "success": false,
  "error": "TooManyRequests",
  "message": "Rate limit excedido. Intente nuevamente en 60 segundos",
  "retry_after": 60
}
```

---

## 10. Formato de Errores

**Estructura estándar de error**:
```json
{
  "success": false,
  "error": "ValidationError",
  "message": "Los datos proporcionados no son válidos",
  "details": [
    {
      "field": "email",
      "message": "El email no tiene un formato válido"
    },
    {
      "field": "password",
      "message": "La contraseña debe tener al menos 8 caracteres"
    }
  ],
  "timestamp": "2026-01-12T10:30:00Z",
  "request_id": "abc123xyz"
}
```

---

## 11. Webhooks (Futuro)

Endpoints para configurar notificaciones en tiempo real:
- `/webhooks` (CRUD)
- Eventos: `factura.creada`, `factura.anulada`, `cliente.creado`

---

## Resumen de Endpoints

| Grupo | Endpoints | Métodos |
|-------|-----------|---------|
| **Auth** | 4 | POST |
| **Clientes** | 5 | GET, POST, PUT, DELETE |
| **Facturas** | 7 | GET, POST |
| **Verificación** | 2 | GET, POST |
| **Reportes** | 3 | GET, POST |
| **Auditoría** | 1 | GET |
| **Admin** | 4 | GET, PUT |
| **Total** | **26** | |

## Próximos Pasos

Con la API REST especificada, finalizaremos el diseño con la selección de bibliotecas criptográficas.
