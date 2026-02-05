"""
Script de Inicialización de Base de Datos
Sistema de Facturación Electrónica - Richard
Ejecuta el script SQL para crear todas las tablas
"""

import sys
import subprocess
import os
from pathlib import Path

# Configuración de conexión
DB_CONFIG = {
    'host': 'localhost',
    'port': '5432',
    'user': 'postgres',
    'password': 'admin',  # Tu contraseña de pgAdmin
    'database_admin': 'postgres',  # BD para crear richard_db
    'database_target': 'richard_db'  # BD objetivo
}

def imprimir_banner():
    """Imprime banner de inicio"""
    print("=" * 60)
    print("  CREACIÓN DE BASE DE DATOS - RICHARD_DB")
    print("  Sistema de Facturación Electrónica con Firma Digital")
    print("=" * 60)
    print()

def verificar_psql():
    """Verifica si psql está disponible"""
    try:
        result = subprocess.run(['psql', '--version'], 
                              capture_output=True, 
                              text=True)
        if result.returncode == 0:
            print(f"✓ PostgreSQL encontrado: {result.stdout.strip()}")
            return True
        return False
    except FileNotFoundError:
        print("✗ ERROR: psql no encontrado en el PATH")
        print()
        print("Por favor, agregue PostgreSQL al PATH del sistema:")
        print("  Ejemplo: C:\\Program Files\\PostgreSQL\\15\\bin")
        return False

def verificar_conexion():
    """Verifica la conexión a PostgreSQL"""
    print()
    print("Verificando conexión a PostgreSQL...")
    print(f"  Host: {DB_CONFIG['host']}")
    print(f"  Puerto: {DB_CONFIG['port']}")
    print(f"  Usuario: {DB_CONFIG['user']}")
    
    try:
        # Configurar variables de entorno para psql
        env = os.environ.copy()
        env['PGPASSWORD'] = DB_CONFIG['password']
        
        result = subprocess.run([
            'psql',
            '-U', DB_CONFIG['user'],
            '-h', DB_CONFIG['host'],
            '-p', DB_CONFIG['port'],
            '-d', DB_CONFIG['database_admin'],
            '-c', 'SELECT version();'
        ], capture_output=True, text=True, env=env)
        
        if result.returncode == 0:
            print("✓ Conexión exitosa a PostgreSQL")
            return True, env
        else:
            print("✗ ERROR: No se pudo conectar a PostgreSQL")
            print(f"  Detalles: {result.stderr}")
            return False, None
            
    except Exception as e:
        print(f"✗ ERROR: {str(e)}")
        return False, None

def verificar_base_datos_existe(env):
    """Verifica si la base de datos richard_db ya existe"""
    try:
        result = subprocess.run([
            'psql',
            '-U', DB_CONFIG['user'],
            '-h', DB_CONFIG['host'],
            '-p', DB_CONFIG['port'],
            '-d', DB_CONFIG['database_admin'],
            '-tAc', "SELECT 1 FROM pg_database WHERE datname='richard_db'"
        ], capture_output=True, text=True, env=env)
        
        return '1' in result.stdout
    except Exception:
        return False

def eliminar_base_datos(env):
    """Elimina la base de datos si existe"""
    print("Eliminando base de datos existente...")
    
    try:
        # Terminar conexiones activas
        subprocess.run([
            'psql',
            '-U', DB_CONFIG['user'],
            '-h', DB_CONFIG['host'],
            '-p', DB_CONFIG['port'],
            '-d', DB_CONFIG['database_admin'],
            '-c', f"""
                SELECT pg_terminate_backend(pg_stat_activity.pid)
                FROM pg_stat_activity
                WHERE pg_stat_activity.datname = '{DB_CONFIG['database_target']}'
                AND pid <> pg_backend_pid();
            """
        ], capture_output=True, env=env)
        
        # Eliminar base de datos
        result = subprocess.run([
            'psql',
            '-U', DB_CONFIG['user'],
            '-h', DB_CONFIG['host'],
            '-p', DB_CONFIG['port'],
            '-d', DB_CONFIG['database_admin'],
            '-c', f"DROP DATABASE IF EXISTS {DB_CONFIG['database_target']};"
        ], capture_output=True, text=True, env=env)
        
        if result.returncode == 0:
            print("✓ Base de datos eliminada")
            return True
        else:
            print(f"✗ Error al eliminar: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False

def crear_base_datos(env):
    """Crea la base de datos richard_db"""
    print()
    print("Creando base de datos richard_db...")
    
    try:
        result = subprocess.run([
            'psql',
            '-U', DB_CONFIG['user'],
            '-h', DB_CONFIG['host'],
            '-p', DB_CONFIG['port'],
            '-d', DB_CONFIG['database_admin'],
            '-c', f"""
                CREATE DATABASE {DB_CONFIG['database_target']} 
                WITH ENCODING='UTF8' 
                OWNER={DB_CONFIG['user']};
            """
        ], capture_output=True, text=True, env=env)
        
        if result.returncode == 0:
            print("✓ Base de datos creada exitosamente")
            return True
        else:
            print(f"✗ Error al crear base de datos: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False

def ejecutar_script_sql(env):
    """Ejecuta el script SQL para crear tablas"""
    print()
    print("Ejecutando script de creación de tablas...")
    
    # Buscar el archivo SQL
    script_path = Path(__file__).parent / 'database_schema.sql'
    
    if not script_path.exists():
        print(f"✗ ERROR: No se encontró el archivo {script_path}")
        return False
    
    print(f"  Script: {script_path}")
    print()
    
    try:
        result = subprocess.run([
            'psql',
            '-U', DB_CONFIG['user'],
            '-h', DB_CONFIG['host'],
            '-p', DB_CONFIG['port'],
            '-d', DB_CONFIG['database_target'],
            '-f', str(script_path)
        ], capture_output=True, text=True, env=env)
        
        # Mostrar salida del script
        if result.stdout:
            print(result.stdout)
        
        if result.returncode == 0:
            print("✓ Script ejecutado exitosamente")
            return True
        else:
            print("✗ Error al ejecutar script:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False

def mostrar_resumen():
    """Muestra resumen final"""
    print()
    print("=" * 60)
    print("  CREACIÓN COMPLETADA EXITOSAMENTE")
    print("=" * 60)
    print()
    print(f"Base de datos: {DB_CONFIG['database_target']}")
    print("Tablas creadas: 7")
    print("  • empresa")
    print("  • usuario")
    print("  • cliente")
    print("  • factura")
    print("  • detalle_factura")
    print("  • audit_log")
    print("  • configuracion")
    print()
    print("Vistas creadas: 3")
    print("Funciones creadas: 3")
    print("Triggers creados: 5")
    print()
    print("CREDENCIALES DE ACCESO:")
    print("  Usuario: admin")
    print("  Password: Admin123!")
    print("  Email: admin@facturasegura.com")
    print()
    print("PRÓXIMOS PASOS:")
    print("  1. Generar claves RSA desde la aplicación Python")
    print("  2. Configurar variable de entorno AES_MASTER_KEY")
    print("  3. Cambiar contraseña del usuario admin en producción")
    print()
    print("=" * 60)

def main():
    """Función principal"""
    imprimir_banner()
    
    # 1. Verificar psql
    if not verificar_psql():
        input("\nPresione Enter para salir...")
        return 1
    
    # 2. Verificar conexión
    conexion_ok, env = verificar_conexion()
    if not conexion_ok:
        input("\nPresione Enter para salir...")
        return 1
    
    # 3. Verificar si la BD ya existe
    print()
    if verificar_base_datos_existe(env):
        print(f"⚠ ADVERTENCIA: La base de datos '{DB_CONFIG['database_target']}' ya existe.")
        respuesta = input("¿Desea eliminarla y recrearla? (S/N): ").strip().upper()
        
        if respuesta == 'S':
            if not eliminar_base_datos(env):
                input("\nPresione Enter para salir...")
                return 1
        else:
            print("Operación cancelada por el usuario.")
            input("\nPresione Enter para salir...")
            return 0
    
    # 4. Crear base de datos
    if not crear_base_datos(env):
        input("\nPresione Enter para salir...")
        return 1
    
    # 5. Ejecutar script SQL
    if not ejecutar_script_sql(env):
        input("\nPresione Enter para salir...")
        return 1
    
    # 6. Mostrar resumen
    mostrar_resumen()
    
    input("\nPresione Enter para salir...")
    return 0

if __name__ == '__main__':
    sys.exit(main())
