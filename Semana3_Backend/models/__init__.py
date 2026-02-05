"""
Inicialización de modelos
"""
from models.base import db
from models.user import Usuario
from models.empresa import Empresa
from models.cliente import Cliente
from models.factura import Factura
from models.audit_log import AuditLog
from models.configuracion import Configuracion

__all__ = [
    'db',
    'Usuario',
    'Empresa',
    'Cliente',
    'Factura',
    'AuditLog',
    'Configuracion'
]
