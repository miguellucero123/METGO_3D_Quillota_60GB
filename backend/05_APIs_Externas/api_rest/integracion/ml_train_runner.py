#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Entrenamiento ligero modelos Quillota (módulo 06) — Fase 8.

Usa SQLite meteo_historico si hay suficientes filas; si no, datos sintéticos.
Guarda en modelos_ml_quillota/ y actualiza configuracion_modelos.json.
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import numpy as np

from api_rest.integracion import meteo_store


MODELS_CONFIG: dict[str, dict[str, Any]] = {
    "temperatura_max": {
        "features": ["dia_año", "hora", "humedad", "presion", "viento_velocidad"],
        "sklearn": "RandomForestRegressor",
    },
    "temperatura_min": {
        "features": ["dia_año", "hora", "humedad", "presion", "viento_velocidad"],
        "sklearn": "RandomForestRegressor",
    },
    "precipitacion": {
        "features": ["dia_año", "hora", "humedad", "presion", "temperatura_max"],
        "sklearn": "RandomForestRegressor",
    },
    "humedad": {
        "features": ["dia_año", "hora", "temperatura_max", "temperatura_min", "presion"],
        "sklearn": "LinearRegression",
    },
    "presion": {
        "features": ["dia_año", "hora", "temperatura_max", "temperatura_min", "humedad"],
        "sklearn": "LinearRegression",
    },
}

MIN_FILAS_REALES = 30


def _quillota_dir() -> Path:
    for p in Path(__file__).resolve().parents:
        if (p / "metgo_paths.py").exists():
            d = p / "backend" / "06_Modelos_ML_IA" / "modelos" / "modelos_ml_quillota"
            d.mkdir(parents=True, exist_ok=True)
            return d
    raise FileNotFoundError("modelos_ml_quillota no encontrado")


def _filas_desde_meteo(estacion_id: str, dias: int) -> list[dict[str, Any]]:
    filas = []
    for row in meteo_store.leer_registros(estacion_id, dias=dias):
        try:
            fecha = datetime.strptime(str(row["fecha"])[:10], "%Y-%m-%d")
        except ValueError:
            continue
        dia = fecha.timetuple().tm_yday
        for hora in (6, 12, 18):
            filas.append(
                {
                    "dia_año": dia,
                    "hora": hora,
                    "temperatura_max": float(row.get("temperatura_max") or 20),
                    "temperatura_min": float(row.get("temperatura_min") or 12),
                    "humedad": float(row.get("humedad") or 60),
                    "precipitacion": float(row.get("precipitacion") or 0),
                    "viento_velocidad": float(row.get("viento") or 5),
                    "presion": float(row.get("presion") or 1013),
                }
            )
    return filas


def _filas_sinteticas(n_dias: int = 180) -> list[dict[str, Any]]:
    filas: list[dict[str, Any]] = []
    inicio = datetime.now() - timedelta(days=n_dias)
    rng = np.random.default_rng(42)
    for i in range(n_dias):
        fecha = inicio + timedelta(days=i)
        dia = fecha.timetuple().tm_yday
        temp_base = 15 + 10 * np.sin(2 * np.pi * dia / 365)
        for hora in range(0, 24, 3):
            humedad = max(0, min(100, 60 + 15 * np.cos(2 * np.pi * hora / 24) + rng.normal(0, 2)))
            presion = 1013 + 8 * np.sin(2 * np.pi * dia / 365) + rng.normal(0, 1)
            viento = max(0, 5 + rng.normal(0, 1.5))
            tmax = temp_base + 5 * np.sin(2 * np.pi * hora / 24) + rng.normal(0, 0.8)
            tmin = tmax - 8 + rng.normal(0, 0.5)
            precip = float(rng.exponential(1.5)) if rng.random() < 0.12 else 0.0
            filas.append(
                {
                    "dia_año": dia,
                    "hora": hora,
                    "temperatura_max": round(tmax, 2),
                    "temperatura_min": round(tmin, 2),
                    "humedad": round(humedad, 2),
                    "precipitacion": round(precip, 2),
                    "viento_velocidad": round(viento, 2),
                    "presion": round(presion, 2),
                }
            )
    return filas


def _modelo_sklearn(nombre: str):
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.linear_model import LinearRegression

    if nombre == "RandomForestRegressor":
        return RandomForestRegressor(n_estimators=80, random_state=42)
    return LinearRegression()


def entrenar_quillota(
    estacion_id: str = "quillota",
    variables: list[str] | None = None,
    dias_datos: int = 365,
) -> dict[str, Any]:
    import joblib
    from sklearn.metrics import mean_squared_error, r2_score
    from sklearn.model_selection import train_test_split

    filas = _filas_desde_meteo(estacion_id, dias_datos)
    origen = "meteo_sqlite"
    if len(filas) < MIN_FILAS_REALES:
        filas = _filas_sinteticas(min(365, max(90, dias_datos)))
        origen = "sintetico"

    targets = variables or list(MODELS_CONFIG.keys())
    out_dir = _quillota_dir()
    resultados: dict[str, Any] = {}

    for var in targets:
        cfg = MODELS_CONFIG.get(var)
        if not cfg:
            resultados[var] = {"error": "variable no soportada"}
            continue
        features = cfg["features"]
        xs, ys = [], []
        for row in filas:
            if row.get(var) is None:
                continue
            try:
                xs.append([float(row.get(f, 0)) for f in features])
                ys.append(float(row[var]))
            except (TypeError, ValueError):
                continue
        if len(xs) < 20:
            resultados[var] = {"error": "datos insuficientes"}
            continue

        X = np.array(xs)
        y = np.array(ys)
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        modelo = _modelo_sklearn(cfg["sklearn"])
        modelo.fit(X_train, y_train)
        pred = modelo.predict(X_test)
        mse = float(mean_squared_error(y_test, pred))
        r2 = float(r2_score(y_test, pred))
        fname = f"modelo_{var}.joblib"
        path = out_dir / fname
        joblib.dump(modelo, path)
        resultados[var] = {
            "variable": var,
            "mse": mse,
            "r2": r2,
            "modelo_path": f"modelos_ml_quillota/{fname}",
            "features": features,
        }

    config_path = out_dir / "configuracion_modelos.json"
    config_path.write_text(
        json.dumps(resultados, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    from api_rest.integracion import ml_registry

    reg = ml_registry.sincronizar_registro()
    return {
        "ok": True,
        "origen_datos": origen,
        "filas": len(filas),
        "estacion_id": estacion_id,
        "entrenados": len([v for v in resultados.values() if "r2" in v]),
        "resultados": resultados,
        "registry_servibles": reg.get("servibles"),
        "registry_total": reg.get("total"),
        "finalizado": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }
