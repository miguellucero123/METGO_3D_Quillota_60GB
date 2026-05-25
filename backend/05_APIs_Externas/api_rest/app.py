#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API REST METGO — Flask + CORS + JWT para frontend Vue.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
for _p in Path(__file__).resolve().parents:
    if (_p / "metgo_paths.py").exists():
        ROOT = _p
        break
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import metgo_paths

metgo_paths.setup_paths("01_meteo", "05_api_rest")
_apis_root = metgo_paths.MODULE_PATHS.get("05_api_rest")
if _apis_root and str(_apis_root) not in sys.path:
    sys.path.insert(0, str(_apis_root))

from flask import Flask, jsonify, request
from flask_cors import CORS

from api_rest import catalog, services, streamlit_launcher
from api_rest.auth_routes import auth_required, register_auth_routes


def create_app() -> Flask:
    app = Flask(__name__)
    CORS(
        app,
        resources={r"/api/*": {"origins": os.getenv("METGO_CORS_ORIGINS", "*").split(",")}},
        supports_credentials=True,
    )

    register_auth_routes(app)

    @app.get("/")
    def index():
        """Evita 404 si se abre :8080 en el navegador por error."""
        return jsonify(
            {
                "servicio": "METGO API REST",
                "estado": "activo",
                "nota": "La interfaz web Vue corre en http://127.0.0.1:5173 (npm run dev)",
                "endpoints": {
                    "health": "/api/health",
                    "login": "POST /api/auth/login",
                    "public_estaciones": "/api/public/estaciones",
                    "public_meteo": "/api/public/meteo/<estacion_id>",
                },
            }
        )

    @app.get("/api/health")
    def health():
        return jsonify(services.health_check())

    @app.get("/api/public/estaciones")
    def public_estaciones():
        """Estaciones principales (solo lectura, sin JWT)."""
        return jsonify(services.listar_estaciones())

    @app.get("/api/public/meteo/<estacion_id>")
    def public_meteo(estacion_id: str):
        """Resumen meteorológico público (solo lectura, sin JWT)."""
        data = services.resumen_meteo(estacion_id)
        if data is None:
            return jsonify({"error": "Sin datos para la estacion"}), 404
        return jsonify(data)

    @app.get("/api/estaciones")
    @auth_required
    def estaciones():
        return jsonify(services.listar_estaciones())

    @app.get("/api/meteo/<estacion_id>")
    @auth_required
    def meteo_resumen(estacion_id: str):
        tipo = request.args.get("tipo", "pronostico")
        if tipo == "historico":
            hist = services.historico_meteo(estacion_id, 7)
            data = hist[-1] if hist else None
        else:
            data = services.resumen_meteo(estacion_id)
        if data is None:
            return jsonify({"error": "Sin datos para la estacion"}), 404
        return jsonify(data)

    @app.get("/api/meteo/<estacion_id>/pronostico")
    @auth_required
    def meteo_pronostico(estacion_id: str):
        dias = request.args.get("dias", 7, type=int)
        data = services.pronostico_meteo(estacion_id, dias)
        if data is None:
            return jsonify({"error": "Sin pronostico"}), 404
        return jsonify(data)

    @app.get("/api/meteo/<estacion_id>/historico")
    @auth_required
    def meteo_historico(estacion_id: str):
        dias = request.args.get("dias", 30, type=int)
        data = services.historico_meteo(estacion_id, dias)
        if data is None:
            return jsonify({"error": "Sin historico"}), 404
        return jsonify(data)

    @app.get("/api/alertas")
    @auth_required
    def alertas():
        estacion_id = request.args.get("estacion")
        return jsonify(services.generar_alertas(estacion_id))

    @app.get("/api/agricola/<estacion_id>")
    @auth_required
    def agricola(estacion_id: str):
        return jsonify(services.recomendaciones_agricolas(estacion_id))

    @app.get("/api/sistema/resumen")
    @auth_required
    def sistema_resumen():
        return jsonify(catalog.resumen_sistema())

    @app.get("/api/modulos")
    @auth_required
    def modulos_lista():
        cat = request.args.get("categoria")
        return jsonify(catalog.listar_modulos(cat))

    @app.get("/api/modulos/<modulo_id>")
    @auth_required
    def modulo_detalle(modulo_id: str):
        m = catalog.obtener_modulo(modulo_id)
        if not m:
            return jsonify({"error": "Modulo no encontrado"}), 404
        return jsonify(m)

    @app.get("/api/configuracion/estacion/<estacion_id>")
    @auth_required
    def config_estacion(estacion_id: str):
        from api_rest.services import slug_a_nombre
        nombre = slug_a_nombre(estacion_id)
        return jsonify(catalog.configuracion_estacion(nombre))

    @app.get("/api/servicios/streamlit")
    @auth_required
    def servicios_streamlit_estado():
        return jsonify(streamlit_launcher.listar_estados())

    @app.post("/api/servicios/streamlit/<modulo_id>/iniciar")
    @auth_required
    def servicios_streamlit_iniciar(modulo_id: str):
        return jsonify(streamlit_launcher.iniciar(modulo_id))

    @app.post("/api/servicios/streamlit/<modulo_id>/detener")
    @auth_required
    def servicios_streamlit_detener(modulo_id: str):
        return jsonify(streamlit_launcher.detener(modulo_id))

    @app.post("/api/servicios/streamlit/detener-todos")
    @auth_required
    def servicios_streamlit_detener_todos():
        return jsonify(streamlit_launcher.detener_todos())

    return app


app = create_app()


def main() -> None:
    # Render/Railway inyectan PORT; en local use METGO_API_PORT (8080)
    port = int(os.getenv("PORT", os.getenv("METGO_API_PORT", "8080")))
    default_host = "0.0.0.0" if os.getenv("PORT") else "127.0.0.1"
    host = os.getenv("METGO_API_HOST", default_host)
    debug = os.getenv("METGO_API_DEBUG", "0") == "1"
    auth_mode = "JWT activo" if os.getenv("METGO_API_AUTH_REQUIRED", "1") != "0" else "sin auth"
    print(f"METGO API REST -> http://{host}:{port}/api/health ({auth_mode})")
    vue_dir = "frontend/vue" if metgo_paths.LAYOUT_CAPAS else "04_Dashboards_Unificados/frontend_vue"
    print(f"Interfaz Vue    -> http://127.0.0.1:5173 (cd {vue_dir} && npm run dev)")
    print("NO abra :8080 en el navegador para la UI; ese puerto es solo la API.")
    app.run(host=host, port=port, debug=debug)


if __name__ == "__main__":
    main()
