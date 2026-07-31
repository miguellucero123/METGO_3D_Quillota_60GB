#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""M10 — board operativo multi-faena (resumen para dashboard Vue)."""

from __future__ import annotations

import logging
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from typing import Any
from zoneinfo import ZoneInfo

TZ_CHILE = ZoneInfo("America/Santiago")
logger = logging.getLogger(__name__)

_MAX_FAENAS = int(os.getenv("METGO_OPS_BOARD_MAX", "24"))
# Por defecto intenta live en todas las del board (antes 6 → resto sin_dato en frío)
_MAX_LIVE = int(os.getenv("METGO_OPS_BOARD_LIVE", "24"))
_LIVE_WORKERS = int(os.getenv("METGO_OPS_BOARD_WORKERS", "4"))

_SPATI_NIVEL = {0: "verde", 1: "amarillo", 2: "amarillo", 3: "rojo"}


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
        "enlace_ahora": f"/f/{faena['id']}/ahora",
    }


def _fila_desde_spati(faena: dict[str, Any], spati: dict[str, Any]) -> dict[str, Any]:
    """Resumen izaje desde motor SPATI cuando no hay paquete ambiental."""
    nmax = int(spati.get("nivel_maximo") or 0)
    nivel = _SPATI_NIVEL.get(nmax, "sin_dato")
    serie = spati.get("serie") or []
    primero = serie[0] if serie else {}
    v_kmh = primero.get("v_final_kmh") or primero.get("rafaga_pluma_kmh")
    raf_ms = None
    if v_kmh is not None:
        try:
            raf_ms = round(float(v_kmh) / 3.6, 2)
        except (TypeError, ValueError):
            raf_ms = None
    razon = spati.get("nivel_maximo_nombre") or f"nivel_{nmax}"
    act = {"nivel": nivel, "razones": [str(razon)]}
    return {
        "faena_id": faena["id"],
        "nombre": faena.get("nombre"),
        "lat": faena.get("lat"),
        "lon": faena.get("lon"),
        "altitud_m": faena.get("altitud_m"),
        "nivel_global": nivel,
        "izaje": act,
        "caminos": {"nivel": "sin_dato", "razones": ["ver_paquete_ambiental"]},
        "botaderos": {"nivel": "sin_dato", "razones": ["ver_paquete_ambiental"]},
        "rafaga_10m_ms": raf_ms,
        "viento_10m_ms": raf_ms,
        "temperatura_c": None,
        "pm2_5": None,
        "degradado": bool(spati.get("aviso") or spati.get("nwp_aviso")),
        "aviso": spati.get("aviso") or spati.get("nwp_aviso"),
        "paquete_en": spati.get("generado_en"),
        "enlace": f"/f/{faena['id']}/",
        "enlace_ambiente": f"/f/{faena['id']}/ambiente",
        "enlace_ahora": f"/f/{faena['id']}/ahora",
        "fuente_paquete": "spati",
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
            "nota": (
                None
                if st.get("estado_mvo") == "ok"
                else "Sin sensores en faena (esperado en minas SPATI sin IoT/SINCA)."
            ),
        }
    except Exception as exc:
        logger.debug("ops-board observado %s: %s", faena_id, exc)
        return {
            "estado_mvo": "error",
            "listo_produccion": False,
            "nota": "Error al evaluar observado",
        }


def _enrich_live(
    fid: str,
    faena: dict[str, Any],
    *,
    prefer_refresh: bool,
) -> tuple[str, dict[str, Any] | None, str | None]:
    """Devuelve (faena_id, pkg|None, fuente)."""
    from api_rest import paquete_ambiental_service as pas

    pkg = None if prefer_refresh else pas._load_lastgood(fid, as_fallback=False)
    fuente = "lastgood" if pkg else None
    if pkg and not prefer_refresh:
        return fid, pkg, fuente
    try:
        fresh = pas.construir_paquete_ambiental(fid, horas=24)
        if fresh and not fresh.get("error"):
            return (
                fid,
                fresh,
                "live" if not fresh.get("degradado") else "degraded",
            )
    except Exception as exc:
        logger.warning("ops-board live %s: %s", fid, exc)
    if pkg:
        return fid, pkg, fuente or "lastgood"
    # Fallback SPATI (izaje) — usa NWP lastgood si existe
    caps = faena.get("capacidades") or []
    if "izaje" in caps or faena.get("origen") == "spati":
        try:
            from api_rest.spati.spati_service import run_spati

            spat = run_spati(fid)
            if isinstance(spat, dict) and not spat.get("error"):
                return fid, {"__spati__": spat}, "spati"
        except Exception as exc:
            logger.warning("ops-board spati %s: %s", fid, exc)
    return fid, None, fuente or "error"


def construir_ops_board(
    faena_ids: list[str],
    *,
    refresh: bool = False,
    incluir_observado: bool = True,
) -> dict[str, Any]:
    """Resumen por faena. Lastgood en disco/memoria; live en paralelo si falta o refresh."""
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

    pending_live: list[tuple[str, dict[str, Any]]] = []
    filas_map: dict[str, dict[str, Any]] = {}
    live_used = 0

    for fid in ids:
        faena = get_faena(fid)
        if not faena:
            filas_map[fid] = {
                "faena_id": fid,
                "nombre": fid,
                "nivel_global": "sin_dato",
                "error": "faena_desconocida",
                "enlace": f"/f/{fid}/",
                "enlace_ahora": f"/f/{fid}/ahora",
                "fuente_paquete": "sin_dato",
            }
            continue
        pkg = None if refresh else pas._load_lastgood(fid, as_fallback=False)
        if pkg:
            row = _fila_desde_paquete(faena, pkg)
            row["fuente_paquete"] = "lastgood"
            filas_map[fid] = row
            if not refresh:
                continue
        pending_live.append((fid, faena))

    to_fetch = pending_live[:_MAX_LIVE]
    if to_fetch:
        workers = max(1, min(_LIVE_WORKERS, len(to_fetch)))
        with ThreadPoolExecutor(max_workers=workers) as pool:
            futs = {
                pool.submit(_enrich_live, fid, faena, prefer_refresh=refresh): (fid, faena)
                for fid, faena in to_fetch
            }
            for fut in as_completed(futs):
                fid, faena = futs[fut]
                try:
                    _, pkg, fuente = fut.result()
                except Exception as exc:
                    logger.warning("ops-board future %s: %s", fid, exc)
                    pkg, fuente = None, "error"
                live_used += 1
                if isinstance(pkg, dict) and pkg.get("__spati__"):
                    filas_map[fid] = _fila_desde_spati(faena, pkg["__spati__"])
                elif pkg:
                    row = _fila_desde_paquete(faena, pkg)
                    row["fuente_paquete"] = fuente or "live"
                    filas_map[fid] = row
                else:
                    row = _fila_desde_paquete(faena, None)
                    row["fuente_paquete"] = fuente or "sin_dato"
                    filas_map[fid] = row

    for fid, faena in pending_live[_MAX_LIVE:]:
        if fid in filas_map:
            continue
        row = _fila_desde_paquete(faena, None)
        row["fuente_paquete"] = "sin_dato"
        row["aviso"] = "Fuera del cupo live de este request; pulse Refrescar o reintente."
        filas_map[fid] = row

    filas = [filas_map[fid] for fid in ids if fid in filas_map]
    if incluir_observado:
        for row in filas:
            if row.get("error"):
                continue
            row["observado"] = _observado_lite(row["faena_id"])

    peso = {"rojo": 0, "amarillo": 1, "verde": 2, "sin_dato": 3}
    filas.sort(key=lambda r: (peso.get(str(r.get("nivel_global")), 9), r.get("nombre") or ""))

    sin_dato_n = sum(1 for r in filas if r.get("nivel_global") == "sin_dato")
    return {
        "fase": "M10",
        "generado_en": datetime.now(TZ_CHILE).isoformat(timespec="seconds"),
        "n_faenas": len(filas),
        "live_usados": live_used,
        "sin_dato": sin_dato_n,
        "filas": filas,
        "nota": (
            "Board multi-faena. Usa lastgood en disco/memoria; regenera live en paralelo "
            f"(hasta {_MAX_LIVE} faenas, {_LIVE_WORKERS} workers). "
            "«sin_observado» es normal sin sensores IoT/SINCA en la faena."
        ),
    }
