"""
Rutas de Clientes
✅ CORREGIDO: Con cifrado/descifrado AES-GCM y todas las operaciones CRUD
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.base import db
from models.cliente import Cliente
from services.crypto_service import get_crypto_service
from services.auth_service import AuthService

cliente_bp = Blueprint('clientes', __name__)


@cliente_bp.route('', methods=['GET'])
@jwt_required()
def list_clientes():
    """
    Listar clientes (con descifrado)
    
    Query params:
        activo: Filtrar por estado (true/false)
        page: Número de página (default: 1)
        limit: Registros por página (default: 20)
    """
    try:
        # Obtener parámetros
        activo = request.args.get('activo')
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
        
        # Construir query
        query = Cliente.query
        
        if activo is not None:
            activo_bool = activo.lower() == 'true'
            query = query.filter_by(activo=activo_bool)
        
        # Ordenar por ID
        query = query.order_by(Cliente.id.asc())
        
        # Paginación
        pagination = query.paginate(page=page, per_page=limit, error_out=False)
        
        # ✅ CRÍTICO: Descifrar datos de cada cliente
        crypto = get_crypto_service()
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        clientes_list = []
        
        for cliente in pagination.items:
            # Descifrar datos sensibles (ahora están concatenados)
            try:
                if cliente.nombres_enc:
                    # Reconstruir datos cifrados
                    encrypted_data = cliente.nombres_enc + cliente.tag
                    aesgcm = AESGCM(crypto.aes_master_key)
                    decrypted_all = aesgcm.decrypt(cliente.iv, encrypted_data, None).decode('utf-8')
                    
                    # Separar por el delimitador
                    partes = decrypted_all.split('|')
                    decrypted_data = {
                        'nombres': partes[0] if len(partes) > 0 else '',
                        'apellidos': partes[1] if len(partes) > 1 else '',
                        'direccion': partes[2] if len(partes) > 2 else '',
                        'telefono': partes[3] if len(partes) > 3 else '',
                        'email': partes[4] if len(partes) > 4 else ''
                    }
                else:
                    decrypted_data = {
                        'nombres': '',
                        'apellidos': '',
                        'direccion': '',
                        'telefono': '',
                        'email': ''
                    }
                clientes_list.append(cliente.to_dict(decrypted_data=decrypted_data))
            except Exception as e:
                print(f"⚠️  Error descifrando cliente {cliente.id}: {str(e)}")
                import traceback
                traceback.print_exc()
                # Incluir con valores por defecto si hay error
                clientes_list.append(cliente.to_dict())
        
        return jsonify({
            'success': True,
            'data': {
                'clientes': clientes_list,
                'pagination': {
                    'page': page,
                    'limit': limit,
                    'total': pagination.total,
                    'pages': pagination.pages
                }
            }
        }), 200
        
    except Exception as e:
        print(f"❌ Error listando clientes: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': 'Error en el servidor',
            'details': str(e)
        }), 500


@cliente_bp.route('/<int:cliente_id>', methods=['GET'])
@jwt_required()
def get_cliente(cliente_id):
    """Obtener cliente por ID (con descifrado)"""
    try:
        cliente = Cliente.query.get(cliente_id)
        
        if not cliente:
            return jsonify({
                'success': False,
                'error': 'Cliente no encontrado'
            }), 404
        
        # Descifrar datos (ahora están concatenados)
        crypto = get_crypto_service()
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        
        if cliente.nombres_enc:
            try:
                # Reconstruir datos cifrados
                encrypted_data = cliente.nombres_enc + cliente.tag
                aesgcm = AESGCM(crypto.aes_master_key)
                decrypted_all = aesgcm.decrypt(cliente.iv, encrypted_data, None).decode('utf-8')
                
                # Separar por el delimitador
                partes = decrypted_all.split('|')
                decrypted_data = {
                    'nombres': partes[0] if len(partes) > 0 else '',
                    'apellidos': partes[1] if len(partes) > 1 else '',
                    'direccion': partes[2] if len(partes) > 2 else '',
                    'telefono': partes[3] if len(partes) > 3 else '',
                    'email': partes[4] if len(partes) > 4 else ''
                }
            except Exception as e:
                print(f"❌ Error descifrando cliente {cliente_id}: {str(e)}")
                import traceback
                traceback.print_exc()
                decrypted_data = {
                    'nombres': '[ERROR_DESCIFRADO]',
                    'apellidos': '[ERROR_DESCIFRADO]',
                    'direccion': '[ERROR_DESCIFRADO]',
                    'telefono': '[ERROR_DESCIFRADO]',
                    'email': '[ERROR_DESCIFRADO]'
                }
        else:
            decrypted_data = {
                'nombres': '',
                'apellidos': '',
                'direccion': '',
                'telefono': '',
                'email': ''
            }
        
        return jsonify({
            'success': True,
            'data': cliente.to_dict(decrypted_data=decrypted_data)
        }), 200
        
    except Exception as e:
        print(f"❌ Error obteniendo cliente {cliente_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Error en el servidor',
            'details': str(e)
        }), 500


@cliente_bp.route('', methods=['POST'])
@jwt_required()
def create_cliente():
    """
    Crear nuevo cliente (con cifrado)
    
    Body:
        tipo_identificacion: str (requerido) - CEDULA, RUC, PASAPORTE
        identificacion: str (requerido)
        razon_social: str (opcional, para RUC)
        nombres: str (opcional)
        apellidos: str (opcional)
        direccion: str (opcional)
        telefono: str (opcional)
        email: str (opcional)
    """
    try:
        data = request.get_json()
        
        # Validar campos requeridos
        if not data.get('tipo_identificacion') or not data.get('identificacion'):
            return jsonify({
                'success': False,
                'error': 'tipo_identificacion e identificacion son requeridos'
            }), 400
        
        # Verificar unicidad
        existing = Cliente.query.filter_by(identificacion=data['identificacion']).first()
        if existing:
            return jsonify({
                'success': False,
                'error': 'Ya existe un cliente con esa identificación'
            }), 400
        
        # ✅ CRÍTICO: Cifrar datos sensibles
        crypto = get_crypto_service()
        
        # Generar un solo IV para todos los campos (correcto en AES-GCM)
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        import os
        iv = os.urandom(12)  # 96 bits para GCM
        
        # Cifrar cada campo con el mismo IV pero diferentes datos
        nombres_val = data.get('nombres', '')
        apellidos_val = data.get('apellidos', '')
        direccion_val = data.get('direccion', '')
        telefono_val = data.get('telefono', '')
        email_val = data.get('email', '')
        
        # Cifrar con AES-GCM usando el mismo IV
        aesgcm = AESGCM(crypto.aes_master_key)
        nombres_enc = aesgcm.encrypt(iv, nombres_val.encode('utf-8'), None) if nombres_val else b''
        apellidos_enc = aesgcm.encrypt(iv, apellidos_val.encode('utf-8'), None) if apellidos_val else b''
        direccion_enc = aesgcm.encrypt(iv, direccion_val.encode('utf-8'), None) if direccion_val else b''
        telefono_enc = aesgcm.encrypt(iv, telefono_val.encode('utf-8'), None) if telefono_val else b''
        email_enc = aesgcm.encrypt(iv, email_val.encode('utf-8'), None) if email_val else b''
        
        # Separar ciphertext y tag (GCM concatena automáticamente: ciphertext + tag de 16 bytes)
        def split_gcm(encrypted_data):
            if not encrypted_data:
                return b'', b''
            return encrypted_data[:-16], encrypted_data[-16:]
        
        nombres_cipher, nombres_tag = split_gcm(nombres_enc)
        apellidos_cipher, apellidos_tag = split_gcm(apellidos_enc)
        direccion_cipher, direccion_tag = split_gcm(direccion_enc)
        telefono_cipher, telefono_tag = split_gcm(telefono_enc)
        email_cipher, email_tag = split_gcm(email_enc)
        
        # Usar el tag del primer campo (todos deberían funcionar con el mismo IV)
        # Nota: En realidad, cada campo tiene su propio tag, voy a usar una estrategia diferente
        # MEJOR: Guardar todos los tags concatenados y separarlos al descifrar
        
        # Por ahora, voy a usar el enfoque simple: concatenar todos los datos, cifrar UNA SOLA VEZ
        datos_concatenados = f"{nombres_val}|{apellidos_val}|{direccion_val}|{telefono_val}|{email_val}"
        encrypted_all = aesgcm.encrypt(iv, datos_concatenados.encode('utf-8'), None)
        ciphertext_all = encrypted_all[:-16]
        tag_all = encrypted_all[-16:]
        
        # Crear cliente con datos cifrados en un solo bloque
        cliente = Cliente(
            tipo_identificacion=data['tipo_identificacion'],
            identificacion=data['identificacion'],
            razon_social=data.get('razon_social'),
            nombres_enc=ciphertext_all,  # Ahora guardamos TODO junto
            apellidos_enc=b'',  # Vacíos porque todo está en nombres_enc
            direccion_enc=b'',
            telefono_enc=b'',
            email_enc=b'',
            iv=iv,
            tag=tag_all,
            activo=True
        )
        
        db.session.add(cliente)
        db.session.commit()
        
        # Auditoría
        user_id = get_jwt_identity()
        AuthService.log_audit(
            usuario_id=user_id,
            accion='CREATE',
            entidad='clientes',
            entidad_id=cliente.id,
            datos_nuevos={
                'identificacion': data['identificacion'],
                'tipo_identificacion': data['tipo_identificacion']
            }
        )
        
        # Descifrar para respuesta
        decrypted_data = {
            'nombres': data.get('nombres', ''),
            'apellidos': data.get('apellidos', ''),
            'direccion': data.get('direccion', ''),
            'telefono': data.get('telefono', ''),
            'email': data.get('email', '')
        }
        
        return jsonify({
            'success': True,
            'message': 'Cliente creado exitosamente',
            'data': cliente.to_dict(decrypted_data=decrypted_data)
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error creando cliente: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': 'Error en el servidor',
            'details': str(e)
        }), 500


@cliente_bp.route('/<int:cliente_id>', methods=['PUT'])
@jwt_required()
def update_cliente(cliente_id):
    """Actualizar cliente (con cifrado)"""
    try:
        cliente = Cliente.query.get(cliente_id)
        
        if not cliente:
            return jsonify({
                'success': False,
                'error': 'Cliente no encontrado'
            }), 404
        
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No hay datos para actualizar'
            }), 400
        
        # Actualizar campos no cifrados
        if 'tipo_identificacion' in data:
            cliente.tipo_identificacion = data['tipo_identificacion']
        if 'identificacion' in data:
            # Verificar unicidad
            existing = Cliente.query.filter(
                Cliente.identificacion == data['identificacion'],
                Cliente.id != cliente_id
            ).first()
            if existing:
                return jsonify({
                    'success': False,
                    'error': 'Ya existe un cliente con esa identificación'
                }), 400
            cliente.identificacion = data['identificacion']
        if 'razon_social' in data:
            cliente.razon_social = data['razon_social']
        if 'activo' in data:
            cliente.activo = data['activo']
        
        # ✅ CRÍTICO: Cifrar datos sensibles si se proporcionan
        crypto = get_crypto_service()
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        import os
        
        if any(key in data for key in ['nombres', 'apellidos', 'direccion', 'telefono', 'email']):
            # Primero descifrar los datos actuales para mantener los que no se editan
            try:
                if cliente.nombres_enc:
                    encrypted_data = cliente.nombres_enc + cliente.tag
                    aesgcm = AESGCM(crypto.aes_master_key)
                    decrypted_all = aesgcm.decrypt(cliente.iv, encrypted_data, None).decode('utf-8')
                    partes = decrypted_all.split('|')
                    
                    # Valores actuales
                    current_nombres = partes[0] if len(partes) > 0 else ''
                    current_apellidos = partes[1] if len(partes) > 1 else ''
                    current_direccion = partes[2] if len(partes) > 2 else ''
                    current_telefono = partes[3] if len(partes) > 3 else ''
                    current_email = partes[4] if len(partes) > 4 else ''
                else:
                    current_nombres = current_apellidos = current_direccion = current_telefono = current_email = ''
            except:
                current_nombres = current_apellidos = current_direccion = current_telefono = current_email = ''
            
            # Usar valores nuevos si se proporcionan, sino mantener actuales
            new_nombres = data.get('nombres', current_nombres)
            new_apellidos = data.get('apellidos', current_apellidos)
            new_direccion = data.get('direccion', current_direccion)
            new_telefono = data.get('telefono', current_telefono)
            new_email = data.get('email', current_email)
            
            # Generar nuevo IV
            iv = os.urandom(12)
            
            # Concatenar y cifrar todo junto
            datos_concatenados = f"{new_nombres}|{new_apellidos}|{new_direccion}|{new_telefono}|{new_email}"
            aesgcm = AESGCM(crypto.aes_master_key)
            encrypted_all = aesgcm.encrypt(iv, datos_concatenados.encode('utf-8'), None)
            ciphertext_all = encrypted_all[:-16]
            tag_all = encrypted_all[-16:]
            
            # Actualizar campos
            cliente.nombres_enc = ciphertext_all
            cliente.apellidos_enc = b''
            cliente.direccion_enc = b''
            cliente.telefono_enc = b''
            cliente.email_enc = b''
            cliente.iv = iv
            cliente.tag = tag_all
        
        db.session.commit()
        
        # Auditoría
        user_id = get_jwt_identity()
        AuthService.log_audit(
            usuario_id=user_id,
            accion='UPDATE',
            entidad='clientes',
            entidad_id=cliente_id
        )
        
        # Descifrar para respuesta usando el nuevo formato
        try:
            if cliente.nombres_enc:
                encrypted_data = cliente.nombres_enc + cliente.tag
                aesgcm = AESGCM(crypto.aes_master_key)
                decrypted_all = aesgcm.decrypt(cliente.iv, encrypted_data, None).decode('utf-8')
                partes = decrypted_all.split('|')
                decrypted_data = {
                    'nombres': partes[0] if len(partes) > 0 else '',
                    'apellidos': partes[1] if len(partes) > 1 else '',
                    'direccion': partes[2] if len(partes) > 2 else '',
                    'telefono': partes[3] if len(partes) > 3 else '',
                    'email': partes[4] if len(partes) > 4 else ''
                }
            else:
                decrypted_data = {
                    'nombres': '',
                    'apellidos': '',
                    'direccion': '',
                    'telefono': '',
                    'email': ''
                }
        except Exception as e:
            print(f"❌ Error descifrando respuesta: {str(e)}")
            decrypted_data = {
                'nombres': '[ERROR_DESCIFRADO]',
                'apellidos': '[ERROR_DESCIFRADO]',
                'direccion': '[ERROR_DESCIFRADO]',
                'telefono': '[ERROR_DESCIFRADO]',
                'email': '[ERROR_DESCIFRADO]'
            }
        
        return jsonify({
            'success': True,
            'message': 'Cliente actualizado exitosamente',
            'data': cliente.to_dict(decrypted_data=decrypted_data)
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error actualizando cliente {cliente_id}: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': 'Error en el servidor',
            'details': str(e)
        }), 500


@cliente_bp.route('/<int:cliente_id>', methods=['DELETE'])
@jwt_required()
def delete_cliente(cliente_id):
    """Eliminar (desactivar) cliente"""
    try:
        cliente = Cliente.query.get(cliente_id)
        
        if not cliente:
            return jsonify({
                'success': False,
                'error': 'Cliente no encontrado'
            }), 404
        
        # Soft delete
        cliente.activo = False
        db.session.commit()
        
        # Auditoría
        user_id = get_jwt_identity()
        AuthService.log_audit(
            usuario_id=user_id,
            accion='DELETE',
            entidad='clientes',
            entidad_id=cliente_id
        )
        
        return jsonify({
            'success': True,
            'message': 'Cliente eliminado exitosamente'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error eliminando cliente {cliente_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Error en el servidor',
            'details': str(e)
        }), 500
