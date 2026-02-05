-- ============================================================================
-- SCRIPT DE CREACIÓN DE BASE DE DATOS - VERSIÓN ACTUALIZADA
-- Sistema de Facturación Electrónica con Firma Digital
-- Base de datos: richard_db
-- PostgreSQL 12+
-- ============================================================================

-- Conectar a la base de datos richard_db
\c richard_db;

-- Eliminar tablas si existen (para recrear schema limpio)
DROP TABLE IF EXISTS audit_log CASCADE;
DROP TABLE IF EXISTS factura CASCADE;
DROP TABLE IF EXISTS cliente CASCADE;
DROP TABLE IF EXISTS usuario CASCADE;
DROP TABLE IF EXISTS empresa CASCADE;
DROP TABLE IF EXISTS configuracion CASCADE;

-- ============================================================================
-- TABLA: EMPRESA
-- Almacena información de la empresa emisora de facturas
-- ============================================================================
CREATE TABLE empresa (
    id SERIAL PRIMARY KEY,
    ruc VARCHAR(13) NOT NULL UNIQUE,
    razon_social VARCHAR(300) NOT NULL,
    nombre_comercial VARCHAR(300),
    direccion TEXT NOT NULL,
    telefono VARCHAR(20),
    email VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT chk_empresa_ruc CHECK (LENGTH(ruc) = 13)
);

CREATE INDEX idx_empresa_ruc ON empresa(ruc);

COMMENT ON TABLE empresa IS 'Información de la empresa emisora de facturas electrónicas';

-- ============================================================================
-- TABLA: USUARIO
-- Gestión de usuarios del sistema con diferentes roles
-- ============================================================================
CREATE TABLE usuario (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(60) NOT NULL,
    nombres VARCHAR(100) NOT NULL,
    apellidos VARCHAR(100) NOT NULL,
    rol VARCHAR(20) NOT NULL DEFAULT 'FACTURADOR',
    activo BOOLEAN DEFAULT TRUE,
    ultimo_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT chk_usuario_rol CHECK (rol IN ('ADMIN', 'FACTURADOR', 'CONTADOR', 'AUDITOR'))
);

CREATE INDEX idx_usuario_username ON usuario(username);
CREATE INDEX idx_usuario_email ON usuario(email);
CREATE INDEX idx_usuario_activo ON usuario(activo);

COMMENT ON TABLE usuario IS 'Usuarios del sistema con control de acceso basado en roles';
COMMENT ON COLUMN usuario.password_hash IS 'Hash bcrypt de la contraseña (60 caracteres)';
COMMENT ON COLUMN usuario.rol IS 'ADMIN: control total | FACTURADOR: crear facturas | CONTADOR: reportes | AUDITOR: solo lectura';

-- ============================================================================
-- TABLA: CLIENTE
-- Almacenar información de clientes con datos sensibles cifrados
-- ============================================================================
CREATE TABLE cliente (
    id SERIAL PRIMARY KEY,
    tipo_identificacion VARCHAR(10) NOT NULL,
    identificacion VARCHAR(20) NOT NULL UNIQUE,
    razon_social VARCHAR(300),
    nombres_enc BYTEA,
    apellidos_enc BYTEA,
    direccion_enc BYTEA,
    telefono_enc BYTEA,
    email_enc BYTEA,
    iv BYTEA NOT NULL,
    tag BYTEA,
    activo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT chk_cliente_tipo_identificacion CHECK (
        tipo_identificacion IN ('RUC', 'CEDULA', 'PASAPORTE', 'CONSUMIDOR_FINAL')
    )
);

CREATE INDEX idx_cliente_identificacion ON cliente(identificacion);
CREATE INDEX idx_cliente_tipo ON cliente(tipo_identificacion);
CREATE INDEX idx_cliente_activo ON cliente(activo);

COMMENT ON TABLE cliente IS 'Clientes con datos personales cifrados con AES-256-GCM';
COMMENT ON COLUMN cliente.nombres_enc IS 'Todos los datos cifrados concatenados (nombres|apellidos|direccion|telefono|email)';
COMMENT ON COLUMN cliente.iv IS 'Vector de inicialización único por registro (12 bytes para GCM)';
COMMENT ON COLUMN cliente.tag IS 'Tag de autenticación de AES-GCM para detectar manipulación (16 bytes)';

-- ============================================================================
-- TABLA: FACTURA (MODELO SIMPLIFICADO)
-- Facturas electrónicas con firma digital RSA-2048
-- ============================================================================
CREATE TABLE factura (
    id SERIAL PRIMARY KEY,
    cliente_id INTEGER NOT NULL,
    usuario_id INTEGER NOT NULL,
    numero_factura VARCHAR(17) NOT NULL UNIQUE,
    fecha_emision TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    subtotal NUMERIC(12, 2) NOT NULL DEFAULT 0.00,
    iva NUMERIC(12, 2) NOT NULL DEFAULT 0.00,
    total NUMERIC(12, 2) NOT NULL,
    items JSONB NOT NULL,
    xml_firmado TEXT,
    hash_sha256 VARCHAR(64) NOT NULL UNIQUE,
    firma_digital TEXT NOT NULL,
    num_autorizacion VARCHAR(49),
    fecha_autorizacion TIMESTAMP,
    estado_sri VARCHAR(20) DEFAULT 'AUTORIZADO',
    qr_image TEXT,
    qr_data TEXT,
    observaciones TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_factura_cliente FOREIGN KEY (cliente_id) 
        REFERENCES cliente(id) ON DELETE RESTRICT,
    CONSTRAINT fk_factura_usuario FOREIGN KEY (usuario_id) 
        REFERENCES usuario(id) ON DELETE RESTRICT,
    
    CONSTRAINT chk_factura_numero_factura CHECK (numero_factura ~ '^[0-9]{3}-[0-9]{3}-[0-9]{9}$'),
    CONSTRAINT chk_factura_total_positivo CHECK (total >= 0),
    CONSTRAINT chk_factura_estado CHECK (estado_sri IN ('AUTORIZADO', 'RECHAZADO')),
    CONSTRAINT chk_factura_hash_sha256 CHECK (LENGTH(hash_sha256) = 64)
);

CREATE INDEX idx_factura_numero ON factura(numero_factura);
CREATE INDEX idx_factura_fecha ON factura(fecha_emision);
CREATE INDEX idx_factura_cliente ON factura(cliente_id);
CREATE INDEX idx_factura_usuario ON factura(usuario_id);
CREATE INDEX idx_factura_estado ON factura(estado_sri);
CREATE UNIQUE INDEX idx_factura_hash ON factura(hash_sha256);
CREATE INDEX idx_factura_num_autorizacion ON factura(num_autorizacion);

COMMENT ON TABLE factura IS 'Facturas electrónicas con firma digital RSA-2048 y hash SHA-256';
COMMENT ON COLUMN factura.items IS 'Array JSON con productos: [{codigo, nombre, cantidad, precio_unitario, iva_porcentaje}]';
COMMENT ON COLUMN factura.hash_sha256 IS 'Hash SHA-256 del XML para verificar integridad (64 caracteres hex)';
COMMENT ON COLUMN factura.firma_digital IS 'Firma RSA-2048 con PSS padding del hash (base64)';
COMMENT ON COLUMN factura.num_autorizacion IS 'Número de autorización SRI simulado (49 dígitos)';
COMMENT ON COLUMN factura.qr_image IS 'Código QR en formato data URI (imagen PNG en base64)';
COMMENT ON COLUMN factura.qr_data IS 'Datos del QR: URL de verificación con hash';

-- ============================================================================
-- TABLA: AUDIT_LOG
-- Registro de auditoría para trazabilidad completa
-- ============================================================================
CREATE TABLE audit_log (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER,
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    accion VARCHAR(50) NOT NULL,
    entidad VARCHAR(50) NOT NULL,
    entidad_id INTEGER,
    datos_anteriores JSONB,
    datos_nuevos JSONB,
    ip_address VARCHAR(45),
    user_agent TEXT,
    resultado VARCHAR(20) DEFAULT 'EXITO',
    mensaje_error TEXT,
    
    CONSTRAINT fk_audit_usuario FOREIGN KEY (usuario_id) 
        REFERENCES usuario(id) ON DELETE SET NULL,
    
    CONSTRAINT chk_audit_accion CHECK (
        accion IN ('LOGIN', 'LOGOUT', 'CREATE', 'UPDATE', 'DELETE', 'READ', 'EXPORT', 'VERIFY')
    ),
    CONSTRAINT chk_audit_resultado CHECK (resultado IN ('EXITO', 'ERROR', 'DENEGADO'))
);

CREATE INDEX idx_audit_usuario ON audit_log(usuario_id);
CREATE INDEX idx_audit_timestamp ON audit_log(timestamp);
CREATE INDEX idx_audit_accion ON audit_log(accion);
CREATE INDEX idx_audit_entidad ON audit_log(entidad, entidad_id);

COMMENT ON TABLE audit_log IS 'Registro de auditoría completo para trazabilidad y cumplimiento';

-- ============================================================================
-- TABLA: CONFIGURACION
-- Configuración del sistema
-- ============================================================================
CREATE TABLE configuracion (
    id SERIAL PRIMARY KEY,
    clave VARCHAR(100) NOT NULL UNIQUE,
    valor TEXT,
    tipo_dato VARCHAR(20) DEFAULT 'STRING',
    descripcion TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT chk_config_tipo_dato CHECK (tipo_dato IN ('STRING', 'INTEGER', 'BOOLEAN', 'JSON'))
);

CREATE INDEX idx_config_clave ON configuracion(clave);

COMMENT ON TABLE configuracion IS 'Configuración del sistema en formato clave-valor';

-- ============================================================================
-- DATOS INICIALES
-- ============================================================================

-- Usuario admin por defecto (contraseña: admin123!)
INSERT INTO usuario (username, email, password_hash, nombres, apellidos, rol, activo)
VALUES (
    'admin',
    'admin@facturacion.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5ygOQ3ZPrn4zW',
    'Administrador',
    'Sistema',
    'ADMIN',
    TRUE
);

-- Empresa de ejemplo
INSERT INTO empresa (ruc, razon_social, nombre_comercial, direccion, telefono, email)
VALUES (
    '1790123456001',
    'EMPRESA DE FACTURACIÓN ELECTRÓNICA S.A.',
    'FactElec',
    'Av. Principal 123 y Secundaria, Quito - Ecuador',
    '(02) 2345678',
    'info@factelec.com.ec'
);

-- Configuraciones iniciales
INSERT INTO configuracion (clave, valor, tipo_dato, descripcion) VALUES
('empresa_ambiente', 'PRUEBAS', 'STRING', 'PRODUCCION o PRUEBAS'),
('iva_porcentaje', '15', 'INTEGER', 'Porcentaje de IVA actual'),
('dias_validez_factura', '7', 'INTEGER', 'Días de validez de la factura');

-- ============================================================================
-- MENSAJE DE CONFIRMACIÓN
-- ============================================================================
SELECT 
    'Base de datos richard_db creada exitosamente' AS mensaje,
    'Tablas: empresa, usuario, cliente, factura, audit_log, configuracion' AS tablas_creadas,
    'Usuario admin: admin / admin123!' AS acceso_inicial;
