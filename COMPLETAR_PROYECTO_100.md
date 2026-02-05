# COMPLETAR PROYECTO AL 100% - SISTEMA DE FACTURACIÓN ELECTRÓNICA

## SITUACIÓN ACTUAL
- ✅ Autenticación (JWT + Bcrypt)
- ✅ CRUD Usuarios
- ✅ CRUD Clientes (con cifrado AES-256-GCM)
- ✅ Base de datos PostgreSQL
- ❌ **FALTA: Módulo completo de Facturas con RSA, QR y SRI simulado**

---

## PROBLEMA DEL ERROR DE DESCIFRADO

**Causa**: Los clientes en la base de datos se cifraron con claves AES temporales diferentes.

**Solución DEFINITIVA**:
1. Ya creaste archivo `.env` con clave AES fija ✅
2. Necesitas **BORRAR TODOS los clientes** y reiniciar el backend

```sql
-- Ejecuta en PostgreSQL:
DELETE FROM cliente;
```

Luego reinicia el backend. Ahora todos los nuevos clientes se cifrarán con la misma clave y NO habrá errores de descifrado.

---

## LO QUE FALTA IMPLEMENTAR (60% DEL PROYECTO)

### 1. **Modelo de Factura Completo** (ya existe parcialmente)
Necesita:
- Campo para almacenar detalle JSON de productos
- QR en base64
- Datos para QR en JSON

### 2. **Servicio de Facturación (`services/factura_service.py`)**  
Debe hacer:
- Generar XML de la factura según esquema SRI
- Calcular hash SHA-256 del XML
- Firmar con RSA-2048 (clave privada de empresa)
- Generar código QR con: hash, número factura, fecha, monto, URL verificación
- Simular autorización del SRI (generar número de autorización falso)

### 3. **Rutas de Facturas (`routes/factura_routes.py`)**
Endpoints necesarios:
```
POST   /api/v1/facturas          - Crear factura (genera XML, firma, QR)
GET    /api/v1/facturas          - Listar facturas
GET    /api/v1/facturas/:id      - Ver factura individual
GET    /api/v1/facturas/:id/xml  - Descargar XML
GET    /api/v1/facturas/:id/pdf  - Descargar PDF con QR
DELETE /api/v1/facturas/:id      - Anular factura

# Verificación pública (sin autenticación)
GET    /api/v1/verificar/:hash   - Verificar factura por hash del QR
```

### 4. **Componente Frontend de Facturas**
Debe tener:
- Formulario para crear factura (seleccionar cliente, agregar productos)
- Tabla listando facturas con botón para ver QR
- Modal mostrando QR grande para escanear
- Botones de descarga XML/PDF

### 5. **Página Pública de Verificación**
- Sin necesidad de login
- Escanea QR o ingresa hash manual
- Muestra: ✅ VÁLIDA o ❌ ALTERADA
- Detalles de la factura verificada

---

## RESUMEN TÉCNICO DE LA IMPLEMENTACIÓN

### **Proceso de Creación de Factura:**

```
1. Usuario crea factura → Frontend envía datos
2. Backend:
   a. Genera XML según esquema SRI Ecuador
   b. Calcula SHA-256 del XML
   c. Firma el hash con RSA privada de empresa
   d. Genera número de autorización simulado (49 dígitos)
   e. Crea código QR con:
      - Hash SHA-256
      - Número de factura
      - Fecha
      - Monto total
      - URL: https://tudominio.com/verificar/{hash}
   f. Guarda todo en base de datos
3. Frontend muestra factura con QR visible
```

### **Proceso de Verificación (QR):**

```
1. Cliente escanea QR → Abre URL de verificación
2. Backend:
   a. Busca factura por hash
   b. Recalcula hash del XML almacenado
   c. Compara: hash_almacenado === hash_calculado
   d. Verifica firma RSA con clave pública
3. Muestra resultado:
   ✅ FACTURA VÁLIDA (no alterada)
   ❌ FACTURA ALTERADA (hash no coincide)
```

---

## SIMULACIÓN DEL SRI (Para Demostración)

**NO necesitas conectarte al SRI real**. Solo simula:

1. **Número de autorización**: Generar 49 dígitos aleatorios
   ```python
   import random
   num_autorizacion = ''.join([str(random.randint(0, 9)) for _ in range(49)])
   ```

2. **Estado**: Siempre retornar "AUTORIZADA"

3. **XML**: Crear XML que PAREZCA oficial pero es simulado

4. **Fecha de autorización**: Fecha actual

**Para el profesor**: El sistema funciona completo, genera XML válido, firma RSA real, QR funcional. Solo no se envía al SRI real porque es demo educativa.

---

## PRIORIDAD DE IMPLEMENTACIÓN

### **PASO 1: Arreglar datos cifrados (10 min)**
```sql
DELETE FROM cliente;
```
Reiniciar backend. Ya no habrá errores de descifrado.

### **PASO 2: Crear servicio de facturación (30 min)**
- Generar XML simple
- Calcular SHA-256
- Firmar con RSA (ya tienes crypto_service)
- Generar QR con biblioteca `qrcode`

### **PASO 3: Crear rutas de facturas (20 min)**
- CRUD básico
- Endpoint de verificación pública

### **PASO 4: Frontend facturas (40 min)**
- Formulario de creación
- Lista de facturas
- Mostrar QR

### **PASO 5: Página de verificación (30 min)**
- Ruta pública
- Escanear/ingresar hash
- Mostrar resultado

---

## CÓDIGO QR - LO MÁS IMPORTANTE

El QR debe contener (en formato JSON o texto plano):

```json
{
  "numero": "001-001-000000123",
  "fecha": "2026-01-19",
  "hash": "a3f5b2c...",
  "total": "112.00",
  "url": "https://facturasegura.com/verificar/a3f5b2c..."
}
```

Al escanear, abre la URL y el sistema:
1. Extrae el hash de la URL
2. Busca factura con ese hash
3. Recalcula hash del XML
4. Compara y verifica firma RSA
5. Muestra ✅ VÁLIDA o ❌ ALTERADA

---

## DEMO PARA EL PROFESOR

Flujo completo para mostrar:

1. **Login como Admin**
2. **Crear Cliente** (datos se cifran con AES-256)
3. **Crear Factura** (productos, cantidades, precios)
4. **Ver Factura generada** con:
   - Código QR grande
   - Botón "Descargar XML"
   - Número de autorización SRI (simulado)
   - Hash SHA-256 visible
5. **Escanear QR con celular** → Abre página de verificación
6. **Verificación muestra**:
   - ✅ FACTURA VÁLIDA
   - No ha sido alterada
   - Firma digital verificada
   - Todos los detalles de la factura

---

## BIBLIOTECAS NECESARIAS

Ya tienes la mayoría. Solo asegúrate de tener en `requirements.txt`:

```txt
qrcode==7.4.2
Pillow==10.2.0
```

Instalar:
```bash
pip install qrcode Pillow
```

---

## ESTADO FINAL ESPERADO

✅ 100% Funcional para demostración
✅ Cifrado AES-256-GCM de clientes
✅ Firma digital RSA-2048 de facturas
✅ Hash SHA-256 para integridad
✅ Códigos QR funcionales
✅ Verificación pública sin login
✅ XML simulado del SRI
✅ Número de autorización SRI (falso pero realista)
✅ Dashboard con estadísticas
✅ Auditoría completa en BD

---

## TIEMPO ESTIMADO TOTAL

- Arreglar cifrado: **10 minutos**
- Implementar facturas backend: **1 hora**
- Implementar facturas frontend: **1 hora**
- Pruebas y ajustes: **30 minutos**

**Total: ~2.5 horas** para tener el proyecto 100% funcional.

---

## SIGUIENTE PASO INMEDIATO

1. Ejecuta: `DELETE FROM cliente;` en PostgreSQL
2. Reinicia el backend
3. Crea un cliente nuevo
4. Edítalo → Ya NO verás errores de descifrado

Luego podemos implementar el módulo de facturas completo paso a paso.

¿Quieres que implemente el servicio de facturación ahora?
