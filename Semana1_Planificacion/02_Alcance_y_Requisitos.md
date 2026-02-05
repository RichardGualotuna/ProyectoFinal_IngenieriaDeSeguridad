# Alcance y Requisitos del Sistema de Facturación Electrónica

## 1. Visión General del Proyecto

### Objetivo Principal
Desarrollar un sistema de facturación electrónica seguro y conforme a las normativas del SRI de Ecuador, que permita a PYMEs y autónomos emitir facturas electrónicas con firma digital, garantizando autenticidad, integridad y confidencialidad.

### Usuarios Objetivo
-  PYMEs (Pequeñas y Medianas Empresas)
-  Autónomos y profesionales independientes
-  Negocios de retail y servicios
-  Contadores y asesores fiscales

### Valor Diferencial
-  Cumplimiento legal automático con SRI
-  Seguridad criptográfica de nivel empresarial
-  Costo accesible para negocios pequeños
-  Implementación rápida y sencilla
-  Verificación instantánea con QR

## 2. Alcance del Sistema

### 2.1 Módulos Incluidos

#### Módulo de Facturación 
- Creación de facturas electrónicas
- Cálculo automático de impuestos (IVA, ICE)
- Numeración secuencial automática
- Generación de XML conforme a SRI
- Vista previa de factura antes de emitir

#### Módulo de Firma Digital 
- Generación de par de claves RSA (2048/4096 bits)
- Firma digital de facturas con RSA
- Timestamp en momento de firma
- Almacenamiento seguro de claves privadas
- Verificación de firmas

#### Módulo de Integridad 
- Cálculo de hash SHA-256 por factura
- Detección de alteraciones
- Registro de auditoría inmutable
- Verificación de integridad de lote

#### Módulo de Seguridad de Datos 
- Cifrado AES-256 de datos del cliente
- Gestión de claves maestras
- Backup cifrado de información sensible
- Logs de acceso a datos cifrados

#### Módulo de Verificación QR 
- Generación de QR por factura
- Código QR con datos de verificación
- Integración con app de SRI (simulada)
- Verificación offline de autenticidad

#### Módulo de Gestión de Usuarios 
- Registro de usuarios con bcrypt
- Login seguro con autenticación
- Roles y permisos (Admin, Facturador, Contador)
- Gestión de sesiones con JWT

#### Módulo de Historial 
- Listado de facturas emitidas
- Búsqueda y filtrado avanzado
- Exportación de reportes
- Estadísticas de facturación

#### Módulo de Exportación Tributaria 
- Exportación a XML para SRI
- Generación de anexos transaccionales
- Reportes de ventas mensuales/anuales
- Formato para declaraciones de IVA/Renta

### 2.2 Funcionalidades Excluidas (Fuera de Alcance)
-  Integración directa en tiempo real con SRI (simulación)
-  Facturación recurrente automática
-  Gestión de inventarios
-  Sistema de cobros y pagos
-  Aplicación móvil nativa (solo web responsive)
-  Firma electrónica con certificado BCE (se usa certificado propio)

## 3. Requisitos Funcionales

### RF-001: Registro de Empresa
**Descripción**: El sistema debe permitir el registro de la empresa emisora
**Datos requeridos**:
- RUC (13 dígitos)
- Razón social
- Nombre comercial
- Dirección matriz
- Teléfono y email
- Logo de la empresa

**Validaciones**:
- RUC válido según algoritmo de módulo 11
- Email con formato válido
- Teléfono con formato ecuatoriano

### RF-002: Gestión de Clientes
**Descripción**: CRUD completo de clientes con datos cifrados
**Datos del cliente**:
- Identificación (RUC, cédula, pasaporte)
- Nombres completos / Razón social
- Dirección (cifrada con AES)
- Email (cifrado con AES)
- Teléfono (cifrado con AES)

**Seguridad**:
- Datos sensibles cifrados con AES-256-GCM
- Búsqueda por identificación sin descifrar base completa

### RF-003: Creación de Facturas
**Descripción**: Interfaz para crear facturas con todos los datos requeridos por SRI

**Datos de la factura**:
- Número secuencial: XXX-XXX-XXXXXXXXX
- Fecha de emisión
- Cliente (seleccionado de catálogo)
- Detalle de productos/servicios
  - Código (opcional)
  - Descripción
  - Cantidad
  - Precio unitario
  - Descuento
  - IVA (0%, 8%, 12%, 15%)
  - ICE (si aplica)
- Totales calculados automáticamente
- Forma de pago
- Observaciones

**Validaciones**:
- Fecha no posterior a hoy
- Al menos un ítem en detalle
- Cálculos matemáticos correctos
- Cliente válido y activo

### RF-004: Firma Digital de Factura
**Descripción**: Al guardar una factura, se firma digitalmente con RSA

**Proceso**:
1. Convertir factura a formato XML (esquema SRI)
2. Generar hash SHA-256 del XML
3. Firmar hash con clave privada RSA
4. Almacenar firma en base de datos
5. Generar número de autorización (49 dígitos)
6. Generar clave de acceso (49 dígitos)

**Salida**:
- Factura firmada con validez legal
- Hash almacenado para verificación
- Timestamp de firma
- Número de autorización

### RF-005: Generación de QR
**Descripción**: Cada factura incluye un código QR para verificación

**Contenido del QR**:
```json
{
  "ruc_emisor": "1234567890001",
  "numero_factura": "001-001-000123456",
  "fecha_emision": "12/01/2026",
  "num_autorizacion": "1234567890...",
  "total": "150.50",
  "hash_sha256": "a3f5b8c2...",
  "url_verificacion": "https://sistema.com/verificar"
}
```

**Ubicación**: Parte inferior derecha de la factura PDF

### RF-006: Visualización de Factura
**Descripción**: Vista previa y PDF de factura con diseño profesional

**Elementos**:
- Logo de empresa
- Datos del emisor
- Datos del cliente
- Detalle de productos/servicios
- Subtotales, impuestos y total
- Firma digital (representada visualmente)
- Código QR
- Número de autorización
- Clave de acceso

### RF-007: Verificación de Factura
**Descripción**: Cualquier persona puede verificar una factura mediante QR o número

**Métodos**:
1. Escanear código QR
2. Ingresar número de autorización
3. Subir archivo XML

**Información mostrada**:
- Factura válida / ❌ Factura inválida
- Hash coincide / Hash no coincide
- Firma válida / Firma inválida
- Datos básicos de la factura
- Fecha de emisión
- Estado de autorización

### RF-008: Gestión de Usuarios
**Descripción**: Sistema multiusuario con roles y permisos

**Roles**:
- **Administrador**: Control total del sistema
- **Facturador**: Crear y consultar facturas
- **Contador**: Solo lectura y reportes

**Funcionalidades**:
- Registro con email único
- Login con bcrypt
- Recuperación de contraseña
- Cambio de contraseña
- Gestión de permisos por rol

### RF-009: Historial de Facturas
**Descripción**: Listado completo de facturas con búsqueda

**Filtros**:
- Rango de fechas
- Cliente específico
- Estado (autorizada, anulada)
- Rango de monto
- Número de factura

**Acciones**:
- Ver detalles
- Descargar PDF
- Descargar XML
- Enviar por email
- Anular (con justificación)

### RF-010: Reportes Tributarios
**Descripción**: Generación de reportes para declaraciones fiscales

**Tipos de reporte**:
- Ventas por período
- IVA cobrado (desglosado por tarifa)
- Retenciones (si aplica)
- Anexo transaccional simplificado (ATS)
- Libro de ventas

**Formatos de exportación**:
- PDF
- Excel
- XML (formato SRI)
- CSV

### RF-011: Auditoría
**Descripción**: Registro inmutable de todas las operaciones

**Eventos registrados**:
- Login/Logout de usuarios
- Creación de facturas
- Modificación de clientes
- Acceso a datos cifrados
- Exportación de reportes
- Cambios de configuración

**Datos del log**:
- Usuario que realizó la acción
- Timestamp exacto
- Tipo de acción
- IP de origen
- Resultado (éxito/fallo)

### RF-012: Exportación XML
**Descripción**: Exportar facturas a formato XML del SRI

**Características**:
- Esquema XSD validado
- Firma XAdES-BES
- Codificación UTF-8
- Compresión para lotes
- Nombrado según convención SRI

## 4. Requisitos No Funcionales

### RNF-001: Seguridad
- Comunicación HTTPS (TLS 1.3)
- Contraseñas hasheadas con bcrypt (12 rounds)
- Tokens JWT con expiración (15 min)
- Datos sensibles cifrados con AES-256
- Protección contra SQL injection
- Protección contra XSS
- Validación de entrada en cliente y servidor
- Rate limiting en API (100 req/min)

### RNF-002: Rendimiento
- Generación de factura < 2 segundos
-  Firma digital < 500ms
-  Carga de dashboard < 1 segundo
-  Búsqueda de facturas < 500ms
-  Soporte para 100 usuarios concurrent

### RNF-003: Escalabilidad
-  Mínimo 50,000 facturas por año
-  Hasta 1,000 clientes activos
-  100 usuarios del sistema
-  Crecimiento del 50% anual sin degradación

### RNF-004: Disponibilidad
-  Uptime objetivo: 99.5%
-  Backups diarios automáticos
-  Recuperación ante desastres < 4 horas
-  Mantenimiento programado fuera de horario laboral

### RNF-005: Usabilidad
-  Interfaz intuitiva sin capacitación extensa
-  Responsive design (móvil, tablet, desktop)
-  Mensajes de error claros y accionables
-  Ayuda contextual en formularios
-  Máximo 3 clics para crear factura

### RNF-006: Compatibilidad
-  Navegadores: Chrome, Firefox, Edge, Safari (últimas 2 versiones)
-  Formato XML compatible con SRI
-  QR compatible con apps estándar
-  PDFs compatibles con Adobe Reader

### RNF-007: Mantenibilidad
-  Código documentado con comentarios
-  Arquitectura modular
-  Tests unitarios > 70% cobertura
-  Logs estructurados para debugging
-  Versionamiento de API

### RNF-008: Conformidad Legal
-  Cumplimiento resoluciones SRI
-  Ley de Comercio Electrónico Ecuador
-  LOPDP (Protección de datos personales)
-  Retención de facturas 7 años
-  Trazabilidad completa de documentos

## 5. Restricciones y Limitaciones

### Técnicas
- Implementación inicial solo para Ecuador
- Base de datos PostgreSQL o MySQL
- Backend en Python (Flask/FastAPI)
- Frontend en React/Vue
- Servidor Linux o compatible

### Operativas
- Requiere conexión a internet para firma digital
- Backup manual de claves privadas RSA
- Renovación anual de certificados (simulado)
- Mantenimiento mensual del sistema

### Legales
- Certificado digital propio (no BCE en versión inicial)
- Sin valor legal pleno sin integración real SRI
- Solo para demostración o uso interno inicial

## 6. Casos de Uso Principales

### CU-001: Emitir Factura a Cliente Nuevo
**Actor**: Facturador
**Precondición**: Usuario autenticado
**Flujo**:
1. Ir a "Nueva Factura"
2. Crear nuevo cliente (datos cifrados)
3. Agregar productos/servicios al detalle
4. Sistema calcula IVA y total
5. Revisar vista previa
6. Confirmar emisión
7. Sistema firma digitalmente
8. Sistema genera QR
9. Mostrar factura con opción de descargar/enviar

### CU-002: Verificar Autenticidad de Factura
**Actor**: Cliente o SRI
**Precondición**: Tener código QR o número de autorización
**Flujo**:
1. Escanear QR o ingresar número
2. Sistema busca factura en BD
3. Sistema verifica hash SHA-256
4. Sistema verifica firma RSA
5. Mostrar resultado: Válida o  Inválida
6. Mostrar detalles si es válida

### CU-003: Generar Reporte de Ventas Mensual
**Actor**: Contador
**Precondición**: Usuario con rol Contador
**Flujo**:
1. Ir a "Reportes"
2. Seleccionar tipo "Ventas Mensuales"
3. Elegir mes y año
4. Sistema descifra datos necesarios
5. Sistema genera reporte
6. Opción de exportar PDF/Excel/XML

### CU-004: Exportar XML para SRI
**Actor**: Administrador o Contador
**Precondición**: Facturas del período autorizadas
**Flujo**:
1. Ir a "Exportar XML"
2. Seleccionar rango de fechas
3. Sistema genera XML conforme a esquema SRI
4. Sistema firma XML con XAdES-BES
5. Sistema comprime en ZIP
6. Usuario descarga archivo

## 7. Priorización de Requisitos (MoSCoW)

### Must Have (Debe tener) 🔴
- RF-001, RF-002, RF-003, RF-004, RF-005, RF-006
- RNF-001 (Seguridad)
- RNF-008 (Conformidad Legal)

### Should Have (Debería tener) 🟡
- RF-007, RF-008, RF-009, RF-011
- RNF-002 (Rendimiento)
- RNF-005 (Usabilidad)

### Could Have (Podría tener) 🟢
- RF-010, RF-012
- RNF-003 (Escalabilidad)
- RNF-004 (Disponibilidad)

### Won't Have (No tendrá en v1) ⚪
- Integración real-time con SRI
- App móvil nativa
- Firma con certificado BCE
- Sistema de pagos integrado

## 8. Matriz de Trazabilidad

| Requisito | Concepto Cripto | Prioridad | Semana Impl. |
|-----------|----------------|-----------|--------------|
| RF-004 | RSA Firma Digital | Must | Semana 3 |
| RF-004 | SHA-256 Hash | Must | Semana 3 |
| RF-002 | AES-256 Cifrado | Must | Semana 3 |
| RF-008 | Bcrypt | Must | Semana 3 |
| RF-005 | QR Code | Must | Semana 3 |
| RF-007 | Verificación RSA | Should | Semana 4 |
| RF-011 | Auditoría | Should | Semana 4 |

## 9. Supuestos y Dependencias

### Supuestos
- Los usuarios tienen conocimientos básicos de facturación
- Existe infraestructura para hosting web
- Se cuenta con servidor de base de datos
- Usuario final tiene navegador moderno

### Dependencias
- Biblioteca cryptography (Python) para operaciones criptográficas
- Biblioteca qrcode para generación de QR
- PyPDF2 o ReportLab para generación de PDF
- Framework web (Flask/FastAPI)
- Frontend framework (React/Vue)

## Próximos Pasos

Con el alcance y requisitos definidos, procederemos a elaborar la propuesta formal del proyecto en el siguiente documento.
