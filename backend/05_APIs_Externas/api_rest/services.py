#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Servicios de negocio para la API REST METGO."""

from __future__ import annotations

import io
import contextlib
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd

from datos_reales_openmeteo import OpenMeteoData, obtener_datos_meteorologicos_reales

# Caché OpenMeteo (Fase 1.4)
_CACHE_MOD = None
for _p in Path(__file__).resolve().parents:
    _gd = _p / "08_Gestion_Datos"
    if (_p / "metgo_paths.py").exists() and _gd.is_dir():
        if str(_gd) not in sys.path:
            sys.path.insert(0, str(_gd))
        try:
            from cache_openmeteo import get_meteo_cached as _get_meteo_cached

            _CACHE_MOD = _get_meteo_cached
        except ImportError:
            pass
        break

# Slug (Vue) -> nombre OpenMeteo
SLUG_A_NOMBRE: dict[str, str] = {
    "quillota": "Quillota",
    "los_nogales": "Los Nogales",
    "hijuelas": "Hijuelas",
    "limache": "Limache",
    "olmue": "Olmue",
    "santiago": "Santiago",
    "valparaiso": "Valparaiso",
    "vina_del_mar": "Viña del Mar",
    "casablanca": "Casablanca",
}

NOMBRE_A_SLUG = {v: k for k, v in SLUG_A_NOMBRE.items()}

# Estaciones expuestas en el dashboard principal
ESTACIONES_PRINCIPALES = [
    "quillota",
    "los_nogales",
    "hijuelas",
    "limache",
    "olmue",
]


def slug_a_nombre(estacion_id: str) -> str:
    key = estacion_id.lower().replace("-", "_")
    if key in SLUG_A_NOMBRE:
        return SLUG_A_NOMBRE[key]
    return estacion_id.replace("_", " ").title()


def nombre_a_slug(nombre: str) -> str:
    return NOMBRE_A_SLUG.get(nombre, nombre.lower().replace(" ", "_"))


def listar_estaciones(tenant_id: str | None = None) -> list[dict[str, Any]]:
    om = OpenMeteoData()
    slugs = ESTACIONES_PRINCIPALES
    if tenant_id:
        try:
            from api_rest.tenants import estaciones_de_tenant

            slugs = [s for s in estaciones_de_tenant(tenant_id) if s in SLUG_A_NOMBRE]
        except ImportError:
            pass
    resultado = []
    for slug in slugs:
        nombre = SLUG_A_NOMBRE[slug]
        if nombre in om.estaciones:
            coords = om.estaciones[nombre]
            resultado.append(
                {
                    "id": slug,
                    "nombre": nombre,
                    "activa": True,
                    "lat": coords["lat"],
                    "lon": coords["lon"],
                }
            )
    return resultado


def _fetch_meteo_raw(estacion: str, tipo: str, dias: int) -> pd.DataFrame | None:
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        return obtener_datos_meteorologicos_reales(
            estacion=estacion, tipo=tipo, dias=dias
        )


def _df_sin_prints(estacion: str, tipo: str, dias: int) -> pd.DataFrame | None:
    """Obtiene DataFrame suprimiendo prints; usa caché si está disponible."""
    if _CACHE_MOD:
        return _CACHE_MOD(estacion, tipo, dias, _fetch_meteo_raw)
    return _fetch_meteo_raw(estacion, tipo, dias)


def _fila_hoy(df: pd.DataFrame | None) -> pd.Series | None:
    """Fila del día actual (o la más reciente pasada), no el último día del pronóstico."""
    if df is None or df.empty:
        return None
    work = df.copy()
    if not pd.api.types.is_datetime64_any_dtype(work["fecha"]):
        work["fecha"] = pd.to_datetime(work["fecha"])
    hoy = pd.Timestamp.now().normalize()
    fechas = work["fecha"].dt.normalize()
    mask_hoy = fechas == hoy
    if mask_hoy.any():
        return work.loc[mask_hoy].sort_values("fecha").iloc[0]
    pasados = work[fechas <= hoy]
    if not pasados.empty:
        return pasados.sort_values("fecha", ascending=False).iloc[0]
    return work.sort_values("fecha", ascending=True).iloc[0]


def _ultima_fila(df: pd.DataFrame | None) -> pd.Series | None:
    """Última fila cronológica (histórico). Para resumen del día use _fila_hoy."""
    if df is None or df.empty:
        return None
    return df.sort_values("fecha", ascending=False).iloc[0]


def _fecha_dia(val: Any) -> str:
    """Normaliza cualquier fecha a YYYY-MM-DD (evita duplicados local vs OpenMeteo)."""
    if val is None:
        return ""
    if hasattr(val, "strftime"):
        return val.strftime("%Y-%m-%d")
    return str(val)[:10]


def _dedupe_historico_por_dia(filas: list[dict[str, Any]], dias: int) -> list[dict[str, Any]]:
    """Una fila por día; OpenMeteo pisa local si hay conflicto."""
    por_dia: dict[str, dict[str, Any]] = {}
    for r in filas:
        dia = _fecha_dia(r.get("fecha"))
        if dia:
            por_dia[dia] = {**r, "fecha": dia}
    return sorted(por_dia.values(), key=lambda x: x["fecha"])[-dias:]


def _fila_a_resumen(row: pd.Series, estacion_id: str) -> dict[str, Any]:
    nombre = row.get("estacion", slug_a_nombre(estacion_id))
    return {
        "estacion_id": estacion_id,
        "estacion": str(nombre),
        "fecha": _fecha_dia(row["fecha"]),
        "temperatura": round(float(row.get("temperatura_promedio") or 0), 1),
        "temperatura_max": round(float(row.get("temperatura_max") or 0), 1),
        "temperatura_min": round(float(row.get("temperatura_min") or 0), 1),
        "humedad": round(float(row.get("humedad_relativa") or 0), 1),
        "viento": round(float(row.get("velocidad_viento") or 0), 1),
        "precipitacion": round(float(row.get("precipitacion") or 0), 1),
        "presion": round(float(row.get("presion_atmosferica") or 0), 1),
        "fuente": str(row.get("fuente_datos", "desconocida")),
        "actualizado": datetime.now().isoformat(),
    }


def resumen_meteo(estacion_id: str) -> dict[str, Any] | None:
    nombre = slug_a_nombre(estacion_id)
    df = _df_sin_prints(nombre, "pronostico", 7)
    row = _fila_hoy(df)
    if row is None:
        return None
    return _fila_a_resumen(row, estacion_id)


def pronostico_meteo(estacion_id: str, dias: int = 7) -> list[dict[str, Any]] | None:
    nombre = slug_a_nombre(estacion_id)
    df = _df_sin_prints(nombre, "pronostico", min(dias, 16))
    if df is None or df.empty:
        return None
    df = df.sort_values("fecha")
    registros = []
    for _, row in df.iterrows():
        registros.append(_fila_a_resumen(row, estacion_id))
    return registros


def historico_meteo(estacion_id: str, dias: int = 30) -> list[dict[str, Any]] | None:
    nombre = slug_a_nombre(estacion_id)
    df = _df_sin_prints(nombre, "historicos", min(dias, 92))
    registros: list[dict[str, Any]] = []
    if df is not None and not df.empty:
        df = df.sort_values("fecha")
        registros = [_fila_a_resumen(row, estacion_id) for _, row in df.iterrows()]
    try:
        from api_rest.integracion.meteo_store import guardar_registros, leer_registros

        if registros:
            guardar_registros(estacion_id, registros)
        local = leer_registros(estacion_id, dias)
        merged: list[dict[str, Any]] = []
        if local:
            merged.extend(local)
        if registros:
            merged.extend(registros)
        if merged:
            return _dedupe_historico_por_dia(merged, dias)
    except ImportError:
        pass
    return _dedupe_historico_por_dia(registros, dias) if registros else None


def generar_alertas(estacion_id: str | None = None) -> list[dict[str, Any]]:
    """Alertas derivadas de umbrales sobre el pronóstico actual."""
    alertas: list[dict[str, Any]] = []
    estaciones = [estacion_id] if estacion_id else ESTACIONES_PRINCIPALES
    aid = 1

    for eid in estaciones:
        resumen = resumen_meteo(eid)
        if not resumen:
            continue
        nombre = resumen["estacion"]

        if resumen["temperatura_max"] >= 32:
            alertas.append(
                {
                    "id": aid,
                    "nivel": "warning",
                    "estacion_id": eid,
                    "mensaje": f"{nombre}: temperatura máxima alta ({resumen['temperatura_max']}°C)",
                }
            )
            aid += 1
        if resumen["temperatura_min"] <= 4:
            alertas.append(
                {
                    "id": aid,
                    "nivel": "warning",
                    "estacion_id": eid,
                    "mensaje": f"{nombre}: riesgo de heladas (mín {resumen['temperatura_min']}°C)",
                }
            )
            aid += 1
        if resumen["precipitacion"] >= 10:
            alertas.append(
                {
                    "id": aid,
                    "nivel": "info",
                    "estacion_id": eid,
                    "mensaje": f"{nombre}: precipitación significativa ({resumen['precipitacion']} mm)",
                }
            )
            aid += 1
        if resumen["viento"] >= 40:
            alertas.append(
                {
                    "id": aid,
                    "nivel": "warning",
                    "estacion_id": eid,
                    "mensaje": f"{nombre}: viento fuerte ({resumen['viento']} km/h)",
                }
            )
            aid += 1
        if resumen["humedad"] >= 90:
            alertas.append(
                {
                    "id": aid,
                    "nivel": "info",
                    "estacion_id": eid,
                    "mensaje": f"{nombre}: humedad muy alta ({resumen['humedad']}%)",
                }
            )
            aid += 1

    if not alertas:
        alertas.append(
            {
                "id": 1,
                "nivel": "info",
                "estacion_id": estacion_id or "quillota",
                "mensaje": "Condiciones dentro de rangos normales",
            }
        )

    try:
        from api_rest.integracion.alertas_store import evaluar_umbrales_01, registrar_alertas

        for eid in estaciones:
            res = resumen_meteo(eid)
            if res:
                extra = evaluar_umbrales_01(res, eid)
                seen = {a["mensaje"] for a in alertas}
                for ex in extra:
                    if ex["mensaje"] not in seen:
                        ex["id"] = aid
                        aid += 1
                        alertas.append(ex)
        registrar_alertas(alertas)
    except ImportError:
        pass

    return alertas


def recomendaciones_agricolas(estacion_id: str, *, avanzado: bool = True) -> list[dict[str, Any]]:
    """Recomendaciones módulo 02 (avanzado si está disponible)."""
    pron = pronostico_meteo(estacion_id, 14) or []
    hist = historico_meteo(estacion_id, 14) or []
    filas = (hist or []) + (pron or [])

    if avanzado and filas:
        try:
            from api_rest.integracion.agricola_avanzado import recomendaciones_lista

            return recomendaciones_lista(filas, estacion_id)
        except Exception:
            pass

    resumen = resumen_meteo(estacion_id)
    if not resumen:
        return [
            {
                "cultivo": "General",
                "accion": "Sin datos",
                "motivo": "No se pudo obtener pronóstico",
            }
        ]

    recs = []
    t_min = resumen["temperatura_min"]
    precip = resumen["precipitacion"]
    humedad = resumen["humedad"]

    if t_min <= 5:
        recs.append(
            {
                "cultivo": "Cítricos / Vid",
                "accion": "Activar protección antihielo",
                "motivo": f"Temperatura mínima prevista {t_min}°C",
            }
        )
    if precip >= 5:
        recs.append(
            {
                "cultivo": "General",
                "accion": "Suspender riego",
                "motivo": f"Precipitación esperada {precip} mm",
            }
        )
    elif precip < 1 and humedad < 50:
        recs.append(
            {
                "cultivo": "Palta / Hortalizas",
                "accion": "Programar riego moderado",
                "motivo": f"Baja humedad ({humedad}%) y sin lluvia",
            }
        )
    else:
        recs.append(
            {
                "cultivo": "General",
                "accion": "Monitoreo rutinario",
                "motivo": "Condiciones estables según pronóstico",
            }
        )

    return recs


def reporte_agricola_avanzado(estacion_id: str) -> dict[str, Any]:
    pron = pronostico_meteo(estacion_id, 14) or []
    hist = historico_meteo(estacion_id, 14) or []
    filas = (hist or []) + (pron or [])
    try:
        from api_rest.integracion.agricola_avanzado import reporte_integral

        return reporte_integral(filas)
    except ImportError as e:
        return {"error": str(e)}


def comparativo_estaciones(tenant_id: str | None = None) -> list[dict[str, Any]]:
    """Resumen actual de todas las estaciones principales (Fase 2.1)."""
    filas = []
    slugs = ESTACIONES_PRINCIPALES
    if tenant_id:
        try:
            from api_rest.tenants import estaciones_de_tenant

            slugs = estaciones_de_tenant(tenant_id)
        except ImportError:
            pass
    for slug in slugs:
        res = resumen_meteo(slug)
        if res:
            filas.append(res)
    return filas


def comparativo_historico(dias: int = 14, tenant_id: str | None = None) -> list[dict[str, Any]]:
    """Histórico reciente de todas las estaciones principales (visualizaciones / comparativo)."""
    slugs = list(ESTACIONES_PRINCIPALES)
    if tenant_id:
        try:
            from api_rest.tenants import estaciones_de_tenant

            slugs = [s for s in estaciones_de_tenant(tenant_id) if s in SLUG_A_NOMBRE]
        except ImportError:
            pass
    filas: list[dict[str, Any]] = []
    limite = min(max(dias, 1), 92)
    for slug in slugs:
        hist = historico_meteo(slug, limite) or []
        nombre = slug_a_nombre(slug)
        for row in hist[-limite:]:
            filas.append(
                {
                    **row,
                    "estacion_id": slug,
                    "estacion": nombre,
                    "fecha": _fecha_dia(row.get("fecha")),
                }
            )
    return filas


def metricas_globales(tenant_id: str | None = None) -> dict[str, Any]:
    """KPIs consolidados del valle (Fase 2.1)."""
    filas = comparativo_estaciones(tenant_id)
    if not filas:
        return {
            "estaciones_activas": 0,
            "temperatura_media_max": None,
            "temperatura_media_min": None,
            "precipitacion_total": 0,
            "alertas_activas": 0,
            "actualizado": datetime.now().isoformat(),
        }
    alertas = generar_alertas()
    alertas_warn = sum(1 for a in alertas if a.get("nivel") == "warning")
    return {
        "estaciones_activas": len(filas),
        "temperatura_media_max": round(
            sum(f["temperatura_max"] for f in filas) / len(filas), 1
        ),
        "temperatura_media_min": round(
            sum(f["temperatura_min"] for f in filas) / len(filas), 1
        ),
        "precipitacion_total": round(sum(f["precipitacion"] for f in filas), 1),
        "viento_max": max(f["viento"] for f in filas),
        "humedad_media": round(sum(f["humedad"] for f in filas) / len(filas), 1),
        "alertas_activas": len(alertas),
        "alertas_warning": alertas_warn,
        "estaciones": [f["estacion_id"] for f in filas],
        "actualizado": datetime.now().isoformat(),
    }


def health_check() -> dict[str, Any]:
    t0 = time.perf_counter()
    om = OpenMeteoData()
    with contextlib.redirect_stdout(io.StringIO()):
        ok = om.verificar_conexion()
    latencia_ms = int((time.perf_counter() - t0) * 1000)
    stats = {"cache_hits": 0, "cache_misses": 0}
    try:
        from cache_openmeteo import cache_stats

        stats = cache_stats()
    except ImportError:
        pass
    return {
        "status": "ok" if ok else "degraded",
        "openmeteo": ok,
        "latencia_openmeteo_ms": latencia_ms,
        "timestamp": datetime.now().isoformat(),
        **stats,
    }
