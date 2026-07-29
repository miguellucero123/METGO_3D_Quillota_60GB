#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""M7 — activación observado demo + estado de readiness por faena.

Sin API SINCA pública: usa plantilla CSV del repo (o METGO_SINCA_CSV_DIR)
para escribir `aire_registros` (tipo_dato=observado) y pares modelo sintéticos
alineados, más lecturas IoT de demostración.
"""

from __future__ import annotations

import csv
import shutil
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

# Slugs demo por faena (estación ancla aire)
_FAENA_SLUGS: dict[str, list[str]] = {
    "paipote": ["paipote"],
    "mantos_blancos": ["mb_rajo"],
    "escondida": ["escondida_rajo", "escondida"],
}


def _repo_root() -> Path:
    for p in Path(__file__).resolve().parents:
        if (p / "metgo_paths.py").exists() or (p / "docs" / "data").is_dir():
            return p
    return Path(__file__).resolve().parents[3]


def _plantilla_path() -> Path:
    root = _repo_root()
    candidates = [
        root / "docs" / "ejemplos" / "plantilla_sinca_observado.csv",
        root / "docs" / "roadmap" / "data" / "plantilla_sinca_observado.csv",
        root / "docs" / "data" / "plantilla_sinca_observado.csv",
    ]
    for p in candidates:
        if p.is_file():
            return p
    return candidates[0]


def _sinca_runtime_dir() -> Path:
    root = _repo_root()
    d = root / "backend" / "08_Gestion_Datos" / "datos_runtime" / "sinca"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _slugs_para_faena(faena_id: str) -> list[str]:
    from api_rest.faena_catalogo import get_faena

    f = get_faena(faena_id)
    if not f:
        return []
    fid = f["id"]
    if fid in _FAENA_SLUGS:
        return list(_FAENA_SLUGS[fid])
    # SPATI / genérico: rajo + id
    ancla = None
    for e in f.get("estaciones_area") or []:
        if e.get("rol") == "rajo":
            ancla = e.get("id")
            break
    out = []
    if ancla:
        out.append(str(ancla))
    if fid not in out:
        out.append(fid)
    return out


def _filas_demo_dias(n_dias: int = 7) -> list[dict[str, Any]]:
    """Genera filas diarias recientes (observado) a partir de la plantilla o defaults."""
    base_vals = [
        {"pm25": 12.5, "pm10": 28.0, "so2": 3.1, "no2": 8.2, "o3": 45.0},
        {"pm25": 14.0, "pm10": 32.5, "so2": 2.8, "no2": 9.0, "o3": 42.1},
        {"pm25": 11.2, "pm10": 25.0, "so2": 4.0, "no2": 7.5, "o3": 48.3},
    ]
    plantilla = _plantilla_path()
    if plantilla.is_file():
        with plantilla.open(encoding="utf-8-sig", newline="") as fh:
            rows = list(csv.DictReader(fh))
            if rows:
                base_vals = []
                for r in rows:
                    base_vals.append(
                        {
                            "pm25": float(r.get("pm25") or r.get("pm2_5") or 12),
                            "pm10": float(r.get("pm10") or 25),
                            "so2": float(r.get("so2") or 3),
                            "no2": float(r.get("no2") or 8),
                            "o3": float(r.get("o3") or 40),
                        }
                    )
    hoy = datetime.now(timezone.utc).date()
    out: list[dict[str, Any]] = []
    for i in range(n_dias):
        d = hoy - timedelta(days=n_dias - 1 - i)
        v = base_vals[i % len(base_vals)]
        # ligera variación
        factor = 1.0 + (i % 3) * 0.03
        out.append(
            {
                "fecha": d.isoformat(),
                "pm2_5": round(v["pm25"] * factor, 1),
                "pm10": round(v["pm10"] * factor, 1),
                "sulphur_dioxide": round(v["so2"] * factor, 1),
                "nitrogen_dioxide": round(v["no2"] * factor, 1),
                "ozone": round(v["o3"] * factor, 1),
                "tipo_dato": "observado",
                "fuente": "sinca",
            }
        )
    return out


def _modelo_desde_obs(filas_obs: list[dict[str, Any]], sesgo_pm10: float = 8.0) -> list[dict[str, Any]]:
    """Pares modelo = observado + sesgo (simula CAMS sobreestimado)."""
    out = []
    for f in filas_obs:
        m = dict(f)
        m["fuente"] = "openmeteo_cams"
        m["tipo_dato"] = "modelo"
        if m.get("pm2_5") is not None:
            m["pm2_5"] = round(float(m["pm2_5"]) + sesgo_pm10 * 0.4, 1)
        if m.get("pm10") is not None:
            m["pm10"] = round(float(m["pm10"]) + sesgo_pm10, 1)
        out.append(m)
    return out


def _escribir_csv_runtime(slug: str, filas: list[dict[str, Any]]) -> Path:
    path = _sinca_runtime_dir() / f"{slug}.csv"
    with path.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["fecha", "pm25", "pm10", "so2", "no2", "o3"])
        w.writeheader()
        for f in filas:
            w.writerow(
                {
                    "fecha": f.get("fecha"),
                    "pm25": f.get("pm2_5"),
                    "pm10": f.get("pm10"),
                    "so2": f.get("sulphur_dioxide"),
                    "no2": f.get("nitrogen_dioxide"),
                    "o3": f.get("ozone"),
                }
            )
    return path


def seed_iot_faena(faena_id: str, n: int = 6) -> int:
    """Registra lecturas IoT demo en la estación ancla de la faena."""
    from api_rest import iot_services
    from api_rest.faena_catalogo import get_faena

    f = get_faena(faena_id)
    if not f:
        return 0
    estacion = f.get("estacion_ancla") or f["id"]
    for e in f.get("estaciones_area") or []:
        if e.get("rol") == "rajo":
            estacion = e.get("id") or estacion
            break
    tipos = ("temperatura", "humedad", "viento", "presion")
    n_ok = 0
    for i in range(n):
        iot_services.registrar_lectura(
            {
                "sensor_id": f"demo-{faena_id}-{i}",
                "tipo": tipos[i % len(tipos)],
                "estacion_id": estacion,
                "valor": 10.0 + i * 1.5,
                "fuente": "m7_demo",
            }
        )
        n_ok += 1
    return n_ok


def activar_demo_observado(
    faena_id: str | None = None,
    *,
    dias: int = 7,
) -> dict[str, Any]:
    """Carga observado+modelo demo y IoT. Si faena_id es None, Paipote+Mantos+Escondida."""
    from api_rest.faena_catalogo import get_faena
    from api_rest.integracion import aire_store

    targets = [faena_id] if faena_id else ["paipote", "mantos_blancos", "escondida"]
    detalle: dict[str, Any] = {}
    total_obs = 0
    total_mod = 0
    total_iot = 0

    for fid in targets:
        f = get_faena(fid)
        if not f:
            detalle[str(fid)] = {"error": "faena_no_encontrada"}
            continue
        slugs = _slugs_para_faena(fid)
        filas_obs = _filas_demo_dias(dias)
        filas_mod = _modelo_desde_obs(filas_obs)
        sync_slugs: dict[str, int] = {}
        for slug in slugs:
            _escribir_csv_runtime(slug, filas_obs)
            n_obs = aire_store.guardar_aire(
                slug, filas_obs, fuente="sinca", tipo_dato="observado"
            )
            n_mod = aire_store.guardar_aire(
                slug, filas_mod, fuente="openmeteo_cams", tipo_dato="modelo"
            )
            sync_slugs[slug] = n_obs
            total_obs += n_obs
            total_mod += n_mod
        n_iot = seed_iot_faena(fid)
        total_iot += n_iot
        detalle[f["id"]] = {
            "slugs": sync_slugs,
            "iot": n_iot,
            "csv_dir": str(_sinca_runtime_dir()),
        }

    return {
        "ok": True,
        "fase": "M7",
        "faenas": detalle,
        "total_observado": total_obs,
        "total_modelo": total_mod,
        "total_iot": total_iot,
        "plantilla": str(_plantilla_path()),
        "nota": (
            "Demo escribe aire_registros (sinca/observado + cams/modelo) e IoT. "
            "Validar GET …/modelo-vs-observado (estado ok|parcial)."
        ),
    }


def estado_observado_faena(faena_id: str, *, dias: int = 14) -> dict[str, Any]:
    """Readiness M7: conteos + reporte MVO resumido."""
    from api_rest.faena_catalogo import get_faena
    from api_rest.modelo_vs_observado_service import reporte_modelo_vs_observado

    f = get_faena(faena_id)
    if not f:
        return {"error": "faena_no_encontrada", "faena_id": faena_id}
    mvo = reporte_modelo_vs_observado(f["id"], dias=dias) or {}
    return {
        "faena_id": f["id"],
        "nombre": f.get("nombre"),
        "fase": "M7",
        "estado_mvo": mvo.get("estado"),
        "aire": {
            "n_pares": (mvo.get("aire") or {}).get("n_pares"),
            "n_modelo": (mvo.get("aire") or {}).get("n_modelo"),
            "n_observado": (mvo.get("aire") or {}).get("n_observado"),
            "pm10_sesgo": ((mvo.get("aire") or {}).get("pm10") or {}).get("sesgo_medio"),
            "pm25_sesgo": ((mvo.get("aire") or {}).get("pm25") or {}).get("sesgo_medio"),
        },
        "iot": mvo.get("iot"),
        "documentos": {
            "csv": f"/api/public/operaciones/faena/{f['id']}/informe?formato=csv",
            "pdf": f"/api/public/operaciones/faena/{f['id']}/informe?formato=pdf",
            "mvo_csv": f"/api/public/operaciones/faena/{f['id']}/modelo-vs-observado?formato=csv",
        },
        "listo_produccion": mvo.get("estado") in ("ok", "parcial"),
        "guia": mvo.get("guia"),
    }
