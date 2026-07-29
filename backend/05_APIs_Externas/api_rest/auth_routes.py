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
            g.faena_id = None
            g.org_id = None
            g.plan_code = "pro"
            g.sub_status = "active"
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
        # S1: faena minera + suscripción (claims opcionales)
        g.faena_id = payload.get("faena")
        g.org_id = payload.get("org_id")
        g.plan_code = payload.get("plan_code")
        g.sub_status = payload.get("sub_status")
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
        username = (data.get("username") or data.get("usuario") or data.get("email") or "").strip()
        password = data.get("password") or data.get("contraseña") or data.get("contrasena") or ""
        sitio_req = data.get("sitio") or data.get("site")
        faena_req = (data.get("faena") or "").strip().lower() or None

        # S1: identidad comercial (email + sitio + faena)
        try:
            from api_rest.identity import identity_store, pii_crypto

            sitio_try = (sitio_req or "").strip().lower() or None
            # SPATI SPA aún declara sitio mantos_blancos: aceptar también spati
            sitios_try = []
            if sitio_try:
                sitios_try.append(sitio_try)
            if faena_req and "spati" not in sitios_try:
                sitios_try.append("spati")
            for sitio_id in sitios_try:
                user = identity_store.buscar_usuario_login(username, sitio_id, faena_req)
                if not user or not pii_crypto.verify_password(
                    password, user.get("password_hash") or ""
                ):
                    continue
                if user.get("status") == "suspended":
                    return jsonify({"error": "Usuario suspendido"}), 403
                sub = identity_store.suscripcion_de_org(user.get("org_id") or "") or {}
                return jsonify(
                    metgo_auth.crear_token_identidad(
                        sub=user.get("email_norm") or username,
                        role=user.get("role") or "operador",
                        sitio=user.get("sitio") or sitio_id,
                        faena=user.get("faena"),
                        org_id=user.get("org_id"),
                        plan_code=sub.get("plan_code") or "trial",
                        sub_status=sub.get("status") or "trialing",
                    )
                )
        except Exception:
            pass

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
        body = {
            "username": g.current_user,
            "role": g.user_role,
            "tenant": g.tenant_id,
            "sitio": getattr(g, "sitio_id", None),
            "faena": getattr(g, "faena_id", None),
            "org_id": getattr(g, "org_id", None),
            "plan_code": getattr(g, "plan_code", None),
            "sub_status": getattr(g, "sub_status", None),
        }
        org_id = getattr(g, "org_id", None)
        if org_id:
            sub = None
            try:
                from api_rest.identity import identity_store

                sub = identity_store.suscripcion_de_org(org_id)
            except Exception:
                sub = None
            if sub:
                body["plan_code"] = sub.get("plan_code") or body["plan_code"]
                body["sub_status"] = sub.get("status") or body["sub_status"]
                body["suscripcion"] = {
                    "plan_code": sub.get("plan_code"),
                    "status": sub.get("status"),
                    "current_period_end": sub.get("current_period_end"),
                    "faena": sub.get("faena"),
                }
        try:
            from api_rest.identity import identity_store

            hub = identity_store.resolver_hub_faenas(
                email=g.current_user,
                role=g.user_role,
                sitio=getattr(g, "sitio_id", None),
                faena_jwt=getattr(g, "faena_id", None),
                plan_code=body.get("plan_code"),
            )
            body["hub"] = hub
            body["multi_faena"] = bool(hub.get("multi_faena"))
            body["catalogo_completo"] = bool(hub.get("catalogo_completo"))
            body["faenas"] = hub.get("faenas") or []
        except Exception:
            body["hub"] = {
                "catalogo_completo": (g.user_role or "") == "admin",
                "multi_faena": False,
                "faenas": (
                    [{"slug": g.faena_id}] if getattr(g, "faena_id", None) else []
                ),
            }
        return jsonify(body)

    @app.post("/api/auth/refresh")
    @auth_required
    def refresh():
        try:
            if getattr(g, "org_id", None) or (
                g.current_user and "@" in str(g.current_user)
            ):
                return jsonify(
                    metgo_auth.crear_token_identidad(
                        sub=g.current_user,
                        role=g.user_role or "operador",
                        sitio=getattr(g, "sitio_id", None),
                        faena=getattr(g, "faena_id", None),
                        org_id=getattr(g, "org_id", None),
                        plan_code=getattr(g, "plan_code", None),
                        sub_status=getattr(g, "sub_status", None),
                    )
                )
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
