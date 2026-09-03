import os
from dotenv import load_dotenv

load_dotenv()


def _env_is_production() -> bool:
    env = (os.getenv("METGO_ENV") or "").strip().lower()
    if env in ("production", "prod"):
        return True
    return (os.getenv("RENDER") or "").strip().lower() in ("true", "1", "yes")


def _looks_like_anon_key(key: str) -> bool:
    """Heurística: JWT role=anon o prefijo publishable (no service)."""
    k = (key or "").strip()
    if not k:
        return False
    low = k.lower()
    if low.startswith("sb_publishable_"):
        return True
    # JWT legacy: eyJ... con "role":"anon" en payload (sin verificar firma)
    if k.startswith("eyJ"):
        try:
            import base64
            import json

            parts = k.split(".")
            if len(parts) < 2:
                return False
            pad = "=" * (-len(parts[1]) % 4)
            payload = json.loads(base64.urlsafe_b64decode(parts[1] + pad))
            return str(payload.get("role") or "").lower() == "anon"
        except Exception:
            return False
    return False


def _resolve_supabase_creds() -> tuple[str | None, str | None]:
    url = (
        os.getenv("SUPABASE_URL")
        or os.getenv("METGO_SUPABASE_URL")
        or os.getenv("VITE_SUPABASE_URL")
        or ""
    ).strip() or None
    # En production no usar ANON como fallback (R1 Ley 21.719 / seguridad)
    if _env_is_production():
        key = (
            os.getenv("SUPABASE_KEY")
            or os.getenv("SUPABASE_SERVICE_ROLE_KEY")
            or os.getenv("METGO_SUPABASE_KEY")
            or ""
        ).strip() or None
    else:
        key = (
            os.getenv("SUPABASE_KEY")
            or os.getenv("SUPABASE_SERVICE_ROLE_KEY")
            or os.getenv("METGO_SUPABASE_KEY")
            or os.getenv("SUPABASE_ANON_KEY")
            or ""
        ).strip() or None
    if key and _env_is_production() and _looks_like_anon_key(key):
        raise RuntimeError(
            "METGO: SUPABASE_KEY parece anon/publishable en production. "
            "Use service_role / sb_secret_ (nunca anon en Render)."
        )
    return url, key


SUPABASE_URL, SUPABASE_KEY = None, None
try:
    SUPABASE_URL, SUPABASE_KEY = _resolve_supabase_creds()
except RuntimeError:
    SUPABASE_URL, SUPABASE_KEY = None, None

_supabase_client = None


def get_supabase_client():
    """Retorna la instancia singleton del cliente de Supabase."""
    global _supabase_client, SUPABASE_URL, SUPABASE_KEY
    if _supabase_client is None:
        try:
            SUPABASE_URL, SUPABASE_KEY = _resolve_supabase_creds()
        except RuntimeError as exc:
            print(str(exc))
            _supabase_client = False
            return _supabase_client
        if SUPABASE_URL and SUPABASE_KEY:
            try:
                from supabase import create_client

                _supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
            except ImportError:
                print("Librería supabase no está instalada.")
                _supabase_client = False
        else:
            print(
                "Supabase inactivo: defina SUPABASE_URL y SUPABASE_KEY "
                "(o SUPABASE_SERVICE_ROLE_KEY) en el entorno."
            )
            _supabase_client = False
    return _supabase_client


def supabase_configurado() -> bool:
    try:
        url, key = _resolve_supabase_creds()
    except RuntimeError:
        return False
    return bool(url and key)
