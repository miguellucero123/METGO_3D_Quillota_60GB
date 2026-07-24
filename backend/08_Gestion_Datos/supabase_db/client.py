import os
from dotenv import load_dotenv

load_dotenv()


def _resolve_supabase_creds() -> tuple[str | None, str | None]:
    url = (
        os.getenv("SUPABASE_URL")
        or os.getenv("METGO_SUPABASE_URL")
        or os.getenv("VITE_SUPABASE_URL")
        or ""
    ).strip() or None
    key = (
        os.getenv("SUPABASE_KEY")
        or os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        or os.getenv("METGO_SUPABASE_KEY")
        or os.getenv("SUPABASE_ANON_KEY")
        or ""
    ).strip() or None
    return url, key


SUPABASE_URL, SUPABASE_KEY = _resolve_supabase_creds()

_supabase_client = None


def get_supabase_client():
    """Retorna la instancia singleton del cliente de Supabase."""
    global _supabase_client, SUPABASE_URL, SUPABASE_KEY
    if _supabase_client is None:
        SUPABASE_URL, SUPABASE_KEY = _resolve_supabase_creds()
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
    url, key = _resolve_supabase_creds()
    return bool(url and key)
