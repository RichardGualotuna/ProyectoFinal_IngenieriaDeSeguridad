# Modelo de Base de Datos - Sistema de Facturación Electrónica

## 1. Diagrama Entidad-Relación (ER)

```
┌─────────────────────┐
│      EMPRESA        │
│─────────────────────│
│ PK id               │
│    ruc              │◄───────┐
│    razon_social     │        │
│    nombre_comercial │        │
│    direccion        │        │
│    telefono         │        │
│    email            │        │
│    logo_path        │        │
│    clave_publica    │        │ 1
│    clave_privada_enc│        │
│    establecimiento  │        │
│    punto_emision    │        │
│    ambiente         │        │
│    created_at       │        │
│    updated_at       │        │
└─────────────────────┘        │
                                │
┌─────────────────────┐        │
│      USUARIO        │        │
│─────────────────────│        │
│ PK id               │        │
│    username         │        │
│    email            │        │
│    password_hash    │        │
│    nombres          │        │
│    apellidos        │        │
│    rol              │        │
│    activo           │        │
│    ultimo_login     │        │
│    created_at       │        │
│    updated_at       │        │
└──────────┬──────────┘        │
           │ 1                 │
           │                   │
           │ N                 │
┌──────────▼──────────┐        │
│      FACTURA        │        │
│─────────────────────│        │
│ PK id               │        │
│ FK empresa_id       │────────┘
│ FK cliente_id       │────────┐
│ FK usuario_id       │◄───────┼──┐
│    numero_factura   │        │  │
│    establecimiento  │        │  │
│    punto_emision    │        │  │
│    secuencial       │        │  │
│    fecha_emision    │        │  │
│    subtotal_sin_imp │        │  │
│    subtotal_iva     │        │  │
│    subtotal_iva_0   │        │  │
│    iva              │        │  │
│    propina          │        │  │
│    total            │        │  │
│    forma_pago       │        │  │
│    xml_contenido    │        │  │
│    xml_firmado      │        │  │
│    hash_sha256      │        │  │
│    firma_digital    │        │  │
│    num_autorizacion │        │  │
│    clave_acceso     │        │  │
│    fecha_autorizacion│       │  │
│    qr_code_path     │        │  │
│    estado           │        │  │
│    observaciones    │        │  │
│    ambiente         │        │  │
│    created_at       │        │  │
│    updated_at       │        │  │
└──────────┬──────────┘        │  │
           │ 1                 │  │
           │                   │  │
           │ N                 │  │
┌──────────▼──────────┐        │  │
│  DETALLE_FACTURA    │        │  │
│─────────────────────│        │  │
│ PK id               │        │  │
│ FK factura_id       │◄───────┘  │
│    codigo_principal │           │
│    codigo_auxiliar  │           │
│    descripcion      │           │
│    cantidad         │           │
│    precio_unitario  │           │
│    descuento        │           │
│    precio_total_sin_imp│        │
│    tarifa_iva       │           │
│    valor_iva        │           │
│    total_linea      │           │
│    created_at       │           │
└─────────────────────┘           │
                                  │
┌─────────────────────┐           │
│      CLIENTE        │           │
│─────────────────────│           │
│ PK id               │           │
│    tipo_identificacion│         │
│    identificacion   │           │
│    razon_social     │           │
│    nombres_enc      │ ◄─AES     │
│    apellidos_enc    │ ◄─AES     │
│    direccion_enc    │ ◄─AES     │
│    telefono_enc     │ ◄─AES     │
│    email_enc        │ ◄─AES     │
│    iv              │ (IV para AES)
│    activo           │           │
│    created_at       │           │
│    updated_at       │           │
└──────────┬──────────┘           │
           │ 1                    │
           └──────────────────────┘
           
┌─────────────────────┐
│     AUDIT_LOG       │
│─────────────────────│
│ PK id               │
│ FK usuario_id       │
│    timestamp        │
│    accion           │
│    entidad          │
│    entidad_id       │
│    datos_anteriores │
│    datos_nuevos     │
│    ip_address       │
│    user_agent       │
│    resultado        │
└─────────────────────┘

┌─────────────────────┐
│    CONFIGURACION    │
│─────────────────────│
│ PK id               │
│    clave            │
│    valor            │
│    descripcion      │
│    tipo_dato        │
│    cifrado          │
│    updated_at       │
└─────────────────────┘
```

## 2. Definición de Tablas

### 2.1 Tabla: EMPRESA

**Propósito**: Almacenar información de la empresa emisora de facturas

```sql
CREATE TABLE empresa (
    id SERIAL PRIMARY KEY,
    ruc VARCHAR(13) NOT NULL UNIQUE,
    razon_social VARCHAR(300) NOT NULL,
    nombre_comercial VARCHAR(300),
    direccion TEXT NOT NULL,
    telefono VARCHAR(20),
    email VARCHAR(100) NOT NULL,
    logo_path VARCHAR(255),
    clave_publica TEXT NOT NULL,        -- RSA Public Key (PEM format)
    clave_privada_enc TEXT NOT NULL,    -- RSA Private Key cifrada con AES
    establecimiento VARCHAR(3) DEFAULT '001',
    punto_emision VARCHAR(3) DEFAULT '001',
    ambiente VARCHAR(20) DEFAULT 'PRODUCCION',  -- PRODUCCION | PRUEBAS
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT chk_ruc CHECK (LENGTH(ruc) = 13),
    CONSTRAINT chk_establecimiento CHECK (establecimiento ~ '^[0-9]{3}$'),
    CONSTRAINT chk_punto_emision CHECK (punto_emision ~ '^[0-9]{3}$'),
    CONSTRAINT chk_ambiente CHECK (ambiente IN ('PRODUCCION', 'PRUEBAS'))
);

-- Índices
CREATE INDEX idx_empresa_ruc ON empresa(ruc);

-- Comentarios
COMMENT ON TABLE empresa IS 'Información de la empresa emisora de facturas electrónicas';
COMMENT ON COLUMN empresa.clave_publica IS 'Clave pública RSA para verificación de firmas';
COMMENT ON COLUMN empresa.clave_privada_enc IS 'Clave privada RSA cifrada con AES-256 (no almacenar en texto plano)';
```

### 2.2 Tabla: USUARIO

**Propósito**: Gestión de usuarios del sistema con diferentes roles

```sql
CREATE TABLE usuario (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(60) NOT NULL,     -- Bcrypt hash
    nombres VARCHAR(100) NOT NULL,
    apellidos VARCHAR(100) NOT NULL,
    rol VARCHAR(20) NOT NULL DEFAULT 'FACTURADOR',
    activo BOOLEAN DEFAULT TRUE,
    ultimo_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT chk_rol CHECK (rol IN ('ADMIN', 'FACTURADOR', 'CONTADOR', 'AUDITOR'))
);

-- Índices
CREATE INDEX idx_usuario_username ON usuario(username);
CREATE INDEX idx_usuario_email ON usuario(email);
CREATE INDEX idx_usuario_activo ON usuario(activo);

-- Comentarios
COMMENT ON TABLE usuario IS 'Usuarios del sistema con control de acceso basado en roles';
COMMENT ON COLUMN usuario.password_hash IS 'Hash bcrypt de la contraseña (60 caracteres)';
COMMENT ON COLUMN usuario.rol IS 'ADMIN: control total | FACTURADOR: crear facturas | CONTADOR: reportes | AUDITOR: solo lectura';
```

### 2.3 Tabla: CLIENTE

**Propósito**: Almacenar información de clientes con datos sensibles cifrados

```sql
CREATE TABLE cliente (
    id SERIAL PRIMARY KEY,
    tipo_identificacion VARCHAR(10) NOT NULL,
    identificacion VARCHAR(20) NOT NULL UNIQUE,
    razon_social VARCHAR(300),              -- Para empresas
    nombres_enc BYTEA,                      -- AES encrypted
    apellidos_enc BYTEA,                    -- AES encrypted
    direccion_enc BYTEA,                    -- AES encrypted
    telefono_enc BYTEA,                     -- AES encrypted
    email_enc BYTEA,                        -- AES encrypted
    iv BYTEA NOT NULL,                      -- Initialization Vector para AES-GCM
    tag BYTEA,                              -- Authentication tag de AES-GCM
    activo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT chk_tipo_identificacion CHECK (
        tipo_identificacion IN ('RUC', 'CEDULA', 'PASAPORTE', 'CONSUMIDOR_FINAL')
    )
);

-- Índices
CREATE INDEX idx_cliente_identificacion ON cliente(identificacion);
CREATE INDEX idx_cliente_tipo ON cliente(tipo_identificacion);
CREATE INDEX idx_cliente_activo ON cliente(activo);

-- Comentarios
COMMENT ON TABLE cliente IS 'Clientes con datos personales cifrados con AES-256-GCM';
COMMENT ON COLUMN cliente.nombres_enc IS 'Nombres cifrados con AES-256-GCM';
COMMENT ON COLUMN cliente.iv IS 'Vector de inicialización único por registro';
COMMENT ON COLUMN cliente.tag IS 'Tag de autenticación de AES-GCM para detectar manipulación';
```

### 2.4 Tabla: FACTURA

**Propósito**: Facturas electrónicas con firma digital

```sql
CREATE TABLE factura (
    id SERIAL PRIMARY KEY,
    empresa_id INTEGER NOT NULL,
    cliente_id INTEGER NOT NULL,
    usuario_id INTEGER NOT NULL,
    numero_factura VARCHAR(17) NOT NULL UNIQUE,  -- 001-001-000123456
    establecimiento VARCHAR(3) NOT NULL,
    punto_emision VARCHAR(3) NOT NULL,
    secuencial VARCHAR(9) NOT NULL,
    fecha_emision TIMESTAMP NOT NULL,
    subtotal_sin_imp DECIMAL(12,2) NOT NULL DEFAULT 0.00,
    subtotal_iva DECIMAL(12,2) NOT NULL DEFAULT 0.00,
    subtotal_iva_0 DECIMAL(12,2) NOT NULL DEFAULT 0.00,
    iva DECIMAL(12,2) NOT NULL DEFAULT 0.00,
    propina DECIMAL(12,2) DEFAULT 0.00,
    total DECIMAL(12,2) NOT NULL,
    forma_pago VARCHAR(50) DEFAULT 'SIN UTILIZACION DEL SISTEMA FINANCIERO',
    xml_contenido TEXT,                          -- XML sin firmar
    xml_firmado TEXT,                            -- XML firmado (XAdES-BES)
    hash_sha256 VARCHAR(64) NOT NULL,            -- SHA-256 del XML
    firma_digital TEXT NOT NULL,                 -- Firma RSA en base64
    num_autorizacion VARCHAR(49) NOT NULL UNIQUE,
    clave_acceso VARCHAR(49) NOT NULL UNIQUE,
    fecha_autorizacion TIMESTAMP NOT NULL,
    qr_code_path VARCHAR(255),                   -- Ruta a imagen QR
    estado VARCHAR(20) DEFAULT 'AUTORIZADA',
    observaciones TEXT,
    ambiente VARCHAR(20) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_factura_empresa FOREIGN KEY (empresa_id) 
        REFERENCES empresa(id) ON DELETE RESTRICT,
    CONSTRAINT fk_factura_cliente FOREIGN KEY (cliente_id) 
        REFERENCES cliente(id) ON DELETE RESTRICT,
    CONSTRAINT fk_factura_usuario FOREIGN KEY (usuario_id) 
        REFERENCES usuario(id) ON DELETE RESTRICT,
    
    CONSTRAINT chk_numero_factura CHECK (numero_factura ~ '^[0-9]{3}-[0-9]{3}-[0-9]{9}$'),
    CONSTRAINT chk_secuencial CHECK (secuencial ~ '^[0-9]{9}$'),
    CONSTRAINT chk_total_positivo CHECK (total >= 0),
    CONSTRAINT chk_estado CHECK (estado IN ('AUTORIZADA', 'ANULADA', 'DEVUELTA')),
    CONSTRAINT chk_hash_sha256 CHECK (LENGTH(hash_sha256) = 64),
    CONSTRAINT chk_num_autorizacion CHECK (LENGTH(num_autorizacion) = 49),
    CONSTRAINT chk_clave_acceso CHECK (LENGTH(clave_acceso) = 49)
);

-- Índices
CREATE INDEX idx_factura_numero ON factura(numero_factura);
CREATE INDEX idx_factura_fecha ON factura(fecha_emision);
CREATE INDEX idx_factura_cliente ON factura(cliente_id);
CREATE INDEX idx_factura_usuario ON factura(usuario_id);
CREATE INDEX idx_factura_estado ON factura(estado);
CREATE INDEX idx_factura_num_autorizacion ON factura(num_autorizacion);
CREATE INDEX idx_factura_clave_acceso ON factura(clave_acceso);
CREATE INDEX idx_factura_hash ON factura(hash_sha256);

-- Índice compuesto para búsquedas por rango de fechas
CREATE INDEX idx_factura_fecha_estado ON factura(fecha_emision, estado);

-- Comentarios
COMMENT ON TABLE factura IS 'Facturas electrónicas con firma digital RSA y hash SHA-256';
COMMENT ON COLUMN factura.hash_sha256 IS 'Hash SHA-256 del XML para verificar integridad';
COMMENT ON COLUMN factura.firma_digital IS 'Firma RSA del hash (base64)';
COMMENT ON COLUMN factura.num_autorizacion IS 'Número de autorización SRI (49 dígitos)';
COMMENT ON COLUMN factura.clave_acceso IS 'Clave de acceso única de la factura (49 dígitos)';
```

### 2.5 Tabla: DETALLE_FACTURA

**Propósito**: Detalles de productos/servicios de cada factura

```sql
CREATE TABLE detalle_factura (
    id SERIAL PRIMARY KEY,
    factura_id INTEGER NOT NULL,
    codigo_principal VARCHAR(25),
    codigo_auxiliar VARCHAR(25),
    descripcion VARCHAR(300) NOT NULL,
    cantidad DECIMAL(12,4) NOT NULL,
    precio_unitario DECIMAL(12,4) NOT NULL,
    descuento DECIMAL(12,2) DEFAULT 0.00,
    precio_total_sin_imp DECIMAL(12,2) NOT NULL,
    tarifa_iva INTEGER NOT NULL,             -- 0, 8, 12, 15
    valor_iva DECIMAL(12,2) NOT NULL DEFAULT 0.00,
    total_linea DECIMAL(12,2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_detalle_factura FOREIGN KEY (factura_id) 
        REFERENCES factura(id) ON DELETE CASCADE,
    
    CONSTRAINT chk_cantidad_positiva CHECK (cantidad > 0),
    CONSTRAINT chk_precio_positivo CHECK (precio_unitario >= 0),
    CONSTRAINT chk_descuento_positivo CHECK (descuento >= 0),
    CONSTRAINT chk_tarifa_iva CHECK (tarifa_iva IN (0, 8, 12, 15))
);

-- Índices
CREATE INDEX idx_detalle_factura_id ON detalle_factura(factura_id);

-- Comentarios
COMMENT ON TABLE detalle_factura IS 'Líneas de detalle de cada factura (productos/servicios)';
COMMENT ON COLUMN detalle_factura.tarifa_iva IS 'Porcentaje de IVA: 0, 8, 12 o 15';
```

### 2.6 Tabla: AUDIT_LOG

**Propósito**: Registro inmutable de todas las operaciones del sistema

```sql
CREATE TABLE audit_log (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    accion VARCHAR(50) NOT NULL,             -- LOGIN, LOGOUT, CREATE, UPDATE, DELETE, VIEW
    entidad VARCHAR(50) NOT NULL,            -- FACTURA, CLIENTE, USUARIO, etc.
    entidad_id INTEGER,
    datos_anteriores JSONB,                  -- Estado antes del cambio
    datos_nuevos JSONB,                      -- Estado después del cambio
    ip_address INET NOT NULL,
    user_agent TEXT,
    resultado VARCHAR(20) DEFAULT 'EXITO',   -- EXITO | FALLO
    mensaje_error TEXT,
    
    CONSTRAINT fk_audit_usuario FOREIGN KEY (usuario_id) 
        REFERENCES usuario(id) ON DELETE SET NULL,
    
    CONSTRAINT chk_accion CHECK (
        accion IN ('LOGIN', 'LOGOUT', 'CREATE', 'UPDATE', 'DELETE', 'VIEW', 
                   'EXPORT', 'PRINT', 'VERIFY', 'DECRYPT')
    ),
    CONSTRAINT chk_resultado CHECK (resultado IN ('EXITO', 'FALLO'))
);

-- Índices
CREATE INDEX idx_audit_timestamp ON audit_log(timestamp);
CREATE INDEX idx_audit_usuario ON audit_log(usuario_id);
CREATE INDEX idx_audit_accion ON audit_log(accion);
CREATE INDEX idx_audit_entidad ON audit_log(entidad);
CREATE INDEX idx_audit_resultado ON audit_log(resultado);

-- Índice GIN para búsquedas en JSON
CREATE INDEX idx_audit_datos_gin ON audit_log USING GIN (datos_nuevos);

-- Comentarios
COMMENT ON TABLE audit_log IS 'Registro de auditoría inmutable de todas las operaciones';
COMMENT ON COLUMN audit_log.datos_anteriores IS 'Estado anterior del registro (JSON)';
COMMENT ON COLUMN audit_log.datos_nuevos IS 'Estado nuevo del registro (JSON)';
```

### 2.7 Tabla: CONFIGURACION

**Propósito**: Configuraciones del sistema

```sql
CREATE TABLE configuracion (
    id SERIAL PRIMARY KEY,
    clave VARCHAR(100) NOT NULL UNIQUE,
    valor TEXT NOT NULL,
    descripcion TEXT,
    tipo_dato VARCHAR(20) DEFAULT 'STRING',  -- STRING, INTEGER, BOOLEAN, JSON
    cifrado BOOLEAN DEFAULT FALSE,            -- Si el valor está cifrado con AES
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT chk_tipo_dato CHECK (
        tipo_dato IN ('STRING', 'INTEGER', 'BOOLEAN', 'JSON', 'ENCRYPTED')
    )
);

-- Índices
CREATE INDEX idx_configuracion_clave ON configuracion(clave);

-- Comentarios
COMMENT ON TABLE configuracion IS 'Configuraciones generales del sistema';
COMMENT ON COLUMN configuracion.cifrado IS 'TRUE si el valor está cifrado con AES';

-- Valores iniciales
INSERT INTO configuracion (clave, valor, descripcion, tipo_dato) VALUES
('AES_KEY_VERSION', '1', 'Versión actual de la clave AES', 'INTEGER'),
('IVA_TARIFA_ACTUAL', '15', 'Tarifa de IVA actual (%)', 'INTEGER'),
('MAX_INTENTOS_LOGIN', '5', 'Máximo intentos de login antes de bloqueo', 'INTEGER'),
('TIMEOUT_SESSION', '900', 'Timeout de sesión en segundos (15 min)', 'INTEGER'),
('AMBIENTE_SRI', 'PRUEBAS', 'Ambiente del SRI (PRUEBAS | PRODUCCION)', 'STRING');
```

## 3. Vistas Útiles

### 3.1 Vista: Facturas con Cliente

```sql
CREATE VIEW v_facturas_clientes AS
SELECT 
    f.id,
    f.numero_factura,
    f.fecha_emision,
    f.total,
    f.estado,
    c.identificacion AS cliente_identificacion,
    c.razon_social AS cliente_razon_social,
    u.username AS usuario_emisor,
    e.razon_social AS empresa_emisor
FROM factura f
INNER JOIN cliente c ON f.cliente_id = c.id
INNER JOIN usuario u ON f.usuario_id = u.id
INNER JOIN empresa e ON f.empresa_id = e.id;

COMMENT ON VIEW v_facturas_clientes IS 
'Vista desnormalizada de facturas con información de cliente y usuario';
```

### 3.2 Vista: Resumen de Ventas por Mes

```sql
CREATE VIEW v_ventas_mensuales AS
SELECT 
    DATE_TRUNC('month', fecha_emision) AS mes,
    COUNT(*) AS total_facturas,
    SUM(subtotal_sin_imp) AS subtotal,
    SUM(iva) AS total_iva,
    SUM(total) AS total_ventas,
    AVG(total) AS ticket_promedio
FROM factura
WHERE estado = 'AUTORIZADA'
GROUP BY DATE_TRUNC('month', fecha_emision)
ORDER BY mes DESC;

COMMENT ON VIEW v_ventas_mensuales IS 
'Resumen mensual de ventas para reportes';
```

### 3.3 Vista: Auditoría de Acceso a Datos Cifrados

```sql
CREATE VIEW v_audit_acceso_datos_sensibles AS
SELECT 
    a.id,
    a.timestamp,
    u.username,
    u.rol,
    a.accion,
    a.entidad,
    a.ip_address,
    a.resultado
FROM audit_log a
INNER JOIN usuario u ON a.usuario_id = u.id
WHERE a.accion IN ('DECRYPT', 'VIEW') 
  AND a.entidad = 'CLIENTE'
ORDER BY a.timestamp DESC;

COMMENT ON VIEW v_audit_acceso_datos_sensibles IS 
'Auditoría de accesos a datos cifrados de clientes';
```

## 4. Funciones y Triggers

### 4.1 Trigger: Actualizar updated_at automáticamente

```sql
-- Función genérica
CREATE OR REPLACE FUNCTION actualizar_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Aplicar a tablas
CREATE TRIGGER trg_empresa_updated 
    BEFORE UPDATE ON empresa
    FOR EACH ROW EXECUTE FUNCTION actualizar_updated_at();

CREATE TRIGGER trg_usuario_updated 
    BEFORE UPDATE ON usuario
    FOR EACH ROW EXECUTE FUNCTION actualizar_updated_at();

CREATE TRIGGER trg_cliente_updated 
    BEFORE UPDATE ON cliente
    FOR EACH ROW EXECUTE FUNCTION actualizar_updated_at();

CREATE TRIGGER trg_factura_updated 
    BEFORE UPDATE ON factura
    FOR EACH ROW EXECUTE FUNCTION actualizar_updated_at();
```

### 4.2 Función: Generar Número de Factura

```sql
CREATE OR REPLACE FUNCTION generar_numero_factura(
    p_establecimiento VARCHAR,
    p_punto_emision VARCHAR
)
RETURNS VARCHAR AS $$
DECLARE
    v_secuencial INTEGER;
    v_numero_factura VARCHAR(17);
BEGIN
    -- Obtener último secuencial
    SELECT COALESCE(MAX(CAST(secuencial AS INTEGER)), 0) + 1
    INTO v_secuencial
    FROM factura
    WHERE establecimiento = p_establecimiento
      AND punto_emision = p_punto_emision;
    
    -- Formatear número
    v_numero_factura := p_establecimiento || '-' || 
                        p_punto_emision || '-' || 
                        LPAD(v_secuencial::TEXT, 9, '0');
    
    RETURN v_numero_factura;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION generar_numero_factura IS 
'Genera el siguiente número de factura secuencial';
```

### 4.3 Función: Validar RUC Ecuatoriano

```sql
CREATE OR REPLACE FUNCTION validar_ruc(p_ruc VARCHAR)
RETURNS BOOLEAN AS $$
DECLARE
    v_suma INTEGER := 0;
    v_digito INTEGER;
    v_verificador INTEGER;
    v_coeficientes INTEGER[] := ARRAY[4,3,2,7,6,5,4,3,2,0,0,0,0];
BEGIN
    -- Verificar longitud
    IF LENGTH(p_ruc) != 13 THEN
        RETURN FALSE;
    END IF;
    
    -- Verificar que sea numérico
    IF p_ruc !~ '^[0-9]+$' THEN
        RETURN FALSE;
    END IF;
    
    -- Algoritmo de módulo 11
    FOR i IN 1..10 LOOP
        v_digito := SUBSTRING(p_ruc FROM i FOR 1)::INTEGER;
        v_suma := v_suma + (v_digito * v_coeficientes[i]);
    END LOOP;
    
    v_verificador := 11 - (v_suma % 11);
    IF v_verificador = 11 THEN
        v_verificador := 0;
    END IF;
    
    -- Comparar con dígito verificador
    RETURN v_verificador = SUBSTRING(p_ruc FROM 3 FOR 1)::INTEGER;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION validar_ruc IS 
'Valida un RUC ecuatoriano usando algoritmo de módulo 11';
```

## 5. Scripts de Inicialización

### 5.1 Crear Empresa de Ejemplo

```sql
-- Script de inicialización con datos de ejemplo
INSERT INTO empresa (
    ruc, 
    razon_social, 
    nombre_comercial, 
    direccion, 
    telefono, 
    email,
    clave_publica,
    clave_privada_enc,
    establecimiento,
    punto_emision,
    ambiente
) VALUES (
    '1234567890001',
    'EMPRESA DE PRUEBAS S.A.',
    'EmpresaTest',
    'Av. Principal 123 y Secundaria',
    '023456789',
    'contacto@empresatest.com',
    '-----BEGIN PUBLIC KEY-----\n[CLAVE_PUBLICA_RSA]\n-----END PUBLIC KEY-----',
    '[CLAVE_PRIVADA_CIFRADA_AES]',
    '001',
    '001',
    'PRUEBAS'
);
```

### 5.2 Crear Usuario Administrador

```sql
-- Usuario admin por defecto (password: Admin123!)
INSERT INTO usuario (
    username,
    email,
    password_hash,
    nombres,
    apellidos,
    rol,
    activo
) VALUES (
    'admin',
    'admin@facturasegura.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqVkP0fELy',
    'Administrador',
    'Sistema',
    'ADMIN',
    TRUE
);
```

## 6. Índices de Rendimiento Adicionales

```sql
-- Índice para búsqueda de facturas por hash (verificación)
CREATE INDEX idx_factura_hash_lookup ON factura(hash_sha256) 
    WHERE estado = 'AUTORIZADA';

-- Índice parcial para facturas activas
CREATE INDEX idx_factura_activas ON factura(fecha_emision, total) 
    WHERE estado = 'AUTORIZADA';

-- Índice para reportes por cliente
CREATE INDEX idx_factura_cliente_fecha ON factura(cliente_id, fecha_emision DESC);

-- Índice compuesto para búsquedas de auditoría
CREATE INDEX idx_audit_usuario_timestamp ON audit_log(usuario_id, timestamp DESC);
```

## 7. Políticas de Retención

```sql
-- Política de particionado por año para audit_log
CREATE TABLE audit_log_2026 PARTITION OF audit_log
    FOR VALUES FROM ('2026-01-01') TO ('2027-01-01');

CREATE TABLE audit_log_2027 PARTITION OF audit_log
    FOR VALUES FROM ('2027-01-01') TO ('2028-01-01');

-- Job para archivar logs antiguos (más de 7 años)
-- Se ejecutaría mediante cron job externo
```

## 8. Seguridad de Base de Datos

### 8.1 Roles y Permisos

```sql
-- Crear roles
CREATE ROLE facturasegura_app LOGIN PASSWORD 'changeme';
CREATE ROLE facturasegura_readonly;

-- Permisos para aplicación
GRANT CONNECT ON DATABASE facturasegura TO facturasegura_app;
GRANT USAGE ON SCHEMA public TO facturasegura_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO facturasegura_app;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO facturasegura_app;

-- Permisos solo lectura para reportes
GRANT CONNECT ON DATABASE facturasegura TO facturasegura_readonly;
GRANT USAGE ON SCHEMA public TO facturasegura_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO facturasegura_readonly;
GRANT SELECT ON ALL VIEWS IN SCHEMA public TO facturasegura_readonly;
```

### 8.2 Row Level Security (RLS)

```sql
-- Habilitar RLS en tabla de facturas
ALTER TABLE factura ENABLE ROW LEVEL SECURITY;

-- Política: Usuarios solo ven sus propias facturas
CREATE POLICY factura_usuario_policy ON factura
    FOR SELECT
    USING (usuario_id = current_setting('app.current_user_id')::INTEGER);

-- Política: Admin ve todo
CREATE POLICY factura_admin_policy ON factura
    FOR ALL
    USING (current_setting('app.user_role') = 'ADMIN');
```

## 9. Backup y Recuperación

```sql
-- Script de backup
-- pg_dump -U postgres -d facturasegura -F c -b -v -f backup_$(date +%Y%m%d).backup

-- Script de restore
-- pg_restore -U postgres -d facturasegura -v backup_20260112.backup
```

## 10. Resumen del Modelo

### Estadísticas del Modelo

| Métrica | Valor |
|---------|-------|
| **Total de tablas** | 7 |
| **Total de vistas** | 3 |
| **Total de índices** | ~25 |
| **Total de funciones** | 4 |
| **Total de triggers** | 4 |
| **Campos cifrados** | 5 (cliente) |
| **Campos con hash** | 1 (usuario) + facturas |
| **Foreign keys** | 6 |

### Consideraciones de Almacenamiento

- **Factura completa**: ~3-5 KB (sin XML)
- **Factura con XML**: ~10-15 KB
- **Cliente**: ~1 KB (cifrado)
- **Audit log entry**: ~500 bytes
- **Estimado 50,000 facturas/año**: ~750 MB/año

## Próximos Pasos

Con el modelo de datos definido, procederemos a especificar la API REST en el siguiente documento.
