#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Emisión DTE — dry-run por defecto. No envía al SII sin certificado y flag explícito."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from config import load_config
from dte_types import build_placeholder_xml, validate_payload

EJEMPLO = {
    "tipo_dte": 39,
    "emisor": {
        "rut": "76123456-0",
        "razon_social": "METGO 3D SpA",
    },
    "receptor": {
        "rut": "66666666-6",
        "razon_social": "Cliente demo",
    },
    "items": [
        {
            "nombre": "Plan Starter METGO — mes",
            "cantidad": 1,
            "precio_unitario": 300000,
        }
    ],
    "monto_total": 300000,
    "referencia": "org_demo_trial",
}


def main() -> int:
    p = argparse.ArgumentParser(description="Scaffold emisión DTE METGO")
    p.add_argument("--dry-run", action="store_true", default=True, help="Solo validar + XML placeholder")
    p.add_argument("--send", action="store_true", help="Intentar firma/envío (requiere cert; aún stub)")
    p.add_argument("--tipo", type=int, default=None, help="Override tipo_dte (33/34/39/41)")
    p.add_argument("--ejemplo", action="store_true", help="Usar payload de ejemplo")
    p.add_argument("--input", help="JSON de entrada")
    p.add_argument("--out", help="Escribir XML a archivo")
    p.add_argument("--folio", type=int, default=1)
    args = p.parse_args()

    if args.ejemplo:
        data = dict(EJEMPLO)
    elif args.input:
        data = json.loads(Path(args.input).read_text(encoding="utf-8"))
    else:
        print("Indique --ejemplo o --input", file=sys.stderr)
        return 2

    if args.tipo is not None:
        data["tipo_dte"] = args.tipo

    cfg = load_config()
    # Completar emisor desde env si falta
    emisor = data.setdefault("emisor", {})
    if cfg.rut_emisor:
        emisor["rut"] = cfg.rut_emisor
    if cfg.razon_emisor:
        emisor["razon_social"] = cfg.razon_emisor

    result = validate_payload(data)
    if not result["ok"]:
        print(json.dumps(result, ensure_ascii=False, indent=2), file=sys.stderr)
        return 1

    xml = build_placeholder_xml(data, folio=args.folio)
    if args.out:
        Path(args.out).write_text(xml, encoding="utf-8")
        print(f"XML escrito: {args.out}")
    else:
        print(xml)

    print(
        json.dumps(
            {
                "ok": True,
                "modo": "send" if args.send else "dry-run",
                "ambiente": cfg.ambiente,
                "puede_firmar": cfg.puede_firmar,
                "listo_emision": cfg.listo_emision,
                "nota": (
                    "Stub: con --send se exigirá certificado; aún no hay cliente SII cableado."
                    if args.send
                    else "Dry-run OK — no se firmó ni se envió al SII."
                ),
            },
            ensure_ascii=False,
            indent=2,
        ),
        file=sys.stderr,
    )

    if args.send:
        if not cfg.listo_emision:
            print(
                "Faltan SII_RUT_EMISOR / SII_CERT_PATH / SII_CERT_PASSWORD para emisión real.",
                file=sys.stderr,
            )
            return 3
        print(
            "TODO: firmar XML con .p12 y enviar a ambiente SII (cert/prod). "
            "Integrar LibreDTE u otro facturador autorizado.",
            file=sys.stderr,
        )
        return 4

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
