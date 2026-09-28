#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests: alerta de helada por predio (funciones puras, sin red)."""

from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone

os.environ.setdefault("METGO_JWT_SECRET", "test-secret-heladas-predio-min-32-bytes!!")

import pytest

from api_rest import heladas_predio_service as hp

MODELOS = ["ecmwf_ifs025", "icon_seamless", "gfs_seamless"]


def _hourly(tmin_noche: float, *, desfase_modelos=(0.0, 0.5, -0.5), nubes=5.0, viento=1.0):
    """48 h horarias UTC desde el 28-sep 12:00 local; mínimo a las 06:00 locales del 29."""
    inicio_local = datetime(2026, 9, 28, 12, tzinfo=hp.TZ)
    times, temp = [], []
    for h in range(48):
        t_local = inicio_local + timedelta(hours=h)
        times.append(t_local.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M"))
        if t_local.day == 29 and t_local.hour == 6:
            temp.append(tmin_noche)
        elif 18 <= t_local.hour or t_local.hour < 9:
            temp.append(tmin_noche + 4.0)
        else:
            temp.append(20.0)
    hourly = {"time": times}
    for m, d in zip(MODELOS, desfase_modelos):
        hourly[f"temperature_2m_{m}"] = [x + d for x in temp]
        hourly[f"dew_point_2m_{m}"] = [x - 6 for x in temp]
        hourly[f"relative_humidity_2m_{m}"] = [55.0] * 48
        hourly[f"cloud_cover_{m}"] = [nubes] * 48
        hourly[f"wind_speed_10m_{m}"] = [viento] * 48
    return hourly


AHORA = datetime(2026, 9, 28, 17, 0, tzinfo=hp.TZ)
PREDIO = {"id": "p1", "nombre": "Cerezos test", "cultivo": "cerezo", "altitud_m": 600}


def test_ventana_noche_tarde_y_madrugada():
    ini, fin = hp.ventana_noche(AHORA)
    assert ini.hour == 18 and ini.day == 28 and fin.hour == 9 and fin.day == 29
    ini2, _ = hp.ventana_noche(datetime(2026, 9, 29, 3, 0, tzinfo=hp.TZ))
    assert ini2.day == 28  # a las 03:00 sigue siendo la noche en curso


def test_noche_fria_da_rojo_con_hora_real():
    r = hp.evaluar_noche(PREDIO, _hourly(-3.0), AHORA, MODELOS)
    assert r["tmin_c"] == -3.0
    assert r["hora_min"] == "06:00"
    assert r["nivel"] == "rojo"
    assert r["prob_helada_pct"] > 90
    assert r["n_modelos"] == 3
    assert r["tmin_por_modelo_c"]["gfs_seamless"] == -3.5


def test_noche_templada_da_verde():
    r = hp.evaluar_noche(PREDIO, _hourly(8.0, nubes=90, viento=5), AHORA, MODELOS)
    assert r["nivel"] == "verde"
    assert r["prob_helada_pct"] < 1


def test_ajuste_local_enfria_el_predio():
    base = hp.evaluar_noche(PREDIO, _hourly(1.0), AHORA, MODELOS)
    ajustado = hp.evaluar_noche({**PREDIO, "ajuste_tmin_c": -2.0}, _hourly(1.0), AHORA, MODELOS)
    assert ajustado["tmin_c"] == base["tmin_c"] - 2.0
    assert ajustado["prob_accion_pct"] > base["prob_accion_pct"]


def test_umbral_accion_por_defecto_y_override():
    assert hp.umbral_accion_predio({"cultivo": "cerezo"}) == -1.0
    assert hp.umbral_accion_predio({"cultivo": "palto", "umbral_accion_c": 1.5}) == 1.5


def test_sin_datos_no_inventa():
    with pytest.raises(hp.PronosticoNoDisponibleError):
        hp.evaluar_noche(PREDIO, {"time": []}, AHORA, MODELOS)


def test_mensaje_y_link_whatsapp():
    r = hp.evaluar_noche(PREDIO, _hourly(-3.0), AHORA, MODELOS)
    txt = hp.mensaje_whatsapp(r)
    assert "PRENDE CONTROL" in txt and "-3,0 °C" in txt and "no una garantía" in txt
    link = hp.link_whatsapp("+56 9 1234 5678", txt)
    assert link.startswith("https://wa.me/56912345678?text=")
    assert hp.link_whatsapp("", txt) is None


def test_escalamiento_nocturno():
    verde = {"nivel": "verde", "tmin_c": 4.0}
    amarillo = {"nivel": "amarillo", "tmin_c": 0.5}
    assert hp.debe_escalar(verde, amarillo)
    assert not hp.debe_escalar(amarillo, {"nivel": "amarillo", "tmin_c": 0.0})
    assert hp.debe_escalar(amarillo, {"nivel": "amarillo", "tmin_c": -1.2})
    assert not hp.debe_escalar(None, {"nivel": "verde", "tmin_c": 5.0})


def test_validacion_sugiere_ajuste():
    v = hp.validar_contra_observado([(2.0, 0.5), (1.0, -0.5), (3.0, 1.5)])
    assert v["sesgo_c"] == -1.5 and v["ajuste_sugerido_c"] == -1.5 and v["aplicar"]
    assert not hp.validar_contra_observado([(2.0, 1.0)])["aplicar"]
