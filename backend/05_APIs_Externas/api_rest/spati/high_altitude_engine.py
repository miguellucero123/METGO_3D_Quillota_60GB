#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SPATI — HighAltitudeEngine: correcciones ISA / barométricas / flags cordillera.

Usar cuando altitud_msnm > 1500. La densidad ρ cae ~37% a 4400 m; la fuerza F
cae en la misma proporción. El umbral operativo de alerta (36 km/h) NO se reduce:
el control es por fuerza aerodinámica + flags secundarios.
"""

from __future__ import annotations

import math
from typing import Any

import pandas as pd

# ISA / gas ideal
P0_PA = 101325.0
T0_K = 288.15
L_K_PER_M = 0.0065
G_M = 9.80665
M_AIR = 0.0289644
R_UNIV = 8.314462618
R_D = 287.05  # J/(kg·K)
RHO_ISA_SL = 1.225  # kg/m³
# Exponente barométrico ISA: g·M / (R·L) ≈ 5.25588
_ISA_EXP = (G_M * M_AIR) / (R_UNIV * L_K_PER_M)

# Factor de ráfaga (tipo_eolico, zona_climatica) → GF
GUST_FACTOR_ALTA: dict[tuple[str, str], float] = {
    ("rajo_norte_grande", "altiplano"): 1.75,
    ("rajo_norte_grande", "precordillera"): 1.65,
    ("terreno_abierto", "altiplano"): 1.40,
    ("quebrada_cordillera", "andes_central"): 1.85,
    ("quebrada_cordillera", "andes_sur"): 1.90,
    ("quebrada_cordillera", "altiplano"): 1.85,
    ("rajo", "andes_central"): 1.80,
    ("superficie_plana", "altiplano"): 1.35,
    ("superficie_plana", "costero"): 1.30,
    ("rajo_minero", "altiplano"): 1.75,
    ("rajo_minero", "precordillera"): 1.65,
    ("valle_cordillera", "andes_central"): 1.85,
    ("valle_cordillera", "andes_sur"): 1.90,
    ("valle_cordillera", "precordillera"): 1.70,
}

SITIOS_ZONDA = frozenset({"los_bronces", "andina", "los_pelambres"})
SITIOS_NIEVE = frozenset({"los_bronces", "andina", "el_teniente", "los_pelambres"})
SITIOS_POLVO = frozenset(
    {
        "quebrada_blanca",
        "collahuasi",
        "el_abra",
        "escondida",
        "maricunga",
        "cerro_colorado",
        "spence",
        "radomiro_tomic",
    }
)
SITIOS_RAYOS_ANDINOS = frozenset(
    {"los_bronces", "andina", "el_teniente", "los_pelambres"}
)


class HighAltitudeEngine:
    """Correcciones físicas y flags para faenas ≥ 1500 msnm."""

    def calcular_presion_barometrica(self, altitud_m: float) -> float:
        """p(h) = p₀ · (1 − L·h/T₀)^5.2561  [Pa]. ISA / ICAO Doc 7488."""
        if altitud_m < -500 or altitud_m > 6000:
            raise ValueError(f"altitud fuera de rango operacional Chile: {altitud_m}")
        ratio = 1.0 - (L_K_PER_M * float(altitud_m)) / T0_K
        if ratio <= 0:
            raise ValueError(f"altitud inválida para ISA: {altitud_m}")
        return float(P0_PA * (ratio**_ISA_EXP))

    def temperatura_isa_celsius(self, altitud_m: float) -> float:
        return float(15.0 - L_K_PER_M * 1000.0 * (float(altitud_m) / 1000.0))

    def calcular_densidad_altitud(self, altitud_m: float, temp_celsius: float) -> float:
        """ρ(h,T) = p(h) / (R_d · T_K). Usa T real del sitio (no ISA)."""
        if temp_celsius < -60 or temp_celsius > 60:
            raise ValueError(f"temperatura fuera de rango: {temp_celsius}")
        p = self.calcular_presion_barometrica(altitud_m)
        return float(p / (R_D * (temp_celsius + 273.15)))

    def densidad_isa(self, altitud_m: float) -> float:
        """ρ ISA a altitud (referencia fija del sitio)."""
        t_isa = self.temperatura_isa_celsius(altitud_m)
        return self.calcular_densidad_altitud(altitud_m, t_isa)

    def factor_reduccion_densidad(self, rho_real: float) -> float:
        """FR = ρ_real / 1.225."""
        if rho_real <= 0:
            raise ValueError("rho_real debe ser > 0")
        return float(rho_real / RHO_ISA_SL)

    def umbral_velocidad_equivalente(self, v_umbral_nmm: float, rho_real: float) -> float:
        """Velocidad en faena que genera la misma F que v_umbral a nivel del mar.

        Informativo para el operador. NO reemplaza el umbral de alerta (36 km/h).
        """
        if rho_real <= 0:
            raise ValueError("rho_real inválido")
        return float(v_umbral_nmm * math.sqrt(RHO_ISA_SL / rho_real))

    def velocidad_eas(self, v_real_kmh: float, rho_real: float) -> float:
        """Equivalent Airspeed: v_EAS = v_real · √FR."""
        fr = self.factor_reduccion_densidad(rho_real)
        return float(v_real_kmh * math.sqrt(fr))

    def factor_rafaga_terreno(
        self,
        tipo_terreno_eolico: str,
        zona_climatica: str,
        default: float = 1.65,
    ) -> float:
        key = (str(tipo_terreno_eolico), str(zona_climatica))
        if key in GUST_FACTOR_ALTA:
            return float(GUST_FACTOR_ALTA[key])
        for (_t, z), gf in GUST_FACTOR_ALTA.items():
            if z == zona_climatica:
                return float(gf)
        return float(default)

    def ajuste_cd_nieve(self, cd_base: float, flag_nieve: bool) -> float:
        """Acumulación hielo/nieve: +20% C_d (conservador)."""
        return float(cd_base * 1.20) if flag_nieve else float(cd_base)

    def umbral_dron_altitud(self, v_max_fabricante_ms: float, rho_real: float) -> float:
        """Límite de viento del dron corregido por densidad (−15% margen)."""
        v = float(v_max_fabricante_ms) * math.sqrt(RHO_ISA_SL / float(rho_real))
        return float(v * 0.85)

    def parametros_sitio(self, altitud_m: float) -> dict[str, float]:
        """Lookup ISA fijo del sitio (para catálogo / Supabase)."""
        p = self.calcular_presion_barometrica(altitud_m)
        t_isa = self.temperatura_isa_celsius(altitud_m)
        rho = p / (R_D * (t_isa + 273.15))
        fr = rho / RHO_ISA_SL
        v_eq = self.umbral_velocidad_equivalente(36.0, rho)
        return {
            "presion_barometrica_pa": round(p, 1),
            "temp_isa_celsius": round(t_isa, 2),
            "rho_isa_kg_m3": round(rho, 4),
            "factor_reduccion": round(fr, 4),
            "v_equiv_36_kmh": round(v_eq, 1),
        }

    def evaluar_flags_alta_montana(
        self,
        row: dict[str, Any] | pd.Series,
        sitio_config: dict[str, Any],
        *,
        delta_temp_3h: float | None = None,
        delta_rh_3h: float | None = None,
    ) -> dict[str, bool]:
        """Flags secundarios por intervalo (Zonda, nieve, polvo, rayos, onda)."""
        sitio_id = str(sitio_config.get("sitio_id") or sitio_config.get("slug") or "")
        zona = str(sitio_config.get("zona_climatica") or "")
        alt = float(sitio_config.get("altitud_msnm") or 0)

        def _g(key: str, default=None):
            if isinstance(row, dict):
                return row.get(key, default)
            return row.get(key, default) if hasattr(row, "get") else default

        dir_v = _g("dir_modelo")
        temp = _g("temp_celsius")
        rh = _g("rh_pct")
        precip = _g("precip_mmh") or 0.0
        snowfall = _g("snowfall_mm") or 0.0
        vis_m = _g("visibilidad_m")
        vis_km = (float(vis_m) / 1000.0) if vis_m is not None and pd.notna(vis_m) else None
        v10 = _g("viento_modelo_10m") or _g("v_final_kmh") or 0.0
        prob_rayos = _g("prob_rayos_pct")
        w500 = _g("viento_500hpa_kt")
        d500 = _g("dir_500hpa")

        flag_zonda = False
        if sitio_id in SITIOS_ZONDA and dir_v is not None and pd.notna(dir_v):
            d = float(dir_v)
            if 80.0 <= d <= 120.0 and delta_temp_3h is not None and delta_rh_3h is not None:
                if delta_temp_3h > 5.0 and delta_rh_3h < -30.0:
                    flag_zonda = True

        flag_nieve = False
        if sitio_id in SITIOS_NIEVE or zona in ("andes_central", "andes_sur"):
            t_ok = temp is not None and pd.notna(temp) and float(temp) < 2.0
            p_ok = float(precip) > 0.5 or float(snowfall) > 0.1
            flag_nieve = bool(t_ok and p_ok)

        flag_polvo = False
        if sitio_id in SITIOS_POLVO or zona in ("altiplano", "precordillera"):
            if vis_km is not None and rh is not None and pd.notna(rh):
                if vis_km < 3.0 and float(rh) < 15.0:
                    flag_polvo = True
            elif v10 is not None and rh is not None and pd.notna(rh):
                if float(v10) > 20.0 and float(rh) < 15.0:
                    flag_polvo = True

        flag_rayos = False
        umbral_rayos = 20.0 if sitio_id in SITIOS_RAYOS_ANDINOS else 30.0
        if prob_rayos is not None and pd.notna(prob_rayos):
            flag_rayos = float(prob_rayos) > umbral_rayos

        flag_onda = False
        if alt >= 2500 and w500 is not None and pd.notna(w500):
            if float(w500) > 25.0:
                if d500 is None or (pd.notna(d500) and 80.0 <= float(d500) <= 130.0):
                    flag_onda = True

        return {
            "flag_zonda": flag_zonda,
            "flag_nieve_vuelo": flag_nieve,
            "flag_polvo_visibilidad": flag_polvo,
            "flag_rayos_andinos": flag_rayos,
            "flag_onda_montana": flag_onda,
            "flag_requiere_dgac": bool(
                sitio_config.get("requiere_autorizacion_dgac", alt > 1740)
            ),
        }

    def aplicar_correcciones_serie(
        self,
        df: pd.DataFrame,
        sitio_config: dict[str, Any],
        *,
        cd_base: float,
    ) -> pd.DataFrame:
        """Sobrescribe ρ con barométrica+T real; agrega FR, EAS, flags, Cd ajustado."""
        out = df.copy()
        alt = float(sitio_config.get("altitud_msnm") or 0)
        tipo_e = str(
            sitio_config.get("tipo_terreno_eolico")
            or sitio_config.get("tipo_terreno")
            or "rajo_minero"
        )
        zona = str(sitio_config.get("zona_climatica") or "altiplano")
        gf = self.factor_rafaga_terreno(tipo_e, zona)

        if "temp_celsius" in out.columns:
            dtemp = out["temp_celsius"] - out["temp_celsius"].shift(12)
        else:
            dtemp = pd.Series([None] * len(out), index=out.index)
        if "rh_pct" in out.columns:
            drh = out["rh_pct"] - out["rh_pct"].shift(12)
        else:
            drh = pd.Series([None] * len(out), index=out.index)

        rhos, frs, eas, cds = [], [], [], []
        fz, fn, fp, fray, fo, fdgac = [], [], [], [], [], []

        for i, (_ts, row) in enumerate(out.iterrows()):
            t = row.get("temp_celsius")
            p_nwp = row.get("presion_pa")
            try:
                if t is None or (isinstance(t, float) and math.isnan(t)):
                    raise ValueError("sin T")
                if p_nwp is not None and pd.notna(p_nwp) and 45000 <= float(p_nwp) <= 106000:
                    rho = float(p_nwp) / (R_D * (float(t) + 273.15))
                else:
                    rho = self.calcular_densidad_altitud(alt, float(t))
                fr = self.factor_reduccion_densidad(rho)
            except Exception:
                try:
                    rho = self.densidad_isa(alt) if alt > 0 else RHO_ISA_SL
                    fr = self.factor_reduccion_densidad(rho)
                except Exception:
                    rho, fr = None, None

            dt3 = float(dtemp.iloc[i]) if pd.notna(dtemp.iloc[i]) else None
            drh3 = float(drh.iloc[i]) if pd.notna(drh.iloc[i]) else None
            flags = self.evaluar_flags_alta_montana(
                row, sitio_config, delta_temp_3h=dt3, delta_rh_3h=drh3
            )
            cd = self.ajuste_cd_nieve(cd_base, flags["flag_nieve_vuelo"])

            v_ref = row.get("v_final_kmh") or row.get("v_fisica_grua") or row.get(
                "viento_modelo_10m"
            )
            eas_v = None
            if rho is not None and v_ref is not None and pd.notna(v_ref):
                try:
                    eas_v = round(self.velocidad_eas(float(v_ref), rho), 1)
                except Exception:
                    eas_v = None

            rhos.append(round(rho, 4) if rho is not None else None)
            frs.append(round(fr, 4) if fr is not None else None)
            eas.append(eas_v)
            cds.append(round(cd, 3))
            fz.append(flags["flag_zonda"])
            fn.append(flags["flag_nieve_vuelo"])
            fp.append(flags["flag_polvo_visibilidad"])
            fray.append(flags["flag_rayos_andinos"])
            fo.append(flags["flag_onda_montana"])
            fdgac.append(flags["flag_requiere_dgac"])

        out["rho"] = rhos
        out["factor_reduccion"] = frs
        out["v_eas_kmh"] = eas
        out["coef_forma_cd_efectivo"] = cds
        out["gust_factor_sitio"] = gf
        out["flag_zonda"] = fz
        out["flag_nieve_vuelo"] = fn
        out["flag_polvo_visibilidad"] = fp
        out["flag_rayos_andinos"] = fray
        out["flag_onda_montana"] = fo
        out["flag_requiere_dgac"] = fdgac
        return out

    def elevar_nivel_por_flags(
        self, flags: dict[str, bool], nivel: int
    ) -> tuple[int, list[str]]:
        """Zonda / nieve / onda / rayos → mín. Nivel 2; polvo → 1."""
        razones: list[str] = []
        n = int(nivel)
        if flags.get("flag_zonda"):
            n = max(n, 2)
            razones.append("ZONDA")
        if flags.get("flag_nieve_vuelo"):
            n = max(n, 2)
            razones.append("NIEVE_EN_VUELO")
        if flags.get("flag_onda_montana"):
            n = max(n, 2)
            razones.append("ONDA_DE_MONTAÑA")
        if flags.get("flag_rayos_andinos"):
            n = max(n, 2)
            razones.append("RAYOS_ANDINOS")
        if flags.get("flag_polvo_visibilidad"):
            n = max(n, 1)
            razones.append("POLVO_VISIBILIDAD")
        return n, razones
