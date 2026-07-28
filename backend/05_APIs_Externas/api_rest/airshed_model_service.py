#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""METGO Airshed Modeler (MAM) — proxy operativo inspirado en AERMOD/CALPUFF.

No ejecuta binarios EPA/CALPUFF (licencia, Fortran, HPC). En su lugar:

  01 Entradas     → topografía bbox, estaciones, emisiones seed
  02 Prep         → grilla UTM-like lon/lat, estabilidad
  03 Meteo 3D     → viento + PBL desde Open-Meteo / dispersion_service
  04 Dispersión   → pluma gaussiana a nivel suelo (AERMOD-lite) + aporte estaciones
  05 Postproceso  → máximos, contornos umbral, vectores de viento, frames horarios

Innovación regional: airshed minero-urbano Copiapó (inversión, camanchaca,
fuentes punta_del_cobre / paipote) integrado al SPA METGO.
"""

from __future__ import annotations

import math
from datetime import datetime
from typing import Any
from zoneinfo import ZoneInfo

from api_rest.estaciones_catalogo import ESTACIONES_POR_SITIO, SLUG_A_NOMBRE

TZ_CHILE = ZoneInfo("America/Santiago")

# Dominios por sitio (bbox mapa + airshed)
BBOX_POR_SITIO: dict[str, dict[str, float]] = {
    "copiapo": {"west": -70.45, "south": -27.60, "east": -70.20, "north": -27.25},
    "mantos_blancos": {"west": -70.35, "south": -23.55, "east": -69.95, "north": -23.30},
}

# Fuentes seed por sitio (Q relativo µg/s — visualización operativa)
FUENTES_POR_SITIO: dict[str, list[dict[str, Any]]] = {
    "copiapo": [
        {
            "id": "punta_del_cobre",
            "nombre": "Punta del Cobre (faena)",
            "lon": -70.21,
            "lat": -27.44,
            "q": 180.0,
            "altura_m": 30.0,
            "tipo": "mineria",
        },
        {
            "id": "paipote",
            "nombre": "Paipote (industrial)",
            "lon": -70.2853,
            "lat": -27.4064,
            "q": 120.0,
            "altura_m": 25.0,
            "tipo": "industrial",
        },
        {
            "id": "copiapo_centro",
            "nombre": "Área urbana (área source)",
            "lon": -70.3323,
            "lat": -27.3668,
            "q": 40.0,
            "altura_m": 10.0,
            "tipo": "urbano",
        },
    ],
    "mantos_blancos": [
        {
            "id": "mb_rajo",
            "nombre": "Rajo Mantos Blancos",
            "lon": -70.06,
            "lat": -23.43,
            "q": 200.0,
            "altura_m": 35.0,
            "tipo": "mineria",
        },
        {
            "id": "mb_chancado",
            "nombre": "Chancado (polvo)",
            "lon": -70.07,
            "lat": -23.44,
            "q": 110.0,
            "altura_m": 20.0,
            "tipo": "proceso",
        },
        {
            "id": "mb_ruta_acceso",
            "nombre": "Ruta de acceso (tráfico)",
            "lon": -70.2,
            "lat": -23.5,
            "q": 55.0,
            "altura_m": 5.0,
            "tipo": "transporte",
        },
    ],
}

# Compat legacy
BBOX = BBOX_POR_SITIO["copiapo"]
FUENTES_SEED = FUENTES_POR_SITIO["copiapo"]


def _dominio(sitio: str) -> tuple[dict[str, float], list[dict[str, Any]]]:
    bbox = BBOX_POR_SITIO.get(sitio) or BBOX_POR_SITIO["copiapo"]
    fuentes = FUENTES_POR_SITIO.get(sitio) or FUENTES_POR_SITIO["copiapo"]
    return bbox, fuentes

PIPELINE = [
    {
        "paso": 1,
        "id": "entradas",
        "titulo": "Datos de entrada",
        "detalle": "Topografía bbox, uso de suelo proxy, estaciones ICAP, fuentes seed",
        "tags": ["Topografía", "Estaciones", "Emisiones"],
    },
    {
        "paso": 2,
        "id": "prep",
        "titulo": "Preprocesamiento",
        "detalle": "Grilla lon/lat del airshed y parámetros de estabilidad",
        "tags": ["Geofísica", "Coordenadas", "Estabilidad"],
    },
    {
        "paso": 3,
        "id": "meteo",
        "titulo": "Meteorología 3D (proxy CALMET)",
        "detalle": "Viento 10 m, PBL e inversión desde Forecast/dispersión METGO",
        "tags": ["Viento 3D", "Estabilidad", "Altura de mezcla"],
    },
    {
        "paso": 4,
        "id": "dispersion",
        "titulo": "Dispersión (proxy AERMOD/CALPUFF)",
        "detalle": "Pluma gaussiana suelo + fusión con PM observado/modelo en estaciones",
        "tags": ["Emisiones", "Transporte", "Mezcla"],
    },
    {
        "paso": 5,
        "id": "post",
        "titulo": "Postproceso (proxy CALPOST)",
        "detalle": "Máximos, rankings, frames horarios y vectores de viento",
        "tags": ["Promedios", "Máximos", "Animación"],
    },
]


def _estabilidad_clase(inversion: bool, viento_ms: float, pbl_m: float | None) -> str:
    """Clase Pasquill-Gifford simplificada (A–F)."""
    u = max(0.1, float(viento_ms or 0.5))
    pbl = float(pbl_m) if pbl_m is not None else 400.0
    if inversion or pbl < 120:
        return "F" if u < 2 else "E"
    if u < 2:
        return "A"
    if u < 3:
        return "B"
    if u < 5:
        return "C"
    return "D"


def _sigma(x_m: float, clase: str) -> tuple[float, float]:
    """σy, σz (m) — parametrización tipo Briggs open-country (proxy AERMOD rural)."""
    x = max(10.0, abs(x_m)) / 1000.0  # km
    # σy ≈ a * x^0.894 ; σz ≈ b * x^c  (valores tipificados)
    table = {
        "A": (213.0, 440.0, 1.0),
        "B": (156.0, 160.0, 0.95),
        "C": (104.0, 80.0, 0.90),
        "D": (68.0, 45.0, 0.85),
        "E": (50.5, 30.0, 0.80),
        "F": (34.0, 18.0, 0.75),
    }
    a, b, c = table.get(clase, table["D"])
    sy = a * (x**0.894)
    sz = b * (x**c)
    return max(sy, 5.0), max(sz, 3.0)


def _gauss_suelo(
    dx_m: float,
    dy_m: float,
    u: float,
    q: float,
    h_stack: float,
    clase: str,
) -> float:
    """Concentración relativa (µg/m³ proxy) en receptor a sotavento."""
    if dx_m <= 0:
        return 0.0
    u_eff = max(0.35, float(u))
    sy, sz = _sigma(dx_m, clase)
    # Término vertical reflexión simple (suelo)
    vert = math.exp(-0.5 * (h_stack / sz) ** 2)
    horiz = math.exp(-0.5 * (dy_m / sy) ** 2)
    c = (q / (math.pi * sy * sz * u_eff)) * horiz * vert
    return max(0.0, c)


def _rot_wind_frame(east_m: float, north_m: float, dir_from_deg: float) -> tuple[float, float]:
    """Transforma ENU → ejes viento (x sotavento, y transversal). dir = FROM meteo."""
    # Hacia donde sopla
    to_rad = math.radians((dir_from_deg + 180.0) % 360.0)
    # x positivo sotavento
    x = east_m * math.sin(to_rad) + north_m * math.cos(to_rad)
    y = -east_m * math.cos(to_rad) + north_m * math.sin(to_rad)
    return x, y


def _m_per_deg(lat: float) -> tuple[float, float]:
    m_lat = 111_320.0
    m_lon = 111_320.0 * math.cos(math.radians(lat))
    return m_lon, m_lat


def _meteo_frame(estacion_ref: str = "copiapo_centro") -> dict[str, Any]:
    from api_rest import dispersion_service

    serie = dispersion_service.dispersion_horaria(estacion_ref, horas=24) or []
    if not serie:
        return {
            "fecha_hora": datetime.now(TZ_CHILE).isoformat(timespec="minutes"),
            "viento_velocidad": 2.0,
            "viento_direccion": 180.0,
            "altura_capa_limite": 300.0,
            "inversion": False,
            "indice_dispersion": 50.0,
            "potencial_dispersion": "moderada",
        }
    f0 = serie[0]
    return {
        "fecha_hora": f0.get("fecha_hora"),
        "viento_velocidad": float(f0.get("viento_velocidad") or 1.5),
        "viento_direccion": float(f0.get("viento_direccion") or 180.0),
        "altura_capa_limite": f0.get("altura_capa_limite"),
        "inversion": bool(f0.get("inversion")),
        "indice_dispersion": f0.get("indice_dispersion"),
        "potencial_dispersion": f0.get("potencial_dispersion"),
        "serie": serie[:12],
    }


def _pm_estaciones(sitio: str) -> dict[str, float]:
    """PM10 actual por estación (aporte de fusión campo)."""
    from api_rest import aire_service

    out: dict[str, float] = {}
    for slug in ESTACIONES_POR_SITIO.get(sitio, []):
        try:
            a = aire_service.aire_actual(slug)
        except Exception:
            a = None
        if not a:
            continue
        val = a.get("pm10")
        if val is None:
            val = a.get("pm2_5")
        if val is not None:
            try:
                out[slug] = float(val)
            except (TypeError, ValueError):
                pass
    return out


def _idw(lon: float, lat: float, samples: dict[str, tuple[float, float, float]], power: float = 2.0) -> float:
    """samples: slug -> (lon, lat, value)."""
    if not samples:
        return 0.0
    num = 0.0
    den = 0.0
    for _slug, (slon, slat, val) in samples.items():
        d2 = (lon - slon) ** 2 + (lat - slat) ** 2
        if d2 < 1e-12:
            return val
        w = 1.0 / (d2 ** (power / 2.0))
        num += w * val
        den += w
    return num / den if den else 0.0


def _build_grid(
    meteo: dict[str, Any],
    nx: int = 36,
    ny: int = 36,
    sitio: str = "copiapo",
) -> dict[str, Any]:
    bbox, fuentes = _dominio(sitio)
    u = float(meteo["viento_velocidad"])
    dir_from = float(meteo["viento_direccion"])
    pbl = meteo.get("altura_capa_limite")
    clase = _estabilidad_clase(bool(meteo.get("inversion")), u, pbl)
    mid_lat = (bbox["south"] + bbox["north"]) / 2
    m_lon, m_lat = _m_per_deg(mid_lat)

    # Muestras estación para fusión
    pm_map = _pm_estaciones(sitio)
    samples: dict[str, tuple[float, float, float]] = {}
    for slug, val in pm_map.items():
        from api_rest.estaciones_catalogo import COORDS

        c = COORDS.get(slug)
        if c:
            samples[slug] = (c["lon"], c["lat"], val)

    lons = [
        bbox["west"] + (bbox["east"] - bbox["west"]) * (i + 0.5) / nx for i in range(nx)
    ]
    lats = [
        bbox["south"] + (bbox["north"] - bbox["south"]) * (j + 0.5) / ny for j in range(ny)
    ]

    values: list[list[float]] = []
    vmax = 0.0
    vmax_lon = lons[0]
    vmax_lat = lats[0]
    heat_points: list[dict[str, Any]] = []

    for j, lat in enumerate(lats):
        row: list[float] = []
        for i, lon in enumerate(lons):
            c_plume = 0.0
            for src in fuentes:
                east = (lon - src["lon"]) * m_lon
                north = (lat - src["lat"]) * m_lat
                x, y = _rot_wind_frame(east, north, dir_from)
                c_plume += _gauss_suelo(x, y, u, src["q"], float(src["altura_m"]), clase)
            c_obs = _idw(lon, lat, samples) if samples else 0.0
            # Fusión: modelo + 35% campo observado/CAMS
            c = round(c_plume + 0.35 * c_obs, 3)
            row.append(c)
            if c > vmax:
                vmax = c
                vmax_lon, vmax_lat = lon, lat
            if c > 0.05:
                heat_points.append(
                    {
                        "type": "Feature",
                        "properties": {"c": c, "w": min(1.0, c / max(vmax, 0.2))},
                        "geometry": {"type": "Point", "coordinates": [lon, lat]},
                    }
                )
        values.append(row)

    # Vectores de viento (grilla gruesa)
    wind_vectors: list[dict[str, Any]] = []
    step = max(1, nx // 8)
    to_deg = (dir_from + 180.0) % 360.0
    for j in range(0, ny, step):
        for i in range(0, nx, step):
            wind_vectors.append(
                {
                    "lon": lons[i],
                    "lat": lats[j],
                    "dir_to": round(to_deg, 1),
                    "dir_from": round(dir_from, 1),
                    "speed_ms": round(u, 2),
                }
            )

    return {
        "nx": nx,
        "ny": ny,
        "lons": [round(x, 5) for x in lons],
        "lats": [round(y, 5) for y in lats],
        "values": values,
        "unidad": "µg/m³ (proxy)",
        "contaminante": "pm10_equiv",
        "clase_estabilidad": clase,
        "max": {"value": vmax, "lon": round(vmax_lon, 5), "lat": round(vmax_lat, 5)},
        "heat_geojson": {"type": "FeatureCollection", "features": heat_points},
        "wind_vectors": wind_vectors,
        "fuentes": fuentes,
        "estaciones_pm": pm_map,
        "bbox": bbox,
    }


def modelar_airshed(
    sitio: str = "copiapo",
    nx: int = 32,
    ny: int = 32,
    frames: int = 6,
) -> dict[str, Any]:
    """Genera campo de concentración + meteo + pipeline (MVP MAM)."""
    sitio = (sitio or "copiapo").strip().lower()
    if sitio not in ESTACIONES_POR_SITIO:
        return {"error": "sitio_desconocido", "sitio": sitio}

    nx = max(12, min(int(nx), 48))
    ny = max(12, min(int(ny), 48))
    frames = max(1, min(int(frames), 12))

    meteo = _meteo_frame(
        "copiapo_centro" if sitio == "copiapo" else ESTACIONES_POR_SITIO[sitio][0]
    )
    serie = meteo.pop("serie", []) or []
    bbox, _fuentes = _dominio(sitio)

    frame_list: list[dict[str, Any]] = []
    # Frame 0 = ahora
    g0 = _build_grid(meteo, nx=nx, ny=ny, sitio=sitio)
    frame_list.append(
        {
            "t": 0,
            "fecha_hora": meteo.get("fecha_hora"),
            "meteo": {
                "viento_velocidad": meteo["viento_velocidad"],
                "viento_direccion": meteo["viento_direccion"],
                "altura_capa_limite": meteo.get("altura_capa_limite"),
                "inversion": meteo.get("inversion"),
                "indice_dispersion": meteo.get("indice_dispersion"),
                "potencial_dispersion": meteo.get("potencial_dispersion"),
                "clase_estabilidad": g0["clase_estabilidad"],
            },
            "grid": g0,
        }
    )

    # Frames adicionales desde serie horaria (recalcula con viento de cada hora)
    for t, f in enumerate(serie[1:frames], start=1):
        m = {
            "fecha_hora": f.get("fecha_hora"),
            "viento_velocidad": float(f.get("viento_velocidad") or meteo["viento_velocidad"]),
            "viento_direccion": float(f.get("viento_direccion") or meteo["viento_direccion"]),
            "altura_capa_limite": f.get("altura_capa_limite"),
            "inversion": bool(f.get("inversion")),
            "indice_dispersion": f.get("indice_dispersion"),
            "potencial_dispersion": f.get("potencial_dispersion"),
        }
        g = _build_grid(m, nx=nx, ny=ny, sitio=sitio)
        frame_list.append(
            {
                "t": t,
                "fecha_hora": m["fecha_hora"],
                "meteo": {
                    **{k: m[k] for k in (
                        "viento_velocidad",
                        "viento_direccion",
                        "altura_capa_limite",
                        "inversion",
                        "indice_dispersion",
                        "potencial_dispersion",
                    )},
                    "clase_estabilidad": g["clase_estabilidad"],
                },
                "grid": g,
            }
        )

    return {
        "modelo": "METGO-Airshed-v1",
        "nombre": "METGO Airshed Modeler",
        "inspiracion": "AERMOD + CALMET/CALPUFF/CALPOST (proxy operativo open-source)",
        "nota": (
            "Campo proxy para decisión minera-urbana; no sustituye modelación "
            "regulatoria con AERMOD/CALPUFF certificados."
        ),
        "sitio": sitio,
        "bbox": bbox,
        "pipeline": PIPELINE,
        "estaciones": [
            {"id": s, "nombre": SLUG_A_NOMBRE.get(s, s)} for s in ESTACIONES_POR_SITIO.get(sitio, [])
        ],
        "frame_activo": 0,
        "frames": frame_list,
        "generado": datetime.now(TZ_CHILE).isoformat(timespec="seconds"),
    }
