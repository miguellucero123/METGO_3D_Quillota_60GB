#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Evalúa el pronóstico portuario real (VENTORA Izaje Mar) y registra
incidentes estructurados (ráfaga real, umbral cruzado, hora UTC) en
`alertas_store`, para que el informe de incidentes deje de ser un stub.

Antes de este módulo, `_build_alerts()`/`_build_alertas_resonancia()` en
`puerto_pronostico_service.py` calculaban alertas por request pero nunca se
persistían — no existía ningún historial real de eventos de suspensión.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)

# Solo se registran alertas cuya ventana ya empezó o empieza pronto — evita
# convertir alertas especulativas de horizonte lejano (72h) en "incidentes".
_HORIZONTE_REGISTRO_HORAS = 6


def _dentro_de_horizonte(timestamp_iso: str | None) -> bool:
    if not timestamp_iso:
        return False
    try:
        ts = datetime.fromisoformat(str(timestamp_iso).replace("Z", "+00:00"))
    except ValueError:
        return False
    if ts.tzinfo is None:
        ts = ts.replace(tzinfo=timezone.utc)
    delta_h = (ts - datetime.now(timezone.utc)).total_seconds() / 3600.0
    return -1.0 <= delta_h <= _HORIZONTE_REGISTRO_HORAS


def evaluar_puerto_y_registrar_incidentes(
    sitio_id: str, *, forzar: bool = False
) -> dict[str, Any]:
    """Corre el pronóstico real del puerto y persiste los eventos de alerta
    imminentes (viento sostenido, resonancia pendular) como incidentes
    estructurados. Idempotente: `alertas_store` deduplica por (sitio,
    mensaje) dentro de una ventana de 6 h, así que correr esto cada 15-20
    min no duplica el mismo evento en curso."""
    from api_rest.spati.puerto_pronostico_service import generar_pronostico_puerto

    sid = (sitio_id or "").strip().lower()
    data = generar_pronostico_puerto(sid, hours=24)
    if data.get("error"):
        return {"sitio_id": sid, "ok": False, "error": data.get("error"), "registrados": 0}

    nombre = data.get("nombre") or sid
    alerts = data.get("alerts") or []
    candidatos: list[dict[str, Any]] = []

    for a in alerts:
        ts = a.get("timestamp")
        if not forzar and not _dentro_de_horizonte(ts):
            continue
        tipo = a.get("type")
        if tipo == "sustained_wind":
            nivel_txt = "critical" if a.get("level") == "RED" else "warning"
            mensaje = (
                f"Viento sostenido en {nombre}: {a.get('wind_kmh')} km/h "
                f"(umbral {a.get('threshold_kmh')} km/h) desde {ts}"
            )
            candidatos.append(
                {
                    "nivel": nivel_txt,
                    "estacion_id": sid,
                    "mensaje": mensaje,
                    "origen": "puerto_incidente",
                    "tipo_incidente": "sustained_wind",
                    "valid_time": ts,
                    "viento_kmh": a.get("wind_kmh"),
                    "umbral_kmh": a.get("threshold_kmh"),
                    "duracion_horas": a.get("duration_hours"),
                }
            )
        elif tipo == "pendulum_resonance":
            mensaje = (
                f"Riesgo de resonancia pendular en {nombre}: delta "
                f"{a.get('delta_s')} s desde {ts}"
            )
            candidatos.append(
                {
                    "nivel": "critical",
                    "estacion_id": sid,
                    "mensaje": mensaje,
                    "origen": "puerto_incidente",
                    "tipo_incidente": "pendulum_resonance",
                    "valid_time": ts,
                    "delta_s": a.get("delta_s"),
                    "duracion_horas": a.get("duration_hours"),
                }
            )

    registrados = 0
    if candidatos:
        try:
            from api_rest.integracion import alertas_store

            antes = len(alertas_store.filtrar_por_cadencia(candidatos))
            alertas_store.registrar_alertas(candidatos)
            registrados = antes
        except Exception as exc:
            logger.warning("puerto_alert_job %s: no se pudo registrar (%s)", sid, exc)
            return {
                "sitio_id": sid,
                "ok": False,
                "error": str(exc),
                "candidatos": len(candidatos),
                "registrados": 0,
            }

    return {
        "sitio_id": sid,
        "ok": True,
        "candidatos": len(candidatos),
        "registrados": registrados,
    }


def evaluar_puertos(sitios: list[str] | None = None, *, forzar: bool = False) -> dict[str, Any]:
    ids = sitios or ["iqq", "ventanas_muelle", "anf", "vlp", "san", "pmc"]
    detalle = []
    n_ok = 0
    n_reg = 0
    for sid in ids:
        try:
            r = evaluar_puerto_y_registrar_incidentes(sid, forzar=forzar)
        except Exception as exc:
            r = {"sitio_id": sid, "ok": False, "error": str(exc), "registrados": 0}
        detalle.append(r)
        if r.get("ok"):
            n_ok += 1
        n_reg += int(r.get("registrados") or 0)
    return {"fase": "puerto_incidentes", "sitios": len(ids), "ok": n_ok, "registrados": n_reg, "detalle": detalle}
