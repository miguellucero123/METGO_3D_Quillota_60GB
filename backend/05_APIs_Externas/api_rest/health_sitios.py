#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Healthchecks por sitio (E10) — frescura de datos y SLOs."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from api_rest.estaciones_catalogo import ESTACIONES_POR_SITIO, SITIOS_META, normalizar_sitio

# Umbrales SLO (docs/roadmap/SLO_E10.md)
SLO_AIRE_MAX_HORAS = 2.0
SLO_METEO_MAX_HORAS = 24.0
SLO_OPS_MAX_HORAS = 3.0


def _parse_ts(value: Any) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        dt = value
    else:
        s = str(value).strip().replace("Z", "+00:00")
        try:
            dt = datetime.fromisoformat(s)
        except ValueError:
            return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _edad_horas(ts: datetime | None) -> float | None:
    if ts is None:
        return None
    return max(0.0, (datetime.now(timezone.utc) - ts).total_seconds() / 3600.0)


def _ultima_fecha_tabla(
    tabla: str,
    estacion_ids: list[str],
    col_fecha: str = "fecha_hora",
) -> datetime | None:
    if not estacion_ids:
        return None
    try:
        from api_rest.integracion.supabase_store import get_supabase_client

        client = get_supabase_client()
        if not client:
            return None
        res = (
            client.table(tabla)
            .select(col_fecha)
            .in_("estacion_id", estacion_ids[:40])
            .order(col_fecha, desc=True)
            .limit(1)
            .execute()
        )
        if not res.data:
            return None
        return _parse_ts(res.data[0].get(col_fecha))
    except Exception:
        return None


def _estado_frescura(edad_h: float | None, max_h: float) -> str:
    if edad_h is None:
        return "sin_datos"
    if edad_h <= max_h:
        return "ok"
    if edad_h <= max_h * 2:
        return "degradado"
    return "critico"


def evaluar_sitio(sitio: str) -> dict[str, Any]:
    slug = normalizar_sitio(sitio)
    meta = dict(SITIOS_META.get(slug, {"slug": slug, "nombre": slug}))
    estaciones = list(ESTACIONES_POR_SITIO.get(slug, []))
    dominio = meta.get("dominio") or "meteo"

    out: dict[str, Any] = {
        "sitio": slug,
        "nombre": meta.get("nombre"),
        "dominio": dominio,
        "estaciones": len(estaciones),
        "slo": {
            "aire_max_h": SLO_AIRE_MAX_HORAS,
            "meteo_max_h": SLO_METEO_MAX_HORAS,
            "ops_max_h": SLO_OPS_MAX_HORAS,
        },
        "frescura": {},
        "estado": "ok",
    }

    # Meteo (todos los sitios con estaciones meteo)
    meteo_ts = _ultima_fecha_tabla("meteo_registros", estaciones, col_fecha="fecha")
    if meteo_ts is None:
        # fallback local store
        try:
            from api_rest.integracion import meteo_store

            est = meteo_store.estadisticas_store()
            # sin timestamp global; marcar desconocido si hay registros
            if est.get("registros"):
                out["frescura"]["meteo"] = {
                    "fuente": "sqlite_local",
                    "edad_horas": None,
                    "estado": "desconocido",
                    "registros": est.get("registros"),
                }
        except Exception:
            pass
    if "meteo" not in out["frescura"]:
        edad = _edad_horas(meteo_ts)
        st = _estado_frescura(edad, SLO_METEO_MAX_HORAS)
        out["frescura"]["meteo"] = {
            "ultima": meteo_ts.isoformat() if meteo_ts else None,
            "edad_horas": round(edad, 2) if edad is not None else None,
            "estado": st,
            "slo_max_h": SLO_METEO_MAX_HORAS,
        }

    if dominio in ("aire", "mineria") or slug in ("copiapo", "mantos_blancos"):
        aire_ts = _ultima_fecha_tabla("aire_registros", estaciones)
        edad = _edad_horas(aire_ts)
        st = _estado_frescura(edad, SLO_AIRE_MAX_HORAS)
        out["frescura"]["aire"] = {
            "ultima": aire_ts.isoformat() if aire_ts else None,
            "edad_horas": round(edad, 2) if edad is not None else None,
            "estado": st,
            "slo_max_h": SLO_AIRE_MAX_HORAS,
        }

    if dominio == "mineria" or slug == "mantos_blancos":
        ops_ts = _ultima_fecha_tabla("operaciones_ventanas", estaciones)
        edad = _edad_horas(ops_ts)
        st = _estado_frescura(edad, SLO_OPS_MAX_HORAS)
        out["frescura"]["operaciones"] = {
            "ultima": ops_ts.isoformat() if ops_ts else None,
            "edad_horas": round(edad, 2) if edad is not None else None,
            "estado": st,
            "slo_max_h": SLO_OPS_MAX_HORAS,
        }

    estados = [v.get("estado") for v in out["frescura"].values()]
    if any(s == "critico" for s in estados):
        out["estado"] = "critico"
    elif any(s in ("degradado", "sin_datos") for s in estados):
        out["estado"] = "degradado"
    else:
        out["estado"] = "ok"
    return out


def listar_health_sitios(incluir_plantilla: bool = False) -> dict[str, Any]:
    sitios = []
    for slug, meta in SITIOS_META.items():
        if not incluir_plantilla and meta.get("estado") == "plantilla":
            continue
        sitios.append(evaluar_sitio(slug))
    globales = "ok"
    if any(s["estado"] == "critico" for s in sitios):
        globales = "critico"
    elif any(s["estado"] == "degradado" for s in sitios):
        globales = "degradado"
    return {
        "fase": "E10",
        "estado": globales,
        "generado": datetime.now(timezone.utc).isoformat(),
        "sitios": sitios,
        "slo_ref": "docs/roadmap/SLO_E10.md",
    }
