#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Túnel ngrok para exponer el dashboard público METGO (site-web).
No confundir con dashboard_web_publico.py (Streamlit sin ngrok).
"""

from __future__ import annotations

import os
import subprocess
import sys
import threading
import time
import urllib.request
from pathlib import Path

_root = Path(__file__).resolve()
for _p in _root.parents:
    if (_p / "metgo_paths.py").exists():
        PROJECT_ROOT = _p
        break
else:
    raise RuntimeError("No se encontró metgo_paths.py")

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import metgo_paths

DASHBOARD = metgo_paths.site_web_streamlit_path("dashboard_web_publico.py")
PORT = os.getenv("METGO_PUBLIC_PORT", "8505")


def verificar_ngrok() -> bool:
    try:
        subprocess.run(["ngrok", "version"], capture_output=True, text=True, shell=True)
        return True
    except Exception:
        return False


def ejecutar_streamlit() -> None:
    comando = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        str(DASHBOARD),
        f"--server.port={PORT}",
        "--server.address=127.0.0.1",
        "--server.headless=true",
    ]
    subprocess.run(comando, cwd=str(PROJECT_ROOT))


def ejecutar_ngrok() -> None:
    subprocess.run(["ngrok", "http", PORT, "--log=stdout"], shell=True)


def main() -> None:
    print("METGO — túnel ngrok para dashboard público")
    if not verificar_ngrok():
        print("Instale ngrok: https://ngrok.com/download")
        print(f"Ejecutando solo Streamlit en http://127.0.0.1:{PORT}")
        ejecutar_streamlit()
        return

    threading.Thread(target=ejecutar_streamlit, daemon=True).start()
    time.sleep(5)
    threading.Thread(target=ejecutar_ngrok, daemon=True).start()
    print(f"Local: http://127.0.0.1:{PORT}")
    print("Panel ngrok: http://127.0.0.1:4040")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Detenido.")


if __name__ == "__main__":
    main()
