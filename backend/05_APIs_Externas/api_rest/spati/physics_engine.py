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

# Niveles AGL estándar para zona de izaje / calibración dron
ALTURAS_PERFIL_IZAJES_M: tuple[int, ...] = (10, 20, 30, 40, 50, 60, 70, 80, 100, 200)

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

    def velocidad_a_altura(
        self,
        v_ref: float,
        h_objetivo: float,
        z0: float,
        h_ref: float = 10.0,
    ) -> float:
        """Perfil logarítmico Prandtl. Permite h == h_ref. Retorno km/h."""
        if z0 <= 0:
            raise ValueError(f"z0 inválido: {z0}")
        if h_objetivo <= z0:
            raise ValueError(f"h_objetivo ({h_objetivo}) debe ser > z0 ({z0})")
        if h_ref <= z0:
            raise ValueError(f"h_ref ({h_ref}) debe ser > z0 ({z0})")
        if v_ref < 0:
            raise ValueError(f"v_ref negativo: {v_ref}")
        if abs(h_objetivo - h_ref) < 1e-9:
            return float(v_ref)
        return float(v_ref * (math.log(h_objetivo / z0) / math.log(h_ref / z0)))

    def extrapolar_altura(
        self,
        v_ref: float,
        h_objetivo: float,
        z0: float,
        h_ref: float = 10.0,
    ) -> float:
        """Alias hacia arriba (h > h_ref). Retrocompatibilidad API."""
        if h_objetivo < h_ref:
            raise ValueError(
                f"h_objetivo ({h_objetivo}) debe ser > h_ref ({h_ref}); "
                "use velocidad_a_altura para niveles ≤ h_ref"
            )
        return self.velocidad_a_altura(v_ref, h_objetivo, z0, h_ref)

    def perfil_vertical_izaje(
        self,
        v_10m_kmh: float,
        z0: float,
        *,
        alturas_m: tuple[int, ...] | list[int] | None = None,
        v_80m_kmh: float | None = None,
        v_100m_kmh: float | None = None,
        h_ref: float = 10.0,
        rho: float | None = None,
        area_m2: float | None = None,
        cd: float | None = None,
    ) -> list[dict[str, Any]]:
        """Perfil 10…100…200 m AGL. Ancla NWP 80/100 si existen; si no, log puro.

        Retorna lista [{altura_m, v_kmh, fuente, fuerza_n?}].
        """
        alturas = tuple(alturas_m or ALTURAS_PERFIL_IZAJES_M)
        if v_10m_kmh is None or (isinstance(v_10m_kmh, float) and math.isnan(v_10m_kmh)):
            raise ValueError("v_10m_kmh requerido")

        # Anclas (h, v, fuente)
        anchors: list[tuple[float, float, str]] = [(h_ref, float(v_10m_kmh), "nwp_10m")]
        if v_80m_kmh is not None and not (isinstance(v_80m_kmh, float) and math.isnan(v_80m_kmh)):
            anchors.append((80.0, float(v_80m_kmh), "nwp_80m"))
        else:
            anchors.append(
                (80.0, self.velocidad_a_altura(float(v_10m_kmh), 80.0, z0, h_ref), "log_desde_10m")
            )
        if v_100m_kmh is not None and not (
            isinstance(v_100m_kmh, float) and math.isnan(v_100m_kmh)
        ):
            anchors.append((100.0, float(v_100m_kmh), "nwp_100m"))
        else:
            # Extrapolar desde la última ancla conocida
            h_a, v_a, _ = anchors[-1]
            anchors.append(
                (100.0, self.velocidad_a_altura(v_a, 100.0, z0, h_a), "log_desde_ancla")
            )
        anchors.sort(key=lambda x: x[0])

        out: list[dict[str, Any]] = []
        for h in alturas:
            hf = float(h)
            v, fuente = self._interpolar_anclas(hf, anchors, z0)
            item: dict[str, Any] = {
                "altura_m": int(h) if float(h).is_integer() else h,
                "v_kmh": round(v, 2),
                "fuente": fuente,
            }
            if rho is not None and area_m2 is not None and cd is not None:
                try:
                    item["fuerza_n"] = round(
                        self.calcular_fuerza(v, float(rho), float(area_m2), float(cd)), 1
                    )
                except Exception:
                    item["fuerza_n"] = None
            out.append(item)
        return out

    def _interpolar_anclas(
        self,
        h: float,
        anchors: list[tuple[float, float, str]],
        z0: float,
    ) -> tuple[float, str]:
        """Interp. lineal en ln(h) entre anclas; fuera de rango → log desde ancla cercana."""
        if h <= z0:
            raise ValueError(f"h={h} ≤ z0={z0}")
        # Exact match
        for ha, va, fa in anchors:
            if abs(h - ha) < 1e-6:
                return float(va), fa
        # Debajo de primera ancla
        if h < anchors[0][0]:
            ha, va, _ = anchors[0]
            return self.velocidad_a_altura(va, h, z0, ha), "log_desde_ancla"
        # Entre anclas
        for i in range(len(anchors) - 1):
            h0, v0, f0 = anchors[i]
            h1, v1, f1 = anchors[i + 1]
            if h0 <= h <= h1:
                ln0, ln1, lnh = math.log(h0 / z0), math.log(h1 / z0), math.log(h / z0)
                if abs(ln1 - ln0) < 1e-12:
                    return float(v0), f"{f0}+{f1}"
                w = (lnh - ln0) / (ln1 - ln0)
                return float(v0 + w * (v1 - v0)), f"blend_{int(h0)}_{int(h1)}"
        # Sobre última ancla (p.ej. 200 m desde 100 m)
        h_a, v_a, _ = anchors[-1]
        return self.velocidad_a_altura(v_a, h, z0, h_a), "log_sobre_100m"

    def cizalladura_vertical(
        self, v_bajo: float, v_alto: float, h_bajo: float, h_alto: float
    ) -> dict[str, float]:
        """Δv y gradiente (km/h)/m entre dos niveles."""
        dh = float(h_alto) - float(h_bajo)
        if dh <= 0:
            raise ValueError("h_alto debe ser > h_bajo")
        dv = float(v_alto) - float(v_bajo)
        return {
            "delta_v_kmh": round(dv, 2),
            "gradiente_kmh_por_m": round(dv / dh, 4),
            "h_bajo_m": float(h_bajo),
            "h_alto_m": float(h_alto),
        }

    def indice_turbulencia(self, v_media_kmh: float, rafaga_kmh: float) -> float | None:
        """(ráfaga − media) / media. None si media ≈ 0."""
        vm = float(v_media_kmh or 0)
        if vm < 0.5:
            return None
        return round((float(rafaga_kmh) - vm) / vm, 3)

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
