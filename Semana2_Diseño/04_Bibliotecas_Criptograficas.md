# Bibliotecas Criptográficas - Sistema de Facturación Electrónica

## 1. Resumen de Selección

| Tecnología | Biblioteca Python | Versión | Licencia | Justificación |
|-----------|-------------------|---------|----------|---------------|
| **RSA** | `cryptography` | 41.0+ | Apache 2.0 / BSD | Estándar de facto, bien mantenida, auditoría |
| **AES** | `cryptography` | 41.0+ | Apache 2.0 / BSD | Misma biblioteca, consistencia |
| **SHA-256** | `hashlib` | stdlib | PSF | Nativa de Python, rápida, confiable |
| **Bcrypt** | `bcrypt` | 4.1+ | Apache 2.0 | Especializada en passwords, salt automático |
| **JWT** | `PyJWT` | 2.8+ | MIT | Ampliamente adoptada, bien documentada |
| **QR Code** | `qrcode` + `pillow` | 7.4+ / 10.0+ | BSD / HPND | Generación simple, flexible |
| **XML** | `lxml` | 4.9+ | BSD | Parser rápido, XPath support |
| **PDF** | `reportlab` | 4.0+ | BSD | Profesional, flexible, bien documentado |

## 2. Biblioteca Principal: `cryptography`

### 2.1 Información General

**Nombre**: `cryptography`  
**Versión recomendada**: 41.0.7 o superior  
**Sitio oficial**: https://cryptography.io/  
**GitHub**: https://github.com/pyca/cryptography  
**Documentación**: https://cryptography.io/en/latest/

**Ventajas**:
- ✅ Biblioteca de criptografía de nivel empresarial
- ✅ Respaldada por la Python Cryptographic Authority (PyCA)
- ✅ Auditorías de seguridad regulares
- ✅ Bindings a OpenSSL (C backend rápido)
- ✅ API de alto nivel (recipes) y bajo nivel (hazmat)
- ✅ Soporte multiplataforma (Windows, Linux, macOS)
- ✅ Mantenimiento activo y actualizaciones frecuentes

**Desventajas**:
- ⚠️ Requiere compilación de extensiones C (puede complicar deployment)
- ⚠️ Tamaño de instalación más grande que alternativas

### 2.2 Instalación

```bash
pip install cryptography==41.0.7
```

**Dependencias**:
- `cffi` (Foreign Function Interface)
- `pycparser`
- OpenSSL 1.1.1+ (generalmente incluido)

### 2.3 Implementación RSA

#### Generación de Claves

```python
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.backends import default_backend
import os

def generar_par_claves_rsa(tamaño_bits=2048):
    """
    Genera un par de claves RSA (pública y privada)
    
    Args:
        tamaño_bits: 2048 (recomendado) o 4096 (máxima seguridad)
        
    Returns:
        tuple: (clave_privada, clave_publica)
    """
    # Generar clave privada
    clave_privada = rsa.generate_private_key(
        public_exponent=65537,  # Estándar F4
        key_size=tamaño_bits,
        backend=default_backend()
    )
    
    # Extraer clave pública
    clave_publica = clave_privada.public_key()
    
    return clave_privada, clave_publica


def guardar_clave_privada(clave_privada, ruta_archivo, password=None):
    """
    Guarda la clave privada en formato PEM (opcionalmente cifrada)
    
    Args:
        clave_privada: Objeto RSAPrivateKey
        ruta_archivo: Ruta donde guardar el archivo
        password: Contraseña para cifrar (bytes) o None
    """
    if password:
        encryption_algorithm = serialization.BestAvailableEncryption(password)
    else:
        encryption_algorithm = serialization.NoEncryption()
    
    pem = clave_privada.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=encryption_algorithm
    )
    
    with open(ruta_archivo, 'wb') as f:
        f.write(pem)
    
    # Establecer permisos restrictivos (solo lectura para owner)
    os.chmod(ruta_archivo, 0o400)


def guardar_clave_publica(clave_publica, ruta_archivo):
    """
    Guarda la clave pública en formato PEM
    
    Args:
        clave_publica: Objeto RSAPublicKey
        ruta_archivo: Ruta donde guardar el archivo
    """
    pem = clave_publica.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    
    with open(ruta_archivo, 'wb') as f:
        f.write(pem)


def cargar_clave_privada(ruta_archivo, password=None):
    """
    Carga una clave privada desde archivo PEM
    
    Args:
        ruta_archivo: Ruta del archivo
        password: Contraseña si está cifrada (bytes)
        
    Returns:
        RSAPrivateKey
    """
    with open(ruta_archivo, 'rb') as f:
        pem_data = f.read()
    
    return serialization.load_pem_private_key(
        pem_data,
        password=password,
        backend=default_backend()
    )


def cargar_clave_publica(ruta_archivo):
    """
    Carga una clave pública desde archivo PEM
    
    Args:
        ruta_archivo: Ruta del archivo
        
    Returns:
        RSAPublicKey
    """
    with open(ruta_archivo, 'rb') as f:
        pem_data = f.read()
    
    return serialization.load_pem_public_key(
        pem_data,
        backend=default_backend()
    )
```

#### Firma Digital

```python
import hashlib
import base64

def firmar_documento(documento, clave_privada):
    """
    Firma digitalmente un documento con RSA-PSS
    
    Args:
        documento: Datos a firmar (bytes o str)
        clave_privada: RSAPrivateKey
        
    Returns:
        str: Firma en base64
    """
    # Convertir a bytes si es string
    if isinstance(documento, str):
        documento = documento.encode('utf-8')
    
    # Calcular hash SHA-256 del documento
    hash_documento = hashlib.sha256(documento).digest()
    
    # Firmar el hash
    firma = clave_privada.sign(
        hash_documento,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    
    # Retornar en base64 para almacenamiento
    return base64.b64encode(firma).decode('utf-8')


def verificar_firma(documento, firma_b64, clave_publica):
    """
    Verifica la firma digital de un documento
    
    Args:
        documento: Datos originales (bytes o str)
        firma_b64: Firma en base64 (str)
        clave_publica: RSAPublicKey
        
    Returns:
        bool: True si válida, False si inválida
    """
    # Convertir documento a bytes
    if isinstance(documento, str):
        documento = documento.encode('utf-8')
    
    # Decodificar firma
    firma = base64.b64decode(firma_b64)
    
    # Calcular hash
    hash_documento = hashlib.sha256(documento).digest()
    
    try:
        # Verificar firma
        clave_publica.verify(
            firma,
            hash_documento,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return True
    except Exception:
        return False


def calcular_hash_sha256(documento):
    """
    Calcula el hash SHA-256 de un documento
    
    Args:
        documento: Datos a hashear (bytes o str)
        
    Returns:
        str: Hash en hexadecimal (64 caracteres)
    """
    if isinstance(documento, str):
        documento = documento.encode('utf-8')
    
    return hashlib.sha256(documento).hexdigest()
```

#### Ejemplo de Uso: Firmar Factura

```python
# Paso 1: Generar claves (una vez al configurar empresa)
clave_privada, clave_publica = generar_par_claves_rsa(2048)
guardar_clave_privada(clave_privada, 'empresa_privada.pem', password=b'clave_segura')
guardar_clave_publica(clave_publica, 'empresa_publica.pem')

# Paso 2: Al crear factura
xml_factura = """<?xml version="1.0" encoding="UTF-8"?>
<factura>
    <infoTributaria>
        <ruc>1234567890001</ruc>
        <numeroFactura>001-001-000000123</numeroFactura>
    </infoTributaria>
    <!-- más XML -->
</factura>"""

# Calcular hash
hash_factura = calcular_hash_sha256(xml_factura)
print(f"Hash SHA-256: {hash_factura}")

# Cargar clave privada
clave_privada = cargar_clave_privada('empresa_privada.pem', password=b'clave_segura')

# Firmar
firma_digital = firmar_documento(xml_factura, clave_privada)
print(f"Firma digital: {firma_digital[:50]}...")

# Paso 3: Verificación (por cliente o SRI)
clave_publica = cargar_clave_publica('empresa_publica.pem')
es_valida = verificar_firma(xml_factura, firma_digital, clave_publica)
print(f"Firma válida: {es_valida}")
```

### 2.4 Implementación AES-GCM

```python
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import os
import base64

def generar_clave_aes():
    """
    Genera una clave AES-256 aleatoria (32 bytes)
    
    Returns:
        bytes: Clave de 256 bits
    """
    return os.urandom(32)


def cifrar_aes_gcm(datos, clave_maestra):
    """
    Cifra datos con AES-256-GCM
    
    Args:
        datos: Datos a cifrar (str o bytes)
        clave_maestra: Clave AES de 256 bits (32 bytes)
        
    Returns:
        dict: {
            'datos_cifrados': str (base64),
            'iv': str (base64),
            'tag': str (base64)
        }
    """
    # Convertir a bytes si es string
    if isinstance(datos, str):
        datos = datos.encode('utf-8')
    
    # Generar IV único (12 bytes para GCM)
    iv = os.urandom(12)
    
    # Crear cifrador AES-GCM
    cipher = Cipher(
        algorithms.AES(clave_maestra),
        modes.GCM(iv),
        backend=default_backend()
    )
    
    encryptor = cipher.encryptor()
    
    # Cifrar
    datos_cifrados = encryptor.update(datos) + encryptor.finalize()
    
    # Retornar todo en base64
    return {
        'datos_cifrados': base64.b64encode(datos_cifrados).decode('utf-8'),
        'iv': base64.b64encode(iv).decode('utf-8'),
        'tag': base64.b64encode(encryptor.tag).decode('utf-8')
    }


def descifrar_aes_gcm(datos_cifrados_b64, iv_b64, tag_b64, clave_maestra):
    """
    Descifra datos cifrados con AES-256-GCM
    
    Args:
        datos_cifrados_b64: Datos cifrados en base64
        iv_b64: IV en base64
        tag_b64: Tag de autenticación en base64
        clave_maestra: Clave AES de 256 bits
        
    Returns:
        str: Datos descifrados
        
    Raises:
        InvalidTag: Si los datos fueron manipulados
    """
    # Decodificar de base64
    datos_cifrados = base64.b64decode(datos_cifrados_b64)
    iv = base64.b64decode(iv_b64)
    tag = base64.b64decode(tag_b64)
    
    # Crear descifrador
    cipher = Cipher(
        algorithms.AES(clave_maestra),
        modes.GCM(iv, tag),
        backend=default_backend()
    )
    
    decryptor = cipher.decryptor()
    
    # Descifrar (lanza InvalidTag si manipulado)
    datos_planos = decryptor.update(datos_cifrados) + decryptor.finalize()
    
    return datos_planos.decode('utf-8')


# Ejemplo de uso: Cifrar datos de cliente
clave_maestra = generar_clave_aes()  # En producción, cargar de variable de entorno

# Cifrar email
email_cliente = "cliente@example.com"
email_cifrado = cifrar_aes_gcm(email_cliente, clave_maestra)
print(f"Email cifrado: {email_cifrado['datos_cifrados'][:30]}...")

# Guardar en BD: email_cifrado['datos_cifrados'], iv, tag

# Descifrar cuando se necesita
email_descifrado = descifrar_aes_gcm(
    email_cifrado['datos_cifrados'],
    email_cifrado['iv'],
    email_cifrado['tag'],
    clave_maestra
)
print(f"Email descifrado: {email_descifrado}")
```

### 2.5 Gestión de Claves

```python
import os
from pathlib import Path

class GestorClaves:
    """Gestor centralizado de claves criptográficas"""
    
    def __init__(self, directorio_claves='./keys'):
        self.directorio = Path(directorio_claves)
        self.directorio.mkdir(exist_ok=True, mode=0o700)
        
        # Cargar clave AES maestra desde variable de entorno
        clave_env = os.environ.get('AES_MASTER_KEY')
        if clave_env:
            self.clave_aes_maestra = base64.b64decode(clave_env)
        else:
            raise ValueError("AES_MASTER_KEY no configurada")
    
    def cargar_claves_rsa_empresa(self, empresa_id, password=None):
        """Carga las claves RSA de una empresa"""
        ruta_privada = self.directorio / f'empresa_{empresa_id}_privada.pem'
        ruta_publica = self.directorio / f'empresa_{empresa_id}_publica.pem'
        
        if password:
            password = password.encode() if isinstance(password, str) else password
        
        clave_privada = cargar_clave_privada(str(ruta_privada), password)
        clave_publica = cargar_clave_publica(str(ruta_publica))
        
        return clave_privada, clave_publica
    
    def cifrar_datos_sensibles(self, datos):
        """Cifra datos sensibles con AES-GCM"""
        return cifrar_aes_gcm(datos, self.clave_aes_maestra)
    
    def descifrar_datos_sensibles(self, datos_cifrados, iv, tag):
        """Descifra datos sensibles"""
        return descifrar_aes_gcm(datos_cifrados, iv, tag, self.clave_aes_maestra)
```

## 3. Biblioteca de Passwords: `bcrypt`

### 3.1 Información

**Nombre**: `bcrypt`  
**Versión**: 4.1.2  
**Documentación**: https://github.com/pyca/bcrypt

**Ventajas**:
- ✅ Diseñada específicamente para passwords
- ✅ Salt automático incluido en el hash
- ✅ Factor de trabajo configurable (adaptive)
- ✅ Resistente a ataques de fuerza bruta
- ✅ Implementación en C (rápida)

### 3.2 Instalación

```bash
pip install bcrypt==4.1.2
```

### 3.3 Implementación

```python
import bcrypt

def hashear_password(password, rounds=12):
    """
    Genera hash bcrypt de una contraseña
    
    Args:
        password: Contraseña en texto plano (str)
        rounds: Factor de trabajo (10-12 recomendado)
        
    Returns:
        str: Hash bcrypt (60 caracteres)
    """
    # Convertir a bytes
    password_bytes = password.encode('utf-8')
    
    # Generar salt y hash
    salt = bcrypt.gensalt(rounds=rounds)
    hashed = bcrypt.hashpw(password_bytes, salt)
    
    # Retornar como string
    return hashed.decode('utf-8')


def verificar_password(password, password_hash):
    """
    Verifica una contraseña contra su hash
    
    Args:
        password: Contraseña en texto plano
        password_hash: Hash almacenado
        
    Returns:
        bool: True si coincide
    """
    password_bytes = password.encode('utf-8')
    hash_bytes = password_hash.encode('utf-8')
    
    return bcrypt.checkpw(password_bytes, hash_bytes)


# Ejemplo de uso
password = "MiPassword123!"

# Registrar usuario
hash_guardado = hashear_password(password)
print(f"Hash: {hash_guardado}")
# $2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqVkP0fELy

# Login
es_valido = verificar_password("MiPassword123!", hash_guardado)
print(f"Password válido: {es_valido}")  # True

es_valido = verificar_password("PasswordIncorrecto", hash_guardado)
print(f"Password válido: {es_valido}")  # False
```

### 3.4 Validación de Fortaleza de Contraseña

```python
import re

def validar_password(password):
    """
    Valida fortaleza de contraseña
    
    Requisitos:
    - Mínimo 8 caracteres
    - Al menos una mayúscula
    - Al menos una minúscula
    - Al menos un número
    - Al menos un carácter especial
    
    Returns:
        tuple: (bool, str) - (es_valida, mensaje)
    """
    if len(password) < 8:
        return False, "La contraseña debe tener al menos 8 caracteres"
    
    if not re.search(r'[A-Z]', password):
        return False, "Debe contener al menos una mayúscula"
    
    if not re.search(r'[a-z]', password):
        return False, "Debe contener al menos una minúscula"
    
    if not re.search(r'[0-9]', password):
        return False, "Debe contener al menos un número"
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Debe contener al menos un carácter especial"
    
    return True, "Contraseña válida"
```

## 4. Generación de Códigos QR: `qrcode` + `pillow`

### 4.1 Instalación

```bash
pip install qrcode[pil]==7.4.2
pip install pillow==10.2.0
```

### 4.2 Implementación

```python
import qrcode
from PIL import Image
import json
import io

def generar_qr_factura(datos_factura, ruta_salida=None):
    """
    Genera código QR para verificación de factura
    
    Args:
        datos_factura: dict con datos de la factura
        ruta_salida: Ruta donde guardar imagen (opcional)
        
    Returns:
        PIL.Image o bytes: Imagen QR
    """
    # Preparar datos para QR
    qr_data = {
        'ruc_emisor': datos_factura['ruc_emisor'],
        'numero_factura': datos_factura['numero_factura'],
        'fecha_emision': datos_factura['fecha_emision'],
        'num_autorizacion': datos_factura['num_autorizacion'],
        'total': str(datos_factura['total']),
        'hash_sha256': datos_factura['hash_sha256'],
        'url_verificacion': f"https://sistema.com/verificar/{datos_factura['num_autorizacion']}"
    }
    
    # Convertir a JSON
    qr_json = json.dumps(qr_data, separators=(',', ':'))
    
    # Crear código QR
    qr = qrcode.QRCode(
        version=5,  # Tamaño (1-40)
        error_correction=qrcode.constants.ERROR_CORRECT_H,  # Alta corrección de errores
        box_size=10,  # Tamaño de cada "caja"
        border=4,  # Borde mínimo
    )
    
    qr.add_data(qr_json)
    qr.make(fit=True)
    
    # Generar imagen
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Guardar si se especifica ruta
    if ruta_salida:
        img.save(ruta_salida)
    
    return img


def qr_a_bytes(img_qr):
    """Convierte imagen QR a bytes para almacenar en BD"""
    buffer = io.BytesIO()
    img_qr.save(buffer, format='PNG')
    return buffer.getvalue()


# Ejemplo de uso
datos_factura = {
    'ruc_emisor': '1234567890001',
    'numero_factura': '001-001-000000123',
    'fecha_emision': '2026-01-12',
    'num_autorizacion': '1234567890' * 5 + '123456789',  # 49 dígitos
    'total': 115.00,
    'hash_sha256': 'a3f5b8c2d4e6f8a0b1c3d5e7f9a1b3c5d7e9f1a3b5c7d9e1f3a5b7c9d1e3f5a7'
}

qr_img = generar_qr_factura(datos_factura, 'factura_123_qr.png')
print("QR generado exitosamente")
```

## 5. Dependencias Completas

### 5.1 `requirements.txt`

```txt
# Core Framework
Flask==3.0.0
Flask-SQLAlchemy==3.1.1
Flask-CORS==4.0.0

# Criptografía
cryptography==41.0.7
bcrypt==4.1.2

# Tokens JWT
PyJWT==2.8.0

# QR Codes
qrcode[pil]==7.4.2
Pillow==10.2.0

# XML
lxml==4.9.4

# PDF
reportlab==4.0.9

# Base de datos
psycopg2-binary==2.9.9

# Validaciones
email-validator==2.1.0

# Utilidades
python-dotenv==1.0.0
requests==2.31.0

# Testing (desarrollo)
pytest==7.4.4
pytest-cov==4.1.0

# Logging
python-json-logger==2.0.7
```

### 5.2 Instalación Completa

```bash
# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate  # Windows

# Instalar dependencias
pip install -r requirements.txt

# Verificar instalación
pip list
```

## 6. Configuración de Variables de Entorno

```bash
# .env
# Clave secreta de Flask
SECRET_KEY=tu_clave_secreta_muy_larga_y_aleatoria

# Clave maestra AES (32 bytes en base64)
AES_MASTER_KEY=base64_encoded_32_bytes_key

# Password para claves RSA privadas
RSA_KEY_PASSWORD=password_seguro_para_claves_rsa

# Base de datos
DATABASE_URL=postgresql://user:password@localhost:5432/facturasegura

# JWT
JWT_SECRET_KEY=otra_clave_secreta_para_jwt
JWT_ACCESS_TOKEN_EXPIRES=900  # 15 minutos
JWT_REFRESH_TOKEN_EXPIRES=2592000  # 30 días

# Ambiente
ENVIRONMENT=development  # development | production
DEBUG=True
```

### Generar Claves Seguras

```python
import os
import base64

# Generar clave secreta Flask (32 bytes)
secret_key = base64.b64encode(os.urandom(32)).decode('utf-8')
print(f"SECRET_KEY={secret_key}")

# Generar clave AES maestra (32 bytes para AES-256)
aes_key = base64.b64encode(os.urandom(32)).decode('utf-8')
print(f"AES_MASTER_KEY={aes_key}")

# Generar clave JWT (32 bytes)
jwt_key = base64.b64encode(os.urandom(32)).decode('utf-8')
print(f"JWT_SECRET_KEY={jwt_key}")
```

## 7. Auditoría de Seguridad

### 7.1 Verificar Versiones

```bash
# Verificar vulnerabilidades conocidas
pip install safety
safety check

# Resultado esperado: No known security vulnerabilities found
```

### 7.2 Análisis de Código

```bash
# Instalar bandit (análisis de seguridad)
pip install bandit

# Ejecutar análisis
bandit -r . -f json -o security_report.json
```

### 7.3 Pruebas de Bibliotecas

```python
# test_crypto.py
import pytest
from services.crypto_service import CryptoService

def test_rsa_firma_verificacion():
    """Prueba de firma y verificación RSA"""
    crypto = CryptoService()
    
    # Generar claves
    privada, publica = crypto.generar_claves_rsa()
    
    # Firmar
    documento = "Factura de prueba"
    firma = crypto.firmar(documento, privada)
    
    # Verificar
    assert crypto.verificar(documento, firma, publica) == True
    
    # Verificar con documento alterado
    assert crypto.verificar("Documento alterado", firma, publica) == False


def test_aes_cifrado_descifrado():
    """Prueba de cifrado y descifrado AES"""
    crypto = CryptoService()
    
    # Datos originales
    datos_sensibles = "cliente@example.com"
    
    # Cifrar
    cifrado = crypto.cifrar_aes(datos_sensibles)
    
    # Descifrar
    descifrado = crypto.descifrar_aes(
        cifrado['datos_cifrados'],
        cifrado['iv'],
        cifrado['tag']
    )
    
    assert descifrado == datos_sensibles


def test_bcrypt_password():
    """Prueba de hashing y verificación de passwords"""
    password = "TestPassword123!"
    
    # Hashear
    hash_password = hashear_password(password)
    
    # Verificar correcto
    assert verificar_password(password, hash_password) == True
    
    # Verificar incorrecto
    assert verificar_password("WrongPassword", hash_password) == False


# Ejecutar pruebas
# pytest test_crypto.py -v
```

## 8. Consideraciones de Rendimiento

| Operación | Tiempo Esperado | Notas |
|-----------|-----------------|-------|
| Generar par RSA-2048 | ~500ms | Una vez por empresa |
| Firmar con RSA | ~10-50ms | Por factura |
| Verificar firma RSA | ~5-20ms | Por verificación |
| Cifrar con AES-GCM | <1ms | Por campo |
| Descifrar con AES-GCM | <1ms | Por campo |
| Hash bcrypt (12 rounds) | ~100-300ms | Por login |
| Hash SHA-256 | <1ms | Por factura |
| Generar QR | ~50-100ms | Por factura |

## 9. Recomendaciones de Seguridad

1. **Nunca almacenar claves privadas sin cifrar**
2. **Rotar claves AES anualmente**
3. **Backup cifrado de claves RSA**
4. **Usar variables de entorno para secretos**
5. **Auditar accesos a datos cifrados**
6. **Mantener bibliotecas actualizadas**
7. **Implementar rate limiting**
8. **Logs de operaciones criptográficas**

## Resumen

Con esta selección de bibliotecas tenemos:
- ✅ **Seguridad robusta**: Bibliotecas auditadas y mantenidas
- ✅ **Cumplimiento legal**: Algoritmos aprobados para Ecuador
- ✅ **Rendimiento adecuado**: Operaciones en milisegundos
- ✅ **Facilidad de uso**: APIs bien documentadas
- ✅ **Mantenibilidad**: Stack estándar de Python

¡Diseño de la Semana 2 completado!
