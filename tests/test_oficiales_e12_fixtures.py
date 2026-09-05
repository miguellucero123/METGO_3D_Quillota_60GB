# -*- coding: utf-8 -*-
"""E12 fixtures DMC/Agromet resolubles sin docs/."""
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend" / "05_APIs_Externas"))
sys.path.insert(0, str(ROOT / "backend" / "08_Gestion_Datos"))
sys.path.insert(0, str(ROOT))


def test_resolve_csv_dir_fixtures():
    from api_rest.oficiales_service import resolve_csv_dir

    for key in ("METGO_DMC_CSV_DIR", "METGO_AGROMET_CSV_DIR"):
        os.environ.pop(key, None)
    os.environ["METGO_DMC_USE_EJEMPLOS"] = "1"
    os.environ["METGO_AGROMET_USE_EJEMPLOS"] = "1"
    p, origen = resolve_csv_dir("dmc")
    assert origen in ("fixtures", "ejemplos", "env")
    assert p is not None and p.is_dir()
    assert (p / "quillota.csv").is_file()


def test_fetch_dmc_historico_quillota():
    from api_rest.oficiales_service import fetch_dmc_historico

    os.environ.pop("METGO_DMC_CSV_DIR", None)
    os.environ["METGO_DMC_USE_EJEMPLOS"] = "1"
    filas = fetch_dmc_historico("quillota", dias=30)
    assert len(filas) >= 1
    assert "fecha" in filas[0]
