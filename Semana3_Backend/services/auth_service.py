"""
Servicio de Autenticación
Login, registro, gestión de usuarios, auditoría
"""
import bcrypt
from datetime import datetime
from flask import request
from models.base import db
from models.user import Usuario
from models.audit_log import AuditLog


class AuthService:
    """Servicio centralizado de autenticación"""
    
    @staticmethod
    def hash_password(password):
        """
        Hashear contraseña con Bcrypt
        
        Args:
            password: Contraseña en texto plano
            
        Returns:
            str: Hash bcrypt
        """
        salt = bcrypt.gensalt(rounds=12)
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    @staticmethod
    def verify_password(password, password_hash):
        """
        Verificar contraseña contra hash
        
        Args:
            password: Contraseña en texto plano
            password_hash: Hash bcrypt
            
        Returns:
            bool: True si coincide
        """
        try:
            return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
        except Exception as e:
            print(f"❌ Error verificando contraseña: {str(e)}")
            return False
    
    @staticmethod
    def register_user(username, password, nombres, apellidos, email, rol='FACTURADOR'):
        """
        Registrar nuevo usuario
        
        Args:
            username: Nombre de usuario único
            password: Contraseña en texto plano
            nombres: Nombres del usuario
            apellidos: Apellidos del usuario
            email: Email único
            rol: Rol del usuario (ADMIN, FACTURADOR, CONTADOR, AUDITOR)
            
        Returns:
            Usuario: Usuario creado
            
        Raises:
            ValueError: Si el username o email ya existe
        """
        # Validar unicidad
        if Usuario.query.filter_by(username=username).first():
            raise ValueError('El nombre de usuario ya está en uso')
        
        if Usuario.query.filter_by(email=email).first():
            raise ValueError('El email ya está registrado')
        
        # Validar rol
        roles_validos = ['ADMIN', 'FACTURADOR', 'CONTADOR', 'AUDITOR']
        if rol not in roles_validos:
            raise ValueError(f'Rol inválido. Debe ser uno de: {", ".join(roles_validos)}')
        
        # Hashear contraseña
        password_hash = AuthService.hash_password(password)
        
        # Crear usuario
        usuario = Usuario(
            username=username,
            password_hash=password_hash,
            nombres=nombres,
            apellidos=apellidos,
            email=email,
            rol=rol,
            activo=True
        )
        
        db.session.add(usuario)
        db.session.commit()
        
        # Auditoría
        AuthService.log_audit(
            usuario_id=None,
            accion='CREATE',
            entidad='usuarios',
            entidad_id=usuario.id,
            datos_nuevos={
                'username': username,
                'email': email,
                'rol': rol
            }
        )
        
        print(f"✅ Usuario creado: {username} (ID: {usuario.id})")
        return usuario
    
    @staticmethod
    def login(username, password):
        """
        Iniciar sesión
        
        Args:
            username: Nombre de usuario
            password: Contraseña
            
        Returns:
            Usuario: Usuario autenticado
            
        Raises:
            ValueError: Si las credenciales son inválidas
        """
        # Buscar usuario
        usuario = Usuario.query.filter_by(username=username).first()
        
        if not usuario:
            AuthService.log_audit(
                usuario_id=None,
                accion='LOGIN',
                entidad='usuarios',
                resultado='ERROR',
                mensaje_error='Usuario no encontrado'
            )
            raise ValueError('Credenciales inválidas')
        
        # Verificar contraseña
        if not AuthService.verify_password(password, usuario.password_hash):
            AuthService.log_audit(
                usuario_id=usuario.id,
                accion='LOGIN',
                entidad='usuarios',
                resultado='ERROR',
                mensaje_error='Contraseña incorrecta'
            )
            raise ValueError('Credenciales inválidas')
        
        # Verificar si está activo
        if not usuario.activo:
            AuthService.log_audit(
                usuario_id=usuario.id,
                accion='LOGIN',
                entidad='usuarios',
                resultado='ERROR',
                mensaje_error='Usuario inactivo'
            )
            raise ValueError('Usuario inactivo')
        
        # Actualizar último login
        usuario.ultimo_login = datetime.utcnow()
        db.session.commit()
        
        # Auditoría
        AuthService.log_audit(
            usuario_id=usuario.id,
            accion='LOGIN',
            entidad='usuarios',
            entidad_id=usuario.id
        )
        
        print(f"✅ Login exitoso: {username}")
        return usuario
    
    @staticmethod
    def get_user_by_id(user_id):
        """
        Obtener usuario por ID
        
        Args:
            user_id: ID del usuario
            
        Returns:
            Usuario: Usuario encontrado o None
        """
        return Usuario.query.get(user_id)
    
    @staticmethod
    def update_user(user_id, **kwargs):
        """
        Actualizar usuario
        
        Args:
            user_id: ID del usuario
            **kwargs: Campos a actualizar
            
        Returns:
            Usuario: Usuario actualizado
            
        Raises:
            ValueError: Si el usuario no existe
        """
        usuario = Usuario.query.get(user_id)
        
        if not usuario:
            raise ValueError('Usuario no encontrado')
        
        # Guardar datos anteriores para auditoría
        datos_anteriores = usuario.to_dict()
        
        # Actualizar campos permitidos
        campos_permitidos = ['email', 'nombres', 'apellidos', 'rol', 'activo']
        
        for campo, valor in kwargs.items():
            if campo in campos_permitidos and hasattr(usuario, campo):
                # Validar unicidad de email si se actualiza
                if campo == 'email' and valor != usuario.email:
                    existing = Usuario.query.filter_by(email=valor).first()
                    if existing:
                        raise ValueError('El email ya está en uso')
                
                setattr(usuario, campo, valor)
        
        # Si se proporciona nueva contraseña
        if 'password' in kwargs and kwargs['password']:
            usuario.password_hash = AuthService.hash_password(kwargs['password'])
        
        usuario.updated_at = datetime.utcnow()
        db.session.commit()
        
        # Auditoría
        AuthService.log_audit(
            usuario_id=None,
            accion='UPDATE',
            entidad='usuarios',
            entidad_id=usuario.id,
            datos_anteriores=datos_anteriores,
            datos_nuevos=usuario.to_dict()
        )
        
        print(f"✅ Usuario actualizado: {usuario.username} (ID: {user_id})")
        return usuario
    
    @staticmethod
    def delete_user(user_id):
        """
        Eliminar (desactivar) usuario
        
        Args:
            user_id: ID del usuario
            
        Raises:
            ValueError: Si el usuario no existe
        """
        usuario = Usuario.query.get(user_id)
        
        if not usuario:
            raise ValueError('Usuario no encontrado')
        
        # Soft delete - desactivar
        datos_anteriores = usuario.to_dict()
        usuario.activo = False
        usuario.updated_at = datetime.utcnow()
        db.session.commit()
        
        # Auditoría
        AuthService.log_audit(
            usuario_id=None,
            accion='DELETE',
            entidad='usuarios',
            entidad_id=user_id,
            datos_anteriores=datos_anteriores
        )
        
        print(f"✅ Usuario desactivado: {usuario.username} (ID: {user_id})")
    
    @staticmethod
    def log_audit(usuario_id, accion, entidad, entidad_id=None, 
                  datos_anteriores=None, datos_nuevos=None, 
                  resultado='EXITO', mensaje_error=None):
        """
        Registrar evento en auditoría
        
        Args:
            usuario_id: ID del usuario que realiza la acción
            accion: Tipo de acción (CREATE, UPDATE, DELETE, LOGIN, etc.)
            entidad: Nombre de la entidad afectada
            entidad_id: ID de la entidad afectada
            datos_anteriores: Datos antes del cambio (dict)
            datos_nuevos: Datos después del cambio (dict)
            resultado: EXITO o ERROR
            mensaje_error: Mensaje de error si aplica
        """
        try:
            # Obtener IP del request
            ip_address = request.remote_addr if request else '127.0.0.1'
            user_agent = request.headers.get('User-Agent') if request else 'Unknown'
            
            audit_log = AuditLog(
                usuario_id=usuario_id,
                accion=accion,
                entidad=entidad,
                entidad_id=entidad_id,
                datos_anteriores=datos_anteriores,
                datos_nuevos=datos_nuevos,
                ip_address=ip_address,
                user_agent=user_agent,
                resultado=resultado,
                mensaje_error=mensaje_error
            )
            
            db.session.add(audit_log)
            db.session.commit()
            
        except Exception as e:
            print(f"⚠️  Error registrando auditoría: {str(e)}")
            # No fallar si no se puede registrar auditoría
