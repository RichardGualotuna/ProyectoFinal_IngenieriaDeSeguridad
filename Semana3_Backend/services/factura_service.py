"""
Servicio de Facturación Electrónica con Criptografía
- Generación de XML según esquema SRI Ecuador
- Firma digital RSA-2048 con SHA-256
- Generación de códigos QR con datos de verificación
- Simulación de autorización SRI
"""

import os
import base64
import hashlib
import qrcode
from io import BytesIO
from datetime import datetime
from decimal import Decimal
from lxml import etree
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend

from models import db
from models.factura import Factura
from models.cliente import Cliente
from services.crypto_service import get_crypto_service


class FacturaService:
    """Servicio para gestión de facturas electrónicas con criptografía"""
    
    def __init__(self):
        """
        Inicializar servicio con CryptoService y obtener/crear claves RSA desde BD
        """
        from models.configuracion import Configuracion
        
        self.crypto_service = get_crypto_service()
        
        print("🔍 Buscando claves RSA en configuracion...")
        
        # Obtener o crear claves RSA desde configuracion
        config_rsa = Configuracion.query.filter_by(clave='rsa_keys').first()
        
        if config_rsa and config_rsa.valor:
            # Usar claves existentes
            import json
            self.rsa_keys = json.loads(config_rsa.valor)
            print("✅ FacturaService inicializado con RSA-2048 existente desde BD")
        else:
            # Generar nuevas claves y almacenarlas
            print("🔑 Generando nuevo par de claves RSA-2048...")
            private_pem, public_pem = self.crypto_service.generar_par_claves_rsa()
            self.rsa_keys = {
                'private_key': private_pem,
                'public_key': public_pem
            }
            
            # Guardar en BD
            import json
            if config_rsa:
                config_rsa.valor = json.dumps(self.rsa_keys)
                print("♻️  Actualizando claves RSA en configuracion")
            else:
                config_rsa = Configuracion(
                    clave='rsa_keys',
                    valor=json.dumps(self.rsa_keys),
                    descripcion='Claves RSA-2048 para firma digital de facturas'
                )
                db.session.add(config_rsa)
                print("💾 Creando registro de claves RSA en configuracion")
            
            try:
                db.session.commit()
                print("✅ FacturaService inicializado con RSA-2048 nuevo y almacenado en BD")
            except Exception as e:
                print(f"❌ Error almacenando claves RSA: {e}")
                db.session.rollback()
        
    def generar_numero_factura(self) -> str:
        """
        Genera número de factura secuencial formato SRI:
        001-001-000000001
        """
        ultima_factura = Factura.query.order_by(Factura.id.desc()).first()
        
        if not ultima_factura:
            secuencial = 1
        else:
            # Extraer secuencial del número anterior
            partes = ultima_factura.numero_factura.split('-')
            secuencial = int(partes[2]) + 1
        
        return f"001-001-{secuencial:09d}"
    
    def calcular_totales(self, items: list) -> dict:
        """
        Calcula totales de la factura
        Args:
            items: Lista de ítems con {producto_id, cantidad, precio_unitario, iva_porcentaje}
        Returns:
            dict con subtotal, iva, total
        """
        subtotal = Decimal('0.00')
        total_iva = Decimal('0.00')
        
        for item in items:
            cantidad = Decimal(str(item['cantidad']))
            precio = Decimal(str(item['precio_unitario']))
            iva_pct = Decimal(str(item.get('iva_porcentaje', 15)))
            
            subtotal_item = cantidad * precio
            iva_item = subtotal_item * (iva_pct / Decimal('100'))
            
            subtotal += subtotal_item
            total_iva += iva_item
        
        total = subtotal + total_iva
        
        return {
            'subtotal': float(subtotal),
            'iva': float(total_iva),
            'total': float(total)
        }
    
    def generar_xml_factura(self, factura_data: dict, cliente: Cliente, items: list) -> str:
        """
        Genera XML de factura según esquema SRI Ecuador (simplificado)
        """
        # Descifrar datos del cliente
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        if cliente.nombres_enc:
            encrypted_data = cliente.nombres_enc + cliente.tag
            aesgcm = AESGCM(self.crypto_service.aes_master_key)
            decrypted_all = aesgcm.decrypt(cliente.iv, encrypted_data, None).decode('utf-8')
            partes = decrypted_all.split('|')
            decrypted_data = {
                'nombres': partes[0] if len(partes) > 0 else '',
                'apellidos': partes[1] if len(partes) > 1 else '',
                'direccion': partes[2] if len(partes) > 2 else '',
                'telefono': partes[3] if len(partes) > 3 else '',
                'email': partes[4] if len(partes) > 4 else ''
            }
        else:
            decrypted_data = {
                'nombres': '',
                'apellidos': '',
                'direccion': '',
                'telefono': '',
                'email': ''
            }
        cliente_datos = cliente.to_dict(decrypted_data=decrypted_data)
        
        # Crear estructura XML
        root = etree.Element("factura", version="1.0.0")
        
        # InfoTributaria
        info_tributaria = etree.SubElement(root, "infoTributaria")
        etree.SubElement(info_tributaria, "ambiente").text = "1"  # 1=Pruebas, 2=Producción
        etree.SubElement(info_tributaria, "tipoEmision").text = "1"  # Normal
        etree.SubElement(info_tributaria, "razonSocial").text = factura_data.get('empresa_razon_social', 'Mi Empresa S.A.')
        etree.SubElement(info_tributaria, "nombreComercial").text = "Mi Empresa"
        etree.SubElement(info_tributaria, "ruc").text = factura_data.get('empresa_ruc', '1234567890001')
        etree.SubElement(info_tributaria, "claveAcceso").text = self._generar_clave_acceso(factura_data)
        etree.SubElement(info_tributaria, "codDoc").text = "01"  # 01=Factura
        etree.SubElement(info_tributaria, "estab").text = "001"
        etree.SubElement(info_tributaria, "ptoEmi").text = "001"
        etree.SubElement(info_tributaria, "secuencial").text = factura_data['numero_factura'].split('-')[2]
        etree.SubElement(info_tributaria, "dirMatriz").text = "Av. Principal 123, Quito"
        
        # InfoFactura
        info_factura = etree.SubElement(root, "infoFactura")
        etree.SubElement(info_factura, "fechaEmision").text = factura_data['fecha_emision'].strftime('%d/%m/%Y')
        etree.SubElement(info_factura, "dirEstablecimiento").text = "Av. Principal 123"
        etree.SubElement(info_factura, "obligadoContabilidad").text = "SI"
        etree.SubElement(info_factura, "tipoIdentificacionComprador").text = cliente_datos['tipo_identificacion']
        etree.SubElement(info_factura, "razonSocialComprador").text = f"{cliente_datos['nombres']} {cliente_datos['apellidos']}"
        etree.SubElement(info_factura, "identificacionComprador").text = cliente_datos['identificacion']
        etree.SubElement(info_factura, "direccionComprador").text = cliente_datos['direccion']
        etree.SubElement(info_factura, "totalSinImpuestos").text = f"{factura_data['subtotal']:.2f}"
        etree.SubElement(info_factura, "totalDescuento").text = "0.00"
        
        # Total con impuestos
        totales_impuestos = etree.SubElement(info_factura, "totalConImpuestos")
        total_impuesto = etree.SubElement(totales_impuestos, "totalImpuesto")
        etree.SubElement(total_impuesto, "codigo").text = "2"  # IVA
        etree.SubElement(total_impuesto, "codigoPorcentaje").text = "2"  # 15%
        etree.SubElement(total_impuesto, "baseImponible").text = f"{factura_data['subtotal']:.2f}"
        etree.SubElement(total_impuesto, "valor").text = f"{factura_data['iva']:.2f}"
        
        etree.SubElement(info_factura, "propina").text = "0.00"
        etree.SubElement(info_factura, "importeTotal").text = f"{factura_data['total']:.2f}"
        etree.SubElement(info_factura, "moneda").text = "DOLAR"
        
        # Detalles (items)
        detalles = etree.SubElement(root, "detalles")
        for idx, item in enumerate(items, 1):
            detalle = etree.SubElement(detalles, "detalle")
            etree.SubElement(detalle, "codigoPrincipal").text = item.get('codigo', f"PROD{idx:03d}")
            etree.SubElement(detalle, "descripcion").text = item['nombre']
            etree.SubElement(detalle, "cantidad").text = str(item['cantidad'])
            etree.SubElement(detalle, "precioUnitario").text = f"{item['precio_unitario']:.2f}"
            etree.SubElement(detalle, "descuento").text = "0.00"
            subtotal_item = Decimal(str(item['cantidad'])) * Decimal(str(item['precio_unitario']))
            etree.SubElement(detalle, "precioTotalSinImpuesto").text = f"{subtotal_item:.2f}"
        
        # Convertir a string
        xml_str = etree.tostring(root, pretty_print=True, xml_declaration=True, encoding='UTF-8')
        return xml_str.decode('utf-8')
    
    def _generar_clave_acceso(self, factura_data: dict) -> str:
        """
        Genera clave de acceso de 49 dígitos según algoritmo SRI
        (Simulado para propósitos educativos)
        """
        fecha = factura_data['fecha_emision'].strftime('%d%m%Y')
        tipo_comprobante = '01'  # Factura
        ruc = factura_data.get('empresa_ruc', '1234567890001')
        ambiente = '1'  # Pruebas
        secuencial = factura_data['numero_factura'].split('-')[2]
        codigo_numerico = '12345678'  # Aleatorio
        tipo_emision = '1'
        
        # Construir clave sin dígito verificador
        clave_sin_verificador = f"{fecha}{tipo_comprobante}{ruc}{ambiente}{secuencial}{codigo_numerico}{tipo_emision}"
        
        # Calcular dígito verificador (módulo 11)
        digito = self._calcular_digito_verificador(clave_sin_verificador)
        
        return clave_sin_verificador + str(digito)
    
    def _calcular_digito_verificador(self, numero: str) -> int:
        """Calcula dígito verificador módulo 11"""
        factor = 2
        suma = 0
        
        for digito in reversed(numero):
            suma += int(digito) * factor
            factor = factor + 1 if factor < 7 else 2
        
        residuo = suma % 11
        resultado = 11 - residuo
        
        if resultado == 11:
            return 0
        elif resultado == 10:
            return 1
        else:
            return resultado
    
    def firmar_xml(self, xml_content: str) -> dict:
        """
        Firma digitalmente el XML con RSA-2048 y SHA-256
        Returns:
            dict con hash_sha256, firma_digital, xml_firmado
        """
        # 1. Calcular hash SHA-256 del XML
        xml_bytes = xml_content.encode('utf-8')
        hash_sha256 = hashlib.sha256(xml_bytes).hexdigest()
        
        # 2. Cargar clave privada desde PEM
        private_key_pem = self.rsa_keys['private_key']
        private_key = serialization.load_pem_private_key(
            private_key_pem.encode('utf-8'),
            password=None,
            backend=default_backend()
        )
        
        # 3. Firmar el hash con clave privada RSA
        hash_bytes = hash_sha256.encode('utf-8')
        
        firma = private_key.sign(
            hash_bytes,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        
        firma_base64 = base64.b64encode(firma).decode('utf-8')
        
        # 3. Crear XML firmado (agregar firma al XML original)
        root = etree.fromstring(xml_content.encode('utf-8'))
        
        # Definir namespace para la firma
        NSMAP = {'ds': 'http://www.w3.org/2000/09/xmldsig#'}
        signature = etree.SubElement(root, f"{{{NSMAP['ds']}}}Signature", nsmap=NSMAP)
        etree.SubElement(signature, f"{{{NSMAP['ds']}}}SignatureValue").text = firma_base64
        etree.SubElement(signature, f"{{{NSMAP['ds']}}}DigestValue").text = hash_sha256
        
        xml_firmado = etree.tostring(root, pretty_print=True, xml_declaration=True, encoding='UTF-8')
        
        return {
            'hash_sha256': hash_sha256,
            'firma_digital': firma_base64,
            'xml_firmado': xml_firmado.decode('utf-8')
        }
    
    def verificar_firma(self, hash_original: str, firma_base64: str) -> bool:
        """
        Verifica la firma digital RSA
        Returns:
            True si la firma es válida
        """
        try:
            # Cargar clave pública desde PEM
            public_key_pem = self.rsa_keys['public_key']
            public_key = serialization.load_pem_public_key(
                public_key_pem.encode('utf-8'),
                backend=default_backend()
            )
            
            firma = base64.b64decode(firma_base64)
            hash_bytes = hash_original.encode('utf-8')
            
            public_key.verify(
                firma,
                hash_bytes,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except Exception as e:
            print(f"❌ Error verificando firma: {e}")
            return False
    
    def generar_qr(self, factura: Factura, url_base: str = "http://localhost:5173") -> dict:
        """
        Genera código QR con datos de verificación
        Returns:
            dict con qr_image (base64), qr_data (string)
        """
        # Datos para el QR
        qr_data = f"{url_base}/verificar/{factura.hash_sha256}"
        qr_info = f"Factura: {factura.numero_factura}\n"
        qr_info += f"Fecha: {factura.fecha_emision.strftime('%d/%m/%Y')}\n"
        qr_info += f"Total: ${factura.total:.2f}\n"
        qr_info += f"Verificar: {qr_data}"
        
        # Generar imagen QR
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convertir a base64
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        return {
            'qr_image': f"data:image/png;base64,{img_base64}",
            'qr_data': qr_info
        }
    
    def simular_autorizacion_sri(self, factura: Factura) -> dict:
        """
        Simula el proceso de autorización del SRI
        (En producción real, esto sería una llamada al Web Service del SRI)
        """
        # Generar número de autorización aleatorio de 49 dígitos
        fecha_autorizacion = datetime.now()
        num_autorizacion = self._generar_clave_acceso({
            'fecha_emision': fecha_autorizacion,
            'empresa_ruc': '1234567890001',
            'numero_factura': factura.numero_factura
        })
        
        return {
            'num_autorizacion': num_autorizacion,
            'fecha_autorizacion': fecha_autorizacion,
            'estado_sri': 'AUTORIZADO'
        }
    
    def crear_factura(self, usuario_id: int, cliente_id: int, items: list, 
                     observaciones: str = None) -> Factura:
        """
        Crea una factura electrónica completa con firma digital y QR
        
        Args:
            usuario_id: ID del usuario que emite la factura
            cliente_id: ID del cliente
            items: Lista de items [{producto_id, codigo, nombre, cantidad, precio_unitario, iva_porcentaje}]
            observaciones: Notas adicionales
            
        Returns:
            Factura creada y almacenada en BD
        """
        # 1. Validar cliente
        cliente = Cliente.query.get(cliente_id)
        if not cliente:
            raise ValueError(f"Cliente {cliente_id} no encontrado")
        
        # 2. Calcular totales
        totales = self.calcular_totales(items)
        
        # 3. Generar número de factura
        numero_factura = self.generar_numero_factura()
        
        # 4. Preparar datos de factura
        factura_data = {
            'numero_factura': numero_factura,
            'fecha_emision': datetime.now(),
            'subtotal': totales['subtotal'],
            'iva': totales['iva'],
            'total': totales['total'],
            'empresa_ruc': '1234567890001',
            'empresa_razon_social': 'Sistema de Facturación Electrónica S.A.'
        }
        
        # 5. Generar XML
        xml_content = self.generar_xml_factura(factura_data, cliente, items)
        
        # 6. Firmar XML con RSA
        firma_data = self.firmar_xml(xml_content)
        
        # 7. Crear registro en BD
        factura = Factura(
            numero_factura=numero_factura,
            cliente_id=cliente_id,
            usuario_id=usuario_id,
            fecha_emision=factura_data['fecha_emision'],
            subtotal=totales['subtotal'],
            iva=totales['iva'],
            total=totales['total'],
            hash_sha256=firma_data['hash_sha256'],
            firma_digital=firma_data['firma_digital'],
            xml_firmado=firma_data['xml_firmado'],
            observaciones=observaciones,
            items=items  # Almacenar como JSONB
        )
        
        db.session.add(factura)
        db.session.flush()  # Para obtener el ID antes de commit
        
        # 8. Generar código QR
        qr_data = self.generar_qr(factura)
        factura.qr_image = qr_data['qr_image']
        factura.qr_data = qr_data['qr_data']
        
        # 9. Simular autorización SRI
        autorizacion = self.simular_autorizacion_sri(factura)
        factura.num_autorizacion = autorizacion['num_autorizacion']
        factura.fecha_autorizacion = autorizacion['fecha_autorizacion']
        factura.estado_sri = autorizacion['estado_sri']
        
        db.session.commit()
        
        return factura
    
    def verificar_integridad(self, hash_sha256: str) -> dict:
        """
        Verifica la integridad de una factura por su hash
        Endpoint público para verificación vía QR
        
        Returns:
            dict con status, factura_data, mensaje
        """
        factura = Factura.query.filter_by(hash_sha256=hash_sha256).first()
        
        if not factura:
            return {
                'status': 'NO_ENCONTRADA',
                'valida': False,
                'mensaje': 'Factura no encontrada en el sistema'
            }
        
        # Verificar firma digital RSA - esto es suficiente para garantizar integridad
        print(f"🔍 Verificando firma para hash: {factura.hash_sha256[:16]}...")
        firma_valida = self.verificar_firma(factura.hash_sha256, factura.firma_digital)
        
        if not firma_valida:
            print("❌ Firma digital inválida")
            return {
                'status': 'ALTERADA',
                'valida': False,
                'mensaje': 'La firma digital no es válida. El documento ha sido alterado.'
            }
        
        print("✅ Firma digital válida")
        
        # Factura válida
        cliente = Cliente.query.get(factura.cliente_id)
        # Descifrar datos del cliente
        if cliente and cliente.nombres_enc:
            from cryptography.hazmat.primitives.ciphers.aead import AESGCM
            encrypted_data = cliente.nombres_enc + cliente.tag
            aesgcm = AESGCM(self.crypto_service.aes_master_key)
            decrypted_all = aesgcm.decrypt(cliente.iv, encrypted_data, None).decode('utf-8')
            partes = decrypted_all.split('|')
            decrypted_data = {
                'nombres': partes[0] if len(partes) > 0 else '',
                'apellidos': partes[1] if len(partes) > 1 else '',
                'direccion': partes[2] if len(partes) > 2 else '',
                'telefono': partes[3] if len(partes) > 3 else '',
                'email': partes[4] if len(partes) > 4 else ''
            }
            cliente_datos = cliente.to_dict(decrypted_data=decrypted_data)
        else:
            cliente_datos = {}
        
        return {
            'status': 'VALIDA',
            'valida': True,
            'mensaje': 'Factura válida y auténtica',
            'factura': {
                'numero_factura': factura.numero_factura,
                'fecha_emision': factura.fecha_emision.strftime('%d/%m/%Y %H:%M:%S'),
                'cliente': f"{cliente_datos.get('nombres', '')} {cliente_datos.get('apellidos', '')}",
                'identificacion': cliente_datos.get('identificacion', ''),
                'total': float(factura.total),
                'estado_sri': factura.estado_sri,
                'num_autorizacion': factura.num_autorizacion,
                'fecha_autorizacion': factura.fecha_autorizacion.strftime('%d/%m/%Y %H:%M:%S') if factura.fecha_autorizacion else None
            }
        }
