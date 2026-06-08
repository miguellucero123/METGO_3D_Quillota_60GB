#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Utilidades meteorológicas derivadas (punto rocío, wind chill)."""

from __future__ import annotations

import math


def calcular_punto_rocio(temperatura: float, humedad_relativa: float) -> float:
    """Punto de rocío (°C) — fórmula Magnus."""
    if humedad_relativa <= 0:
        return temperatura
    hr = max(1.0, min(100.0, humedad_relativa))
    a, b = 17.27, 237.7
    alpha = (a * temperatura) / (b + temperatura) + math.log(hr / 100.0)
    return round((b * alpha) / (a - alpha), 1)


def indice_humedad_percibida(temp: float, viento_ms: float) -> float:
    """Wind chill simplificado (°C) si T < 10 y viento > 1.3 m/s."""
    if temp >= 10 or viento_ms <= 1.3:
        return round(temp, 1)
    v_kmh = viento_ms * 3.6
    wc = (
        13.12
        + 0.6215 * temp
        - 11.37 * (v_kmh**0.16)
        + 0.3965 * temp * (v_kmh**0.16)
    )
    return round(wc, 1)


def clasificar_velocidad_viento(velocidad: float) -> str:
    if velocidad < 1:
        return "Calma"
    if velocidad < 6:
        return "Brisa ligera"
    if velocidad < 12:
        return "Brisa moderada"
    if velocidad < 20:
        return "Viento fresco"
    if velocidad < 29:
        return "Viento fuerte"
    return "Tormenta"


def ventilacion_vertical_indice(viento_ms: float, cobertura_nubosa: float) -> float:
    """Índice 0–10 de dispersión atmosférica (heurística)."""
    base = min(10.0, viento_ms * 1.2)
    if cobertura_nubosa > 80:
        base *= 0.6
    return round(max(0.0, min(10.0, base)), 1)
