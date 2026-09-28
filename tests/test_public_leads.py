#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests: POST /api/public/leads acepta los formularios en español de la SPA."""

from __future__ import annotations

import os

os.environ.setdefault("METGO_JWT_SECRET", "test-secret-public-leads-min-32-bytes!!")

from api_rest.schemas import LeadCaptureRequest


def _client():
    from api_rest.app import create_app

    return create_app().test_client()


def test_formulario_contacto_en_espanol_se_guarda(mock_supabase):
    r = _client().post(
        "/api/public/leads",
        json={
            "nombre": "Juan Pérez Soto",
            "empresa": "Fundo Los Cerezos",
            "sector": "heladas",
            "email": "juan@example.com",
            "telefono": "+56912345678",
            "mensaje": "Plan: basico",
        },
    )
    assert r.status_code == 201, r.get_json()
    fila = mock_supabase.db["leads"][-1]
    assert fila["first_name"] == "Juan" and fila["last_name"] == "Pérez Soto"
    assert fila["company_name"] == "Fundo Los Cerezos"
    assert fila["phone"] == "+56912345678" and fila["notes"] == "Plan: basico"
    assert fila["sector"] == "heladas"


def test_lead_magnet_solo_email(mock_supabase):
    r = _client().post(
        "/api/public/leads",
        json={"email": "x@example.com", "nombre": "", "empresa": "", "sector": "", "source": "lead_magnet_bar"},
    )
    assert r.status_code == 201, r.get_json()
    assert mock_supabase.db["leads"][-1]["sector"] == "sin_especificar"


def test_campos_en_ingles_siguen_funcionando():
    lead = LeadCaptureRequest.desde_payload(
        {"first_name": "Ana", "last_name": "Rojas", "company_name": "Agro", "email": "a@example.com", "sector": "agricultura"}
    )
    assert lead.first_name == "Ana" and lead.company_name == "Agro"


def test_sin_email_es_400():
    assert _client().post("/api/public/leads", json={"nombre": "X"}).status_code == 400
