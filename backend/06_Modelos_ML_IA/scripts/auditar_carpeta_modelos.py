#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Auditoría de backend/06_Modelos_ML_IA/modelos y scripts de entrenamiento.

Detecta artefactos corruptos, huérfanos y scripts legacy peligrosos.
"""

from __future__ import annotations

import json
import sys
import warnings
from pathlib import Path
from typing import Any

import joblib
import numpy as np

SCRIPT_DIR = Path(__file__).resolve().parent
MODELOS_ROOT = SCRIPT_DIR.parent / "modelos"
MANIFEST_PATH = MODELOS_ROOT / "model_manifest.json"

DEMO = {
    "dia_año": 180,
    "hora": 12,
    "dia_semana": 2,
    "mes": 6,
    "temperatura_max": 22.0,
    "temperatura_min": 12.0,
    "temperatura_promedio": 17.0,
    "temperatura_actual": 17.0,
    "humedad": 55.0,
    "humedad_relativa": 55.0,
    "precipitacion": 0.0,
    "viento_velocidad": 8.0,
    "velocidad_viento": 8.0,
    "presion": 1015.0,
    "presion_atmosferica": 1015.0,
    "nubosidad": 40.0,
}

SCRIPTS_PELIGROSOS = [
    "sistema_predicciones_ml_avanzado.py",
    "sistema_modelos_dinamicos.py",
    "sistema_modelos_ultra_optimizado.py",
    "sistema_modelos_hibridos_innovadores.py",
    "pipeline_ml_optimizado.py",
    "fix_ml_models.py",
    "ejecutar_ml_avanzado.py",
    "ia_avanzada_metgo.py",
    "deep_learning_avanzado_metgo.py",
]


def _vector(features: list[str]) -> list[float]:
    return [float(DEMO.get(f, 0.0)) for f in features]


def _n_features(modelo: Any) -> int | None:
    if hasattr(modelo, "n_features_in_"):
        return int(modelo.n_features_in_)
    if hasattr(modelo, "steps"):
        for _, step in modelo.steps:
            if hasattr(step, "n_features_in_"):
                return int(step.n_features_in_)
    return None


def _sanity(path: Path, features: list[str] | None, scaler_path: Path | None = None) -> dict[str, Any]:
    if not path.is_file():
        return {"ok": False, "motivo": "archivo no encontrado"}
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            artefacto = joblib.load(path)
    except Exception as e:
        return {"ok": False, "motivo": f"load: {e}"}

    if isinstance(artefacto, dict):
        claves = sorted(artefacto.keys())
        return {
            "ok": False,
            "motivo": f"artefacto es dict (esperado estimador sklearn): claves={claves}",
        }

    modelo = artefacto
    scaler = None
    if scaler_path and scaler_path.is_file():
        try:
            scaler = joblib.load(scaler_path)
        except Exception as e:
            return {"ok": False, "motivo": f"scaler_load: {e}"}

    feats = features or ["dia_año", "hora", "humedad", "presion", "viento_velocidad"]
    X = _vector(feats)
    n = _n_features(modelo)
    if n and n != len(X):
        X = (X + [0.0] * n)[:n]

    try:
        X_in = scaler.transform([X]) if scaler is not None else [X]
        pred = modelo.predict(X_in)
        val = float(np.asarray(pred).ravel()[0])
        if val != val:
            return {"ok": False, "motivo": "prediccion NaN"}
        return {"ok": True, "prediccion_prueba": round(val, 4)}
    except Exception as e:
        return {"ok": False, "motivo": f"predict: {e}"}


def auditar_manifest() -> dict[str, Any]:
    if not MANIFEST_PATH.is_file():
        return {"error": "model_manifest.json no encontrado", "servibles": 0, "total": 0}

    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    modelos = manifest.get("modelos", [])
    ok, fallos = [], []

    for m in modelos:
        rel = m.get("modelo_path") or f"{m.get('paquete')}/{m.get('archivo')}"
        path = MODELOS_ROOT / rel
        scaler = MODELOS_ROOT / m["scaler"] if m.get("scaler") else None
        s = _sanity(path, m.get("features"), scaler)
        item = {"modelo_path": rel, **s}
        if s.get("ok"):
            ok.append(item)
        else:
            fallos.append(item)

    return {
        "total": len(modelos),
        "servibles": len(ok),
        "no_servibles": len(fallos),
        "fallos": fallos,
        "sklearn_manifest": manifest.get("sklearn_version"),
        "actualizado": manifest.get("actualizado"),
    }


def auditar_huérfanos() -> dict[str, Any]:
    if not MANIFEST_PATH.is_file():
        return {
            "activos_manifest": [],
            "huérfanos_joblib": [],
            "pkl_legacy": [],
            "archivo_residual": [],
        }

    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    activos_manifest = []
    en_manifest = set()
    for m in manifest.get("modelos", []):
        rel = m.get("modelo_path") or f"{m.get('paquete')}/{m.get('archivo')}"
        en_manifest.add(m.get("archivo"))
        en_manifest.add(Path(rel).name)
        activos_manifest.append(rel)

    joblib_todos = {p.name for p in MODELOS_ROOT.rglob("*.joblib")}
    pkl_todos = {p.relative_to(MODELOS_ROOT).as_posix() for p in MODELOS_ROOT.rglob("*.pkl")}
    archivo_residual = sorted(
        p.relative_to(MODELOS_ROOT).as_posix()
        for p in MODELOS_ROOT.rglob("*")
        if p.is_dir() and p.name.lower() in {"deep_learning", "deprecated", "archive", "archivo"}
    )

    huérfanos_joblib = sorted(
        p.relative_to(MODELOS_ROOT).as_posix()
        for p in MODELOS_ROOT.rglob("*.joblib")
        if p.name not in en_manifest and not p.name.endswith("_scaler.joblib")
    )
    # scalers linked via manifest scaler field — skip if stem matches
    stems_manifest = {Path(x).stem.replace("_scaler", "") for x in en_manifest}
    huérfanos_joblib = [
        h
        for h in huérfanos_joblib
        if Path(h).stem.replace("_scaler", "") not in stems_manifest
        or not h.endswith("_scaler.joblib")
    ]

    return {
        "activos_manifest": activos_manifest,
        "joblib_en_disco": len(joblib_todos),
        "pkl_legacy": sorted(pkl_todos),
        "huérfanos_joblib": huérfanos_joblib,
        "archivo_residual": archivo_residual,
    }


def auditar_scripts() -> list[dict[str, str]]:
    hallazgos = []
    for nombre in SCRIPTS_PELIGROSOS:
        path = SCRIPT_DIR / nombre
        if not path.is_file():
            continue
        texto = path.read_text(encoding="utf-8", errors="replace")
        riesgos = []
        if 'modelos_dir = "' in texto or "models_dir = '" in texto or 'directorio_modelos = "' in texto:
            riesgos.append("ruta_relativa_cwd")
        if "joblib.dump({" in texto:
            riesgos.append("guarda_dict_no_estimador")
        if ".pkl" in texto and "joblib.dump" in texto:
            riesgos.append("mezcla_pkl_joblib")
        if "DecisionTreeRegressor" in texto:
            riesgos.append("decision_tree_legacy_sklearn")
        if riesgos:
            hallazgos.append({"script": nombre, "riesgos": ", ".join(riesgos)})
    return hallazgos


def main() -> int:
    print("=== Auditoría METGO módulo 06 — modelos ===\n")
    print(f"Raíz modelos: {MODELOS_ROOT}\n")

    man = auditar_manifest()
    print(f"Manifest: {man.get('servibles', 0)}/{man.get('total', 0)} servibles")
    if man.get("sklearn_manifest"):
        print(f"  sklearn entrenamiento: {man['sklearn_manifest']}  ({man.get('actualizado', '')})")
    for f in man.get("fallos", []):
        print(f"  ✗ {f['modelo_path']}: {f.get('motivo')}")

    print("\n--- Huérfanos / residuos ---")
    h = auditar_huérfanos()
    if h.get("pkl_legacy"):
        print(f"  .pkl legacy (no usados por API): {', '.join(h['pkl_legacy'])}")
    if h.get("huérfanos_joblib"):
        for o in h["huérfanos_joblib"]:
            print(f"  joblib fuera de manifest: {o}")
    if h.get("carpeta_deep_learning_residual"):
        print("  ⚠ modelos/modelos/deep_learning/ — residual, no integrado en API")

    print("\n--- Scripts legacy con riesgo de corrupción ---")
    for s in auditar_scripts():
        print(f"  {s['script']}: {s['riesgos']}")
    print("\n  Pipeline producción: api_rest.integracion.ml_train_runner.entrenar_todos()")
    print("  No ejecutar scripts legacy salvo METGO_ALLOW_LEGACY_ML=1\n")

    return 0 if man.get("no_servibles", 1) == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
