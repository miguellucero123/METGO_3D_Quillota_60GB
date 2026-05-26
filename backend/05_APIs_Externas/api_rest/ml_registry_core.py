#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Registro MLOps módulo 06: escaneo, sanity-check y predicción segura.

Genera/lee ml_registry.json en datos_runtime.
"""

from __future__ import annotations

import json
import warnings
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from api_rest import services

# Paquetes bajo backend/06_Modelos_ML_IA/modelos/
PAQUETES_ML = (
    "modelos_ml_quillota",
    "modelos_ml",
    "modelos_ml_avanzados",
    "modelos_dinamicos",
    "modelos_ultra_optimizados",
    "modelos_hibridos_rapidos",
)

ALGO_PREFIXES = (
    "GradientBoosting_",
    "LinearRegression_",
    "RandomForest_",
    "Ridge_",
    "Ensemble_",
    "Voting_",
    "Ultra_",
    "GB_",
    "RF_",
)

FEATURES_GENERICAS = [
    "dia_año",
    "hora",
    "temperatura_max",
    "temperatura_min",
    "humedad",
    "presion",
    "viento_velocidad",
    "precipitacion",
]

_CACHE: dict[str, Any] | None = None
_CACHE_MTIME: float | None = None


def _repo_root() -> Path | None:
    for p in Path(__file__).resolve().parents:
        if (p / "metgo_paths.py").exists():
            return p
    return None


def _modelos_root() -> Path | None:
    root = _repo_root()
    if not root:
        return None
    d = root / "backend" / "06_Modelos_ML_IA" / "modelos"
    return d if d.is_dir() else None


def _registry_path() -> Path:
    root = _repo_root()
    if root:
        d = root / "backend" / "08_Gestion_Datos" / "datos_runtime"
        d.mkdir(parents=True, exist_ok=True)
        return d / "ml_registry.json"
    return Path("ml_registry.json")


def _norm(s: str) -> str:
    return (s or "").strip().lower().replace("-", "_").replace(" ", "_")


def _variable_desde_archivo(stem: str) -> str:
    s = stem
    for pref in ALGO_PREFIXES:
        if s.startswith(pref):
            s = s[len(pref) :]
            break
    if s.endswith("_scaler"):
        s = s[: -len("_scaler")]
    return s.replace("_", " ")


def _vector_generico(resumen: dict[str, Any]) -> list[float]:
    now = datetime.now()
    return [
        float(now.timetuple().tm_yday),
        float(now.hour),
        float(resumen.get("temperatura_max", 20)),
        float(resumen.get("temperatura_min", 10)),
        float(resumen.get("humedad", 0)),
        float(resumen.get("presion", 1013)),
        float(resumen.get("viento", 0)),
        float(resumen.get("precipitacion", 0)),
    ]


def _vector_config(resumen: dict[str, Any], features: list[str]) -> list[float]:
    now = datetime.now()
    mapping = {
        "dia_año": float(now.timetuple().tm_yday),
        "hora": float(now.hour),
        "humedad": float(resumen.get("humedad", 0)),
        "presion": float(resumen.get("presion", 1013)),
        "viento_velocidad": float(resumen.get("viento", 0)),
        "temperatura_max": float(resumen.get("temperatura_max", 20)),
        "temperatura_min": float(resumen.get("temperatura_min", 10)),
        "precipitacion": float(resumen.get("precipitacion", 0)),
    }
    return [mapping.get(f, 0.0) for f in features]


def _ajustar_dims(X: list[float], n: int | None) -> list[float]:
    if not isinstance(n, int) or n <= 0:
        return X
    if len(X) == n:
        return X
    if len(X) > n:
        return X[:n]
    return X + [0.0] * (n - len(X))


def _n_features(modelo: Any) -> int | None:
    n = getattr(modelo, "n_features_in_", None)
    if isinstance(n, int) and n > 0:
        return n
    if hasattr(modelo, "steps"):
        try:
            last = modelo.steps[-1][1]
            return getattr(last, "n_features_in_", None)
        except (IndexError, AttributeError):
            pass
    return None


def _cargar_artefacto(path: Path) -> tuple[Any | None, str | None]:
    try:
        import joblib
    except ImportError:
        return None, "joblib no instalado"
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=UserWarning)
            return joblib.load(path), None
    except Exception as e:
        return None, str(e)


def sanity_check(
    model_path: Path,
    scaler_path: Path | None = None,
    features: list[str] | None = None,
) -> dict[str, Any]:
    """Carga + dims + predict de prueba."""
    resumen_demo = {
        "temperatura_max": 22.0,
        "temperatura_min": 12.0,
        "humedad": 55.0,
        "presion": 1015.0,
        "viento": 8.0,
        "precipitacion": 0.0,
    }
    if features:
        X = _vector_config(resumen_demo, features)
    else:
        X = _vector_generico(resumen_demo)

    modelo, err = _cargar_artefacto(model_path)
    if err:
        return {"ok": False, "motivo": f"load: {err}"}

    scaler = None
    if scaler_path and scaler_path.is_file():
        scaler, err_s = _cargar_artefacto(scaler_path)
        if err_s:
            return {"ok": False, "motivo": f"scaler_load: {err_s}"}

    n = _n_features(modelo)
    X = _ajustar_dims(X, n)

    try:
        if scaler is not None:
            X_in = scaler.transform([X])
        else:
            X_in = [X]
        pred = modelo.predict(X_in)
        val = float(pred[0]) if hasattr(pred, "__getitem__") else float(pred)
        if val != val:  # NaN
            return {"ok": False, "motivo": "prediccion NaN"}
        return {
            "ok": True,
            "n_features": n or len(X),
            "usa_scaler": scaler is not None,
            "prediccion_prueba": round(val, 4),
        }
    except Exception as e:
        return {"ok": False, "motivo": f"predict: {e}"}


def _leer_config_quillota() -> dict[str, Any]:
    root = _modelos_root()
    if not root:
        return {}
    cfg_path = root / "modelos_ml_quillota" / "configuracion_modelos.json"
    if not cfg_path.is_file():
        return {}
    return json.loads(cfg_path.read_text(encoding="utf-8"))


def _escanear_paquete(paquete: str, root: Path) -> list[dict[str, Any]]:
    pkg_dir = root / paquete
    if not pkg_dir.is_dir():
        return []
    entradas: list[dict[str, Any]] = []
    for f in sorted(pkg_dir.glob("*.joblib")):
        if f.name.endswith("_scaler.joblib"):
            continue
        scaler_path = pkg_dir / f"{f.stem}_scaler.joblib"
        if not scaler_path.is_file():
            scaler_path = None
        variable = _variable_desde_archivo(f.stem)
        entradas.append(
            {
                "paquete": paquete,
                "archivo": f.name,
                "ruta_relativa": f"{paquete}/{f.name}",
                "variable": variable,
                "variable_key": _norm(variable),
                "scaler": scaler_path.name if scaler_path else None,
                "path": str(f),
                "features": [],
                "modo": "generico",
            }
        )
    for f in sorted(pkg_dir.glob("*.pkl")):
        variable = _variable_desde_archivo(f.stem.replace("modelo_", ""))
        entradas.append(
            {
                "paquete": paquete,
                "archivo": f.name,
                "ruta_relativa": f"{paquete}/{f.name}",
                "variable": variable,
                "variable_key": _norm(variable),
                "scaler": None,
                "path": str(f),
                "features": [],
                "modo": "pkl",
            }
        )
    return entradas


def sincronizar_registro(forzar: bool = False) -> dict[str, Any]:
    """Escanea todos los paquetes y ejecuta sanity-check."""
    global _CACHE, _CACHE_MTIME
    root = _modelos_root()
    if not root:
        return {"error": "Directorio modelos no encontrado", "modelos": []}

    entradas: list[dict[str, Any]] = []
    cfg = _leer_config_quillota()
    quillota_dir = root / "modelos_ml_quillota"

    for var, meta in cfg.items():
        fname = Path(meta.get("modelo_path", "")).name
        model_path = quillota_dir / fname
        if not model_path.is_file():
            continue
        features = meta.get("features", [])
        sanity = sanity_check(model_path, features=features)
        entradas.append(
            {
                "id": f"config:{var}",
                "paquete": "modelos_ml_quillota",
                "archivo": fname,
                "ruta_relativa": f"modelos_ml_quillota/{fname}",
                "variable": var,
                "variable_key": _norm(var),
                "servible": sanity.get("ok", False),
                "sanity": sanity,
                "motivo_no_servible": None if sanity.get("ok") else sanity.get("motivo"),
                "features": features,
                "modo": "configuracion_modelos",
                "r2": meta.get("r2"),
                "mse": meta.get("mse"),
                "scaler": None,
            }
        )

    archivos_config = {Path(m.get("modelo_path", "")).name for m in cfg.values()}
    for paquete in PAQUETES_ML:
        for raw in _escanear_paquete(paquete, root):
            if paquete == "modelos_ml_quillota" and raw["archivo"] in archivos_config:
                continue
            model_path = Path(raw["path"])
            scaler_path = (
                model_path.parent / raw["scaler"] if raw.get("scaler") else None
            )
            sanity = sanity_check(model_path, scaler_path)
            raw["id"] = f"{paquete}/{raw['archivo']}"
            raw["servible"] = sanity.get("ok", False)
            raw["sanity"] = sanity
            raw["motivo_no_servible"] = None if sanity.get("ok") else sanity.get("motivo")
            entradas.append(raw)

    servibles = sum(1 for e in entradas if e.get("servible"))
    reg = {
        "actualizado": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "total": len(entradas),
        "servibles": servibles,
        "no_servibles": len(entradas) - servibles,
        "paquetes": list(PAQUETES_ML),
        "modelos": entradas,
    }
    path = _registry_path()
    path.write_text(json.dumps(reg, ensure_ascii=False, indent=2), encoding="utf-8")
    _CACHE = reg
    _CACHE_MTIME = path.stat().st_mtime
    return reg


def leer_registro(recargar: bool = False) -> dict[str, Any]:
    global _CACHE, _CACHE_MTIME
    path = _registry_path()
    if not path.is_file() or recargar:
        return sincronizar_registro()
    mtime = path.stat().st_mtime
    if _CACHE is not None and _CACHE_MTIME == mtime and not recargar:
        return _CACHE
    _CACHE = json.loads(path.read_text(encoding="utf-8"))
    _CACHE_MTIME = mtime
    return _CACHE


def listar_desde_registro() -> list[dict[str, Any]]:
    reg = leer_registro()
    out = []
    for m in reg.get("modelos", []):
        sanity = m.get("sanity") or {}
        out.append(
            {
                "id": m.get("id"),
                "variable": m.get("variable"),
                "archivo": m.get("archivo"),
                "paquete": m.get("paquete"),
                "disponible": m.get("servible", False),
                "servible": m.get("servible", False),
                "features": m.get("features", []),
                "r2": m.get("r2"),
                "mse": m.get("mse"),
                "modo_prediccion": m.get("modo"),
                "motivo_no_servible": m.get("motivo_no_servible"),
                "n_features": sanity.get("n_features"),
                "usa_scaler": sanity.get("usa_scaler"),
            }
        )
    return out


def _buscar_entrada(variable: str, solo_servible: bool = True) -> dict[str, Any] | None:
    key = _norm(variable)
    reg = leer_registro()
    candidatos = [m for m in reg.get("modelos", []) if _norm(m.get("variable", "")) == key]
    if not candidatos:
        candidatos = [
            m
            for m in reg.get("modelos", [])
            if key in _norm(m.get("variable", "")) or key in _norm(m.get("archivo", ""))
        ]
    if solo_servible:
        candidatos = [m for m in candidatos if m.get("servible")]
    if not candidatos:
        return None
    # Prioridad: config > quillota > avanzados > ml > resto
    orden = {
        "configuracion_modelos": 0,
        "modelos_ml_quillota": 1,
        "modelos_ml_avanzados": 2,
        "modelos_ml": 3,
        "modelos_ultra_optimizados": 4,
        "modelos_dinamicos": 5,
        "modelos_hibridos_rapidos": 6,
    }
    candidatos.sort(key=lambda m: (orden.get(m.get("modo") if m.get("modo") == "configuracion_modelos" else m.get("paquete"), 9)))
    return candidatos[0]


def predecir_registrado(variable: str, estacion_id: str = "quillota") -> dict[str, Any]:
    entrada = _buscar_entrada(variable, solo_servible=True)
    if not entrada:
        reg = leer_registro()
        no_srv = [
            m
            for m in reg.get("modelos", [])
            if _norm(m.get("variable", "")) == _norm(variable) and not m.get("servible")
        ]
        if no_srv:
            return {
                "error": "Modelo encontrado pero no servible (sanity-check falló)",
                "variable": variable,
                "motivo": no_srv[0].get("motivo_no_servible"),
                "archivo": no_srv[0].get("archivo"),
                "paquete": no_srv[0].get("paquete"),
            }
        return {"error": f"Variable no modelada o sin modelo servible: {variable}"}

    resumen = services.resumen_meteo(estacion_id)
    if not resumen:
        return {"error": "Sin datos meteo para construir features"}

    model_path = Path(entrada.get("path") or "")
    if not model_path.is_file():
        root = _modelos_root()
        model_path = (root / entrada["ruta_relativa"]) if root else model_path

    scaler_path = None
    if entrada.get("scaler") and model_path.parent:
        scaler_path = model_path.parent / entrada["scaler"]

    features = entrada.get("features") or []
    if features:
        X = _vector_config(resumen, features)
    else:
        X = _vector_generico(resumen)

    modelo, err = _cargar_artefacto(model_path)
    if err:
        return {"error": err}

    scaler = None
    if scaler_path and scaler_path.is_file():
        scaler, err_s = _cargar_artefacto(scaler_path)
        if err_s:
            return {"error": err_s}

    n = _n_features(modelo)
    X = _ajustar_dims(X, n)
    try:
        if scaler is not None:
            X_in = scaler.transform([X])
        else:
            X_in = [X]
        pred = float(modelo.predict(X_in)[0])
    except Exception as e:
        return {"error": f"Error en prediccion: {e}"}

    return {
        "variable": variable,
        "estacion_id": estacion_id,
        "prediccion": round(pred, 2),
        "modelo": entrada.get("archivo"),
        "paquete": entrada.get("paquete"),
        "registry_id": entrada.get("id"),
        "servible": True,
        "features_usadas": features or FEATURES_GENERICAS[: len(X)],
        "modo_prediccion": entrada.get("modo"),
        "usa_scaler": bool(scaler),
        "n_features": n,
        "actualizado": datetime.now().isoformat(),
    }


def resumen_registro() -> dict[str, Any]:
    reg = leer_registro()
    return {
        "total_modelos": reg.get("total", 0),
        "servibles": reg.get("servibles", 0),
        "no_servibles": reg.get("no_servibles", 0),
        "actualizado": reg.get("actualizado"),
        "registry_path": str(_registry_path()),
        "paquetes": reg.get("paquetes", []),
    }
