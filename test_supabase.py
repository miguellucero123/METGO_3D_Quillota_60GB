import os
from dotenv import load_dotenv
import sys
import importlib

sys.path.append(os.path.join(os.path.dirname(__file__), "backend"))
client_module = importlib.import_module("08_Gestion_Datos.supabase_db.client")
repo_module = importlib.import_module("08_Gestion_Datos.supabase_db.meteo_repository")

# Cargar variables de entorno del archivo .env
load_dotenv()

print("Iniciando prueba de conexión a Supabase...")

client = client_module.get_supabase_client()
if client:
    print("✅ Cliente Supabase creado exitosamente.")
    print(f"URL conectada: {os.getenv('SUPABASE_URL')}")
    
    # Intentar obtener estadísticas de la tabla
    print("\nVerificando tabla 'meteo_registros'...")
    try:
        stats = repo_module.estadisticas_store()
        print(f"✅ Conexión exitosa a la tabla.")
        print(f"Registros encontrados: {stats.get('registros', 0)}")
        print("¡Todo funciona correctamente!")
    except Exception as e:
        print(f"❌ Error al consultar la tabla: {e}")
        print("¿Asegúrate de haber ejecutado el CREATE TABLE en el SQL Editor de Supabase?")
else:
    print("❌ Error: No se pudo crear el cliente.")
    print("Verifica que las variables SUPABASE_URL y SUPABASE_KEY estén en tu archivo .env y que hayas hecho 'pip install supabase'.")
