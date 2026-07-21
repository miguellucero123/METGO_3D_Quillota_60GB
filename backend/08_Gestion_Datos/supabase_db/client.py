import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

_supabase_client = None

def get_supabase_client():
    """Retorna la instancia singleton del cliente de Supabase."""
    global _supabase_client
    if _supabase_client is None:
        if SUPABASE_URL and SUPABASE_KEY:
            try:
                from supabase import create_client
                _supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
            except ImportError:
                print("Librería supabase no está instalada.")
                _supabase_client = False
        else:
            _supabase_client = False
    return _supabase_client
