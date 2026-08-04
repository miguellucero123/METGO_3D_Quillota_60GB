#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Catálogo de planes y precios escalonados por sitio/faena.

Fuente comercial: docs/roadmap/PLAN_COMERCIAL_SPATI_3_PLANES.md
Básico $300.000 · Pro $500.000 · Enterprise desde $1.200.000 (a medida).
"""

from __future__ import annotations

from typing import Any

# Precio base CLP/mes por plan (Stripe Price IDs vía env en S2)
_BASE_PLANS: dict[str, dict[str, Any]] = {
    "trial": {
        "plan_code": "trial",
        "nombre": "Piloto 15 días",
        "nombre_corto": "Piloto",
        "precio_mensual_clp": 0,
        "seats": 2,
        "faenas_max": 1,
        "gruas_max": 1,
        "features": ["panel", "ambiente", "ahora"],
        "trial_days": 15,
        "canales_alerta": ["email"],
        "descripcion": "Pronóstico 72 h y vista Ahora en una faena, sin tarjeta.",
        "entregables": ["panel_web", "pdf_operacion"],
    },
    "starter": {
        "plan_code": "starter",
        "nombre": "Básico",
        "nombre_corto": "Básico",
        "precio_mensual_clp": 300_000,
        "seats": 3,
        "faenas_max": 1,
        "gruas_max": 2,
        "features": ["panel", "ambiente", "ahora", "alertas"],
        "canales_alerta": ["email"],
        "descripcion": (
            "1 faena, hasta 2 grúas. Vista Ahora + pronóstico 72 h, PDF por "
            "operación y alertas por correo."
        ),
        "entregables": ["panel_web", "pdf_operacion", "datasheet"],
        "publico_objetivo": "Una faena que necesita decidir izaje con datos en el punto GPS.",
    },
    "pro": {
        "plan_code": "pro",
        "nombre": "Pro",
        "nombre_corto": "Pro",
        "precio_mensual_clp": 500_000,
        "seats": 10,
        "faenas_max": 3,
        "gruas_max": 5,
        "features": [
            "panel",
            "ambiente",
            "ahora",
            "dron",
            "umbrales",
            "alertas",
            "reporte_mensual",
        ],
        "canales_alerta": ["email", "whatsapp"],
        "recomendado": True,
        "descripcion": (
            "Hasta 3 faenas / 5 grúas. WhatsApp, umbrales editables, calibración "
            "dron y reporte mensual de ROI."
        ),
        "entregables": [
            "panel_web",
            "pdf_operacion",
            "reporte_mensual",
            "datasheet",
            "propuesta_comercial",
        ],
        "publico_objetivo": "Jefes de operaciones con flota activa y necesidad de ROI medible.",
    },
    "enterprise": {
        "plan_code": "enterprise",
        "nombre": "Enterprise",
        "nombre_corto": "Enterprise",
        "precio_mensual_clp": 1_200_000,
        "precio_etiqueta": "desde",
        "seats": None,
        "faenas_max": None,
        "gruas_max": None,
        "features": [
            "panel",
            "ambiente",
            "ahora",
            "dron",
            "umbrales",
            "alertas",
            "reporte_mensual",
            "multi_faena",
            "api",
            "sla",
            "ops_board",
            "account_manager",
            "white_label",
            "erp_integration",
        ],
        "canales_alerta": ["email", "whatsapp", "sms"],
        "contacto": True,
        "sla_uptime": 0.995,
        "descripcion": (
            "Multi-faena ilimitada, API REST + webhooks, SLA 99.5%, soporte 24/7, "
            "account manager, integración ERP/SAP e informes legales / white-label."
        ),
        "entregables": [
            "panel_web",
            "pdf_operacion_certificado",
            "reporte_mensual_ejecutivo",
            "datasheet_sla",
            "propuesta_comercial",
            "kit_alianza",
            "api_sandbox",
            "runbook_ops",
        ],
        "publico_objetivo": (
            "Mandantes, EPC y empresas con varias faenas que integran SPATI al sistema."
        ),
        "incluye": [
            "Board ops multi-faena (/ops)",
            "API REST + webhooks + sandbox",
            "Hasta 5 días-hombre de integración ERP/SAP o conector BI",
            "SLA 99.5% contractual con créditos de servicio",
            "Account manager + canal 24/7",
            "Reporte mensual ejecutivo personalizado",
            "PDF con firma digital y pack legal",
            "Umbrales y destinos por faena/grúa",
            "Revisión trimestral de exactitud del modelo",
        ],
        "add_ons": [
            {"codigo": "integracion_extra", "nombre": "Días-hombre integración extra"},
            {"codigo": "white_label_dominio", "nombre": "White-label dominio propio"},
            {"codigo": "iot_anemometro", "nombre": "Sensor / IoT anemómetro"},
            {"codigo": "capacitacion", "nombre": "Capacitación in-company"},
            {"codigo": "informe_pericial", "nombre": "Informe pericial / caso legal"},
        ],
    },
    # Acceso temporal interno / demo (no listado comercial)
    "preview": {
        "plan_code": "preview",
        "nombre": "Vista previa 1 h",
        "nombre_corto": "Preview",
        "precio_mensual_clp": 0,
        "seats": 1,
        "faenas_max": 1,
        "gruas_max": 1,
        "features": ["panel", "ahora"],
        "trial_days": 0,
        "hidden": True,
        "ttl_hours": 1,
        "canales_alerta": [],
        "descripcion": "Solo Ahora + Panel técnico. Expira en 1 hora y se elimina.",
        "entregables": ["panel_web"],
    },
}

# Multiplicador comercial por faena (escalado; 1.0 = base)
_FAENA_MULTIPLIER: dict[str, float] = {
    "escondida": 1.25,
    "los_bronces": 1.15,
    "collahuasi": 1.2,
    "andina": 1.1,
    "el_teniente": 1.15,
}

_PLAN_RANK = {"preview": 0, "trial": 0, "starter": 1, "pro": 2, "enterprise": 3}

# Mapeo tab SPA → feature / sistema
TAB_FEATURE = {
    "panel": "panel",
    "ahora": "ahora",
    "dron": "dron",
    "umbrales": "umbrales",
    "ambiente": "ambiente",
}

TAB_SISTEMA = {
    "panel": "izaje",
    "ahora": "izaje",
    "dron": "dron",
    "umbrales": "ops",
    "ambiente": "ambiente",
}


def plan_rank(code: str | None) -> int:
    return _PLAN_RANK.get((code or "trial").lower(), 0)


def listar_planes(sitio: str, faena: str | None = None) -> dict[str, Any]:
    mult = _FAENA_MULTIPLIER.get((faena or "").lower(), 1.0) if sitio == "spati" else 1.0
    planes = []
    for code, p in _BASE_PLANS.items():
        if p.get("hidden"):
            continue
        item = dict(p)
        base = p.get("precio_mensual_clp")
        if base is not None:
            item["precio_mensual_clp"] = int(round(base * mult))
        item["multiplicador_faena"] = mult
        item["moneda"] = "CLP"
        item["iva"] = "no_incluido"
        planes.append(item)
    return {
        "sitio": sitio,
        "faena": faena,
        "moneda": "CLP",
        "iva": "no_incluido",
        "nota": (
            "Precios mensuales sin IVA. Enterprise: precio desde; cotización a medida. "
            "Sin tarifa por informe suelto."
        ),
        "planes": planes,
    }


def features_for_plan(plan_code: str) -> set[str]:
    p = _BASE_PLANS.get((plan_code or "trial").lower()) or _BASE_PLANS["trial"]
    return set(p.get("features") or [])


def trial_days() -> int:
    """Días del piloto (fuente: catálogo trial.trial_days)."""
    p = _BASE_PLANS.get("trial") or {}
    try:
        return max(1, int(p.get("trial_days") or 15))
    except (TypeError, ValueError):
        return 15
