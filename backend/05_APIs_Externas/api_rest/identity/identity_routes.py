#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Rutas identidad comercial S1/S2: registro, verify, access, billing, cuenta."""

from __future__ import annotations

import os

from flask import Flask, g, jsonify, request

from api_rest.auth_routes import auth_required
from api_rest.identity import identity_store, plans_catalog, validators


def _public_spa_base(sitio: str) -> str:
    """URL pública del SPA por producto (verify-email / deep links)."""
    s = (sitio or "").strip().lower() or "quillota"
    defaults = {
        "spati": ("METGO_SPATI_PUBLIC_URL", "https://metgo-spati.pages.dev"),
        "quillota": ("METGO_QUILLOTA_PUBLIC_URL", "https://metgo-quillota.pages.dev"),
        "copiapo": ("METGO_COPIAPO_PUBLIC_URL", "https://metgo-copiapo.pages.dev"),
        "mantos_blancos": ("METGO_MANTOS_PUBLIC_URL", "https://metgo-mantos.pages.dev"),
        "paine": ("METGO_PAINE_PUBLIC_URL", "https://metgo-paine.pages.dev"),
    }
    env_key, fallback = defaults.get(s, ("METGO_PUBLIC_APP_URL", ""))
    raw = (os.getenv(env_key) or "").strip()
    if not raw and env_key != "METGO_PUBLIC_APP_URL":
        raw = (os.getenv("METGO_PUBLIC_APP_URL") or "").strip()
    if not raw and s == "quillota":
        raw = (os.getenv("METGO_VUE_URL") or "").strip()
    return (raw or fallback).rstrip("/")


def _verify_email_url(sitio: str, faena: str | None, token: str) -> str:
    base = _public_spa_base(sitio)
    if not base or not token:
        return ""
    if sitio == "spati" and faena:
        return f"{base}/f/{faena}/verificar?token={token}"
    return f"{base}/verificar?token={token}"


def register_identity_routes(app: Flask) -> None:
    @app.get("/api/public/security-config")
    def public_security_config():
        """Config pública anti-abuso (site key Turnstile; sin secretos)."""
        from api_rest import security_hardening as sec

        return jsonify(sec.security_public_config())

    @app.post("/api/auth/validate-registro")
    def validate_registro():
        from api_rest import security_hardening as sec

        ok_rl, meta = sec.check_rate_limit("auth_validate", limit=30, window_s=60)
        if not ok_rl:
            return sec.rate_limit_response(meta)
        data = request.get_json(silent=True) or {}
        result = validators.validate_registro_payload(data)
        return jsonify(result), (200 if result["ok"] else 400)

    @app.post("/api/auth/register-v2")
    def register_v2():
        from api_rest import security_hardening as sec

        data = request.get_json(silent=True) or {}
        ip = request.headers.get("X-Forwarded-For", request.remote_addr)
        ok_rl, meta = sec.check_rate_limit("auth_register", limit=5, window_s=60, key=ip)
        if not ok_rl:
            return sec.rate_limit_response(meta)
        email_key = (data.get("email") or "").strip().lower()
        if email_key:
            ok_em, meta_em = sec.check_rate_limit(
                "auth_register_email", limit=3, window_s=3600, key=email_key
            )
            if not ok_em:
                return sec.rate_limit_response(meta_em)

        captcha_tok = (
            data.get("turnstile_token")
            or data.get("cf_turnstile_response")
            or data.get("captcha_token")
        )
        ok_cap, cap_msg = sec.verify_turnstile(captcha_tok, remoteip=sec.client_ip())
        if not ok_cap:
            return jsonify({"error": cap_msg, "code": "captcha_failed"}), 400

        ok, msg, extra = identity_store.registrar_v2(data, ip=ip)
        if not ok:
            body = {"error": msg}
            if extra:
                body.update(extra)
            return jsonify(body), 400

        # Enlace de verificación (SPA por sitio)
        token = (extra or {}).get("verify_token")
        faena = (extra or {}).get("faena")
        sitio = (extra or {}).get("sitio") or data.get("sitio") or "quillota"
        spa_base = _public_spa_base(str(sitio))
        if token and spa_base:
            verify_url = _verify_email_url(str(sitio), faena, token)
            if verify_url:
                extra["verify_url"] = verify_url
                try:
                    from api_rest.identity import email_notify

                    mail = email_notify.enviar_verificacion(
                        to_email=str(data.get("email") or ""),
                        verify_url=verify_url,
                        sitio=str(sitio),
                        faena=faena,
                        trial_days=int((extra or {}).get("trial_days") or plans_catalog.trial_days()),
                    )
                    extra["email"] = mail
                except Exception as exc:
                    extra["email"] = {"mode": "error", "sent": False, "error": str(exc)}
            else:
                extra["email"] = {"mode": "skip", "sent": False, "reason": "verify_url_empty"}
        else:
            extra["email"] = {
                "mode": "skip",
                "sent": False,
                "reason": "missing_token_or_spa_base",
                "spa_base": spa_base or None,
            }

        # En prod no devolver verify_token salvo METGO_EMAIL_DEV=1 (memoria → 1 por defecto)
        email_dev = os.getenv("METGO_EMAIL_DEV")
        if email_dev is None:
            email_dev = "1" if identity_store.use_memory() else "0"
        if email_dev != "1" and extra:
            extra.pop("verify_token", None)
            extra.pop("verify_path", None)
        return jsonify({"message": msg, **(extra or {})}), 201

    @app.post("/api/auth/reenviar-verificacion")
    def reenviar_verificacion():
        """Reenvía el mail de verificación (email + password + sitio[/faena])."""
        from api_rest import security_hardening as sec

        ok_rl, meta = sec.check_rate_limit("auth_resend", limit=5, window_s=60)
        if not ok_rl:
            return sec.rate_limit_response(meta)

        data = request.get_json(silent=True) or {}
        email = (data.get("email") or data.get("username") or "").strip().lower()
        password = data.get("password") or ""
        sitio = (data.get("sitio") or data.get("site") or "").strip().lower() or "spati"
        faena = (data.get("faena") or "").strip().lower() or None
        if not email or not password:
            return jsonify({"error": "email y password requeridos"}), 400

        from api_rest.identity import email_notify, pii_crypto

        user = identity_store.buscar_usuario_login(email, sitio, faena)
        if not user or not pii_crypto.verify_password(password, user.get("password_hash") or ""):
            return jsonify({"error": "Credenciales incorrectas"}), 401
        if user.get("email_verified_at"):
            return jsonify({"message": "Email ya verificado", "already_verified": True}), 200

        token = identity_store._issue_email_token(str(user["id"]))
        verify_url = _verify_email_url(str(user.get("sitio") or sitio), user.get("faena") or faena, token)
        if not verify_url:
            return jsonify({"error": "URL pública SPA no configurada"}), 500
        mail = email_notify.enviar_verificacion(
            to_email=email,
            verify_url=verify_url,
            sitio=str(user.get("sitio") or sitio),
            faena=user.get("faena") or faena,
            trial_days=plans_catalog.trial_days(),
        )
        body = {
            "message": "Si el correo es válido, recibirá el enlace de verificación",
            "email": mail,
            "trial_days": plans_catalog.trial_days(),
        }
        email_dev = os.getenv("METGO_EMAIL_DEV")
        if email_dev is None:
            email_dev = "1" if identity_store.use_memory() else "0"
        if email_dev == "1":
            body["verify_token"] = token
            body["verify_url"] = verify_url
        return jsonify(body), 200

    @app.get("/api/auth/verify-email")
    def verify_email():
        token = request.args.get("token") or ""
        ok, msg, extra = identity_store.verificar_email(token)
        if not ok:
            return jsonify({"error": msg}), 400
        return jsonify({"message": msg, **(extra or {})})

    @app.post("/api/auth/invitar")
    @auth_required
    def auth_invitar():
        """B3: invita otro email a la misma org (sin nuevo RUT)."""
        data = request.get_json(silent=True) or {}
        org_id = getattr(g, "org_id", None) or data.get("org_id")
        if not org_id:
            return jsonify({"error": "org_id requerido (sesión registrada)"}), 400
        ok, msg, extra = identity_store.invitar_usuario(
            data,
            org_id=str(org_id),
            invitador_role=getattr(g, "user_role", None),
            invitador_email=getattr(g, "current_user", None),
            ip=request.headers.get("X-Forwarded-For", request.remote_addr),
        )
        if not ok:
            return jsonify({"error": msg}), 400

        token = (extra or {}).get("verify_token")
        faena = (extra or {}).get("faena")
        sitio = (extra or {}).get("sitio") or getattr(g, "sitio_id", None) or "quillota"
        if token:
            verify_url = _verify_email_url(str(sitio), faena, token)
            if verify_url:
                extra["verify_url"] = verify_url
                try:
                    from api_rest.identity import email_notify

                    mail = email_notify.enviar_verificacion(
                        to_email=str(data.get("email") or ""),
                        verify_url=verify_url,
                        sitio=str(sitio),
                        faena=faena,
                        trial_days=plans_catalog.trial_days(),
                    )
                    extra["email"] = mail
                except Exception as exc:
                    extra["email"] = {"mode": "error", "error": str(exc)}

        email_dev = os.getenv("METGO_EMAIL_DEV")
        if email_dev is None:
            email_dev = "1" if identity_store.use_memory() else "0"
        if email_dev != "1" and extra:
            extra.pop("verify_token", None)
            extra.pop("verify_path", None)
        return jsonify({"message": msg, **(extra or {})}), 201

    @app.get("/api/auth/access")
    @auth_required
    def auth_access():
        sitio = (
            request.args.get("sitio")
            or getattr(g, "sitio_id", None)
            or "quillota"
        )
        faena = request.args.get("faena") or getattr(g, "faena_id", None)
        tab = (request.args.get("tab") or "").strip().lower() or None

        plan_code = getattr(g, "plan_code", None) or "pro"
        sub_status = getattr(g, "sub_status", None) or "active"
        org_id = getattr(g, "org_id", None)

        if org_id:
            sub = identity_store.suscripcion_efectiva(
                identity_store.suscripcion_de_org(org_id)
            )
            if sub:
                plan_code = sub.get("plan_code") or plan_code
                sub_status = sub.get("status") or sub_status
                faena = faena or sub.get("faena")

        access = identity_store.compute_access(
            sitio=str(sitio),
            faena=str(faena) if faena else None,
            plan_code=str(plan_code),
            sub_status=str(sub_status),
        )
        if tab:
            access["tab"] = tab
            access["tab_allowed"] = bool((access.get("tabs") or {}).get(tab))
            if not access["tab_allowed"]:
                return jsonify(access), 403
        return jsonify(access)

    @app.get("/api/auth/cuenta")
    @auth_required
    def auth_cuenta():
        faena = request.args.get("faena") or getattr(g, "faena_id", None)
        return jsonify(
            identity_store.cuenta_resumen(
                email=g.current_user,
                org_id=getattr(g, "org_id", None),
                sitio=getattr(g, "sitio_id", None),
                faena=faena,
            )
        )

    @app.get("/api/auth/mis-faenas")
    @auth_required
    def auth_mis_faenas():
        """Faenas visibles según suscripción (no el catálogo comercial completo)."""
        plan_code = getattr(g, "plan_code", None) or "trial"
        org_id = getattr(g, "org_id", None)
        if org_id:
            sub = identity_store.suscripcion_de_org(org_id)
            if sub:
                plan_code = sub.get("plan_code") or plan_code
        hub = identity_store.resolver_hub_faenas(
            email=g.current_user,
            role=getattr(g, "user_role", None),
            sitio=getattr(g, "sitio_id", None) or "spati",
            faena_jwt=getattr(g, "faena_id", None),
            plan_code=plan_code,
        )
        return jsonify(hub)

    @app.get("/api/auth/ops-board")
    @auth_required
    def auth_ops_board():
        """M10: resumen operativo multi-faena (solo hub del usuario / admin)."""
        from api_rest import ops_board_service
        from api_rest.faena_catalogo import listar_faenas

        plan_code = getattr(g, "plan_code", None) or "trial"
        org_id = getattr(g, "org_id", None)
        if org_id:
            sub = identity_store.suscripcion_de_org(org_id)
            if sub:
                plan_code = sub.get("plan_code") or plan_code
        hub = identity_store.resolver_hub_faenas(
            email=g.current_user,
            role=getattr(g, "user_role", None),
            sitio=getattr(g, "sitio_id", None) or "spati",
            faena_jwt=getattr(g, "faena_id", None),
            plan_code=plan_code,
        )
        catalogo = bool(hub.get("catalogo_completo"))
        multi = bool(hub.get("multi_faena"))
        faenas_hub = hub.get("faenas") or []
        if not catalogo and not multi and len(faenas_hub) < 2:
            return (
                jsonify(
                    {
                        "error": "ops_board_requiere_multi_faena",
                        "detalle": "Disponible para admin, plan multi_faena o ≥2 faenas.",
                        "hub": hub,
                    }
                ),
                403,
            )
        if catalogo:
            ids = [f["id"] for f in listar_faenas(incluir_izaje=True)]
        else:
            ids = [str(f.get("slug") or f).lower() for f in faenas_hub]
        refresh = (request.args.get("refresh") or "").strip().lower() in (
            "1",
            "true",
            "yes",
        )
        board = ops_board_service.construir_ops_board(
            ids, refresh=refresh, incluir_observado=True
        )
        board["hub"] = {
            "catalogo_completo": catalogo,
            "multi_faena": multi,
            "n_hub": len(ids),
        }
        return jsonify(board)

    @app.get("/api/public/planes")
    def public_planes():
        sitio = (request.args.get("sitio") or "spati").strip().lower()
        faena = (request.args.get("faena") or "").strip().lower() or None
        return jsonify(plans_catalog.listar_planes(sitio, faena))

    @app.get("/api/public/faenas/<faena>/reglas")
    def public_faena_reglas(faena: str):
        reglas = identity_store.reglas_faena(faena)
        return jsonify({"faena": faena, "reglas": reglas, "enlace": f"/f/{faena}/"})

    @app.post("/api/billing/checkout")
    @auth_required
    def billing_checkout():
        data = request.get_json(silent=True) or {}
        plan = (data.get("plan_code") or "starter").strip().lower()
        sitio = data.get("sitio") or getattr(g, "sitio_id", None) or "spati"
        faena = data.get("faena") or getattr(g, "faena_id", None)
        org_id = getattr(g, "org_id", None) or data.get("org_id")
        catalog = plans_catalog.listar_planes(str(sitio), faena)
        plan_row = next((p for p in catalog["planes"] if p["plan_code"] == plan), None)
        if not plan_row:
            return jsonify({"error": "Plan desconocido"}), 400
        if plan_row.get("contacto"):
            return jsonify({"error": "Contacte ventas para Enterprise", "plan": plan_row}), 400
        if not org_id:
            return jsonify({"error": "org_id requerido (inicie sesión con cuenta registrada)"}), 400

        ok_kyc, kyc_msg = identity_store.assert_kyc_allows_paid_plan(str(org_id), plan)
        if not ok_kyc:
            return (
                jsonify(
                    {
                        "error": kyc_msg,
                        "code": "kyc_required",
                        "kyc": identity_store.org_kyc(str(org_id)),
                    }
                ),
                403,
            )

        stripe_key = (os.getenv("STRIPE_SECRET_KEY") or "").strip()
        if not stripe_key:
            # Mock: aplica plan de inmediato (MVP sin Stripe)
            ok, msg, sub = identity_store.aplicar_plan(str(org_id), plan, status="active")
            if not ok:
                return jsonify({"error": msg}), 400
            return jsonify(
                {
                    "mode": "mock",
                    "applied": True,
                    "message": msg,
                    "plan": plan_row,
                    "suscripcion": sub,
                    "sitio": sitio,
                    "faena": faena,
                }
            )

        price_env = f"STRIPE_PRICE_{plan.upper()}"
        price_id = (os.getenv(price_env) or "").strip()
        if not price_id:
            return jsonify(
                {
                    "mode": "stripe",
                    "error": f"Falta {price_env} en el entorno",
                    "plan": plan_row,
                }
            ), 501

        spa = _public_spa_base(str(sitio))
        if str(sitio).lower() == "spati":
            cuenta_path = f"/f/{faena or 'escondida'}/cuenta"
        else:
            cuenta_path = "/cuenta"
        success = data.get("success_url") or f"{spa}{cuenta_path}?checkout=success"
        cancel = data.get("cancel_url") or f"{spa}{cuenta_path}?checkout=cancel"
        try:
            import requests

            res = requests.post(
                "https://api.stripe.com/v1/checkout/sessions",
                auth=(stripe_key, ""),
                data={
                    "mode": "subscription",
                    "success_url": success,
                    "cancel_url": cancel,
                    "line_items[0][price]": price_id,
                    "line_items[0][quantity]": "1",
                    "client_reference_id": str(org_id),
                    "metadata[org_id]": str(org_id),
                    "metadata[plan_code]": plan,
                    "metadata[sitio]": str(sitio),
                    "metadata[faena]": str(faena or ""),
                },
                timeout=30,
            )
            payload = res.json() if res.content else {}
            if res.status_code >= 400:
                return jsonify({"mode": "stripe", "error": payload.get("error", payload)}), 502
            return jsonify(
                {
                    "mode": "stripe",
                    "checkout_url": payload.get("url"),
                    "session_id": payload.get("id"),
                    "plan": plan_row,
                }
            )
        except Exception as exc:
            return jsonify({"mode": "stripe", "error": str(exc)}), 502

    @app.post("/api/billing/webhook")
    def billing_webhook():
        """Webhook Stripe (mock acepta JSON {org_id, plan_code, status})."""
        payload = request.get_json(silent=True) or {}
        # Firma Stripe opcional
        secret = (os.getenv("STRIPE_WEBHOOK_SECRET") or "").strip()
        if secret:
            sig = request.headers.get("Stripe-Signature", "")
            if not sig:
                return jsonify({"error": "Firma requerida"}), 400

        # Evento simplificado mock / manual
        org_id = payload.get("org_id") or (payload.get("data") or {}).get("object", {}).get(
            "metadata", {}
        ).get("org_id")
        plan = payload.get("plan_code") or "starter"
        status = payload.get("status") or "active"
        if not org_id:
            # checkout.session.completed shape
            obj = (payload.get("data") or {}).get("object") or {}
            org_id = (obj.get("metadata") or {}).get("org_id")
            plan = (obj.get("metadata") or {}).get("plan_code") or plan
        if not org_id:
            return jsonify({"error": "org_id no encontrado en evento"}), 400
        ok_kyc, kyc_msg = identity_store.assert_kyc_allows_paid_plan(str(org_id), str(plan))
        if not ok_kyc:
            return jsonify({"error": kyc_msg, "code": "kyc_required"}), 403
        ok, msg, sub = identity_store.aplicar_plan(str(org_id), str(plan), status=str(status))
        if not ok:
            return jsonify({"error": msg}), 400
        return jsonify({"received": True, "message": msg, "suscripcion": sub})

    @app.post("/api/auth/ops/kyc")
    def ops_set_kyc():
        """KYC manual (ADR A): admin JWT o CRON_SECRET."""
        if not _auth_preview_admin_or_cron():
            return jsonify({"error": "No autorizado", "code": "forbidden"}), 403
        data = request.get_json(silent=True) or {}
        org_id = (data.get("org_id") or "").strip()
        status = (data.get("kyc_status") or data.get("status") or "").strip()
        notes = data.get("notes") or data.get("kyc_notes")
        reviewed_by = data.get("reviewed_by")
        if not reviewed_by:
            auth = request.headers.get("Authorization") or ""
            if auth.startswith("Bearer "):
                try:
                    import metgo_auth

                    pl = metgo_auth.decodificar_token(auth.split(" ", 1)[1])
                    reviewed_by = (pl or {}).get("sub") or "admin"
                except Exception:
                    reviewed_by = "admin"
            else:
                reviewed_by = "ops"
        ok, msg, info = identity_store.set_org_kyc(
            org_id, status, notes=notes, reviewed_by=str(reviewed_by)
        )
        if not ok:
            return jsonify({"error": msg}), 400
        return jsonify({"message": msg, "kyc": info})

    def _auth_preview_admin_or_cron() -> bool:
        secret = request.args.get("token") or request.headers.get("X-Cron-Token")
        cron = (os.getenv("CRON_SECRET") or "").strip()
        if cron and secret == cron:
            return True
        auth = request.headers.get("Authorization") or ""
        if auth.startswith("Bearer "):
            try:
                import metgo_auth

                payload = metgo_auth.decodificar_token(auth.split(" ", 1)[1])
                role = (payload or {}).get("role")
                return role in ("admin", "administrador")
            except Exception:
                return False
        return (os.getenv("METGO_ALLOW_PREVIEW") or "").strip().lower() in (
            "1",
            "true",
            "yes",
        )

    @app.post("/api/auth/preview-hora")
    def create_preview_hora():
        """Crea usuario temporal 1 h: solo Ahora + Panel técnico.

        Auth: CRON_SECRET (?token= / X-Cron-Token), Bearer admin, o METGO_ALLOW_PREVIEW=1.
        """
        if not _auth_preview_admin_or_cron():
            return jsonify({"error": "No autorizado"}), 401

        data = request.get_json(silent=True) or {}
        faena = (data.get("faena") or request.args.get("faena") or "quebrada_blanca").strip()
        horas = float(data.get("horas") or request.args.get("horas") or 1)
        label = data.get("label") or request.args.get("label")
        ok, msg, extra = identity_store.crear_usuario_preview(
            faena=faena, horas=horas, label=label
        )
        if not ok:
            return jsonify({"error": msg}), 400
        return jsonify({"message": msg, **(extra or {})}), 201

    @app.post("/api/auth/preview-demo")
    def ensure_preview_demo():
        """Upsert usuario demo fijo (requiere METGO_SEED_DEMO_PREVIEW=1).

        Auth: CRON_SECRET, Bearer admin, o METGO_ALLOW_PREVIEW=1.
        Por defecto la demo está desactivada; preferir DELETE para retirarla.
        """
        if not _auth_preview_admin_or_cron():
            return jsonify({"error": "No autorizado"}), 401
        if (os.getenv("METGO_SEED_DEMO_PREVIEW") or "0").strip().lower() not in (
            "1",
            "true",
            "yes",
        ):
            return (
                jsonify(
                    {
                        "error": "Demo fija desactivada",
                        "hint": "Usar DELETE /api/auth/preview-demo para eliminar; "
                        "o METGO_SEED_DEMO_PREVIEW=1 solo en entorno controlado.",
                    }
                ),
                410,
            )

        data = request.get_json(silent=True) or {}
        faena = (data.get("faena") or request.args.get("faena") or "quebrada_blanca").strip()
        horas = float(data.get("horas") or request.args.get("horas") or 24)
        ok, msg, extra = identity_store.ensure_usuario_demo_fijo(faena=faena, horas=horas)
        if not ok:
            return jsonify({"error": msg}), 400
        # No devolver la clave en claro en la respuesta HTTP.
        safe = {k: v for k, v in (extra or {}).items() if k != "password"}
        return jsonify({"message": msg, **safe}), 200

    @app.delete("/api/auth/preview-demo")
    def delete_preview_demo():
        """Elimina la cuenta demo fija (demo@ventora.demo) y su org."""
        if not _auth_preview_admin_or_cron():
            return jsonify({"error": "No autorizado"}), 401
        ok, msg, extra = identity_store.eliminar_usuario_demo_fijo()
        if not ok:
            return jsonify({"error": msg}), 400
        return jsonify({"ok": True, "message": msg, **(extra or {})}), 200

    @app.post("/api/cron/identity/purge-preview")
    def cron_purge_preview():
        if not _auth_preview_admin_or_cron():
            return jsonify({"error": "No autorizado"}), 401
        result = identity_store.purge_preview_expirados()
        return jsonify({"ok": True, **result})
