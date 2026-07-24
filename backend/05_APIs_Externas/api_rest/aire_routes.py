#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Rutas calidad del aire (E7 — Copiapó). Contrato en openapi.yaml."""

from __future__ import annotations

from flask import Flask, jsonify, request

from api_rest import aire_service, dispersion_service
from api_rest.auth_routes import requiere_estacion

_ERROR_503 = {"error": "Servicio de calidad del aire temporalmente no disponible"}


def _responder(data, estacion_id: str):
    if data is None:
        if aire_service._coords_de(estacion_id) is None:
            return jsonify({"error": "Estación no encontrada", "estacion_id": estacion_id}), 404
        return jsonify(_ERROR_503), 503
    return jsonify(data)


def register_aire_routes(app: Flask) -> None:
    @app.get("/api/public/aire/<estacion_id>")
    def public_aire_actual(estacion_id: str):
        """Calidad del aire actual (CAMS) + ICAP, sin JWT."""
        try:
            data = aire_service.aire_actual(estacion_id)
        except Exception as exc:
            app.logger.warning("public_aire %s error: %s", estacion_id, exc)
            return jsonify(_ERROR_503), 503
        return _responder(data, estacion_id)

    @app.get("/api/public/aire/<estacion_id>/pronostico")
    def public_aire_pronostico(estacion_id: str):
        dias = max(1, min(request.args.get("dias", default=5, type=int), 7))
        try:
            data = aire_service.aire_pronostico(estacion_id, dias)
        except Exception as exc:
            app.logger.warning("public_aire_pronostico %s error: %s", estacion_id, exc)
            return jsonify(_ERROR_503), 503
        return _responder(data, estacion_id)

    @app.get("/api/public/aire/<estacion_id>/historico")
    def public_aire_historico(estacion_id: str):
        dias = max(1, min(request.args.get("dias", default=7, type=int), 92))
        try:
            data = aire_service.aire_historico(estacion_id, dias)
        except Exception as exc:
            app.logger.warning("public_aire_historico %s error: %s", estacion_id, exc)
            return jsonify(_ERROR_503), 503
        return _responder(data, estacion_id)

    @app.get("/api/public/aire/alertas")
    def public_aire_alertas():
        """Alertas de salud por umbral ICAP para un sitio (por defecto Copiapó)."""
        sitio = (request.args.get("sitio") or "copiapo").strip().lower()
        try:
            return jsonify(aire_service.alertas_aire(sitio))
        except Exception as exc:
            app.logger.warning("public_aire_alertas %s error: %s", sitio, exc)
            return jsonify(_ERROR_503), 503

    @app.get("/api/public/aire/sinca/estado")
    def public_sinca_estado():
        """Estado de la integración SINCA (observado MMA) — stub E7/E12."""
        try:
            from api_rest import sinca_service

            return jsonify(sinca_service.estado_sinca())
        except Exception as exc:
            app.logger.warning("sinca_estado error: %s", exc)
            return jsonify(_ERROR_503), 503

    @app.get("/api/public/aire/sinca/sesgo")
    def public_sinca_sesgo():
        """Sesgo CAMS(modelo) − SINCA(observado) por estación (E12)."""
        estacion_id = (request.args.get("estacion_id") or "copiapo_centro").strip()
        dias = max(1, min(request.args.get("dias", default=14, type=int), 92))
        try:
            from api_rest import sinca_service

            data = sinca_service.sesgo_cams_vs_sinca(estacion_id, dias=dias)
            if data.get("error") == "estacion_no_en_catalogo_sinca":
                return jsonify(data), 404
            return jsonify(data)
        except Exception as exc:
            app.logger.warning("sinca_sesgo error: %s", exc)
            return jsonify(_ERROR_503), 503

    @app.get("/api/public/ml/dominios")
    def public_ml_dominios():
        """Catálogo stubs ML por dominio (E12)."""
        sitio = (request.args.get("sitio") or "").strip().lower() or None
        try:
            from api_rest import ml_domain_service

            return jsonify(ml_domain_service.listar_modelos_dominio(sitio))
        except Exception as exc:
            app.logger.warning("ml_dominios error: %s", exc)
            return jsonify(_ERROR_503), 503

    @app.get("/api/public/ml/dominios/<modelo_id>/prediccion")
    def public_ml_dominio_prediccion(modelo_id: str):
        """Predicción por dominio (PM10 sklearn / viento baseline / stubs)."""
        estacion_id = (request.args.get("estacion_id") or "copiapo_centro").strip()
        viento_ms = request.args.get("viento_ms", type=float)
        try:
            from api_rest import ml_domain_service

            data = ml_domain_service.prediccion_dominio(
                modelo_id, estacion_id=estacion_id, viento_ms=viento_ms
            )
            if data.get("error") == "modelo_dominio_desconocido":
                return jsonify(data), 404
            return jsonify(data)
        except Exception as exc:
            app.logger.warning("ml_dominio_prediccion error: %s", exc)
            return jsonify(_ERROR_503), 503

    # ---------------------------------------------------- dispersión de contaminantes

    @app.get("/api/public/aire/dispersion/alertas")
    def public_dispersion_alertas():
        """Alertas de mala dispersión por horizonte (horaria|diaria|proyeccion)."""
        sitio = (request.args.get("sitio") or "copiapo").strip().lower()
        horizonte = (request.args.get("horizonte") or "horaria").strip().lower()
        if horizonte not in ("horaria", "diaria", "proyeccion"):
            horizonte = "horaria"
        try:
            return jsonify(dispersion_service.alertas_dispersion(sitio, horizonte))
        except Exception as exc:
            app.logger.warning("dispersion_alertas %s error: %s", sitio, exc)
            return jsonify(_ERROR_503), 503

    @app.get("/api/public/aire/<estacion_id>/dispersion")
    def public_dispersion_horaria(estacion_id: str):
        """Serie horaria de dispersión: inversión, viento, capa límite, niebla (24/48/72 h)."""
        horas = max(1, min(request.args.get("horas", default=72, type=int), 168))
        try:
            data = dispersion_service.dispersion_horaria(estacion_id, horas)
        except Exception as exc:
            app.logger.warning("dispersion_horaria %s error: %s", estacion_id, exc)
            return jsonify(_ERROR_503), 503
        return _responder(data, estacion_id)

    @app.get("/api/public/aire/<estacion_id>/dispersion/diaria")
    def public_dispersion_diaria(estacion_id: str):
        dias = max(1, min(request.args.get("dias", default=7, type=int), 16))
        try:
            data = dispersion_service.dispersion_diaria(estacion_id, dias)
        except Exception as exc:
            app.logger.warning("dispersion_diaria %s error: %s", estacion_id, exc)
            return jsonify(_ERROR_503), 503
        return _responder(data, estacion_id)

    @app.get("/api/public/aire/<estacion_id>/dispersion/proyeccion")
    def public_dispersion_proyeccion(estacion_id: str):
        """Proyección climatológica 16-30 días (baja confianza)."""
        try:
            data = dispersion_service.dispersion_proyeccion(estacion_id)
        except Exception as exc:
            app.logger.warning("dispersion_proyeccion %s error: %s", estacion_id, exc)
            return jsonify(_ERROR_503), 503
        return _responder(data, estacion_id)

    @app.get("/api/aire/<estacion_id>")
    @requiere_estacion
    def aire_actual_auth(estacion_id: str):
        try:
            data = aire_service.aire_actual(estacion_id)
        except Exception as exc:
            app.logger.warning("aire %s error: %s", estacion_id, exc)
            return jsonify(_ERROR_503), 503
        return _responder(data, estacion_id)
