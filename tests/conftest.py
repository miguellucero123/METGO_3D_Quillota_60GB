import pytest
import sys
import os
from pathlib import Path
from types import SimpleNamespace

# Garantiza import de api_rest aunque pytest <7 ignore pythonpath de pytest.ini
_ROOT = Path(__file__).resolve().parents[1]
_APIS = _ROOT / "backend" / "05_APIs_Externas"
for _p in (_ROOT, _APIS):
    _s = str(_p)
    if _s not in sys.path:
        sys.path.insert(0, _s)


@pytest.fixture(autouse=True)
def mock_env_passwords(monkeypatch):
    """Fuerza contraseñas por defecto para los tests independientemente del .env o CI."""
    monkeypatch.setenv("METGO_PASSWORD_ADMIN", "admin123")
    monkeypatch.setenv("METGO_PASSWORD_USER", "user123")
    monkeypatch.setenv("METGO_PASSWORD_LECTOR", "lec123")
    monkeypatch.setenv("METGO_PASSWORD_OPERADOR", "op123")
    monkeypatch.setenv("METGO_PASSWORD_AGRONOMO", "agro123")
    monkeypatch.setenv("METGO_PASSWORD_METGO", "metgo2025")
    # Seguridad: no ensuciar la suite con rate-limit ni gate KYC de pago
    monkeypatch.setenv("METGO_RATE_LIMIT_ENABLED", "0")
    monkeypatch.setenv("METGO_KYC_GATE_PAID", "0")
    try:
        from api_rest import security_hardening as sec

        sec.reset_rate_limits()
    except Exception:
        pass

class MockTable:
    def __init__(self, name, db):
        self.name = name
        self.db = db
        if name not in self.db:
            self.db[name] = []
        self._results = self.db[name]
        self._is_delete = False

    def select(self, *args):
        self._results = list(self.db[self.name])
        return self
        
    def eq(self, k, v):
        self._results = [x for x in self._results if x.get(k) == v]
        return self
        
    def gte(self, k, v):
        self._results = [x for x in self._results if str(x.get(k, "")) >= str(v)]
        return self
        
    def lte(self, k, v):
        self._results = [x for x in self._results if str(x.get(k, "")) <= str(v)]
        return self
        
    def order(self, k, desc=False, **kwargs):
        # Para evitar problemas con tipos mixtos, convertimos a string.
        self._results.sort(key=lambda x: str(x.get(k, "")), reverse=desc)
        return self
        
    def limit(self, n):
        self._results = self._results[:n]
        return self

    def range(self, start, end):
        """PostgREST-style inclusive range (offset..end)."""
        start = max(0, int(start))
        end = max(start, int(end))
        self._results = self._results[start : end + 1]
        return self

    def delete(self):
        self._is_delete = True
        return self
        
    def in_(self, k, values):
        if getattr(self, "_is_delete", False):
            self.db[self.name] = [x for x in self.db[self.name] if x.get(k) not in values]
        return self
        
    def execute(self):
        return SimpleNamespace(data=self._results)
        
    def insert(self, data):
        if isinstance(data, list):
            self.db[self.name].extend(data)
        else:
            self.db[self.name].append(data)
        return self
        
    def upsert(self, data, on_conflict=None, **kwargs):
        keys = on_conflict.split(",") if on_conflict else ["id"]
        rows = data if isinstance(data, list) else [data]
        for r in rows:
            match_idx = -1
            for i, x in enumerate(self.db[self.name]):
                if all(x.get(k) == r.get(k) for k in keys):
                    match_idx = i
                    break
            if match_idx >= 0:
                self.db[self.name][match_idx].update(r)
            else:
                self.db[self.name].append(r)
        return self


class MockSupabaseClient:
    def __init__(self):
        self.db = {}
    
    def table(self, name):
        return MockTable(name, self.db)


@pytest.fixture(autouse=True)
def mock_supabase(monkeypatch):
    """Mocks Supabase globally for tests so they don't hit the real DB and don't fail if creds missing."""
    client = MockSupabaseClient()
    
    # Pre-cargar datos si alguna prueba lo asume (seed de iot)
    client.db["datos_iot"] = [
        {"sensor_id": "sensor_test_1", "estacion_id": "quillota", "tipo": "temperatura", "valor": 20.0, "timestamp": "2026-01-01T00:00:00Z"},
        {"sensor_id": "sensor_test_2", "estacion_id": "quillota", "tipo": "humedad", "valor": 50.0, "timestamp": "2026-01-01T00:00:00Z"}
    ]
    
    # Helper to mock safely
    def _mock_safely(module_path):
        try:
            monkeypatch.setattr(module_path, lambda: client)
        except (ImportError, AttributeError):
            pass

    _mock_safely("api_rest.integracion.supabase_store.get_supabase_client")
    _mock_safely("api_rest.iot_services.get_supabase_client")
    _mock_safely("api_rest.ml_registry_core.get_supabase_client")
    _mock_safely("backend.08_Gestion_Datos.supabase_db.client.get_supabase_client")
    
    return client
