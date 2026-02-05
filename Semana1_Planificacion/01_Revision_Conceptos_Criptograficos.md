# Revisión de Conceptos Criptográficos

## 1. Firma Digital RSA

### Concepto
La firma digital RSA es un mecanismo criptográfico que garantiza la autenticidad e integridad de documentos electrónicos, proporcionando validez legal a las facturas.

### Funcionamiento
1. **Generación de Claves**: Se crean un par de claves (pública y privada)
   - Clave privada: Secreta, usada para firmar facturas
   - Clave pública: Compartida, usada para verificar firmas

2. **Proceso de Firma**:
   ```
   Hash(Factura) + Clave_Privada → Firma_Digital
   ```

3. **Proceso de Verificación**:
   ```
   Firma_Digital + Clave_Pública → Hash_Original
   Hash(Factura_Recibida) == Hash_Original → Válida
   ```

### Ventajas para Facturación
- Validez legal en Ecuador (Ley de Comercio Electrónico)
- No repudio: El emisor no puede negar haber firmado
- Autenticidad: Verifica la identidad del emisor
- Integridad: Detecta cualquier modificación

### Tamaño de Clave
- **Recomendado**: RSA-2048 o RSA-4096
- **Justificación**: Balance entre seguridad y rendimiento

## 2. Hash SHA-256

### Concepto
Función hash criptográfica que genera una "huella digital" única de 256 bits para cada factura.

### Características
- **Determinista**: Mismo input → mismo output
- **Unidireccional**: Imposible recuperar el documento original
- **Efecto avalancha**: Cambio mínimo → hash completamente diferente
- **Resistente a colisiones**: Prácticamente imposible encontrar dos facturas con el mismo hash

### Aplicación en Facturas
```python
import hashlib

factura_data = {
    "numero": "001-001-000123456",
    "fecha": "2026-01-12",
    "total": 150.50,
    "cliente": "Juan Pérez",
    # ... más datos
}

# Generar hash
factura_json = json.dumps(factura_data, sort_keys=True)
hash_factura = hashlib.sha256(factura_json.encode()).hexdigest()
```

### Beneficios
-  Detección de alteraciones
-  Auditoría de integridad
-  Cálculo rápido
-  Tamaño fijo (64 caracteres hexadecimales)

## 3. Cifrado AES-256

### Concepto
Advanced Encryption Standard con clave de 256 bits para cifrado simétrico de datos sensibles del cliente.

### Datos a Cifrar
- RUC/Cédula del cliente
- Dirección fiscal
- Correo electrónico
- Teléfono
- Información bancaria (si aplica)

### Modos de Operación
**Recomendado: AES-GCM (Galois/Counter Mode)**
- Cifrado + autenticación
- Detecta manipulación de datos cifrados
- Mejor rendimiento que CBC con HMAC

### Ejemplo de Implementación
```python
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import os

def cifrar_datos_cliente(datos_sensibles, clave_maestra):
    # Generar IV único
    iv = os.urandom(16)
    
    # Crear cifrador AES-GCM
    cipher = Cipher(
        algorithms.AES(clave_maestra),
        modes.GCM(iv),
        backend=default_backend()
    )
    
    encryptor = cipher.encryptor()
    datos_cifrados = encryptor.update(datos_sensibles.encode()) + encryptor.finalize()
    
    return {
        'iv': iv,
        'datos_cifrados': datos_cifrados,
        'tag': encryptor.tag  # Para autenticación
    }
```

### Gestión de Claves
- Clave maestra almacenada en variables de entorno
- Rotación periódica de claves
- Backup seguro de claves

## 4. Bcrypt para Autenticación

### Concepto
Función hash diseñada específicamente para contraseñas, con "salt" automático y factor de trabajo configurable.

### Características Clave
- **Salt aleatorio**: Protege contra rainbow tables
- **Trabajo adaptable**: Se puede aumentar el costo computacional con el tiempo
- **Lento por diseño**: Dificulta ataques de fuerza bruta

### Implementación
```python
import bcrypt

# Registro de usuario
def registrar_usuario(username, password):
    # Generar hash (salt incluido automáticamente)
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=12))
    # Guardar username + hashed en BD
    
# Login
def verificar_login(username, password):
    # Recuperar hash de BD
    stored_hash = obtener_hash_de_bd(username)
    # Verificar
    return bcrypt.checkpw(password.encode(), stored_hash)
```

### Factor de Trabajo
- **Recomendado**: 12 rounds
- Tiempo de hash: ~100-300ms (aceptable para login)
- Aumentar en el futuro según capacidad de cómputo

## 5. Códigos QR para Verificación

### Concepto
Código de respuesta rápida que contiene información de verificación de la factura.

### Contenido del QR
```json
{
    "numero_autorizacion": "1234567890123456789012345678901234567890",
    "fecha_autorizacion": "2026-01-12T10:30:00",
    "ruc_emisor": "1234567890001",
    "hash_factura": "a3f5b8c2d4e6f8g0h2i4j6k8l0m2n4p6q8r0s2t4u6v8w0x2y4z6",
    "url_verificacion": "https://sri.gob.ec/verificar"
}
```

### Generación
```python
import qrcode

def generar_qr_factura(datos_verificacion):
    qr = qrcode.QRCode(
        version=5,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(json.dumps(datos_verificacion))
    qr.make(fit=True)
    return qr.make_image(fill_color="black", back_color="white")
```

### Beneficios
-  Verificación instantánea por clientes
-  Compatibilidad con app del SRI
-  No requiere conexión constante
-  Fácil auditoría física

## 6. Estándares y Normativas Ecuatorianas

### Resoluciones del SRI
- **NAC-DGERCGC15-00000284**: Facturación electrónica
- **NAC-DGERCGC16-00000423**: Firma electrónica
- Formato XML conforme a XSD del SRI

### Requisitos Legales de Firma Digital
1. Certificado digital emitido por entidad certificadora acreditada
2. Algoritmo RSA mínimo 2048 bits
3. Timestamp del momento de firma
4. Cadena de certificación completa

### Formato de Factura Electrónica
- XML firmado digitalmente (XAdES-BES)
- Autorización del SRI (número de 49 dígitos)
- Clave de acceso de 49 dígitos
- Ambiente: Producción o Pruebas

## 7. Arquitectura de Seguridad Multicapa

```
┌─────────────────────────────────────────┐
│        CAPA DE PRESENTACIÓN             │
│  - HTTPS (TLS 1.3)                     │
│  - QR de verificación                  │
└─────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│         CAPA DE APLICACIÓN              │
│  - Autenticación (Bcrypt)              │
│  - Autorización (JWT)                  │
│  - Validación de entrada               │
└─────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│      CAPA DE LÓGICA DE NEGOCIO         │
│  - Generación de facturas              │
│  - Firma digital RSA                   │
│  - Cálculo de hash SHA-256             │
└─────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│         CAPA DE DATOS                   │
│  - Cifrado AES de datos sensibles      │
│  - Hashing de contraseñas (Bcrypt)     │
│  - Integridad con hash SHA-256         │
└─────────────────────────────────────────┘
```

## 8. Resumen de Aplicaciones

| Tecnología | Propósito | Justificación |
|-----------|-----------|---------------|
| **RSA-2048** | Firma digital de facturas | Validez legal, no repudio |
| **SHA-256** | Hash de facturas | Integridad, detección de alteraciones |
| **AES-256-GCM** | Cifrado de datos del cliente | Confidencialidad + autenticación |
| **Bcrypt** | Hash de contraseñas | Protección de cuentas de usuario |
| **QR Code** | Verificación rápida | Usabilidad, cumplimiento SRI |
| **TLS 1.3** | Transporte seguro | Confidencialidad en tránsito |

## Próximos Pasos

En la siguiente sección definiremos el alcance completo del sistema y los requisitos específicos basados en estos fundamentos criptográficos.
