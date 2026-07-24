#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Rutas y decoradores JWT para la API REST (E9: claim sitio)."""

from __future__ import annotations

import os
from functools import wraps
from typing import Callable

from flask import Flask, g, jsonify, request

import metgo_auth


def auth_required(f: Callable) -> Callable:
    """Exige Authorization: Bearer <token> salvo METGO_API_AUTH_REQUIRED=0."""

    @wraps(f)
    def wrapper(*args, **kwargs):
        if os.getenv("METGO_API_AUTH_REQUIRED", "1") == "0":
            g.current_user = "anonymous"
            g.user_role = "admin"
            g.tenant_id = None
            g.sitio_id = None
            return f(*args, **kwargs)

        header = request.headers.get("Authorization", "")
        if not header.startswith("Bearer "):
            return jsonify({"error": "Token requerido"}), 401

        payload = metgo_auth.decodificar_token(header[7:].strip())
        if not payload:
            return jsonify({"error": "Token invalido o expirado"}), 401

        g.current_user = payload.get("sub")
        g.user_role = payload.get("role") or metgo_auth.rol_de_usuario(g.current_user or "")
        g.tenant_id = payload.get("tenant")
        if g.tenant_id is None and g.current_user:
            g.tenant_id = metgo_auth.tenant_de_usuario(g.current_user)

        # E9: sitio de producto (claim o membresía)
        g.sitio_id = payload.get("sitio")
        if g.sitio_id is None and "sitio" not in payload and g.current_user:
            g.sitio_id = metgo_auth.sitio_de_usuario(g.current_user)
        return f(*args, **kwargs)

    return wrapper


def requiere_rol(*roles: str) -> Callable:
    """RBAC: admin siempre pasa; otros roles deben estar en roles."""

    def decorator(f: Callable) -> Callable:
        @wraps(f)
        @auth_required
        def wrapper(*args, **kwargs):
            if not metgo_auth.rol_permitido(g.user_role or "", roles):
                return (
                    jsonify(
                        {
                            "error": "Sin permisos",
                            "role": g.user_role,
                            "requiere": list(roles),
                        }
                    ),
                    403,
                )
            return f(*args, **kwargs)

        return wrapper

    return decorator


def requiere_sitio(recurso_sitio: str | None = None) -> Callable:
    """Exige que el JWT pueda acceder al sitio del recurso (o query ?sitio=)."""

    def decorator(f: Callable) -> Callable:
        @wraps(f)
        @auth_required
        def wrapper(*args, **kwargs):
            from api_rest.sitios_auth import sitio_permitido

            target = recurso_sitio
            if target is None:
                target = kwargs.get("sitio") or request.args.get("sitio")
                if target is None and request.view_args:
                    target = request.view_args.get("sitio")
            if target and not sitio_permitido(getattr(g, "sitio_id", None), str(target)):
                return (
                    jsonify(
                        {
                            "error": "Sitio no autorizado",
                            "sitio_token": g.sitio_id,
                            "sitio_recurso": target,
                        }
                    ),
                    403,
                )
            return f(*args, **kwargs)

        return wrapper

    return decorator


def requiere_estacion(f: Callable) -> Callable:
    """Exige que la estación del path pertenezca al sitio del JWT (E9)."""

    @wraps(f)
    @auth_required
    def wrapper(*args, **kwargs):
        from api_rest.sitios_auth import estacion_permitida

        estacion_id = kwargs.get("estacion_id")
        if estacion_id is None and request.view_args:
            estacion_id = request.view_args.get("estacion_id")
        if estacion_id and not estacion_permitida(getattr(g, "sitio_id", None), str(estacion_id)):
            return (
                jsonify(
                    {
                        "error": "Estación fuera del sitio autorizado",
                        "sitio_token": g.sitio_id,
                        "estacion_id": estacion_id,
                    }
                ),
                403,
            )
        return f(*args, **kwargs)

    return wrapper


def register_auth_routes(app: Flask) -> None:
    @app.post("/api/auth/login")
    def login():
        data = request.get_json(silent=True) or {}
        username = (data.get("username") or data.get("usuario") or "").strip()
        password = data.get("password") or data.get("contraseña") or data.get("contrasena") or ""
        sitio_req = data.get("sitio") or data.get("site")

        if not metgo_auth.verificar_credenciales(username, password):
            return jsonify({"error": "Usuario o contraseña incorrectos"}), 401

        try:
            from api_rest.sitios_auth import resolver_sitio_login

            sitio, err = resolver_sitio_login(username, sitio_req)
            if err:
                return jsonify({"error": err}), 403
            return jsonify(metgo_auth.crear_token_acceso(username, sitio=sitio))
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.post("/api/auth/register")
    def register():
        data = request.get_json(silent=True) or {}
        username = (data.get("username") or data.get("usuario") or "").strip()
        password = data.get("password") or data.get("contraseña") or data.get("contrasena") or ""
        email = data.get("email") or data.get("correo")
        sitio = data.get("sitio") or data.get("site")

        ok, msg = metgo_auth.registrar_usuario(username, password, email, sitio=sitio)
        if not ok:
            return jsonify({"error": msg}), 400

        try:
            sitio_tok = metgo_auth.sitio_de_usuario(username)
            payload = metgo_auth.crear_token_acceso(username, sitio=sitio_tok)
            payload["message"] = msg
            return jsonify(payload), 201
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.get("/api/auth/me")
    @auth_required
    def me():
        return jsonify(
            {
                "username": g.current_user,
                "role": g.user_role,
                "tenant": g.tenant_id,
                "sitio": getattr(g, "sitio_id", None),
            }
        )

    @app.post("/api/auth/refresh")
    @auth_required
    def refresh():
        try:
            return jsonify(
                metgo_auth.crear_token_acceso(
                    g.current_user, sitio=getattr(g, "sitio_id", None)
                )
            )
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.get("/api/public/sitios-auth")
    def public_sitios_auth():
        """Catálogo de sitios disponibles para login (sin secretos)."""
        from api_rest.sitios_auth import listar_sitios_auth

        return jsonify(listar_sitios_auth(incluir_plantilla=False))

    @app.get("/api/me/preferencias")
    @auth_required
    def get_preferencias():
        from api_rest.integracion import preferencias_store

        sitio = request.args.get("sitio") or getattr(g, "sitio_id", None) or "quillota"
        from api_rest.sitios_auth import sitio_permitido

        if not sitio_permitido(getattr(g, "sitio_id", None), sitio):
            return jsonify({"error": "Sitio no autorizado"}), 403
        data = preferencias_store.leer(g.current_user, sitio)
        return jsonify(data)

    @app.put("/api/me/preferencias")
    @auth_required
    def put_preferencias():
        from api_rest.integracion import preferencias_store
        from api_rest.sitios_auth import sitio_permitido

        body = request.get_json(silent=True) or {}
        sitio = body.get("sitio") or getattr(g, "sitio_id", None) or "quillota"
        if not sitio_permitido(getattr(g, "sitio_id", None), sitio):
            return jsonify({"error": "Sitio no autorizado"}), 403
        prefs = body.get("prefs") if isinstance(body.get("prefs"), dict) else body.get("preferencias")
        favorites = body.get("favorites") if isinstance(body.get("favorites"), list) else body.get("favoritos")
        if prefs is None and "prefs" not in body and favorites is None:
            # Permitir body plano como prefs
            prefs = {k: v for k, v in body.items() if k not in ("sitio", "favorites", "favoritos")}
        ok = preferencias_store.guardar(
            g.current_user,
            sitio,
            prefs=prefs if isinstance(prefs, dict) else None,
            favorites=favorites if isinstance(favorites, list) else None,
        )
        if not ok:
            return jsonify({"error": "No se pudieron guardar preferencias (Supabase?)"}), 503
        return jsonify(preferencias_store.leer(g.current_user, sitio))
