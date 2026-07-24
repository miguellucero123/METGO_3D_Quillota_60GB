#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Persistencia meteo (Supabase) para complementar OpenMeteo.

Usa el cliente de ``api_rest.integracion.supabase_store`` (mismas env vars que
aire/ops). Evita importar ``backend.08_Gestion_Datos`` (falla en algunos
despliegues Render → store vacío → 503).
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

try:
    from zoneinfo import ZoneInfo
except ImportError:  # pragma: no cover
    ZoneInfo = None  # type: ignore


def _db_path() -> Path:
    """Ruta legacy SQLite (capabilities / integración fase 4)."""
    for p in Path(__file__).resolve().parents:
        if (p / "metgo_paths.py").exists():
            gd = p / "backend" / "08_Gestion_Datos" / "datos_runtime"
            gd.mkdir(parents=True, exist_ok=True)
            return gd / "meteo_historico.db"
    return Path("meteo_historico.db")


def _client():
    try:
        from api_rest.integracion.supabase_store import get_supabase_client

        return get_supabase_client()
    except Exception as exc:
        print(f"meteo_store: cliente Supabase no disponible: {exc}")
        return None


def _hoy_chile() -> str:
    if ZoneInfo is not None:
        return datetime.now(ZoneInfo("America/Santiago")).date().isoformat()
    return datetime.utcnow().date().isoformat()


def _fila_registro(estacion_id: str, row: dict[str, Any]) -> dict[str, Any]:
    return {
        "estacion_id": estacion_id,
        "fecha": row.get("fecha"),
        "temperatura_max": row.get("temperatura_max"),
        "temperatura_min": row.get("temperatura_min"),
        "temperatura_promedio": row.get("temperatura_promedio") or row.get("temperatura"),
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


def guardar_registros(estacion_id: str, filas: list[dict[str, Any]], fuente: str = "openmeteo") -> int:
    client = _client()
    if not client or not filas:
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
                "temperatura_promedio": row.get("temperatura_promedio") or row.get("temperatura"),
                "humedad": row.get("humedad"),
                "precipitacion": row.get("precipitacion"),
                "viento": row.get("viento"),
                "presion": row.get("presion"),
                "fuente": fuente,
            }
            client.table("meteo_registros").upsert(data, on_conflict="estacion_id,fecha").execute()
            n += 1
        except Exception as e:
            print(f"meteo_store.guardar_registros: {e}")
    return n


def leer_registros(estacion_id: str, dias: int = 30) -> list[dict[str, Any]]:
    dias = max(1, min(int(dias or 30), 3650))
    client = _client()
    if client:
        try:
            res = (
                client.table("meteo_registros")
                .select("*")
                .eq("estacion_id", estacion_id)
                .order("fecha", desc=True)
                .limit(dias)
                .execute()
            )
            rows = [_fila_registro(estacion_id, r) for r in (res.data or [])]
            return list(reversed(rows))
        except Exception as e:
            print(f"meteo_store.leer_registros SDK {estacion_id}: {e}")
    try:
        from api_rest.integracion.supabase_store import rest_select

        raw = rest_select(
            "meteo_registros",
            params={
                "estacion_id": f"eq.{estacion_id}",
                "order": "fecha.desc",
                "select": "*",
            },
            limit=dias,
        )
        return list(reversed([_fila_registro(estacion_id, r) for r in raw]))
    except Exception as e:
        print(f"meteo_store.leer_registros REST {estacion_id}: {e}")
        return []


def guardar_pronostico(
    estacion_id: str, filas: list[dict[str, Any]], fuente: str = "openmeteo_pronostico"
) -> int:
    client = _client()
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
                "probabilidad_lluvia": row.get("probabilidad_lluvia"),
                "viento": row.get("viento"),
                "direccion_viento": row.get("direccion_viento"),
                "presion": row.get("presion"),
                "cobertura_nubosa": row.get("cobertura_nubosa"),
                "visibilidad": row.get("visibilidad"),
                "radiacion": row.get("radiacion_solar_sum") or row.get("radiacion"),
                "fuente": fuente,
            }
            client.table("meteo_pronostico").upsert(
                data, on_conflict="estacion_id,fecha"
            ).execute()
            n += 1
        except Exception as e:
            print(f"meteo_store.guardar_pronostico: {e}")
    return n


def leer_pronostico(estacion_id: str, dias: int = 7) -> list[dict[str, Any]]:
    """Lee pronóstico persistido. Si no hay filas ≥ hoy, usa las últimas N guardadas."""
    dias = max(1, min(int(dias or 7), 16))
    hoy = _hoy_chile()

    def _map_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
        out = []
        for row in rows:
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

    client = _client()
    if client:
        try:
            res = (
                client.table("meteo_pronostico")
                .select("*")
                .eq("estacion_id", estacion_id)
                .gte("fecha", hoy)
                .order("fecha", desc=False)
                .limit(dias)
                .execute()
            )
            rows = res.data or []
            if not rows:
                res2 = (
                    client.table("meteo_pronostico")
                    .select("*")
                    .eq("estacion_id", estacion_id)
                    .order("fecha", desc=True)
                    .limit(dias)
                    .execute()
                )
                rows = list(reversed(res2.data or []))
            return _map_rows(rows)
        except Exception as e:
            print(f"meteo_store.leer_pronostico SDK {estacion_id}: {e}")

    try:
        from api_rest.integracion.supabase_store import rest_select

        raw = rest_select(
            "meteo_pronostico",
            params={
                "estacion_id": f"eq.{estacion_id}",
                "fecha": f"gte.{hoy}",
                "order": "fecha.asc",
                "select": "*",
            },
            limit=dias,
        )
        if not raw:
            raw = list(
                reversed(
                    rest_select(
                        "meteo_pronostico",
                        params={
                            "estacion_id": f"eq.{estacion_id}",
                            "order": "fecha.desc",
                            "select": "*",
                        },
                        limit=dias,
                    )
                )
            )
        return _map_rows(raw)
    except Exception as e:
        print(f"meteo_store.leer_pronostico REST {estacion_id}: {e}")
        return []


def guardar_serie(estacion_id: str, tipo: str, payload: dict[str, Any]) -> bool:
    client = _client()
    if not client or not payload:
        return False
    try:
        client.table("meteo_series").upsert(
            {
                "estacion_id": estacion_id,
                "tipo": tipo,
                "payload": payload,
                "actualizado": datetime.utcnow().isoformat(),
            },
            on_conflict="estacion_id,tipo",
        ).execute()
        return True
    except Exception as e:
        print(f"meteo_store.guardar_serie: {e}")
        return False


def leer_serie(estacion_id: str, tipo: str, max_edad_horas: int = 48) -> dict[str, Any] | None:
    client = _client()
    if not client:
        return None
    try:
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
        return payload if isinstance(payload, dict) else None
    except Exception as e:
        print(f"meteo_store.leer_serie: {e}")
        return None


def guardar_helada_pronostico(
    estacion_id: str,
    filas: list[dict[str, Any]],
    cultivo: str = "palto",
    fuente: str = "modelo_helada_radiativa",
) -> int:
    client = _client()
    if not client or not filas:
        return 0
    n = 0
    for row in filas:
        fecha = str(row.get("fecha") or "")[:10]
        if not fecha:
            continue
        try:
            data = dict(row)
            data["estacion_id"] = estacion_id
            data["fecha"] = fecha
            data["cultivo"] = cultivo
            data["fuente"] = fuente
            client.table("meteo_helada_pronostico").upsert(
                data, on_conflict="estacion_id,fecha,cultivo"
            ).execute()
            n += 1
        except Exception as e:
            print(f"meteo_store.guardar_helada: {e}")
    return n


def leer_helada_pronostico(
    estacion_id: str, dias: int = 7, cultivo: str = "palto"
) -> list[dict[str, Any]]:
    client = _client()
    if not client:
        return []
    try:
        res = (
            client.table("meteo_helada_pronostico")
            .select("*")
            .eq("estacion_id", estacion_id)
            .eq("cultivo", cultivo)
            .order("fecha", desc=True)
            .limit(max(1, dias))
            .execute()
        )
        return list(reversed(res.data or []))
    except Exception as e:
        print(f"meteo_store.leer_helada: {e}")
        return []


def estadisticas_store() -> dict[str, Any]:
    try:
        from api_rest.integracion.supabase_store import (
            SUPABASE_URL,
            rest_select,
            supabase_status,
        )
    except Exception:
        SUPABASE_URL = None
        rest_select = None  # type: ignore
        supabase_status = None  # type: ignore

    client = _client()
    if client:
        try:
            res = (
                client.table("meteo_registros")
                .select("estacion_id", count="exact")
                .limit(1)
                .execute()
            )
            total = res.count if res.count is not None else len(res.data or [])
            if not total:
                sample = (
                    client.table("meteo_registros")
                    .select("estacion_id")
                    .eq("estacion_id", "quillota")
                    .limit(5)
                    .execute()
                )
                total = len(sample.data or [])
            return {
                "registros": total,
                "estaciones": 0,
                "db": SUPABASE_URL,
                "mode": "sdk",
            }
        except Exception as e:
            return {
                "registros": 0,
                "estaciones": 0,
                "db": SUPABASE_URL,
                "error": str(e),
            }

    if rest_select:
        sample = rest_select(
            "meteo_registros",
            params={"select": "estacion_id", "estacion_id": "eq.quillota"},
            limit=5,
        )
        st = supabase_status() if supabase_status else {}
        if sample or st.get("rest_ok"):
            return {
                "registros": len(sample),
                "estaciones": 0,
                "db": SUPABASE_URL,
                "mode": "rest",
            }
        return {
            "registros": 0,
            "estaciones": 0,
            "db": "supabase (inactivo)",
            "error": st.get("error"),
        }

    return {"registros": 0, "estaciones": 0, "db": "supabase (inactivo)"}
