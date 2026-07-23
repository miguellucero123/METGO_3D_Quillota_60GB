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

from flask import Flask, g, jsonify, request
from flask_cors import CORS

from api_rest import catalog, services, streamlit_launcher
from api_rest.alertas_config import generar_alertas_combinadas
from api_rest.alertas_routes import register_alertas_routes
from api_rest.auth_routes import auth_required, register_auth_routes, requiere_rol
from api_rest.docs_routes import register_docs_routes
from api_rest.health import build_health_payload
from api_rest.fase3_routes import register_fase3_routes
from api_rest.fase4_routes import register_fase4_routes
from api_rest.fase7_routes import register_fase7_routes
from api_rest.fase8_routes import register_fase8_routes
from api_rest.fase9_routes import register_fase9_routes
from api_rest.fase10_routes import register_fase10_routes
from api_rest.aire_routes import register_aire_routes
from api_rest.precipitacion_routes import register_precipitacion_routes
from api_rest.meteo_avanzada_routes import register_meteo_avanzada_routes
from api_rest.mapas_routes import register_mapas_routes
from api_rest.observability import register_observability


def create_app() -> Flask:
    app = Flask(__name__)
    CORS(
        app,
        resources={r"/api/*": {"origins": os.getenv("METGO_CORS_ORIGINS", "*").split(",")}},
        supports_credentials=True,
    )

    register_observability(app)
    register_auth_routes(app)
    register_alertas_routes(app)
    register_fase3_routes(app)
    register_fase4_routes(app)
    register_fase7_routes(app)
    register_fase8_routes(app)
    register_fase9_routes(app)
    register_fase10_routes(app)
    register_aire_routes(app)
    register_precipitacion_routes(app)
    register_meteo_avanzada_routes(app)
    register_mapas_routes(app)
    register_docs_routes(app)

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
                    "docs": "/api/docs",
                    "login": "POST /api/auth/login",
                    "public_sitios": "/api/public/sitios",
                    "public_estaciones": "/api/public/estaciones",
                    "public_meteo": "/api/public/meteo/<estacion_id>",
                    "public_aire": "/api/public/aire/<estacion_id>",
                },
            }
        )

    @app.get("/api/health")
    def health():
        return jsonify(build_health_payload(services.health_check))

    @app.get("/api/public/sitios")
    def public_sitios():
        """Catálogo de sitios METGO (solo lectura, sin JWT)."""
        incluir = request.args.get("incluir_plantilla", "1") not in ("0", "false", "False")
        return jsonify(services.listar_sitios(incluir_plantilla=incluir))

    @app.get("/api/public/estaciones")
    def public_estaciones():
        """Estaciones por sitio (solo lectura, sin JWT). Query: sitio=quillota|paine|demo."""
        sitio = request.args.get("sitio")
        return jsonify(services.listar_estaciones(sitio=sitio))

    @app.get("/api/public/meteo/<estacion_id>")
    def public_meteo(estacion_id: str):
        """Resumen meteorológico público (solo lectura, sin JWT)."""
        key = estacion_id.lower().replace("-", "_")
        if key not in services.SLUG_A_NOMBRE:
            return jsonify({"error": "No encontrado", "estacion_id": estacion_id}), 404

        try:
            data = services.resumen_meteo(estacion_id)
        except Exception as exc:
            app.logger.warning("public_meteo %s error: %s", estacion_id, exc)
            return jsonify({"error": "Servicio de OpenMeteo temporalmente no disponible"}), 503
            
        if data is None:
            return jsonify({"error": "Servicio de OpenMeteo temporalmente no disponible"}), 503
        return jsonify(data)

    @app.get("/api/public/meteo/<estacion_id>/pronostico")
    def public_meteo_pronostico(estacion_id: str):
        """Pronóstico diario público (Paine / demos sin JWT)."""
        key = estacion_id.lower().replace("-", "_")
        if key not in services.SLUG_A_NOMBRE:
            return jsonify({"error": "No encontrado", "estacion_id": estacion_id}), 404
        dias = request.args.get("dias", 7, type=int)
        try:
            data = services.pronostico_meteo(estacion_id, dias)
        except Exception as exc:
            app.logger.warning("public_meteo_pronostico %s error: %s", estacion_id, exc)
            return jsonify({"error": "Servicio de OpenMeteo temporalmente no disponible"}), 503
        if data is None:
            return jsonify({"error": "Servicio de OpenMeteo temporalmente no disponible"}), 503
        return jsonify(data)

    @app.get("/api/sitios")
    @auth_required
    def sitios():
        incluir = request.args.get("incluir_plantilla", "1") not in ("0", "false", "False")
        return jsonify(services.listar_sitios(incluir_plantilla=incluir))

    @app.get("/api/estaciones")
    @auth_required
    def estaciones():
        sitio = request.args.get("sitio")
        return jsonify(
            services.listar_estaciones(getattr(g, "tenant_id", None), sitio=sitio)
        )
    @app.get("/api/meteo/<estacion_id>")
    @auth_required
    def meteo_resumen(estacion_id: str):
        key = estacion_id.lower().replace("-", "_")
        if key not in services.SLUG_A_NOMBRE:
            return jsonify({"error": "Estación no encontrada", "estacion_id": estacion_id}), 404

        tipo = request.args.get("tipo", "pronostico")
        try:
            if tipo == "historico":
                hist = services.historico_meteo(estacion_id, 7)
                data = hist[-1] if hist else None
            else:
                data = services.resumen_meteo(estacion_id)
        except Exception as exc:
            app.logger.warning("meteo_resumen %s error: %s", estacion_id, exc)
            return jsonify({"error": "Servicio de OpenMeteo temporalmente no disponible"}), 503
        if data is None:
            return jsonify({"error": "Servicio de OpenMeteo temporalmente no disponible"}), 503
        return jsonify(data)

    @app.get("/api/meteo/<estacion_id>/pronostico")
    @auth_required
    def meteo_pronostico(estacion_id: str):
        key = estacion_id.lower().replace("-", "_")
        if key not in services.SLUG_A_NOMBRE:
            return jsonify({"error": "Estación no encontrada", "estacion_id": estacion_id}), 404
        dias = request.args.get("dias", 7, type=int)
        try:
            data = services.pronostico_meteo(estacion_id, dias)
        except Exception as exc:
            app.logger.warning("meteo_pronostico %s error: %s", estacion_id, exc)
            return jsonify({"error": "Servicio de OpenMeteo temporalmente no disponible"}), 503
        if data is None:
            return jsonify({"error": "Servicio de OpenMeteo temporalmente no disponible"}), 503
        return jsonify(data)

    @app.get("/api/meteo/<estacion_id>/viento-horario")
    @auth_required
    def meteo_viento_horario(estacion_id: str):
        dias = request.args.get("dias", 7, type=int)
        data = services.viento_horario_meteo(estacion_id, dias)
        if not data:
            return jsonify({"error": "Servicio de OpenMeteo temporalmente no disponible"}), 503
        return jsonify(data)

    @app.get("/api/meteo/<estacion_id>/historico")
    @auth_required
    def meteo_historico(estacion_id: str):
        """Histórico diario. dias>92 lee solo del store (ETL Archive). Lista (contrato Vue)."""
        dias = request.args.get("dias", 30, type=int)
        dias = max(1, min(int(dias or 30), 3650))
        data = services.historico_meteo(estacion_id, dias)
        if data is None:
            return jsonify({"error": "Servicio de OpenMeteo temporalmente no disponible"}), 503
        return jsonify(data)

    @app.get("/api/alertas")
    @auth_required
    def alertas():
        estacion_id = request.args.get("estacion")
        return jsonify(generar_alertas_combinadas(estacion_id))

    @app.get("/api/meteo/comparativo")
    @auth_required
    def meteo_comparativo():
        return jsonify(services.comparativo_estaciones(getattr(g, "tenant_id", None)))

    @app.get("/api/meteo/comparativo/historico")
    @auth_required
    def meteo_comparativo_historico():
        dias = request.args.get("dias", 14, type=int)
        return jsonify(
            services.comparativo_historico(dias, getattr(g, "tenant_id", None))
        )

    @app.get("/api/metricas/globales")
    @auth_required
    def metricas_globales():
        return jsonify(services.metricas_globales(getattr(g, "tenant_id", None)))

    @app.get("/api/agricola/<estacion_id>")
    @auth_required
    def agricola(estacion_id: str):
        return jsonify(services.recomendaciones_agricolas(estacion_id))

    @app.get("/api/sistema/resumen")
    @auth_required
    def sistema_resumen():
        return jsonify(catalog.resumen_sistema())

    @app.get("/api/catalogo")
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
    @requiere_rol("admin", "operador")
    def servicios_streamlit_iniciar(modulo_id: str):
        return jsonify(streamlit_launcher.iniciar(modulo_id))

    @app.post("/api/servicios/streamlit/<modulo_id>/detener")
    @requiere_rol("admin", "operador")
    def servicios_streamlit_detener(modulo_id: str):
        return jsonify(streamlit_launcher.detener(modulo_id))

    @app.post("/api/servicios/streamlit/detener-todos")
    @requiere_rol("admin")
    def servicios_streamlit_detener_todos():
        return jsonify(streamlit_launcher.detener_todos())

    @app.get("/api/servicios/streamlit/<modulo_id>/visor")
    @auth_required
    def servicios_streamlit_visor(modulo_id: str):
        return jsonify(streamlit_launcher.url_visor_modulo(modulo_id))

    return app


app = create_app()


def ml_bootstrap() -> None:
    """Entrena/sincroniza modelos al arrancar (usado por main() y por gunicorn)."""
    if os.getenv("METGO_ML_AUTO_TRAIN", "1").lower() in ("0", "false", "no"):
        return
    try:
        from api_rest.integracion.ml_train_runner import ensure_modelos_servibles

        boot = ensure_modelos_servibles()
        if boot and boot.get("ok"):
            print(
                f"ML bootstrap: {boot.get('entrenados', 0)} modelos entrenados "
                f"({boot.get('origen_datos', '?')}), servibles={boot.get('registry_servibles')}"
            )
        elif boot and boot.get("error"):
            print(f"ML bootstrap omitido: {boot['error']}")
        from api_rest.integracion import ml_registry

        reg = ml_registry.sincronizar_registro()
        print(f"ML registry: {reg.get('servibles', 0)}/{reg.get('total', 0)} servibles (legacy_scan={reg.get('legacy_scan')})")
    except Exception as exc:
        print(f"ML bootstrap omitido: {exc}")


def main() -> None:
    # Render/Railway inyectan PORT; en local use METGO_API_PORT (8080)
    ml_bootstrap()

    port = int(os.getenv("PORT", os.getenv("METGO_API_PORT", "8080")))
    default_host = "0.0.0.0" if os.getenv("PORT") else "127.0.0.1"
    host = os.getenv("METGO_API_HOST", default_host)
    debug = os.getenv("METGO_API_DEBUG", "0") == "1"
    auth_mode = "JWT activo" if os.getenv("METGO_API_AUTH_REQUIRED", "1") != "0" else "sin auth"
    print(f"METGO API REST -> http://{host}:{port}/api/health ({auth_mode})")
    vue_dir = "frontend/vue" if metgo_paths.LAYOUT_CAPAS else "04_Dashboards_Unificados/frontend_vue"
    print(f"Interfaz Vue    -> http://127.0.0.1:5173 (cd {vue_dir} && npm run dev)")
    print("NO abra :8080 en el navegador para la UI; ese puerto es solo la API.")
    # threaded=True: sin esto, una llamada lenta a OpenMeteo bloquea todas las
    # demás peticiones del SPA (en Render el proxy las corta sin cabeceras CORS).
    app.run(host=host, port=port, debug=debug, threaded=True)


if __name__ == "__main__":
    main()
