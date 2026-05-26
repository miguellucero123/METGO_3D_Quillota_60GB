#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Historial de alertas (módulo 07) + umbrales módulo 01."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Umbrales alineados con sistema_alertas_automaticas (01)
UMBRALES_01 = {
    "temperatura_maxima": 35.0,
    "temperatura_minima": -2.0,
    "precipitacion_intensa": 20.0,
    "viento_fuerte": 40.0,
    "humedad_alta": 90.0,
    "humedad_baja": 30.0,
}


def _path() -> Path:
    for p in Path(__file__).resolve().parents:
        if (p / "metgo_paths.py").exists():
            gd = p / "backend" / "08_Gestion_Datos" / "datos_runtime"
            gd.mkdir(parents=True, exist_ok=True)
            return gd / "alertas_historial.json"
    return Path("alertas_historial.json")


def _load() -> list[dict[str, Any]]:
    path = _path()
    if not path.is_file():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        return []


def _save(items: list[dict[str, Any]]) -> None:
    _path().write_text(
        json.dumps(items[-500:], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def evaluar_umbrales_01(resumen: dict[str, Any], estacion_id: str) -> list[dict[str, Any]]:
    alertas = []
    if not resumen:
        return alertas
    t_max = float(resumen.get("temperatura_max", 0))
    t_min = float(resumen.get("temperatura_min", 0))
    precip = float(resumen.get("precipitacion", 0))
    viento = float(resumen.get("viento", 0))
    humedad = float(resumen.get("humedad", 0))

    checks = [
        (t_max >= UMBRALES_01["temperatura_maxima"], "warning", f"Temperatura máxima extrema ({t_max}°C)"),
        (t_min <= UMBRALES_01["temperatura_minima"], "warning", f"Riesgo helada ({t_min}°C)"),
        (precip >= UMBRALES_01["precipitacion_intensa"], "warning", f"Precipitación intensa ({precip} mm)"),
        (viento >= UMBRALES_01["viento_fuerte"], "warning", f"Viento fuerte ({viento} km/h)"),
        (humedad >= UMBRALES_01["humedad_alta"], "info", f"Humedad muy alta ({humedad}%)"),
        (humedad <= UMBRALES_01["humedad_baja"], "info", f"Humedad baja ({humedad}%)"),
    ]
    for ok, nivel, msg in checks:
        if ok:
            alertas.append(
                {
                    "nivel": nivel,
                    "estacion_id": estacion_id,
                    "mensaje": msg,
                    "origen": "modulo_01_umbrales",
                }
            )
    return alertas


def registrar_alertas(alertas: list[dict[str, Any]]) -> None:
    if not alertas:
        return
    items = _load()
    ts = datetime.now(timezone.utc).isoformat()
    try:
        from api_rest.integracion import notificaciones
    except ImportError:
        notificaciones = None
    for a in alertas:
        if a.get("nivel") == "info" and "normales" in (a.get("mensaje") or "").lower():
            continue
        items.append({**a, "registrado_en": ts})
        if notificaciones:
            try:
                notificaciones.enviar_alerta_critica(a)
            except Exception:
                pass
    _save(items)


def listar_historial(estacion_id: str | None = None, limite: int = 50) -> list[dict[str, Any]]:
    items = _load()
    if estacion_id:
        items = [x for x in items if x.get("estacion_id") == estacion_id]
    return sorted(items, key=lambda x: x.get("registrado_en", ""), reverse=True)[:limite]
