"""
Modelo de Configuración
"""
from models.base import db
from datetime import datetime


class Configuracion(db.Model):
    __tablename__ = 'configuracion'
    
    id = db.Column(db.Integer, primary_key=True)
    clave = db.Column(db.String(100), unique=True, nullable=False, index=True)
    valor = db.Column(db.Text, nullable=False)
    descripcion = db.Column(db.Text)
    tipo_dato = db.Column(db.String(20), default='STRING')  # STRING, INTEGER, BOOLEAN, JSON
    cifrado = db.Column(db.Boolean, default=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Convertir a diccionario"""
        return {
            'id': self.id,
            'clave': self.clave,
            'valor': self.valor,
            'descripcion': self.descripcion,
            'tipo_dato': self.tipo_dato,
            'cifrado': self.cifrado,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<Configuracion {self.clave}>'
