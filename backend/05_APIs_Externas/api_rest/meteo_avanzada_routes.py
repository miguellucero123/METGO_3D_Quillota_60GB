#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Rutas REST de meteorología avanzada."""

from __future__ import annotations

import logging

from flask import jsonify, request

from api_rest.auth_routes import auth_required
from api_rest.meteo_avanzado_core import (
    analisis_nubosidad,
    pronostico_helada_avanzado,
    pronostico_niebla,
    validar_estacion,
    variables_meteo_completas,
)
from api_rest.meteo_variables import catalogo_variables
from api_rest.services import serie_helada_madrugada_meteo

logger = logging.getLogger(__name__)


def register_meteo_avanzada_routes(app) -> None:
    @app.get("/api/meteo/variables-catalogo")
    @auth_required
    def meteo_variables_catalogo():
        return jsonify(catalogo_variables())

    @app.get("/api/meteo/<estacion_id>/helada")
    @auth_required
    def meteo_helada_avanzada(estacion_id: str):
        try:
            validar_estacion(estacion_id)
            dias = request.args.get("dias", 7, type=int)
            cultivo = request.args.get("cultivo", "palto")
            return jsonify(pronostico_helada_avanzado(estacion_id, dias, cultivo))
        except ValueError as e:
            return jsonify({"error": str(e)}), 404
        except Exception as e:
            logger.exception("Error helada avanzada: %s", e)
            return jsonify({"error": "Error interno"}), 500

    @app.get("/api/meteo/<estacion_id>/helada-madrugada")
    @auth_required
    def meteo_helada_madrugada(estacion_id: str):
        try:
            validar_estacion(estacion_id)
            dias = request.args.get("dias", 7, type=int)
            data = serie_helada_madrugada_meteo(estacion_id, dias)
            return jsonify(data or {})
        except ValueError as e:
            return jsonify({"error": str(e)}), 404
        except Exception as e:
            logger.exception("Error helada madrugada: %s", e)
            return jsonify({"error": "Error interno"}), 500

    @app.get("/api/meteo/<estacion_id>/nubosidad")
    @auth_required
    def meteo_nubosidad(estacion_id: str):
        try:
            validar_estacion(estacion_id)
            dias = request.args.get("dias", 7, type=int)
            return jsonify(analisis_nubosidad(estacion_id, dias))
        except ValueError as e:
            return jsonify({"error": str(e)}), 404
        except Exception as e:
            logger.exception("Error nubosidad: %s", e)
            return jsonify({"error": "Error interno"}), 500

    @app.get("/api/meteo/<estacion_id>/niebla")
    @auth_required
    def meteo_niebla(estacion_id: str):
        try:
            validar_estacion(estacion_id)
            dias = request.args.get("dias", 7, type=int)
            return jsonify(pronostico_niebla(estacion_id, dias))
        except ValueError as e:
            return jsonify({"error": str(e)}), 404
        except Exception as e:
            logger.exception("Error niebla: %s", e)
            return jsonify({"error": "Error interno"}), 500

    @app.get("/api/meteo/<estacion_id>/variables-completas")
    @auth_required
    def meteo_variables_completas(estacion_id: str):
        try:
            validar_estacion(estacion_id)
            dias = request.args.get("dias", 7, type=int)
            return jsonify(variables_meteo_completas(estacion_id, dias))
        except ValueError as e:
            return jsonify({"error": str(e)}), 404
        except Exception as e:
            logger.exception("Error variables completas: %s", e)
            return jsonify({"error": "Error interno"}), 500
