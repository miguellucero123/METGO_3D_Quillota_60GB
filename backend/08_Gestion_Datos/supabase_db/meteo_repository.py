from typing import Any
from .client import get_supabase_client, SUPABASE_URL


def _bool_o_none(v: Any) -> bool | None:
    if v is None:
        return None
    if isinstance(v, bool):
        return v
    if isinstance(v, (int, float)):
        return bool(v)
    s = str(v).strip().lower()
    if s in ("1", "true", "t", "yes", "si", "sí"):
        return True
    if s in ("0", "false", "f", "no"):
        return False
    return None


def _helada_desde_fila(row: dict[str, Any]) -> bool | None:
    h = _bool_o_none(row.get("helada"))
    if h is not None:
        return h
    tmin = row.get("temperatura_min")
    if tmin is None:
        return None
    try:
        return float(tmin) <= 0.0
    except (TypeError, ValueError):
        return None


def _niebla_desde_fila(row: dict[str, Any]) -> bool | None:
    n = _bool_o_none(row.get("niebla"))
    if n is not None:
        return n
    for key in ("visibilidad_madrugada", "visibilidad"):
        vis = row.get(key)
        if vis is None:
            continue
        try:
            return float(vis) < 1.0
        except (TypeError, ValueError):
            continue
    return None


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
            radiacion = row.get("radiacion_solar_sum")
            if radiacion is None:
                radiacion = row.get("radiacion")
            data = {
                "estacion_id": estacion_id,
                "fecha": fecha,
                "temperatura_max": row.get("temperatura_max"),
                "temperatura_min": row.get("temperatura_min"),
                "temperatura_promedio": row.get("temperatura_promedio") or row.get("temperatura"),
                "humedad": row.get("humedad"),
                "precipitacion": row.get("precipitacion"),
                "viento": row.get("viento"),
                "presion": row.get("presion"),
                "cobertura_nubosa": row.get("cobertura_nubosa"),
                "visibilidad": row.get("visibilidad"),
                "radiacion": radiacion,
                "evapotranspiracion": row.get("evapotranspiracion"),
                "helada": _helada_desde_fila(row),
                "niebla": _niebla_desde_fila(row),
                "fuente": fuente,
            }
            client.table("meteo_registros").upsert(data, on_conflict="estacion_id,fecha").execute()
            n += 1
        except Exception as e:
            print(f"Error al guardar registro en Supabase: {e}")
            continue
    return n


def leer_registros(estacion_id: str, dias: int = 30) -> list[dict[str, Any]]:
    """Lee histórico por estación. Pagina de a 1000 (tope PostgREST por defecto)."""
    client = get_supabase_client()
    if not client:
        return []

    dias = max(1, int(dias))
    page_size = 1000
    rows: list[dict[str, Any]] = []

    try:
        offset = 0
        while offset < dias:
            end = min(offset + page_size, dias) - 1
            res = (
                client.table("meteo_registros")
                .select("*")
                .eq("estacion_id", estacion_id)
                .order("fecha", desc=True)
                .range(offset, end)
                .execute()
            )
            batch = res.data or []
            if not batch:
                break
            rows.extend(batch)
            if len(batch) < (end - offset + 1):
                break
            offset += page_size

        out = []
        for row in rows:
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


def _fecha_helada(row: dict[str, Any]) -> str:
    raw = row.get("fecha") or row.get("fecha_pronostico") or ""
    return str(raw)[:10]


def guardar_helada_pronostico(
    estacion_id: str,
    filas: list[dict[str, Any]],
    cultivo: str = "palto",
    fuente: str = "modelo_helada_radiativa",
) -> int:
    """Upsert del pronóstico de identificación de helada (modelo radiativo + psicrómetro)."""
    client = get_supabase_client()
    if not client or not filas:
        return 0

    from datetime import datetime, timezone

    cultivo_n = (cultivo or "palto").lower()
    ahora = datetime.now(timezone.utc).isoformat()
    n = 0
    for row in filas:
        fecha = _fecha_helada(row)
        if not fecha:
            continue
        try:
            data = {
                "estacion_id": estacion_id,
                "fecha": fecha,
                "cultivo": cultivo_n,
                "probabilidad_helada": row.get("probabilidad_helada"),
                "probabilidad_boletin": row.get("probabilidad_boletin"),
                "nivel_riesgo": row.get("nivel_riesgo"),
                "riesgo_severo": bool(row.get("riesgo_severo")),
                "riesgo_moderado": bool(row.get("riesgo_moderado")),
                "riesgo_inminente": bool(row.get("riesgo_inminente")),
                "tipo_helada": row.get("tipo_helada")
                or (row.get("dano_cultivo") or {}).get("tipo_helada"),
                "temperatura_minima_esperada": row.get("temperatura_minima_esperada"),
                "temperatura_maxima": row.get("temperatura_maxima"),
                "temperatura_atardecer": row.get("temperatura_atardecer"),
                "punto_rocio_atardecer": row.get("punto_rocio_atardecer")
                or row.get("punto_rocio"),
                "bulbo_humedo_atardecer": row.get("bulbo_humedo_atardecer")
                or row.get("bulbo_humedo"),
                "humedad_relativa": row.get("humedad_relativa") or row.get("humedad"),
                "cobertura_nubosa": row.get("cobertura_nubosa"),
                "velocidad_viento": row.get("velocidad_viento") or row.get("viento"),
                "umbral_cultivo": row.get("umbral_cultivo"),
                "umbrales_cultivo": row.get("umbrales_cultivo"),
                "alerta_cultivo": bool(row.get("alerta_cultivo"))
                if row.get("alerta_cultivo") is not None
                else None,
                "hora_critica_esperada": row.get("hora_critica_esperada") or "04:00",
                "criterio_psicrometro": row.get("criterio_psicrometro"),
                "condiciones_atmosfericas": row.get("condiciones_atmosfericas"),
                "factor_oquedad": row.get("factor_oquedad"),
                "factor_humedad_suelo": row.get("factor_humedad_suelo"),
                "dano_cultivo": row.get("dano_cultivo"),
                "scores_componentes": row.get("scores_componentes"),
                "factores_contribuyentes": row.get("factores_contribuyentes"),
                "recomendaciones": row.get("recomendaciones"),
                "fuente": fuente,
                "actualizado": ahora,
            }
            client.table("meteo_helada_pronostico").upsert(
                data, on_conflict="estacion_id,fecha,cultivo"
            ).execute()
            n += 1
        except Exception as e:
            print(f"Error al guardar helada en Supabase: {e}")
            continue
    return n


def leer_helada_pronostico(
    estacion_id: str, dias: int = 7, cultivo: str = "palto"
) -> list[dict[str, Any]]:
    """Pronóstico de helada persistido desde hoy (Chile)."""
    client = get_supabase_client()
    if not client:
        return []
    try:
        from datetime import datetime
        from zoneinfo import ZoneInfo

        hoy = datetime.now(ZoneInfo("America/Santiago")).date().isoformat()
        cultivo_n = (cultivo or "palto").lower()
        res = (
            client.table("meteo_helada_pronostico")
            .select("*")
            .eq("estacion_id", estacion_id)
            .eq("cultivo", cultivo_n)
            .gte("fecha", hoy)
            .order("fecha", desc=False)
            .limit(dias)
            .execute()
        )
        out: list[dict[str, Any]] = []
        for row in res.data or []:
            out.append(
                {
                    "estacion_id": estacion_id,
                    "fecha_pronostico": row.get("fecha"),
                    "cultivo": row.get("cultivo") or cultivo_n,
                    "probabilidad_helada": row.get("probabilidad_helada"),
                    "probabilidad_boletin": row.get("probabilidad_boletin"),
                    "nivel_riesgo": row.get("nivel_riesgo"),
                    "riesgo_severo": row.get("riesgo_severo"),
                    "riesgo_moderado": row.get("riesgo_moderado"),
                    "riesgo_inminente": row.get("riesgo_inminente"),
                    "tipo_helada": row.get("tipo_helada"),
                    "temperatura_minima_esperada": row.get("temperatura_minima_esperada"),
                    "temperatura_maxima": row.get("temperatura_maxima"),
                    "temperatura_atardecer": row.get("temperatura_atardecer"),
                    "punto_rocio_atardecer": row.get("punto_rocio_atardecer"),
                    "punto_rocio": row.get("punto_rocio_atardecer"),
                    "bulbo_humedo_atardecer": row.get("bulbo_humedo_atardecer"),
                    "bulbo_humedo": row.get("bulbo_humedo_atardecer"),
                    "humedad_relativa": row.get("humedad_relativa"),
                    "cobertura_nubosa": row.get("cobertura_nubosa"),
                    "velocidad_viento": row.get("velocidad_viento"),
                    "umbral_cultivo": row.get("umbral_cultivo"),
                    "umbrales_cultivo": row.get("umbrales_cultivo"),
                    "alerta_cultivo": row.get("alerta_cultivo"),
                    "hora_critica_esperada": row.get("hora_critica_esperada"),
                    "criterio_psicrometro": row.get("criterio_psicrometro"),
                    "condiciones_atmosfericas": row.get("condiciones_atmosfericas"),
                    "factor_oquedad": row.get("factor_oquedad"),
                    "factor_humedad_suelo": row.get("factor_humedad_suelo"),
                    "dano_cultivo": row.get("dano_cultivo"),
                    "scores_componentes": row.get("scores_componentes"),
                    "factores_contribuyentes": row.get("factores_contribuyentes"),
                    "recomendaciones": row.get("recomendaciones"),
                    "recomendacion": (
                        (row.get("criterio_psicrometro") or {}).get("mensaje")
                        if isinstance(row.get("criterio_psicrometro"), dict)
                        else None
                    ),
                    "fuente": row.get("fuente") or "supabase_db",
                    "desde_cache": True,
                }
            )
        return out
    except Exception as e:
        print(f"Error al leer helada en Supabase: {e}")
        return []


def estadisticas_store() -> dict[str, Any]:
    client = get_supabase_client()
    if not client:
        return {"registros": 0, "estaciones": 0, "db": "supabase (inactivo)"}
    try:
        res = client.table("meteo_registros").select("estacion_id", count="exact").limit(1).execute()
        total = res.count if res.count is not None else 0
        out: dict[str, Any] = {"registros": total, "estaciones": 0, "db": SUPABASE_URL}
        try:
            hp = (
                client.table("meteo_helada_pronostico")
                .select("id", count="exact")
                .limit(1)
                .execute()
            )
            out["heladas_pronostico"] = hp.count if hp.count is not None else 0
        except Exception:
            out["heladas_pronostico"] = 0
        try:
            pr = (
                client.table("meteo_pronostico")
                .select("id", count="exact")
                .limit(1)
                .execute()
            )
            out["pronosticos"] = pr.count if pr.count is not None else 0
        except Exception:
            out["pronosticos"] = 0
        return out
    except Exception:
        return {"registros": 0, "estaciones": 0, "db": SUPABASE_URL}
