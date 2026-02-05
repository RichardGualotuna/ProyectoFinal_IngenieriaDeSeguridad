# Arquitectura del Sistema de Facturación Electrónica

## 1. Vista General de la Arquitectura

### Arquitectura en Capas (Layered Architecture)

```
┌─────────────────────────────────────────────────────────────┐
│                   CAPA DE PRESENTACIÓN                      │
│                      (Frontend Layer)                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │  React SPA  │  │  Tailwind   │  │  React      │        │
│  │  Components │  │  CSS        │  │  Router     │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────┘
                          ↕ HTTPS (TLS 1.3)
┌─────────────────────────────────────────────────────────────┐
│                    CAPA DE API (REST)                       │
│                   (API Gateway Layer)                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   Flask     │  │    CORS     │  │    JWT      │        │
│  │   Routes    │  │   Middleware│  │    Auth     │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────┘
                              ↕
┌─────────────────────────────────────────────────────────────┐
│               CAPA DE LÓGICA DE NEGOCIO                     │
│                  (Business Logic Layer)                      │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐       │
│  │  Facturación │ │   Crypto     │ │    Auth      │       │
│  │   Service    │ │   Service    │ │   Service    │       │
│  └──────────────┘ └──────────────┘ └──────────────┘       │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐       │
│  │   Validators │ │  QR Generator│ │ XML Generator│       │
│  └──────────────┘ └──────────────┘ └──────────────┘       │
└─────────────────────────────────────────────────────────────┘
                              ↕
┌─────────────────────────────────────────────────────────────┐
│                CAPA DE ACCESO A DATOS                       │
│                  (Data Access Layer)                         │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐       │
│  │  SQLAlchemy  │ │   Models     │ │  Migrations  │       │
│  │     ORM      │ │  (Entities)  │ │  (Alembic)   │       │
│  └──────────────┘ └──────────────┘ └──────────────┘       │
└─────────────────────────────────────────────────────────────┘
                              ↕
┌─────────────────────────────────────────────────────────────┐
│                   CAPA DE PERSISTENCIA                      │
│                   (Persistence Layer)                        │
│  ┌──────────────────────────────────────────────────────┐  │
│  │          PostgreSQL 15 Database                      │  │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐  │  │
│  │  │Empresas │ │Clientes │ │Facturas │ │Usuarios │  │  │
│  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘  │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              ↕
┌─────────────────────────────────────────────────────────────┐
│                ALMACENAMIENTO EXTERNO                       │
│                  (External Storage)                          │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐       │
│  │Claves RSA    │ │  Archivos    │ │   Backups    │       │
│  │(Filesystem)  │ │  PDF/XML     │ │  (Cifrados)  │       │
│  └──────────────┘ └──────────────┘ └──────────────┘       │
└─────────────────────────────────────────────────────────────┘
```

## 2. Patrones Arquitectónicos Aplicados

### 2.1 MVC (Model-View-Controller) Modificado

**Model (Modelo)**:
- Entidades SQLAlchemy
- Representa estructura de datos
- Validaciones básicas de integridad

**View (Vista)**:
- Componentes React
- Presentación de datos al usuario
- Interacción frontend

**Controller (Controlador)**:
- Routes de Flask
- Orquestación de servicios
- Manejo de peticiones HTTP

### 2.2 Repository Pattern

```python
# Abstracción del acceso a datos
class BaseRepository:
    def __init__(self, model):
        self.model = model
    
    def get_by_id(self, id):
        return db.session.query(self.model).get(id)
    
    def get_all(self):
        return db.session.query(self.model).all()
    
    def create(self, **kwargs):
        instance = self.model(**kwargs)
        db.session.add(instance)
        db.session.commit()
        return instance
    
    def update(self, id, **kwargs):
        instance = self.get_by_id(id)
        for key, value in kwargs.items():
            setattr(instance, key, value)
        db.session.commit()
        return instance
    
    def delete(self, id):
        instance = self.get_by_id(id)
        db.session.delete(instance)
        db.session.commit()
```

### 2.3 Service Layer Pattern

```python
# Lógica de negocio encapsulada
class FacturacionService:
    def __init__(self):
        self.factura_repo = FacturaRepository()
        self.crypto_service = CryptoService()
        self.qr_service = QRService()
    
    def crear_factura(self, datos_factura, usuario_id):
        # 1. Validar datos
        # 2. Calcular totales
        # 3. Generar XML
        # 4. Firmar digitalmente
        # 5. Generar QR
        # 6. Guardar en BD
        # 7. Registrar auditoría
        pass
```

### 2.4 Dependency Injection

```python
# Inyección de dependencias para testabilidad
class FacturaController:
    def __init__(self, facturacion_service=None):
        self.facturacion_service = facturacion_service or FacturacionService()
    
    def crear_factura(self):
        # Usar servicio inyectado
        pass
```

## 3. Componentes del Sistema

### 3.1 Frontend Components

```
src/
├── components/
│   ├── common/
│   │   ├── Button.jsx
│   │   ├── Input.jsx
│   │   ├── Modal.jsx
│   │   ├── Table.jsx
│   │   └── Alert.jsx
│   ├── facturacion/
│   │   ├── FormularioFactura.jsx
│   │   ├── DetalleFactura.jsx
│   │   ├── ListaFacturas.jsx
│   │   └── VistaFacturaPDF.jsx
│   ├── clientes/
│   │   ├── FormularioCliente.jsx
│   │   ├── ListaClientes.jsx
│   │   └── DetalleCliente.jsx
│   ├── verificacion/
│   │   ├── EscanerQR.jsx
│   │   ├── VerificadorFactura.jsx
│   │   └── ResultadoVerificacion.jsx
│   └── reportes/
│       ├── ReporteVentas.jsx
│       ├── ExportadorXML.jsx
│       └── Dashboard.jsx
│
├── contexts/
│   ├── AuthContext.jsx
│   └── NotificationContext.jsx
│
├── services/
│   ├── api.js
│   ├── facturacionService.js
│   ├── authService.js
│   └── cryptoService.js
│
└── utils/
    ├── validators.js
    ├── formatters.js
    └── constants.js
```

### 3.2 Backend Modules

```
backend/
├── models/
│   ├── base.py              # Base model
│   ├── empresa.py
│   ├── cliente.py
│   ├── usuario.py
│   ├── factura.py
│   ├── detalle_factura.py
│   └── audit_log.py
│
├── routes/
│   ├── auth_routes.py       # Login, logout, registro
│   ├── factura_routes.py    # CRUD facturas
│   ├── cliente_routes.py    # CRUD clientes
│   ├── empresa_routes.py    # Configuración empresa
│   ├── verificacion_routes.py
│   ├── reporte_routes.py
│   └── audit_routes.py
│
├── services/
│   ├── auth_service.py      # Autenticación, JWT
│   ├── crypto_service.py    # RSA, AES, SHA-256
│   ├── facturacion_service.py
│   ├── qr_service.py
│   ├── xml_service.py
│   └── email_service.py
│
├── repositories/
│   ├── base_repository.py
│   ├── factura_repository.py
│   ├── cliente_repository.py
│   └── usuario_repository.py
│
├── utils/
│   ├── validators.py        # Validaciones de entrada
│   ├── formatters.py        # Formateo de datos
│   ├── sri_validator.py     # Validación RUC, cédula
│   └── helpers.py
│
├── config/
│   ├── config.py           # Configuración app
│   ├── database.py         # Conexión BD
│   └── crypto_config.py    # Config criptográfica
│
└── app.py                  # Entry point
```

## 4. Flujos de Datos Principales

### 4.1 Flujo de Autenticación

```
┌──────┐                ┌──────────┐                ┌──────────┐
│Client│                │  Flask   │                │PostgreSQL│
└──┬───┘                └────┬─────┘                └────┬─────┘
   │                         │                           │
   │  POST /api/auth/login   │                           │
   │  {email, password}      │                           │
   ├────────────────────────>│                           │
   │                         │                           │
   │                         │ SELECT * FROM usuarios    │
   │                         │ WHERE email = ?           │
   │                         ├──────────────────────────>│
   │                         │                           │
   │                         │<──────user_data───────────│
   │                         │                           │
   │                         │ bcrypt.checkpw()          │
   │                         │ (verify password)         │
   │                         │                           │
   │                         │ generate_jwt_token()      │
   │                         │ (create token)            │
   │                         │                           │
   │  {token, user}          │                           │
   │<────────────────────────│                           │
   │                         │                           │
```

### 4.2 Flujo de Creación de Factura

```
┌──────┐     ┌───────┐     ┌────────┐     ┌──────┐     ┌──────┐
│Client│     │ Flask │     │Crypto  │     │  QR  │     │  DB  │
└──┬───┘     └───┬───┘     │Service │     │Service│    └──┬───┘
   │             │          └───┬────┘     └───┬──┘       │
   │ POST /api/  │              │              │           │
   │ facturas    │              │              │           │
   ├────────────>│              │              │           │
   │             │              │              │           │
   │             │ Validar JWT  │              │           │
   │             │              │              │           │
   │             │ Validar datos│              │           │
   │             │ Calcular IVA │              │           │
   │             │              │              │           │
   │             │ Generar XML  │              │           │
   │             │              │              │           │
   │             │ SHA256(XML) ─┤              │           │
   │             │              │              │           │
   │             │<─────hash────│              │           │
   │             │              │              │           │
   │             │ sign_rsa()───┤              │           │
   │             │              │              │           │
   │             │<───signature─│              │           │
   │             │              │              │           │
   │             │ gen_qr()─────┼──────────────┤           │
   │             │              │              │           │
   │             │<──────────────qr_image──────│           │
   │             │              │              │           │
   │             │ INSERT factura               │           │
   │             ├─────────────────────────────────────────>│
   │             │                             │           │
   │             │<─────────factura_id─────────────────────│
   │             │              │              │           │
   │  {factura}  │              │              │           │
   │<────────────│              │              │           │
   │             │              │              │           │
```

### 4.3 Flujo de Verificación de Factura

```
┌──────┐           ┌───────┐           ┌────────┐           ┌──────┐
│Client│           │ Flask │           │Crypto  │           │  DB  │
│(QR)  │           │       │           │Service │           │      │
└──┬───┘           └───┬───┘           └───┬────┘           └──┬───┘
   │                   │                   │                   │
   │ Escanear QR       │                   │                   │
   │ (hash, num_autor) │                   │                   │
   │                   │                   │                   │
   │ GET /api/verificar│                   │                   │
   │ ?num_autor=xxx    │                   │                   │
   ├──────────────────>│                   │                   │
   │                   │                   │                   │
   │                   │ SELECT * FROM facturas               │
   │                   │ WHERE num_autorizacion = ?           │
   │                   ├────────────────────────────────────>│
   │                   │                   │                   │
   │                   │<─────factura_data─────────────────────│
   │                   │                   │                   │
   │                   │ SHA256(factura)───┤                   │
   │                   │                   │                   │
   │                   │<──calculated_hash─│                   │
   │                   │                   │                   │
   │                   │ stored_hash == calculated_hash?       │
   │                   │                   │                   │
   │                   │ verify_rsa()──────┤                   │
   │                   │                   │                   │
   │                   │<─signature_valid──│                   │
   │                   │                   │                   │
   │  {                │                   │                   │
   │    valid: true,   │                   │                   │
   │    hash_match: ✅ │                   │                   │
   │    firma_valid: ✅│                   │                   │
   │    datos_factura  │                   │                   │
   │  }                │                   │                   │
   │<──────────────────│                   │                   │
   │                   │                   │                   │
```

## 5. Seguridad Arquitectónica

### 5.1 Capas de Seguridad

```
┌──────────────────────────────────────────────────────────┐
│ CAPA 1: Transporte (HTTPS/TLS 1.3)                     │
│ • Cifrado end-to-end                                     │
│ • Certificado SSL/TLS                                    │
└──────────────────────────────────────────────────────────┘
                          ↓
┌──────────────────────────────────────────────────────────┐
│ CAPA 2: Autenticación (JWT + Bcrypt)                    │
│ • Token JWT con expiración                               │
│ • Refresh tokens                                         │
│ • Contraseñas hasheadas con bcrypt                       │
└──────────────────────────────────────────────────────────┘
                          ↓
┌──────────────────────────────────────────────────────────┐
│ CAPA 3: Autorización (RBAC)                             │
│ • Roles: Admin, Facturador, Contador                     │
│ • Permisos granulares por endpoint                       │
│ • Validación de permisos en cada request                 │
└──────────────────────────────────────────────────────────┘
                          ↓
┌──────────────────────────────────────────────────────────┐
│ CAPA 4: Validación de Entrada                           │
│ • Sanitización de inputs                                 │
│ • Validación de tipos y formatos                         │
│ • Protección contra injection                            │
└──────────────────────────────────────────────────────────┘
                          ↓
┌──────────────────────────────────────────────────────────┐
│ CAPA 5: Lógica de Negocio                               │
│ • Validaciones de dominio                                │
│ • Reglas de negocio aplicadas                            │
└──────────────────────────────────────────────────────────┘
                          ↓
┌──────────────────────────────────────────────────────────┐
│ CAPA 6: Cifrado de Datos (AES-256)                      │
│ • Datos sensibles cifrados at-rest                       │
│ • Claves gestionadas centralmente                        │
└──────────────────────────────────────────────────────────┘
                          ↓
┌──────────────────────────────────────────────────────────┐
│ CAPA 7: Integridad (SHA-256 + RSA)                      │
│ • Hash de cada factura                                   │
│ • Firma digital RSA                                      │
│ • Detección de alteraciones                              │
└──────────────────────────────────────────────────────────┘
                          ↓
┌──────────────────────────────────────────────────────────┐
│ CAPA 8: Auditoría                                        │
│ • Log de todas las operaciones                           │
│ • Trazabilidad completa                                  │
│ • Registros inmutables                                   │
└──────────────────────────────────────────────────────────┘
```

### 5.2 Middleware Stack

```python
# Orden de ejecución de middleware
app = Flask(__name__)

# 1. CORS (primero)
CORS(app, origins=['https://frontend.com'])

# 2. Rate Limiting
limiter = Limiter(app, key_func=get_remote_address)
@limiter.limit("100/minute")

# 3. Request Logging
@app.before_request
def log_request():
    logger.info(f"{request.method} {request.path}")

# 4. JWT Validation
@app.before_request
def validate_jwt():
    if request.endpoint not in ['auth.login', 'auth.register']:
        verify_jwt_in_request()

# 5. RBAC Authorization
@app.before_request
def check_permissions():
    if current_user.role not in get_required_roles(request.endpoint):
        abort(403)

# 6. Input Validation
@app.before_request
def validate_input():
    # Sanitizar y validar datos de entrada
    pass

# 7. CSRF Protection (si usa cookies)
CSRFProtect(app)
```

## 6. Escalabilidad y Performance

### 6.1 Estrategias de Optimización

**Caching**:
```python
from flask_caching import Cache

cache = Cache(config={'CACHE_TYPE': 'redis'})

@cache.cached(timeout=300, key_prefix='lista_clientes')
def get_clientes():
    # Cachear lista de clientes por 5 min
    pass
```

**Database Indexing**:
```sql
-- Índices para mejorar consultas frecuentes
CREATE INDEX idx_factura_numero ON facturas(numero_factura);
CREATE INDEX idx_factura_fecha ON facturas(fecha_emision);
CREATE INDEX idx_factura_cliente ON facturas(cliente_id);
CREATE INDEX idx_cliente_identificacion ON clientes(identificacion);
```

**Lazy Loading**:
```python
# SQLAlchemy lazy loading de relaciones
class Factura(db.Model):
    # Solo cargar detalles cuando se acceden
    detalles = db.relationship('DetalleFactura', lazy='select')
```

**Pagination**:
```python
@app.route('/api/facturas')
def get_facturas():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    facturas = Factura.query.paginate(
        page=page, per_page=per_page, error_out=False
    )
    return jsonify({
        'items': [f.to_dict() for f in facturas.items],
        'total': facturas.total,
        'pages': facturas.pages
    })
```

### 6.2 Arquitectura para Escalamiento Horizontal

```
                    ┌──────────────┐
                    │  Load        │
                    │  Balancer    │
                    │  (Nginx)     │
                    └──────┬───────┘
                           │
         ┌─────────────────┼─────────────────┐
         │                 │                 │
    ┌────▼────┐      ┌────▼────┐      ┌────▼────┐
    │ Flask   │      │ Flask   │      │ Flask   │
    │ App 1   │      │ App 2   │      │ App 3   │
    └────┬────┘      └────┬────┘      └────┬────┘
         │                 │                 │
         └─────────────────┼─────────────────┘
                           │
                    ┌──────▼───────┐
                    │  PostgreSQL  │
                    │  (Primary)   │
                    └──────┬───────┘
                           │
                    ┌──────▼───────┐
                    │  PostgreSQL  │
                    │  (Replica)   │
                    └──────────────┘
```

## 7. Monitoreo y Logging

### 7.1 Estructura de Logs

```python
import logging
from pythonjsonlogger import jsonlogger

# Configuración de logging estructurado
logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter()
logHandler.setFormatter(formatter)

logger = logging.getLogger()
logger.addHandler(logHandler)
logger.setLevel(logging.INFO)

# Ejemplo de uso
logger.info('Factura creada', extra={
    'usuario_id': user.id,
    'factura_id': factura.id,
    'total': factura.total,
    'ip': request.remote_addr
})
```

### 7.2 Métricas de Sistema

```python
from prometheus_flask_exporter import PrometheusMetrics

metrics = PrometheusMetrics(app)

# Métricas personalizadas
facturas_counter = metrics.counter(
    'facturas_created_total',
    'Total de facturas creadas'
)

@app.route('/api/facturas', methods=['POST'])
def crear_factura():
    # ... lógica ...
    facturas_counter.inc()
    return jsonify(factura.to_dict())
```

## 8. Manejo de Errores

### 8.1 Jerarquía de Excepciones

```python
class FacturaSeguraException(Exception):
    """Base exception"""
    pass

class ValidationError(FacturaSeguraException):
    """Error de validación de datos"""
    status_code = 400

class AuthenticationError(FacturaSeguraException):
    """Error de autenticación"""
    status_code = 401

class AuthorizationError(FacturaSeguraException):
    """Error de autorización"""
    status_code = 403

class NotFoundError(FacturaSeguraException):
    """Recurso no encontrado"""
    status_code = 404

class CryptoError(FacturaSeguraException):
    """Error en operaciones criptográficas"""
    status_code = 500
```

### 8.2 Error Handler Global

```python
@app.errorhandler(FacturaSeguraException)
def handle_exception(error):
    response = {
        'error': error.__class__.__name__,
        'message': str(error),
        'timestamp': datetime.utcnow().isoformat()
    }
    return jsonify(response), error.status_code

@app.errorhandler(500)
def internal_error(error):
    logger.error('Internal server error', exc_info=True)
    return jsonify({
        'error': 'InternalServerError',
        'message': 'Ha ocurrido un error interno'
    }), 500
```

## 9. Configuración por Ambientes

```python
# config.py
class Config:
    """Configuración base"""
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
class DevelopmentConfig(Config):
    """Desarrollo"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'postgresql://localhost/facturasegura_dev'
    
class TestingConfig(Config):
    """Testing"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'postgresql://localhost/facturasegura_test'
    
class ProductionConfig(Config):
    """Producción"""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig
}
```

## 10. Resumen de Decisiones Arquitectónicas

| Aspecto | Decisión | Justificación |
|---------|----------|---------------|
| **Arquitectura** | Layered + Service | Separación de responsabilidades, testeable |
| **Framework Web** | Flask | Ligero, flexible, bien documentado |
| **ORM** | SQLAlchemy | Maduro, soporte PostgreSQL excelente |
| **Base de Datos** | PostgreSQL | Open source, robusto, ACID compliant |
| **Autenticación** | JWT + Bcrypt | Stateless, escalable, seguro |
| **API Style** | RESTful | Estándar de la industria, interoperable |
| **Frontend** | React SPA | Componentización, ecosistema rico |
| **Empaquetado** | Docker | Portabilidad, consistencia entre ambientes |

## Próximos Pasos

Con la arquitectura definida, procederemos al diseño detallado de la base de datos en el siguiente documento.
