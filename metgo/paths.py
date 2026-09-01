#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rutas centralizadas del proyecto METGO.
Soporta layout por capas (backend/frontend/site-web) y layout legacy (01–12 en raíz).
"""

from __future__ import annotations

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Capas (v4)
BACKEND = PROJECT_ROOT / "backend"
FRONTEND = PROJECT_ROOT / "frontend"
SITE_WEB = PROJECT_ROOT / "site-web"
DOCS = PROJECT_ROOT / "docs"

LAYOUT_CAPAS = (BACKEND / "05_APIs_Externas").is_dir()


def _root_module(name: str) -> Path:
    """Ruta de módulo numerado (backend/XX o raíz/XX)."""
    if LAYOUT_CAPAS:
        return BACKEND / name
    return PROJECT_ROOT / name


def _frontend_path(*parts: str) -> Path:
    if LAYOUT_CAPAS:
        return FRONTEND.joinpath(*parts)
    return PROJECT_ROOT.joinpath("04_Dashboards_Unificados", *parts)


def _docs_path(*parts: str) -> Path:
    base = DOCS if DOCS.is_dir() else PROJECT_ROOT / "11_Documentacion"
    return base.joinpath(*parts)


# Runtime
_gd = _root_module("08_Gestion_Datos")
DATA_DIR = _gd / "datos_runtime"
LOGS_DIR = _gd / "logs_runtime"
DATOS_OFICIALES = _gd / "datos"
RESPALDOS_DIR = _root_module("12_Respaldos_Archivos") / "backups"

MODULE_PATHS = {
    "01_meteo": _root_module("01_Sistema_Meteorologico") / "scripts",
    "02_agricola": _root_module("02_Sistema_Agricola") / "scripts",
    "03_iot": _root_module("03_Sistema_IoT_Drones") / "scripts",
    "04_dashboards": _frontend_path("dashboards"),
    "04_mobile": _frontend_path("app_movil"),
    "05_apis": _root_module("05_APIs_Externas") / "scripts",
    "05_api_rest": _root_module("05_APIs_Externas"),
    "06_ml": _root_module("06_Modelos_ML_IA") / "scripts",
    "07_monitoreo": _root_module("07_Sistema_Monitoreo") / "scripts",
    "08_datos": _gd / "scripts",
    "09_testing": _root_module("09_Testing_Validacion") / "scripts",
    "10_deploy": _root_module("10_Deployment_Produccion") / "scripts",
    "11_docs": _docs_path("manuales"),
    "12_respaldos": _root_module("12_Respaldos_Archivos") / "versionado",
    "frontend_vue": _frontend_path("vue"),
    "site_web": SITE_WEB,
}


def setup_paths(*modules: str) -> None:
    """Agrega rutas de módulos al sys.path (sin duplicar)."""
    if not modules:
        modules = tuple(MODULE_PATHS.keys())
    for name in modules:
        path = MODULE_PATHS.get(name)
        if path and path.exists():
            path_str = str(path)
            if path_str not in sys.path:
                sys.path.insert(0, path_str)


def setup_all_paths() -> None:
    """Registra todas las rutas de módulos conocidas."""
    setup_paths(*MODULE_PATHS.keys())


def ensure_runtime_dirs() -> None:
    """Crea carpetas de datos/logs de ejecución."""
    for path in (DATA_DIR, LOGS_DIR, DATOS_OFICIALES, RESPALDOS_DIR):
        path.mkdir(parents=True, exist_ok=True)


def streamlit_dashboard_path(filename: str) -> Path:
    """Ruta a un script Streamlit en frontend/dashboards."""
    return _frontend_path("dashboards", filename)


def site_web_streamlit_dir() -> Path:
    """Directorio Streamlit público (site-web o stub CI en tests/fixtures/streamlit_public)."""
    canonical = SITE_WEB / "streamlit"
    if canonical.is_dir():
        return canonical
    fixtures = PROJECT_ROOT / "tests" / "fixtures" / "streamlit_public"
    if fixtures.is_dir():
        return fixtures
    return canonical


def site_web_streamlit_path(filename: str) -> Path:
    """Ruta a un script Streamlit en site-web/streamlit/."""
    return site_web_streamlit_dir() / filename


def frontend_vue_dir() -> Path:
    """Directorio de la SPA Vue."""
    return _frontend_path("vue")


def frontend_app_movil_dir() -> Path:
    """Directorio de la app móvil React Native."""
    canonical = _frontend_path("app_movil")
    if canonical.is_dir():
        return canonical
    return _frontend_path("dashboards", "app_movil_metgo")


def deploy_script(name: str) -> Path:
    """Ruta a script en 10_Deployment."""
    return _root_module("10_Deployment_Produccion") / "scripts" / name


def backend_script(module: str, *parts: str) -> Path:
    """Ruta bajo backend/XX_.../scripts/ o equivalente legacy."""
    return _root_module(module) / "scripts" / Path(*parts)


def compat_scripts_dir() -> Path:
    """Wrappers de compatibilidad (imports legacy desde dashboards)."""
    return PROJECT_ROOT / "scripts" / "compat"
