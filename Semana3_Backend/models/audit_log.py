"""
Modelo de Auditoría (Inmutable)
"""
from models.base import db
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSONB, INET


class AuditLog(db.Model):
    __tablename__ = 'audit_log'
    
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id', ondelete='SET NULL'))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    accion = db.Column(db.String(50), nullable=False)  # CREATE, UPDATE, DELETE, LOGIN, LOGOUT
    entidad = db.Column(db.String(50), nullable=False)  # usuarios, clientes, facturas, etc.
    entidad_id = db.Column(db.Integer)
    
    datos_anteriores = db.Column(JSONB)
    datos_nuevos = db.Column(JSONB)
    
    ip_address = db.Column(INET, nullable=False)
    user_agent = db.Column(db.Text)
    
    resultado = db.Column(db.String(20), default='EXITO')  # EXITO, ERROR
    mensaje_error = db.Column(db.Text)
    
    # Relación inversa
    usuario = db.relationship('Usuario', back_populates='audit_logs')
    
    def to_dict(self):
        """Convertir a diccionario"""
        return {
            'id': self.id,
            'usuario_id': self.usuario_id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'accion': self.accion,
            'entidad': self.entidad,
            'entidad_id': self.entidad_id,
            'datos_anteriores': self.datos_anteriores,
            'datos_nuevos': self.datos_nuevos,
            'ip_address': str(self.ip_address) if self.ip_address else None,
            'user_agent': self.user_agent,
            'resultado': self.resultado,
            'mensaje_error': self.mensaje_error
        }
    
    def __repr__(self):
        return f'<AuditLog {self.accion} - {self.entidad}>'
