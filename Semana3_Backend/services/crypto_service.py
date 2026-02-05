"""
Servicio de Criptografía
RSA, AES-256-GCM, SHA-256, QR Codes
"""
import base64
import hashlib
import qrcode
from io import BytesIO
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.backends import default_backend
import os


class CryptoService:
    """Servicio centralizado de criptografía"""
    
    def __init__(self, aes_master_key_b64):
        """
        Inicializar servicio con clave AES maestra
        
        Args:
            aes_master_key_b64: Clave AES en formato base64 (32 bytes)
        """
        self.aes_master_key = base64.b64decode(aes_master_key_b64)
        if len(self.aes_master_key) != 32:
            raise ValueError("AES master key debe ser de 32 bytes")
    
    # ========================================================================
    # RSA - FIRMA DIGITAL
    # ========================================================================
    
    def generar_par_claves_rsa(self):
        """
        Generar par de claves RSA-2048
        
        Returns:
            tuple: (clave_privada_pem, clave_publica_pem)
        """
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        
        # Serializar clave privada (sin contraseña)
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ).decode('utf-8')
        
        # Serializar clave pública
        public_key = private_key.public_key()
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode('utf-8')
        
        return private_pem, public_pem
    
    def firmar_rsa(self, mensaje, private_key_pem):
        """
        Firmar mensaje con RSA-2048 + SHA-256
        
        Args:
            mensaje: Texto a firmar (str)
            private_key_pem: Clave privada en formato PEM
            
        Returns:
            str: Firma en base64
        """
        # Cargar clave privada
        private_key = serialization.load_pem_private_key(
            private_key_pem.encode('utf-8'),
            password=None,
            backend=default_backend()
        )
        
        # Firmar
        signature = private_key.sign(
            mensaje.encode('utf-8'),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        
        return base64.b64encode(signature).decode('utf-8')
    
    def verificar_firma_rsa(self, mensaje, firma_b64, public_key_pem):
        """
        Verificar firma RSA
        
        Args:
            mensaje: Texto original (str)
            firma_b64: Firma en base64
            public_key_pem: Clave pública en formato PEM
            
        Returns:
            bool: True si la firma es válida
        """
        try:
            # Cargar clave pública
            public_key = serialization.load_pem_public_key(
                public_key_pem.encode('utf-8'),
                backend=default_backend()
            )
            
            # Decodificar firma
            signature = base64.b64decode(firma_b64)
            
            # Verificar
            public_key.verify(
                signature,
                mensaje.encode('utf-8'),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            
            return True
            
        except Exception as e:
            print(f"❌ Error verificando firma: {str(e)}")
            return False
    
    # ========================================================================
    # AES-256-GCM - CIFRADO SIMÉTRICO
    # ========================================================================
    
    def cifrar_aes_gcm(self, texto):
        """
        Cifrar texto con AES-256-GCM
        
        Args:
            texto: Texto a cifrar (str)
            
        Returns:
            dict: {iv: bytes, ciphertext: bytes, tag: bytes}
        """
        if not texto:
            return {'iv': b'', 'ciphertext': b'', 'tag': b''}
        
        # Generar IV aleatorio (12 bytes recomendado para GCM)
        iv = os.urandom(12)
        
        # Cifrar
        aesgcm = AESGCM(self.aes_master_key)
        ciphertext = aesgcm.encrypt(iv, texto.encode('utf-8'), None)
        
        # GCM incluye el tag en el ciphertext (últimos 16 bytes)
        tag = ciphertext[-16:]
        ciphertext_only = ciphertext[:-16]
        
        return {
            'iv': iv,
            'ciphertext': ciphertext_only,
            'tag': tag
        }
    
    def descifrar_aes_gcm(self, iv, ciphertext, tag):
        """
        Descifrar con AES-256-GCM
        
        Args:
            iv: IV (bytes)
            ciphertext: Texto cifrado (bytes)
            tag: Tag de autenticación (bytes)
            
        Returns:
            str: Texto descifrado
        """
        if not ciphertext:
            return ''
        
        try:
            # Reconstruir ciphertext completo (ciphertext + tag)
            full_ciphertext = ciphertext + tag
            
            # Descifrar
            aesgcm = AESGCM(self.aes_master_key)
            plaintext = aesgcm.decrypt(iv, full_ciphertext, None)
            
            return plaintext.decode('utf-8')
            
        except Exception as e:
            print(f"❌ Error descifrando: {str(e)}")
            return '[ERROR_DESCIFRADO]'
    
    # ========================================================================
    # SHA-256 - HASH
    # ========================================================================
    
    def calcular_hash_sha256(self, datos):
        """
        Calcular hash SHA-256
        
        Args:
            datos: Texto o diccionario a hashear
            
        Returns:
            str: Hash en hexadecimal
        """
        if isinstance(datos, dict):
            import json
            datos = json.dumps(datos, sort_keys=True)
        
        return hashlib.sha256(datos.encode('utf-8')).hexdigest()
    
    # ========================================================================
    # QR CODE
    # ========================================================================
    
    def generar_qr(self, datos):
        """
        Generar código QR
        
        Args:
            datos: Texto a codificar en QR
            
        Returns:
            BytesIO: Imagen QR en memoria
        """
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(datos)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Guardar en memoria
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        return buffer


# Instancia global
_crypto_service = None


def init_crypto_service(aes_master_key_b64):
    """Inicializar servicio global"""
    global _crypto_service
    _crypto_service = CryptoService(aes_master_key_b64)
    print("✅ CryptoService inicializado")


def get_crypto_service():
    """Obtener instancia del servicio"""
    if _crypto_service is None:
        raise RuntimeError("CryptoService no ha sido inicializado")
    return _crypto_service
