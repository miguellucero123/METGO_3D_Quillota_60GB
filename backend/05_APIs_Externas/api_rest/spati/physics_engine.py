#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SPATI — Física operacional de viento en altura de pluma.

DECISIÓN: ecuaciones exactas (perfil logarítmico Prandtl, gas ideal, fuerza ½ρv²ACd).
Unidades de viento de entrada/salida: km/h salvo donde se indique m/s.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

import pandas as pd

R_D = 287.05  # J/(kg·K)

GUST_FACTOR_TERRENO: dict[str, float] = {
    "costero_abierto": 1.30,
    "llano_semiarido": 1.40,
    "rajo_minero": 1.65,
    "valle_cordillera": 1.80,
    "zona_urbana": 1.50,
    # Alias eólicos alta montaña (fallback si no hay HighAltitudeEngine)
    "rajo_norte_grande": 1.75,
    "terreno_abierto": 1.40,
    "quebrada_cordillera": 1.85,
    "superficie_plana": 1.35,
    "rajo": 1.80,
}


@dataclass
class GruaConfig:
    """Parámetros de sitio / grúa (sin magic numbers en el pipeline)."""

    sitio_id: str
    lat: float
    lon: float
    altitud_msnm: float = 0.0
    altura_pluma_m: float = 55.0
    z0_terreno: float = 0.15
    tipo_terreno: str = "rajo_minero"
    area_carga_m2: float = 12.5
    coef_forma_cd: float = 1.2
    fuerza_limite_n: float = 25000.0
    h_ref_m: float = 10.0
    nombre: str = ""

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "GruaConfig":
        return cls(
            sitio_id=str(d.get("sitio_id") or d.get("id") or "sitio"),
            lat=float(d["lat"]),
            lon=float(d["lon"]),
            altitud_msnm=float(d.get("altitud_msnm") or 0),
            altura_pluma_m=float(d.get("altura_pluma_m") or 55),
            z0_terreno=float(d.get("z0_terreno") or 0.15),
            tipo_terreno=str(d.get("tipo_terreno") or "rajo_minero"),
            area_carga_m2=float(d.get("area_carga_m2") or 12.5),
            coef_forma_cd=float(d.get("coef_forma_cd") or 1.2),
            fuerza_limite_n=float(d.get("fuerza_limite_n") or 25000),
            h_ref_m=float(d.get("h_ref_m") or 10),
            nombre=str(d.get("nombre") or ""),
        )


class PhysicsEngine:
    """Extrapolación vertical, densidad y fuerza aerodinámica sobre la carga."""

    def extrapolar_altura(
        self,
        v_ref: float,
        h_objetivo: float,
        z0: float,
        h_ref: float = 10.0,
    ) -> float:
        """Perfil logarítmico: v(h) = v_ref · ln(h/z0) / ln(h_ref/z0). Retorno km/h."""
        if z0 <= 0 or z0 >= h_objetivo:
            raise ValueError(f"z0 inválido: {z0} (debe 0 < z0 < h_objetivo={h_objetivo})")
        if v_ref < 0:
            raise ValueError(f"v_ref negativo: {v_ref}")
        if h_objetivo <= h_ref:
            raise ValueError(
                f"h_objetivo ({h_objetivo}) debe ser > h_ref ({h_ref}); no se extrapola hacia abajo"
            )
        return float(v_ref * (math.log(h_objetivo / z0) / math.log(h_ref / z0)))

    def calcular_densidad(self, temp_celsius: float, presion_pa: float) -> float:
        """ρ = p / (R_d · T_K). Retorno kg/m³. Permite ≥45 kPa (≈4500+ msnm)."""
        if temp_celsius < -60 or temp_celsius > 60:
            raise ValueError(f"temperatura fuera de rango: {temp_celsius} °C")
        if presion_pa < 45000 or presion_pa > 106000:
            raise ValueError(f"presión fuera de rango: {presion_pa} Pa")
        t_k = temp_celsius + 273.15
        return float(presion_pa / (R_D * t_k))

    def calcular_fuerza(
        self,
        velocidad_kmh: float,
        rho: float,
        area_m2: float,
        cd: float,
    ) -> float:
        """F = ½ · ρ · (v/3.6)² · A · Cd. Retorno Newton."""
        v_ms = velocidad_kmh / 3.6
        return float(0.5 * rho * (v_ms**2) * area_m2 * cd)

    def porcentaje_del_limite(self, fuerza_n: float, f_limite_n: float) -> float:
        if f_limite_n <= 0:
            raise ValueError("F_limite debe ser > 0")
        return float(100.0 * fuerza_n / f_limite_n)

    def calcular_componentes_uv(
        self, velocidad: float, direccion_deg: float
    ) -> tuple[float, float]:
        """u = −v·sin(dir), v = −v·cos(dir). Convención meteo FROM."""
        rad = math.radians(direccion_deg)
        u = -velocidad * math.sin(rad)
        v = -velocidad * math.cos(rad)
        return float(u), float(v)

    def aplicar_gust_factor(self, v_media: float, tipo_terreno: str) -> float:
        gf = GUST_FACTOR_TERRENO.get(tipo_terreno)
        if gf is None:
            raise ValueError(
                f"tipo_terreno desconocido: {tipo_terreno}. "
                f"Válidos: {list(GUST_FACTOR_TERRENO)}"
            )
        return float(v_media * gf)

    def extrapolar_serie(self, df: pd.DataFrame, cfg: GruaConfig) -> pd.DataFrame:
        """Agrega v_fisica_grua, rho, fuerza_n, pct_limite_diseno."""
        out = df.copy()
        v_col = "viento_modelo_10m" if "viento_modelo_10m" in out.columns else "v_modelo_10m"
        if v_col not in out.columns:
            raise KeyError("DataFrame sin columna viento_modelo_10m / v_modelo_10m")

        vs = []
        for v in out[v_col].tolist():
            if v is None or (isinstance(v, float) and math.isnan(v)):
                vs.append(None)
            else:
                vs.append(
                    self.extrapolar_altura(
                        float(v), cfg.altura_pluma_m, cfg.z0_terreno, cfg.h_ref_m
                    )
                )
        out["v_fisica_grua"] = vs

        temp_col = "temp_celsius" if "temp_celsius" in out.columns else "temperature_2m"
        p_col = "presion_pa" if "presion_pa" in out.columns else "surface_pressure"
        rhos, fuerzas, pcts = [], [], []
        for i, row in out.iterrows():
            t = row.get(temp_col)
            p = row.get(p_col)
            vf = row.get("v_fisica_grua")
            try:
                if t is None or p is None or vf is None:
                    raise ValueError("faltan T/p/v")
                rho = self.calcular_densidad(float(t), float(p))
                f = self.calcular_fuerza(float(vf), rho, cfg.area_carga_m2, cfg.coef_forma_cd)
                pct = self.porcentaje_del_limite(f, cfg.fuerza_limite_n)
            except Exception:
                rho, f, pct = None, None, None
            rhos.append(rho)
            fuerzas.append(round(f, 1) if f is not None else None)
            pcts.append(round(pct, 1) if pct is not None else None)
        out["rho"] = rhos
        out["fuerza_n"] = fuerzas
        out["pct_limite_diseno"] = pcts
        return out
