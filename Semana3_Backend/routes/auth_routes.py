"""
Rutas de Autenticación
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from services.auth_service import AuthService
from datetime import timedelta

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Iniciar sesión
    
    Body:
        username: str
        password: str
    """
    try:
        data = request.get_json()
        
        # Validar datos
        if not data or not data.get('username') or not data.get('password'):
            return jsonify({
                'success': False,
                'error': 'Username y password son requeridos'
            }), 400
        
        # Autenticar
        usuario = AuthService.login(data['username'], data['password'])
        
        # Crear token JWT con claims adicionales
        additional_claims = {
            'rol': usuario.rol,
            'nombres': usuario.nombres,
            'apellidos': usuario.apellidos
        }
        
        access_token = create_access_token(
            identity=usuario.id,
            additional_claims=additional_claims,
            expires_delta=timedelta(hours=8)
        )
        
        return jsonify({
            'success': True,
            'message': 'Login exitoso',
            'data': {
                'token': access_token,
                'user': usuario.to_dict()
            }
        }), 200
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 401
    except Exception as e:
        print(f"❌ Error en login: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': 'Error en el servidor',
            'details': str(e)
        }), 500


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Obtener usuario actual autenticado"""
    try:
        user_id = get_jwt_identity()
        usuario = AuthService.get_user_by_id(user_id)
        
        if not usuario:
            return jsonify({
                'success': False,
                'error': 'Usuario no encontrado'
            }), 404
        
        if not usuario.activo:
            return jsonify({
                'success': False,
                'error': 'Usuario inactivo'
            }), 403
        
        return jsonify({
            'success': True,
            'data': usuario.to_dict()
        }), 200
        
    except Exception as e:
        print(f"❌ Error obteniendo usuario actual: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Error en el servidor',
            'details': str(e)
        }), 500


@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """Cerrar sesión (solo registra en auditoría)"""
    try:
        user_id = get_jwt_identity()
        
        # Registrar en auditoría
        AuthService.log_audit(
            usuario_id=user_id,
            accion='LOGOUT',
            entidad='usuarios',
            entidad_id=user_id
        )
        
        return jsonify({
            'success': True,
            'message': 'Sesión cerrada exitosamente'
        }), 200
        
    except Exception as e:
        print(f"❌ Error en logout: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Error en el servidor'
        }), 500


@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Registrar nuevo usuario (solo para desarrollo/testing)
    En producción, usar /api/v1/users (requiere admin)
    """
    try:
        data = request.get_json()
        
        # Validar campos requeridos
        required_fields = ['username', 'password', 'nombres', 'apellidos', 'email']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'error': f'El campo {field} es requerido'
                }), 400
        
        # Registrar usuario
        usuario = AuthService.register_user(
            username=data['username'],
            password=data['password'],
            nombres=data['nombres'],
            apellidos=data['apellidos'],
            email=data['email'],
            rol=data.get('rol', 'FACTURADOR')
        )
        
        return jsonify({
            'success': True,
            'message': 'Usuario registrado exitosamente',
            'data': usuario.to_dict()
        }), 201
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        print(f"❌ Error en registro: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': 'Error en el servidor',
            'details': str(e)
        }), 500
