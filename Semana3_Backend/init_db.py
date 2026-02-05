"""
Script para inicializar la base de datos
Crea todas las tablas y datos iniciales
"""
from app import create_app
from models.base import db
from models import Usuario, Empresa, Cliente, Configuracion
from services.auth_service import AuthService
import base64

def init_database():
    """Inicializar base de datos con datos iniciales"""
    app = create_app()
    
    with app.app_context():
        print("=" * 70)
        print("🔧 Inicializando Base de Datos")
        print("=" * 70)
        
        # Crear todas las tablas
        print("📦 Creando tablas...")
        db.create_all()
        print("✅ Tablas creadas")
        
        # Verificar si ya existen datos
        if Usuario.query.first():
            print("⚠️  La base de datos ya tiene datos. Saltando inicialización.")
            return
        
        # Crear usuario administrador
        print("\n👤 Creando usuario administrador...")
        try:
            admin = AuthService.register_user(
                username='admin',
                password='Admin123!',
                nombres='Administrador',
                apellidos='Sistema',
                email='admin@facturasegura.com',
                rol='ADMIN'
            )
            print(f"✅ Usuario admin creado (ID: {admin.id})")
            print(f"   Username: admin")
            print(f"   Password: Admin123!")
        except Exception as e:
            print(f"❌ Error creando admin: {str(e)}")
        
        # Crear configuraciones iniciales
        print("\n⚙️  Creando configuraciones...")
        configs = [
            Configuracion(
                clave='IVA_TARIFA_ACTUAL',
                valor='15',
                descripcion='Tarifa de IVA actual (%)',
                tipo_dato='INTEGER'
            ),
            Configuracion(
                clave='AMBIENTE_SRI',
                valor='PRUEBAS',
                descripcion='Ambiente del SRI (PRUEBAS o PRODUCCION)',
                tipo_dato='STRING'
            )
        ]
        
        for config in configs:
            db.session.add(config)
        
        db.session.commit()
        print("✅ Configuraciones creadas")
        
        print("\n" + "=" * 70)
        print("✅ Base de datos inicializada correctamente")
        print("=" * 70)
        print("\n📋 RESUMEN:")
        print(f"   Usuarios: {Usuario.query.count()}")
        print(f"   Configuraciones: {Configuracion.query.count()}")
        print("\n🔐 CREDENCIALES DE ACCESO:")
        print("   Usuario: admin")
        print("   Password: Admin123!")
        print("   Email: admin@facturasegura.com")
        print("=" * 70)


if __name__ == '__main__':
    init_database()
