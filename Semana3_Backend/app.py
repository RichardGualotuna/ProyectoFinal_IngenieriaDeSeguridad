"""
Aplicación Principal - Sistema de Facturación Electrónica
✅ CORREGIDO: Con manejo de errores mejorado y CORS configurado correctamente
"""
import os
import base64
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config import get_config
from models.base import db
from services.crypto_service import init_crypto_service

# Importar blueprints
from routes.auth_routes import auth_bp
from routes.user_routes import user_bp
from routes.cliente_routes import cliente_bp
from routes.factura_routes import factura_bp


def create_app(config_name=None):
    """
    Factory para crear la aplicación Flask
    
    Args:
        config_name: Nombre de la configuración a usar
        
    Returns:
        Flask: Aplicación configurada
    """
    app = Flask(__name__)
    
    # ✅ Configurar Flask
    app.url_map.strict_slashes = False
    
    # Cargar configuración
    if config_name:
        app.config.from_object(config_name)
    else:
        config_class = get_config()
        app.config.from_object(config_class)
    
    # ✅ Inicializar base de datos
    db.init_app(app)
    
    # ✅ Configurar CORS correctamente
    CORS(app,
         origins=app.config['CORS_ORIGINS'],
         supports_credentials=True,
         allow_headers=['Content-Type', 'Authorization'],
         methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
         expose_headers=['Content-Type', 'Authorization'])
    
    # ✅ Inicializar JWT
    jwt = JWTManager(app)
    
    # ✅ Inicializar servicio criptográfico
    with app.app_context():
        aes_key = app.config.get('AES_MASTER_KEY')
        if not aes_key:
            print("⚠️  WARNING: Generando clave AES temporal. Configura AES_MASTER_KEY en producción.")
            aes_key = base64.b64encode(os.urandom(32)).decode()
        
        try:
            init_crypto_service(aes_key)
        except Exception as e:
            print(f"❌ Error inicializando CryptoService: {str(e)}")
    
    # ✅ Registrar blueprints con prefijos correctos
    app.register_blueprint(auth_bp, url_prefix='/api/v1/auth')
    app.register_blueprint(user_bp, url_prefix='/api/v1/users')
    app.register_blueprint(cliente_bp, url_prefix='/api/v1/clientes')
    app.register_blueprint(factura_bp, url_prefix='/api/v1/facturas')
    
    print("✅ Rutas registradas:")
    print("   - /api/v1/auth (login, logout, me, register)")
    print("   - /api/v1/users (CRUD usuarios - solo ADMIN)")
    print("   - /api/v1/clientes (CRUD clientes)")
    print("   - /api/v1/facturas (Facturas con RSA, QR y SRI)")
    print("   - /api/v1/facturas/verificar/:hash (Verificación pública de QR)")
    
    # ========================================================================
    # MANEJADORES DE ERRORES JWT
    # ========================================================================
    
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        """Token expirado"""
        print("⚠️  JWT: Token expirado")
        return jsonify({
            'success': False,
            'error': 'Token expirado',
            'message': 'El token ha expirado. Por favor, inicie sesión nuevamente.'
        }), 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        """Token inválido"""
        print(f"⚠️  JWT: Token inválido - {error}")
        return jsonify({
            'success': False,
            'error': 'Token inválido',
            'message': 'El token proporcionado no es válido.'
        }), 401
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        """Token no proporcionado"""
        print(f"⚠️  JWT: Token no proporcionado - {error}")
        return jsonify({
            'success': False,
            'error': 'Token no proporcionado',
            'message': 'Se requiere autenticación para acceder a este recurso.'
        }), 401
    
    # ========================================================================
    # RUTAS BÁSICAS
    # ========================================================================
    
    @app.route('/')
    def index():
        """Ruta principal"""
        return jsonify({
            'success': True,
            'message': 'Sistema de Facturación Electrónica - API v1.0',
            'status': 'running',
            'endpoints': {
                'auth': '/api/v1/auth',
                'users': '/api/v1/users',
                'clientes': '/api/v1/clientes',
                'facturas': '/api/v1/facturas',
                'verificar_qr': '/api/v1/facturas/verificar/:hash (público)'
            }
        })
    
    @app.route('/health')
    def health():
        """Endpoint de salud para monitoreo"""
        try:
            # Verificar conexión a BD
            db.session.execute('SELECT 1')
            db_status = 'connected'
        except Exception as e:
            print(f"❌ Error en health check: {str(e)}")
            db_status = 'disconnected'
        
        return jsonify({
            'success': True,
            'status': 'healthy',
            'database': db_status
        })
    
    # ========================================================================
    # MANEJADORES DE ERRORES GLOBALES
    # ========================================================================
    
    @app.errorhandler(404)
    def not_found(error):
        """404 - Not Found"""
        return jsonify({
            'success': False,
            'error': 'Endpoint no encontrado',
            'message': f'La ruta solicitada no existe.'
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """500 - Internal Server Error"""
        print(f"❌ Error 500: {str(error)}")
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor',
            'message': 'Ha ocurrido un error inesperado. Por favor, intente nuevamente.'
        }), 500
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        """405 - Method Not Allowed"""
        return jsonify({
            'success': False,
            'error': 'Método no permitido',
            'message': 'El método HTTP utilizado no está permitido para esta ruta.'
        }), 405
    
    return app


# ============================================================================
# PUNTO DE ENTRADA
# ============================================================================

if __name__ == '__main__':
    app = create_app()
    
    print("=" * 70)
    print("🚀 Iniciando Sistema de Facturación Electrónica")
    print("=" * 70)
    print(f"Entorno: {app.config.get('FLASK_ENV', 'development')}")
    print(f"Debug: {app.config.get('DEBUG', False)}")
    print(f"Base de datos: {app.config.get('POSTGRES_DB')}")
    print("=" * 70)
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )
