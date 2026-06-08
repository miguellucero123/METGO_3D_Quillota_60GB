#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Estado MLOps desde registry METGO (dashboard 8505 / alineado con Vue /ml)."""

from __future__ import annotations

from typing import Any

VARIABLES_ML = [
    "temperatura_max",
    "temperatura_min",
    "humedad",
    "precipitacion",
    "viento",
]

LABELS_VAR = {
    "temperatura_max": "T° máx",
    "temperatura_min": "T° mín",
    "humedad": "Humedad",
    "precipitacion": "Lluvia",
    "viento": "Viento",
}


def cargar_estado_ml(estacion_id: str = "quillota", sincronizar: bool = False) -> dict[str, Any]:
    from api_rest import ml_services
    from api_rest.integracion import ml_registry
    from api_rest.services import resumen_meteo

    if sincronizar:
        ml_services.sincronizar_registro()

    resumen_ops = ml_services.resumen_mlops()
    modelos = ml_services.listar_modelos()
    meteo = resumen_meteo(estacion_id) or {}

    servibles = [m for m in modelos if m.get("servible")]
    vars_ok = [v for v in VARIABLES_ML if any(m.get("variable") == v for m in servibles)]
    batch = ml_registry.prediccion_batch(vars_ok or None, estacion_id) if servibles else []

    filas_chart = []
    for item in batch:
        var = item.get("variable", "")
        pred = item.get("prediccion") or {}
        val_pred = pred.get("prediccion") if isinstance(pred, dict) else pred
        if item.get("ok") and val_pred is not None and "error" not in pred:
            campo = {
                "temperatura_max": "temperatura_max",
                "temperatura_min": "temperatura_min",
                "humedad": "humedad",
                "precipitacion": "precipitacion",
                "viento": "viento",
            }.get(var)
            actual = pred.get("valor_actual")
            if actual is None:
                actual = meteo.get(campo) or meteo.get("temperatura")
            filas_chart.append(
                {
                    "variable": LABELS_VAR.get(var, var),
                    "variable_key": var,
                    "actual": actual,
                    "prediccion": val_pred,
                    "tipo_dato": pred.get("tipo_dato") or meteo.get("tipo_dato"),
                    "unidad": "°C" if "temp" in var else (" mm" if var == "precipitacion" else (" km/h" if var == "viento" else "%")),
                }
            )

    return {
        "estacion_id": estacion_id,
        "resumen_ops": resumen_ops,
        "modelos": modelos,
        "servibles": len(servibles),
        "total": len(modelos),
        "meteo": meteo,
        "proyecciones": filas_chart,
    }
