"""
Script para actualizar la contraseña del usuario admin
"""
from app import create_app
from models.base import db
from models.user import Usuario
from services.auth_service import AuthService

def fix_admin_password():
    """Actualizar contraseña del admin"""
    app = create_app()
    
    with app.app_context():
        # Buscar admin
        admin = Usuario.query.filter_by(username='admin').first()
        
        if not admin:
            print("❌ Usuario admin no encontrado")
            return
        
        # Nueva contraseña
        new_password = 'Admin123!'
        
        # Generar nuevo hash
        new_hash = AuthService.hash_password(new_password)
        
        print(f"Usuario: {admin.username}")
        print(f"Hash anterior: {admin.password_hash[:60]}...")
        print(f"Hash nuevo: {new_hash[:60]}...")
        
        # Actualizar
        admin.password_hash = new_hash
        db.session.commit()
        
        print("\n✅ Contraseña actualizada")
        
        # Verificar
        print("\n🔍 Verificando...")
        if AuthService.verify_password(new_password, admin.password_hash):
            print("✅ Verificación exitosa - Password funciona correctamente")
        else:
            print("❌ Verificación falló")

if __name__ == '__main__':
    fix_admin_password()
