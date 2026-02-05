# Semana 2 - Diseño del Sistema de Facturación Electrónica

## Descripción General

En esta semana se define la arquitectura técnica completa del sistema, incluyendo el diseño de la base de datos, especificación de la API REST, y la selección de bibliotecas criptográficas.

## Contenido de la Semana

1. **Arquitectura del Sistema**: Diseño de componentes y patrones arquitectónicos
2. **Modelo de Base de Datos**: Esquema completo con tablas y relaciones
3. **Especificación API REST**: Endpoints, métodos y contratos de datos
4. **Bibliotecas Criptográficas**: Selección y configuración de herramientas

## Objetivos de la Semana

-  Definir arquitectura escalable y segura
-  Diseñar modelo de datos normalizado
-  Especificar API RESTful completa
-  Seleccionar stack tecnológico óptimo
-  Documentar decisiones técnicas

## Decisiones Arquitectónicas Clave

### Stack Tecnológico Final

**Backend**:
- Python 3.11+
- Flask 3.0 (Web framework)
- SQLAlchemy 2.0 (ORM)
- PostgreSQL 15 (Base de datos)

**Frontend**:
- React 18
- Vite (Build tool)
- TailwindCSS (Estilos)
- Axios (HTTP client)

**Seguridad**:
- cryptography 41.0+ (RSA, AES)
- bcrypt 4.1+ (Passwords)
- PyJWT 2.8+ (Tokens)
- qrcode 7.4+ (QR codes)

## Principios de Diseño

1. 🔐 **Seguridad por diseño**: Cifrado y validación en todas las capas
2. 📦 **Modularidad**: Componentes independientes y reutilizables
3. 🚀 **Escalabilidad**: Preparado para crecimiento
4. 🧪 **Testeable**: Arquitectura que facilita pruebas
5. 📝 **Documentado**: Código y APIs bien documentados

## Siguientes Pasos

Una vez completado el diseño, procederemos a la implementación del backend en la Semana 3.
