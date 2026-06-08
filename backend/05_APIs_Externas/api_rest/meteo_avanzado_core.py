#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Orquestación de meteo avanzado: heladas, nubosidad, nieblas, variables completas."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from zoneinfo import ZoneInfo

from api_rest.meteo_avanzado import (
    AnalizadorNubosidad,
    ModeloHeladaRadiativa,
    PredictorNiebla,
    calcular_punto_rocio,
    clasificar_velocidad_viento,
    indice_humedad_percibida,
)
from api_rest.meteo_avanzado.meteo_utils import ventilacion_vertical_indice
from api_rest.services import ESTACIONES_PRINCIPALES, pronostico_meteo, slug_a_nombre

TZ = ZoneInfo("America/Santiago")

COORDS_ESTACIONES: dict[str, dict[str, float]] = {
    "quillota": {"lat": -32.8833, "lon": -71.25, "altitud": 127},
    "los_nogales": {"lat": -32.9333, "lon": -71.2167, "altitud": 180},
    "hijuelas": {"lat": -32.8000, "lon": -71.1333, "altitud": 350},
    "limache": {"lat": -33.0167, "lon": -71.2667, "altitud": 120},
    "olmue": {"lat": -33.0000, "lon": -71.2167, "altitud": 145},
}

UMBRALES_HELADA_CULTIVO = {
    "palto": -2,
    "vid": -5,
    "citricos": -4,
    "tomate": -1,
    "lechuga": -2,
}


def validar_estacion(estacion_id: str) -> None:
    if estacion_id.lower() not in ESTACIONES_PRINCIPALES:
        raise ValueError(f"Estación no válida: {estacion_id}")


def obtener_estacion_meta(estacion_id: str) -> dict[str, Any]:
    validar_estacion(estacion_id)
    slug = estacion_id.lower()
    coords = COORDS_ESTACIONES.get(slug, COORDS_ESTACIONES["quillota"])
    return {
        "id": slug,
        "nombre": slug_a_nombre(slug),
        "latitud": coords["lat"],
        "longitud": coords["lon"],
        "altitud": coords.get("altitud", 145),
    }


def _num(d: dict, key: str, default: float) -> float:
    v = d.get(key)
    if v is None:
        return default
    try:
        return float(v)
    except (TypeError, ValueError):
        return default


def estimar_visibilidad_km(temp: float, hr: float, punto_rocio: float) -> float:
    diff = temp - punto_rocio
    if diff < 0.5 and hr > 92:
        return 0.2
    if diff < 1.5 and hr > 88:
        return 0.6
    if diff < 3 and hr > 80:
        return 1.2
    return min(10.0, 3.0 + diff * 1.8)


def _radiacion_wm2_desde_sum(radiacion_sum_mj: float | None) -> float:
    """Convierte shortwave_radiation_sum (MJ/m²/día) a W/m² promedio diurno ~12 h."""
    if radiacion_sum_mj is None:
        return 500.0
    return max(0.0, (float(radiacion_sum_mj) * 1e6) / (12 * 3600))


def pronostico_helada_avanzado(
    estacion_id: str, dias: int = 7, cultivo: str = "palto"
) -> dict[str, Any]:
    validar_estacion(estacion_id)
    estacion = obtener_estacion_meta(estacion_id)
    filas = pronostico_meteo(estacion_id, dias) or []
    modelo = ModeloHeladaRadiativa(estacion_id)
    heladas: list[dict[str, Any]] = []

    for row in filas[:dias]:
        fecha = datetime.fromisoformat(row["fecha"]).replace(tzinfo=TZ)
        temp_max = _num(row, "temperatura_max", 20)
        temp_min = _num(row, "temperatura_min", 10)
        cobertura = _num(row, "cobertura_nubosa", 50)
        viento = _num(row, "viento", 5)
        hr = _num(row, "humedad", 70)
        pr = calcular_punto_rocio(temp_min, hr)

        riesgo = modelo.calcular_riesgo_helada(
            temperatura_pronosticada=temp_max,
            temperatura_minima_pronosticada=temp_min,
            cobertura_nubosa=cobertura,
            velocidad_viento=viento,
            humedad_relativa=hr,
            punto_rocio=pr,
            fecha=fecha,
        )
        riesgo["cobertura_nubosa"] = round(cobertura, 1)
        riesgo["velocidad_viento"] = round(viento, 1)
        riesgo["humedad_relativa"] = round(hr, 1)
        umbral = UMBRALES_HELADA_CULTIVO.get(cultivo, -2)
        riesgo["umbral_cultivo"] = umbral
        riesgo["alerta_cultivo"] = temp_min <= umbral
        heladas.append(riesgo)

    return {
        "estacion_id": estacion_id,
        "estacion_nombre": estacion["nombre"],
        "cultivo": cultivo,
        "fecha_solicitud": datetime.now(TZ).isoformat(),
        "pronosticos_helada": heladas,
        "resumen": {
            "dias_con_riesgo": len([h for h in heladas if h["probabilidad_helada"] > 20]),
            "dias_riesgo_severo": len([h for h in heladas if h["riesgo_severo"]]),
            "dias_riesgo_moderado": len([h for h in heladas if h["riesgo_moderado"]]),
            "temperatura_minima_7d": min(
                (h["temperatura_minima_esperada"] for h in heladas), default=None
            ),
        },
    }


def analisis_nubosidad(estacion_id: str, dias: int = 7) -> dict[str, Any]:
    validar_estacion(estacion_id)
    estacion = obtener_estacion_meta(estacion_id)
    filas = pronostico_meteo(estacion_id, dias) or []
    analizador = AnalizadorNubosidad()
    datos: list[dict[str, Any]] = []

    for row in filas[:dias]:
        cobertura = _num(row, "cobertura_nubosa", 50)
        radiacion_bruta = _radiacion_wm2_desde_sum(row.get("radiacion_solar_sum"))
        temp_max = _num(row, "temperatura_max", 20)
        temp_min = _num(row, "temperatura_min", 10)

        rad = analizador.estimar_radiacion_solar(
            radiacion_bruta, cobertura, estacion["altitud"]
        )
        impacto = analizador.impacto_en_temperatura(cobertura, temp_max, temp_min)
        datos.append(
            {
                "fecha": row["fecha"],
                "cobertura": round(cobertura, 1),
                "cobertura_nubosa": round(cobertura, 1),
                "tipo_nube": analizador.clasificar_cobertura(cobertura).value,
                "radiacion": rad["radiacion_global_superficie"],
                "radiacion_global": rad["radiacion_global_superficie"],
                "radiacion_directa": rad["radiacion_directa"],
                "radiacion_difusa": rad["radiacion_difusa"],
                "impacto_temp_dia": impacto["efecto_dia"],
                "impacto_temp_noche": impacto["efecto_noche"],
                "temperatura_max_real": impacto["temperatura_dia_estimada"],
                "temperatura_min_real": impacto["temperatura_noche_estimada"],
            }
        )

    return {
        "estacion_id": estacion_id,
        "estacion_nombre": estacion["nombre"],
        "periodo": f"Próximos {dias} días",
        "datos": datos,
        "metadatos": {
            "fecha_solicitud": datetime.now(TZ).isoformat(),
            "altitud_estacion": estacion["altitud"],
            "fuente": "OpenMeteo + AnalizadorNubosidad",
        },
    }


def pronostico_niebla(estacion_id: str, dias: int = 7) -> dict[str, Any]:
    validar_estacion(estacion_id)
    estacion = obtener_estacion_meta(estacion_id)
    filas = pronostico_meteo(estacion_id, dias) or []
    predictor = PredictorNiebla(estacion_id, estacion["altitud"])
    pronosticos: list[dict[str, Any]] = []

    for row in filas[:dias]:
        temp = _num(row, "temperatura_min", 10)
        hr = _num(row, "humedad", 70)
        viento = _num(row, "viento", 5)
        cobertura = _num(row, "cobertura_nubosa", 50)
        vis_api = row.get("visibilidad_madrugada") or row.get("visibilidad")
        pr = calcular_punto_rocio(temp, hr)
        vis = (
            float(vis_api)
            if vis_api is not None
            else estimar_visibilidad_km(temp, hr, pr)
        )
        pronosticos.append(
            predictor.predecir_niebla(
                temperatura=temp,
                humedad_relativa=hr,
                visibilidad_pronosticada=vis,
                velocidad_viento=viento,
                punto_rocio=pr,
                hora_del_dia=4,
                cobertura_nubosa=cobertura,
                fecha_iso=row["fecha"],
            )
        )

    return {
        "estacion_id": estacion_id,
        "estacion_nombre": estacion["nombre"],
        "periodo": f"Próximos {dias} días",
        "pronosticos_niebla": pronosticos,
        "resumen": {
            "dias_con_niebla": len(
                [d for d in pronosticos if d["probabilidad_niebla"] > 20]
            ),
            "dias_niebla_densa": len(
                [d for d in pronosticos if d["severidad"] in ("densa", "muy_densa")]
            ),
            "visibilidad_minima": min(
                (d["visibilidad_esperada"] for d in pronosticos), default=None
            ),
        },
        "metadatos": {
            "fecha_solicitud": datetime.now(TZ).isoformat(),
            "altitud_estacion": estacion["altitud"],
            "fuente": "OpenMeteo + PredictorNiebla",
        },
    }


def variables_meteo_completas(estacion_id: str, dias: int = 7) -> dict[str, Any]:
    validar_estacion(estacion_id)
    estacion = obtener_estacion_meta(estacion_id)
    filas = pronostico_meteo(estacion_id, dias) or []
    analizador = AnalizadorNubosidad()
    datos: list[dict[str, Any]] = []

    for row in filas[:dias]:
        temp_max = _num(row, "temperatura_max", 20)
        temp_min = _num(row, "temperatura_min", 10)
        hr = _num(row, "humedad", 70)
        presion = _num(row, "presion", 1013)
        viento = _num(row, "viento", 5)
        precip = _num(row, "precipitacion", 0)
        cobertura = _num(row, "cobertura_nubosa", 50)
        radiacion_sum = row.get("radiacion_solar_sum")
        radiacion_teorica = _radiacion_wm2_desde_sum(radiacion_sum)
        pr = calcular_punto_rocio(temp_min, hr)
        vis = row.get("visibilidad")
        if vis is None:
            vis = estimar_visibilidad_km(temp_min, hr, pr)
        rad_real = analizador.estimar_radiacion_solar(
            radiacion_teorica, cobertura, estacion["altitud"]
        )["radiacion_global_superficie"]

        datos.append(
            {
                "fecha": row["fecha"],
                "temperatura": {
                    "maxima_celsius": round(temp_max, 1),
                    "minima_celsius": round(temp_min, 1),
                    "minima_absoluta": round(temp_min, 1),
                    "media_celsius": round((temp_max + temp_min) / 2, 1),
                    "punto_rocio_celsius": pr,
                    "humedad_percibida_celsius": indice_humedad_percibida(
                        temp_min, viento
                    ),
                },
                "humedad": {
                    "relativa_porcentaje": round(hr, 1),
                    "saturacion": "sí" if abs(temp_min - pr) < 1 else "no",
                },
                "presion": {"atmosferica_hpa": round(presion, 1)},
                "viento": {
                    "velocidad_ms": round(viento, 1),
                    "velocidad_kmh": round(viento * 3.6, 1),
                    "direccion_grados": row.get("direccion_viento"),
                    "categoria": clasificar_velocidad_viento(viento),
                },
                "precipitacion": {
                    "acumulado_24h_mm": round(precip, 1),
                    "probabilidad_porcentaje": row.get("pop"),
                },
                "radiacion_solar": {
                    "global_teorica_wm2": round(radiacion_teorica, 0),
                    "global_superficie_wm2": round(rad_real, 0),
                },
                "nubosidad": {
                    "cobertura_porcentaje": round(cobertura, 1),
                    "clasificacion": analizador.clasificar_cobertura(cobertura).value,
                },
                "visibilidad": {"horizontal_km": round(float(vis), 2)},
                "indices_agricolas": {
                    "riesgo_helada_radiativa": _riesgo_helada_simple(temp_min),
                    "riesgo_niebla": _riesgo_niebla_simple(hr, pr, temp_min),
                    "ventilacion_vertical": ventilacion_vertical_indice(
                        viento, cobertura
                    ),
                },
            }
        )

    return {
        "estacion_id": estacion_id,
        "estacion_nombre": estacion["nombre"],
        "ubicacion": estacion,
        "periodo": f"Próximos {dias} días",
        "datos": datos,
        "metadatos": {
            "variables_incluidas": 15,
            "fecha_solicitud": datetime.now(TZ).isoformat(),
            "fuente": "OpenMeteo + cálculos derivados",
        },
    }


def _riesgo_helada_simple(temp_min: float) -> str:
    if temp_min < -5:
        return "CRÍTICO"
    if temp_min < 0:
        return "ALTO"
    if temp_min < 5:
        return "MODERADO"
    return "BAJO"


def _riesgo_niebla_simple(hr: float, pr: float, temp: float) -> str:
    diff = temp - pr
    if diff < 0.5 and hr > 85:
        return "ALTO"
    if diff < 2 and hr > 75:
        return "MODERADO"
    return "BAJO"
