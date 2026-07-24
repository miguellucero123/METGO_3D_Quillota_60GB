#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Entrena clasificador episodio PM10 (Copiapó) — E12.

Fuente de entrenamiento (prioridad):
1. CSV histórico ``--csv`` (columnas fecha,pm10,pm25,so2,no2,o3)
2. Open-Meteo Air Quality (CAMS) past_days si hay red
3. Serie sintética autocorrelacionada (solo para CI / smoke)

Etiqueta: episodio al día siguiente si ICAP(PM10,PM2.5) >= 200.
Artefacto: ``modelos/modelos_dominio_copiapo/pm10_episodio.joblib`` + meta.json
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
MODELOS_DIR = Path(__file__).resolve().parents[1] / "modelos" / "modelos_dominio_copiapo"
API_REST = ROOT / "backend" / "05_APIs_Externas"
if str(API_REST) not in sys.path:
    sys.path.insert(0, str(API_REST))

FEATURES = ["pm10", "pm25", "so2", "no2", "o3", "dia_año", "sin_doy", "cos_doy"]


def _icap_pm10(conc: float) -> float:
    bp = [(0, 0.0), (100, 150.0), (200, 195.0), (300, 240.0), (500, 330.0)]
    if conc <= 0:
        return 0.0
    for (i0, c0), (i1, c1) in zip(bp, bp[1:]):
        if conc <= c1:
            return i0 + (conc - c0) * (i1 - i0) / (c1 - c0)
    return 500.0


def _icap_pm25(conc: float) -> float:
    bp = [(0, 0.0), (100, 50.0), (200, 80.0), (300, 110.0), (500, 170.0)]
    if conc <= 0:
        return 0.0
    for (i0, c0), (i1, c1) in zip(bp, bp[1:]):
        if conc <= c1:
            return i0 + (conc - c0) * (i1 - i0) / (c1 - c0)
    return 500.0


def _icap(pm25: float | None, pm10: float | None) -> float:
    vals = []
    if pm25 is not None:
        vals.append(_icap_pm25(float(pm25)))
    if pm10 is not None:
        vals.append(_icap_pm10(float(pm10)))
    return max(vals) if vals else 0.0


def _feats(row: dict[str, Any]) -> list[float]:
    d = row.get("fecha") or "2026-01-01"
    try:
        dt = date.fromisoformat(str(d)[:10])
    except ValueError:
        dt = date(2026, 1, 1)
    doy = dt.timetuple().tm_yday
    ang = 2 * math.pi * doy / 366.0
    return [
        float(row.get("pm10") or 0.0),
        float(row.get("pm25") or row.get("pm2_5") or 0.0),
        float(row.get("so2") or 0.0),
        float(row.get("no2") or 0.0),
        float(row.get("o3") or 0.0),
        float(doy),
        math.sin(ang),
        math.cos(ang),
    ]


def _leer_csv(path: Path) -> list[dict[str, Any]]:
    filas: list[dict[str, Any]] = []
    with path.open(encoding="utf-8-sig", newline="") as fh:
        for row in csv.DictReader(fh):
            fecha = (row.get("fecha") or "").strip()[:10]
            if not fecha:
                continue
            item: dict[str, Any] = {"fecha": fecha}
            for k in ("pm10", "pm25", "pm2_5", "so2", "no2", "o3"):
                raw = row.get(k)
                if raw is None or str(raw).strip() == "":
                    continue
                try:
                    item["pm25" if k == "pm2_5" else k] = float(raw)
                except ValueError:
                    pass
            filas.append(item)
    return filas


def _fetch_cams(lat: float, lon: float, past_days: int = 92) -> list[dict[str, Any]]:
    import requests

    url = "https://air-quality-api.open-meteo.com/v1/air-quality"
    params = {
        "latitude": lat,
        "longitude": lon,
        "past_days": min(past_days, 92),
        "forecast_days": 1,
        "hourly": "pm10,pm2_5,sulphur_dioxide,nitrogen_dioxide,ozone",
        "timezone": "America/Santiago",
    }
    r = requests.get(url, params=params, timeout=45)
    r.raise_for_status()
    hourly = r.json().get("hourly") or {}
    tiempos = hourly.get("time") or []
    por_dia: dict[str, dict[str, list[float]]] = {}
    keys = {
        "pm10": "pm10",
        "pm2_5": "pm25",
        "sulphur_dioxide": "so2",
        "nitrogen_dioxide": "no2",
        "ozone": "o3",
    }
    for i, ts in enumerate(tiempos):
        dia = str(ts)[:10]
        bucket = por_dia.setdefault(dia, {v: [] for v in keys.values()})
        for api_k, out_k in keys.items():
            serie = hourly.get(api_k) or []
            if i < len(serie) and serie[i] is not None:
                bucket[out_k].append(float(serie[i]))
    filas = []
    for dia in sorted(por_dia):
        b = por_dia[dia]
        fila = {"fecha": dia}
        for k, vals in b.items():
            fila[k] = round(sum(vals) / len(vals), 2) if vals else 0.0
        filas.append(fila)
    return filas


def _sintetica(n: int = 180, seed: int = 42) -> list[dict[str, Any]]:
    """Serie AR con episodios ocasionales (para CI sin red)."""
    import random

    rng = random.Random(seed)
    pm10 = 40.0
    filas = []
    base = date(2025, 1, 1)
    for i in range(n):
        shock = 80.0 if rng.random() < 0.08 else 0.0
        pm10 = max(5.0, 0.75 * pm10 + rng.gauss(12, 8) + shock)
        pm25 = max(2.0, pm10 * (0.35 + rng.random() * 0.15))
        filas.append(
            {
                "fecha": (base + timedelta(days=i)).isoformat(),
                "pm10": round(pm10, 1),
                "pm25": round(pm25, 1),
                "so2": round(max(0.0, rng.gauss(3, 1.5)), 1),
                "no2": round(max(0.0, rng.gauss(8, 3)), 1),
                "o3": round(max(0.0, rng.gauss(40, 10)), 1),
            }
        )
    return filas


def _dataset(filas: list[dict[str, Any]]) -> tuple[list[list[float]], list[int]]:
    X: list[list[float]] = []
    y: list[int] = []
    for i in range(len(filas) - 1):
        hoy = filas[i]
        manana = filas[i + 1]
        icap_m = _icap(manana.get("pm25"), manana.get("pm10"))
        X.append(_feats(hoy))
        y.append(1 if icap_m >= 200 else 0)
    return X, y


def entrenar(filas: list[dict[str, Any]], origen: str) -> dict[str, Any]:
    """Regresa ICAP del día siguiente; episodio = pred >= 200."""
    from sklearn.ensemble import GradientBoostingRegressor
    from sklearn.metrics import mean_absolute_error, r2_score
    from sklearn.model_selection import train_test_split
    import joblib

    X: list[list[float]] = []
    y: list[float] = []
    for i in range(len(filas) - 1):
        X.append(_feats(filas[i]))
        y.append(_icap(filas[i + 1].get("pm25"), filas[i + 1].get("pm10")))
    if len(X) < 30:
        raise SystemExit(f"Pocos días para entrenar: {len(X)}")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42
    )
    reg = GradientBoostingRegressor(
        n_estimators=80, max_depth=3, learning_rate=0.08, random_state=42
    )
    reg.fit(X_train, y_train)
    pred = reg.predict(X_test)
    mae = float(mean_absolute_error(y_test, pred))
    r2 = float(r2_score(y_test, pred))
    # Clasificación derivada en test
    y_ep = [1 if v >= 200 else 0 for v in y_test]
    p_ep = [1 if v >= 200 else 0 for v in pred]
    tp = sum(1 for a, b in zip(y_ep, p_ep) if a == 1 and b == 1)
    fp = sum(1 for a, b in zip(y_ep, p_ep) if a == 0 and b == 1)
    fn = sum(1 for a, b in zip(y_ep, p_ep) if a == 1 and b == 0)
    prec = tp / (tp + fp) if (tp + fp) else 0.0
    rec = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = 2 * prec * rec / (prec + rec) if (prec + rec) else 0.0

    meta = {
        "id": "pm10_episodio_copiapo",
        "variable": "episodio_pm10",
        "target": "icap_dia_siguiente",
        "sitio": "copiapo",
        "features": FEATURES,
        "sklearn": "GradientBoostingRegressor",
        "umbral_icap_etiqueta": 200,
        "horizonte": "dia_siguiente",
        "origen_datos": origen,
        "n_filas": len(filas),
        "n_train": len(X_train),
        "n_test": len(X_test),
        "mae_icap": round(mae, 4),
        "r2": round(r2, 4),
        "f1_episodio_derivado": round(f1, 4),
        "positivos_test": int(sum(y_ep)),
        "entrenado": datetime.now(timezone.utc).isoformat(),
        "servible": True,
        "archivo": "pm10_episodio.joblib",
    }
    MODELOS_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(
        {"model": reg, "features": FEATURES, "meta": meta, "tipo": "regresor_icap"},
        MODELOS_DIR / "pm10_episodio.joblib",
    )
    (MODELOS_DIR / "meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    return meta


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", type=Path, default=None)
    parser.add_argument("--lat", type=float, default=-27.3668)
    parser.add_argument("--lon", type=float, default=-70.3323)
    parser.add_argument("--past-days", type=int, default=92)
    parser.add_argument("--sintetico", action="store_true")
    args = parser.parse_args()

    origen = "sintetico"
    filas: list[dict[str, Any]] = []
    if args.csv and args.csv.is_file():
        filas = _leer_csv(args.csv)
        origen = f"csv:{args.csv.name}"
    elif not args.sintetico:
        try:
            filas = _fetch_cams(args.lat, args.lon, args.past_days)
            origen = "openmeteo_cams"
            print(f"CAMS: {len(filas)} días")
        except Exception as exc:
            print(f"CAMS no disponible ({exc}); usando sintético")
            filas = _sintetica()
            origen = "sintetico_fallback"
    else:
        filas = _sintetica()

    meta = entrenar(filas, origen)
    print(json.dumps(meta, indent=2))


if __name__ == "__main__":
    main()
