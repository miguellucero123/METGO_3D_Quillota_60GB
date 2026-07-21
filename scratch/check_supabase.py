import sys
from pathlib import Path
import sqlite3
import os
from dotenv import load_dotenv

root_path = Path(r"d:\METGO_3D_Quillota_60GB")
sys.path.append(str(root_path))
load_dotenv(root_path / ".env")

print("SUPABASE_URL:", os.getenv("SUPABASE_URL"))
print("SUPABASE_KEY:", "SET" if os.getenv("SUPABASE_KEY") else "NOT SET")

# Check local sqlite
try:
    db_path = root_path / "backend" / "08_Gestion_Datos" / "datos_runtime" / "meteo_historico.db"
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT fuente, COUNT(*) FROM registros GROUP BY fuente")
    rows = cur.fetchall()
    print("\nLocal DB Registros por fuente:")
    for r in rows:
        print(f" - {r[0]}: {r[1]}")
    conn.close()
except Exception as e:
    print("Error local DB:", e)

# Check supabase directly
try:
    import importlib
    _repo = importlib.import_module("backend.08_Gestion_Datos.supabase_db.meteo_repository")
    leer_registros, estadisticas_store = _repo.leer_registros, _repo.estadisticas_store
    print("\nSupabase Stats:")
    print(estadisticas_store())
except Exception as e:
    print("Error Supabase:", e)
