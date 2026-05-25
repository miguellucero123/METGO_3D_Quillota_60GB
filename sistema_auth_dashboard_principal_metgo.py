#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Entrypoint legacy en la raíz del repo (Streamlit Cloud suele usar este nombre).

No ejecuta el panel antiguo: delega en streamlit_app.py (Vue embebido si METGO_VUE_URL).
Para forzar el dashboard legacy en local: streamlit run frontend/dashboards/sistema_auth_dashboard_principal_metgo.py
"""
from __future__ import annotations

import runpy
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

runpy.run_path(str(ROOT / "streamlit_app.py"), run_name="__main__")
