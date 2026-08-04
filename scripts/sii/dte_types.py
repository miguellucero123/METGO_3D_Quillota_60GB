#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tipos DTE y validación básica de payload (Chile)."""

from __future__ import annotations

import re
from typing import Any

DTE_TIPOS = {
    33: "Factura electrónica",
    34: "Factura exenta electrónica",
    39: "Boleta electrónica",
    41: "Boleta exenta electrónica",
}

_RUT_RE = re.compile(r"^\d{1,8}-[\dkK]$")


def normalizar_rut(rut: str) -> str:
    r = (rut or "").strip().upper().replace(".", "").replace(" ", "")
    if "-" not in r and len(r) > 1:
        r = f"{r[:-1]}-{r[-1]}"
    return r


def validar_dv_rut(rut: str) -> bool:
    """Valida dígito verificador chileno."""
    r = normalizar_rut(rut)
    if not _RUT_RE.match(r):
        return False
    cuerpo, dv = r.split("-")
    try:
        nums = list(map(int, reversed(cuerpo)))
    except ValueError:
        return False
    factors = [2, 3, 4, 5, 6, 7]
    s = sum(n * factors[i % 6] for i, n in enumerate(nums))
    resto = 11 - (s % 11)
    esperado = "0" if resto == 11 else "K" if resto == 10 else str(resto)
    return dv == esperado


def validate_payload(data: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    tipo = data.get("tipo_dte")
    try:
        tipo_i = int(tipo)
    except (TypeError, ValueError):
        tipo_i = None
    if tipo_i not in DTE_TIPOS:
        errors.append(f"tipo_dte inválido (permitidos: {sorted(DTE_TIPOS)})")

    emisor = data.get("emisor") or {}
    receptor = data.get("receptor") or {}
    for label, bloque in (("emisor", emisor), ("receptor", receptor)):
        rut = normalizar_rut(str(bloque.get("rut") or ""))
        if not rut:
            errors.append(f"{label}.rut requerido")
        elif not validar_dv_rut(rut):
            errors.append(f"{label}.rut DV inválido: {rut}")
        if not (bloque.get("razon_social") or "").strip():
            errors.append(f"{label}.razon_social requerida")

    items = data.get("items") or []
    if not items:
        errors.append("items: al menos una línea")
    total = 0.0
    for i, it in enumerate(items):
        try:
            cant = float(it.get("cantidad") or 0)
            precio = float(it.get("precio_unitario") or 0)
        except (TypeError, ValueError):
            errors.append(f"items[{i}]: cantidad/precio inválidos")
            continue
        if cant <= 0 or precio < 0:
            errors.append(f"items[{i}]: cantidad > 0 y precio >= 0")
        total += cant * precio
    if data.get("monto_total") is not None:
        try:
            if abs(float(data["monto_total"]) - total) > 0.5:
                errors.append("monto_total no cuadra con suma de ítems")
        except (TypeError, ValueError):
            errors.append("monto_total inválido")

    return {
        "ok": not errors,
        "errors": errors,
        "tipo_nombre": DTE_TIPOS.get(tipo_i or -1),
        "monto_calculado": round(total),
    }


def build_placeholder_xml(data: dict[str, Any], folio: int = 1) -> str:
    """XML ilustrativo — NO válido para SII (sin firma / sin esquema real)."""
    tipo = int(data.get("tipo_dte") or 39)
    emisor = data.get("emisor") or {}
    receptor = data.get("receptor") or {}
    items_xml = []
    for i, it in enumerate(data.get("items") or [], start=1):
        items_xml.append(
            f'  <Detalle NroLinDet="{i}">'
            f"<NmbItem>{it.get('nombre', 'Item')}</NmbItem>"
            f"<QtyItem>{it.get('cantidad', 1)}</QtyItem>"
            f"<PrcItem>{it.get('precio_unitario', 0)}</PrcItem>"
            f"</Detalle>"
        )
    return (
        '<?xml version="1.0" encoding="ISO-8859-1"?>\n'
        f"<!-- PLACEHOLDER METGO — no firmar ni enviar al SII -->\n"
        f'<DTE version="1.0">\n'
        f'  <Documento ID="F{folio}T{tipo}">\n'
        f"    <TipoDTE>{tipo}</TipoDTE>\n"
        f"    <Folio>{folio}</Folio>\n"
        f"    <EmisorRUT>{normalizar_rut(str(emisor.get('rut') or ''))}</EmisorRUT>\n"
        f"    <EmisorRzn>{emisor.get('razon_social') or ''}</EmisorRzn>\n"
        f"    <ReceptorRUT>{normalizar_rut(str(receptor.get('rut') or ''))}</ReceptorRUT>\n"
        f"    <ReceptorRzn>{receptor.get('razon_social') or ''}</ReceptorRzn>\n"
        + "\n".join(items_xml)
        + "\n  </Documento>\n</DTE>\n"
    )
