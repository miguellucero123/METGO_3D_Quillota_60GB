import os
import sys
import importlib
from pathlib import Path

from dotenv import load_dotenv

root = Path(r"D:\METGO_3D_Quillota_60GB")
sys.path.insert(0, str(root))
load_dotenv(root / ".env")

print("URL set:", bool(os.getenv("SUPABASE_URL")), "| KEY set:", bool(os.getenv("SUPABASE_KEY")))

client_mod = importlib.import_module("backend.08_Gestion_Datos.supabase_db.client")
c = client_mod.get_supabase_client()
print("cliente:", bool(c))

if c:
    for tabla in ("meteo_registros", "meteo_pronostico", "meteo_series"):
        try:
            r = c.table(tabla).select("*", count="exact").limit(2).execute()
            print(f"{tabla} -> count: {r.count} | muestra: {len(r.data)}")
        except Exception as e:
            print(f"{tabla} -> ERROR: {e}")
