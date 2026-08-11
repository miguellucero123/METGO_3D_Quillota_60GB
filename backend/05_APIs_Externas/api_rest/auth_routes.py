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
        g.jti = payload.get("jti")

        # Sesión única: solo el jti más reciente es válido (+ idle opcional)
        try:
            from api_rest.identity.session_store import is_session_active, touch_session

            if g.current_user and not is_session_active(str(g.current_user), g.jti):
                return (
                    jsonify(
                        {
                            "error": "Sesión iniciada en otro dispositivo o inactiva",
                            "code": "session_replaced",
                        }
                    ),
                    401,
                )
            if g.current_user and g.jti:
                touch_session(str(g.current_user), g.jti)
        except Exception:
            pass
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
        from api_rest import security_hardening as sec

        ok_rl, meta = sec.check_rate_limit("auth_login", limit=20, window_s=60)
        if not ok_rl:
            return sec.rate_limit_response(meta)

        data = request.get_json(silent=True) or {}
        username = (data.get("username") or data.get("usuario") or data.get("email") or "").strip()
        password = data.get("password") or data.get("contraseña") or data.get("contrasena") or ""
        sitio_req = data.get("sitio") or data.get("site")
        faena_req = (data.get("faena") or "").strip().lower() or None

        # Control de fuerza bruta con el nuevo servicio
        from api_rest.domain_services.auth_service import auth_service
        ip_address = request.remote_addr or "unknown"
        is_allowed, error_msg = auth_service.check_brute_force(username, ip_address)
        if not is_allowed:
            return jsonify({"error": error_msg, "code": "brute_force_blocked"}), 429

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
                require_verify = (
                    os.getenv("METGO_REQUIRE_EMAIL_VERIFY", "1").strip().lower()
                    not in ("0", "false", "no", "off")
                )
                if require_verify and not user.get("email_verified_at"):
                    return (
                        jsonify(
                            {
                                "error": (
                                    "Debe verificar su email antes de iniciar sesión. "
                                    "Revise su correo (y spam) o solicite reenvío."
                                ),
                                "code": "email_not_verified",
                            }
                        ),
                        403,
                    )
                sub_raw = identity_store.suscripcion_de_org(user.get("org_id") or "") or {}
                sub = identity_store.suscripcion_efectiva(sub_raw)
                if sub.get("status") not in ("trialing", "active"):
                    return (
                        jsonify(
                            {
                                "error": "Acceso expirado o cancelado. El piloto de 15 días terminó o la suscripción no está activa.",
                                "code": "subscription_expired",
                                "plan_code": sub.get("plan_code"),
                            }
                        ),
                        403,
                    )
                rem = identity_store.segundos_restantes_suscripcion(sub_raw)
                token_kwargs = {
                    "sub": user.get("email_norm") or username,
                    "role": user.get("role") or "operador",
                    "sitio": user.get("sitio") or sitio_id,
                    "faena": user.get("faena"),
                    "org_id": user.get("org_id"),
                    "plan_code": sub.get("plan_code") or "trial",
                    "sub_status": sub.get("status") or "trialing",
                }
                if rem is not None and (sub.get("plan_code") == "preview" or rem < 3600):
                    token_kwargs["expires_in"] = max(60, rem)
                
                auth_service.record_successful_login(username)
                return jsonify(metgo_auth.crear_token_identidad(**token_kwargs))
        except Exception:
            pass

        if not metgo_auth.verificar_credenciales(username, password):
            auth_service.record_failed_login(username, ip_address)
            return jsonify({"error": "Usuario o contraseña incorrectos"}), 401

        try:
            from api_rest.sitios_auth import resolver_sitio_login

            sitio, err = resolver_sitio_login(username, sitio_req)
            if err:
                return jsonify({"error": err}), 403
            
            auth_service.record_successful_login(username)
            return jsonify(metgo_auth.crear_token_acceso(username, sitio=sitio))
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.post("/api/public/leads")
    def create_lead():
        """Recibe prospectos comerciales (demo/cotización) desde la SPA Vue y los guarda en Supabase."""
        from api_rest import security_hardening as sec
        from api_rest.integracion.supabase_store import get_supabase_client, rest_insert
        from datetime import datetime

        ok_rl, meta = sec.check_rate_limit("public_leads", limit=10, window_s=3600)
        if not ok_rl:
            return sec.rate_limit_response(meta)

        data = request.get_json(silent=True) or {}
        email = (data.get("email") or "").strip().lower()
        if not email:
            return jsonify({"error": "El email es requerido"}), 400
            
        # Pydantic validation
        from api_rest.schemas import LeadCaptureRequest
        try:
            lead_validated = LeadCaptureRequest(**data)
        except Exception as e:
            return jsonify({"error": "Datos inválidos", "detail": str(e)}), 400

        row = {
            "first_name": lead_validated.first_name,
            "last_name": lead_validated.last_name,
            "company_name": lead_validated.company_name,
            "sector": lead_validated.sector,
            "email": lead_validated.email,
            "phone": lead_validated.phone,
            "whatsapp": lead_validated.whatsapp,
            "notes": lead_validated.message,
            "source": lead_validated.source,
            "created_at": datetime.utcnow().isoformat() + "Z"
        }

        try:
            client = get_supabase_client()
            if client:
                res = client.table("leads").insert(row).execute()
                if not res.data:
                    return jsonify({"error": "Error al guardar prospecto"}), 500
            else:
                inserted = rest_insert("leads", row)
                if not inserted:
                    return jsonify({"error": "Error de conexión con la base de datos"}), 500

            # Aviso comercial (no bloquea si SMTP falla)
            try:
                from api_rest.identity import email_notify

                dest = (
                    (os.getenv("METGO_LEADS_TO") or "").strip()
                    or "miguel.lucero@metgo3d.com"
                )
                body = (
                    f"Nuevo lead METGO\n"
                    f"Nombre: {row.get('first_name')} {row.get('last_name')}\n"
                    f"Empresa: {row.get('company_name')}\n"
                    f"Sector: {row.get('sector')}\n"
                    f"Email: {row.get('email')}\n"
                    f"Tel: {row.get('phone') or row.get('whatsapp')}\n"
                    f"Notas: {row.get('notes')}\n"
                    f"Fuente: {row.get('source')}\n"
                )
                email_notify.enviar_texto(
                    to_email=dest,
                    subject=f"[METGO lead] {row.get('company_name') or row.get('email')}",
                    body=body,
                )
            except Exception as mail_exc:
                app.logger.warning("Lead guardado pero email no enviado: %s", mail_exc)

            return jsonify({"status": "ok", "message": "Lead registrado exitosamente"}), 201
        except Exception as e:
            app.logger.error("Error al registrar lead: %s", e)
            return jsonify({"error": "Error interno del servidor"}), 500

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
            
        # Enviar email bienvenida
        try:
            from api_rest.domain_services.email_service import email_service
            email_service.send_welcome_email(user_email=email, user_name=username)
        except Exception as e:
            app.logger.error(f"Failed to send welcome email: {e}")

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
