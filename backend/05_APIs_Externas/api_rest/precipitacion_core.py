#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pronóstico de precipitación calibrado, alertas agrícolas y heladas."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any
from zoneinfo import ZoneInfo

TZ = ZoneInfo("America/Santiago")

# Umbrales de precipitación por cultivo (mm/24h y mm/48h)
UMBRALES_PRECIP_CULTIVO: dict[str, dict[str, float]] = {
    "palto": {"lluvia_24h_rojo": 25.0, "lluvia_48h_rojo": 50.0, "intensidad_rojo": 5.0},
    "vid": {"lluvia_24h_rojo": 20.0, "lluvia_48h_rojo": 40.0, "intensidad_rojo": 4.0},
    "citricos": {"lluvia_24h_rojo": 22.0, "lluvia_48h_rojo": 45.0, "intensidad_rojo": 4.5},
    "tomate": {"lluvia_24h_rojo": 18.0, "lluvia_48h_rojo": 35.0, "intensidad_rojo": 3.5},
    "lechuga": {"lluvia_24h_rojo": 15.0, "lluvia_48h_rojo": 30.0, "intensidad_rojo": 3.0},
}

# Umbrales helada por cultivo (°C mínima pronosticada)
UMBRALES_HELADA_CULTIVO: dict[str, dict[str, float]] = {
    "palto": {"critico": 0.0, "alto": 2.0, "moderado": 5.0},
    "vid": {"critico": -1.0, "alto": 1.0, "moderado": 4.0},
    "citricos": {"critico": 0.0, "alto": 2.5, "moderado": 5.0},
    "tomate": {"critico": 2.0, "alto": 4.0, "moderado": 6.0},
    "lechuga": {"critico": 3.0, "alto": 5.0, "moderado": 7.0},
}

CULTIVOS_DEFAULT = list(UMBRALES_PRECIP_CULTIVO.keys())


def clasificar_intensidad(mm: float) -> str:
    if mm <= 0.1:
        return "sin_lluvia"
    if mm < 2:
        return "ligera"
    if mm < 10:
        return "moderada"
    if mm < 25:
        return "fuerte"
    return "extrema"


def intensidad_mm_h(precip_dia: float) -> float:
    """Estimación mm/h asumiendo concentración en ~6 h de lluvia."""
    if precip_dia <= 0:
        return 0.0
    return round(precip_dia / 6.0, 2)


def intensidad_mm_h_ventana(precip_3h: float) -> float:
    """Intensidad media en ventana de 3 h."""
    if precip_3h <= 0:
        return 0.0
    return round(precip_3h / 3.0, 2)


def severidad_precip(mm: float) -> str:
    if mm > 40:
        return "morado"
    if mm > 25:
        return "rojo"
    if mm > 10:
        return "naranja"
    if mm > 2:
        return "amarillo"
    return "verde"


def severidad_helada(t_min: float, cultivo: str = "palto") -> str:
    umb = UMBRALES_HELADA_CULTIVO.get(cultivo, UMBRALES_HELADA_CULTIVO["palto"])
    if t_min <= umb["critico"]:
        return "critico"
    if t_min <= umb["alto"]:
        return "alto"
    if t_min <= umb["moderado"]:
        return "moderado"
    return "bajo"


def _calcular_bias(estacion_id: str, pronostico_fn, historico_fn) -> float:
    """Factor multiplicativo histórico (obs/pred) en días con lluvia pronosticada."""
    hist = historico_fn(estacion_id, 90) or []
    pron = pronostico_fn(estacion_id, 14) or []
    if not hist:
        return 0.92
    ratios: list[float] = []
    hist_map = {str(h.get("fecha", ""))[:10]: h for h in hist}
    for p in pron:
        dia = str(p.get("fecha", ""))[:10]
        if dia not in hist_map:
            continue
        pred = float(p.get("precipitacion") or 0)
        obs = float(hist_map[dia].get("precipitacion") or 0)
        if pred >= 0.5:
            ratios.append(obs / pred if pred > 0 else 1.0)
    if len(ratios) >= 5:
        ratios.sort()
        return max(0.5, min(1.5, ratios[len(ratios) // 2]))
    return 0.92


def pronostico_precipitacion_bruto(
    estacion_id: str,
    dias: int,
    pronostico_fn,
    slug_a_nombre_fn,
) -> dict[str, Any] | None:
    filas = pronostico_fn(estacion_id, dias)
    if not filas:
        return None
    fechas = []
    precip = []
    pop = []
    intensidad = []
    for r in filas:
        fechas.append(r["fecha"])
        p = float(r.get("precipitacion") or 0)
        precip.append(round(p, 2))
        pop.append(round(float(r.get("probabilidad_lluvia") or r.get("pop") or 0), 0))
        intensidad.append(intensidad_mm_h(p))
    return {
        "estacion_id": estacion_id,
        "estacion_nombre": slug_a_nombre_fn(estacion_id),
        "fechas": fechas,
        "datos": {
            "precipitacion": precip,
            "pop": pop,
            "intensidad": intensidad,
            "intensidad_clase": [clasificar_intensidad(p) for p in precip],
        },
        "metadatos": {
            "calibrado": False,
            "fuente": "openmeteo",
            "modelos": ["gfs"],
            "fecha_solicitud": datetime.now(TZ).isoformat(),
        },
    }


def pronostico_precipitacion_3h_bruto(
    estacion_id: str,
    dias: int,
    precip_3h_fn,
    slug_a_nombre_fn,
) -> dict[str, Any] | None:
    raw = precip_3h_fn(estacion_id, dias)
    if not raw or not raw.get("fechas"):
        return None
    precip = [float(p) for p in raw.get("precipitacion") or []]
    pop = [float(p) for p in raw.get("pop") or []]
    intensidad = [intensidad_mm_h_ventana(p) for p in precip]
    return {
        "estacion_id": estacion_id,
        "estacion_nombre": slug_a_nombre_fn(estacion_id),
        "resolucion": "3h",
        "fechas": raw["fechas"],
        "datos": {
            "precipitacion": [round(p, 2) for p in precip],
            "pop": [round(p, 0) for p in pop],
            "intensidad": intensidad,
            "intensidad_clase": [clasificar_intensidad(p) for p in precip],
        },
        "metadatos": {
            "calibrado": False,
            "fuente": raw.get("fuente_datos", "openmeteo_hourly_3h"),
            "modelos": ["gfs"],
            "intervalo_horas": 3,
            "fecha_solicitud": datetime.now(TZ).isoformat(),
        },
    }


def pronostico_precipitacion_3h_calibrado(
    estacion_id: str,
    dias: int,
    precip_3h_fn,
    pronostico_diario_fn,
    historico_fn,
    slug_a_nombre_fn,
) -> dict[str, Any] | None:
    bruto = pronostico_precipitacion_3h_bruto(
        estacion_id, dias, precip_3h_fn, slug_a_nombre_fn
    )
    if not bruto:
        return None
    bias = _calcular_bias(estacion_id, pronostico_diario_fn, historico_fn)
    precip_raw = bruto["datos"]["precipitacion"]
    calibrada = [round(max(0.0, p * bias), 2) for p in precip_raw]
    p10 = [round(max(0.0, c * 0.75), 2) for c in calibrada]
    p90 = [round(c * 1.3, 2) for c in calibrada]
    alerta_lluvia_fuerte = any(p >= 12 for p in calibrada[:8])
    return {
        **bruto,
        "precipitacion_calibrada": calibrada,
        "precipitacion_p10": p10,
        "precipitacion_p50": calibrada,
        "precipitacion_p90": p90,
        "pop": bruto["datos"]["pop"],
        "intensidad": bruto["datos"]["intensidad"],
        "incertidumbre": {
            "desvio_estandar": [
                round((hi - lo) / 3.92, 2) for lo, hi in zip(p10, p90)
            ],
            "intervalo_confianza_90": [
                {"bajo": lo, "alto": hi} for lo, hi in zip(p10, p90)
            ],
        },
        "metodo_calibracion": "bias_historico_local",
        "factor_bias": round(bias, 3),
        "alerta_lluvia_fuerte": alerta_lluvia_fuerte,
        "metadatos": {
            **bruto["metadatos"],
            "calibrado": True,
            "tipo_dato": "pronostico_calibrado_3h",
        },
    }


def pronostico_precipitacion_calibrado(
    estacion_id: str,
    dias: int,
    pronostico_fn,
    historico_fn,
    slug_a_nombre_fn,
) -> dict[str, Any] | None:
    bruto = pronostico_precipitacion_bruto(
        estacion_id, dias, pronostico_fn, slug_a_nombre_fn
    )
    if not bruto:
        return None
    bias = _calcular_bias(estacion_id, pronostico_fn, historico_fn)
    precip_raw = bruto["datos"]["precipitacion"]
    calibrada = [round(max(0.0, p * bias), 2) for p in precip_raw]
    p10 = [round(max(0.0, c * 0.75), 2) for c in calibrada]
    p90 = [round(c * 1.3, 2) for c in calibrada]
    alerta_lluvia_fuerte = any(p >= 25 for p in calibrada[:3])
    return {
        **bruto,
        "precipitacion_calibrada": calibrada,
        "precipitacion_p10": p10,
        "precipitacion_p50": calibrada,
        "precipitacion_p90": p90,
        "pop": bruto["datos"]["pop"],
        "intensidad": bruto["datos"]["intensidad"],
        "incertidumbre": {
            "desvio_estandar": [
                round((hi - lo) / 3.92, 2) for lo, hi in zip(p10, p90)
            ],
            "intervalo_confianza_90": [
                {"bajo": lo, "alto": hi} for lo, hi in zip(p10, p90)
            ],
        },
        "metodo_calibracion": "bias_historico_local",
        "factor_bias": round(bias, 3),
        "modelos_usados": ["gfs"],
        "confianza": "alta" if bias != 0.92 else "media",
        "alerta_lluvia_fuerte": alerta_lluvia_fuerte,
        "metadatos": {
            **bruto["metadatos"],
            "calibrado": True,
            "tipo_dato": "pronostico_calibrado",
        },
    }


def generar_alertas_precipitacion(
    estacion_id: str,
    pronostico_calibrado_fn,
    cultivo: str | None = None,
) -> list[dict[str, Any]]:
    data = pronostico_calibrado_fn(estacion_id, 7)
    if not data:
        return []
    cultivos = [cultivo] if cultivo else CULTIVOS_DEFAULT
    alertas: list[dict[str, Any]] = []
    precip = data.get("precipitacion_calibrada") or data["datos"]["precipitacion"]
    fechas = data["fechas"]
    aid = 1
    for cult in cultivos:
        umb = UMBRALES_PRECIP_CULTIVO.get(cult, UMBRALES_PRECIP_CULTIVO["palto"])
        for i, (fecha, lluvia_24h) in enumerate(zip(fechas, precip)):
            lluvia_48h = lluvia_24h + (precip[i + 1] if i + 1 < len(precip) else 0)
            intens = intensidad_mm_h(lluvia_24h)
            nivel = None
            tipo = None
            recs: list[str] = []
            if lluvia_24h >= umb["lluvia_24h_rojo"] or intens >= umb["intensidad_rojo"]:
                nivel = "rojo"
                tipo = "lluvia_intensa"
                recs = ["Suspender riego", "Verificar drenaje", "Inspeccionar parcelas"]
            elif lluvia_48h >= umb["lluvia_48h_rojo"]:
                nivel = "rojo"
                tipo = "encharcamiento"
                recs = [
                    "Suspender riego inmediatamente",
                    "Monitorear humedad de suelo 48 h",
                ]
            elif lluvia_24h >= umb["lluvia_24h_rojo"] * 0.6:
                nivel = "naranja"
                tipo = "vigilancia_lluvia"
                recs = ["Considerar posponer riego", "Revisar pronóstico actualizado"]
            if not nivel:
                continue
            alertas.append(
                {
                    "id": aid,
                    "estacion_id": estacion_id,
                    "cultivo": cult,
                    "tipo_alerta": tipo,
                    "nivel_severidad": nivel,
                    "descripcion": (
                        f"Lluvia pronosticada {lluvia_24h:.1f} mm/24h "
                        f"({clasificar_intensidad(lluvia_24h)})"
                    ),
                    "lluvia_24h_pronosticada": round(lluvia_24h, 1),
                    "lluvia_48h_pronosticada": round(lluvia_48h, 1),
                    "intensidad_mm_h": intens,
                    "fecha": fecha,
                    "recomendaciones": recs,
                    "fuente": "pronostico_calibrado",
                }
            )
            aid += 1
    return alertas


def pronostico_heladas(
    estacion_id: str,
    dias: int,
    pronostico_fn,
    slug_a_nombre_fn,
) -> dict[str, Any]:
    filas = pronostico_fn(estacion_id, dias) or []
    dias_helada = []
    peor = None
    for r in filas:
        t_min = float(r.get("temperatura_min") or 99)
        entry = {
            "fecha": r["fecha"],
            "temperatura_min": t_min,
            "severidad": severidad_helada(t_min),
            "por_cultivo": {
                c: severidad_helada(t_min, c) for c in CULTIVOS_DEFAULT
            },
        }
        dias_helada.append(entry)
        if peor is None or t_min < peor["temperatura_min"]:
            peor = entry
    alerta_activa = peor is not None and peor["severidad"] in ("critico", "alto")
    return {
        "estacion_id": estacion_id,
        "estacion_nombre": slug_a_nombre_fn(estacion_id),
        "dias": dias_helada,
        "peor_dia": peor,
        "alerta_activa": alerta_activa,
        "fuente": "openmeteo",
        "tipo_dato": "pronostico",
        "actualizado": datetime.now(TZ).isoformat(),
    }


def generar_alertas_helada(
    estacion_id: str,
    pronostico_heladas_fn,
) -> list[dict[str, Any]]:
    data = pronostico_heladas_fn(estacion_id, 7)
    alertas: list[dict[str, Any]] = []
    aid = 1
    for dia in data.get("dias", []):
        if dia["severidad"] not in ("critico", "alto", "moderado"):
            continue
        nivel = "warning" if dia["severidad"] in ("critico", "alto") else "info"
        cultivos_afectados = [
            c for c, s in dia.get("por_cultivo", {}).items() if s in ("critico", "alto")
        ]
        alertas.append(
            {
                "id": aid,
                "nivel": nivel,
                "estacion_id": estacion_id,
                "tipo": "helada",
                "fecha": dia["fecha"],
                "temperatura_min": dia["temperatura_min"],
                "severidad": dia["severidad"],
                "cultivos_afectados": cultivos_afectados,
                "mensaje": (
                    f"Riesgo de helada {dia['severidad']}: "
                    f"mín {dia['temperatura_min']}°C el {dia['fecha']}"
                ),
                "recomendaciones": _recomendaciones_helada(dia["severidad"]),
            }
        )
        aid += 1
    return alertas


def _recomendaciones_helada(severidad: str) -> list[str]:
    base = ["Monitorear temperatura nocturna", "Revisar pronóstico cada 6 h"]
    if severidad == "critico":
        return base + [
            "Activar protección antihielo (aspersión, ventiladores)",
            "Suspender riego por aspersión",
        ]
    if severidad == "alto":
        return base + ["Preparar protección antihielo", "Evitar labores sensibles al frío"]
    return base + ["Vigilar sectores bajos del valle"]


def obtener_acumulado_precipitacion(
    estacion_id: str,
    dias_rango: int,
    pronostico_calibrado_fn,
    historico_fn,
    hoy_fn,
) -> dict[str, Any]:
    hoy = hoy_fn()
    hist = historico_fn(estacion_id, dias_rango) or []
    hist_filas = [h for h in hist if str(h.get("fecha", ""))[:10] <= hoy]
    acum_hist = 0.0
    fechas_hist = []
    precip_hist = []
    acum_corriente = []
    for h in hist_filas:
        p = float(h.get("precipitacion") or 0)
        acum_hist += p
        fechas_hist.append(h["fecha"])
        precip_hist.append(round(p, 2))
        acum_corriente.append(round(acum_hist, 2))
    cal = pronostico_calibrado_fn(estacion_id, dias_rango)
    pron_fechas = []
    pron_precip = []
    pron_acum = []
    acum = acum_hist
    if cal:
        for f, p in zip(
            cal["fechas"],
            cal.get("precipitacion_calibrada") or cal["datos"]["precipitacion"],
        ):
            pron_fechas.append(f)
            pron_precip.append(p)
            acum += p
            pron_acum.append(round(acum, 2))
    return {
        "estacion_id": estacion_id,
        "periodo": f"{(datetime.fromisoformat(hoy) - timedelta(days=dias_rango)).date().isoformat()} a {hoy}",
        "historico": {
            "fechas": fechas_hist,
            "precipitacion_diaria": precip_hist,
            "acumulado_corriente": acum_corriente,
        },
        "pronostico": {
            "fechas": pron_fechas,
            "precipitacion_diaria": pron_precip,
            "acumulado_proyectado": pron_acum,
        },
        "totales": {
            "historico": round(acum_hist, 2),
            "pronosticado": round(sum(pron_precip), 2),
            "acumulado_total": round(acum, 2),
        },
    }


def obtener_historico_precipitacion(
    estacion_id: str,
    desde: str,
    hasta: str,
    historico_fn,
    hoy_fn,
) -> dict[str, Any]:
    hist = historico_fn(estacion_id, 365) or []
    hoy = hoy_fn()
    datos = []
    precip_vals = []
    for h in hist:
        dia = str(h.get("fecha", ""))[:10]
        if not dia or dia < desde or dia > hasta or dia > hoy:
            continue
        p = float(h.get("precipitacion") or 0)
        datos.append(
            {
                "fecha": dia,
                "precipitacion": round(p, 2),
                "fuente": h.get("tipo_dato", "observado"),
            }
        )
        if p > 0:
            precip_vals.append(p)
    stats = {}
    if datos:
        stats = {
            "dias_con_lluvia": len(precip_vals),
            "dias_sin_lluvia": len(datos) - len(precip_vals),
            "precipitacion_total": round(sum(precip_vals), 2),
            "precipitacion_media_dia_lluvia": round(
                sum(precip_vals) / len(precip_vals), 2
            )
            if precip_vals
            else 0,
            "precipitacion_max_dia": round(max(precip_vals), 2) if precip_vals else 0,
            "dias_lluvia_fuerte": len([p for p in precip_vals if p > 20]),
        }
    return {
        "estacion_id": estacion_id,
        "periodo": f"{desde} a {hasta}",
        "datos": datos,
        "estadisticas": stats,
    }


def cronograma_riego_inteligente(
    estacion_id: str,
    cultivo_id: str,
    pronostico_calibrado_fn,
    resumen_fn,
) -> dict[str, Any]:
    cal = pronostico_calibrado_fn(estacion_id, 7)
    resumen = resumen_fn(estacion_id) or {}
    precip_48h = 0.0
    precip_72h = 0.0
    if cal:
        vals = cal.get("precipitacion_calibrada") or cal["datos"]["precipitacion"]
        precip_48h = sum(vals[:2]) if len(vals) >= 2 else sum(vals)
        precip_72h = sum(vals[:3]) if len(vals) >= 3 else sum(vals)
    hum = float(resumen.get("humedad") or 50)
    t_min = float(resumen.get("temperatura_min") or 10)
    accion = "riego_normal"
    motivo = f"Humedad {hum:.0f}%"
    dias_posponer = 0
    if precip_48h >= 5:
        accion = "posponer_riego"
        dias_posponer = 2 if precip_48h < 15 else 3
        motivo = f"Lluvia esperada {precip_48h:.1f} mm en 48 h — posponer riego {dias_posponer} días"
    elif precip_72h >= 8:
        accion = "posponer_riego"
        dias_posponer = 2
        motivo = f"Acumulado pronosticado 72 h: {precip_72h:.1f} mm"
    elif t_min <= 4:
        accion = "suspender_riego_helada"
        motivo = f"Riesgo helada (mín {t_min:.1f}°C) — evitar riego por aspersión"
    elif hum < 45:
        accion = "riego_recomendado"
        motivo = "Baja humedad y sin lluvia significativa próxima"
    return {
        "estacion_id": estacion_id,
        "cultivo": cultivo_id,
        "accion": accion,
        "dias_posponer": dias_posponer,
        "precipitacion_48h_mm": round(precip_48h, 1),
        "precipitacion_72h_mm": round(precip_72h, 1),
        "motivo": motivo,
        "fuente_pronostico": "calibrado",
    }
