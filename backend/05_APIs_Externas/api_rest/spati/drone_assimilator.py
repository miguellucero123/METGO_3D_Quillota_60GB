#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SPATI — Asimilación de perfil vertical de dron (sesgo + decaimiento)."""

from __future__ import annotations

import math
from datetime import datetime, timezone
from typing import Any

import numpy as np
import pandas as pd


class DroneProfileError(ValueError):
    pass


class DroneAssimilator:
    """e(z) = v_dron − v_modelo; v_corr = v_mos + e · exp(−t/τ)."""

    def validar_perfil(self, perfil: dict[str, Any], h_pluma: float) -> None:
        niveles = perfil.get("niveles") or []
        if len(niveles) < 2:
            raise DroneProfileError("Se requieren al menos 2 niveles en el perfil")
        alts = [float(n["altura_m"]) for n in niveles]
        if alts != sorted(alts):
            raise DroneProfileError("Niveles deben estar ordenados por altura ascendente")
        if max(alts) < h_pluma:
            raise DroneProfileError(
                f"Altura máxima del perfil ({max(alts)} m) < h_pluma ({h_pluma} m)"
            )
        vels = [float(n["velocidad_kmh"]) for n in niveles]
        for a, b in zip(vels, vels[1:]):
            if abs(b - a) > 30:
                raise DroneProfileError(
                    f"Salto sospechoso de velocidad entre niveles: {a} → {b} km/h"
                )
        ts = perfil.get("timestamp_vuelo")
        if ts:
            try:
                t = datetime.fromisoformat(str(ts).replace("Z", "+00:00"))
                if t.tzinfo is None:
                    t = t.replace(tzinfo=timezone.utc)
                age_h = (datetime.now(timezone.utc) - t.astimezone(timezone.utc)).total_seconds() / 3600
                if age_h > 12:
                    raise DroneProfileError(
                        f"Perfil con más de 12 h de antigüedad ({age_h:.1f} h)"
                    )
            except DroneProfileError:
                raise
            except Exception as exc:
                raise DroneProfileError(f"timestamp_vuelo inválido: {exc}") from exc

    def calcular_sesgo(
        self,
        perfil: dict[str, Any],
        v_modelo_en_h_pluma: float,
        h_pluma: float,
    ) -> float:
        self.validar_perfil(perfil, h_pluma)
        niveles = perfil["niveles"]
        alts = np.array([float(n["altura_m"]) for n in niveles], dtype=float)
        vels = np.array([float(n["velocidad_kmh"]) for n in niveles], dtype=float)
        v_dron = float(np.interp(h_pluma, alts, vels))
        return float(v_dron - float(v_modelo_en_h_pluma))

    def aplicar_correccion(
        self,
        df: pd.DataFrame,
        sesgo: float,
        tau_horas: float = 6.0,
        col_in: str = "v_mos_kmh",
        col_out: str = "v_dron_corr_kmh",
    ) -> pd.DataFrame:
        out = df.copy()
        if "horas_desde_vuelo" not in out.columns:
            raise KeyError("DataFrame sin columna horas_desde_vuelo")
        if col_in not in out.columns:
            raise KeyError(f"DataFrame sin columna {col_in}")
        w = np.exp(-out["horas_desde_vuelo"].astype(float) / float(tau_horas))
        out["peso_dron"] = w
        base = out[col_in].astype(float)
        out[col_out] = (base + float(sesgo) * w).clip(lower=0.0)
        return out

    def promedio_multivuelo(self, lista_perfiles: list[dict[str, Any]]) -> dict[str, Any]:
        if not lista_perfiles:
            raise DroneProfileError("lista_perfiles vacía")
        # Agrupar por altura redondeada y mediana de velocidad
        from collections import defaultdict

        buckets: dict[float, list[float]] = defaultdict(list)
        dirs: dict[float, list[float]] = defaultdict(list)
        for p in lista_perfiles[:5]:
            for n in p.get("niveles") or []:
                h = round(float(n["altura_m"]), 1)
                buckets[h].append(float(n["velocidad_kmh"]))
                if n.get("direccion_deg") is not None:
                    dirs[h].append(float(n["direccion_deg"]))
        niveles = []
        for h in sorted(buckets):
            item = {
                "altura_m": h,
                "velocidad_kmh": float(np.median(buckets[h])),
            }
            if dirs.get(h):
                item["direccion_deg"] = float(np.median(dirs[h]))
            niveles.append(item)
        base = dict(lista_perfiles[0])
        base["niveles"] = niveles
        base["timestamp_vuelo"] = lista_perfiles[-1].get("timestamp_vuelo")
        return base
