#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Umbrales y factores de helada por cultivo (Valle de Aconcagua / Quillota).

Helada meteorológica: T° aire ≤ 0 °C.
Helada agrometeorológica: daño fisiológico con T° hasta ~3 °C según cultivo sensible.
Probabilidad boletín alerta temprana: baja ≤66 %, media 66–<90 %, alta ≥90 %.
"""

from __future__ import annotations

from typing import Any

# Umbrales T° mínima (°C) por cultivo — daño fisiológico / alerta
# critico ≤ T → daño alto; alto ≤ T → alerta; moderado ≤ T → vigilancia
UMBRALES_HELADA_CULTIVO: dict[str, dict[str, Any]] = {
    "lechuga": {
        "nombre": "Lechuga",
        "sensibilidad": "muy_alta",
        "critico": 3.0,
        "alto": 5.0,
        "moderado": 7.0,
        "descripcion": "Cultivo sensible: daño fisiológico posible hasta ~3 °C (helada agrometeorológica).",
    },
    "tomate": {
        "nombre": "Tomate",
        "sensibilidad": "muy_alta",
        "critico": 2.0,
        "alto": 4.0,
        "moderado": 6.0,
        "descripcion": "Muy sensible: daño floral/vegetativo bajo umbrales positivos.",
    },
    "palto": {
        "nombre": "Palto",
        "sensibilidad": "alta",
        "critico": 0.0,
        "alto": 2.0,
        "moderado": 4.0,
        "descripcion": "Daño crítico desde 0 °C; flores y brotes sensibles a 0–2 °C.",
    },
    "citricos": {
        "nombre": "Cítricos",
        "sensibilidad": "media",
        "critico": -1.0,
        "alto": 1.5,
        "moderado": 4.0,
        "descripcion": "Fruto tolera levemente bajo 0 °C; flores más sensibles cerca de 0–1.5 °C.",
    },
    "vid": {
        "nombre": "Vid",
        "sensibilidad": "media_baja",
        "critico": -2.0,
        "alto": 0.0,
        "moderado": 3.0,
        "descripcion": "Yemas latentes más resistentes; tejido verde dañado cerca o bajo 0 °C.",
    },
}

# Helada meteorológica (definición climática, independiente del cultivo)
UMBRAL_HELADA_METEOROLOGICA_C = 0.0

# Clasificación probabilidad — boletines de alerta temprana
POP_BAJA_MAX = 66.0
POP_ALTA_MIN = 90.0

# Altitudes de referencia Valle Aconcagua (m s.n.m.) — acumulación aire frío
# Fondos de valle / oquedad: menor altitud → mayor riesgo radiativo local
ALTITUD_OQUEDAD_ALTA_M = 150.0
ALTITUD_OQUEDAD_MEDIA_M = 220.0


def obtener_umbrales_cultivo(cultivo: str) -> dict[str, Any]:
    key = (cultivo or "palto").lower().strip()
    return dict(UMBRALES_HELADA_CULTIVO.get(key, UMBRALES_HELADA_CULTIVO["palto"]))


def clasificar_probabilidad_boletin(probabilidad: float) -> str:
    """Baja ≤66 %, media 66–<90 %, alta ≥90 %."""
    p = float(probabilidad)
    if p >= POP_ALTA_MIN:
        return "alta"
    if p > POP_BAJA_MAX:
        return "media"
    return "baja"


def clasificar_dano_cultivo(temp_min: float, cultivo: str) -> dict[str, Any]:
    """Evalúa helada meteorológica vs agrometeorológica según umbrales del cultivo."""
    umb = obtener_umbrales_cultivo(cultivo)
    t = float(temp_min)
    helada_meteo = t <= UMBRAL_HELADA_METEOROLOGICA_C

    if t <= umb["critico"]:
        severidad = "critico"
    elif t <= umb["alto"]:
        severidad = "alto"
    elif t <= umb["moderado"]:
        severidad = "moderado"
    else:
        severidad = "bajo"

    tipo = "sin_helada"
    if helada_meteo:
        tipo = "meteorologica"
    elif severidad in ("critico", "alto", "moderado"):
        tipo = "agrometeorologica"

    return {
        "cultivo": (cultivo or "palto").lower(),
        "cultivo_nombre": umb["nombre"],
        "sensibilidad": umb["sensibilidad"],
        "temperatura_minima": round(t, 1),
        "umbrales": {
            "critico": umb["critico"],
            "alto": umb["alto"],
            "moderado": umb["moderado"],
            "helada_meteorologica": UMBRAL_HELADA_METEOROLOGICA_C,
        },
        "severidad_cultivo": severidad,
        "tipo_helada": tipo,
        "helada_meteorologica": helada_meteo,
        "alerta_cultivo": severidad in ("critico", "alto"),
        "descripcion_umbral": umb["descripcion"],
    }


def factor_oquedad_relieve(altitud_m: float | None) -> dict[str, Any]:
    """Efecto de oquedad / fondo de valle (acumulación de aire frío).

    El biombo climático del Aconcagua resguarda de la influencia marina directa
    pero acumula aire frío en sectores bajos.
    """
    if altitud_m is None:
        return {
            "score": 0.5,
            "nivel": "desconocido",
            "altitud_m": None,
            "mensaje": "Sin altitud de estación; factor oquedad neutro.",
        }
    alt = float(altitud_m)
    if alt <= ALTITUD_OQUEDAD_ALTA_M:
        score, nivel = 1.0, "alto"
        msg = (
            f"Fondo de valle / oquedad ({alt:.0f} m): alta acumulación de aire frío "
            "por irradiación nocturna."
        )
    elif alt <= ALTITUD_OQUEDAD_MEDIA_M:
        score, nivel = 0.65, "medio"
        msg = (
            f"Relieve intermedio ({alt:.0f} m): acumulación moderada de aire frío."
        )
    else:
        score, nivel = 0.25, "bajo"
        msg = (
            f"Mayor altitud relativa ({alt:.0f} m): menor acumulación de aire frío "
            "que en fondos de valle."
        )
    return {
        "score": score,
        "nivel": nivel,
        "altitud_m": round(alt, 0),
        "mensaje": msg,
    }


def factor_humedad_suelo(
    humedad_suelo_pct: float | None = None,
    precip_reciente_mm: float | None = None,
    suelo_descubierto: bool | None = None,
) -> dict[str, Any]:
    """Suelos secos o descubiertos reducen inercia térmica → caída más rápida de T° superficial.

    Si no hay sensor, se estima con precipitación reciente (proxy).
    """
    fuente = "default"
    hs: float | None = None

    if humedad_suelo_pct is not None:
        hs = max(0.0, min(100.0, float(humedad_suelo_pct)))
        fuente = "sensor_o_parametro"
    elif precip_reciente_mm is not None:
        # Proxy: <2 mm recientes → seco; 2–10 → medio; >10 → húmedo
        p = max(0.0, float(precip_reciente_mm))
        if p < 2:
            hs = 25.0
        elif p < 10:
            hs = 50.0
        else:
            hs = 75.0
        fuente = "proxy_precipitacion"

    if hs is None:
        hs = 50.0
        fuente = "default_neutro"

    # Score de riesgo: suelo más seco → score más alto
    if hs < 25:
        score, nivel = 1.0, "seco"
    elif hs < 40:
        score, nivel = 0.75, "algo_seco"
    elif hs < 60:
        score, nivel = 0.4, "medio"
    else:
        score, nivel = 0.15, "humedo"

    descubierto = bool(suelo_descubierto) if suelo_descubierto is not None else False
    if descubierto:
        score = min(1.0, score + 0.2)
        nivel = f"{nivel}_descubierto"

    return {
        "score": round(score, 2),
        "nivel": nivel,
        "humedad_suelo_pct": round(hs, 1),
        "suelo_descubierto": descubierto,
        "fuente": fuente,
        "mensaje": (
            f"Humedad de suelo {hs:.0f}% ({nivel}): "
            + (
                "baja inercia térmica, acelera caída de T° superficial."
                if score >= 0.6
                else "inercia térmica moderada o favorable."
            )
        ),
    }


def evaluar_condiciones_atmosfericas_noche(
    cobertura_nubosa: float,
    velocidad_viento: float,
    humedad_relativa: float,
) -> dict[str, Any]:
    """Cielo despejado + calma + baja HR nocturna → pérdida rápida de calor por irradiación."""
    cielo = cobertura_nubosa < 20
    calma = velocidad_viento < 3.0
    baja_hr = humedad_relativa < 60

    score = 0.0
    if cielo:
        score += 0.4
    elif cobertura_nubosa < 40:
        score += 0.2
    if calma:
        score += 0.35
    elif velocidad_viento < 5:
        score += 0.15
    if baja_hr:
        score += 0.25
    elif humedad_relativa < 75:
        score += 0.1

    return {
        "score": round(min(1.0, score), 2),
        "cielo_despejado": cielo,
        "viento_calma": calma,
        "baja_humedad_nocturna": baja_hr,
        "favorables_irradiacion": cielo and calma and baja_hr,
        "mensaje": (
            "Condiciones nocturnas favorables a irradiación (despejado, calma, baja HR)."
            if cielo and calma and baja_hr
            else "Condiciones atmosféricas parciales o desfavorables a helada radiativa pura."
        ),
    }
