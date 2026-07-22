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


def calcular_bulbo_humedo(temperatura: float, humedad_relativa: float) -> float:
    """Temperatura de bulbo húmedo (°C) — aproximación Stull (2011).

    Representa el límite al que puede enfriarse el aire por evaporación.
    Útil en el método del psicrómetro al atardecer para helada radiativa.
    """
    t = float(temperatura)
    hr = max(1.0, min(100.0, float(humedad_relativa)))
    # Stull, R. (2011). Wet-Bulb Temperature from Relative Humidity and
    # Air Temperature. Journal of Applied Meteorology and Climatology.
    tw = (
        t * math.atan(0.151977 * (hr + 8.313659) ** 0.5)
        + math.atan(t + hr)
        - math.atan(hr - 1.676331)
        + 0.00391838 * (hr ** 1.5) * math.atan(0.023101 * hr)
        - 4.686035
    )
    # Tw no puede superar T ni quedar por debajo de Td
    td = calcular_punto_rocio(t, hr)
    return round(max(td, min(t, tw)), 1)


def estimar_temp_atardecer(temp_max: float, temp_min: float) -> float:
    """Proxy de T° al atardecer sin serie horaria (antes del ocaso).

    Usa ~55 % del rango diario desde el máximo: lectura típica de psicrómetro
    de campo cuando el Sol aún no se oculta por completo.
    """
    t_max = float(temp_max)
    t_min = float(temp_min)
    if t_max < t_min:
        t_max, t_min = t_min, t_max
    return round(t_max - 0.55 * (t_max - t_min), 1)


def evaluar_criterio_psicrometro(
    punto_rocio: float,
    bulbo_humedo: float,
    cobertura_nubosa: float,
    velocidad_viento: float,
) -> dict:
    """Criterio práctico de helada radiativa (psicrómetro al atardecer).

    - Td ≤ 0 °C + cielo despejado + calma → riesgo alto (escarcha).
    - Th ≤ 2 °C + cielo despejado → riesgo inminente (T° < 0 en madrugada).
    """
    cielo_despejado = cobertura_nubosa < 20
    calma = velocidad_viento < 3.0
    td_bajo = punto_rocio <= 0.0
    th_critico = bulbo_humedo <= 2.0

    riesgo_alto = td_bajo and cielo_despejado and calma
    riesgo_inminente = th_critico and cielo_despejado

    if riesgo_inminente and calma:
        nivel = "inminente"
        mensaje = (
            "Riesgo inminente: bulbo húmedo ≤ 2 °C al atardecer con cielo despejado; "
            "se espera temperatura bajo 0 °C en la madrugada."
        )
    elif riesgo_alto:
        nivel = "alto"
        mensaje = (
            "Riesgo alto: punto de rocío ≤ 0 °C con cielo despejado y viento en calma; "
            "condiciones favorables a escarcha."
        )
    elif th_critico or td_bajo:
        nivel = "vigilancia"
        mensaje = (
            "Vigilancia: Td o Th en umbral crítico, pero nubes o viento reducen "
            "la probabilidad de helada radiativa pura."
        )
    else:
        nivel = "bajo"
        mensaje = "Criterio psicrómetro sin señal de helada radiativa."

    return {
        "nivel": nivel,
        "riesgo_alto": riesgo_alto,
        "riesgo_inminente": riesgo_inminente,
        "cielo_despejado": cielo_despejado,
        "viento_calma": calma,
        "punto_rocio_bajo_cero": td_bajo,
        "bulbo_humedo_critico": th_critico,
        "mensaje": mensaje,
    }


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
