#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""M10 — board operativo multi-faena (resumen para dashboard Vue)."""

from __future__ import annotations

import logging
import os
from datetime import datetime
from typing import Any
from zoneinfo import ZoneInfo

TZ_CHILE = ZoneInfo("America/Santiago")
logger = logging.getLogger(__name__)

_MAX_FAENAS = int(os.getenv("METGO_OPS_BOARD_MAX", "24"))
_MAX_LIVE = int(os.getenv("METGO_OPS_BOARD_LIVE", "6"))


def _fila_desde_paquete(faena: dict[str, Any], pkg: dict[str, Any] | None) -> dict[str, Any]:
    a = (pkg or {}).get("actual") or {}
    flags = (pkg or {}).get("flags") or {}
    ops = ((pkg or {}).get("operaciones") or {}).get("actividades") or {}
    fuente = (pkg or {}).get("fuente") or {}

    def act(aid: str) -> dict[str, Any]:
        av = ops.get(aid) or {}
        return {
            "nivel": av.get("nivel") or "sin_dato",
            "razones": list(av.get("razones") or []),
        }

    return {
        "faena_id": faena["id"],
        "nombre": faena.get("nombre"),
        "lat": faena.get("lat"),
        "lon": faena.get("lon"),
        "altitud_m": faena.get("altitud_m"),
        "nivel_global": flags.get("nivel_global") or ("sin_dato" if not pkg else "verde"),
        "izaje": act("izaje"),
        "caminos": act("caminos"),
        "botaderos": act("botaderos"),
        "rafaga_10m_ms": a.get("rafaga_10m_ms"),
        "viento_10m_ms": a.get("viento_10m_ms"),
        "temperatura_c": a.get("temperatura_c"),
        "pm2_5": a.get("pm2_5"),
        "degradado": bool((pkg or {}).get("degradado") or fuente.get("meteo") == "synthetic_degraded"),
        "aviso": (pkg or {}).get("aviso"),
        "paquete_en": (pkg or {}).get("generado_en"),
        "enlace": f"/f/{faena['id']}/",
        "enlace_ambiente": f"/f/{faena['id']}/ambiente",
    }


def _observado_lite(faena_id: str) -> dict[str, Any]:
    try:
        from api_rest.m7_observado_service import estado_observado_faena

        st = estado_observado_faena(faena_id, dias=14)
        return {
            "estado_mvo": st.get("estado_mvo"),
            "listo_produccion": st.get("listo_produccion"),
            "aire_pares": (st.get("aire") or {}).get("n_pares"),
            "iot_lecturas": ((st.get("iot") or {}).get("n_lecturas")),
        }
    except Exception as exc:
        logger.debug("ops-board observado %s: %s", faena_id, exc)
        return {"estado_mvo": "error", "listo_produccion": False}


def construir_ops_board(
    faena_ids: list[str],
    *,
    refresh: bool = False,
    incluir_observado: bool = True,
) -> dict[str, Any]:
    """Resumen por faena. Preferencia lastgood; live limitado si refresh."""
    from api_rest.faena_catalogo import get_faena
    from api_rest import paquete_ambiental_service as pas

    ids: list[str] = []
    seen: set[str] = set()
    for raw in faena_ids:
        fid = str(raw or "").strip().lower()
        if not fid or fid in seen:
            continue
        seen.add(fid)
        ids.append(fid)
        if len(ids) >= _MAX_FAENAS:
            break

    filas: list[dict[str, Any]] = []
    live_used = 0
    for fid in ids:
        faena = get_faena(fid)
        if not faena:
            filas.append(
                {
                    "faena_id": fid,
                    "nombre": fid,
                    "nivel_global": "sin_dato",
                    "error": "faena_desconocida",
                    "enlace": f"/f/{fid}/",
                }
            )
            continue
        pkg = pas._load_lastgood(fid)
        fuente_pkg = "lastgood" if pkg else None
        if (refresh or not pkg) and live_used < _MAX_LIVE:
            try:
                fresh = pas.construir_paquete_ambiental(fid, horas=24)
                if fresh and not fresh.get("error"):
                    pkg = fresh
                    fuente_pkg = "live" if not fresh.get("degradado") else "degraded"
                live_used += 1
            except Exception as exc:
                logger.warning("ops-board live %s: %s", fid, exc)
                fuente_pkg = fuente_pkg or "error"
        row = _fila_desde_paquete(faena, pkg)
        row["fuente_paquete"] = fuente_pkg or "sin_dato"
        if incluir_observado:
            row["observado"] = _observado_lite(fid)
        filas.append(row)

    # Orden: rojo → amarillo → resto
    peso = {"rojo": 0, "amarillo": 1, "verde": 2, "sin_dato": 3}
    filas.sort(key=lambda r: (peso.get(str(r.get("nivel_global")), 9), r.get("nombre") or ""))

    return {
        "fase": "M10",
        "generado_en": datetime.now(TZ_CHILE).isoformat(timespec="seconds"),
        "n_faenas": len(filas),
        "live_usados": live_used,
        "filas": filas,
        "nota": (
            "Board multi-faena. Sin ?refresh=1 usa lastgood (rápido). "
            f"Refresh live limitado a {_MAX_LIVE} faenas por request."
        ),
    }
