"""
Rutas de API para Facturas Electrónicas
Endpoints para crear, listar y verificar facturas con firmas RSA y QR
"""

from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from io import BytesIO
from datetime import datetime

from models import db
from models.factura import Factura
from models.cliente import Cliente
from models.user import Usuario
from models.audit_log import AuditLog
from services.factura_service import FacturaService
from services.crypto_service import get_crypto_service
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

factura_bp = Blueprint('facturas', __name__)


def get_factura_service():
    """Lazy initialization del servicio de facturas"""
    if not hasattr(get_factura_service, '_service'):
        get_factura_service._service = FacturaService()
    return get_factura_service._service


@factura_bp.route('/', methods=['GET'])
@jwt_required()
def listar_facturas():
    """
    GET /api/v1/facturas
    Lista todas las facturas con paginación
    Query params: page, per_page, cliente_id, fecha_desde, fecha_hasta
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        cliente_id = request.args.get('cliente_id', type=int)
        fecha_desde = request.args.get('fecha_desde')
        fecha_hasta = request.args.get('fecha_hasta')
        
        # Query base
        query = Factura.query
        
        # Filtros
        if cliente_id:
            query = query.filter(Factura.cliente_id == cliente_id)
        
        if fecha_desde:
            try:
                fecha_desde_dt = datetime.fromisoformat(fecha_desde)
                query = query.filter(Factura.fecha_emision >= fecha_desde_dt)
            except:
                pass
        
        if fecha_hasta:
            try:
                fecha_hasta_dt = datetime.fromisoformat(fecha_hasta)
                query = query.filter(Factura.fecha_emision <= fecha_hasta_dt)
            except:
                pass
        
        # Ordenar por fecha descendente
        query = query.order_by(Factura.fecha_emision.desc())
        
        # Paginar
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        # Incluir datos del cliente en cada factura
        crypto = get_crypto_service()
        facturas_data = []
        for factura in pagination.items:
            factura_dict = factura.to_dict(include_items=True)
            
            # Agregar datos del cliente (desencriptados)
            cliente = Cliente.query.get(factura.cliente_id)
            if cliente:
                # Descifrar datos concatenados
                try:
                    if cliente.nombres_enc:
                        encrypted_data = cliente.nombres_enc + cliente.tag
                        aesgcm = AESGCM(crypto.aes_master_key)
                        decrypted_all = aesgcm.decrypt(cliente.iv, encrypted_data, None).decode('utf-8')
                        partes = decrypted_all.split('|')
                        decrypted_data = {
                            'nombres': partes[0] if len(partes) > 0 else '',
                            'apellidos': partes[1] if len(partes) > 1 else ''
                        }
                    else:
                        decrypted_data = {'nombres': '', 'apellidos': ''}
                    
                    factura_dict['cliente'] = {
                        'id': cliente.id,
                        'identificacion': cliente.identificacion,
                        'tipo_identificacion': cliente.tipo_identificacion,
                        'nombres': decrypted_data.get('nombres', '[ERROR_DESCIFRADO]'),
                        'apellidos': decrypted_data.get('apellidos', '[ERROR_DESCIFRADO]')
                    }
                except Exception as e:
                    print(f"⚠️ Error descifrando cliente {cliente.id}: {e}")
                    factura_dict['cliente'] = {
                        'id': cliente.id,
                        'identificacion': cliente.identificacion,
                        'tipo_identificacion': cliente.tipo_identificacion,
                        'nombres': '[ERROR_DESCIFRADO]',
                        'apellidos': '[ERROR_DESCIFRADO]'
                    }
            
            facturas_data.append(factura_dict)
        
        return jsonify({
            'facturas': facturas_data,
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page,
            'per_page': per_page
        }), 200
        
    except Exception as e:
        print(f"❌ Error listando facturas: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500


@factura_bp.route('/', methods=['POST'])
@jwt_required()
def crear_factura():
    """
    POST /api/v1/facturas
    Crea una factura electrónica con firma RSA y QR
    Body: {cliente_id, items: [{codigo, nombre, cantidad, precio_unitario, iva_porcentaje}], observaciones}
    """
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validar datos requeridos
        if not data.get('cliente_id'):
            return jsonify({'error': 'cliente_id es requerido'}), 400
        
        if not data.get('items') or not isinstance(data['items'], list) or len(data['items']) == 0:
            return jsonify({'error': 'items es requerido y debe contener al menos un producto'}), 400
        
        # Validar estructura de items
        for idx, item in enumerate(data['items']):
            if not all(k in item for k in ['cantidad', 'precio_unitario']):
                return jsonify({'error': f'Item {idx} debe tener cantidad y precio_unitario'}), 400
        
        # Crear factura usando el servicio
        factura = get_factura_service().crear_factura(
            usuario_id=current_user_id,
            cliente_id=data['cliente_id'],
            items=data['items'],
            observaciones=data.get('observaciones')
        )
        
        # Registrar auditoría
        audit_log = AuditLog(
            usuario_id=current_user_id,
            accion='CREATE',
            entidad='facturas',
            entidad_id=factura.id,
            datos_anteriores=None,
            datos_nuevos={'numero_factura': factura.numero_factura, 'total': float(factura.total)},
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent', ''),
            resultado='EXITO'
        )
        db.session.add(audit_log)
        db.session.commit()
        
        # Preparar respuesta con datos completos
        factura_dict = factura.to_dict(include_items=True)
        
        # Agregar datos del cliente
        cliente = Cliente.query.get(factura.cliente_id)
        if cliente:
            # Descifrar datos concatenados
            crypto = get_crypto_service()
            try:
                if cliente.nombres_enc:
                    encrypted_data = cliente.nombres_enc + cliente.tag
                    aesgcm = AESGCM(crypto.aes_master_key)
                    decrypted_all = aesgcm.decrypt(cliente.iv, encrypted_data, None).decode('utf-8')
                    partes = decrypted_all.split('|')
                    decrypted_data = {
                        'nombres': partes[0] if len(partes) > 0 else '',
                        'apellidos': partes[1] if len(partes) > 1 else ''
                    }
                else:
                    decrypted_data = {'nombres': '', 'apellidos': ''}
                
                factura_dict['cliente'] = {
                    'identificacion': cliente.identificacion,
                    'nombres': decrypted_data.get('nombres', '[ERROR_DESCIFRADO]'),
                    'apellidos': decrypted_data.get('apellidos', '[ERROR_DESCIFRADO]')
                }
            except Exception as e:
                print(f"⚠️ Error descifrando cliente {cliente.id}: {e}")
                factura_dict['cliente'] = {
                    'identificacion': cliente.identificacion,
                    'nombres': '[ERROR_DESCIFRADO]',
                    'apellidos': '[ERROR_DESCIFRADO]'
                }
        
        return jsonify(factura_dict), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        print(f"❌ Error creando factura: {e}")
        db.session.rollback()
        return jsonify({'error': f'Error interno del servidor: {str(e)}'}), 500


@factura_bp.route('/<int:factura_id>', methods=['GET'])
@jwt_required()
def obtener_factura(factura_id):
    """
    GET /api/v1/facturas/:id
    Obtiene una factura específica con todos sus datos
    """
    try:
        factura = Factura.query.get(factura_id)
        
        if not factura:
            return jsonify({'error': 'Factura no encontrada'}), 404
        
        factura_dict = factura.to_dict(include_items=True)
        
        # Agregar datos completos del cliente
        cliente = Cliente.query.get(factura.cliente_id)
        if cliente:
            # Descifrar datos concatenados
            crypto = get_crypto_service()
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
                    decrypted_data = {'nombres': '', 'apellidos': '', 'direccion': '', 'telefono': '', 'email': ''}
                
                factura_dict['cliente'] = cliente.to_dict(decrypted_data=decrypted_data)
            except Exception as e:
                print(f"⚠️ Error descifrando cliente {cliente.id}: {e}")
                import traceback
                traceback.print_exc()
                factura_dict['cliente'] = cliente.to_dict()
        
        # Agregar datos del usuario emisor
        usuario = Usuario.query.get(factura.usuario_id)
        if usuario:
            factura_dict['usuario'] = {
                'id': usuario.id,
                'username': usuario.username,
                'nombres': usuario.nombres,
                'apellidos': usuario.apellidos
            }
        
        return jsonify(factura_dict), 200
        
    except Exception as e:
        print(f"❌ Error obteniendo factura: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Error interno del servidor'}), 500


@factura_bp.route('/<int:factura_id>/xml', methods=['GET'])
@jwt_required()
def descargar_xml(factura_id):
    """
    GET /api/v1/facturas/:id/xml
    Descarga el XML firmado de la factura
    """
    try:
        factura = Factura.query.get(factura_id)
        
        if not factura:
            return jsonify({'error': 'Factura no encontrada'}), 404
        
        if not factura.xml_firmado:
            return jsonify({'error': 'XML no disponible'}), 404
        
        # Crear archivo en memoria
        xml_bytes = factura.xml_firmado.encode('utf-8')
        xml_buffer = BytesIO(xml_bytes)
        xml_buffer.seek(0)
        
        filename = f"factura_{factura.numero_factura.replace('-', '_')}.xml"
        
        return send_file(
            xml_buffer,
            mimetype='application/xml',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        print(f"❌ Error descargando XML: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500


@factura_bp.route('/verificar/<string:hash_sha256>', methods=['GET'])
def verificar_factura(hash_sha256):
    """
    GET /api/v1/facturas/verificar/:hash
    Endpoint PÚBLICO para verificar autenticidad de factura (sin JWT)
    Usado por el código QR
    """
    try:
        resultado = get_factura_service().verificar_integridad(hash_sha256)
        
        # Siempre devolver 200, el cliente decide cómo manejar valida=true/false
        return jsonify(resultado), 200
        
    except Exception as e:
        print(f"❌ Error verificando factura: {e}")
        return jsonify({
            'status': 'ERROR',
            'valida': False,
            'mensaje': 'Error en el servidor al verificar la factura'
        }), 500


@factura_bp.route('/estadisticas', methods=['GET'])
@jwt_required()
def obtener_estadisticas():
    """
    GET /api/v1/facturas/estadisticas
    Obtiene estadísticas generales de facturación
    """
    try:
        # Total de facturas
        total_facturas = Factura.query.count()
        
        # Total facturado
        total_facturado = db.session.query(
            db.func.sum(Factura.total)
        ).scalar() or 0
        
        # Facturas del mes actual
        from datetime import date
        primer_dia_mes = date.today().replace(day=1)
        facturas_mes = Factura.query.filter(
            Factura.fecha_emision >= primer_dia_mes
        ).count()
        
        total_mes = db.session.query(
            db.func.sum(Factura.total)
        ).filter(
            Factura.fecha_emision >= primer_dia_mes
        ).scalar() or 0
        
        # Facturas por estado SRI
        facturas_por_estado = db.session.query(
            Factura.estado_sri,
            db.func.count(Factura.id)
        ).group_by(Factura.estado_sri).all()
        
        estados_dict = {estado: count for estado, count in facturas_por_estado}
        
        return jsonify({
            'total_facturas': total_facturas,
            'total_facturado': float(total_facturado),
            'facturas_mes': facturas_mes,
            'total_mes': float(total_mes),
            'estados': estados_dict
        }), 200
        
    except Exception as e:
        print(f"❌ Error obteniendo estadísticas: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500
