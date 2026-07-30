#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Rutas identidad comercial S1/S2: registro, verify, access, billing, cuenta."""

from __future__ import annotations

import os

from flask import Flask, g, jsonify, request

from api_rest.auth_routes import auth_required
from api_rest.identity import identity_store, plans_catalog, validators


def register_identity_routes(app: Flask) -> None:
    @app.post("/api/auth/validate-registro")
    def validate_registro():
        data = request.get_json(silent=True) or {}
        result = validators.validate_registro_payload(data)
        return jsonify(result), (200 if result["ok"] else 400)

    @app.post("/api/auth/register-v2")
    def register_v2():
        data = request.get_json(silent=True) or {}
        ok, msg, extra = identity_store.registrar_v2(
            data, ip=request.headers.get("X-Forwarded-For", request.remote_addr)
        )
        if not ok:
            body = {"error": msg}
            if extra:
                body.update(extra)
            return jsonify(body), 400

        # Enlace de verificación (SPA o API)
        token = (extra or {}).get("verify_token")
        faena = (extra or {}).get("faena")
        sitio = (extra or {}).get("sitio") or "spati"
        spa_base = (
            (os.getenv("METGO_SPATI_PUBLIC_URL") or "https://metgo-spati.pages.dev").rstrip("/")
            if sitio == "spati"
            else (os.getenv("METGO_PUBLIC_APP_URL") or "").rstrip("/")
        )
        if token and spa_base and faena:
            verify_url = f"{spa_base}/f/{faena}/verificar?token={token}"
            extra["verify_url"] = verify_url
            try:
                from api_rest.identity import email_notify

                mail = email_notify.enviar_verificacion(
                    to_email=str(data.get("email") or ""),
                    verify_url=verify_url,
                    sitio=str(sitio),
                    faena=faena,
                )
                extra["email"] = mail
            except Exception as exc:
                extra["email"] = {"mode": "error", "error": str(exc)}

        # En prod no devolver verify_token salvo METGO_EMAIL_DEV=1 (memoria → 1 por defecto)
        email_dev = os.getenv("METGO_EMAIL_DEV")
        if email_dev is None:
            email_dev = "1" if identity_store.use_memory() else "0"
        if email_dev != "1" and extra:
            extra.pop("verify_token", None)
            extra.pop("verify_path", None)
        return jsonify({"message": msg, **(extra or {})}), 201

    @app.get("/api/auth/verify-email")
    def verify_email():
        token = request.args.get("token") or ""
        ok, msg, extra = identity_store.verificar_email(token)
        if not ok:
            return jsonify({"error": msg}), 400
        return jsonify({"message": msg, **(extra or {})})

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
            sub = identity_store.suscripcion_de_org(org_id)
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

        success = data.get("success_url") or (
            f"{(os.getenv('METGO_SPATI_PUBLIC_URL') or 'https://metgo-spati.pages.dev').rstrip('/')}"
            f"/f/{faena or 'escondida'}/cuenta?checkout=success"
        )
        cancel = data.get("cancel_url") or (
            f"{(os.getenv('METGO_SPATI_PUBLIC_URL') or 'https://metgo-spati.pages.dev').rstrip('/')}"
            f"/f/{faena or 'escondida'}/cuenta?checkout=cancel"
        )
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
        ok, msg, sub = identity_store.aplicar_plan(str(org_id), str(plan), status=str(status))
        if not ok:
            return jsonify({"error": msg}), 400
        return jsonify({"received": True, "message": msg, "suscripcion": sub})
