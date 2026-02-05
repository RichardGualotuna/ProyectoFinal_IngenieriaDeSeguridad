"""
Configuración de la aplicación Flask
Sistema de Facturación Electrónica - Richard
"""
import os
from datetime import timedelta
from decouple import config


class Config:
    """Configuración base"""
    # Seguridad
    SECRET_KEY = config('SECRET_KEY', default='dev-secret-key-change-in-production-12345')
    
    # Base de datos PostgreSQL
    POSTGRES_USER = config('POSTGRES_USER', default='postgres')
    POSTGRES_PASSWORD = config('POSTGRES_PASSWORD', default='admin')
    POSTGRES_HOST = config('POSTGRES_HOST', default='localhost')
    POSTGRES_PORT = config('POSTGRES_PORT', default='5432')
    POSTGRES_DB = config('POSTGRES_DB', default='richard_db')
    
    SQLALCHEMY_DATABASE_URI = (
        f'postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@'
        f'{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    
    # JWT
    JWT_SECRET_KEY = config('JWT_SECRET_KEY', default=SECRET_KEY)
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=8)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    JWT_TOKEN_LOCATION = ['headers']
    JWT_HEADER_NAME = 'Authorization'
    JWT_HEADER_TYPE = 'Bearer'
    
    # CORS
    CORS_ORIGINS = config('CORS_ORIGINS', default='http://localhost:5173,http://localhost:3000', cast=lambda v: v.split(','))
    
    # Criptografía - IMPORTANTE: Configurar en producción
    AES_MASTER_KEY = config('AES_MASTER_KEY', default=None)
    
    # Archivos
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    
    # SRI Ecuador
    AMBIENTE_SRI = config('AMBIENTE_SRI', default='PRUEBAS')  # PRUEBAS o PRODUCCION


class DevelopmentConfig(Config):
    """Configuración de desarrollo"""
    DEBUG = True
    SQLALCHEMY_ECHO = True


class ProductionConfig(Config):
    """Configuración de producción"""
    DEBUG = False
    SQLALCHEMY_ECHO = False
    

class TestingConfig(Config):
    """Configuración para pruebas"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


def get_config():
    """Obtener configuración según el entorno"""
    env = config('FLASK_ENV', default='development')
    
    configs = {
        'development': DevelopmentConfig,
        'production': ProductionConfig,
        'testing': TestingConfig
    }
    
    return configs.get(env, DevelopmentConfig)
