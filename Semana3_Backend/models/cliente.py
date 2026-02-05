"""
Modelo de Cliente (con cifrado AES-GCM)
"""
from models.base import db
from datetime import datetime


class Cliente(db.Model):
    __tablename__ = 'cliente'
    
    id = db.Column(db.Integer, primary_key=True)
    tipo_identificacion = db.Column(db.String(20), nullable=False)  # CEDULA, RUC, PASAPORTE
    identificacion = db.Column(db.String(20), unique=True, nullable=False, index=True)
    razon_social = db.Column(db.String(300))  # Para empresas (RUC)
    
    # Datos cifrados con AES-256-GCM
    nombres_enc = db.Column(db.LargeBinary)
    apellidos_enc = db.Column(db.LargeBinary)
    direccion_enc = db.Column(db.LargeBinary)
    telefono_enc = db.Column(db.LargeBinary)
    email_enc = db.Column(db.LargeBinary)
    
    # IV y Tag para AES-GCM
    iv = db.Column(db.LargeBinary, nullable=False)
    tag = db.Column(db.LargeBinary)
    
    activo = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    facturas = db.relationship('Factura', back_populates='cliente', lazy='dynamic')
    
    def to_dict(self, decrypted_data=None):
        """
        Convertir a diccionario
        
        Args:
            decrypted_data: Dict con datos descifrados {nombres, apellidos, direccion, telefono, email}
        """
        data = {
            'id': self.id,
            'tipo_identificacion': self.tipo_identificacion,
            'identificacion': self.identificacion,
            'razon_social': self.razon_social,
            'activo': self.activo,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        # Si se proporcionan datos descifrados, incluirlos
        if decrypted_data:
            data.update({
                'nombres': decrypted_data.get('nombres'),
                'apellidos': decrypted_data.get('apellidos'),
                'direccion': decrypted_data.get('direccion'),
                'telefono': decrypted_data.get('telefono'),
                'email': decrypted_data.get('email')
            })
        else:
            # Marcar como cifrado
            data.update({
                'nombres': '[CIFRADO]',
                'apellidos': '[CIFRADO]',
                'direccion': '[CIFRADO]',
                'telefono': '[CIFRADO]',
                'email': '[CIFRADO]'
            })
            
        return data
    
    def __repr__(self):
        return f'<Cliente {self.identificacion}>'
