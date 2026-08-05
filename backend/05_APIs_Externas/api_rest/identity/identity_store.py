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
from api_rest.identity import plans_catalog
from api_rest.identity.plans_catalog import features_for_plan, trial_days

_lock = threading.Lock()
_MEM: dict[str, list[dict[str, Any]]] = {
    "orgs": [],
    "usuarios_app": [],
    "consentimientos": [],
    "suscripciones": [],
    "entitlements": [],
    "faena_reglas": [],
    "audit_auth": [],
    "email_tokens": [],
}

# Seed reglas en memoria — 17 faenas SPATI (izaje/ambiente trial; dron pro; ops/pro)
_SPATI_FAENAS = (
    "quebrada_blanca",
    "collahuasi",
    "cerro_colorado",
    "el_abra",
    "chuquicamata",
    "radomiro_tomic",
    "ministro_hales",
    "spence",
    "escondida",
    "el_penon",
    "la_coipa",
    "maricunga",
    "candelaria",
    "los_pelambres",
    "los_bronces",
    "andina",
    "el_teniente",
)

_DEFAULT_REGLAS: list[tuple[str, str, bool, str]] = []
for _f in _SPATI_FAENAS:
    _DEFAULT_REGLAS.extend(
        [
            (_f, "izaje", True, "trial"),
            (_f, "ambiente", True, "trial"),
            (_f, "dron", True, "pro"),
            (_f, "ops", True, "pro"),
        ]
    )


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

        rut_h = pii_crypto.rut_lookup_hash(str(payload.get("rut") or ""))
        for o in _MEM["orgs"]:
            if (
                o.get("sitio") == sitio
                and o.get("faena") == faena
                and o.get("rut_hash") == rut_h
            ):
                return (
                    False,
                    "Este RUT ya tiene cuenta en este producto. "
                    "Inicie sesión o solicite invitación a su administrador (no cree otra cuenta con otro correo).",
                    {"code": "rut_already_registered"},
                )

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
            "rut_hash": rut_h,
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

        trial_end = (_utcnow() + timedelta(days=trial_days())).isoformat()
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

        verify_token = _issue_email_token(user_id, locked=True)
        out = {
            "usuario_id": user_id,
            "org_id": org_id,
            "sitio": sitio,
            "faena": faena,
            "status": "pending",
            "plan_code": "trial",
            "sub_status": "trialing",
            "consent_version": ver,
            "verify_token": verify_token,
            "verify_path": f"/api/auth/verify-email?token={verify_token}",
        }
        return True, "Usuario creado (verifique email)", out


def _register_supabase(payload, email, sitio, faena, password, cons, ip):
    from api_rest.integracion import supabase_store as sb

    # unicidad email
    params = {"email_norm": f"eq.{email}", "sitio": f"eq.{sitio}", "select": "id"}
    if faena:
        params["faena"] = f"eq.{faena}"
    else:
        params["faena"] = "is.null"
    existing = sb.rest_select("usuarios_app", params=params, limit=1)
    if existing:
        return False, "Email ya registrado en este sitio/faena", None

    # unicidad RUT (hash determinístico; rut_enc AES no sirve para UNIQUE)
    rut_h = pii_crypto.rut_lookup_hash(str(payload.get("rut") or ""))
    org_params = {"sitio": f"eq.{sitio}", "rut_hash": f"eq.{rut_h}", "select": "id"}
    if faena:
        org_params["faena"] = f"eq.{faena}"
    else:
        org_params["faena"] = "is.null"
    try:
        org_dup = sb.rest_select("orgs", params=org_params, limit=1)
    except Exception:
        org_dup = []
    # PostgREST sin columna rut_hash → lista vacía / error; no bloquear registro
    if org_dup:
        return (
            False,
            "Este RUT ya tiene cuenta en este producto. "
            "Inicie sesión o solicite invitación a su administrador (no cree otra cuenta con otro correo).",
            {"code": "rut_already_registered"},
        )

    org_payload = {
        "sitio": sitio,
        "faena": faena,
        "razon_social_enc": pii_crypto.encrypt_pii(str(payload.get("razon_social") or "")),
        "rut_enc": pii_crypto.encrypt_pii(str(payload.get("rut") or "")),
        "rut_hash": rut_h,
        "giro": payload.get("giro"),
    }
    org_rows = sb.rest_insert("orgs", org_payload)
    if not org_rows:
        # Migración rut_hash pendiente en Supabase: reintentar sin la columna
        org_payload.pop("rut_hash", None)
        org_rows = sb.rest_insert("orgs", org_payload)
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

    trial_end = (_utcnow() + timedelta(days=trial_days())).isoformat()
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
        "verify_token": _issue_email_token(user_id),
    }


def _issue_email_token(user_id: str, *, locked: bool = False) -> str:
    import secrets

    token = secrets.token_urlsafe(24)
    exp = (_utcnow() + timedelta(hours=48)).isoformat()
    row = {"token": token, "usuario_id": user_id, "expires_at": exp, "used": False}
    if use_memory():
        if locked:
            _MEM["email_tokens"].append(row)
        else:
            with _lock:
                _MEM["email_tokens"].append(row)
        return token
    # Token firmado user_id.exp.mac (sin tabla extra)
    import hashlib
    import hmac

    mac = hmac.new(
        pii_crypto._kek(),
        f"{user_id}:{exp}".encode(),
        hashlib.sha256,
    ).hexdigest()[:24]
    return f"{user_id}.{exp}.{mac}"


def verificar_email(token: str) -> tuple[bool, str, dict[str, Any] | None]:
    token = (token or "").strip()
    if not token:
        return False, "Token requerido", None

    if use_memory():
        with _lock:
            for t in _MEM["email_tokens"]:
                if t["token"] != token:
                    continue
                if t.get("used"):
                    return False, "Token ya usado", None
                if t["expires_at"] < _utcnow().isoformat():
                    return False, "Token expirado", None
                uid = t["usuario_id"]
                t["used"] = True
                for u in _MEM["usuarios_app"]:
                    if u["id"] == uid:
                        u["email_verified_at"] = _utcnow().isoformat()
                        u["status"] = "active"
                        return True, "Email verificado", {
                            "usuario_id": uid,
                            "status": "active",
                            "email": u["email_norm"],
                        }
                return False, "Usuario no encontrado", None
        return False, "Token invalido", None

    # Token firmado user.exp.mac
    parts = token.split(".")
    if len(parts) != 3:
        return False, "Token invalido", None
    user_id, exp, mac = parts
    import hashlib
    import hmac

    expect = hmac.new(
        pii_crypto._kek(),
        f"{user_id}:{exp}".encode(),
        hashlib.sha256,
    ).hexdigest()[:24]
    if not hmac.compare_digest(mac, expect):
        return False, "Token invalido", None
    if exp < _utcnow().isoformat():
        return False, "Token expirado", None
    from api_rest.integracion import supabase_store as sb

    rows = sb.rest_patch(
        "usuarios_app",
        {"id": f"eq.{user_id}"},
        {"email_verified_at": _utcnow().isoformat(), "status": "active"},
    )
    if not rows:
        return False, "No se pudo verificar (Supabase)", None
    return True, "Email verificado", {
        "usuario_id": user_id,
        "status": "active",
        "email": rows[0].get("email_norm"),
    }


def invitar_usuario(
    payload: dict[str, Any],
    *,
    org_id: str,
    invitador_role: str | None = None,
    invitador_email: str | None = None,
    ip: str | None = None,
) -> tuple[bool, str, dict[str, Any] | None]:
    """Alta secundaria en org existente (mismo RUT/org; otro email). B3."""
    role_l = (invitador_role or "").strip().lower()
    if role_l not in ("admin", "administrador", "superadmin", "owner", "operador"):
        # operadores de la org también pueden invitar (piloto); restringir luego si hace falta
        pass
    if not org_id:
        return False, "org_id requerido", None

    email = (payload.get("email") or "").strip().lower()
    password = payload.get("password") or payload.get("contraseña") or ""
    nombres = str(payload.get("nombres") or payload.get("nombre") or "Invitado").strip()
    apellidos = str(payload.get("apellidos") or payload.get("apellido") or "METGO").strip()
    role = (payload.get("role") or "operador").strip().lower()
    if role not in ("operador", "admin", "viewer"):
        role = "operador"

    if not email or "@" not in email:
        return False, "Email inválido", None
    pwd_errs = []
    import re as _re

    if len(str(password)) < 10:
        pwd_errs.append("Mínimo 10 caracteres")
    if not _re.search(r"[A-ZÁÉÍÓÚÜÑ]", str(password or "")):
        pwd_errs.append("Debe incluir mayúscula")
    if not _re.search(r"[a-záéíóúüñ]", str(password or "")):
        pwd_errs.append("Debe incluir minúscula")
    if not _re.search(r"\d", str(password or "")):
        pwd_errs.append("Debe incluir número")
    if pwd_errs:
        return False, "; ".join(pwd_errs), None

    # Resolver org → sitio/faena
    sitio = None
    faena = None
    if use_memory():
        with _lock:
            org = next((o for o in _MEM["orgs"] if o["id"] == org_id), None)
            if not org:
                return False, "Organización no encontrada", None
            sitio = org.get("sitio")
            faena = org.get("faena")
            if any(
                u.get("email_norm") == email
                and u.get("sitio") == sitio
                and (u.get("faena") or None) == (faena or None)
                for u in _MEM["usuarios_app"]
            ):
                return False, "Email ya registrado en este sitio/faena", None
            user_id = str(uuid.uuid4())
            now = _utcnow().isoformat()
            _MEM["usuarios_app"].append(
                {
                    "id": user_id,
                    "email_norm": email,
                    "password_hash": pii_crypto.hash_password(str(password)),
                    "nombres_enc": pii_crypto.encrypt_pii(nombres),
                    "apellidos_enc": pii_crypto.encrypt_pii(apellidos),
                    "org_id": org_id,
                    "sitio": sitio,
                    "faena": faena,
                    "role": role,
                    "status": "pending",
                    "created_at": now,
                }
            )
            _MEM["audit_auth"].append(
                {
                    "usuario_id": user_id,
                    "sitio": sitio,
                    "faena": faena,
                    "evento": "invite",
                    "ip_hash": pii_crypto.hash_ip(ip),
                    "meta": {"invitador": invitador_email},
                    "at": now,
                }
            )
            verify_token = _issue_email_token(user_id, locked=True)
        return True, "Invitación creada", {
            "usuario_id": user_id,
            "org_id": org_id,
            "sitio": sitio,
            "faena": faena,
            "status": "pending",
            "verify_token": verify_token,
            "verify_path": f"/api/auth/verify-email?token={verify_token}",
        }

    from api_rest.integracion import supabase_store as sb

    orgs = sb.rest_select("orgs", params={"id": f"eq.{org_id}", "select": "*"}, limit=1)
    if not orgs:
        return False, "Organización no encontrada", None
    org = orgs[0]
    sitio = org.get("sitio")
    faena = org.get("faena")

    params = {"email_norm": f"eq.{email}", "sitio": f"eq.{sitio}", "select": "id"}
    if faena:
        params["faena"] = f"eq.{faena}"
    else:
        params["faena"] = "is.null"
    if sb.rest_select("usuarios_app", params=params, limit=1):
        return False, "Email ya registrado en este sitio/faena", None

    user_rows = sb.rest_insert(
        "usuarios_app",
        {
            "email_norm": email,
            "password_hash": pii_crypto.hash_password(str(password)),
            "nombres_enc": pii_crypto.encrypt_pii(nombres),
            "apellidos_enc": pii_crypto.encrypt_pii(apellidos),
            "org_id": org_id,
            "sitio": sitio,
            "faena": faena,
            "role": role,
            "status": "pending",
        },
    )
    if not user_rows:
        return False, "No se pudo crear usuario invitado", None
    user_id = user_rows[0]["id"]
    verify_token = _issue_email_token(user_id)
    return True, "Invitación creada", {
        "usuario_id": user_id,
        "org_id": org_id,
        "sitio": sitio,
        "faena": faena,
        "status": "pending",
        "verify_token": verify_token,
        "verify_path": f"/api/auth/verify-email?token={verify_token}",
    }


def aplicar_plan(
    org_id: str,
    plan_code: str,
    *,
    status: str = "active",
    stripe_customer_id: str | None = None,
    stripe_subscription_id: str | None = None,
) -> tuple[bool, str, dict[str, Any] | None]:
    plan_code = (plan_code or "").strip().lower()
    if plan_code not in ("trial", "starter", "pro", "enterprise", "preview"):
        return False, "Plan desconocido", None
    feats = features_for_plan(plan_code)
    if plan_code == "preview":
        period_end = (_utcnow() + timedelta(hours=1)).isoformat()
    else:
        period_end = (_utcnow() + timedelta(days=30)).isoformat()

    if use_memory():
        with _lock:
            sub = None
            for s in _MEM["suscripciones"]:
                if s["org_id"] == org_id:
                    sub = s
                    break
            if not sub:
                return False, "Suscripción no encontrada", None
            sub["plan_code"] = plan_code
            if plan_code == "preview":
                sub["status"] = "trialing"
            else:
                sub["status"] = status if plan_code != "trial" else "trialing"
            sub["current_period_end"] = period_end
            if stripe_customer_id:
                sub["stripe_customer_id"] = stripe_customer_id
            if stripe_subscription_id:
                sub["stripe_subscription_id"] = stripe_subscription_id
            sub_id = sub["id"]
            _MEM["entitlements"] = [e for e in _MEM["entitlements"] if e["suscripcion_id"] != sub_id]
            for fk in feats:
                _MEM["entitlements"].append(
                    {
                        "id": str(uuid.uuid4()),
                        "suscripcion_id": sub_id,
                        "feature_key": fk,
                        "enabled": True,
                    }
                )
            return True, "Plan aplicado", dict(sub)

    from api_rest.integracion import supabase_store as sb

    patch = {
        "plan_code": plan_code,
        "status": status if plan_code != "trial" else "trialing",
        "current_period_end": period_end,
    }
    if stripe_customer_id:
        patch["stripe_customer_id"] = stripe_customer_id
    if stripe_subscription_id:
        patch["stripe_subscription_id"] = stripe_subscription_id
    rows = sb.rest_patch("suscripciones", {"org_id": f"eq.{org_id}"}, patch)
    if not rows:
        return False, "No se pudo actualizar suscripción", None
    sub = rows[0]
    sub_id = sub.get("id")
    # Entitlements: insert nuevos (simplificado; no borra viejos por falta de DELETE genérico)
    for fk in feats:
        sb.rest_insert(
            "entitlements",
            {"suscripcion_id": sub_id, "feature_key": fk, "enabled": True},
        )
    return True, "Plan aplicado", sub


def cuenta_resumen(*, email: str | None, org_id: str | None, sitio: str | None, faena: str | None) -> dict[str, Any]:
    user = None
    if email and sitio:
        user = buscar_usuario_login(email, sitio, faena)
        if not user and faena:
            user = buscar_usuario_login(email, "spati", faena)
    org_id = org_id or (user or {}).get("org_id")
    sub = suscripcion_de_org(org_id) if org_id else None
    plan = (sub or {}).get("plan_code") or "trial"
    status = (sub or {}).get("status") or "trialing"
    access = compute_access(
        sitio=sitio or (user or {}).get("sitio") or "spati",
        faena=faena or (user or {}).get("faena"),
        plan_code=plan,
        sub_status=status,
    )
    return {
        "usuario": {
            "email": (user or {}).get("email_norm") or email,
            "status": (user or {}).get("status"),
            "role": (user or {}).get("role"),
            "email_verified": bool((user or {}).get("email_verified_at")),
            "org_id": org_id,
            "sitio": (user or {}).get("sitio") or sitio,
            "faena": (user or {}).get("faena") or faena,
        },
        "suscripcion": sub,
        "access": access,
        "planes": plans_catalog.listar_planes(
            (user or {}).get("sitio") or sitio or "spati",
            (user or {}).get("faena") or faena,
        ),
    }


def buscar_usuario_por_org(org_id: str) -> dict[str, Any] | None:
    if use_memory():
        with _lock:
            for u in _MEM["usuarios_app"]:
                if u.get("org_id") == org_id:
                    return dict(u)
        return None
    from api_rest.integracion import supabase_store as sb

    rows = sb.rest_select(
        "usuarios_app",
        params={"org_id": f"eq.{org_id}", "select": "*", "limit": "1"},
        limit=1,
    )
    return rows[0] if rows else None


def buscar_usuario_login(email: str, sitio: str, faena: str | None) -> dict[str, Any] | None:
    email = (email or "").strip().lower()
    sitio = (sitio or "").strip().lower()
    faena = (faena or "").strip().lower() or None
    if use_memory():
        with _lock:
            candidates = [
                u
                for u in _MEM["usuarios_app"]
                if u["email_norm"] == email and u["sitio"] == sitio
            ]
            if faena:
                for u in candidates:
                    if u.get("faena") == faena:
                        return dict(u)
                return None
            # Sin faena: preferir coincidencia exacta null, si no la primera membresía
            for u in candidates:
                if u.get("faena") in (None, ""):
                    return dict(u)
            return dict(candidates[0]) if candidates else None
    from api_rest.integracion import supabase_store as sb

    params = {"email_norm": f"eq.{email}", "sitio": f"eq.{sitio}", "select": "*"}
    if faena:
        params["faena"] = f"eq.{faena}"
        rows = sb.rest_select("usuarios_app", params=params, limit=1)
        return rows[0] if rows else None
    rows = sb.rest_select(
        "usuarios_app",
        params={"email_norm": f"eq.{email}", "sitio": f"eq.{sitio}", "select": "*"},
        limit=20,
    )
    if not rows:
        return None
    for r in rows:
        if r.get("faena") in (None, ""):
            return r
    return rows[0]

def listar_membresias_email(email: str, sitio: str = "spati") -> list[dict[str, Any]]:
    """Membresías del mismo email en un producto (puede haber varias faenas)."""
    email = (email or "").strip().lower()
    sitio = (sitio or "").strip().lower() or "spati"
    if not email:
        return []
    if use_memory():
        with _lock:
            return [
                dict(u)
                for u in _MEM["usuarios_app"]
                if u.get("email_norm") == email and u.get("sitio") == sitio
            ]
    from api_rest.integracion import supabase_store as sb

    return sb.rest_select(
        "usuarios_app",
        params={
            "email_norm": f"eq.{email}",
            "sitio": f"eq.{sitio}",
            "select": "id,email_norm,sitio,faena,org_id,role,status",
        },
        limit=50,
    )


def resolver_hub_faenas(
    *,
    email: str | None,
    role: str | None,
    sitio: str | None,
    faena_jwt: str | None,
    plan_code: str | None,
) -> dict[str, Any]:
    """Qué faenas puede ver en el hub / cambiar de URL.

    - admin / enterprise (multi_faena): catálogo completo
    - resto: solo membresías (registro/login en esa faena) + claim JWT
    """
    from api_rest.identity.plans_catalog import features_for_plan

    role_l = (role or "").strip().lower()
    plan = (plan_code or "trial").strip().lower()
    multi = "multi_faena" in features_for_plan(plan)
    is_admin = role_l in ("admin", "administrador", "superadmin")
    if is_admin or multi:
        return {
            "catalogo_completo": True,
            "multi_faena": True,
            "faenas": [],
            "motivo": "admin" if is_admin else "plan_multi_faena",
        }

    sitio_l = (sitio or "spati").strip().lower()
    memberships = listar_membresias_email(email or "", sitio_l)
    if not memberships and sitio_l != "spati":
        memberships = listar_membresias_email(email or "", "spati")

    slugs: list[str] = []
    seen: set[str] = set()
    for m in memberships:
        slug = (m.get("faena") or "").strip().lower()
        if slug and slug not in seen:
            seen.add(slug)
            slugs.append(slug)
    jwt_f = (faena_jwt or "").strip().lower()
    if jwt_f and jwt_f not in seen:
        slugs.insert(0, jwt_f)

    return {
        "catalogo_completo": False,
        "multi_faena": False,
        "faenas": [{"slug": s} for s in slugs],
        "motivo": "membresia",
    }


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


def _parse_iso(ts: str | None) -> datetime | None:
    if not ts:
        return None
    try:
        raw = str(ts).replace("Z", "+00:00")
        dt = datetime.fromisoformat(raw)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    except Exception:
        return None


def suscripcion_efectiva(sub: dict[str, Any] | None) -> dict[str, Any]:
    """Ajusta status a canceled si current_period_end ya pasó."""
    if not sub:
        return {"plan_code": "trial", "status": "canceled"}
    out = dict(sub)
    end = _parse_iso(out.get("current_period_end"))
    if end and _utcnow() >= end:
        out["status"] = "canceled"
        out["expired"] = True
    return out


def segundos_restantes_suscripcion(sub: dict[str, Any] | None) -> int | None:
    if not sub:
        return None
    end = _parse_iso(sub.get("current_period_end"))
    if not end:
        return None
    return max(0, int((end - _utcnow()).total_seconds()))


# Demo fija (login SPA) — retirada de prod; seed solo con METGO_SEED_DEMO_PREVIEW=1.
DEMO_PREVIEW_EMAIL = "demo@ventora.demo"
DEMO_PREVIEW_PASSWORD_DEFAULT = "DemoVentora1!"


def demo_preview_password() -> str:
    return (os.getenv("METGO_DEMO_PASSWORD") or DEMO_PREVIEW_PASSWORD_DEFAULT).strip() or DEMO_PREVIEW_PASSWORD_DEFAULT


def crear_usuario_preview(
    *,
    faena: str = "quebrada_blanca",
    horas: float = 1.0,
    label: str | None = None,
) -> tuple[bool, str, dict[str, Any] | None]:
    """Crea usuario temporal: solo Ahora + Panel, TTL horas, luego purge."""
    import secrets
    import string

    faena = (faena or "quebrada_blanca").strip().lower()
    horas = max(0.25, min(float(horas or 1.0), 24.0))
    stamp = _utcnow().strftime("%Y%m%d%H%M%S")
    suffix = "".join(secrets.choice(string.ascii_lowercase + string.digits) for _ in range(4))
    email = f"preview.{faena}.{stamp}.{suffix}@ventora.demo"
    alphabet = string.ascii_letters + string.digits
    password = "Vp!" + "".join(secrets.choice(alphabet) for _ in range(10))
    period_end = (_utcnow() + timedelta(hours=horas)).isoformat()
    feats = features_for_plan("preview")
    now = _utcnow().isoformat()
    org_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())
    sub_id = str(uuid.uuid4())
    meta = {"preview": True, "label": label or "demo_1h", "auto_delete": True}

    if use_memory():
        with _lock:
            _ensure_mem_reglas()
            _MEM["orgs"].append(
                {
                    "id": org_id,
                    "sitio": "spati",
                    "faena": faena,
                    "razon_social_enc": pii_crypto.encrypt_pii("VENTORA Preview"),
                    "rut_enc": pii_crypto.encrypt_pii("76.000.000-0"),
                    "giro": "demo",
                    "created_at": now,
                    "metadata": meta,
                }
            )
            _MEM["usuarios_app"].append(
                {
                    "id": user_id,
                    "email_norm": email,
                    "password_hash": pii_crypto.hash_password(password),
                    "nombres_enc": pii_crypto.encrypt_pii("Preview"),
                    "apellidos_enc": pii_crypto.encrypt_pii(label or "Demo"),
                    "telefono_enc": None,
                    "org_id": org_id,
                    "sitio": "spati",
                    "faena": faena,
                    "role": "operador",
                    "email_verified_at": now,
                    "status": "active",
                    "created_at": now,
                }
            )
            _MEM["suscripciones"].append(
                {
                    "id": sub_id,
                    "org_id": org_id,
                    "sitio": "spati",
                    "faena": faena,
                    "plan_code": "preview",
                    "status": "trialing",
                    "current_period_end": period_end,
                    "seats": 1,
                    "metadata": meta,
                }
            )
            for fk in feats:
                _MEM["entitlements"].append(
                    {
                        "id": str(uuid.uuid4()),
                        "suscripcion_id": sub_id,
                        "feature_key": fk,
                        "enabled": True,
                    }
                )
    else:
        from api_rest.integracion import supabase_store as sb

        org = sb.rest_insert(
            "orgs",
            {
                "id": org_id,
                "sitio": "spati",
                "faena": faena,
                "razon_social_enc": pii_crypto.encrypt_pii("VENTORA Preview"),
                "rut_enc": pii_crypto.encrypt_pii("76.000.000-0"),
                "giro": "demo",
            },
        )
        if not org:
            return False, "No se pudo crear org preview", None
        user = sb.rest_insert(
            "usuarios_app",
            {
                "id": user_id,
                "email_norm": email,
                "password_hash": pii_crypto.hash_password(password),
                "nombres_enc": pii_crypto.encrypt_pii("Preview"),
                "apellidos_enc": pii_crypto.encrypt_pii(label or "Demo"),
                "org_id": org_id,
                "sitio": "spati",
                "faena": faena,
                "role": "operador",
                "email_verified_at": now,
                "status": "active",
            },
        )
        if not user:
            return False, "No se pudo crear usuario preview", None
        sub = sb.rest_insert(
            "suscripciones",
            {
                "id": sub_id,
                "org_id": org_id,
                "sitio": "spati",
                "faena": faena,
                "plan_code": "preview",
                "status": "trialing",
                "current_period_end": period_end,
                "seats": 1,
            },
        )
        if not sub:
            return False, "No se pudo crear suscripción preview", None
        for fk in feats:
            sb.rest_insert(
                "entitlements",
                {"suscripcion_id": sub_id, "feature_key": fk, "enabled": True},
            )

    spa = (os.getenv("METGO_SPATI_PUBLIC_URL") or "https://metgo-spati.pages.dev").rstrip("/")
    return (
        True,
        "Usuario preview creado",
        {
            "email": email,
            "password": password,
            "faena": faena,
            "plan_code": "preview",
            "tabs": ["ahora", "panel"],
            "expires_at": period_end,
            "ttl_hours": horas,
            "org_id": org_id,
            "usuario_id": user_id,
            "login_url": f"{spa}/login?faena={faena}",
            "nota": "Solo Ahora y Panel técnico. Tras 1 h el acceso caduca; purge elimina la org.",
        },
    )


def _org_es_demo_fija(org: dict[str, Any] | None) -> bool:
    if not org:
        return False
    meta = org.get("metadata") or {}
    if isinstance(meta, str):
        return False
    return bool(meta.get("fixed_demo"))


def eliminar_usuario_demo_fijo() -> tuple[bool, str, dict[str, Any] | None]:
    """Elimina la cuenta demo fija (demo@ventora.demo) y su org/suscripción asociadas."""
    email = (os.getenv("METGO_DEMO_EMAIL") or DEMO_PREVIEW_EMAIL).strip().lower() or DEMO_PREVIEW_EMAIL
    known_org = "a0000000-0000-4000-8000-000000000001"

    if use_memory():
        with _lock:
            users = [u for u in _MEM["usuarios_app"] if u.get("email_norm") == email and u.get("sitio") == "spati"]
            org_ids = {str(u.get("org_id")) for u in users if u.get("org_id")}
            org_ids |= {
                str(o.get("id"))
                for o in _MEM["orgs"]
                if _org_es_demo_fija(o) or str(o.get("id")) == known_org
            }
            if not org_ids and not users:
                return True, "Demo ya inexistente", {"email": email, "removed": 0}
            sub_ids = {
                str(s.get("id"))
                for s in _MEM["suscripciones"]
                if str(s.get("org_id")) in org_ids
            }
            _MEM["entitlements"] = [
                e for e in _MEM["entitlements"] if str(e.get("suscripcion_id")) not in sub_ids
            ]
            _MEM["suscripciones"] = [
                s for s in _MEM["suscripciones"] if str(s.get("org_id")) not in org_ids
            ]
            _MEM["usuarios_app"] = [
                u for u in _MEM["usuarios_app"] if str(u.get("org_id")) not in org_ids
            ]
            _MEM["orgs"] = [o for o in _MEM["orgs"] if str(o.get("id")) not in org_ids]
        return True, "Usuario demo eliminado", {"email": email, "removed": len(org_ids), "org_ids": sorted(org_ids)}

    from api_rest.integracion import supabase_store as sb

    users = sb.rest_select(
        "usuarios_app",
        params={"email_norm": f"eq.{email}", "sitio": "eq.spati", "select": "id,org_id"},
        limit=20,
    )
    org_ids = {str(u.get("org_id")) for u in (users or []) if u.get("org_id")}
    org_ids.add(known_org)
    removed = 0
    for oid in sorted(org_ids):
        subs = sb.rest_select(
            "suscripciones",
            params={"org_id": f"eq.{oid}", "select": "id"},
            limit=50,
        )
        for s in subs or []:
            sid = s.get("id")
            if sid:
                sb.rest_delete("entitlements", {"suscripcion_id": f"eq.{sid}"})
        sb.rest_delete("suscripciones", {"org_id": f"eq.{oid}"})
        sb.rest_delete("usuarios_app", {"org_id": f"eq.{oid}"})
        n = sb.rest_delete("orgs", {"id": f"eq.{oid}"})
        removed += int(n or 0)
    # Por si el usuario quedó huérfano sin org conocida
    sb.rest_delete("usuarios_app", {"email_norm": f"eq.{email}", "sitio": "eq.spati"})
    return True, "Usuario demo eliminado", {"email": email, "removed": removed, "org_ids": sorted(org_ids)}


def ensure_usuario_demo_fijo(
    *,
    faena: str = "quebrada_blanca",
    horas: float = 24.0,
) -> tuple[bool, str, dict[str, Any] | None]:
    """Upsert demo fija (solo si ops lo pide explícitamente). Tabs: Ahora + Panel."""
    faena = (faena or "quebrada_blanca").strip().lower()
    horas = max(1.0, min(float(horas or 24.0), 720.0))
    email = (os.getenv("METGO_DEMO_EMAIL") or DEMO_PREVIEW_EMAIL).strip().lower() or DEMO_PREVIEW_EMAIL
    password = demo_preview_password()
    period_end = (_utcnow() + timedelta(hours=horas)).isoformat()
    feats = features_for_plan("preview")
    now = _utcnow().isoformat()
    meta = {
        "preview": True,
        "fixed_demo": True,
        "label": "demo_fijo",
        "auto_delete": False,
    }
    spa = (os.getenv("METGO_SPATI_PUBLIC_URL") or "https://metgo-spati.pages.dev").rstrip("/")
    payload_out = {
        "email": email,
        "password": password,
        "faena": faena,
        "plan_code": "preview",
        "tabs": ["ahora", "panel"],
        "expires_at": period_end,
        "ttl_hours": horas,
        "fixed": True,
        "login_url": f"{spa}/login?faena={faena}",
        "nota": "Usuario demo fijo. Solo Ahora y Panel. No se elimina en purge-preview.",
    }

    if use_memory():
        with _lock:
            _ensure_mem_reglas()
            user = next(
                (u for u in _MEM["usuarios_app"] if u.get("email_norm") == email and u.get("sitio") == "spati"),
                None,
            )
            if user:
                org_id = str(user.get("org_id"))
                user["password_hash"] = pii_crypto.hash_password(password)
                user["faena"] = faena
                user["status"] = "active"
                user["email_verified_at"] = now
                org = next((o for o in _MEM["orgs"] if str(o.get("id")) == org_id), None)
                if org:
                    org["faena"] = faena
                    org["metadata"] = meta
                sub = next(
                    (s for s in _MEM["suscripciones"] if str(s.get("org_id")) == org_id),
                    None,
                )
                if sub:
                    sub["faena"] = faena
                    sub["plan_code"] = "preview"
                    sub["status"] = "trialing"
                    sub["current_period_end"] = period_end
                    sub["metadata"] = meta
                    sub_id = str(sub["id"])
                else:
                    sub_id = str(uuid.uuid4())
                    _MEM["suscripciones"].append(
                        {
                            "id": sub_id,
                            "org_id": org_id,
                            "sitio": "spati",
                            "faena": faena,
                            "plan_code": "preview",
                            "status": "trialing",
                            "current_period_end": period_end,
                            "seats": 1,
                            "metadata": meta,
                        }
                    )
                keep_feats = {e.get("feature_key") for e in _MEM["entitlements"] if e.get("suscripcion_id") == sub_id}
                for fk in feats:
                    if fk not in keep_feats:
                        _MEM["entitlements"].append(
                            {
                                "id": str(uuid.uuid4()),
                                "suscripcion_id": sub_id,
                                "feature_key": fk,
                                "enabled": True,
                            }
                        )
                payload_out["org_id"] = org_id
                payload_out["usuario_id"] = str(user.get("id"))
                payload_out["renewed"] = True
                return True, "Usuario demo renovado", payload_out

            org_id = str(uuid.uuid4())
            user_id = str(uuid.uuid4())
            sub_id = str(uuid.uuid4())
            _MEM["orgs"].append(
                {
                    "id": org_id,
                    "sitio": "spati",
                    "faena": faena,
                    "razon_social_enc": pii_crypto.encrypt_pii("VENTORA Demo"),
                    "rut_enc": pii_crypto.encrypt_pii("76.000.000-0"),
                    "giro": "demo",
                    "created_at": now,
                    "metadata": meta,
                }
            )
            _MEM["usuarios_app"].append(
                {
                    "id": user_id,
                    "email_norm": email,
                    "password_hash": pii_crypto.hash_password(password),
                    "nombres_enc": pii_crypto.encrypt_pii("Demo"),
                    "apellidos_enc": pii_crypto.encrypt_pii("VENTORA"),
                    "telefono_enc": None,
                    "org_id": org_id,
                    "sitio": "spati",
                    "faena": faena,
                    "role": "operador",
                    "email_verified_at": now,
                    "status": "active",
                    "created_at": now,
                }
            )
            _MEM["suscripciones"].append(
                {
                    "id": sub_id,
                    "org_id": org_id,
                    "sitio": "spati",
                    "faena": faena,
                    "plan_code": "preview",
                    "status": "trialing",
                    "current_period_end": period_end,
                    "seats": 1,
                    "metadata": meta,
                }
            )
            for fk in feats:
                _MEM["entitlements"].append(
                    {
                        "id": str(uuid.uuid4()),
                        "suscripcion_id": sub_id,
                        "feature_key": fk,
                        "enabled": True,
                    }
                )
            payload_out["org_id"] = org_id
            payload_out["usuario_id"] = user_id
            payload_out["renewed"] = False
            return True, "Usuario demo creado", payload_out

    from api_rest.integracion import supabase_store as sb

    rows = sb.rest_select(
        "usuarios_app",
        params={"email_norm": f"eq.{email}", "sitio": "eq.spati", "select": "*"},
        limit=1,
    )
    if rows:
        user = rows[0]
        org_id = str(user.get("org_id"))
        sb.rest_patch(
            "usuarios_app",
            {"id": f"eq.{user['id']}"},
            {
                "password_hash": pii_crypto.hash_password(password),
                "faena": faena,
                "status": "active",
                "email_verified_at": now,
            },
        )
        sb.rest_patch(
            "orgs",
            {"id": f"eq.{org_id}"},
            {"faena": faena},
        )
        subs = sb.rest_select(
            "suscripciones",
            params={"org_id": f"eq.{org_id}", "select": "*"},
            limit=5,
        )
        if subs:
            sub_id = str(subs[0]["id"])
            sb.rest_patch(
                "suscripciones",
                {"id": f"eq.{sub_id}"},
                {
                    "faena": faena,
                    "plan_code": "preview",
                    "status": "trialing",
                    "current_period_end": period_end,
                },
            )
        else:
            sub_id = str(uuid.uuid4())
            sb.rest_insert(
                "suscripciones",
                {
                    "id": sub_id,
                    "org_id": org_id,
                    "sitio": "spati",
                    "faena": faena,
                    "plan_code": "preview",
                    "status": "trialing",
                    "current_period_end": period_end,
                    "seats": 1,
                },
            )
            for fk in feats:
                sb.rest_insert(
                    "entitlements",
                    {"suscripcion_id": sub_id, "feature_key": fk, "enabled": True},
                )
        payload_out["org_id"] = org_id
        payload_out["usuario_id"] = str(user.get("id"))
        payload_out["renewed"] = True
        return True, "Usuario demo renovado", payload_out

    org_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())
    sub_id = str(uuid.uuid4())
    if not sb.rest_insert(
        "orgs",
        {
            "id": org_id,
            "sitio": "spati",
            "faena": faena,
            "razon_social_enc": pii_crypto.encrypt_pii("VENTORA Demo"),
            "rut_enc": pii_crypto.encrypt_pii("76.000.000-0"),
            "giro": "demo",
        },
    ):
        return False, "No se pudo crear org demo", None
    if not sb.rest_insert(
        "usuarios_app",
        {
            "id": user_id,
            "email_norm": email,
            "password_hash": pii_crypto.hash_password(password),
            "nombres_enc": pii_crypto.encrypt_pii("Demo"),
            "apellidos_enc": pii_crypto.encrypt_pii("VENTORA"),
            "org_id": org_id,
            "sitio": "spati",
            "faena": faena,
            "role": "operador",
            "email_verified_at": now,
            "status": "active",
        },
    ):
        return False, "No se pudo crear usuario demo", None
    if not sb.rest_insert(
        "suscripciones",
        {
            "id": sub_id,
            "org_id": org_id,
            "sitio": "spati",
            "faena": faena,
            "plan_code": "preview",
            "status": "trialing",
            "current_period_end": period_end,
            "seats": 1,
        },
    ):
        return False, "No se pudo crear suscripción demo", None
    for fk in feats:
        sb.rest_insert(
            "entitlements",
            {"suscripcion_id": sub_id, "feature_key": fk, "enabled": True},
        )
    payload_out["org_id"] = org_id
    payload_out["usuario_id"] = user_id
    payload_out["renewed"] = False
    return True, "Usuario demo creado", payload_out


def purge_preview_expirados() -> dict[str, Any]:
    """Elimina orgs preview cuyo current_period_end ya pasó (salvo demo fija)."""
    purged: list[str] = []
    now = _utcnow()
    if use_memory():
        with _lock:
            expired_orgs: set[str] = set()
            fixed_orgs = {
                str(o.get("id"))
                for o in _MEM["orgs"]
                if _org_es_demo_fija(o)
            }
            for s in _MEM["suscripciones"]:
                if (s.get("plan_code") or "") != "preview":
                    continue
                oid = str(s.get("org_id"))
                if oid in fixed_orgs or (s.get("metadata") or {}).get("fixed_demo"):
                    continue
                end = _parse_iso(s.get("current_period_end"))
                if end and now >= end:
                    expired_orgs.add(oid)
            if not expired_orgs:
                return {"purged": 0, "org_ids": []}
            _MEM["suscripciones"] = [
                s for s in _MEM["suscripciones"] if str(s.get("org_id")) not in expired_orgs
            ]
            keep_subs = {s["id"] for s in _MEM["suscripciones"]}
            _MEM["entitlements"] = [
                e for e in _MEM["entitlements"] if e.get("suscripcion_id") in keep_subs
            ]
            _MEM["usuarios_app"] = [
                u for u in _MEM["usuarios_app"] if str(u.get("org_id")) not in expired_orgs
            ]
            _MEM["orgs"] = [o for o in _MEM["orgs"] if str(o.get("id")) not in expired_orgs]
            purged = sorted(expired_orgs)
        return {"purged": len(purged), "org_ids": purged}

    from api_rest.integracion import supabase_store as sb

    rows = sb.rest_select(
        "suscripciones",
        params={"plan_code": "eq.preview", "select": "id,org_id,current_period_end"},
        limit=200,
    )
    demo_email = (os.getenv("METGO_DEMO_EMAIL") or DEMO_PREVIEW_EMAIL).strip().lower()
    demo_users = sb.rest_select(
        "usuarios_app",
        params={"email_norm": f"eq.{demo_email}", "sitio": "eq.spati", "select": "org_id"},
        limit=5,
    )
    skip_orgs = {str(u.get("org_id")) for u in (demo_users or []) if u.get("org_id")}
    for s in rows or []:
        end = _parse_iso(s.get("current_period_end"))
        oid = s.get("org_id")
        if oid and str(oid) in skip_orgs:
            continue
        if oid and end and now >= end:
            try:
                sb.rest_patch(
                    "suscripciones",
                    {"org_id": f"eq.{oid}"},
                    {"status": "canceled"},
                )
                sb.rest_patch(
                    "usuarios_app",
                    {"org_id": f"eq.{oid}"},
                    {"status": "suspended"},
                )
            except Exception:
                pass
            purged.append(str(oid))
    return {"purged": len(purged), "org_ids": purged}


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
        # ahora hereda de panel (planes legacy sin feature "ahora")
        feat_ok = feat in feats or (feat == "ahora" and "panel" in feats)
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
        "preview": plan_code == "preview",
    }
