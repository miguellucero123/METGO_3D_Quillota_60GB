#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Autenticacion compartida METGO (Streamlit + API REST JWT).
Credenciales: METGO_PASSWORD_{USUARIO} en mayúsculas.
Roles: admin | agronomo | operador | lectura
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import warnings
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

try:
    import jwt
except ImportError:
    jwt = None  # type: ignore

# Usuario de login -> rol JWT
USER_TO_ROLE: dict[str, str] = {
    "admin": "admin",
    "admin@metgo3d.com": "admin",
    "user": "operador",
    "user@metgo3d.com": "operador",
    "metgo": "agronomo",
    "metgo@metgo3d.com": "agronomo",
    "agronomo": "agronomo",
    "agronomo@metgo3d.com": "agronomo",
    "operador": "operador",
    "operador@metgo3d.com": "operador",
    "lector": "lectura",
    "lector@metgo3d.com": "lectura",
    # E9 — demos por sitio de producto
    "copiapo": "lectura",
    "copiapo@metgo3d.com": "lectura",
    "mantos": "operador",
    "mantos@metgo3d.com": "operador",
    "paine": "lectura",
    "paine@metgo3d.com": "lectura",
}

USUARIOS_VALIDOS = tuple(USER_TO_ROLE.keys())

ROLE_HIERARCHY = ("admin", "agronomo", "operador", "lectura")

_DEV_FALLBACK = {
    "admin": "admin123",
    "admin@metgo3d.com": "admin123",
    "user": "user123",
    "user@metgo3d.com": "user123",
    "metgo": "metgo2025",
    "metgo@metgo3d.com": "metgo2025",
    "agronomo": "agro123",
    "agronomo@metgo3d.com": "agro123",
    "operador": "op123",
    "operador@metgo3d.com": "op123",
    "lector": "lec123",
    "lector@metgo3d.com": "lec123",
    "copiapo": "copiapo123",
    "copiapo@metgo3d.com": "copiapo123",
    "mantos": "mantos123",
    "mantos@metgo3d.com": "mantos123",
    "paine": "paine123",
    "paine@metgo3d.com": "paine123",
}

_warned_dev = False

_USERNAME_RE = re.compile(r"^[a-z0-9_]{3,32}$")


def es_entorno_produccion() -> bool:
    """True en Render o METGO_ENV=production|prod."""
    env = (os.getenv("METGO_ENV") or "").strip().lower()
    if env in ("production", "prod"):
        return True
    return bool(os.getenv("RENDER"))


def self_register_habilitado() -> bool:
    """Default off. Activar solo con METGO_ALLOW_SELF_REGISTER=1 (local/demo)."""
    return os.getenv("METGO_ALLOW_SELF_REGISTER", "0") == "1"


def _registry_path() -> Path:
    for p in Path(__file__).resolve().parents:
        if (p / "metgo_paths.py").exists():
            gd = p / "backend" / "08_Gestion_Datos" / "datos_runtime"
            gd.mkdir(parents=True, exist_ok=True)
            return gd / "usuarios_registrados.json"
    return Path("usuarios_registrados.json")


def cargar_usuarios_registrados() -> dict[str, dict[str, Any]]:
    path = _registry_path()
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (json.JSONDecodeError, OSError):
        return {}


def _hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def usuario_existe(usuario: str) -> bool:
    u = usuario.lower().strip()
    return u in USER_TO_ROLE or u in cargar_usuarios_registrados()


def registrar_usuario(
    usuario: str,
    contraseña: str,
    email: str | None = None,
    sitio: str | None = None,
) -> tuple[bool, str]:
    """Auto-registro (rol lectura). Requiere METGO_ALLOW_SELF_REGISTER=1."""
    if not self_register_habilitado():
        return False, "Registro deshabilitado en este entorno"

    u = usuario.lower().strip()
    if not _USERNAME_RE.match(u):
        return (
            False,
            "Usuario inválido (3-32 caracteres: letras minúsculas, números, _)",
        )
    if u in USER_TO_ROLE:
        return False, "Nombre de usuario reservado del sistema"
    if u in cargar_usuarios_registrados():
        return False, "El usuario ya existe"
    if len(contraseña or "") < 6:
        return False, "La contraseña debe tener al menos 6 caracteres"

    sitio_reg = (sitio or os.getenv("METGO_SITIO_DEFAULT", "quillota") or "quillota").strip().lower()
    try:
        from api_rest.estaciones_catalogo import ESTACIONES_POR_SITIO

        if sitio_reg not in ESTACIONES_POR_SITIO:
            return False, f"Sitio desconocido: {sitio_reg}"
    except ImportError:
        pass

    reg = cargar_usuarios_registrados()
    reg[u] = {
        "password_hash": _hash_password(contraseña),
        "email": (email or "").strip() or None,
        "role": "lectura",
        "sitio": sitio_reg,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    path = _registry_path()
    path.write_text(json.dumps(reg, indent=2, ensure_ascii=False), encoding="utf-8")
    return True, "Usuario registrado correctamente"


def rol_de_usuario(usuario: str) -> str:
    u = usuario.lower().strip()
    if u in USER_TO_ROLE:
        return USER_TO_ROLE[u]
    if u in cargar_usuarios_registrados():
        return str(cargar_usuarios_registrados()[u].get("role") or "lectura")
    return "lectura"


def tenant_de_usuario(usuario: str) -> str | None:
    """None = admin ve todos los tenants."""
    try:
        from api_rest.tenants import tenant_de_usuario as _t

        return _t(usuario)
    except ImportError:
        return "quillota" if usuario != "admin" else None


def sitio_de_usuario(usuario: str) -> str | None:
    """E9: sitio de producto. None = admin global."""
    u = usuario.lower().strip()
    # Preferir sitio guardado en registro
    reg = cargar_usuarios_registrados()
    if u in reg and reg[u].get("sitio"):
        return str(reg[u]["sitio"]).lower().strip()
    try:
        from api_rest.sitios_auth import sitio_de_usuario as _s

        return _s(usuario)
    except ImportError:
        return tenant_de_usuario(usuario)


def rol_permitido(user_role: str, roles_requeridos: tuple[str, ...]) -> bool:
    if user_role == "admin":
        return True
    return user_role in roles_requeridos


def _warn_dev_fallback() -> None:
    global _warned_dev
    if not _warned_dev:
        warnings.warn(
            "METGO: usando contraseñas de desarrollo. "
            "Defina METGO_PASSWORD_* en el entorno.",
            stacklevel=3,
        )
        _warned_dev = True


def obtener_password(usuario: str) -> str | None:
    usuario = usuario.lower().strip()
    if usuario in cargar_usuarios_registrados():
        return None
    if usuario not in USUARIOS_VALIDOS:
        return None
        
    base_user = usuario.split("@")[0]
    env_key = f"METGO_PASSWORD_{base_user.upper()}"
    value = os.getenv(env_key)
    if value:
        return value
        
    # Fase 1: Se habilita temporalmente el fallback demo incluso en producción
    # para permitir acceso inmediato a las plataformas satélite (spati, ventora, etc.)
    if usuario in _DEV_FALLBACK:
        _warn_dev_fallback()
        return _DEV_FALLBACK[usuario]
    return None


def verificar_credenciales(usuario: str, contraseña: str) -> bool:
    if not usuario or not contraseña:
        return False
    u = usuario.lower().strip()
    reg = cargar_usuarios_registrados()
    if u in reg:
        return reg[u].get("password_hash") == _hash_password(contraseña)
    esperada = obtener_password(u)
    return esperada is not None and esperada == contraseña


def jwt_secret() -> str:
    secret = os.getenv("METGO_JWT_SECRET")
    if secret:
        return secret
    if es_entorno_produccion():
        raise RuntimeError(
            "METGO_JWT_SECRET es obligatorio en producción (RENDER / METGO_ENV=production)"
        )
    _warn_dev_fallback()
    return os.getenv("METGO_JWT_SECRET_DEV", "metgo-dev-jwt-change-in-production")


def jwt_expiration_seconds() -> int:
    return int(os.getenv("METGO_JWT_EXPIRATION_SECONDS", "3600"))


def jwt_algorithm() -> str:
    return os.getenv("METGO_JWT_ALGORITHM", "HS256")


def crear_token_acceso(usuario: str, sitio: str | None = None) -> dict[str, Any]:
    if jwt is None:
        raise RuntimeError("Instale PyJWT: pip install PyJWT")

    import uuid

    usuario = usuario.lower().strip()
    if not usuario_existe(usuario):
        raise ValueError("Usuario no permitido")

    role = rol_de_usuario(usuario)
    tenant = tenant_de_usuario(usuario)

    # E9: sitio de producto (quillota|paine|copiapo|mantos_blancos|…).
    sitio_efectivo = sitio if sitio is not None else sitio_de_usuario(usuario)
    exp_secs = jwt_expiration_seconds()
    now = datetime.now(timezone.utc)
    jti = str(uuid.uuid4())
    payload = {
        "sub": usuario,
        "role": role,
        "tenant": tenant,  # legacy Fase 3.3 (mapa geográfico)
        "sitio": sitio_efectivo,  # E9 producto/sitio
        "jti": jti,
        "iat": now,
        "exp": now + timedelta(seconds=exp_secs),
    }
    token = jwt.encode(payload, jwt_secret(), algorithm=jwt_algorithm())
    if isinstance(token, bytes):
        token = token.decode("utf-8")

    try:
        from api_rest.identity.session_store import register_session

        register_session(usuario, jti)
    except Exception:
        pass

    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": exp_secs,
        "user": {
            "username": usuario,
            "role": role,
            "tenant": tenant,
            "sitio": sitio_efectivo,
        },
    }


def crear_token_identidad(
    *,
    sub: str,
    role: str,
    sitio: str | None,
    faena: str | None = None,
    org_id: str | None = None,
    plan_code: str | None = None,
    sub_status: str | None = None,
    expires_in: int | None = None,
) -> dict[str, Any]:
    """JWT para usuarios comerciales (usuarios_app), sin USER_TO_ROLE."""
    if jwt is None:
        raise RuntimeError("Instale PyJWT: pip install PyJWT")
    import uuid

    exp_secs = int(expires_in) if expires_in is not None else jwt_expiration_seconds()
    exp_secs = max(60, min(exp_secs, jwt_expiration_seconds()))
    now = datetime.now(timezone.utc)
    sub_n = (sub or "").lower().strip()
    jti = str(uuid.uuid4())
    payload: dict[str, Any] = {
        "sub": sub_n,
        "role": role or "operador",
        "tenant": None,
        "sitio": sitio,
        "faena": faena,
        "org_id": org_id,
        "plan_code": plan_code or "trial",
        "sub_status": sub_status or "trialing",
        "jti": jti,
        "iat": now,
        "exp": now + timedelta(seconds=exp_secs),
    }
    token = jwt.encode(payload, jwt_secret(), algorithm=jwt_algorithm())
    if isinstance(token, bytes):
        token = token.decode("utf-8")
    try:
        from api_rest.identity.session_store import register_session

        register_session(sub_n, jti)
    except Exception:
        pass
    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": exp_secs,
        "user": {
            "username": sub_n,
            "email": sub_n,
            "role": role or "operador",
            "sitio": sitio,
            "faena": faena,
            "org_id": org_id,
            "plan_code": plan_code or "trial",
            "sub_status": sub_status or "trialing",
        },
    }


def decodificar_token(token: str) -> dict[str, Any] | None:
    if jwt is None or not token:
        return None
    try:
        return jwt.decode(
            token,
            jwt_secret(),
            algorithms=[jwt_algorithm()],
        )
    except jwt.PyJWTError:
        return None
