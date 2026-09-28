#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Alerta de helada por predio (producto comercial "Heladas METGO 3D").

Cada tarde se calcula, para las coordenadas propias de cada predio (no la
estación más cercana), la noche que viene:

- Tmín prevista = mínimo de la media del ensamble real ECMWF/ICON/GFS
  (``openmeteo_multimodelo``) entre las 18:00 y las 09:00 locales, más el
  ajuste de calibración local del predio (``ajuste_tmin_c``).
- Hora más fría = hora local de ese mínimo (no un valor fijo).
- Probabilidades P(Tmín ≤ 0 °C) y P(Tmín ≤ umbral de acción del cultivo):
  aproximación normal con σ = √(dispersión_entre_modelos² + σ_base²).
  σ_base (1.5 °C por defecto) representa el error típico de Tmín de un NWP a
  ~1 día en fondos de valle; se ajusta por predio con la validación en
  terreno (``validar_contra_observado``). Es una heurística documentada, no un
  sistema de ensamble calibrado.
- Criterio del psicrómetro al atardecer y factores de irradiación reutilizan
  ``ModeloHeladaRadiativa`` (misma lógica que el módulo /meteo/avanzado).

Es un pronóstico, no una garantía: el mensaje siempre lo dice.
"""

from __future__ import annotations

import math
import statistics
from datetime import datetime, timedelta, timezone
from typing import Any
from urllib.parse import quote
from zoneinfo import ZoneInfo

from api_rest.integracion.openmeteo_multimodelo import (
    MODELOS_DETERMINISTAS,
    ensamble_variable,
    fetch_multimodelo,
)
from api_rest.meteo_avanzado import ModeloHeladaRadiativa, obtener_umbrales_cultivo
from api_rest.meteo_avanzado.meteo_utils import calcular_bulbo_humedo

TZ = ZoneInfo("America/Santiago")

HOURLY_VARS = [
    "temperature_2m",
    "dew_point_2m",
    "relative_humidity_2m",
    "cloud_cover",
    "wind_speed_10m",
]

SIGMA_BASE_C = 1.5
HORA_INICIO_NOCHE = 18
HORA_FIN_NOCHE = 9
HORA_ATARDECER = 20  # lectura de psicrómetro ~ tras la puesta de sol (primavera, horario verano)

# Umbrales de decisión sobre P(Tmín ≤ umbral de acción)
P_ROJO = 50.0
P_AMARILLO = 20.0

NIVELES = {"verde": 0, "amarillo": 1, "rojo": 2}


class PronosticoNoDisponibleError(RuntimeError):
    """No hubo datos reales suficientes: no se debe enviar mensaje al cliente."""


def _prob_bajo(umbral: float, media: float, sigma: float) -> float:
    """P(X ≤ umbral) para X ~ N(media, sigma), en %."""
    if sigma <= 0:
        return 100.0 if media <= umbral else 0.0
    z = (umbral - media) / (sigma * math.sqrt(2))
    return round(50.0 * (1.0 + math.erf(z)), 1)


def _parse_times_local(times: list[str]) -> list[datetime]:
    return [
        datetime.fromisoformat(t).replace(tzinfo=timezone.utc).astimezone(TZ) for t in times
    ]


def ventana_noche(ahora: datetime) -> tuple[datetime, datetime]:
    """Noche a pronosticar: si aún no son las 09:00, la noche en curso; si no, la de hoy."""
    local = ahora.astimezone(TZ)
    base = local.date() if local.hour >= HORA_FIN_NOCHE else local.date() - timedelta(days=1)
    inicio = datetime(base.year, base.month, base.day, HORA_INICIO_NOCHE, tzinfo=TZ)
    fin = inicio + timedelta(hours=24 - HORA_INICIO_NOCHE + HORA_FIN_NOCHE)
    return inicio, fin


def umbral_accion_predio(predio: dict[str, Any]) -> float:
    """Umbral para 'prende control': el del predio, o el nivel 'alto' del cultivo."""
    if predio.get("umbral_accion_c") is not None:
        return float(predio["umbral_accion_c"])
    return float(obtener_umbrales_cultivo(predio.get("cultivo") or "palto")["alto"])


def _media(vals: list[float | None]) -> float | None:
    v = [x for x in vals if x is not None]
    return sum(v) / len(v) if v else None


def evaluar_noche(
    predio: dict[str, Any],
    hourly: dict[str, Any],
    ahora: datetime,
    modelos: list[str] | None = None,
) -> dict[str, Any]:
    """Cálculo puro (sin red) del riesgo de helada de la noche para un predio."""
    modelos = modelos or MODELOS_DETERMINISTAS
    ajuste = float(predio.get("ajuste_tmin_c") or 0.0)
    sigma_base = float(predio.get("sigma_c") or SIGMA_BASE_C)
    cultivo = (predio.get("cultivo") or "palto").lower()
    umb_cultivo = obtener_umbrales_cultivo(cultivo)
    umbral_accion = umbral_accion_predio(predio)

    tiempos = _parse_times_local(hourly.get("time") or [])
    inicio, fin = ventana_noche(ahora)
    idx_noche = [i for i, t in enumerate(tiempos) if inicio <= t <= fin]
    if len(idx_noche) < 10:
        raise PronosticoNoDisponibleError("pronóstico sin cobertura horaria de la noche")

    temp = ensamble_variable(hourly, "temperature_2m", modelos)
    if temp["n_modelos"] == 0:
        raise PronosticoNoDisponibleError("sin temperatura de ningún modelo")
    media = temp["media"]
    spread = temp["spread"]

    validos = [i for i in idx_noche if media[i] is not None]
    if not validos:
        raise PronosticoNoDisponibleError("temperatura nula en toda la noche")
    i_min = min(validos, key=lambda i: media[i])
    tmin = media[i_min] + ajuste
    sigma = math.sqrt((spread[i_min] or 0.0) ** 2 + sigma_base**2)

    tmin_por_modelo: dict[str, float] = {}
    for modelo, serie in temp["modelos"].items():
        vals = [serie[i] for i in idx_noche if i < len(serie) and serie[i] is not None]
        if vals:
            tmin_por_modelo[modelo] = round(min(vals) + ajuste, 1)

    # Primera hora en que la media cruza el umbral de acción (hora sugerida de encendido)
    hora_accion = next(
        (tiempos[i] for i in validos if media[i] + ajuste <= umbral_accion), None
    )

    def _serie_media(var: str) -> list[float | None]:
        return ensamble_variable(hourly, var, modelos)["media"]

    nubes = _serie_media("cloud_cover")
    viento = _serie_media("wind_speed_10m")
    hr = _serie_media("relative_humidity_2m")
    td = _serie_media("dew_point_2m")

    madrugada = [i for i in idx_noche if tiempos[i].hour <= 6 and tiempos[i] > inicio]
    nubes_noche = _media([nubes[i] for i in madrugada]) if nubes else None
    viento_noche = _media([viento[i] for i in madrugada]) if viento else None
    hr_noche = _media([hr[i] for i in madrugada]) if hr else None

    i_atardecer = next(
        (i for i in idx_noche if tiempos[i].hour == HORA_ATARDECER), idx_noche[0]
    )
    t_atardecer = media[i_atardecer]
    hr_atardecer = hr[i_atardecer] if hr else None
    td_atardecer = td[i_atardecer] if td else None
    tarde = [
        i
        for i, t in enumerate(tiempos)
        if t.date() == inicio.date() and 12 <= t.hour <= 18 and media[i] is not None
    ]
    tmax = max((media[i] for i in tarde), default=t_atardecer)

    radiativo: dict[str, Any] = {}
    if None not in (t_atardecer, hr_atardecer, nubes_noche, viento_noche, hr_noche):
        th = calcular_bulbo_humedo(t_atardecer, hr_atardecer)
        radiativo = ModeloHeladaRadiativa(
            predio.get("id") or "predio", altitud_m=predio.get("altitud_m")
        ).calcular_riesgo_helada(
            temperatura_pronosticada=tmax,
            temperatura_minima_pronosticada=tmin,
            cobertura_nubosa=nubes_noche,
            velocidad_viento=viento_noche,
            humedad_relativa=hr_noche,
            punto_rocio=td_atardecer,
            fecha=inicio,
            temperatura_atardecer=t_atardecer,
            bulbo_humedo=th,
            cultivo=cultivo,
        )
    criterio = radiativo.get("criterio_psicrometro") or {}

    p_helada = _prob_bajo(0.0, tmin, sigma)
    p_accion = _prob_bajo(umbral_accion, tmin, sigma)
    p_dano = _prob_bajo(float(umb_cultivo["critico"]), tmin, sigma)

    if p_accion >= P_ROJO or (criterio.get("riesgo_inminente") and p_accion >= P_AMARILLO):
        nivel = "rojo"
    elif p_accion >= P_AMARILLO or criterio.get("riesgo_alto"):
        nivel = "amarillo"
    else:
        nivel = "verde"

    return {
        "predio_id": predio.get("id"),
        "predio_nombre": predio.get("nombre") or predio.get("id"),
        "cultivo": cultivo,
        "cultivo_nombre": umb_cultivo["nombre"],
        "noche_inicio": inicio.isoformat(),
        "noche_fin": fin.isoformat(),
        "emitido": ahora.astimezone(TZ).isoformat(timespec="minutes"),
        "tmin_c": round(tmin, 1),
        "tmin_rango_c": [round(tmin - sigma, 1), round(tmin + sigma, 1)],
        "sigma_c": round(sigma, 2),
        "spread_modelos_c": round(spread[i_min] or 0.0, 2),
        "tmin_por_modelo_c": tmin_por_modelo,
        "n_modelos": temp["n_modelos"],
        "hora_min": tiempos[i_min].strftime("%H:%M"),
        "hora_accion": hora_accion.strftime("%H:%M") if hora_accion else None,
        "umbral_accion_c": umbral_accion,
        "umbral_dano_c": float(umb_cultivo["critico"]),
        "ajuste_tmin_c": ajuste,
        "prob_helada_pct": p_helada,
        "prob_accion_pct": p_accion,
        "prob_dano_pct": p_dano,
        "nivel": nivel,
        "nubosidad_noche_pct": round(nubes_noche, 0) if nubes_noche is not None else None,
        "viento_noche_ms": round(viento_noche, 1) if viento_noche is not None else None,
        "criterio_psicrometro": criterio.get("nivel"),
        "factores": radiativo.get("factores_contribuyentes") or [],
        "fuente": f"Open-Meteo ensamble {'/'.join(temp['modelos'].keys())}",
    }


def pronostico_predio(predio: dict[str, Any], ahora: datetime | None = None) -> dict[str, Any]:
    """Descarga el multi-modelo real para el predio y evalúa la noche."""
    ahora = ahora or datetime.now(TZ)
    hourly = fetch_multimodelo(
        float(predio["lat"]),
        float(predio["lon"]),
        hourly_vars=HOURLY_VARS,
        forecast_days=3,
        past_days=1,
    ).get("hourly") or {}
    return evaluar_noche(predio, hourly, ahora)


# ---------------------------------------------------------------------------
# Mensajes
# ---------------------------------------------------------------------------

_DIAS = ["lun", "mar", "mié", "jue", "vie", "sáb", "dom"]


def _fecha_corta(iso: str) -> str:
    d = datetime.fromisoformat(iso)
    return f"{_DIAS[d.weekday()]} {d.day:02d}/{d.month:02d}"


def _fmt(v: float) -> str:
    return f"{v:.1f}".replace(".", ",")


def recomendacion(r: dict[str, Any]) -> str:
    umbral = _fmt(r["umbral_accion_c"])
    if r["nivel"] == "rojo":
        hora = f", probablemente cerca de las {r['hora_accion']}" if r.get("hora_accion") else ""
        return (
            "🔴 PRENDE CONTROL. Deja listo tu sistema (hélices, aspersión o calefactores) "
            f"y enciéndelo cuando tu termómetro de referencia marque {umbral} °C{hora}."
        )
    if r["nivel"] == "amarillo":
        return (
            "🟡 ATENTO. Deja el sistema listo y revisa el termómetro desde la medianoche. "
            "Si el riesgo sube en la noche, te avisamos."
        )
    return f"🟢 TRANQUILO. No se esperan temperaturas de daño para {r['cultivo_nombre'].lower()}."


def mensaje_whatsapp(r: dict[str, Any], *, actualizacion: bool = False) -> str:
    lo, hi = r["tmin_rango_c"]
    cab = "⚠️ ACTUALIZACIÓN NOCTURNA\n" if actualizacion else ""
    return (
        f"{cab}🌡️ METGO 3D · Heladas — {r['predio_nombre']}\n"
        f"Noche del {_fecha_corta(r['noche_inicio'])}\n\n"
        f"Mínima prevista: {_fmt(r['tmin_c'])} °C (entre {_fmt(lo)} y {_fmt(hi)})\n"
        f"Hora más fría: ~{r['hora_min']}\n"
        f"Probabilidad de helada (≤ 0 °C): {r['prob_helada_pct']:.0f} %\n"
        f"Probabilidad de bajar de {_fmt(r['umbral_accion_c'])} °C "
        f"({r['cultivo_nombre'].lower()}): {r['prob_accion_pct']:.0f} %\n\n"
        f"{recomendacion(r)}\n\n"
        "Es un pronóstico, no una garantía: confirma siempre con tu termómetro en terreno.\n"
        "— METGO 3D"
    )


def link_whatsapp(telefono: str | None, texto: str) -> str | None:
    """Enlace wa.me con el texto precargado (envío manual en un clic)."""
    if not telefono:
        return None
    numero = "".join(ch for ch in str(telefono) if ch.isdigit())
    if not numero:
        return None
    return f"https://wa.me/{numero}?text={quote(texto)}"


def debe_escalar(anterior: dict[str, Any] | None, actual: dict[str, Any]) -> bool:
    """Alerta nocturna extra: sube el nivel o la mínima cae ≥ 1.5 °C respecto de la tarde."""
    if not anterior:
        return actual["nivel"] != "verde"
    if NIVELES[actual["nivel"]] > NIVELES.get(anterior.get("nivel", "verde"), 0):
        return True
    return actual["nivel"] != "verde" and (
        float(anterior.get("tmin_c", 99)) - actual["tmin_c"] >= 1.5
    )


# ---------------------------------------------------------------------------
# Validación en terreno (semana 2: afinar umbral y calibración)
# ---------------------------------------------------------------------------


def validar_contra_observado(
    pares: list[tuple[float, float]], ajuste_actual: float = 0.0
) -> dict[str, Any]:
    """Compara (tmin_pronosticada, tmin_observada) de un predio.

    Devuelve sesgo, MAE y el ajuste sugerido (ajuste_actual + sesgo medio) —
    solo se recomienda aplicarlo con ≥ 3 noches observadas.
    """
    if not pares:
        return {"n": 0}
    errores = [obs - pred for pred, obs in pares]
    sesgo = statistics.fmean(errores)
    return {
        "n": len(pares),
        "sesgo_c": round(sesgo, 2),
        "mae_c": round(statistics.fmean(abs(e) for e in errores), 2),
        "desv_error_c": round(statistics.pstdev(errores), 2) if len(errores) > 1 else None,
        "ajuste_sugerido_c": round(ajuste_actual + sesgo, 1),
        "aplicar": len(pares) >= 3,
    }
