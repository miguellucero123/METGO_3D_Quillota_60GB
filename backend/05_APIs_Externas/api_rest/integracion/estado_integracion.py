#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Métricas de grado de integración por módulo (cálculo dinámico)."""

from __future__ import annotations

from typing import Any

from api_rest.integracion import alertas_store, meteo_store, reportes_bridge
from api_rest.integracion.capabilities import evaluar_todos
from api_rest.integracion import testing_info, deploy_info


def resumen_integracion_health() -> dict[str, Any]:
    """Solo métricas agregadas para GET /api/health (sin detalle operativo)."""
    modulos = evaluar_todos()
    activos = [m for m in modulos if m["id"] != "12"]
    promedio = round(sum(m["porcentaje"] for m in activos) / len(activos)) if activos else 0
    return {
        "promedio_integracion": promedio,
        "integracion_completa": promedio >= 95,
        "modulos_total": len(modulos),
    }


def estado_modulos() -> dict[str, Any]:
    modulos = evaluar_todos()
    activos = [m for m in modulos if m["id"] != "12"]
    promedio = round(sum(m["porcentaje"] for m in activos) / len(activos)) if activos else 0
    meteo_stats = meteo_store.estadisticas_store()
    reportes = reportes_bridge.listar_ultimos_reportes(3)
    historial_alertas = len(alertas_store._load())
    tests = testing_info.resumen_tests()

    return {
        "promedio_integracion": promedio,
        "integracion_completa": promedio >= 95,
        "fase": "10",
        "modulos": modulos,
        "meteo_store": {
            "registros": meteo_stats.get("registros", 0),
            "estaciones": meteo_stats.get("estaciones", 0),
        },
        "reportes_disponibles": len(reportes),
        "historial_alertas": historial_alertas,
        "tests": {
            "tests_raiz": tests.get("tests_raiz", 0),
            "ci_github": tests.get("ci_github", False),
        },
        "deploy": deploy_info.resumen_deploy_publico(),
    }
