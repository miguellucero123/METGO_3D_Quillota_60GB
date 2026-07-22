#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ETL OpenMeteo Archive → Supabase `meteo_registros` (fuente openmeteo_archive).

Uso:
    python backend/08_Gestion_Datos/scripts/etl_archive_openmeteo.py
    python backend/08_Gestion_Datos/scripts/etl_archive_openmeteo.py --anios 3
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

import pandas as pd


def _repo_root() -> Path:
    for p in Path(__file__).resolve().parents:
        if (p / "metgo_paths.py").exists():
            return p
    raise SystemExit("No se encontró metgo_paths.py (ejecutar desde repo METGO)")


def _setup_import_paths() -> None:
    root = _repo_root()
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    import metgo_paths

    metgo_paths.setup_paths("01_meteo", "05_api_rest")
    apis_root = metgo_paths.MODULE_PATHS.get("05_api_rest")
    if apis_root and Path(apis_root).is_dir():
        ap = str(apis_root)
        if ap not in sys.path:
            sys.path.insert(0, ap)


def _fecha_iso(val: Any) -> str:
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return ""
    if hasattr(val, "strftime"):
        return val.strftime("%Y-%m-%d")
    return str(val)[:10]


def dataframe_a_filas_store(df: pd.DataFrame) -> list[dict[str, Any]]:
    filas: list[dict[str, Any]] = []
    for _, row in df.iterrows():
        fecha = _fecha_iso(row.get("fecha"))
        if not fecha:
            continue
        filas.append(
            {
                "fecha": fecha,
                "temperatura_max": row.get("temperatura_max"),
                "temperatura_min": row.get("temperatura_min"),
                "temperatura_promedio": row.get("temperatura_promedio"),
                "humedad": row.get("humedad_relativa"),
                "precipitacion": row.get("precipitacion"),
                "viento": row.get("velocidad_viento"),
                "presion": row.get("presion_atmosferica"),
                "cobertura_nubosa": row.get("cobertura_nubosa"),
                "radiacion_solar_sum": row.get("radiacion_solar_sum"),
                "evapotranspiracion": row.get("evapotranspiracion"),
                "helada": row.get("helada"),
                "niebla": row.get("niebla"),
                "visibilidad": row.get("visibilidad"),
            }
        )
    return filas


def sincronizar_archive_openmeteo(anios: int = 5) -> dict[str, Any]:
    """Descarga archive por estación principal y persiste en meteo_store."""
    _setup_import_paths()

    from api_rest.integracion import meteo_store
    from api_rest.services import ESTACIONES_PRINCIPALES, SLUG_A_NOMBRE
    from datos_reales_openmeteo import obtener_datos_archive_openmeteo

    detalle: dict[str, int] = {}
    errores: list[str] = []
    anios = max(1, int(anios))

    for slug in ESTACIONES_PRINCIPALES:
        nombre = SLUG_A_NOMBRE.get(slug, slug.replace("_", " ").title())
        try:
            df = obtener_datos_archive_openmeteo(nombre, anios=anios)
            if df is None or df.empty:
                detalle[slug] = 0
                errores.append(f"{slug}: sin datos archive")
                continue
            filas = dataframe_a_filas_store(df)
            n = meteo_store.guardar_registros(
                slug, filas, fuente="openmeteo_archive"
            )
            detalle[slug] = n
            print(f"  {slug} ({nombre}): {n} registros persistidos")
        except Exception as e:
            errores.append(f"{slug}: {e}")
            detalle[slug] = 0
            print(f"  {slug}: ERROR {e}")

    return {
        "archive_sync": detalle,
        "param_anios": anios,
        "errores": errores,
        "total_registros": sum(detalle.values()),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="ETL OpenMeteo Archive → meteo_registros")
    parser.add_argument("--anios", type=int, default=5, help="Años hacia atrás (default 5)")
    args = parser.parse_args()

    print(f"ETL OpenMeteo Archive ({args.anios} años) — estaciones principales")
    res = sincronizar_archive_openmeteo(anios=args.anios)
    print("Resumen:", res.get("archive_sync"))
    if res.get("errores"):
        print("Errores:", res["errores"])
    return 0 if res.get("total_registros", 0) > 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
