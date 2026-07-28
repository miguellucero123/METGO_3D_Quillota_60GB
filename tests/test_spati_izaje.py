#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests SPATI — física, alertas y API smoke."""

from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import metgo_paths


def _setup_api():
    metgo_paths.setup_paths("01_meteo", "05_api_rest")
    apis = metgo_paths.MODULE_PATHS["05_api_rest"]
    if str(apis) not in sys.path:
        sys.path.insert(0, str(apis))


def test_physics_perfil_logaritmico():
    _setup_api()
    from api_rest.spati.physics_engine import PhysicsEngine

    pe = PhysicsEngine()
    v = pe.extrapolar_altura(20.0, 55.0, 0.15, 10.0)
    assert v > 20.0
    assert math.isclose(v, 20.0 * math.log(55 / 0.15) / math.log(10 / 0.15), rel_tol=1e-9)

    try:
        pe.extrapolar_altura(10, 5, 0.15)
        assert False, "debía fallar h < h_ref"
    except ValueError:
        pass


def test_physics_densidad_y_fuerza():
    _setup_api()
    from api_rest.spati.physics_engine import PhysicsEngine

    pe = PhysicsEngine()
    rho = pe.calcular_densidad(15.0, 101325.0)
    assert 1.1 < rho < 1.3
    f = pe.calcular_fuerza(36.0, rho, 12.5, 1.2)
    assert f > 0
    pct = pe.porcentaje_del_limite(f, 25000)
    assert pct > 0


def test_alert_levels():
    _setup_api()
    from api_rest.spati.alert_system import CraneSafetyAlertSystem

    a = CraneSafetyAlertSystem()
    assert a.clasificar_nivel(20).nivel == 0
    assert a.clasificar_nivel(27).nivel == 1
    assert a.clasificar_nivel(32).nivel == 2
    r = a.clasificar_nivel(37)
    assert r.nivel == 3 and r.flag_critico
    r2 = a.clasificar_nivel(20, precip_mmh=3.0)
    assert r2.nivel >= 2 and r2.flag_meteo


def test_drone_sesgo():
    _setup_api()
    from datetime import datetime, timezone

    from api_rest.spati.drone_assimilator import DroneAssimilator

    d = DroneAssimilator()
    perfil = {
        "timestamp_vuelo": datetime.now(timezone.utc).isoformat(),
        "niveles": [
            {"altura_m": 10, "velocidad_kmh": 18},
            {"altura_m": 55, "velocidad_kmh": 30},
            {"altura_m": 100, "velocidad_kmh": 32},
        ],
    }
    e = d.calcular_sesgo(perfil, v_modelo_en_h_pluma=25.0, h_pluma=55.0)
    assert abs(e - 5.0) < 0.01


def test_catalogo_alta_montana():
    _setup_api()
    from api_rest.spati.sitios_catalogo import get_sitio, listar_sitios

    alta = listar_sitios(solo_alta_montana=True)
    assert len(alta) == 17
    assert get_sitio("escondida")["altitud_msnm"] == 3075
    assert get_sitio("quebrada_blanca")["lat"] == -21.0
    assert get_sitio("chuqui")["sitio_id"] == "chuquicamata"
    assert get_sitio("los_bronces")["region"] == "Metropolitana"
    qb = get_sitio("quebrada_blanca")
    assert qb["z0_terreno"] == 0.25
    assert qb["factor_reduccion"] < 0.65
    assert qb["requiere_autorizacion_dgac"] is True
    assert get_sitio("andina")["z0_terreno"] == 0.40
    assert get_sitio("candelaria")["requiere_autorizacion_dgac"] is False


def test_high_altitude_engine():
    _setup_api()
    from api_rest.spati.high_altitude_engine import HighAltitudeEngine

    ha = HighAltitudeEngine()
    p4400 = ha.calcular_presion_barometrica(4400)
    # ISA ≈ 58.5 kPa a 4400 m (tabla HTML ~56.2 kPa es aproximación)
    assert 57500 < p4400 < 59500
    rho = ha.calcular_densidad_altitud(4400, -13.6)
    fr = ha.factor_reduccion_densidad(rho)
    assert 0.60 < fr < 0.68
    params = ha.parametros_sitio(4400)
    assert abs(params["factor_reduccion"] - fr) < 0.02
    v_eq = ha.umbral_velocidad_equivalente(36.0, rho)
    assert v_eq > 36.0  # mismo F → más km/h en altura
    assert ha.factor_rafaga_terreno("quebrada_cordillera", "andes_central") == 1.85
    assert ha.ajuste_cd_nieve(1.2, True) == 1.2 * 1.20
    flags = ha.evaluar_flags_alta_montana(
        {"temp_celsius": -1, "precip_mmh": 1.0, "dir_modelo": 90},
        {"sitio_id": "andina", "zona_climatica": "andes_central", "altitud_msnm": 3950},
        delta_temp_3h=6,
        delta_rh_3h=-35,
    )
    assert flags["flag_nieve_vuelo"]
    assert flags["flag_zonda"]
    n, raz = ha.elevar_nivel_por_flags(flags, 0)
    assert n >= 2 and "ZONDA" in raz

def test_api_spati_sitios_y_physics():
    _setup_api()
    from api_rest.app import create_app

    c = create_app().test_client()
    r = c.get("/api/public/spati/sitios?alta_montana=1")
    assert r.status_code == 200
    sitios = r.get_json()["sitios"]
    assert len(sitios) == 17
    esc = next(s for s in sitios if s["sitio_id"] == "escondida")
    assert esc["z0_terreno"] == 0.25
    assert "factor_reduccion" in esc

    rp = c.post(
        "/api/public/spati/physics/extrapolar",
        json={"v_ref": 20, "h_objetivo": 55, "z0": 0.15},
    )
    assert rp.status_code == 200
    assert rp.get_json()["v_kmh"] > 20

    rha = c.post(
        "/api/public/spati/physics/alta-montana",
        json={"sitio_id": "quebrada_blanca", "temp_celsius": -10},
    )
    assert rha.status_code == 200
    body_ha = rha.get_json()
    assert body_ha["altitud_msnm"] == 4400
    assert body_ha["factor_reduccion"] < 0.65
    assert body_ha["gust_factor"] >= 1.65

    rf = c.get("/api/public/spati/escondida/pronostico")
    assert rf.status_code in (200, 503)
    if rf.status_code == 200:
        body = rf.get_json()
        assert body["n_intervalos"] >= 200
        assert body["sitio"]["nombre"] == "Escondida"
        assert body["config"]["altitud_msnm"] == 3075
        assert body["config"]["alta_montana"] is True
        assert body["config"]["z0_terreno"] == 0.25
        assert body["config"]["factor_reduccion"] is not None
        assert "serie" in body
        assert body["umbrales"]["flag_critico_kmh"] == 36
        assert body["serie"][0].get("factor_reduccion") is not None or body["serie"][0].get("rho") is not None
