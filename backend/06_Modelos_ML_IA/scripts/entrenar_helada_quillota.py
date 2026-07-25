#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Entrena clasificador de riesgo de helada (Quillota) — E12.

Features: Tmín, Tmáx, humedad, precipitación, viento, doy cíclico.
Etiqueta: helada al día siguiente si Tmín_t+1 <= 0 °C.

Fuente (prioridad):
1. CSV ``--csv`` (fecha,temperatura_min,temperatura_max,humedad,precipitacion,viento)
2. Serie sintética estacional (CI / smoke)

Artefacto: ``modelos/modelos_dominio_quillota/helada_riesgo.joblib`` + meta.json
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
MODELOS_DIR = Path(__file__).resolve().parents[1] / "modelos" / "modelos_dominio_quillota"

FEATURES = [
    "temperatura_min",
    "temperatura_max",
    "humedad",
    "precipitacion",
    "viento",
    "dia_año",
    "sin_doy",
    "cos_doy",
]


def _feats(row: dict[str, Any]) -> list[float]:
    d = row.get("fecha") or "2026-01-01"
    try:
        dt = date.fromisoformat(str(d)[:10])
    except ValueError:
        dt = date(2026, 1, 1)
    doy = dt.timetuple().tm_yday
    ang = 2 * math.pi * doy / 366.0
    return [
        float(row.get("temperatura_min") or row.get("t_min") or 0.0),
        float(row.get("temperatura_max") or row.get("t_max") or 0.0),
        float(row.get("humedad") or 60.0),
        float(row.get("precipitacion") or row.get("lluvia") or 0.0),
        float(row.get("viento") or 0.0),
        float(doy),
        math.sin(ang),
        math.cos(ang),
    ]


def _load_csv(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        for r in reader:
            rows.append(dict(r))
    return rows


def _serie_sintetica(n: int = 180) -> list[dict[str, Any]]:
    """Invierno chilleno: Tmín baja en jun–ago."""
    import random

    rng = random.Random(42)
    out: list[dict[str, Any]] = []
    base = date(2025, 1, 1)
    for i in range(n):
        d = base.fromordinal(base.toordinal() + i)
        doy = d.timetuple().tm_yday
        # Ciclo anual: mínimo ~ julio (doy 180–210)
        seasonal = 8.0 * math.cos(2 * math.pi * (doy - 15) / 365.0)
        t_min = seasonal + rng.uniform(-3.5, 2.0)
        t_max = t_min + rng.uniform(8.0, 16.0)
        out.append(
            {
                "fecha": d.isoformat(),
                "temperatura_min": round(t_min, 2),
                "temperatura_max": round(t_max, 2),
                "humedad": round(rng.uniform(40, 95), 1),
                "precipitacion": round(max(0.0, rng.gauss(0.5, 2.0)), 2),
                "viento": round(rng.uniform(0.5, 8.0), 2),
            }
        )
    return out


def _pares(rows: list[dict[str, Any]]) -> tuple[list[list[float]], list[int]]:
    X: list[list[float]] = []
    y: list[int] = []
    for i in range(len(rows) - 1):
        t_next = rows[i + 1].get("temperatura_min") or rows[i + 1].get("t_min")
        if t_next is None:
            continue
        try:
            label = 1 if float(t_next) <= 0.0 else 0
        except (TypeError, ValueError):
            continue
        X.append(_feats(rows[i]))
        y.append(label)
    return X, y


def entrenar(csv_path: Path | None = None) -> dict[str, Any]:
    from sklearn.ensemble import GradientBoostingClassifier
    from sklearn.metrics import accuracy_score, f1_score
    import joblib

    origen = "sintetico"
    if csv_path and csv_path.is_file():
        rows = _load_csv(csv_path)
        origen = f"csv:{csv_path.name}"
    else:
        rows = _serie_sintetica(220)

    X, y = _pares(rows)
    if len(X) < 30:
        raise SystemExit(f"Pocos pares de entrenamiento: {len(X)}")

    split = max(10, int(len(X) * 0.8))
    X_tr, X_te = X[:split], X[split:]
    y_tr, y_te = y[:split], y[split:]

    model = GradientBoostingClassifier(
        n_estimators=80,
        max_depth=3,
        learning_rate=0.08,
        random_state=42,
    )
    model.fit(X_tr, y_tr)
    pred = model.predict(X_te) if X_te else y_tr
    y_eval = y_te if X_te else y_tr
    acc = float(accuracy_score(y_eval, pred))
    f1 = float(f1_score(y_eval, pred, zero_division=0))

    MODELOS_DIR.mkdir(parents=True, exist_ok=True)
    meta = {
        "modelo_id": "helada_quillota",
        "tipo": "clasificador_helada",
        "features": FEATURES,
        "accuracy": round(acc, 4),
        "f1": round(f1, 4),
        "n_train": len(X_tr),
        "n_test": len(X_te),
        "positivos": int(sum(y)),
        "origen_datos": origen,
        "entrenado": datetime.now(timezone.utc).isoformat(),
        "umbral_tmin_c": 0.0,
    }
    bundle = {"tipo": "clasificador_helada", "model": model, "meta": meta, "features": FEATURES}
    joblib.dump(bundle, MODELOS_DIR / "helada_riesgo.joblib")
    (MODELOS_DIR / "meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(meta, ensure_ascii=False, indent=2))
    return meta


def main() -> None:
    parser = argparse.ArgumentParser(description="Entrena helada_quillota (E12)")
    parser.add_argument("--csv", type=Path, default=None, help="CSV histórico meteo")
    args = parser.parse_args()
    entrenar(args.csv)


if __name__ == "__main__":
    main()
