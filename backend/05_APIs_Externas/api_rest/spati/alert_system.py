#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SPATI — Niveles de alerta izaje (0–3) + ventanas seguras + resumen."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

import pandas as pd

NIVEL_NOMBRE = {0: "VERDE", 1: "AMARILLO", 2: "NARANJA", 3: "ROJO"}


@dataclass
class AlertResult:
    nivel: int
    flag_critico: bool
    flag_meteo: bool
    razon: str


class CraneSafetyAlertSystem:
    """Clasificación multi-variable por intervalo de 15 min."""

    def __init__(
        self,
        *,
        amarillo_min_kmh: float = 26.0,
        naranja_min_kmh: float = 30.0,
        rojo_min_kmh: float = 35.0,
        flag_critico_kmh: float = 36.0,
        rayos_pct: float = 30.0,
        precip_mmh: float = 2.0,
        fuerza_naranja_pct: float = 55.0,
        fuerza_rojo_pct: float = 80.0,
        **_extra: Any,
    ) -> None:
        self.amarillo_min_kmh = float(amarillo_min_kmh)
        self.naranja_min_kmh = float(naranja_min_kmh)
        self.rojo_min_kmh = float(rojo_min_kmh)
        self.flag_critico_kmh = float(flag_critico_kmh)
        self.rayos_pct = float(rayos_pct)
        self.precip_mmh = float(precip_mmh)
        self.fuerza_naranja_pct = float(fuerza_naranja_pct)
        self.fuerza_rojo_pct = float(fuerza_rojo_pct)

    @classmethod
    def from_umbrales(cls, umb: dict[str, Any] | None) -> "CraneSafetyAlertSystem":
        u = umb or {}
        return cls(
            amarillo_min_kmh=u.get("amarillo_min_kmh", 26),
            naranja_min_kmh=u.get("naranja_min_kmh", 30),
            rojo_min_kmh=u.get("rojo_min_kmh", 35),
            flag_critico_kmh=u.get("flag_critico_kmh", 36),
            rayos_pct=u.get("rayos_pct", 30),
            precip_mmh=u.get("precip_mmh", 2.0),
            fuerza_naranja_pct=u.get("fuerza_naranja_pct", 55),
            fuerza_rojo_pct=u.get("fuerza_rojo_pct", 80),
        )

    def clasificar_nivel(
        self,
        rafaga_kmh: float | None,
        prob_rayos_pct: float | None = None,
        precip_mmh: float | None = None,
        pct_fuerza: float | None = None,
    ) -> AlertResult:
        rafaga = float(rafaga_kmh or 0)
        razones: list[str] = []

        if rafaga >= self.rojo_min_kmh:
            nivel_viento = 3
            razones.append(f"ráfaga {rafaga:.1f} ≥ {self.rojo_min_kmh:g} km/h")
        elif rafaga >= self.naranja_min_kmh:
            nivel_viento = 2
            razones.append(
                f"ráfaga {rafaga:.1f} en {self.naranja_min_kmh:g}–{self.rojo_min_kmh - 1:g} km/h"
            )
        elif rafaga >= self.amarillo_min_kmh:
            nivel_viento = 1
            razones.append(
                f"ráfaga {rafaga:.1f} en {self.amarillo_min_kmh:g}–{self.naranja_min_kmh - 1:g} km/h"
            )
        else:
            nivel_viento = 0
            razones.append(f"ráfaga {rafaga:.1f} < {self.amarillo_min_kmh:g} km/h")

        flag_meteo = False
        if (prob_rayos_pct is not None and float(prob_rayos_pct) > self.rayos_pct) or (
            precip_mmh is not None and float(precip_mmh) > self.precip_mmh
        ):
            flag_meteo = True
            nivel_viento = max(nivel_viento, 2)
            razones.append("meteo secundaria (rayos/precip)")

        if pct_fuerza is not None:
            pf = float(pct_fuerza)
            if pf >= self.fuerza_rojo_pct and nivel_viento < 3:
                nivel_viento = 3
                razones.append(f"fuerza {pf:.0f}% ≥ {self.fuerza_rojo_pct:g}% límite")
            elif pf >= self.fuerza_naranja_pct and nivel_viento < 2:
                nivel_viento = 2
                razones.append(f"fuerza {pf:.0f}% ≥ {self.fuerza_naranja_pct:g}% límite")

        flag_critico = rafaga >= self.flag_critico_kmh
        if flag_critico:
            razones.append(f"flag crítico ≥ {self.flag_critico_kmh:g} km/h")

        return AlertResult(
            nivel=nivel_viento,
            flag_critico=flag_critico,
            flag_meteo=flag_meteo,
            razon="; ".join(razones),
        )

    def clasificar_serie(self, df: pd.DataFrame) -> pd.DataFrame:
        out = df.copy()
        # Ráfaga operativa: preferir v_final, si no rafaga modelo o v_fisica
        if "v_final_kmh" in out.columns:
            raf = out["v_final_kmh"]
        elif "rafaga_modelo_10m" in out.columns:
            raf = out["rafaga_modelo_10m"].fillna(out.get("v_fisica_grua"))
        else:
            raf = out.get("v_fisica_grua", out.get("viento_modelo_10m"))

        niveles, flags_c, flags_m, razones = [], [], [], []
        for i in range(len(out)):
            row = out.iloc[i]
            r = self.clasificar_nivel(
                float(raf.iloc[i]) if raf is not None and pd.notna(raf.iloc[i]) else 0.0,
                row.get("prob_rayos_pct"),
                row.get("precip_mmh"),
                row.get("pct_limite_diseno"),
            )
            niveles.append(r.nivel)
            flags_c.append(r.flag_critico)
            flags_m.append(r.flag_meteo)
            razones.append(r.razon)
        out["nivel_alerta"] = niveles
        out["nivel_nombre"] = [NIVEL_NOMBRE[n] for n in niveles]
        out["flag_critico"] = flags_c
        out["flag_meteo"] = flags_m
        out["razon_alerta"] = razones
        return out

    def detectar_ventanas_seguras(
        self,
        df: pd.DataFrame,
        min_horas: float = 2.0,
        solo_verde: bool = True,
    ) -> list[dict[str, Any]]:
        if "nivel_alerta" not in df.columns or df.empty:
            return []
        idx = df.index
        niveles = df["nivel_alerta"].tolist()
        max_nivel_ok = 0 if solo_verde else 1
        ventanas = []
        i = 0
        n = len(niveles)
        while i < n:
            if niveles[i] > max_nivel_ok:
                i += 1
                continue
            j = i
            while j < n and niveles[j] <= max_nivel_ok:
                j += 1
            t0, t1 = idx[i], idx[j - 1]
            dur_h = (t1 - t0).total_seconds() / 3600.0 + 0.25  # intervalo inclusivo
            if dur_h >= min_horas:
                sub = df.iloc[i:j]
                col = "v_final_kmh" if "v_final_kmh" in sub.columns else "v_fisica_grua"
                ventanas.append(
                    {
                        "inicio": t0.isoformat() if hasattr(t0, "isoformat") else str(t0),
                        "fin": t1.isoformat() if hasattr(t1, "isoformat") else str(t1),
                        "duracion_horas": round(dur_h, 2),
                        "rafaga_max_en_ventana": (
                            float(sub[col].max()) if col in sub.columns else None
                        ),
                        "tipo": "segura" if solo_verde else "restringida",
                    }
                )
            i = j
        return ventanas

    def generar_resumen_ejecutivo(
        self,
        df: pd.DataFrame,
        ventanas: list[dict[str, Any]],
        sitio: str,
    ) -> str:
        if df.empty:
            return f"[SPATI/{sitio}] Sin datos de pronóstico."
        col = "v_final_kmh" if "v_final_kmh" in df.columns else "v_fisica_grua"
        vmax = float(df[col].max()) if col in df.columns else 0.0
        tmax = df[col].idxmax() if col in df.columns else df.index[0]
        nmax = int(df["nivel_alerta"].max())
        lineas = [
            f"SPATI · {sitio}",
            f"Nivel máximo 72 h: {NIVEL_NOMBRE.get(nmax, nmax)} ({nmax})",
            f"Ráfaga / viento máx.: {vmax:.1f} km/h @ {tmax}",
        ]
        crit = df[df["nivel_alerta"] >= 2]
        if not crit.empty:
            t0 = crit.index[0]
            lineas.append(f"Primer evento Naranja/Rojo: {t0}")
        if ventanas:
            lineas.append("Ventanas seguras (≥2 h VERDE):")
            for v in ventanas[:6]:
                lineas.append(
                    f"  · {v['inicio']} → {v['fin']} ({v['duracion_horas']} h)"
                )
        else:
            lineas.append("Sin ventanas seguras ≥ 2 h en el horizonte.")
        return "\n".join(lineas)

    @staticmethod
    def alert_to_dict(r: AlertResult) -> dict[str, Any]:
        return asdict(r)
