#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests: informe de incidentes real (viento sostenido + resonancia pendular)
para VENTORA Izaje Mar, sustituyendo el stub reporte-mensual."""

from __future__ import annotations

import os

os.environ.setdefault("METGO_JWT_SECRET", "test-secret-incidentes-min-32-bytes!!")
os.environ.setdefault("METGO_RATE_LIMIT_ENABLED", "0")

from datetime import datetime, timedelta, timezone

from api_rest.integracion import alertas_store
from api_rest import puerto_alert_job, reporte_incidentes_service as ris


def _ts_relativo(horas: float) -> str:
    return (datetime.now(timezone.utc) + timedelta(hours=horas)).isoformat().replace("+00:00", "Z")


def _forecast_con_incidentes(sitio_id="iqq", *, hours=24, longitud_cable_m=None, ts_pronto=None, ts_lejos=None):
    ts_pronto = ts_pronto or _ts_relativo(2)
    ts_lejos = ts_lejos or _ts_relativo(48)
    return {
        "site_id": sitio_id,
        "nombre": "Terminal Iquique (ITI)",
        "fuente": "openmeteo_multimodelo_marine",
        "hourly_states": [],
        "alerts": [
            {
                "timestamp": ts_pronto,
                "type": "sustained_wind",
                "level": "RED",
                "wind_kmh": 52.3,
                "threshold_kmh": 32.0,
                "duration_hours": 4,
            },
            {
                "timestamp": ts_pronto,
                "type": "pendulum_resonance",
                "level": "RED",
                "delta_s": 0.15,
                "duration_hours": 2,
            },
            {
                # Fuera del horizonte de registro (48h) -> no debe persistirse
                "timestamp": ts_lejos,
                "type": "sustained_wind",
                "level": "YELLOW",
                "wind_kmh": 35.0,
                "threshold_kmh": 32.0,
                "duration_hours": 3,
            },
        ],
    }


def _reset_alertas():
    path = alertas_store._path()
    if path.exists():
        path.unlink()
    alertas_store._ALERTAS_SUPABASE_WARNED = True  # evitar intentar Supabase


def test_evaluar_puerto_registra_solo_incidentes_dentro_de_horizonte(monkeypatch):
    _reset_alertas()
    monkeypatch.setattr(
        "api_rest.spati.puerto_pronostico_service.generar_pronostico_puerto",
        lambda sid, hours=24, longitud_cable_m=None: _forecast_con_incidentes(sid),
    )
    r = puerto_alert_job.evaluar_puerto_y_registrar_incidentes("iqq")
    assert r["ok"] is True
    # 2 alertas dentro de horizonte (48h queda fuera de _HORIZONTE_REGISTRO_HORAS=6)
    assert r["candidatos"] == 2
    assert r["registrados"] == 2

    historial = alertas_store.listar_historial("iqq", limite=10)
    tipos = {h.get("tipo_incidente") for h in historial}
    assert tipos == {"sustained_wind", "pendulum_resonance"}
    viento = next(h for h in historial if h["tipo_incidente"] == "sustained_wind")
    assert viento["viento_kmh"] == 52.3
    assert viento["umbral_kmh"] == 32.0


def test_evaluar_puerto_no_duplica_dentro_de_cadencia(monkeypatch):
    _reset_alertas()
    # Timestamps fijos: simula 2 corridas de cron consecutivas sobre el MISMO
    # evento en curso (igual que en producción, donde el horario de la
    # ventana pronosticada no cambia entre corridas de 15-20 min).
    ts_pronto = _ts_relativo(2)
    ts_lejos = _ts_relativo(48)
    monkeypatch.setattr(
        "api_rest.spati.puerto_pronostico_service.generar_pronostico_puerto",
        lambda sid, hours=24, longitud_cable_m=None: _forecast_con_incidentes(
            sid, ts_pronto=ts_pronto, ts_lejos=ts_lejos
        ),
    )
    r1 = puerto_alert_job.evaluar_puerto_y_registrar_incidentes("iqq")
    r2 = puerto_alert_job.evaluar_puerto_y_registrar_incidentes("iqq")
    assert r1["registrados"] == 2
    assert r2["registrados"] == 0  # mismo evento, dentro de la ventana de 6h


def test_informe_incidentes_html_incluye_datos_reales(monkeypatch):
    _reset_alertas()
    monkeypatch.setattr(
        "api_rest.spati.puerto_pronostico_service.generar_pronostico_puerto",
        lambda sid, hours=24, longitud_cable_m=None: _forecast_con_incidentes(sid),
    )
    puerto_alert_job.evaluar_puerto_y_registrar_incidentes("iqq")
    html = ris.construir_incidentes_html("iqq", dias=30)
    assert html is not None
    assert "52.3" in html
    assert "32.0" in html or "32" in html
    assert "resonancia" in html.lower()


def test_informe_incidentes_csv_real():
    _reset_alertas()
    from api_rest.spati.puerto_pronostico_service import generar_pronostico_puerto as _real

    alertas_store.registrar_alertas(
        [
            {
                "nivel": "critical",
                "estacion_id": "vlp",
                "mensaje": "Viento sostenido en Puerto Valparaíso: 60.0 km/h (umbral 32.0 km/h)",
                "origen": "puerto_incidente",
                "tipo_incidente": "sustained_wind",
                "valid_time": "2026-09-15T10:00:00Z",
                "viento_kmh": 60.0,
                "umbral_kmh": 32.0,
                "duracion_horas": 5,
            }
        ]
    )
    csv_doc = ris.construir_incidentes_csv("vlp", dias=30)
    assert csv_doc is not None
    assert "60.0" in csv_doc
    assert "vlp" in csv_doc


def test_informe_incidentes_sitio_desconocido():
    assert ris.construir_incidentes_html("puerto_inventado_xyz") is None
    assert ris.construir_incidentes_csv("puerto_inventado_xyz") is None


def test_http_route_reporte_mensual_puerto_usa_incidentes_reales(monkeypatch):
    _reset_alertas()
    monkeypatch.setattr(
        "api_rest.spati.puerto_pronostico_service.generar_pronostico_puerto",
        lambda sid, hours=24, longitud_cable_m=None: _forecast_con_incidentes(sid),
    )
    puerto_alert_job.evaluar_puerto_y_registrar_incidentes("iqq")

    from api_rest.app import create_app

    client = create_app().test_client()
    r = client.get("/api/public/spati/iqq/reporte-mensual?formato=csv")
    assert r.status_code == 200
    assert b"52.3" in r.data


def test_http_route_cron_puerto_incidentes_sin_secret(monkeypatch):
    monkeypatch.delenv("CRON_SECRET", raising=False)
    monkeypatch.setattr(
        "api_rest.spati.puerto_pronostico_service.generar_pronostico_puerto",
        lambda sid, hours=24, longitud_cable_m=None: {"error": "sitio_no_encontrado"},
    )
    from api_rest.app import create_app

    client = create_app().test_client()
    r = client.post("/api/cron/spati/puerto-incidentes?sitio=iqq")
    assert r.status_code == 200
