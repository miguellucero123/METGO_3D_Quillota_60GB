from typing import Any
from .client import get_supabase_client, SUPABASE_URL

def guardar_registros(estacion_id: str, filas: list[dict[str, Any]], fuente: str = "openmeteo") -> int:
    client = get_supabase_client()
    if not client:
        return 0
    if not filas:
        return 0
    
    n = 0
    for row in filas:
        fecha = str(row.get("fecha") or row.get("actualizado") or "")[:10]
        if not fecha:
            continue
        try:
            data = {
                "estacion_id": estacion_id,
                "fecha": fecha,
                "temperatura_max": row.get("temperatura_max"),
                "temperatura_min": row.get("temperatura_min"),
                "humedad": row.get("humedad"),
                "precipitacion": row.get("precipitacion"),
                "viento": row.get("viento"),
                "presion": row.get("presion"),
                "fuente": fuente,
            }
            client.table("meteo_registros").upsert(data, on_conflict="estacion_id,fecha").execute()
            n += 1
        except Exception as e:
            print(f"Error al guardar registro en Supabase: {e}")
            continue
    return n


def leer_registros(estacion_id: str, dias: int = 30) -> list[dict[str, Any]]:
    client = get_supabase_client()
    if not client:
        return []
    
    try:
        res = (
            client.table("meteo_registros")
            .select("*")
            .eq("estacion_id", estacion_id)
            .order("fecha", desc=True)
            .limit(dias)
            .execute()
        )
        
        out = []
        for row in res.data:
            out.append(
                {
                    "estacion_id": estacion_id,
                    "fecha": row.get("fecha"),
                    "temperatura_max": row.get("temperatura_max"),
                    "temperatura_min": row.get("temperatura_min"),
                    "humedad": row.get("humedad"),
                    "precipitacion": row.get("precipitacion"),
                    "viento": row.get("viento"),
                    "presion": row.get("presion"),
                    "fuente": row.get("fuente") or "supabase_db",
                }
            )
        return list(reversed(out))
    except Exception as e:
        print(f"Error al leer registros en Supabase: {e}")
        return []


def estadisticas_store() -> dict[str, Any]:
    client = get_supabase_client()
    if not client:
        return {"registros": 0, "estaciones": 0, "db": "supabase (inactivo)"}
    try:
        res = client.table("meteo_registros").select("estacion_id", count="exact").limit(1).execute()
        total = res.count if res.count is not None else 0
        return {"registros": total, "estaciones": 0, "db": SUPABASE_URL}
    except Exception:
        return {"registros": 0, "estaciones": 0, "db": SUPABASE_URL}
