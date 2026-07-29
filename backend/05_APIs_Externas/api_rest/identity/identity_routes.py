#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Rutas identidad comercial S1: validate, register-v2, access, planes, faena reglas."""

from __future__ import annotations

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
        return jsonify({"message": msg, **(extra or {})}), 201

    @app.get("/api/auth/access")
    @auth_required
    def auth_access():
        """GET para que cada pestaña/SPA verifique entitlements + reglas de faena."""
        sitio = (
            request.args.get("sitio")
            or getattr(g, "sitio_id", None)
            or "quillota"
        )
        faena = request.args.get("faena") or getattr(g, "faena_id", None)
        tab = (request.args.get("tab") or "").strip().lower() or None

        # Bootstrap: usuarios legacy env → acceso amplio en su sitio
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
        """Checkout Stripe o mock (sin STRIPE_SECRET_KEY)."""
        import os

        data = request.get_json(silent=True) or {}
        plan = (data.get("plan_code") or "starter").strip().lower()
        sitio = data.get("sitio") or getattr(g, "sitio_id", None) or "spati"
        faena = data.get("faena") or getattr(g, "faena_id", None)
        catalog = plans_catalog.listar_planes(str(sitio), faena)
        plan_row = next((p for p in catalog["planes"] if p["plan_code"] == plan), None)
        if not plan_row:
            return jsonify({"error": "Plan desconocido"}), 400
        if plan_row.get("contacto"):
            return jsonify({"error": "Contacte ventas para Enterprise", "plan": plan_row}), 400

        if not (os.getenv("STRIPE_SECRET_KEY") or "").strip():
            return jsonify(
                {
                    "mode": "mock",
                    "checkout_url": None,
                    "message": "Stripe no configurado; use METGO_IDENTITY_STORE=memory y patch de plan en S2",
                    "plan": plan_row,
                    "sitio": sitio,
                    "faena": faena,
                }
            )
        return jsonify(
            {
                "mode": "stripe",
                "error": "Checkout Stripe pendiente de Price IDs (fase S2)",
                "plan": plan_row,
            }
        ), 501
