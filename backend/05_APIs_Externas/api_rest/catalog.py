#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Catálogo de módulos y dashboards METGO (alineado con sistema Streamlit)."""

from __future__ import annotations

import os
from typing import Any

# Configuración por estación (desde dashboard principal Streamlit)
CONFIGURACION_ESTACIONES: dict[str, dict[str, str]] = {
    "Quillota": {
        "zona": "Valle Central - Clima Mediterráneo",
        "superficie": "15,000 Ha",
        "actividad": "Agricultura y Agroindustria",
    },
    "Los Nogales": {
        "zona": "Valle Central - Microclima Nogales",
        "superficie": "3,200 Ha",
        "actividad": "Agricultura Especializada",
    },
    "Hijuelas": {
        "zona": "Valle Central - Zona Agrícola Intensiva",
        "superficie": "8,500 Ha",
        "actividad": "Agricultura Intensiva",
    },
    "Limache": {
        "zona": "Valle Central - Clima Templado",
        "superficie": "12,000 Ha",
        "actividad": "Agricultura Diversificada",
    },
    "Olmue": {
        "zona": "Valle Central - Clima Húmedo",
        "superficie": "6,000 Ha",
        "actividad": "Agricultura Tradicional",
    },
}

MODULOS_SISTEMA: list[dict[str, Any]] = [
    {
        "id": "panel",
        "nombre": "Panel general",
        "categoria": "vue",
        "modulo_num": "04",
        "descripcion": "Resumen integrado meteorológico y agrícola con datos OpenMeteo.",
        "tipo_acceso": "vue",
        "ruta_vue": "/",
        "icono": "layout-dashboard",
    },
    {
        "id": "meteo",
        "nombre": "Meteorología",
        "categoria": "meteorologico",
        "modulo_num": "01",
        "descripcion": "Pronóstico, histórico, estaciones y variables atmosféricas.",
        "tipo_acceso": "vue",
        "ruta_vue": "/meteo",
        "icono": "cloud-sun",
        "atributos": ["temperatura", "humedad", "viento", "precipitacion", "presion", "pronostico_7d", "historico_14d"],
    },
    {
        "id": "agricola",
        "nombre": "Gestión agrícola",
        "categoria": "agricola",
        "modulo_num": "02",
        "descripcion": "Recomendaciones, riego, heladas y cultivos del Valle de Aconcagua.",
        "tipo_acceso": "vue",
        "ruta_vue": "/agricola",
        "icono": "sprout",
        "atributos": ["recomendaciones", "riesgo_helada", "riego", "cultivos_quillota"],
    },
    {
        "id": "monitoreo",
        "nombre": "Alertas y monitoreo",
        "categoria": "monitoreo",
        "modulo_num": "07",
        "descripcion": "Alertas automáticas, umbrales y estado del sistema.",
        "tipo_acceso": "vue",
        "ruta_vue": "/monitoreo",
        "icono": "bell-ring",
        "atributos": ["alertas_temperatura", "alertas_viento", "alertas_precipitacion"],
    },
    {
        "id": "configuracion",
        "nombre": "Configuración",
        "categoria": "sistema",
        "modulo_num": "04",
        "descripcion": "Estaciones, tipos de análisis e integración con módulos Streamlit.",
        "tipo_acceso": "vue",
        "ruta_vue": "/configuracion",
        "icono": "settings",
    },
    {
        "id": "modulos_hub",
        "nombre": "Catálogo de módulos",
        "categoria": "sistema",
        "modulo_num": "04",
        "descripcion": "Vista unificada de todos los módulos numerados 01–12 del proyecto.",
        "tipo_acceso": "vue",
        "ruta_vue": "/modulos",
        "icono": "grid-3x3",
    },
    {
        "id": "streamlit_principal",
        "nombre": "Dashboard principal Streamlit",
        "categoria": "streamlit",
        "modulo_num": "04",
        "descripcion": "Dashboard completo con gráficos, selector de análisis y navegación legacy.",
        "utilidad": "Menú central legacy: gráficos, selector de análisis y acceso a sub-dashboards.",
        "tipo_acceso": "streamlit",
        "script": "streamlit_app.py",
        "puerto": 8501,
        "icono": "monitor",
        "ruta_vue_alternativa": "/",
    },
    {
        "id": "meteo_streamlit",
        "nombre": "Análisis meteorológico profesional",
        "categoria": "streamlit",
        "modulo_num": "01",
        "descripcion": "Dashboard meteorológico avanzado con visualizaciones Plotly.",
        "utilidad": "Series históricas, pronóstico multi-variable y gráficos Plotly por estación.",
        "tipo_acceso": "streamlit",
        "script": "frontend/dashboards/dashboard_meteorologico_profesional.py",
        "puerto": 8502,
        "icono": "thermometer",
        "ruta_vue_alternativa": "/meteo",
    },
    {
        "id": "agricola_streamlit",
        "nombre": "Gestión agrícola inteligente",
        "categoria": "streamlit",
        "modulo_num": "02",
        "descripcion": "Riego, plagas, heladas y recomendaciones agrícolas avanzadas.",
        "utilidad": "Riego, heladas, plagas y recomendaciones detalladas por cultivo y zona.",
        "tipo_acceso": "streamlit",
        "script": "frontend/dashboards/dashboard_agricola_inteligente.py",
        "puerto": 8503,
        "icono": "sprout",
        "ruta_vue_alternativa": "/agricola",
    },
    {
        "id": "monitoreo_streamlit",
        "nombre": "Monitoreo en tiempo real",
        "categoria": "streamlit",
        "modulo_num": "07",
        "descripcion": "Monitoreo continuo y métricas operativas.",
        "utilidad": "Métricas en vivo, latencia de sensores y estado operativo del sistema.",
        "tipo_acceso": "streamlit",
        "script": "frontend/dashboards/dashboard_monitoreo_tiempo_real.py",
        "puerto": 8504,
        "icono": "activity",
        "ruta_vue_alternativa": "/monitoreo",
    },
    {
        "id": "ml_streamlit",
        "nombre": "Inteligencia artificial / ML",
        "categoria": "streamlit",
        "modulo_num": "06",
        "descripcion": "Modelos predictivos y análisis ML del sistema.",
        "utilidad": "Entrenamiento, métricas de modelos y predicciones ML sobre variables meteo.",
        "tipo_acceso": "streamlit",
        "script": "frontend/dashboards/dashboard_ia_ml_avanzado.py",
        "puerto": 8505,
        "icono": "cpu",
    },
    {
        "id": "visualizaciones",
        "nombre": "Visualizaciones avanzadas",
        "categoria": "streamlit",
        "modulo_num": "04",
        "descripcion": "Gráficos avanzados y comparativos multi-estación.",
        "utilidad": "Mapas de calor, correlaciones y comparativos Plotly entre estaciones del valle.",
        "tipo_acceso": "streamlit",
        "script": "frontend/dashboards/dashboard_visualizaciones_avanzadas.py",
        "puerto": 8506,
        "icono": "bar-chart-3",
    },
    {
        "id": "metricas_globales",
        "nombre": "Métricas globales",
        "categoria": "streamlit",
        "modulo_num": "04",
        "descripcion": "KPIs y métricas consolidadas del sistema.",
        "utilidad": "KPIs consolidados: temperatura media, alertas activas y resumen multi-estación.",
        "tipo_acceso": "streamlit",
        "script": "frontend/dashboards/dashboard_global_metricas.py",
        "puerto": 8507,
        "icono": "gauge",
    },
    {
        "id": "agricola_precision",
        "nombre": "Agricultura de precisión",
        "categoria": "streamlit",
        "modulo_num": "02",
        "descripcion": "Mapas de precisión, suelos y manejo por zonas.",
        "utilidad": "Zonificación, suelos y manejo diferenciado por parcela en el valle.",
        "tipo_acceso": "streamlit",
        "script": "frontend/dashboards/dashboard_agricultura_precision.py",
        "puerto": 8508,
        "icono": "map",
        "ruta_vue_alternativa": "/agricola",
    },
    {
        "id": "analisis_comparativo",
        "nombre": "Análisis comparativo",
        "categoria": "streamlit",
        "modulo_num": "04",
        "descripcion": "Comparación entre estaciones y períodos.",
        "utilidad": "Compara Quillota, Hijuelas, Limache, etc. en el mismo período o temporada.",
        "tipo_acceso": "streamlit",
        "script": "frontend/dashboards/dashboard_analisis_comparativo.py",
        "puerto": 8509,
        "icono": "git-compare",
        "ruta_vue_alternativa": "/meteo",
    },
    {
        "id": "alertas_streamlit",
        "nombre": "Sistema de alertas automáticas",
        "categoria": "streamlit",
        "modulo_num": "07",
        "descripcion": "Configuración y historial de alertas.",
        "utilidad": "Umbrales, historial y configuración de alertas automáticas por variable.",
        "tipo_acceso": "streamlit",
        "script": "frontend/dashboards/dashboard_alertas_automaticas.py",
        "puerto": 8510,
        "icono": "shield-alert",
        "ruta_vue_alternativa": "/monitoreo",
    },
    {
        "id": "simple",
        "nombre": "Dashboard simple optimizado",
        "categoria": "streamlit",
        "modulo_num": "04",
        "descripcion": "Vista ligera para consultas rápidas.",
        "utilidad": "Consulta rápida sin gráficos pesados; ideal en terreno o conexión lenta.",
        "tipo_acceso": "streamlit",
        "script": "frontend/dashboards/dashboard_simple_optimizado.py",
        "puerto": 8511,
        "icono": "minimize-2",
        "ruta_vue_alternativa": "/",
    },
    {
        "id": "unificado",
        "nombre": "Dashboard unificado",
        "categoria": "streamlit",
        "modulo_num": "04",
        "descripcion": "Vista unificada diferenciada por rol.",
        "utilidad": "Una sola pantalla con vistas distintas para operador, agrónomo y administrador.",
        "tipo_acceso": "streamlit",
        "script": "frontend/dashboards/dashboard_unificado_diferenciado.py",
        "puerto": 8512,
        "icono": "layers",
        "ruta_vue_alternativa": "/",
    },
    {
        "id": "mobile",
        "nombre": "Dashboard móvil",
        "categoria": "streamlit",
        "modulo_num": "04",
        "descripcion": "Interfaz optimizada para dispositivos móviles.",
        "utilidad": "Layout compacto para celular; mismos datos con menos scroll y gráficos táctiles.",
        "tipo_acceso": "streamlit",
        "script": "frontend/dashboards/dashboard_mobile_optimizado.py",
        "puerto": 8513,
        "icono": "smartphone",
        "ruta_vue_alternativa": "/",
    },
    {
        "id": "iot",
        "nombre": "IoT y drones",
        "categoria": "backend",
        "modulo_num": "03",
        "descripcion": "Sensores IoT y datos satelitales (scripts Python).",
        "tipo_acceso": "info",
        "ruta_carpeta": "03_Sistema_IoT_Drones/scripts/",
        "icono": "radio",
    },
    {
        "id": "apis",
        "nombre": "APIs externas",
        "categoria": "backend",
        "modulo_num": "05",
        "descripcion": "Conectores OpenMeteo y APIs meteorológicas.",
        "tipo_acceso": "info",
        "ruta_carpeta": "05_APIs_Externas/",
        "icono": "plug",
    },
    {
        "id": "datos",
        "nombre": "Gestión de datos",
        "categoria": "backend",
        "modulo_num": "08",
        "descripcion": "ETL, orquestación y base de datos histórica.",
        "tipo_acceso": "info",
        "ruta_carpeta": "08_Gestion_Datos/scripts/",
        "icono": "database",
    },
    {
        "id": "notebook_mip",
        "nombre": "Notebook MIP Quillota",
        "categoria": "notebook",
        "modulo_num": "01",
        "descripcion": "Sistema de pronóstico y gestión agrícola MIP (Jupyter).",
        "tipo_acceso": "info",
        "ruta_carpeta": "01_Sistema_Meteorologico/scripts/Sistema_de_Pronostico_Meteorologico_y_Gestion_Agricola_MIP_Quillota_beta.ipynb",
        "icono": "book-open",
    },
]

CATEGORIAS = [
    {"id": "vue", "nombre": "Vue (moderno)", "color": "#3d6b52"},
    {"id": "streamlit", "nombre": "Streamlit", "color": "#5a7c6a"},
    {"id": "meteorologico", "nombre": "Meteorológico", "color": "#4a90a4"},
    {"id": "agricola", "nombre": "Agrícola", "color": "#6b8f5e"},
    {"id": "monitoreo", "nombre": "Monitoreo", "color": "#8b7355"},
    {"id": "backend", "nombre": "Backend / scripts", "color": "#6b7f74"},
    {"id": "notebook", "nombre": "Notebooks", "color": "#7a6b8a"},
    {"id": "sistema", "nombre": "Sistema", "color": "#3d6b52"},
]

TIPOS_ANALISIS = [
    {"id": "historico", "nombre": "Histórico", "dias_default": 30},
    {"id": "pronostico", "nombre": "Pronóstico", "dias_default": 7},
    {"id": "comparativo", "nombre": "Comparativo", "dias_default": 14},
]

INTERVALOS_ACTUALIZACION = ["manual", "5min", "15min", "30min", "1h"]


def streamlit_host() -> str:
    return os.getenv("METGO_STREAMLIT_HOST", "http://127.0.0.1").rstrip("/")


def streamlit_cloud_base() -> str | None:
    """URL del portal Streamlit en Render/Cloud (una app, no 13 puertos)."""
    url = (
        os.getenv("METGO_STREAMLIT_CLOUD_URL")
        or os.getenv("METGO_STREAMLIT_PORTAL_URL")
        or ""
    ).strip().rstrip("/")
    return url or None


def enriquecer_modulo(mod: dict[str, Any]) -> dict[str, Any]:
    m = dict(mod)
    if m.get("tipo_acceso") != "streamlit" or not m.get("puerto"):
        return m

    m["utilidad"] = m.get("utilidad") or m.get("descripcion", "")
    puerto = m["puerto"]
    m["puerto_etiqueta"] = f":{puerto}"
    m["url_local"] = f"http://127.0.0.1:{puerto}"

    from api_rest.streamlit_launcher import _api_en_nube

    nube = streamlit_cloud_base()
    try:
        from metgo.dashboard_loader import url_visor

        visor = url_visor(nube, m["id"]) if nube else None
    except ImportError:
        visor = f"{nube}/Visor_de_puerto?id={m['id']}&embed=true" if nube else None

    if _api_en_nube():
        if nube:
            m["url_visor"] = visor
            m["url_embed"] = visor
            m["url_streamlit"] = visor or f"{nube}/?activar={m['id']}"
            m["url_nube"] = f"{nube}/?activar={m['id']}"
            m["solo_local"] = False
            m["acceso_nube"] = True
        else:
            m["url_streamlit"] = None
            m["url_nube"] = None
            m["solo_local"] = True
            m["acceso_nube"] = False
    else:
        m["url_streamlit"] = f"{streamlit_host()}:{puerto}"
        m["url_visor"] = visor
        m["url_embed"] = f"http://127.0.0.1:{puerto}/?embed=true"
        m["url_nube"] = visor or (f"{nube}/?activar={m['id']}" if nube else None)
        m["solo_local"] = False
        m["acceso_nube"] = bool(nube)
    return m


def listar_modulos(categoria: str | None = None) -> list[dict[str, Any]]:
    items = [enriquecer_modulo(m) for m in MODULOS_SISTEMA]
    if categoria:
        items = [m for m in items if m.get("categoria") == categoria]
    return items


def obtener_modulo(modulo_id: str) -> dict[str, Any] | None:
    for m in MODULOS_SISTEMA:
        if m["id"] == modulo_id:
            return enriquecer_modulo(m)
    return None


def configuracion_estacion(nombre_estacion: str) -> dict[str, Any]:
    cfg = CONFIGURACION_ESTACIONES.get(
        nombre_estacion.title() if nombre_estacion else "Quillota",
        CONFIGURACION_ESTACIONES["Quillota"],
    )
    return {"estacion": nombre_estacion, **cfg}


def resumen_sistema() -> dict[str, Any]:
    return {
        "total_modulos": len(MODULOS_SISTEMA),
        "vue": len([m for m in MODULOS_SISTEMA if m.get("tipo_acceso") == "vue"]),
        "streamlit": len([m for m in MODULOS_SISTEMA if m.get("tipo_acceso") == "streamlit"]),
        "categorias": CATEGORIAS,
        "tipos_analisis": TIPOS_ANALISIS,
        "intervalos": INTERVALOS_ACTUALIZACION,
        "streamlit_host": streamlit_host(),
    }
