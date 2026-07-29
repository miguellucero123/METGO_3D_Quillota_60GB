#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Persistencia identidad: memoria (tests) o Supabase PostgREST."""

from __future__ import annotations

import os
import threading
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

from api_rest.identity import pii_crypto
from api_rest.identity.plans_catalog import features_for_plan

_lock = threading.Lock()
_MEM: dict[str, list[dict[str, Any]]] = {
    "orgs": [],
    "usuarios_app": [],
    "consentimientos": [],
    "suscripciones": [],
    "entitlements": [],
    "faena_reglas": [],
    "audit_auth": [],
}

# Seed reglas en memoria (mismas ideas que la migración)
_DEFAULT_REGLAS = [
    ("escondida", "izaje", True, "trial"),
    ("escondida", "ambiente", True, "trial"),
    ("escondida", "dron", True, "starter"),
    ("escondida", "ops", True, "pro"),
    ("los_bronces", "izaje", True, "trial"),
    ("los_bronces", "ambiente", True, "trial"),
    ("los_bronces", "dron", True, "starter"),
    ("los_bronces", "ops", True, "pro"),
]


def use_memory() -> bool:
    mode = (os.getenv("METGO_IDENTITY_STORE") or "").strip().lower()
    if mode == "memory":
        return True
    if mode == "supabase":
        return False
    try:
        from api_rest.integracion.supabase_store import supabase_configurado

        return not supabase_configurado()
    except Exception:
        return True


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _ensure_mem_reglas() -> None:
    if _MEM["faena_reglas"]:
        return
    for faena, sistema, enabled, plan_min in _DEFAULT_REGLAS:
        _MEM["faena_reglas"].append(
            {
                "faena": faena,
                "sistema": sistema,
                "enabled": enabled,
                "plan_minimo": plan_min,
                "config": {},
            }
        )


def reset_memory() -> None:
    with _lock:
        for k in _MEM:
            _MEM[k] = []
        _ensure_mem_reglas()


def consent_version() -> str:
    return (os.getenv("METGO_CONSENT_VERSION") or "2026-07-29").strip()


def registrar_v2(payload: dict[str, Any], *, ip: str | None = None) -> tuple[bool, str, dict[str, Any] | None]:
    """Crea org + usuario + consentimientos + suscripción trial."""
    from api_rest.identity.validators import validate_registro_payload

    check = validate_registro_payload(payload)
    if not check["ok"]:
        return False, "Validación fallida", {"validation": check}

    email = str(payload.get("email") or "").strip().lower()
    sitio = str(payload.get("sitio") or "").strip().lower()
    faena = (str(payload.get("faena") or "").strip().lower() or None)
    password = payload.get("password") or ""
    cons = payload.get("consentimientos") or {}

    if use_memory():
        return _register_memory(payload, email, sitio, faena, password, cons, ip)

    return _register_supabase(payload, email, sitio, faena, password, cons, ip)


def _register_memory(payload, email, sitio, faena, password, cons, ip):
    with _lock:
        _ensure_mem_reglas()
        for u in _MEM["usuarios_app"]:
            if u["email_norm"] == email and u["sitio"] == sitio and u.get("faena") == faena:
                return False, "Email ya registrado en este sitio/faena", None

        org_id = str(uuid.uuid4())
        user_id = str(uuid.uuid4())
        sub_id = str(uuid.uuid4())
        now = _utcnow().isoformat()

        org = {
            "id": org_id,
            "sitio": sitio,
            "faena": faena,
            "razon_social_enc": pii_crypto.encrypt_pii(str(payload.get("razon_social") or "")),
            "rut_enc": pii_crypto.encrypt_pii(str(payload.get("rut") or "")),
            "giro": payload.get("giro"),
            "created_at": now,
        }
        user = {
            "id": user_id,
            "email_norm": email,
            "password_hash": pii_crypto.hash_password(str(password)),
            "nombres_enc": pii_crypto.encrypt_pii(str(payload.get("nombres") or "")),
            "apellidos_enc": pii_crypto.encrypt_pii(str(payload.get("apellidos") or "")),
            "telefono_enc": pii_crypto.encrypt_pii(str(payload.get("telefono") or ""))
            if payload.get("telefono")
            else None,
            "org_id": org_id,
            "sitio": sitio,
            "faena": faena,
            "role": "operador",
            "email_verified_at": None,
            "status": "pending",
            "created_at": now,
        }
        _MEM["orgs"].append(org)
        _MEM["usuarios_app"].append(user)

        ver = consent_version()
        ip_h = pii_crypto.hash_ip(ip)
        for tipo in ("almacenamiento_datos", "tos", "privacy", "veracidad"):
            if cons.get(tipo) is True:
                _MEM["consentimientos"].append(
                    {
                        "id": str(uuid.uuid4()),
                        "usuario_id": user_id,
                        "tipo": tipo,
                        "version": ver,
                        "accepted_at": now,
                        "ip_hash": ip_h,
                    }
                )

        trial_end = (_utcnow() + timedelta(days=14)).isoformat()
        feats = features_for_plan("trial")
        _MEM["suscripciones"].append(
            {
                "id": sub_id,
                "org_id": org_id,
                "sitio": sitio,
                "faena": faena,
                "plan_code": "trial",
                "status": "trialing",
                "current_period_end": trial_end,
                "seats": 1,
                "metadata": {},
            }
        )
        for fk in feats:
            _MEM["entitlements"].append(
                {"id": str(uuid.uuid4()), "suscripcion_id": sub_id, "feature_key": fk, "enabled": True}
            )

        _MEM["audit_auth"].append(
            {
                "usuario_id": user_id,
                "sitio": sitio,
                "faena": faena,
                "evento": "register_v2",
                "ip_hash": ip_h,
                "at": now,
            }
        )

        return True, "Usuario creado (verifique email)", {
            "usuario_id": user_id,
            "org_id": org_id,
            "sitio": sitio,
            "faena": faena,
            "status": "pending",
            "plan_code": "trial",
            "sub_status": "trialing",
            "consent_version": ver,
        }


def _register_supabase(payload, email, sitio, faena, password, cons, ip):
    from api_rest.integracion import supabase_store as sb

    # unicidad aproximada
    params = {"email_norm": f"eq.{email}", "sitio": f"eq.{sitio}", "select": "id"}
    if faena:
        params["faena"] = f"eq.{faena}"
    else:
        params["faena"] = "is.null"
    existing = sb.rest_select("usuarios_app", params=params, limit=1)
    if existing:
        return False, "Email ya registrado en este sitio/faena", None

    org_rows = sb.rest_insert(
        "orgs",
        {
            "sitio": sitio,
            "faena": faena,
            "razon_social_enc": pii_crypto.encrypt_pii(str(payload.get("razon_social") or "")),
            "rut_enc": pii_crypto.encrypt_pii(str(payload.get("rut") or "")),
            "giro": payload.get("giro"),
        },
    )
    if not org_rows:
        return False, "No se pudo crear organización (Supabase)", None
    org_id = org_rows[0]["id"]

    user_rows = sb.rest_insert(
        "usuarios_app",
        {
            "email_norm": email,
            "password_hash": pii_crypto.hash_password(str(password)),
            "nombres_enc": pii_crypto.encrypt_pii(str(payload.get("nombres") or "")),
            "apellidos_enc": pii_crypto.encrypt_pii(str(payload.get("apellidos") or "")),
            "telefono_enc": pii_crypto.encrypt_pii(str(payload.get("telefono") or ""))
            if payload.get("telefono")
            else None,
            "org_id": org_id,
            "sitio": sitio,
            "faena": faena,
            "role": "operador",
            "status": "pending",
        },
    )
    if not user_rows:
        return False, "No se pudo crear usuario (Supabase)", None
    user_id = user_rows[0]["id"]

    ver = consent_version()
    ip_h = pii_crypto.hash_ip(ip)
    for tipo in ("almacenamiento_datos", "tos", "privacy", "veracidad"):
        if cons.get(tipo) is True:
            sb.rest_insert(
                "consentimientos",
                {
                    "usuario_id": user_id,
                    "tipo": tipo,
                    "version": ver,
                    "ip_hash": ip_h,
                },
            )

    trial_end = (_utcnow() + timedelta(days=14)).isoformat()
    sub_rows = sb.rest_insert(
        "suscripciones",
        {
            "org_id": org_id,
            "sitio": sitio,
            "faena": faena,
            "plan_code": "trial",
            "status": "trialing",
            "current_period_end": trial_end,
            "seats": 1,
            "metadata": {},
        },
    )
    sub_id = (sub_rows or [{}])[0].get("id")
    if sub_id:
        for fk in features_for_plan("trial"):
            sb.rest_insert(
                "entitlements",
                {"suscripcion_id": sub_id, "feature_key": fk, "enabled": True},
            )

    sb.rest_insert(
        "audit_auth",
        {
            "usuario_id": user_id,
            "sitio": sitio,
            "faena": faena,
            "evento": "register_v2",
            "ip_hash": ip_h,
        },
    )

    return True, "Usuario creado (verifique email)", {
        "usuario_id": user_id,
        "org_id": org_id,
        "sitio": sitio,
        "faena": faena,
        "status": "pending",
        "plan_code": "trial",
        "sub_status": "trialing",
        "consent_version": ver,
    }


def buscar_usuario_login(email: str, sitio: str, faena: str | None) -> dict[str, Any] | None:
    email = (email or "").strip().lower()
    sitio = (sitio or "").strip().lower()
    faena = (faena or "").strip().lower() or None
    if use_memory():
        with _lock:
            for u in _MEM["usuarios_app"]:
                if u["email_norm"] == email and u["sitio"] == sitio and u.get("faena") == faena:
                    return dict(u)
        return None
    from api_rest.integracion import supabase_store as sb

    params = {"email_norm": f"eq.{email}", "sitio": f"eq.{sitio}", "select": "*"}
    if faena:
        params["faena"] = f"eq.{faena}"
    else:
        params["faena"] = "is.null"
    rows = sb.rest_select("usuarios_app", params=params, limit=1)
    return rows[0] if rows else None


def suscripcion_de_org(org_id: str) -> dict[str, Any] | None:
    if use_memory():
        with _lock:
            for s in _MEM["suscripciones"]:
                if s["org_id"] == org_id:
                    return dict(s)
        return None
    from api_rest.integracion import supabase_store as sb

    rows = sb.rest_select(
        "suscripciones",
        params={"org_id": f"eq.{org_id}", "select": "*", "limit": "1"},
        limit=1,
    )
    return rows[0] if rows else None


def reglas_faena(faena: str) -> list[dict[str, Any]]:
    faena = (faena or "").strip().lower()
    if use_memory():
        with _lock:
            _ensure_mem_reglas()
            return [dict(r) for r in _MEM["faena_reglas"] if r["faena"] == faena]
    from api_rest.integracion import supabase_store as sb

    return sb.rest_select(
        "faena_reglas",
        params={"faena": f"eq.{faena}", "select": "*"},
        limit=50,
    )


def compute_access(*, sitio: str, faena: str | None, plan_code: str, sub_status: str) -> dict[str, Any]:
    from api_rest.identity.plans_catalog import TAB_FEATURE, TAB_SISTEMA, features_for_plan, plan_rank

    active = sub_status in ("trialing", "active")
    feats = features_for_plan(plan_code) if active else set()
    rank = plan_rank(plan_code)

    sistemas: dict[str, bool] = {}
    tabs: dict[str, bool] = {k: False for k in TAB_FEATURE}
    reasons: dict[str, str] = {}

    if faena and sitio == "spati":
        for r in reglas_faena(faena):
            sist = r.get("sistema")
            enabled = bool(r.get("enabled"))
            min_ok = plan_rank(r.get("plan_minimo")) <= rank
            sistemas[sist] = active and enabled and min_ok
            if not sistemas[sist]:
                reasons[sist] = "plan_o_regla" if active else "sin_suscripcion"
    else:
        sistemas = {
            "izaje": "panel" in feats,
            "ambiente": "ambiente" in feats,
            "dron": "dron" in feats,
            "ops": "umbrales" in feats,
            "aire": sitio == "copiapo" and active,
        }

    for tab, feat in TAB_FEATURE.items():
        sist = TAB_SISTEMA.get(tab)
        feat_ok = feat in feats
        sist_ok = sistemas.get(sist, True) if sist else True
        tabs[tab] = bool(active and feat_ok and sist_ok)
        if not tabs[tab]:
            reasons[tab] = "no_habilitado"

    return {
        "allowed": active,
        "sitio": sitio,
        "faena": faena,
        "plan_code": plan_code,
        "sub_status": sub_status,
        "tabs": tabs,
        "sistemas": sistemas,
        "reasons": reasons,
    }
