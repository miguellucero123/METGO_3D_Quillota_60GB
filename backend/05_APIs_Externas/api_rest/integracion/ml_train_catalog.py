#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Catálogo de los ~43 modelos METGO (módulo 06) para entrenamiento unificado."""

from __future__ import annotations

from typing import Any

# Features compartidas (meteo OpenMeteo / SQLite → filas horarias)
FEATURES_BASE = [
    "dia_año",
    "hora",
    "dia_semana",
    "temperatura_max",
    "temperatura_min",
    "temperatura_promedio",
    "humedad_relativa",
    "viento_velocidad",
    "precipitacion",
    "presion_atmosferica",
    "nubosidad",
]

FEATURES_QUILLOTA = ["dia_año", "hora", "humedad", "presion", "viento_velocidad"]
FEATURES_QUILLOTA_ALT = [
    "dia_año",
    "hora",
    "temperatura_max",
    "temperatura_min",
    "humedad",
    "presion",
    "viento_velocidad",
    "precipitacion",
]

VARS_ML = (
    "temperatura_actual",
    "humedad_relativa",
    "velocidad_viento",
    "precipitacion",
    "presion_atmosferica",
    "nubosidad",
)

ALGOS_ML = (
    ("GradientBoosting", "GradientBoostingRegressor"),
    ("LinearRegression", "LinearRegression"),
    ("RandomForest", "RandomForestRegressor"),
    ("Ridge", "Ridge"),
)


def _entry(
    paquete: str,
    archivo: str,
    variable: str,
    target: str,
    features: list[str],
    sklearn: str,
    *,
    scaler: bool = False,
    modo: str = "manifest",
) -> dict[str, Any]:
    return {
        "paquete": paquete,
        "archivo": archivo,
        "variable": variable,
        "target": target,
        "features": features,
        "sklearn": sklearn,
        "scaler": scaler,
        "modo": modo,
    }


def catalogo_completo() -> list[dict[str, Any]]:
    """Lista de todos los modelos a entrenar y registrar."""
    out: list[dict[str, Any]] = []

    quillota = "modelos_ml_quillota"
    quillota_cfg: list[tuple[str, str, str, list[str]]] = [
        ("modelo_temperatura_max.joblib", "temperatura_max", "temperatura_max", FEATURES_QUILLOTA),
        ("modelo_temperatura_min.joblib", "temperatura_min", "temperatura_min", FEATURES_QUILLOTA),
        ("modelo_precipitacion.joblib", "precipitacion", "precipitacion", FEATURES_QUILLOTA + ["temperatura_max"]),
        ("modelo_humedad.joblib", "humedad", "humedad", ["dia_año", "hora", "temperatura_max", "temperatura_min", "presion"]),
        ("modelo_presion.joblib", "presion", "presion", ["dia_año", "hora", "temperatura_max", "temperatura_min", "humedad"]),
    ]
    for archivo, var, target, feats in quillota_cfg:
        sk = "RandomForestRegressor" if var != "humedad" and var != "presion" else "LinearRegression"
        out.append(_entry(quillota, archivo, var, target, feats, sk))

    pkl_map = (
        ("modelo_random_forest.pkl", "RandomForestRegressor", "temperatura_max"),
        ("modelo_linear_regression.pkl", "LinearRegression", "temperatura_max"),
        ("modelo_gradient_boosting.pkl", "GradientBoostingRegressor", "temperatura_max"),
        ("modelo_svm.pkl", "Ridge", "temperatura_max"),
        ("modelo_knn.pkl", "RandomForestRegressor", "humedad"),
    )
    for archivo, sk, target in pkl_map:
        out.append(
            _entry(quillota, archivo, target, target, FEATURES_QUILLOTA_ALT, sk, modo="pkl")
        )

    pkg_ml = "modelos_ml"
    for algo_prefix, sk in ALGOS_ML:
        for var in VARS_ML:
            target = var
            if var == "temperatura_actual":
                target = "temperatura_promedio"
            archivo = f"{algo_prefix}_{var}.joblib"
            out.append(_entry(pkg_ml, archivo, var.replace("_", " "), target, FEATURES_BASE, sk))

    av = "modelos_ml_avanzados"
    for archivo, sk in (
        ("RandomForest_Rapido_temperatura_promedio.joblib", "RandomForestRegressor"),
        ("GradientBoosting_Rapido_temperatura_promedio.joblib", "GradientBoostingRegressor"),
        ("Ridge_Optimizado_temperatura_promedio.joblib", "Ridge"),
    ):
        out.append(
            _entry(av, archivo, "temperatura promedio", "temperatura_promedio", FEATURES_BASE, sk)
        )

    din = "modelos_dinamicos"
    out.append(
        _entry(din, "RF_Temp_Promedio.joblib", "temp promedio", "temperatura_promedio", FEATURES_BASE, "RandomForestRegressor", scaler=True)
    )
    out.append(
        _entry(din, "GB_Precipitacion.joblib", "precipitacion", "precipitacion", FEATURES_BASE, "GradientBoostingRegressor", scaler=True)
    )

    ultra = "modelos_ultra_optimizados"
    out.append(
        _entry(ultra, "Ultra_Temp_Optimizado.joblib", "temp optimizado", "temperatura_promedio", FEATURES_BASE, "GradientBoostingRegressor")
    )
    out.append(
        _entry(ultra, "Ultra_Humedad_Optimizado.joblib", "humedad optimizado", "humedad_relativa", FEATURES_BASE, "RandomForestRegressor")
    )

    hib = "modelos_hibridos_rapidos"
    out.append(
        _entry(hib, "Ensemble_Rapido_Temp.joblib", "rapido temp", "temperatura_promedio", FEATURES_BASE, "VotingRegressor")
    )
    out.append(
        _entry(hib, "Voting_Rapido_Humedad.joblib", "rapido humedad", "humedad_relativa", FEATURES_BASE, "VotingRegressor")
    )

    return out
