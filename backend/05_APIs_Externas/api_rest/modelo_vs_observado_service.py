#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""M5 — modelo vs observado por faena (aire + meteo + IoT).

Reutiliza SINCA/CAMS cuando hay datos en `aire_registros` (tipo_dato=observado).
Sin observado: responde `estado=sin_observado` con guía de activación.
"""

from __future__ import annotations

from typing import Any

from api_rest.sinca_service import calcular_sesgo, estado_sinca


def _estacion_aire_faena(faena: dict[str, Any]) -> str:
    """Estación ancla para comparar aire (preferir rol rajo / ancla)."""
    for e in faena.get("estaciones_area") or []:
        if e.get("rol") == "rajo" and e.get("id"):
            return str(e["id"])
    ancla = faena.get("estacion_ancla") or faena.get("id")
    return str(ancla)


def _por_dia(
    filas: list[dict[str, Any]], prefix: str, vars_map: dict[str, str]
) -> dict[str, dict[str, float]]:
    out: dict[str, dict[str, float]] = {}
    for f in filas:
        dia = str(f.get("fecha") or f.get("fecha_hora") or "")[:10]
        if not dia:
            continue
        bucket = out.setdefault(dia, {})
        for src, suffix in vars_map.items():
            if f.get(src) is not None:
                try:
                    bucket[f"{prefix}_{suffix}"] = float(f[src])
                except (TypeError, ValueError):
                    pass
    return out


def _metricas_pares(
    pares: list[dict[str, Any]], variables: tuple[str, ...]
) -> dict[str, Any]:
    """Sesgo modelo−observado genérico (mismo shape que calcular_sesgo)."""
    # Adaptar a formato calcular_sesgo para pm25/pm10; resto manual.
    base = calcular_sesgo(pares) if any(v in ("pm25", "pm10") for v in variables) else {
        "n_pares": len(pares),
        "pm25": None,
        "pm10": None,
    }
    for var in variables:
        if var in ("pm25", "pm10") and base.get(var):
            continue
        diffs: list[float] = []
        for p in pares:
            m = p.get(f"modelo_{var}")
            o = p.get(f"obs_{var}")
            if m is None or o is None:
                # aliases cams_/sinca_
                m = p.get(f"cams_{var}")
                o = p.get(f"sinca_{var}")
            if m is None or o is None:
                continue
            diffs.append(float(m) - float(o))
        if not diffs:
            continue
        base[var] = {
            "n": len(diffs),
            "sesgo_medio": round(sum(diffs) / len(diffs), 2),
            "mae": round(sum(abs(d) for d in diffs) / len(diffs), 2),
            "unidad": "ug/m3" if var in ("pm25", "pm10", "so2", "no2") else "var",
            "definicion": "modelo - observado",
        }
    return base


def sesgo_aire_estacion(estacion_id: str, dias: int = 14) -> dict[str, Any]:
    """Compara aire modelo (CAMS) vs observado (SINCA u otras) en aire_registros."""
    slug = estacion_id.lower().replace("-", "_")
    try:
        from api_rest.integracion import aire_store
    except Exception as exc:
        return {"error": str(exc), "estacion_id": slug, "estado": "error"}

    modelo = aire_store.leer_aire_por_fuente(slug, fuente="openmeteo_cams", dias=dias)
    if not modelo:
        modelo = aire_store.leer_aire(slug, dias=dias, tipo_dato="modelo")
    observado = aire_store.leer_aire_por_fuente(slug, fuente="sinca", dias=dias)
    if not observado:
        observado = aire_store.leer_aire(slug, dias=dias, tipo_dato="observado")

    vars_map = {
        "pm2_5": "pm25",
        "pm10": "pm10",
        "sulphur_dioxide": "so2",
        "nitrogen_dioxide": "no2",
    }
    por_m = _por_dia(modelo, "cams", vars_map)
    # usar prefix cams/sinca para reutilizar calcular_sesgo en pm
    por_o = _por_dia(observado, "sinca", vars_map)
    pares: list[dict[str, Any]] = []
    for dia in sorted(set(por_m) & set(por_o)):
        pares.append({"fecha": dia, **por_m[dia], **por_o[dia]})

    metricas = _metricas_pares(pares, ("pm25", "pm10", "so2", "no2"))
    estado = "ok" if pares else "sin_observado"
    if modelo and not observado:
        estado = "sin_observado"
    elif not modelo and observado:
        estado = "sin_modelo"
    elif not modelo and not observado:
        estado = "sin_datos"

    return {
        "estacion_id": slug,
        "dias": dias,
        "n_modelo": len(modelo),
        "n_observado": len(observado),
        "pares": pares[-dias:],
        "tipo_dato_modelo": "modelo",
        "tipo_dato_observado": "observado",
        "fuentes": {"modelo": "openmeteo_cams", "observado": "sinca|observado"},
        "estado": estado,
        "estado_sinca": estado_sinca().get("estado"),
        **{k: metricas.get(k) for k in ("n_pares", "pm25", "pm10", "so2", "no2")},
    }


def sesgo_meteo_estacion(estacion_id: str, dias: int = 14) -> dict[str, Any]:
    """Compara meteo_registros (hist) vs meteo_pronostico si hay solape por fecha."""
    slug = estacion_id.lower().replace("-", "_")
    try:
        from api_rest.integracion import meteo_store
    except Exception as exc:
        return {"error": str(exc), "estacion_id": slug, "estado": "error"}

    obs = meteo_store.leer_registros(slug, dias=dias) or []
    try:
        pron = meteo_store.leer_pronostico(slug, dias=min(dias, 16)) or []
    except Exception:
        pron = []

    def _temp_por_dia(filas: list[dict[str, Any]], key_pref: str) -> dict[str, float]:
        out: dict[str, float] = {}
        for f in filas:
            dia = str(f.get("fecha") or f.get("fecha_hora") or "")[:10]
            if not dia:
                continue
            t = f.get("temperatura") or f.get("temp") or f.get("temperature_2m")
            if t is None:
                continue
            try:
                out[dia] = float(t)
            except (TypeError, ValueError):
                pass
        return out

    o_map = _temp_por_dia(obs, "obs")
    m_map = _temp_por_dia(pron, "modelo")
    pares = []
    for dia in sorted(set(o_map) & set(m_map)):
        pares.append(
            {
                "fecha": dia,
                "modelo_temp": m_map[dia],
                "obs_temp": o_map[dia],
            }
        )
    metricas: dict[str, Any] = {"n_pares": len(pares), "temperatura": None}
    if pares:
        diffs = [p["modelo_temp"] - p["obs_temp"] for p in pares]
        metricas["temperatura"] = {
            "n": len(diffs),
            "sesgo_medio": round(sum(diffs) / len(diffs), 2),
            "mae": round(sum(abs(d) for d in diffs) / len(diffs), 2),
            "unidad": "°C",
            "definicion": "pronostico - registro (observado)",
        }
    return {
        "estacion_id": slug,
        "dias": dias,
        "n_observado": len(obs),
        "n_modelo": len(pron),
        "pares": pares[-dias:],
        "tipo_dato_modelo": "pronostico",
        "tipo_dato_observado": "observado",
        "estado": "ok" if pares else ("sin_observado" if not obs else "sin_pares"),
        **metricas,
    }


def _iot_resumen(estacion_id: str) -> dict[str, Any]:
    try:
        from api_rest import iot_services

        lecturas = iot_services.listar_lecturas(estacion_id=estacion_id, limite=20) or []
    except Exception:
        lecturas = []
    return {
        "n_lecturas": len(lecturas),
        "tipo_dato": "observado",
        "fuente": "iot",
        "estado": "ok" if lecturas else "sin_iot",
        "muestra": lecturas[:5] if lecturas else [],
    }


def reporte_modelo_vs_observado(faena_id: str, *, dias: int = 14) -> dict[str, Any] | None:
    """Reporte M5 completo para una faena del catálogo."""
    from api_rest.faena_catalogo import get_faena

    faena = get_faena(faena_id)
    if not faena:
        return None
    dias = max(3, min(int(dias or 14), 60))
    estacion = _estacion_aire_faena(faena)
    aire = sesgo_aire_estacion(estacion, dias=dias)
    meteo = sesgo_meteo_estacion(estacion, dias=dias)
    iot = _iot_resumen(estacion)

    obs_area = [
        e
        for e in (faena.get("estaciones_area") or [])
        if (e.get("fuente") or "") in ("observado", "seed")
    ]

    estados = [aire.get("estado"), meteo.get("estado"), iot.get("estado")]
    if "ok" in estados:
        global_estado = "ok" if aire.get("estado") == "ok" or meteo.get("estado") == "ok" else "parcial"
    elif all(s in ("sin_observado", "sin_datos", "sin_iot", "sin_pares", "sin_modelo") for s in estados):
        global_estado = "sin_observado"
    else:
        global_estado = "parcial"

    return {
        "faena_id": faena["id"],
        "nombre": faena.get("nombre"),
        "estacion_id": estacion,
        "dias": dias,
        "tipo_dato_modelo": "modelo",
        "tipo_dato_observado": "observado",
        "estado": global_estado,
        "aire": aire,
        "meteo": meteo,
        "iot": iot,
        "estaciones_area": faena.get("estaciones_area") or [],
        "estaciones_con_fuente_observada": obs_area,
        "guia": {
            "sinca": "METGO_SINCA_IDS + METGO_SINCA_CSV_DIR|URL → aire_registros tipo_dato=observado",
            "iot": "POST /api/iot/lecturas o simular; asociar estacion_id de la faena",
            "estaciones_area": "actualizar faena_estaciones_area.fuente='observado' cuando haya AWS/IoT real",
            "docs": "docs/roadmap/fase-3/sinca_activacion.md",
        },
    }
