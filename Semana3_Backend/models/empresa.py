"""
Modelo de Empresa
"""
from models.base import db
from datetime import datetime


class Empresa(db.Model):
    __tablename__ = 'empresa'
    
    id = db.Column(db.Integer, primary_key=True)
    ruc = db.Column(db.String(13), unique=True, nullable=False, index=True)
    razon_social = db.Column(db.String(300), nullable=False)
    nombre_comercial = db.Column(db.String(300))
    direccion = db.Column(db.Text, nullable=False)
    telefono = db.Column(db.String(20))
    email = db.Column(db.String(100), nullable=False)
    logo_path = db.Column(db.String(255))
    
    # Claves RSA
    clave_publica = db.Column(db.Text, nullable=False)  # PEM format
    clave_privada_enc = db.Column(db.Text, nullable=False)  # Cifrada con AES
    
    # Configuración SRI
    establecimiento = db.Column(db.String(3), default='001')
    punto_emision = db.Column(db.String(3), default='001')
    ambiente = db.Column(db.String(20), default='PRUEBAS')  # PRUEBAS o PRODUCCION
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    # NOTA: Deshabilitado porque la tabla factura fue simplificada sin empresa_id
    # facturas = db.relationship('Factura', back_populates='empresa', lazy='dynamic')
    
    def to_dict(self, include_private_key=False):
        """Convertir a diccionario"""
        data = {
            'id': self.id,
            'ruc': self.ruc,
            'razon_social': self.razon_social,
            'nombre_comercial': self.nombre_comercial,
            'direccion': self.direccion,
            'telefono': self.telefono,
            'email': self.email,
            'logo_path': self.logo_path,
            'establecimiento': self.establecimiento,
            'punto_emision': self.punto_emision,
            'ambiente': self.ambiente,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        # Solo incluir clave pública por defecto
        data['clave_publica'] = self.clave_publica
        
        if include_private_key:
            data['clave_privada_enc'] = self.clave_privada_enc
            
        return data
    
    def __repr__(self):
        return f'<Empresa {self.razon_social}>'
