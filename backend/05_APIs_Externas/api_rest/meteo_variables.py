#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Catálogo de variables meteorológicas METGO 3D (base + extensiones agrícolas)."""

from __future__ import annotations

VARIABLES_ACTUALES: dict[str, dict] = {
    "temperatura_maxima": {"unidad": "°C", "rango": [0, 45], "agrícola": True},
    "temperatura_minima": {"unidad": "°C", "rango": [-5, 30], "agrícola": True},
    "humedad_relativa": {"unidad": "%", "rango": [0, 100], "agrícola": True},
    "presion_atmosferica": {"unidad": "hPa", "rango": [980, 1040], "agrícola": False},
    "velocidad_viento": {"unidad": "m/s", "rango": [0, 25], "agrícola": True},
    "direccion_viento": {"unidad": "°", "rango": [0, 360], "agrícola": False},
    "precipitacion": {"unidad": "mm", "rango": [0, 150], "agrícola": True},
}

VARIABLES_NUEVAS: dict[str, dict] = {
    "temperatura_minima_absoluta": {
        "unidad": "°C",
        "rango": [-20, 15],
        "descripcion": "T° mínima esperada en 24 h",
        "fuente": "OpenMeteo daily",
        "agrícola": True,
    },
    "riesgo_helada_radiativa": {
        "unidad": "%",
        "rango": [0, 100],
        "descripcion": "Probabilidad helada radiativa (modelo local)",
        "agrícola": True,
    },
    "cobertura_nubosa": {
        "unidad": "%",
        "rango": [0, 100],
        "descripcion": "Cobertura nubosa media diaria",
        "fuente": "OpenMeteo cloud_cover_mean",
        "agrícola": True,
    },
    "radiacion_solar_global": {
        "unidad": "W/m²",
        "rango": [0, 1000],
        "descripcion": "Radiación solar en superficie",
        "fuente": "OpenMeteo shortwave_radiation_sum",
        "agrícola": True,
    },
    "visibilidad": {
        "unidad": "km",
        "rango": [0, 10],
        "descripcion": "Visibilidad horizontal mínima diaria",
        "fuente": "OpenMeteo hourly visibility",
        "agrícola": True,
    },
    "punto_rocio": {
        "unidad": "°C",
        "rango": [-10, 25],
        "descripcion": "Calculado Magnus (T° + HR)",
        "agrícola": True,
    },
    "indice_humedad_percibida": {
        "unidad": "°C",
        "rango": [-30, 50],
        "descripcion": "Wind chill simplificado",
        "agrícola": False,
    },
    "ventilacion_vertical": {
        "unidad": "índice 0-10",
        "rango": [0, 10],
        "descripcion": "Dispersión atmosférica (viento + nubes)",
        "agrícola": True,
    },
}


def catalogo_variables() -> dict:
    return {
        "variables_actuales": VARIABLES_ACTUALES,
        "variables_nuevas": VARIABLES_NUEVAS,
        "total": len(VARIABLES_ACTUALES) + len(VARIABLES_NUEVAS),
    }
