#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validación de registro (formato + señales de datos no verídicos)."""

from __future__ import annotations

import re
from typing import Any

_EMAIL_RE = re.compile(r"^[a-z0-9._%+\-]+@[a-z0-9.\-]+\.[a-z]{2,}$", re.I)
_PHONE_CL_RE = re.compile(r"^\+?56\s?9\d{8}$|^\+?56\s?[2-9]\d{7,8}$")
_NAME_RE = re.compile(r"^[A-Za-zÁÉÍÓÚÜÑáéíóúüñ' \-]{2,80}$")
_DISPOSABLE = {
    "mailinator.com",
    "guerrillamail.com",
    "tempmail.com",
    "10minutemail.com",
    "yopmail.com",
}
_PLACEHOLDERS = {
    "test",
    "asdf",
    "qwerty",
    "nombre",
    "apellido",
    "empresa",
    "nada",
    "xxx",
    "aaa",
}


def _norm(s: Any) -> str:
    return " ".join(str(s or "").strip().split())


def validar_rut_chileno(rut: str) -> bool:
    raw = re.sub(r"[^0-9kK]", "", (rut or "").strip())
    if len(raw) < 2:
        return False
    cuerpo, dv = raw[:-1], raw[-1].upper()
    if not cuerpo.isdigit():
        return False
    s, m = 0, 2
    for c in reversed(cuerpo):
        s += int(c) * m
        m = 2 if m == 7 else m + 1
    resto = 11 - (s % 11)
    expect = "0" if resto == 11 else ("K" if resto == 10 else str(resto))
    return dv == expect


def _pwd_ok(password: str) -> list[str]:
    errs: list[str] = []
    if len(password or "") < 10:
        errs.append("Mínimo 10 caracteres")
    if not re.search(r"[A-ZÁÉÍÓÚÜÑ]", password or ""):
        errs.append("Debe incluir mayúscula")
    if not re.search(r"[a-záéíóúüñ]", password or ""):
        errs.append("Debe incluir minúscula")
    if not re.search(r"\d", password or ""):
        errs.append("Debe incluir número")
    return errs


def validate_registro_payload(data: dict[str, Any]) -> dict[str, Any]:
    """Dry-run / pre-check. Devuelve {ok, errors, warnings}."""
    errors: dict[str, list[str]] = {}
    warnings: list[str] = []

    def add(field: str, msg: str) -> None:
        errors.setdefault(field, []).append(msg)

    email = _norm(data.get("email") or data.get("correo")).lower()
    nombres = _norm(data.get("nombres") or data.get("nombre"))
    apellidos = _norm(data.get("apellidos") or data.get("apellido"))
    telefono = re.sub(r"\s+", "", _norm(data.get("telefono") or data.get("phone")))
    password = data.get("password") or data.get("contraseña") or data.get("contrasena") or ""
    password2 = data.get("password_confirm") or data.get("password2") or password
    razon = _norm(data.get("razon_social") or data.get("empresa"))
    rut = _norm(data.get("rut") or data.get("rut_empresa"))
    sitio = _norm(data.get("sitio") or data.get("site")).lower()
    faena = _norm(data.get("faena") or "").lower() or None
    cons = data.get("consentimientos") or data.get("consents") or {}

    if not email or not _EMAIL_RE.match(email):
        add("email", "Email inválido")
    else:
        domain = email.split("@", 1)[-1].lower()
        if domain in _DISPOSABLE:
            add("email", "No se aceptan correos temporales")

    if not _NAME_RE.match(nombres or ""):
        add("nombres", "Nombres inválidos")
    elif nombres.lower() in _PLACEHOLDERS:
        add("nombres", "Parece un valor de prueba, use el nombre real")

    if not _NAME_RE.match(apellidos or ""):
        add("apellidos", "Apellidos inválidos")
    elif apellidos.lower() in _PLACEHOLDERS:
        add("apellidos", "Parece un valor de prueba, use apellidos reales")

    if telefono and not _PHONE_CL_RE.match(telefono):
        add("telefono", "Teléfono debe ser formato Chile (+56…)")

    for msg in _pwd_ok(str(password)):
        add("password", msg)
    if password != password2:
        add("password_confirm", "Las contraseñas no coinciden")

    if len(razon) < 3:
        add("razon_social", "Razón social requerida")
    elif razon.lower() in _PLACEHOLDERS:
        add("razon_social", "Indique la razón social real de la empresa")

    if not validar_rut_chileno(rut):
        add("rut", "RUT chileno inválido (dígito verificador)")

    if not sitio:
        add("sitio", "Sitio/producto requerido")

    if sitio == "spati" and not faena:
        add("faena", "En SPATI debe indicar la faena (ej. escondida)")

    required_cons = ("almacenamiento_datos", "tos", "privacy", "veracidad")
    if not isinstance(cons, dict):
        add("consentimientos", "Debe enviar objeto consentimientos")
    else:
        for k in required_cons:
            if cons.get(k) is not True:
                add(
                    "consentimientos",
                    f"Debe aceptar '{k}' (guardar datos / términos / privacidad / veracidad)",
                )

    if email and nombres and email.split("@")[0].lower() in {
        nombres.lower().replace(" ", ""),
        "admin",
        "user",
    }:
        warnings.append("Revise que el email corporativo sea el correcto")

    return {"ok": not errors, "errors": errors, "warnings": warnings}
