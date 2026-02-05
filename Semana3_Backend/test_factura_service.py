from app import create_app

app = create_app()

with app.app_context():
    print("🔍 Probando FacturaService...")
    
    from services.factura_service import FacturaService
    from models.factura import Factura
    
    try:
        fs = FacturaService()
        print("✅ FacturaService inicializado correctamente")
        
        # Buscar una factura existente
        factura = Factura.query.first()
        if factura:
            print(f"✅ Factura encontrada: {factura.numero_factura}")
            print(f"   Hash: {factura.hash_sha256}")
            
            # Probar verificación
            print("🔍 Probando verificación de integridad...")
            resultado = fs.verificar_integridad(factura.hash_sha256)
            print(f"   Resultado: {resultado}")
        else:
            print("❌ No hay facturas en la base de datos")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
