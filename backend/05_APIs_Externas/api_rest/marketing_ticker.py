"""Ticker de marketing (cinta WP) — datos reales agregados de paneles públicos."""
from __future__ import annotations

import logging
import time
from typing import Any

logger = logging.getLogger(__name__)

_CACHE: dict[str, Any] = {"ts": 0.0, "payload": None}
_TTL_S = 3600.0  # 1 h — alineado con refresco de cinta WP


def _viento_altura(perfil: dict[str, Any] | None, altura_m: float = 80.0) -> float | None:
    if not perfil:
        return None
    niveles = perfil.get("niveles") or []
    if not niveles:
        return None
    best = min(
        niveles,
        key=lambda n: abs(float(n.get("altura_m") or 0) - altura_m),
    )
    try:
        return round(float(best.get("v_kmh")), 1)
    except (TypeError, ValueError):
        return None


def _item(dot: str, label: str, val: str, detail: str, href: str) -> dict[str, str]:
    return {
        "dot": dot,
        "label": label,
        "val": val,
        "detail": detail,
        "href": href,
    }


def _quillota() -> dict[str, str] | None:
    from api_rest import services

    data = services.resumen_meteo("quillota")
    if not data:
        return None
    t = data.get("temperatura")
    tmin = data.get("temperatura_min")
    helada = bool(data.get("helada"))
    if helada or (isinstance(tmin, (int, float)) and tmin <= 2):
        detail = "Riesgo de helada"
    elif isinstance(tmin, (int, float)):
        detail = f"T min {tmin:.1f} °C"
    else:
        detail = "Sin riesgo de helada"
    val = f"{t:.1f} °C" if isinstance(t, (int, float)) else "—"
    return _item(
        "agro",
        "Quillota · Tº",
        val,
        detail,
        "https://metgo-quillota.pages.dev",
    )


def _ventora(sitio_id: str = "escondida") -> dict[str, str] | None:
    from api_rest.spati import run_spati

    data = run_spati(sitio_id)
    if not data or data.get("error"):
        return None
    v80 = _viento_altura(data.get("perfil_vertical_ahora"), 80.0)
    nivel = (data.get("nivel_maximo_nombre") or "").strip() or "—"
    umbrales = data.get("umbrales") or {}
    verde_max = umbrales.get("verde_max_kmh") or 26
    sitio = (data.get("sitio") or {}).get("nombre") or sitio_id
    val = f"{v80:.0f} km/h" if isinstance(v80, (int, float)) else "—"
    detail = f"Nivel 72 h: {nivel} · umbral {verde_max:g}"
    return _item(
        "izaje",
        f"VENTORA · {sitio} · Viento 80 m",
        val,
        detail,
        "https://metgo-spati.pages.dev",
    )


def _copiapo() -> dict[str, str] | None:
    from api_rest.aire_service import aire_actual

    data = aire_actual("copiapo_centro")
    if not data:
        return None
    icap = data.get("icap")
    etiqueta = data.get("etiqueta") or data.get("nivel") or "—"
    val = f"{icap:.0f}" if isinstance(icap, (int, float)) else "—"
    return _item(
        "aire",
        "Copiapó · ICAP",
        val,
        str(etiqueta).capitalize(),
        "https://metgo-copiapo.pages.dev",
    )


def _paine() -> dict[str, str] | None:
    from api_rest import services

    data = services.resumen_meteo("base_torres")
    if not data:
        return None
    t = data.get("temperatura")
    v = data.get("viento")
    val_t = f"{t:.1f} °C" if isinstance(t, (int, float)) else "—"
    val_v = f"{v:.0f} km/h" if isinstance(v, (int, float)) else "—"
    return _item(
        "outdoor",
        "Paine · Tº",
        val_t,
        f"Viento {val_v}",
        "https://metgo-paine.pages.dev",
    )


def _mantos() -> dict[str, str] | None:
    from api_rest.operaciones_service import alertas_turno

    data = alertas_turno("mantos_blancos", "dia")
    if not data:
        return None
    bloqueo = bool(data.get("hay_bloqueo"))
    peores = []
    for est in data.get("estaciones") or []:
        acts = est.get("actividades") or {}
        for nombre, info in acts.items():
            if isinstance(info, dict) and info.get("nivel_peor"):
                peores.append(str(info["nivel_peor"]))
    orden = {"verde": 0, "amarillo": 1, "naranja": 2, "rojo": 3}
    peor = "verde"
    for n in peores:
        if orden.get(n, 0) > orden.get(peor, 0):
            peor = n
    val = "Bloqueo turno" if bloqueo else "Operación OK"
    return _item(
        "aire",
        "Mantos Blancos · Turno",
        val,
        f"Nivel peor: {peor}",
        "https://metgo-mantos.pages.dev",
    )


def build_marketing_ticker() -> dict[str, Any]:
    """Agrega ítems de cinta; tolera fallos parciales; cache 1 h."""
    now = time.time()
    cached = _CACHE.get("payload")
    if cached and (now - float(_CACHE.get("ts") or 0)) < _TTL_S:
        return cached

    builders = (
        ("quillota", _quillota),
        ("ventora", _ventora),
        ("copiapo", _copiapo),
        ("paine", _paine),
        ("mantos", _mantos),
    )
    items: list[dict[str, str]] = []
    errores: dict[str, str] = {}
    for key, fn in builders:
        try:
            item = fn()
            if item:
                items.append(item)
        except Exception as exc:  # noqa: BLE001
            logger.warning("ticker %s: %s", key, exc)
            errores[key] = str(exc)[:160]

    payload = {
        "actualizado": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "ttl_s": int(_TTL_S),
        "items": items,
        "n": len(items),
        "errores": errores or None,
        "fuente": "metgo_api",
    }
    _CACHE["ts"] = now
    _CACHE["payload"] = payload
    return payload
