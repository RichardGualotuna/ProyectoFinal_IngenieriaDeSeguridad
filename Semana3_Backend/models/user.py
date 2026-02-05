"""
Modelo de Usuario
"""
from models.base import db
from datetime import datetime


class Usuario(db.Model):
    __tablename__ = 'usuario'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    email = db.Column(db.String(100), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(60), nullable=False)
    nombres = db.Column(db.String(100), nullable=False)
    apellidos = db.Column(db.String(100), nullable=False)
    rol = db.Column(db.String(20), nullable=False, default='FACTURADOR')  # ADMIN, FACTURADOR, CONTADOR, AUDITOR
    activo = db.Column(db.Boolean, default=True)
    ultimo_login = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    facturas = db.relationship('Factura', back_populates='usuario', lazy='dynamic')
    audit_logs = db.relationship('AuditLog', back_populates='usuario', lazy='dynamic')
    
    def to_dict(self, include_password=False):
        """Convertir a diccionario"""
        data = {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'nombres': self.nombres,
            'apellidos': self.apellidos,
            'rol': self.rol,
            'activo': self.activo,
            'ultimo_login': self.ultimo_login.isoformat() if self.ultimo_login else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_password:
            data['password_hash'] = self.password_hash
            
        return data
    
    def __repr__(self):
        return f'<Usuario {self.username}>'
