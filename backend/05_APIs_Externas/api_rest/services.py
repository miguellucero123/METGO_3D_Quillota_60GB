#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Servicios de negocio para la API REST METGO."""

from __future__ import annotations

import io
import contextlib
from datetime import datetime
from typing import Any

import pandas as pd

from datos_reales_openmeteo import OpenMeteoData, obtener_datos_meteorologicos_reales

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


def listar_estaciones() -> list[dict[str, Any]]:
    om = OpenMeteoData()
    resultado = []
    for slug in ESTACIONES_PRINCIPALES:
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


def _df_sin_prints(estacion: str, tipo: str, dias: int) -> pd.DataFrame | None:
    """Obtiene DataFrame suprimiendo prints del módulo OpenMeteo."""
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        df = obtener_datos_meteorologicos_reales(
            estacion=estacion, tipo=tipo, dias=dias
        )
    return df


def _ultima_fila(df: pd.DataFrame | None) -> pd.Series | None:
    if df is None or df.empty:
        return None
    ordenado = df.sort_values("fecha", ascending=False)
    return ordenado.iloc[0]


def _fila_a_resumen(row: pd.Series, estacion_id: str) -> dict[str, Any]:
    nombre = row.get("estacion", slug_a_nombre(estacion_id))
    return {
        "estacion_id": estacion_id,
        "estacion": str(nombre),
        "fecha": row["fecha"].isoformat() if hasattr(row["fecha"], "isoformat") else str(row["fecha"]),
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
    row = _ultima_fila(df)
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
    if df is None or df.empty:
        return None
    df = df.sort_values("fecha")
    return [_fila_a_resumen(row, estacion_id) for _, row in df.iterrows()]


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
    return alertas


def recomendaciones_agricolas(estacion_id: str) -> list[dict[str, Any]]:
    """Recomendaciones simples basadas en pronóstico (módulo 02 — lógica básica)."""
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


def health_check() -> dict[str, Any]:
    om = OpenMeteoData()
    with contextlib.redirect_stdout(io.StringIO()):
        ok = om.verificar_conexion()
    return {
        "status": "ok" if ok else "degraded",
        "openmeteo": ok,
        "timestamp": datetime.now().isoformat(),
    }
