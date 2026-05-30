#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Entrenamiento unificado ~43 modelos METGO (módulo 06).

Genera artefactos compatibles con sklearn 1.4+ y model_manifest.json.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import numpy as np

from api_rest.integracion import meteo_store
from api_rest.integracion.ml_train_catalog import FEATURES_BASE, catalogo_completo

MIN_FILAS_REALES = 30


def _allow_synthetic() -> bool:
    return os.getenv("METGO_ML_ALLOW_SYNTHETIC", "0").lower() in ("1", "true", "yes")


def _repo_root() -> Path:
    for p in Path(__file__).resolve().parents:
        if (p / "metgo_paths.py").exists():
            return p
    raise FileNotFoundError("Raíz METGO no encontrada")


def _setup_openmeteo_imports() -> None:
    """Rutas para datos_reales_openmeteo (módulo 01 + compat)."""
    import sys

    root = _repo_root()
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    import metgo_paths

    metgo_paths.setup_paths("01_meteo", "05_api_rest")
    compat = root / "scripts" / "compat"
    if compat.is_dir() and str(compat) not in sys.path:
        sys.path.insert(0, str(compat))


def _sincronizar_datos_reales(estacion_id: str, dias: int) -> dict[str, Any]:
    """Pobla meteo_store desde CSV 5 años (Quillota) + OpenMeteo reciente."""
    _setup_openmeteo_imports()
    from api_rest.integracion.etl_sync import importar_csv_historico

    detalle: dict[str, Any] = {"csv": importar_csv_historico()}
    try:
        from api_rest.services import historico_meteo

        hist = historico_meteo(estacion_id, dias=min(dias, 92))
        detalle["openmeteo_filas"] = len(hist) if hist else 0
        detalle["openmeteo_ok"] = bool(hist)
    except Exception as exc:
        detalle["openmeteo_error"] = str(exc)
    detalle["store"] = meteo_store.estadisticas_store()
    return detalle


def _etiqueta_origen(meta_sync: dict[str, Any] | None) -> str:
    if not meta_sync:
        return "meteo_sqlite"
    csv_n = int((meta_sync.get("csv") or {}).get("importados") or 0)
    om = int(meta_sync.get("openmeteo_filas") or 0)
    if csv_n and om:
        return "csv_openmeteo"
    if csv_n:
        return "csv_5_anios"
    if om:
        return "openmeteo"
    return "meteo_sqlite"


def _obtener_filas_entrenamiento(
    estacion_id: str,
    dias_datos: int,
) -> tuple[list[dict[str, Any]], str, dict[str, Any] | None]:
    """Datos reales primero; sintético solo con METGO_ML_ALLOW_SYNTHETIC=1."""
    filas = _filas_desde_meteo(estacion_id, dias_datos)
    if len(filas) >= MIN_FILAS_REALES:
        return filas, "meteo_sqlite", None

    sync_meta = _sincronizar_datos_reales(estacion_id, dias_datos)
    filas = _filas_desde_meteo(estacion_id, dias_datos)
    if len(filas) >= MIN_FILAS_REALES:
        return filas, _etiqueta_origen(sync_meta), sync_meta

    if _allow_synthetic():
        n = min(365, max(120, dias_datos))
        return _filas_sinteticas(n), "sintetico", sync_meta

    return [], "sin_datos_reales", sync_meta


def _modelos_root() -> Path:
    for p in Path(__file__).resolve().parents:
        if (p / "metgo_paths.py").exists():
            d = p / "backend" / "06_Modelos_ML_IA" / "modelos"
            d.mkdir(parents=True, exist_ok=True)
            return d
    raise FileNotFoundError("Directorio modelos no encontrado")


def _manifest_path() -> Path:
    return _modelos_root() / "model_manifest.json"


def _filas_desde_meteo(estacion_id: str, dias: int) -> list[dict[str, Any]]:
    filas: list[dict[str, Any]] = []
    for row in meteo_store.leer_registros(estacion_id, dias=dias):
        try:
            fecha = datetime.strptime(str(row["fecha"])[:10], "%Y-%m-%d")
        except ValueError:
            continue
        tmax = float(row.get("temperatura_max") or 20)
        tmin = float(row.get("temperatura_min") or 12)
        hum = float(row.get("humedad") or 60)
        precip = float(row.get("precipitacion") or 0)
        viento = float(row.get("viento") or 5)
        presion = float(row.get("presion") or 1013)
        tprom = (tmax + tmin) / 2.0
        nub = max(0.0, min(100.0, 100 - hum + precip * 5))
        for hora in (0, 3, 6, 9, 12, 15, 18, 21):
            filas.append(
                {
                    "dia_año": fecha.timetuple().tm_yday,
                    "hora": hora,
                    "dia_semana": fecha.weekday(),
                    "mes": fecha.month,
                    "temperatura_max": tmax,
                    "temperatura_min": tmin,
                    "temperatura_promedio": tprom,
                    "temperatura_actual": tprom,
                    "humedad": hum,
                    "humedad_relativa": hum,
                    "precipitacion": precip,
                    "viento_velocidad": viento,
                    "velocidad_viento": viento,
                    "presion": presion,
                    "presion_atmosferica": presion,
                    "nubosidad": nub,
                }
            )
    return filas


def _filas_sinteticas(n_dias: int = 365) -> list[dict[str, Any]]:
    filas: list[dict[str, Any]] = []
    inicio = datetime.now() - timedelta(days=n_dias)
    rng = np.random.default_rng(42)
    for i in range(n_dias):
        fecha = inicio + timedelta(days=i)
        dia = fecha.timetuple().tm_yday
        temp_base = 15 + 10 * np.sin(2 * np.pi * dia / 365)
        for hora in range(0, 24, 3):
            humedad = max(0, min(100, 60 + 15 * np.cos(2 * np.pi * hora / 24) + rng.normal(0, 2)))
            presion = 1013 + 8 * np.sin(2 * np.pi * dia / 365) + rng.normal(0, 1)
            viento = max(0, 5 + rng.normal(0, 1.5))
            tmax = temp_base + 5 * np.sin(2 * np.pi * hora / 24) + rng.normal(0, 0.8)
            tmin = tmax - 8 + rng.normal(0, 0.5)
            precip = float(rng.exponential(1.5)) if rng.random() < 0.12 else 0.0
            tprom = (tmax + tmin) / 2.0
            nub = max(0.0, min(100.0, 100 - humedad + precip * 5))
            filas.append(
                {
                    "dia_año": dia,
                    "hora": hora,
                    "dia_semana": fecha.weekday(),
                    "mes": fecha.month,
                    "temperatura_max": round(tmax, 2),
                    "temperatura_min": round(tmin, 2),
                    "temperatura_promedio": round(tprom, 2),
                    "temperatura_actual": round(tprom, 2),
                    "humedad": round(humedad, 2),
                    "humedad_relativa": round(humedad, 2),
                    "precipitacion": round(precip, 2),
                    "viento_velocidad": round(viento, 2),
                    "velocidad_viento": round(viento, 2),
                    "presion": round(presion, 2),
                    "presion_atmosferica": round(presion, 2),
                    "nubosidad": round(nub, 2),
                }
            )
    return filas


def _instanciar(sklearn_name: str):
    from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor, VotingRegressor
    from sklearn.linear_model import LinearRegression, Ridge

    if sklearn_name == "RandomForestRegressor":
        return RandomForestRegressor(n_estimators=30, max_depth=10, random_state=42)
    if sklearn_name == "GradientBoostingRegressor":
        return GradientBoostingRegressor(n_estimators=30, max_depth=5, random_state=42)
    if sklearn_name == "Ridge":
        return Ridge(alpha=1.0)
    if sklearn_name == "VotingRegressor":
        return VotingRegressor(
            estimators=[
                ("rf", RandomForestRegressor(n_estimators=15, max_depth=8, random_state=42)),
                ("gb", GradientBoostingRegressor(n_estimators=15, max_depth=4, random_state=43)),
            ]
        )
    return LinearRegression()


def _entrenar_uno(
    filas: list[dict[str, Any]],
    spec: dict[str, Any],
    out_dir: Path,
) -> dict[str, Any]:
    import joblib
    from sklearn.metrics import mean_squared_error, r2_score
    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import StandardScaler

    target = spec["target"]
    features = spec["features"]
    xs, ys = [], []
    for row in filas:
        if row.get(target) is None:
            continue
        try:
            xs.append([float(row.get(f, 0)) for f in features])
            ys.append(float(row[target]))
        except (TypeError, ValueError):
            continue
    if len(xs) < 24:
        return {"error": "datos insuficientes", "archivo": spec["archivo"]}

    X = np.array(xs)
    y = np.array(ys)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    scaler = None
    if spec.get("scaler"):
        scaler = StandardScaler()
        X_train = scaler.fit_transform(X_train)
        X_test = scaler.transform(X_test)

    modelo = _instanciar(spec["sklearn"])
    modelo.fit(X_train, y_train)
    pred = modelo.predict(X_test)
    mse = float(mean_squared_error(y_test, pred))
    r2 = float(r2_score(y_test, pred))

    pkg_dir = out_dir / spec["paquete"]
    pkg_dir.mkdir(parents=True, exist_ok=True)
    model_path = pkg_dir / spec["archivo"]
    joblib.dump(modelo, model_path)

    scaler_name = None
    if scaler is not None:
        scaler_name = f"{model_path.stem}_scaler.joblib"
        joblib.dump(scaler, pkg_dir / scaler_name)

    return {
        "paquete": spec["paquete"],
        "archivo": spec["archivo"],
        "variable": spec["variable"],
        "target": target,
        "features": features,
        "sklearn": spec["sklearn"],
        "scaler": scaler_name,
        "modo": spec.get("modo", "manifest"),
        "modelo_path": f"{spec['paquete']}/{spec['archivo']}",
        "mse": mse,
        "r2": r2,
        "servible": True,
    }


def entrenar_todos(
    estacion_id: str = "quillota",
    dias_datos: int = 365,
) -> dict[str, Any]:
    """Entrena el catálogo completo y escribe model_manifest.json."""
    filas, origen, sync_meta = _obtener_filas_entrenamiento(estacion_id, dias_datos)
    if not filas:
        return {
            "ok": False,
            "origen_datos": origen,
            "filas": 0,
            "entrenados": 0,
            "errores": 1,
            "detalle_errores": [
                {
                    "error": (
                        "Sin datos reales suficientes para entrenar. "
                        "Verifique CSV 5 años, OpenMeteo y meteo_historico.db."
                    )
                }
            ],
            "sync_datos": sync_meta,
        }

    root = _modelos_root()
    catalog = catalogo_completo()
    entrenados: list[dict[str, Any]] = []
    errores: list[dict[str, Any]] = []

    for spec in catalog:
        try:
            meta = _entrenar_uno(filas, spec, root)
            if "error" in meta:
                errores.append(meta)
            else:
                entrenados.append(meta)
        except Exception as exc:
            errores.append({"archivo": spec["archivo"], "error": str(exc)})

    manifest = {
        "actualizado": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "origen_datos": origen,
        "filas": len(filas),
        "estacion_id": estacion_id,
        "sklearn_version": _sklearn_version(),
        "total": len(catalog),
        "entrenados": len(entrenados),
        "modelos": entrenados,
    }
    _manifest_path().write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    quillota_cfg = {
        m["variable"]: {
            "variable": m["variable"],
            "mse": m["mse"],
            "r2": m["r2"],
            "modelo_path": m["modelo_path"],
            "features": m["features"],
        }
        for m in entrenados
        if m["paquete"] == "modelos_ml_quillota" and m["archivo"].endswith(".joblib")
    }
    if quillota_cfg:
        cfg_path = root / "modelos_ml_quillota" / "configuracion_modelos.json"
        cfg_path.write_text(json.dumps(quillota_cfg, ensure_ascii=False, indent=2), encoding="utf-8")

    from api_rest.integracion import ml_registry

    reg = ml_registry.sincronizar_registro()
    out = {
        "ok": len(errores) == 0,
        "origen_datos": origen,
        "filas": len(filas),
        "entrenados": len(entrenados),
        "errores": len(errores),
        "detalle_errores": errores[:10],
        "registry_servibles": reg.get("servibles"),
        "registry_total": reg.get("total"),
        "finalizado": manifest["actualizado"],
    }
    if sync_meta:
        out["sync_datos"] = sync_meta
    return out


def _sklearn_version() -> str:
    try:
        import sklearn

        return sklearn.__version__
    except ImportError:
        return "unknown"


def leer_manifest() -> dict[str, Any]:
    path = _manifest_path()
    if not path.is_file():
        return {"modelos": []}
    return json.loads(path.read_text(encoding="utf-8"))


def ensure_modelos_servibles(min_servibles: int | None = None) -> dict[str, Any] | None:
    """Entrena el catálogo completo si faltan modelos servibles."""
    if os.getenv("METGO_ML_AUTO_TRAIN", "1").lower() in ("0", "false", "no"):
        return None
    try:
        import joblib  # noqa: F401
        from sklearn.ensemble import RandomForestRegressor  # noqa: F401
    except ImportError:
        return {"ok": False, "error": "scikit-learn/joblib no instalados"}

    objetivo = min_servibles if min_servibles is not None else len(catalogo_completo())

    try:
        from api_rest.integracion import ml_registry

        reg = ml_registry.sincronizar_registro()
        if reg.get("servibles", 0) >= objetivo:
            return None
    except Exception:
        pass

    try:
        return entrenar_todos()
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


# Compatibilidad API / tests previos
MODELS_CONFIG = {
    "temperatura_max": {"features": ["dia_año", "hora", "humedad", "presion", "viento_velocidad"], "sklearn": "RandomForestRegressor"},
    "temperatura_min": {"features": ["dia_año", "hora", "humedad", "presion", "viento_velocidad"], "sklearn": "RandomForestRegressor"},
    "precipitacion": {"features": ["dia_año", "hora", "humedad", "presion", "temperatura_max"], "sklearn": "RandomForestRegressor"},
    "humedad": {"features": ["dia_año", "hora", "temperatura_max", "temperatura_min", "presion"], "sklearn": "LinearRegression"},
    "presion": {"features": ["dia_año", "hora", "temperatura_max", "temperatura_min", "humedad"], "sklearn": "LinearRegression"},
}


def entrenar_quillota(estacion_id: str = "quillota", variables: list[str] | None = None, dias_datos: int = 365) -> dict[str, Any]:
    return entrenar_todos(estacion_id=estacion_id, dias_datos=dias_datos)
