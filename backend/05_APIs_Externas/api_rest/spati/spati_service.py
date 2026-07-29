#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SPATI — orquestador de pronóstico de izaje 72 h × 15 min + alta montaña."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

import pandas as pd

from api_rest.spati.alert_system import CraneSafetyAlertSystem
from api_rest.spati.drone_assimilator import DroneAssimilator, DroneProfileError
from api_rest.spati.high_altitude_engine import HighAltitudeEngine
from api_rest.spati.mos_corrector import MOSCorrector
from api_rest.spati.nwp_ingestor import NWPDataUnavailableError, NWPIngestor
from api_rest.spati.physics_engine import (
    ALTURAS_PERFIL_IZAJES_M,
    GruaConfig,
    PhysicsEngine,
)
from api_rest.spati.sitios_catalogo import get_sitio, listar_sitios

logger = logging.getLogger(__name__)

__all__ = ["run_spati", "listar_sitios", "get_sitio"]


def run_spati(
    sitio_id: str = "escondida",
    perfil_dron: dict[str, Any] | None = None,
    tau_dron_h: float = 6.0,
) -> dict[str, Any]:
    """Pipeline SPATI: NWP → física → alta montaña → MOS → dron → alertas."""
    raw = get_sitio(sitio_id)
    if not raw:
        return {"error": "sitio_no_encontrado", "sitio_id": sitio_id}

    from api_rest.spati.umbrales_service import umbrales_efectivos, umbrales_internos

    cfg = GruaConfig.from_dict(raw)
    pe = PhysicsEngine()
    ha = HighAltitudeEngine()
    nwp = NWPIngestor()
    mos = MOSCorrector()
    umb_int = umbrales_internos(cfg.sitio_id)
    alerts = CraneSafetyAlertSystem.from_umbrales(umb_int)
    drone = DroneAssimilator()

    alta = float(cfg.altitud_msnm or 0) > 1500
    if raw.get("requiere_autorizacion_dgac"):
        logger.info("SPATI %s: requiere autorización DGAC para vuelo de dron", cfg.sitio_id)

    nwp_fuente = "openmeteo"
    nwp_aviso = None
    try:
        df = nwp.fetch_forecast(
            cfg.lat, cfg.lon, forecast_days=3, alt_msnm=raw.get("altitud_msnm")
        )
        nwp_fuente = getattr(df, "attrs", {}).get("nwp_fuente") or "openmeteo"
        nwp_aviso = getattr(df, "attrs", {}).get("nwp_aviso")
    except NWPDataUnavailableError as exc:
        logger.warning("SPATI NWP error: %s", exc)
        return {
            "error": "nwp_no_disponible",
            "detalle": str(exc),
            "sitio_id": cfg.sitio_id,
            "sugerencia": "Open-Meteo saturado o lento; reintente en 1–2 minutos",
        }

    df = pe.extrapolar_serie(df, cfg)

    # Factor de ráfaga específico por zona climática / terreno eólico
    tipo_gf = str(raw.get("tipo_terreno_eolico") or cfg.tipo_terreno)
    zona = str(raw.get("zona_climatica") or "altiplano")
    if alta:
        gf = ha.factor_rafaga_terreno(tipo_gf, zona)
    else:
        from api_rest.spati.physics_engine import GUST_FACTOR_TERRENO

        gf = float(GUST_FACTOR_TERRENO.get(cfg.tipo_terreno, 1.50))

    if "rafaga_modelo_10m" in df.columns:
        mask = df["rafaga_modelo_10m"].isna() & df["viento_modelo_10m"].notna()
        if mask.any():
            df.loc[mask, "rafaga_modelo_10m"] = df.loc[mask, "viento_modelo_10m"] * gf

    mos.cargar_o_entrenar(None, cfg.sitio_id)
    df["v_mos_kmh"] = mos.predecir(df)
    df["modo_sin_mos"] = mos.modo_sin_mos

    sesgo = None
    if perfil_dron:
        try:
            v0 = float(df["v_fisica_grua"].iloc[0] or 0)
            sesgo = drone.calcular_sesgo(perfil_dron, v0, cfg.altura_pluma_m)
            t_vuelo = datetime.fromisoformat(
                str(
                    perfil_dron.get("timestamp_vuelo")
                    or datetime.now(timezone.utc).isoformat()
                ).replace("Z", "+00:00")
            )
            if t_vuelo.tzinfo is None:
                t_vuelo = t_vuelo.replace(tzinfo=timezone.utc)
            df["horas_desde_vuelo"] = [
                max(0.0, (ts.to_pydatetime() - t_vuelo).total_seconds() / 3600.0)
                for ts in df.index
            ]
            df = drone.aplicar_correccion(df, sesgo, tau_horas=tau_dron_h)
            df["v_final_kmh"] = df["v_dron_corr_kmh"]
        except (DroneProfileError, Exception) as exc:
            logger.warning("SPATI dron omitido: %s", exc)
            df["v_final_kmh"] = df["v_mos_kmh"]
            sesgo = None
    else:
        df["v_final_kmh"] = df["v_mos_kmh"]

    if "rafaga_modelo_10m" in df.columns:
        try:
            raf_pluma = df["rafaga_modelo_10m"].apply(
                lambda v: pe.extrapolar_altura(
                    float(v), cfg.altura_pluma_m, cfg.z0_terreno, cfg.h_ref_m
                )
                if v is not None and pd.notna(v)
                else None
            )
            df["v_final_kmh"] = df[["v_final_kmh"]].join(raf_pluma.rename("raf_pluma")).max(axis=1)
        except Exception:
            pass

    # Correcciones de densidad / flags alta montaña (siempre; útil también <1500 m)
    df = ha.aplicar_correcciones_serie(df, raw, cd_base=cfg.coef_forma_cd)

    fuerzas, pcts = [], []
    for _, row in df.iterrows():
        rho = row.get("rho")
        vf = row.get("v_final_kmh")
        cd = row.get("coef_forma_cd_efectivo") or cfg.coef_forma_cd
        try:
            if rho is None or vf is None:
                raise ValueError("na")
            f = pe.calcular_fuerza(float(vf), float(rho), cfg.area_carga_m2, float(cd))
            pct = pe.porcentaje_del_limite(f, cfg.fuerza_limite_n)
        except Exception:
            f, pct = None, None
        fuerzas.append(round(f, 1) if f is not None else None)
        pcts.append(round(pct, 1) if pct is not None else None)
    df["fuerza_n"] = fuerzas
    df["pct_limite_diseno"] = pcts

    # Recalcular EAS con v_final definitivo
    eas = []
    for _, row in df.iterrows():
        rho = row.get("rho")
        vf = row.get("v_final_kmh")
        try:
            if rho is None or vf is None:
                eas.append(None)
            else:
                eas.append(round(ha.velocidad_eas(float(vf), float(rho)), 1))
        except Exception:
            eas.append(None)
    df["v_eas_kmh"] = eas

    df = alerts.clasificar_serie(df)
    # Elevar nivel por flags de alta montaña
    if alta or any(
        df.get(c, pd.Series(dtype=bool)).any()
        for c in (
            "flag_zonda",
            "flag_nieve_vuelo",
            "flag_polvo_visibilidad",
            "flag_rayos_andinos",
            "flag_onda_montana",
        )
        if c in df.columns
    ):
        niveles, razones = [], []
        for _, row in df.iterrows():
            flags = {
                "flag_zonda": bool(row.get("flag_zonda")),
                "flag_nieve_vuelo": bool(row.get("flag_nieve_vuelo")),
                "flag_polvo_visibilidad": bool(row.get("flag_polvo_visibilidad")),
                "flag_rayos_andinos": bool(row.get("flag_rayos_andinos")),
                "flag_onda_montana": bool(row.get("flag_onda_montana")),
            }
            n, extra = ha.elevar_nivel_por_flags(flags, int(row.get("nivel_alerta") or 0))
            niveles.append(n)
            raz = str(row.get("razon_alerta") or "")
            if extra:
                raz = (raz + "; " if raz else "") + ", ".join(extra)
            razones.append(raz)
        df["nivel_alerta"] = niveles
        from api_rest.spati.alert_system import NIVEL_NOMBRE

        df["nivel_nombre"] = [NIVEL_NOMBRE.get(n, str(n)) for n in niveles]
        df["razon_alerta"] = razones
        df["flag_meteo"] = df["flag_meteo"] | df["flag_zonda"] | df["flag_nieve_vuelo"] | df[
            "flag_onda_montana"
        ]

    ventanas = alerts.detectar_ventanas_seguras(df, min_horas=2.0, solo_verde=True)
    ventanas_rest = alerts.detectar_ventanas_seguras(df, min_horas=2.0, solo_verde=False)
    resumen = alerts.generar_resumen_ejecutivo(df, ventanas, cfg.nombre or cfg.sitio_id)

    rho_isa = raw.get("rho_isa_kg_m3")
    fr_isa = raw.get("factor_reduccion")
    v_eq36 = raw.get("v_equiv_36_kmh")
    try:
        rho_ref = float(rho_isa) if rho_isa else ha.densidad_isa(cfg.altitud_msnm)
        umbral_dron_ms = ha.umbral_dron_altitud(12.0, rho_ref)
    except Exception:
        umbral_dron_ms = None

    serie = []
    for ts, row in df.iterrows():
        v10 = row.get("viento_modelo_10m")
        perfil = None
        ciz_10_100 = None
        ciz_10_pluma = None
        turb = None
        try:
            if v10 is not None and pd.notna(v10):
                perfil = pe.perfil_vertical_izaje(
                    float(v10),
                    cfg.z0_terreno,
                    alturas_m=ALTURAS_PERFIL_IZAJES_M,
                    v_80m_kmh=_opt_float(row.get("viento_modelo_80m")),
                    v_100m_kmh=_opt_float(row.get("viento_modelo_100m")),
                    rho=_opt_float(row.get("rho")),
                    area_m2=cfg.area_carga_m2,
                    cd=float(row.get("coef_forma_cd_efectivo") or cfg.coef_forma_cd),
                )
                by_h = {p["altura_m"]: p["v_kmh"] for p in perfil}
                if 10 in by_h and 100 in by_h:
                    ciz_10_100 = pe.cizalladura_vertical(by_h[10], by_h[100], 10, 100)
                v_pluma = _opt_float(row.get("v_fisica_grua"))
                if v_pluma is not None and 10 in by_h:
                    ciz_10_pluma = pe.cizalladura_vertical(
                        by_h[10], v_pluma, 10, cfg.altura_pluma_m
                    )
                raf = _opt_float(row.get("rafaga_modelo_10m")) or _opt_float(
                    row.get("v_final_kmh")
                )
                if raf is not None:
                    turb = pe.indice_turbulencia(float(v10), raf)
        except Exception as exc:
            logger.debug("perfil vertical omitido: %s", exc)

        nivel = int(row.get("nivel_alerta") or 0)
        serie.append(
            {
                "valid_time": ts.isoformat() if hasattr(ts, "isoformat") else str(ts),
                "v_modelo_10m": _round(row.get("viento_modelo_10m")),
                "v_modelo_80m": _round(row.get("viento_modelo_80m")),
                "v_modelo_100m": _round(row.get("viento_modelo_100m")),
                "v_fisica_grua": _round(row.get("v_fisica_grua")),
                "v_mos_kmh": _round(row.get("v_mos_kmh")),
                "v_final_kmh": _round(row.get("v_final_kmh")),
                "v_eas_kmh": _round(row.get("v_eas_kmh")),
                "dir_viento_deg": _round(row.get("dir_modelo")),
                "dir_100m_deg": _round(row.get("dir_100m")),
                "rafaga_modelo": _round(row.get("rafaga_modelo_10m")),
                "temp_celsius": _round(row.get("temp_celsius")),
                "presion_pa": _round(row.get("presion_pa"), 1),
                "rh_pct": _round(row.get("rh_pct"), 1),
                "visibilidad_m": _round(row.get("visibilidad_m"), 0),
                "visibilidad_km": _round(
                    (float(row["visibilidad_m"]) / 1000.0)
                    if row.get("visibilidad_m") is not None
                    and pd.notna(row.get("visibilidad_m"))
                    else None,
                    2,
                ),
                "rho": _round(row.get("rho"), 4),
                "factor_reduccion": _round(row.get("factor_reduccion"), 4),
                "fuerza_n": row.get("fuerza_n"),
                "pct_fuerza": row.get("pct_limite_diseno"),
                "precip_mmh": _round(row.get("precip_mmh"), 2),
                "snowfall_mm": _round(row.get("snowfall_mm"), 2),
                "perfil_vertical": perfil,
                "cizalladura_10_100": ciz_10_100,
                "cizalladura_10_pluma": ciz_10_pluma,
                "indice_turbulencia": turb,
                "condicion_izaje": _condicion_izaje(nivel),
                "nivel_alerta": nivel,
                "nivel_nombre": row.get("nivel_nombre"),
                "flag_critico": bool(row.get("flag_critico")),
                "flag_meteo": bool(row.get("flag_meteo")),
                "flag_zonda": bool(row.get("flag_zonda")),
                "flag_nieve_vuelo": bool(row.get("flag_nieve_vuelo")),
                "flag_polvo_visibilidad": bool(row.get("flag_polvo_visibilidad")),
                "flag_onda_montana": bool(row.get("flag_onda_montana")),
                "razon_alerta": row.get("razon_alerta"),
            }
        )

    # Snapshots técnicos: ahora + instante de viento máximo en pluma
    perfil_ahora = serie[0] if serie else None
    idx_pico = 0
    if serie:
        vmax = -1.0
        for i, s in enumerate(serie):
            vf = s.get("v_final_kmh")
            if vf is not None and float(vf) > vmax:
                vmax = float(vf)
                idx_pico = i
    perfil_pico = serie[idx_pico] if serie else None

    variables_zona = _variables_zona_izaje(
        perfil_ahora, cfg, raw, gf, umbral_dron_ms, fr_isa, v_eq36
    )

    nmax = int(df["nivel_alerta"].max()) if len(df) else 0
    return {
        "sitio": raw,
        "config": {
            "altura_pluma_m": cfg.altura_pluma_m,
            "z0_terreno": cfg.z0_terreno,
            "tipo_terreno": cfg.tipo_terreno,
            "tipo_terreno_eolico": raw.get("tipo_terreno_eolico"),
            "zona_climatica": raw.get("zona_climatica"),
            "riesgo_eolico": raw.get("riesgo_eolico"),
            "gust_factor": gf,
            "area_carga_m2": cfg.area_carga_m2,
            "coef_forma_cd": cfg.coef_forma_cd,
            "fuerza_limite_n": cfg.fuerza_limite_n,
            "altitud_msnm": raw.get("altitud_msnm"),
            "region": raw.get("region"),
            "operador": raw.get("operador"),
            "alta_montana": alta,
            "requiere_autorizacion_dgac": bool(raw.get("requiere_autorizacion_dgac")),
            "presion_barometrica_pa": raw.get("presion_barometrica_pa"),
            "rho_isa_kg_m3": rho_isa,
            "factor_reduccion": fr_isa,
            "v_equiv_36_kmh": v_eq36,
            "umbral_dron_ms": round(umbral_dron_ms, 2) if umbral_dron_ms else None,
            "alturas_perfil_m": list(ALTURAS_PERFIL_IZAJES_M),
        },
        "run_timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "nwp_fuente": nwp_fuente,
        "nwp_aviso": nwp_aviso,
        "horizonte_h": 72,
        "dt_min": 15,
        "n_intervalos": len(serie),
        "modo_sin_mos": mos.modo_sin_mos,
        "mos_metricas": mos.metricas or None,
        "sesgo_dron_kmh": sesgo,
        "nivel_maximo": nmax,
        "nivel_maximo_nombre": {0: "VERDE", 1: "AMARILLO", 2: "NARANJA", 3: "ROJO"}.get(nmax),
        "ventanas_seguras": ventanas,
        "ventanas_restringidas": ventanas_rest,
        "resumen_ejecutivo": resumen,
        "variables_zona_izaje": variables_zona,
        "perfil_vertical_ahora": {
            "valid_time": (perfil_ahora or {}).get("valid_time"),
            "niveles": (perfil_ahora or {}).get("perfil_vertical"),
            "cizalladura_10_100": (perfil_ahora or {}).get("cizalladura_10_100"),
            "cizalladura_10_pluma": (perfil_ahora or {}).get("cizalladura_10_pluma"),
        },
        "perfil_vertical_pico": {
            "valid_time": (perfil_pico or {}).get("valid_time"),
            "v_final_kmh": (perfil_pico or {}).get("v_final_kmh"),
            "niveles": (perfil_pico or {}).get("perfil_vertical"),
            "cizalladura_10_100": (perfil_pico or {}).get("cizalladura_10_100"),
            "cizalladura_10_pluma": (perfil_pico or {}).get("cizalladura_10_pluma"),
        },
        "serie": serie,
        "umbrales": {
            **umbrales_efectivos(cfg.sitio_id),
            "v_equiv_nivel_mar_36_kmh": v_eq36,
        },
    }


def _opt_float(v: Any) -> float | None:
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return None
    try:
        return float(v)
    except Exception:
        return None


def _condicion_izaje(nivel: int) -> str:
    if nivel >= 3:
        return "suspendido"
    if nivel == 2:
        return "restringido"
    if nivel == 1:
        return "precaucion"
    return "apto"


def _variables_zona_izaje(
    actual: dict[str, Any] | None,
    cfg: GruaConfig,
    raw: dict[str, Any],
    gust_factor: float,
    umbral_dron_ms: float | None,
    fr_isa: Any,
    v_eq36: Any,
) -> dict[str, Any]:
    """KPIs operativos de la zona de trabajo de izaje (instante actual)."""
    a = actual or {}
    return {
        "valid_time": a.get("valid_time"),
        "altura_pluma_m": cfg.altura_pluma_m,
        "z0_terreno_m": cfg.z0_terreno,
        "gust_factor": gust_factor,
        "altitud_msnm": raw.get("altitud_msnm"),
        "zona_climatica": raw.get("zona_climatica"),
        "riesgo_eolico": raw.get("riesgo_eolico"),
        "v_10m_kmh": a.get("v_modelo_10m"),
        "v_80m_kmh": a.get("v_modelo_80m"),
        "v_100m_kmh": a.get("v_modelo_100m"),
        "v_pluma_kmh": a.get("v_fisica_grua"),
        "v_final_kmh": a.get("v_final_kmh"),
        "v_eas_kmh": a.get("v_eas_kmh"),
        "rafaga_10m_kmh": a.get("rafaga_modelo"),
        "dir_10m_deg": a.get("dir_viento_deg"),
        "dir_100m_deg": a.get("dir_100m_deg"),
        "cizalladura_10_100": a.get("cizalladura_10_100"),
        "cizalladura_10_pluma": a.get("cizalladura_10_pluma"),
        "indice_turbulencia": a.get("indice_turbulencia"),
        "temp_celsius": a.get("temp_celsius"),
        "presion_pa": a.get("presion_pa"),
        "rho_kg_m3": a.get("rho"),
        "factor_reduccion": a.get("factor_reduccion") or fr_isa,
        "fuerza_carga_n": a.get("fuerza_n"),
        "pct_limite_diseno": a.get("pct_fuerza"),
        "area_carga_m2": cfg.area_carga_m2,
        "coef_forma_cd": cfg.coef_forma_cd,
        "fuerza_limite_n": cfg.fuerza_limite_n,
        "rh_pct": a.get("rh_pct"),
        "visibilidad_km": a.get("visibilidad_km"),
        "precip_mmh": a.get("precip_mmh"),
        "snowfall_mm": a.get("snowfall_mm"),
        "condicion_izaje": a.get("condicion_izaje"),
        "nivel_alerta": a.get("nivel_alerta"),
        "v_equiv_36_kmh": v_eq36,
        "umbral_dron_ms": round(umbral_dron_ms, 2) if umbral_dron_ms else None,
        "requiere_autorizacion_dgac": bool(raw.get("requiere_autorizacion_dgac")),
        "alturas_perfil_m": list(ALTURAS_PERFIL_IZAJES_M),
        "notas": [
            "Perfil: anclas NWP 10/80/100 m + logarítmico a 20–70 y 200 m",
            "Control operativo por fuerza aerodinámica y umbral 36 km/h (no se reduce por altitud)",
            "Cizalladura 10–100 m crítica en rajos; validar con dron cuando DGAC lo permita",
        ],
    }


def _round(v: Any, nd: int = 1) -> float | None:
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return None
    try:
        return round(float(v), nd)
    except Exception:
        return None
