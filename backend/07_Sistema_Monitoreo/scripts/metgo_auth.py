#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Autenticacion compartida METGO (Streamlit + API REST JWT).
Credenciales: METGO_PASSWORD_{USUARIO} en mayúsculas.
Roles: admin | agronomo | operador | lectura
"""

from __future__ import annotations

import os
import warnings
from datetime import datetime, timedelta, timezone
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
    "user": "operador",
    "metgo": "agronomo",
    "agronomo": "agronomo",
    "operador": "operador",
    "lector": "lectura",
}

USUARIOS_VALIDOS = tuple(USER_TO_ROLE.keys())

ROLE_HIERARCHY = ("admin", "agronomo", "operador", "lectura")

_DEV_FALLBACK = {
    "admin": "admin123",
    "user": "user123",
    "metgo": "metgo2025",
    "agronomo": "agro123",
    "operador": "op123",
    "lector": "lec123",
}

_warned_dev = False


def rol_de_usuario(usuario: str) -> str:
    return USER_TO_ROLE.get(usuario.lower().strip(), "lectura")


def tenant_de_usuario(usuario: str) -> str | None:
    """None = admin ve todos los tenants."""
    try:
        from api_rest.tenants import tenant_de_usuario as _t

        return _t(usuario)
    except ImportError:
        return "quillota" if usuario != "admin" else None


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
    if usuario not in USUARIOS_VALIDOS:
        return None
    env_key = f"METGO_PASSWORD_{usuario.upper()}"
    value = os.getenv(env_key)
    if value:
        return value
    if usuario in _DEV_FALLBACK:
        _warn_dev_fallback()
        return _DEV_FALLBACK[usuario]
    return None


def verificar_credenciales(usuario: str, contraseña: str) -> bool:
    if not usuario or not contraseña:
        return False
    esperada = obtener_password(usuario)
    return esperada is not None and esperada == contraseña


def jwt_secret() -> str:
    secret = os.getenv("METGO_JWT_SECRET")
    if secret:
        return secret
    _warn_dev_fallback()
    return os.getenv("METGO_JWT_SECRET_DEV", "metgo-dev-jwt-change-in-production")


def jwt_expiration_seconds() -> int:
    return int(os.getenv("METGO_JWT_EXPIRATION_SECONDS", "3600"))


def jwt_algorithm() -> str:
    return os.getenv("METGO_JWT_ALGORITHM", "HS256")


def crear_token_acceso(usuario: str) -> dict[str, Any]:
    if jwt is None:
        raise RuntimeError("Instale PyJWT: pip install PyJWT")

    usuario = usuario.lower().strip()
    if usuario not in USUARIOS_VALIDOS:
        raise ValueError("Usuario no permitido")

    role = rol_de_usuario(usuario)
    tenant = tenant_de_usuario(usuario)
    exp_secs = jwt_expiration_seconds()
    now = datetime.now(timezone.utc)
    payload = {
        "sub": usuario,
        "role": role,
        "tenant": tenant,
        "iat": now,
        "exp": now + timedelta(seconds=exp_secs),
    }
    token = jwt.encode(payload, jwt_secret(), algorithm=jwt_algorithm())
    if isinstance(token, bytes):
        token = token.decode("utf-8")

    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": exp_secs,
        "user": {"username": usuario, "role": role, "tenant": tenant},
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
