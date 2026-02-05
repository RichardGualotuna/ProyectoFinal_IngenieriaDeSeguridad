"""
Rutas de Usuarios (Solo Administrador)
✅ CORREGIDO: Con todas las operaciones CRUD funcionales
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from models.base import db
from models.user import Usuario
from services.auth_service import AuthService

user_bp = Blueprint('users', __name__)


def require_admin():
    """Decorador para verificar rol de administrador"""
    claims = get_jwt()
    if claims.get('rol') != 'ADMIN':
        return jsonify({
            'success': False,
            'error': 'Acceso denegado. Se requiere rol de ADMIN.'
        }), 403
    return None


@user_bp.route('', methods=['GET'])
@jwt_required()
def list_users():
    """
    Listar usuarios (con paginación y filtros)
    
    Query params:
        rol: Filtrar por rol
        activo: Filtrar por estado (true/false)
        page: Número de página (default: 1)
        limit: Registros por página (default: 10)
    """
    error_response = require_admin()
    if error_response:
        return error_response
    
    try:
        # Obtener parámetros
        rol = request.args.get('rol')
        activo = request.args.get('activo')
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        
        # Construir query
        query = Usuario.query
        
        if rol:
            query = query.filter_by(rol=rol)
        
        if activo is not None:
            activo_bool = activo.lower() == 'true'
            query = query.filter_by(activo=activo_bool)
        
        # Ordenar por ID
        query = query.order_by(Usuario.id.asc())
        
        # Paginación
        pagination = query.paginate(page=page, per_page=limit, error_out=False)
        
        # ✅ CRÍTICO: Asegurar que devuelve lista vacía si no hay usuarios
        users_list = [user.to_dict() for user in pagination.items] if pagination.items else []
        
        return jsonify({
            'success': True,
            'data': {
                'users': users_list,
                'pagination': {
                    'page': page,
                    'limit': limit,
                    'total': pagination.total,
                    'pages': pagination.pages
                }
            }
        }), 200
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        print(f"❌ Error listando usuarios: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': 'Error en el servidor',
            'details': str(e)
        }), 500


@user_bp.route('/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    """Obtener usuario por ID"""
    error_response = require_admin()
    if error_response:
        return error_response
    
    try:
        usuario = Usuario.query.get(user_id)
        
        if not usuario:
            return jsonify({
                'success': False,
                'error': 'Usuario no encontrado'
            }), 404
        
        return jsonify({
            'success': True,
            'data': usuario.to_dict()
        }), 200
        
    except Exception as e:
        print(f"❌ Error obteniendo usuario {user_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Error en el servidor',
            'details': str(e)
        }), 500


@user_bp.route('', methods=['POST'])
@jwt_required()
def create_user():
    """
    Crear nuevo usuario
    
    Body:
        username: str (requerido)
        password: str (requerido)
        nombres: str (requerido)
        apellidos: str (requerido)
        email: str (requerido)
        rol: str (requerido) - ADMIN, FACTURADOR, CONTADOR, AUDITOR
    """
    error_response = require_admin()
    if error_response:
        return error_response
    
    try:
        data = request.get_json()
        
        # ✅ CRÍTICO: Validar todos los campos requeridos
        required_fields = ['username', 'password', 'nombres', 'apellidos', 'email', 'rol']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'error': f'El campo {field} es requerido'
                }), 400
        
        # Crear usuario
        usuario = AuthService.register_user(
            username=data['username'],
            password=data['password'],
            nombres=data['nombres'],
            apellidos=data['apellidos'],
            email=data['email'],
            rol=data['rol']
        )
        
        # ✅ CRÍTICO: Devolver respuesta consistente
        return jsonify({
            'success': True,
            'message': 'Usuario creado exitosamente',
            'data': usuario.to_dict()
        }), 201
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        print(f"❌ Error creando usuario: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': 'Error en el servidor',
            'details': str(e)
        }), 500


@user_bp.route('/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    """
    Actualizar usuario
    
    Body (todos opcionales):
        email: str
        nombres: str
        apellidos: str
        rol: str
        activo: bool
        password: str (solo si se quiere cambiar)
    """
    error_response = require_admin()
    if error_response:
        return error_response
    
    try:
        data = request.get_json()
        
        # ✅ CRÍTICO: Validar que al menos hay un campo para actualizar
        if not data:
            return jsonify({
                'success': False,
                'error': 'No hay datos para actualizar'
            }), 400
        
        # Actualizar usuario
        usuario = AuthService.update_user(user_id, **data)
        
        # ✅ CRÍTICO: Devolver respuesta consistente
        return jsonify({
            'success': True,
            'message': 'Usuario actualizado exitosamente',
            'data': usuario.to_dict()
        }), 200
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 404
    except Exception as e:
        print(f"❌ Error actualizando usuario {user_id}: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': 'Error en el servidor',
            'details': str(e)
        }), 500


@user_bp.route('/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    """
    Eliminar (desactivar) usuario
    Soft delete - solo marca como inactivo
    """
    error_response = require_admin()
    if error_response:
        return error_response
    
    try:
        # ✅ CRÍTICO: Usar el servicio que hace soft delete
        AuthService.delete_user(user_id)
        
        # ✅ CRÍTICO: Devolver respuesta consistente
        return jsonify({
            'success': True,
            'message': 'Usuario eliminado exitosamente'
        }), 200
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 404
    except Exception as e:
        print(f"❌ Error eliminando usuario {user_id}: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': 'Error en el servidor',
            'details': str(e)
        }), 500
