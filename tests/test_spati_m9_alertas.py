#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""M9 — umbrales por faena + alertas SPATI."""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import metgo_paths


def _setup():
    metgo_paths.setup_paths("05_api_rest")
    apis = metgo_paths.MODULE_PATHS["05_api_rest"]
    if str(apis) not in sys.path:
        sys.path.insert(0, str(apis))


def test_alert_system_umbrales_custom():
    _setup()
    from api_rest.spati.alert_system import CraneSafetyAlertSystem

    alerts = CraneSafetyAlertSystem(
        amarillo_min_kmh=28, naranja_min_kmh=32, rojo_min_kmh=38, flag_critico_kmh=40
    )
    assert alerts.clasificar_nivel(27).nivel == 0
    assert alerts.clasificar_nivel(29).nivel == 1
    assert alerts.clasificar_nivel(33).nivel == 2
    assert alerts.clasificar_nivel(39).nivel == 3
    assert alerts.clasificar_nivel(41).flag_critico is True


def test_umbrales_efectivos_default_y_override(tmp_path, monkeypatch):
    _setup()
    from api_rest.spati import umbrales_service

    monkeypatch.setattr(umbrales_service, "_runtime_overrides_path", lambda: tmp_path / "u.json")
    monkeypatch.delenv("METGO_SPATI_UMBRALES_JSON", raising=False)

    d = umbrales_service.umbrales_efectivos("escondida")
    assert d["rojo_min_kmh"] == 35
    assert d["fuente"] == "default"

    saved = umbrales_service.guardar_umbrales_local(
        "escondida", {"rojo_min_kmh": 40, "verde_max_kmh": 28}
    )
    assert saved["rojo_min_kmh"] == 40
    assert saved["verde_max_kmh"] == 28
    assert saved["fuente"] in ("override", "default")


def test_m9_evaluar_transicion_notifica(tmp_path, monkeypatch):
    _setup()
    from api_rest import spati_alert_job

    monkeypatch.setattr(spati_alert_job, "_state_path", lambda: tmp_path / "state.json")

    fake = {
        "nivel_maximo": 2,
        "sitio": {"nombre": "Escondida"},
        "serie": [{"valid_time": "2026-07-28T12:00:00Z", "nivel_alerta": 2}],
    }
    with patch.object(spati_alert_job, "_persist_supabase"), patch(
        "api_rest.integracion.notificaciones.enviar_notificacion",
        return_value={"ok": True},
    ) as mock_n, patch(
        "api_rest.integracion.alertas_store.registrar_alertas", return_value=None
    ):
        r1 = spati_alert_job.evaluar_y_notificar("escondida", pronostico=fake)
        assert r1["notificado"] is True
        assert mock_n.called
        r2 = spati_alert_job.evaluar_y_notificar("escondida", pronostico=fake)
        assert r2["notificado"] is False
        assert r2["motivo"] == "sin_cambio"


def test_m9_api_umbrales_y_cron():
    _setup()
    from api_rest.app import create_app

    c = create_app().test_client()
    r = c.get("/api/public/spati/escondida/umbrales")
    assert r.status_code == 200
    body = r.get_json()
    assert "umbrales" in body
    assert body["umbrales"]["rojo_min_kmh"] >= 30

    with patch(
        "api_rest.spati_alert_job.evaluar_y_notificar",
        return_value={"ok": True, "notificado": False, "sitio_id": "escondida"},
    ):
        rc = c.post("/api/cron/spati/alertas?sitio=escondida")
        assert rc.status_code == 200
        assert rc.get_json()["ok"] is True
