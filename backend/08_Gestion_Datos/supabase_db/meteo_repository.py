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
                "temperatura_promedio": row.get("temperatura_promedio"),
                "humedad": row.get("humedad"),
                "precipitacion": row.get("precipitacion"),
                "viento": row.get("viento"),
                "presion": row.get("presion"),
                "cobertura_nubosa": row.get("cobertura_nubosa"),
                "visibilidad": row.get("visibilidad"),
                "radiacion": row.get("radiacion_solar_sum"),
                "evapotranspiracion": row.get("evapotranspiracion"),
                "helada": row.get("helada"),
                "niebla": row.get("niebla"),
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
                    "temperatura_promedio": row.get("temperatura_promedio"),
                    "humedad": row.get("humedad"),
                    "precipitacion": row.get("precipitacion"),
                    "viento": row.get("viento"),
                    "presion": row.get("presion"),
                    "cobertura_nubosa": row.get("cobertura_nubosa"),
                    "visibilidad": row.get("visibilidad"),
                    "radiacion": row.get("radiacion"),
                    "evapotranspiracion": row.get("evapotranspiracion"),
                    "helada": row.get("helada"),
                    "niebla": row.get("niebla"),
                    "fuente": row.get("fuente") or "supabase_db",
                }
            )
        return list(reversed(out))
    except Exception as e:
        print(f"Error al leer registros en Supabase: {e}")
        return []


def guardar_pronostico(estacion_id: str, filas: list[dict[str, Any]], fuente: str = "openmeteo_pronostico") -> int:
    """Upsert del pronóstico diario en la tabla meteo_pronostico (1 fila por estación+fecha)."""
    client = get_supabase_client()
    if not client or not filas:
        return 0

    n = 0
    for row in filas:
        fecha = str(row.get("fecha") or "")[:10]
        if not fecha:
            continue
        try:
            data = {
                "estacion_id": estacion_id,
                "fecha": fecha,
                "temperatura_max": row.get("temperatura_max"),
                "temperatura_min": row.get("temperatura_min"),
                "temperatura_promedio": row.get("temperatura") or row.get("temperatura_promedio"),
                "humedad": row.get("humedad"),
                "precipitacion": row.get("precipitacion"),
                "probabilidad_lluvia": row.get("probabilidad_lluvia") or row.get("pop"),
                "viento": row.get("viento"),
                "direccion_viento": row.get("direccion_viento"),
                "presion": row.get("presion"),
                "cobertura_nubosa": row.get("cobertura_nubosa"),
                "visibilidad": row.get("visibilidad"),
                "radiacion": row.get("radiacion_solar_sum"),
                "fuente": fuente,
                "actualizado": row.get("actualizado"),
            }
            client.table("meteo_pronostico").upsert(data, on_conflict="estacion_id,fecha").execute()
            n += 1
        except Exception as e:
            print(f"Error al guardar pronostico en Supabase: {e}")
            continue
    return n


def leer_pronostico(estacion_id: str, dias: int = 7) -> list[dict[str, Any]]:
    """Pronóstico persistido (desde hoy en adelante) ordenado por fecha ascendente."""
    client = get_supabase_client()
    if not client:
        return []

    try:
        from datetime import datetime
        from zoneinfo import ZoneInfo

        hoy = datetime.now(ZoneInfo("America/Santiago")).date().isoformat()
        res = (
            client.table("meteo_pronostico")
            .select("*")
            .eq("estacion_id", estacion_id)
            .gte("fecha", hoy)
            .order("fecha", desc=False)
            .limit(dias)
            .execute()
        )
        out = []
        for row in res.data:
            out.append(
                {
                    "estacion_id": estacion_id,
                    "fecha": row.get("fecha"),
                    "temperatura": row.get("temperatura_promedio"),
                    "temperatura_max": row.get("temperatura_max"),
                    "temperatura_min": row.get("temperatura_min"),
                    "humedad": row.get("humedad"),
                    "precipitacion": row.get("precipitacion"),
                    "probabilidad_lluvia": row.get("probabilidad_lluvia"),
                    "viento": row.get("viento"),
                    "direccion_viento": row.get("direccion_viento"),
                    "presion": row.get("presion"),
                    "cobertura_nubosa": row.get("cobertura_nubosa"),
                    "visibilidad": row.get("visibilidad"),
                    "radiacion_solar_sum": row.get("radiacion"),
                    "fuente": row.get("fuente") or "supabase_db",
                }
            )
        return out
    except Exception as e:
        print(f"Error al leer pronostico en Supabase: {e}")
        return []


def guardar_serie(estacion_id: str, tipo: str, payload: dict[str, Any]) -> bool:
    """Upsert de una serie JSON (viento horario, precip 3h, etc.) por estación+tipo."""
    client = get_supabase_client()
    if not client or not payload:
        return False
    try:
        from datetime import datetime, timezone

        data = {
            "estacion_id": estacion_id,
            "tipo": tipo,
            "payload": payload,
            "actualizado": datetime.now(timezone.utc).isoformat(),
        }
        client.table("meteo_series").upsert(data, on_conflict="estacion_id,tipo").execute()
        return True
    except Exception as e:
        print(f"Error al guardar serie en Supabase: {e}")
        return False


def leer_serie(estacion_id: str, tipo: str, max_edad_horas: int = 48) -> dict[str, Any] | None:
    """Última serie JSON persistida; None si no existe o es más vieja que max_edad_horas."""
    client = get_supabase_client()
    if not client:
        return None
    try:
        from datetime import datetime, timezone

        res = (
            client.table("meteo_series")
            .select("*")
            .eq("estacion_id", estacion_id)
            .eq("tipo", tipo)
            .limit(1)
            .execute()
        )
        if not res.data:
            return None
        row = res.data[0]
        payload = row.get("payload")
        if not isinstance(payload, dict):
            return None
        actualizado = row.get("actualizado")
        if actualizado:
            try:
                ts = datetime.fromisoformat(str(actualizado).replace("Z", "+00:00"))
                edad_h = (datetime.now(timezone.utc) - ts).total_seconds() / 3600.0
                if edad_h > max_edad_horas:
                    return None
                payload = dict(payload)
                payload["desde_cache"] = True
                payload["cache_edad_horas"] = round(edad_h, 1)
            except ValueError:
                pass
        return payload
    except Exception as e:
        print(f"Error al leer serie en Supabase: {e}")
        return None


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
