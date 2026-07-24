#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ML por dominio (E12) — PM10 entrenado + baselines; stubs helada/viento."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

FEATURES_PM10 = ["pm10", "pm25", "so2", "no2", "o3", "dia_año", "sin_doy", "cos_doy"]


def _modelos_dir() -> Path | None:
    here = Path(__file__).resolve()
    for p in here.parents:
        cand = p / "backend" / "06_Modelos_ML_IA" / "modelos" / "modelos_dominio_copiapo"
        if cand.is_dir():
            return cand
        cand2 = p / "06_Modelos_ML_IA" / "modelos" / "modelos_dominio_copiapo"
        if cand2.is_dir():
            return cand2
    return None


def _meta_pm10() -> dict[str, Any]:
    d = _modelos_dir()
    if not d:
        return {}
    meta_path = d / "meta.json"
    if meta_path.is_file():
        try:
            return json.loads(meta_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return {}
    return {}


def _artefacto_pm10_disponible() -> bool:
    d = _modelos_dir()
    return bool(d and (d / "pm10_episodio.joblib").is_file())


def _cargar_pm10():
    d = _modelos_dir()
    if not d:
        return None
    path = d / "pm10_episodio.joblib"
    if not path.is_file():
        return None
    try:
        import joblib

        return joblib.load(path)
    except Exception:
        return None


MODELOS_DOMINIO: list[dict[str, Any]] = [
    {
        "id": "helada_quillota",
        "sitio": "quillota",
        "dominio": "agro",
        "variable": "riesgo_helada",
        "descripcion": "Clasificador/riesgo de helada Valle de Aconcagua",
        "estado": "stub_e12",
        "servible": False,
        "modo": "stub",
        "fuente_features": "meteo_registros + openmeteo_forecast",
    },
    {
        "id": "viento_extremo_paine",
        "sitio": "paine",
        "dominio": "criosfera",
        "variable": "viento_extremo",
        "descripcion": "Umbral de viento extremo / alertas parque",
        "estado": "baseline_e12",
        "servible": True,
        "modo": "baseline_regla",
        "fuente_features": "openmeteo_forecast",
        "umbral_viento_ms": 15.0,
    },
    {
        "id": "viento_extremo_mantos",
        "sitio": "mantos_blancos",
        "dominio": "mineria",
        "variable": "viento_extremo",
        "descripcion": "Viento extremo para ventanas de tronadura/izaje",
        "estado": "baseline_e12",
        "servible": True,
        "modo": "baseline_regla",
        "fuente_features": "operaciones panel / openmeteo",
        "umbral_viento_ms": 12.0,
    },
    {
        "id": "pm10_episodio_copiapo",
        "sitio": "copiapo",
        "dominio": "aire",
        "variable": "episodio_pm10",
        "descripcion": "ICAP día siguiente + episodio (umbral 200)",
        "estado": "entrenado_e12" if _artefacto_pm10_disponible() else "baseline_e12",
        "servible": True,
        "modo": "sklearn_regresor" if _artefacto_pm10_disponible() else "baseline_regla",
        "fuente_features": "aire_actual CAMS; artefacto modelos_dominio_copiapo",
        "umbral_icap": 200,
    },
]


def listar_modelos_dominio(sitio: str | None = None) -> dict[str, Any]:
    rows = []
    for m in MODELOS_DOMINIO:
        item = dict(m)
        if item["id"] == "pm10_episodio_copiapo":
            meta = _meta_pm10()
            if meta:
                item["metrics"] = {
                    "mae_icap": meta.get("mae_icap"),
                    "r2": meta.get("r2"),
                    "origen_datos": meta.get("origen_datos"),
                    "entrenado": meta.get("entrenado"),
                }
                item["estado"] = "entrenado_e12"
                item["modo"] = "sklearn_regresor"
                item["servible"] = True
        rows.append(item)
    if sitio:
        s = sitio.strip().lower()
        rows = [r for r in rows if r.get("sitio") == s]
    return {
        "total": len(rows),
        "servibles": sum(1 for r in rows if r.get("servible")),
        "modelos": rows,
        "nota": (
            "E12: pm10 usa GradientBoosting sobre ICAP t+1 (CAMS); "
            "viento extremo = baseline por umbral; helada sigue stub."
        ),
    }


def _prob_desde_icap(icap: float | None, umbral: float = 200.0) -> float | None:
    if icap is None:
        return None
    if icap < umbral:
        return round(max(0.0, min(0.45, float(icap) / umbral * 0.45)), 3)
    exceso = (float(icap) - umbral) / max(umbral, 1.0)
    return round(min(0.99, 0.55 + exceso * 0.35), 3)


def _vector_features(actual: dict[str, Any]) -> list[float]:
    from datetime import date

    raw = str(actual.get("actualizado") or actual.get("fecha") or "")[:10]
    try:
        dt = date.fromisoformat(raw)
    except ValueError:
        dt = date.today()
    doy = dt.timetuple().tm_yday
    ang = 2 * math.pi * doy / 366.0
    return [
        float(actual.get("pm10") or 0.0),
        float(actual.get("pm2_5") or actual.get("pm25") or 0.0),
        float(actual.get("sulphur_dioxide") or actual.get("so2") or 0.0),
        float(actual.get("nitrogen_dioxide") or actual.get("no2") or 0.0),
        float(actual.get("ozone") or actual.get("o3") or 0.0),
        float(doy),
        math.sin(ang),
        math.cos(ang),
    ]


def prediccion_pm10_episodio(estacion_id: str = "copiapo_centro") -> dict[str, Any]:
    """Prefiere artefacto sklearn; fallback a regla ICAP actual >= 200."""
    slug = estacion_id.lower().replace("-", "_")
    umbral = 200
    try:
        from api_rest import aire_service

        actual = aire_service.aire_actual(slug)
    except Exception as exc:
        return {
            "modelo_id": "pm10_episodio_copiapo",
            "servible": True,
            "error": str(exc),
            "prediccion": None,
        }

    if actual is None:
        return {
            "modelo_id": "pm10_episodio_copiapo",
            "servible": True,
            "modo": "baseline_regla",
            "estacion_id": slug,
            "prediccion": None,
            "motivo": "sin_datos_aire",
        }

    bundle = _cargar_pm10()
    if bundle and bundle.get("tipo") == "regresor_icap":
        model = bundle["model"]
        vec = _vector_features(actual)
        icap_pred = float(model.predict([vec])[0])
        episodio = icap_pred >= umbral
        meta = bundle.get("meta") or _meta_pm10()
        return {
            "modelo_id": "pm10_episodio_copiapo",
            "servible": True,
            "modo": "sklearn_regresor",
            "estado": "entrenado_e12",
            "estacion_id": slug,
            "umbral_icap": umbral,
            "horizonte": "dia_siguiente",
            "prediccion": {
                "episodio": episodio,
                "probabilidad": _prob_desde_icap(icap_pred, umbral),
                "icap_predicho": round(icap_pred, 1),
                "icap_actual": actual.get("icap"),
                "pm10": actual.get("pm10"),
                "nivel": actual.get("nivel"),
                "fuente": actual.get("fuente"),
                "tipo_dato": actual.get("tipo_dato"),
                "actualizado": actual.get("actualizado"),
            },
            "metrics": {
                "mae_icap": meta.get("mae_icap"),
                "r2": meta.get("r2"),
                "origen_datos": meta.get("origen_datos"),
            },
            "nota": "Regresor ICAP t+1 (CAMS). Validar con SINCA cuando haya observado.",
        }

    # Fallback regla
    icap = actual.get("icap")
    try:
        icap_f = float(icap) if icap is not None else None
    except (TypeError, ValueError):
        icap_f = None
    episodio = bool(icap_f is not None and icap_f >= umbral)
    return {
        "modelo_id": "pm10_episodio_copiapo",
        "servible": True,
        "modo": "baseline_regla",
        "estado": "baseline_e12",
        "estacion_id": slug,
        "umbral_icap": umbral,
        "prediccion": {
            "episodio": episodio,
            "probabilidad": _prob_desde_icap(icap_f, umbral),
            "icap": icap_f,
            "pm10": actual.get("pm10"),
            "nivel": actual.get("nivel"),
            "fuente": actual.get("fuente"),
            "tipo_dato": actual.get("tipo_dato"),
            "actualizado": actual.get("actualizado"),
        },
        "nota": "Sin artefacto joblib; regla ICAP actual.",
    }


def prediccion_viento_extremo(
    modelo_id: str,
    estacion_id: str | None = None,
    viento_ms: float | None = None,
) -> dict[str, Any]:
    hit = next((m for m in MODELOS_DOMINIO if m["id"] == modelo_id), None)
    if not hit:
        return {"error": "modelo_dominio_desconocido", "modelo_id": modelo_id}
    umbral = float(hit.get("umbral_viento_ms") or 12.0)
    v = viento_ms
    fuente = "parametro"
    slug = (estacion_id or ("mb_rajo" if hit["sitio"] == "mantos_blancos" else "paine")).lower()
    if v is None:
        try:
            from api_rest import operaciones_service

            if hit["sitio"] == "mantos_blancos":
                serie = operaciones_service.ventanas_operacionales(slug, horas=6) or []
                for reg in serie:
                    if isinstance(reg, dict) and reg.get("viento_velocidad") is not None:
                        v = float(reg["viento_velocidad"])
                        fuente = "operaciones_ventanas"
                        break
        except Exception:
            pass
    if v is None:
        return {
            "modelo_id": modelo_id,
            "servible": True,
            "modo": "baseline_regla",
            "estacion_id": slug,
            "prediccion": None,
            "motivo": "sin_viento",
            "umbral_viento_ms": umbral,
            "nota": "Pasa ?viento_ms= para forzar, o usa estación con datos de operaciones.",
        }
    extremo = float(v) >= umbral
    return {
        "modelo_id": modelo_id,
        "servible": True,
        "modo": "baseline_regla",
        "estado": "baseline_e12",
        "estacion_id": slug,
        "umbral_viento_ms": umbral,
        "prediccion": {
            "extremo": extremo,
            "viento_ms": float(v),
            "fuente": fuente,
        },
    }


def prediccion_dominio(
    modelo_id: str,
    estacion_id: str | None = None,
    viento_ms: float | None = None,
    **_: Any,
) -> dict[str, Any]:
    hit = next((m for m in MODELOS_DOMINIO if m["id"] == modelo_id), None)
    if not hit:
        return {"error": "modelo_dominio_desconocido", "modelo_id": modelo_id}
    if modelo_id == "pm10_episodio_copiapo":
        return prediccion_pm10_episodio(estacion_id or "copiapo_centro")
    if modelo_id.startswith("viento_extremo_"):
        return prediccion_viento_extremo(modelo_id, estacion_id=estacion_id, viento_ms=viento_ms)
    return {
        "modelo_id": modelo_id,
        "servible": False,
        "estado": hit.get("estado"),
        "prediccion": None,
        "motivo": "stub_e12_sin_artefacto",
        "sitio": hit.get("sitio"),
        "variable": hit.get("variable"),
    }
