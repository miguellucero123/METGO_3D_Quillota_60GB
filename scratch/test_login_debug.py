import sys
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import metgo_paths
metgo_paths.setup_paths("01_meteo", "05_api_rest")
_apis = metgo_paths.MODULE_PATHS["05_api_rest"]
if str(_apis) not in sys.path:
    sys.path.insert(0, str(_apis))

from api_rest.app import create_app
import metgo_auth

print("METGO_PASSWORD_ADMIN in os.environ:", os.environ.get("METGO_PASSWORD_ADMIN"))
print("metgo_auth.obtener_password('admin'):", metgo_auth.obtener_password("admin"))
print("metgo_auth.verificar_credenciales('admin', 'admin123'):", metgo_auth.verificar_credenciales('admin', 'admin123'))

app = create_app()
with app.test_client() as client:
    resp = client.post("/api/auth/login", json={"username": "admin", "password": "admin123"})
    print("Response status:", resp.status_code)
    print("Response body:", resp.get_json())
