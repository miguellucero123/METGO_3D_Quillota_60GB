#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Valida un JSON de boleta/factura (sin emitir)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from dte_types import validate_payload


def main() -> int:
    p = argparse.ArgumentParser(description="Validar payload DTE METGO")
    p.add_argument("--input", required=True, help="Ruta JSON")
    args = p.parse_args()
    path = Path(args.input)
    if not path.is_file():
        print(f"No existe: {path}", file=sys.stderr)
        return 2
    data = json.loads(path.read_text(encoding="utf-8"))
    result = validate_payload(data)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
