#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ETL módulo 08 → store SQLite (OpenMeteo + CSV histórico 5 años)."""

from __future__ import annotations

import csv
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from api_rest.integracion import meteo_store
from api_rest.services import (
    SLUG_A_NOMBRE,
    ESTACIONES_PRINCIPALES,
    historico_meteo,
    pronostico_meteo,
)


def _runtime_dir() -> Path:
    """Mismo criterio que meteo_store (_db_path padre)."""
    for p in Path(__file__).resolve().parents:
        if (p / "metgo_paths.py").exists():
            d = p / "backend" / "08_Gestion_Datos" / "datos_runtime"
            d.mkdir(parents=True, exist_ok=True)
            return d
    return Path(".")


def _etl_metrics_path() -> Path:
    return _runtime_dir() / "etl_meteo_metrics.json"


def leer_etl_metrics() -> dict[str, Any]:
    path = _etl_metrics_path()
    if not path.is_file():
        return {
            "historial": [],
            "ultimo": None,
            "ruta": str(path),
        }
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            return data
    except (json.JSONDecodeError, OSError):
        pass
    return {"historial": [], "ultimo": None, "ruta": str(path)}


def _persistir_metrics(resultado: dict[str, Any], origen: str) -> None:
    path = _etl_metrics_path()
    prev = leer_etl_metrics()
    hist = prev.get("historial") if isinstance(prev.get("historial"), list) else []
    entry = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "origen": origen,
        "dias": resultado.get("param_dias"),
        "incluir_csv": resultado.get("param_incluir_csv"),
        "store": resultado.get("store"),
        "errores_count": len(resultado.get("errores") or []),
        "csv_importados": (resultado.get("csv") or {}).get("importados"),
    }
    hist = hist[-19:] + [entry]
    blob = {
        "ultimo": entry,
        "historial": hist,
        "ruta": str(path),
        "store_path": str((resultado.get("store") or {}).get("db", "")),
    }
    path.write_text(json.dumps(blob, ensure_ascii=False, indent=2), encoding="utf-8")


def etl_parametros_defaults() -> tuple[int, bool]:
    dias = int(os.environ.get("METGO_ETL_DIAS_SYNC", "30"))
    incluir = os.environ.get("METGO_ETL_SKIP_CSV", "").lower() not in ("1", "true", "yes")
    return dias, incluir


def _csv_5_anios() -> Path | None:
    for p in Path(__file__).resolve().parents:
        cand = (
            p
            / "backend"
            / "08_Gestion_Datos"
            / "datos"
            / "exportaciones"
            / "datos_historicos_5_anios_quillota_centro_20251007_230406.csv"
        )
        if cand.is_file():
            return cand
    return None


def _slug_desde_estacion_csv(nombre: str) -> str:
    n = (nombre or "").lower().replace(" ", "_").replace("-", "_")
    if "quillota" in n:
        return "quillota"
    if n in SLUG_A_NOMBRE:
        return n
    return "quillota"


def importar_csv_historico() -> dict[str, Any]:
    path = _csv_5_anios()
    if not path:
        return {"importados": 0, "fuente": None, "error": "CSV 5 años no encontrado"}
    filas: list[dict[str, Any]] = []
    with path.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            fecha = str(row.get("fecha") or "")[:10]
            if not fecha:
                continue
            slug = _slug_desde_estacion_csv(row.get("estacion", "quillota"))
            filas.append(
                {
                    "estacion_id": slug,
                    "fecha": fecha,
                    "temperatura_max": _float(row.get("temperatura_max")),
                    "temperatura_min": _float(row.get("temperatura_min")),
                    "humedad": _float(row.get("humedad_relativa")),
                    "precipitacion": _float(row.get("precipitacion")),
                    "viento": _float(row.get("velocidad_viento")),
                    "presion": _float(row.get("presion_atmosferica")),
                    "helada": (
                        _float(row.get("temperatura_min")) is not None
                        and _float(row.get("temperatura_min")) <= 0.0
                    ),
                }
            )
    by_station: dict[str, list[dict[str, Any]]] = {}
    for r in filas:
        by_station.setdefault(r["estacion_id"], []).append(r)
    total = 0
    for slug, rows in by_station.items():
        payload = [
            {
                "fecha": x["fecha"],
                "temperatura_max": x["temperatura_max"],
                "temperatura_min": x["temperatura_min"],
                "humedad": x["humedad"],
                "precipitacion": x["precipitacion"],
                "viento": x["viento"],
                "presion": x["presion"],
                "helada": x.get("helada"),
            }
            for x in rows
        ]
        total += meteo_store.guardar_registros(slug, payload, fuente="csv_5_anios")
    return {"importados": total, "fuente": str(path), "estaciones": list(by_station.keys())}


def _float(v: Any) -> float | None:
    try:
        return float(v) if v not in (None, "") else None
    except (TypeError, ValueError):
        return None


def _archive_etl_module():
    """Carga el script ETL archive (módulo 08) bajo el mismo layout que el CLI."""
    import sys

    for p in Path(__file__).resolve().parents:
        if (p / "metgo_paths.py").exists():
            root = p
            break
    else:
        return None
    script_dir = root / "backend" / "08_Gestion_Datos" / "scripts"
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    try:
        import metgo_paths

        metgo_paths.setup_paths("01_meteo", "05_api_rest")
        apis_root = metgo_paths.MODULE_PATHS.get("05_api_rest")
        if apis_root:
            ap = str(apis_root)
            if ap not in sys.path:
                sys.path.insert(0, ap)
        if str(script_dir) not in sys.path:
            sys.path.insert(0, str(script_dir))
        import etl_archive_openmeteo

        return etl_archive_openmeteo
    except ImportError:
        return None


def sincronizar_archive(anios: int = 5) -> dict[str, Any]:
    mod = _archive_etl_module()
    if mod is None:
        return {
            "archive_sync": {},
            "error": "No se pudo cargar etl_archive_openmeteo",
            "param_anios": anios,
        }
    return mod.sincronizar_archive_openmeteo(anios=anios)


def sincronizar_estaciones(
    dias: int = 30,
    incluir_csv: bool = True,
    incluir_archive: bool = False,
    anios_archive: int = 5,
    origen: str = "api",
) -> dict[str, Any]:
    """Pobla el store desde OpenMeteo (histórico + pronóstico + heladas) para todas las estaciones."""
    detalle: dict[str, int] = {}
    detalle_pronostico: dict[str, int] = {}
    detalle_helada: dict[str, int] = {}
    detalle_serie_helada: dict[str, bool] = {}
    errores: list[str] = []
    for slug in ESTACIONES_PRINCIPALES:
        try:
            hist = historico_meteo(slug, dias=dias)
            detalle[slug] = len(hist) if hist else 0
        except Exception as e:
            errores.append(f"{slug}: {e}")
            detalle[slug] = 0
        try:
            # pronostico_meteo persiste en Supabase (meteo_pronostico) al obtener datos frescos
            pron = pronostico_meteo(slug, dias=7)
            detalle_pronostico[slug] = len(pron) if pron else 0
        except Exception as e:
            errores.append(f"{slug} (pronostico): {e}")
            detalle_pronostico[slug] = 0
        try:
            from api_rest.meteo_avanzado_core import sincronizar_helada_store

            detalle_helada[slug] = sincronizar_helada_store(slug, dias=7, cultivo="palto")
        except Exception as e:
            errores.append(f"{slug} (helada): {e}")
            detalle_helada[slug] = 0
        try:
            from api_rest.services import serie_helada_madrugada_meteo

            serie = serie_helada_madrugada_meteo(slug, dias=7)
            detalle_serie_helada[slug] = bool(serie and (serie.get("horas") or serie.get("puntos")))
        except Exception as e:
            errores.append(f"{slug} (serie_helada): {e}")
            detalle_serie_helada[slug] = False
    csv_res = importar_csv_historico() if incluir_csv else {"importados": 0, "omitido": True}
    archive_res: dict[str, Any] = {"omitido": True}
    if incluir_archive:
        archive_res = sincronizar_archive(anios=int(anios_archive))
        if archive_res.get("errores"):
            errores.extend(archive_res["errores"])
    stats = meteo_store.estadisticas_store()
    out = {
        "estaciones_sync": detalle,
        "pronostico_sync": detalle_pronostico,
        "helada_sync": detalle_helada,
        "serie_helada_sync": detalle_serie_helada,
        "csv": csv_res,
        "archive_sync": archive_res,
        "store": stats,
        "errores": errores,
        "param_dias": dias,
        "param_incluir_csv": incluir_csv,
        "param_incluir_archive": incluir_archive,
        "param_anios_archive": int(anios_archive) if incluir_archive else None,
    }
    try:
        _persistir_metrics(out, origen)
    except OSError:
        pass
    return out


def fuentes_datos() -> dict[str, Any]:
    csv_path = _csv_5_anios()
    out: dict[str, Any] = {
        "openmeteo": True,
        "openmeteo_archive": True,
        "cache_modulo_08": True,
        "sqlite_meteo": str(meteo_store._db_path()),
        "csv_5_anios": str(csv_path) if csv_path else None,
        "csv_disponible": bool(csv_path),
        "supabase": meteo_store.estadisticas_store(),
        "e7_e8": _conteos_e7_e8(),
    }
    try:
        from api_rest.integracion import fuentes_store

        out["gobernanza"] = fuentes_store.resumen_gobernanza()
    except Exception as exc:
        out["gobernanza"] = {"error": str(exc)}
    try:
        from api_rest import oficiales_service

        out["oficiales_chile"] = oficiales_service.estado_fuentes()
    except Exception as exc:
        out["oficiales_chile"] = {"error": str(exc)}
    return out


def _conteos_e7_e8() -> dict[str, Any]:
    """Conteos de tablas aire/operaciones (monitoreo post-migración)."""
    try:
        from api_rest.integracion.supabase_store import get_supabase_client

        client = get_supabase_client()
        if not client:
            return {"activo": False}
        out: dict[str, Any] = {"activo": True}
        for tabla in (
            "aire_registros",
            "aire_dispersion",
            "operaciones_ventanas",
            "faena_estaciones_area",
        ):
            try:
                res = client.table(tabla).select("*", count="exact").limit(1).execute()
                out[tabla] = res.count
            except Exception as exc:
                out[tabla] = {"error": str(exc)[:80]}
        return out
    except Exception as exc:
        return {"activo": False, "error": str(exc)[:120]}
