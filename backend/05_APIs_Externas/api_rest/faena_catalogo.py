#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Catálogo de faenas atmosféricas / mineras (M1 multi-faena).

Incluye:
- Paipote / Mantos Blancos (ventilación N/R/M + aire CAMS).
- Mineras SPATI (izaje grúa) como faenas con paquete ambiental y estaciones por área.
"""

from __future__ import annotations

from typing import Any

# Faenas ventilación (E7/E8) — preservar estacion_ancla y bbox dict.
FAENAS: dict[str, dict[str, Any]] = {
    "paipote": {
        "id": "paipote",
        "sitio": "copiapo",
        "nombre": "Paipote",
        "estacion_ancla": "paipote",
        "region": "Atacama · valle Copiapó",
        "modelo_ventilacion": "METGO-Ventilacion-Paipote-v1",
        "satelite_sector": "ssa",
        "bbox": {"west": -70.45, "south": -27.6, "east": -70.2, "north": -27.25},
        "capacidades": ["ventilacion", "aire", "paquete", "paquete_ambiental", "informe"],
        "industrias": ["fundicion", "mineria"],
    },
    "mantos_blancos": {
        "id": "mantos_blancos",
        "sitio": "mantos_blancos",
        "nombre": "Mantos Blancos",
        "estacion_ancla": "mb_rajo",
        "region": "Antofagasta · faena minera",
        "modelo_ventilacion": "METGO-Ventilacion-Mantos-v1",
        "satelite_sector": "ssa",
        "bbox": {"west": -70.35, "south": -23.55, "east": -69.95, "north": -23.30},
        "capacidades": ["ventilacion", "aire", "paquete", "paquete_ambiental", "informe"],
        "industrias": ["mineria"],
    },
    "ventanas_muelle": {
        "id": "ventanas_muelle",
        "sitio": "ventanas_muelle",
        "nombre": "Puerto Ventanas (Muelle)",
        "estacion_ancla": "ventanas_muelle",
        "region": "Valparaíso · Puerto",
        "modelo_ventilacion": "METGO-Ventilacion-Ventanas-v1",
        "satelite_sector": "ssa",
        "bbox": {"west": -71.6, "south": -32.9, "east": -71.4, "north": -32.6},
        "capacidades": ["izaje", "paquete_ambiental", "informe", "meteo_nwp"],
        "industrias": ["puerto", "izaje"],
    },
    "iqq": {
        "id": "iqq",
        "sitio": "iqq",
        "nombre": "Terminal Iquique (ITI)",
        "estacion_ancla": "iqq",
        "region": "Tarapacá · Puerto",
        "modelo_ventilacion": "METGO-Ventilacion-IQQ-v1",
        "satelite_sector": "ssa",
        "bbox": {"west": -70.3, "south": -20.4, "east": -70.1, "north": -20.1},
        "capacidades": ["izaje", "paquete_ambiental", "informe", "meteo_nwp"],
        "industrias": ["puerto", "izaje"],
    },
}

_ALIASES: dict[str, str] = {
    "paipote": "paipote",
    "copiapo": "paipote",
    "copiapó": "paipote",
    "mantos": "mantos_blancos",
    "mantos_blancos": "mantos_blancos",
    "mb": "mantos_blancos",
}


def _estaciones_area(sid: str, lat: float, lon: float) -> list[dict[str, Any]]:
    """Puntos por área. Mantos/Paipote usan coords canónicas del catálogo de estaciones."""
    if sid == "mantos_blancos":
        try:
            from api_rest.estaciones_catalogo import COORDS, SLUG_A_NOMBRE

            out = []
            for eid, rol in (
                ("mb_rajo", "rajo"),
                ("mb_campamento", "campamento"),
                ("mb_chancado", "chancado"),
                ("mb_ruta_acceso", "ruta"),
            ):
                c = COORDS.get(eid) or {}
                out.append(
                    {
                        "id": eid,
                        "nombre": SLUG_A_NOMBRE.get(eid) or eid,
                        "rol": rol,
                        "lat": float(c.get("lat", lat)),
                        "lon": float(c.get("lon", lon)),
                        "fuente": "seed",
                    }
                )
            return out
        except Exception:
            pass
    if sid == "paipote":
        try:
            from api_rest.estaciones_catalogo import COORDS

            c = COORDS.get("paipote") or {"lat": lat, "lon": lon}
            plat, plon = float(c["lat"]), float(c["lon"])
            return [
                {
                    "id": "paipote",
                    "nombre": "Paipote (rajo/pluma)",
                    "rol": "rajo",
                    "lat": plat,
                    "lon": plon,
                    "fuente": "seed",
                },
                {
                    "id": "paipote_campamento",
                    "nombre": "Campamento",
                    "rol": "campamento",
                    "lat": round(plat + 0.02, 5),
                    "lon": round(plon - 0.02, 5),
                    "fuente": "modelo",
                },
                {
                    "id": "paipote_chancado",
                    "nombre": "Chancado",
                    "rol": "chancado",
                    "lat": round(plat - 0.015, 5),
                    "lon": round(plon + 0.02, 5),
                    "fuente": "modelo",
                },
                {
                    "id": "paipote_botadero",
                    "nombre": "Botadero",
                    "rol": "botadero",
                    "lat": round(plat + 0.01, 5),
                    "lon": round(plon + 0.025, 5),
                    "fuente": "modelo",
                },
            ]
        except Exception:
            pass
    return [
        {
            "id": f"{sid}_rajo",
            "nombre": "Rajo / pluma",
            "rol": "rajo",
            "lat": round(lat, 5),
            "lon": round(lon, 5),
            "fuente": "modelo",
        },
        {
            "id": f"{sid}_campamento",
            "nombre": "Campamento",
            "rol": "campamento",
            "lat": round(lat + 0.02, 5),
            "lon": round(lon - 0.02, 5),
            "fuente": "modelo",
        },
        {
            "id": f"{sid}_chancado",
            "nombre": "Chancado",
            "rol": "chancado",
            "lat": round(lat - 0.015, 5),
            "lon": round(lon + 0.02, 5),
            "fuente": "modelo",
        },
        {
            "id": f"{sid}_botadero",
            "nombre": "Botadero",
            "rol": "botadero",
            "lat": round(lat + 0.01, 5),
            "lon": round(lon + 0.025, 5),
            "fuente": "modelo",
        },
    ]


def _merge_estaciones_supabase(faena_id: str, locales: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Preferir filas Supabase si existen (M4); completar con catálogo local."""
    try:
        from api_rest.integracion import estaciones_area_store

        remotas = estaciones_area_store.leer_estaciones_area(faena_id)
    except Exception:
        remotas = []
    if not remotas:
        return locales
    by_id = {e["id"]: e for e in locales}
    for r in remotas:
        by_id[r["id"]] = {
            "id": r["id"],
            "nombre": r.get("nombre"),
            "rol": r.get("rol"),
            "lat": r.get("lat"),
            "lon": r.get("lon"),
            "fuente": r.get("fuente") or "modelo",
            "altitud_m": r.get("altitud_m"),
        }
    # Orden estable por rol
    orden = {"rajo": 0, "campamento": 1, "chancado": 2, "botadero": 3, "ruta": 4}
    return sorted(by_id.values(), key=lambda x: (orden.get(str(x.get("rol")), 9), str(x.get("id"))))


def _coords_estacion(estacion_id: str) -> tuple[float | None, float | None]:
    try:
        from api_rest.estaciones_catalogo import COORDS

        c = COORDS.get(estacion_id) or COORDS.get(estacion_id.replace("_", "-"))
        if isinstance(c, dict) and "lat" in c and "lon" in c:
            return float(c["lat"]), float(c["lon"])
        if c and len(c) >= 2 and not isinstance(c, dict):
            return float(c[0]), float(c[1])
    except Exception:
        pass
    return None, None


def _enrich_ventilacion_faena(meta: dict[str, Any]) -> dict[str, Any]:
    out = dict(meta)
    lat, lon = _coords_estacion(str(meta.get("estacion_ancla") or ""))
    out["lat"] = lat
    out["lon"] = lon
    if lat is not None and lon is not None:
        locales = _estaciones_area(str(meta["id"]), lat, lon)
    else:
        locales = []
    out["estaciones_area"] = _merge_estaciones_supabase(str(meta["id"]), locales)
    out.setdefault("capacidades", ["ventilacion", "aire", "paquete_ambiental", "informe"])
    out.setdefault("industrias", ["mineria"])
    out["origen"] = "ventilacion"
    return out


def _from_spati(sitio_id: str) -> dict[str, Any] | None:
    try:
        from api_rest.spati.sitios_catalogo import get_sitio, normalizar_sitio_id
    except Exception:
        return None
    sid = normalizar_sitio_id(sitio_id)
    if not sid:
        return None
    s = get_sitio(sid)
    if not s:
        return None
    lat = float(s["lat"])
    lon = float(s["lon"])
    return {
        "id": sid,
        "nombre": s.get("nombre") or sid,
        "sitio": sid,
        "estacion_ancla": sid,
        "region": s.get("region"),
        "lat": lat,
        "lon": lon,
        "bbox": {
            "west": round(lon - 0.15, 4),
            "south": round(lat - 0.15, 4),
            "east": round(lon + 0.15, 4),
            "north": round(lat + 0.15, 4),
        },
        "altitud_m": s.get("altitud_msnm"),
        "operador": s.get("operador"),
        "capacidades": ["izaje", "paquete_ambiental", "informe", "meteo_nwp"],
        "industrias": ["mineria", "izaje"],
        "estaciones_area": _merge_estaciones_supabase(sid, _estaciones_area(sid, lat, lon)),
        "origen": "spati",
    }


def normalizar_faena_id(raw: str | None) -> str | None:
    if not raw:
        return None
    key = str(raw).strip().lower().replace(" ", "_").replace("-", "_")
    if key in _ALIASES:
        return _ALIASES[key]
    if key in FAENAS:
        return key
    try:
        from api_rest.spati.sitios_catalogo import normalizar_sitio_id

        sid = normalizar_sitio_id(raw)
        if sid:
            return sid
    except Exception:
        pass
    return None


def get_faena(faena_id: str | None) -> dict[str, Any] | None:
    nid = normalizar_faena_id(faena_id)
    if not nid:
        return None
    if nid in FAENAS:
        return _enrich_ventilacion_faena(FAENAS[nid])
    return _from_spati(nid)


def estacion_ancla(faena_id: str | None) -> str | None:
    f = get_faena(faena_id)
    return f["estacion_ancla"] if f else None


def listar_faenas(*, incluir_izaje: bool = True) -> list[dict[str, Any]]:
    out = [_enrich_ventilacion_faena(v) for v in FAENAS.values()]
    if not incluir_izaje:
        return out
    seen = {f["id"] for f in out}
    try:
        from api_rest.spati.sitios_catalogo import listar_sitios

        for s in listar_sitios():
            sid = str(s.get("sitio_id") or s.get("id") or "")
            if not sid or sid in seen:
                continue
            meta = _from_spati(sid)
            if meta:
                out.append(meta)
                seen.add(sid)
    except Exception:
        pass
    return out


def estaciones_area_faena(faena_id: str | None) -> list[dict[str, Any]]:
    f = get_faena(faena_id)
    if not f:
        return []
    return list(f.get("estaciones_area") or [])
