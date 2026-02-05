"""
Modelo de Factura - Simplificado para funcionamiento inmediato
"""
from models.base import db
from datetime import datetime
from decimal import Decimal


class Factura(db.Model):
    __tablename__ = 'factura'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Relaciones
    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id'), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    
    # Numeración simplificada
    numero_factura = db.Column(db.String(17), unique=True, nullable=False, index=True)  # 001-001-000000001
    fecha_emision = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Valores
    subtotal = db.Column(db.Numeric(12, 2), nullable=False, default=Decimal('0.00'))
    iva = db.Column(db.Numeric(12, 2), nullable=False, default=Decimal('0.00'))
    total = db.Column(db.Numeric(12, 2), nullable=False)
    
    # Items como JSONB
    items = db.Column(db.JSON, nullable=False)  # [{producto_id, codigo, nombre, cantidad, precio_unitario, iva_porcentaje}]
    
    # XML firmado
    xml_firmado = db.Column(db.Text)
    
    # Seguridad Criptográfica
    hash_sha256 = db.Column(db.String(64), nullable=False, index=True, unique=True)
    firma_digital = db.Column(db.Text, nullable=False)  # Firma RSA en base64
    
    # SRI (simulado)
    num_autorizacion = db.Column(db.String(49))  # Clave de acceso simulada
    fecha_autorizacion = db.Column(db.DateTime)
    estado_sri = db.Column(db.String(20), default='AUTORIZADO')  # AUTORIZADO, RECHAZADO
    
    # QR Codes
    qr_image = db.Column(db.Text)  # Base64 data URI
    qr_data = db.Column(db.Text)   # Texto del QR
    
    # Estado y notas
    observaciones = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones bidireccionales con back_populates
    cliente = db.relationship('Cliente', back_populates='facturas')
    usuario = db.relationship('Usuario', back_populates='facturas')
    
    def to_dict(self, include_items=True):
        """Convertir a diccionario"""
        data = {
            'id': self.id,
            'cliente_id': self.cliente_id,
            'usuario_id': self.usuario_id,
            'numero_factura': self.numero_factura,
            'fecha_emision': self.fecha_emision.isoformat() if self.fecha_emision else None,
            'subtotal': float(self.subtotal),
            'iva': float(self.iva),
            'total': float(self.total),
            'hash_sha256': self.hash_sha256,
            'num_autorizacion': self.num_autorizacion,
            'fecha_autorizacion': self.fecha_autorizacion.isoformat() if self.fecha_autorizacion else None,
            'estado_sri': self.estado_sri,
            'qr_image': self.qr_image,
            'qr_data': self.qr_data,
            'observaciones': self.observaciones,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_items and self.items:
            # Manejar items como string JSON o como dict
            import json
            if isinstance(self.items, str):
                try:
                    data['items'] = json.loads(self.items)
                except:
                    data['items'] = []
            else:
                data['items'] = self.items
            
        return data
    
    def __repr__(self):
        return f'<Factura {self.numero_factura}>'
