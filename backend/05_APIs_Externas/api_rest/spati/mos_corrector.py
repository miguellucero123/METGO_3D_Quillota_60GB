#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SPATI — MOS / corrección estadística (XGBoost opcional; fallback sin MOS)."""

from __future__ import annotations

import logging
from typing import Any

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


class MOSCorrector:
    """Si no hay historial suficiente o falta xgboost → modo_sin_mos=True."""

    def __init__(self):
        self.modelo = None
        self.modo_sin_mos = True
        self.metricas: dict[str, Any] = {}

    def _features(self, df: pd.DataFrame) -> pd.DataFrame:
        out = pd.DataFrame(index=df.index)
        out["v_fisica_grua"] = df.get("v_fisica_grua", df.get("viento_modelo_10m"))
        out["dir_modelo"] = df.get("dir_modelo", 0)
        u, v = [], []
        from api_rest.spati.physics_engine import PhysicsEngine

        pe = PhysicsEngine()
        for i in range(len(df)):
            vel = float(out["v_fisica_grua"].iloc[i] or 0)
            dire = float(out["dir_modelo"].iloc[i] or 0)
            ui, vi = pe.calcular_componentes_uv(vel, dire)
            u.append(ui)
            v.append(vi)
        out["u_viento"] = u
        out["v_viento"] = v
        out["rafaga_modelo_10m"] = df.get("rafaga_modelo_10m", out["v_fisica_grua"])
        out["temp_modelo"] = df.get("temp_celsius", 15)
        if hasattr(df.index, "hour"):
            hora = df.index.hour.astype(float)
            mes = df.index.month.astype(float)
        else:
            hora = np.zeros(len(df))
            mes = np.ones(len(df))
        out["hora_dia"] = hora
        out["mes"] = mes
        out["seno_hora"] = np.sin(2 * np.pi * hora / 24)
        out["coseno_hora"] = np.cos(2 * np.pi * hora / 24)
        out["seno_mes"] = np.sin(2 * np.pi * mes / 12)
        out["coseno_mes"] = np.cos(2 * np.pi * mes / 12)
        return out.fillna(0)

    def cargar_o_entrenar(
        self,
        df_hist: pd.DataFrame | None,
        sitio_id: str,
        min_dias: int = 30,
    ) -> "MOSCorrector":
        """Entrena XGBoost si hay ≥ min_dias de pares; si no, modo sin MOS."""
        self.modo_sin_mos = True
        self.modelo = None
        if df_hist is None or df_hist.empty:
            logger.info("MOS %s: sin historial → modo_sin_mos", sitio_id)
            return self
        if "rafaga_maxima_aws" not in df_hist.columns:
            logger.info("MOS %s: sin columna rafaga_maxima_aws → modo_sin_mos", sitio_id)
            return self
        try:
            import xgboost as xgb
            from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
        except ImportError:
            logger.warning("xgboost/sklearn no disponible → modo_sin_mos")
            return self

        df = df_hist.sort_index()
        if len(df) < max(48, min_dias * 4):
            logger.info("MOS %s: historial insuficiente (%s filas)", sitio_id, len(df))
            return self

        X = self._features(df)
        y = df["rafaga_maxima_aws"].astype(float)
        n_train = int(len(df) * 0.80)
        X_train, X_test = X.iloc[:n_train], X.iloc[n_train:]
        y_train, y_test = y.iloc[:n_train], y.iloc[n_train:]
        model = xgb.XGBRegressor(
            n_estimators=300,
            max_depth=5,
            learning_rate=0.07,
            subsample=0.8,
            colsample_bytree=0.8,
            min_child_weight=3,
            reg_alpha=0.05,
            reg_lambda=1.0,
            random_state=42,
            objective="reg:squarederror",
        )
        model.fit(X_train, y_train)
        pred = model.predict(X_test) if len(X_test) else model.predict(X_train)
        y_eval = y_test if len(X_test) else y_train
        self.metricas = {
            "mae": float(mean_absolute_error(y_eval, pred)),
            "rmse": float(mean_squared_error(y_eval, pred) ** 0.5),
            "bias": float(np.mean(pred - y_eval)),
            "r2": float(r2_score(y_eval, pred)) if len(y_eval) > 1 else None,
            "n_train": int(n_train),
            "sitio_id": sitio_id,
        }
        self.modelo = model
        self.modo_sin_mos = False
        logger.info("MOS %s entrenado: MAE=%.2f", sitio_id, self.metricas["mae"])
        return self

    def predecir(self, df: pd.DataFrame) -> pd.Series:
        if self.modo_sin_mos or self.modelo is None:
            # Sin MOS: usar ráfaga modelo o v_fisica
            if "rafaga_modelo_10m" in df.columns:
                base = df["rafaga_modelo_10m"].fillna(df.get("v_fisica_grua"))
            else:
                base = df["v_fisica_grua"]
            return base.astype(float)
        X = self._features(df)
        return pd.Series(self.modelo.predict(X), index=df.index, name="v_mos_kmh")
