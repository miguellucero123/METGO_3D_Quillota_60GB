#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Métricas de grado de integración por módulo (cálculo dinámico)."""

from __future__ import annotations

from typing import Any

from api_rest.integracion import alertas_store, meteo_store, reportes_bridge
from api_rest.integracion.capabilities import evaluar_todos
from api_rest.integracion import etl_sync, testing_info, deploy_info, docs_index


def estado_modulos() -> dict[str, Any]:
    modulos = evaluar_todos()
    activos = [m for m in modulos if m["id"] != "12"]
    promedio = round(sum(m["porcentaje"] for m in activos) / len(activos)) if activos else 0
    meteo_stats = meteo_store.estadisticas_store()
    reportes = reportes_bridge.listar_ultimos_reportes(3)
    historial_alertas = len(alertas_store._load())

    return {
        "promedio_integracion": promedio,
        "integracion_completa": promedio >= 95,
        "fase": "10",
        "modulos": modulos,
        "meteo_store": meteo_stats,
        "reportes_disponibles": len(reportes),
        "historial_alertas": historial_alertas,
        "fuentes_datos": etl_sync.fuentes_datos(),
        "tests": testing_info.resumen_tests(),
        "deploy": deploy_info.resumen_deploy(),
        "documentacion": docs_index.indice_documentacion(),
    }
