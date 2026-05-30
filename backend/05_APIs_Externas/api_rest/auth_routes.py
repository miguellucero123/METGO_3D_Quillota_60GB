#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Rutas y decoradores JWT para la API REST."""

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


def register_auth_routes(app: Flask) -> None:
    @app.post("/api/auth/login")
    def login():
        data = request.get_json(silent=True) or {}
        username = (data.get("username") or data.get("usuario") or "").strip()
        password = data.get("password") or data.get("contraseña") or data.get("contrasena") or ""

        if not metgo_auth.verificar_credenciales(username, password):
            return jsonify({"error": "Usuario o contraseña incorrectos"}), 401

        try:
            return jsonify(metgo_auth.crear_token_acceso(username))
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.post("/api/auth/register")
    def register():
        data = request.get_json(silent=True) or {}
        username = (data.get("username") or data.get("usuario") or "").strip()
        password = data.get("password") or data.get("contraseña") or data.get("contrasena") or ""
        email = data.get("email") or data.get("correo")

        ok, msg = metgo_auth.registrar_usuario(username, password, email)
        if not ok:
            return jsonify({"error": msg}), 400

        try:
            payload = metgo_auth.crear_token_acceso(username)
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
            }
        )

    @app.post("/api/auth/refresh")
    @auth_required
    def refresh():
        try:
            return jsonify(metgo_auth.crear_token_acceso(g.current_user))
        except Exception as e:
            return jsonify({"error": str(e)}), 500
