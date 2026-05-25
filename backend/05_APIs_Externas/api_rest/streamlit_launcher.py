#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Arranque bajo demanda de dashboards Streamlit desde la API METGO."""

from __future__ import annotations

import os
import socket
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

from api_rest import catalog


def _api_en_nube() -> bool:
    """En Render/Railway no se pueden levantar Streamlit locales en 127.0.0.1."""
    if os.getenv("METGO_STREAMLIT_LOCAL_ONLY", "").lower() in ("0", "false", "no"):
        return False
    if os.getenv("METGO_STREAMLIT_LOCAL_ONLY", "").lower() in ("1", "true", "yes"):
        return True
    return bool(os.getenv("RENDER") or os.getenv("RENDER_SERVICE_ID") or os.getenv("PORT"))

ROOT = Path(__file__).resolve().parent
for _p in Path(__file__).resolve().parents:
    if (_p / "metgo_paths.py").exists():
        ROOT = _p
        break
_procesos: dict[str, subprocess.Popen] = {}


def _puerto_ocupado(puerto: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.3)
        return s.connect_ex(("127.0.0.1", puerto)) == 0


def _modulo_streamlit(modulo_id: str) -> dict[str, Any] | None:
    m = catalog.obtener_modulo(modulo_id)
    if not m or m.get("tipo_acceso") != "streamlit":
        return None
    return m


def estado_servicio(modulo_id: str) -> dict[str, Any]:
    m = _modulo_streamlit(modulo_id)
    if not m:
        return {"id": modulo_id, "estado": "desconocido"}

    puerto = m["puerto"]
    url = f"{catalog.streamlit_host()}:{puerto}"
    if _api_en_nube():
        return {
            **m,
            "estado": "solo_local",
            "url": None,
            "acceso": "local",
            "mensaje_acceso": (
                "Este dashboard Streamlit corre en su PC (puerto "
                f"{puerto}), no en la nube. Use la app Vue o ejecute METGO en local."
            ),
        }

    proc = _procesos.get(modulo_id)

    if proc and proc.poll() is None:
        return {**m, "estado": "corriendo", "url": url, "pid": proc.pid}
    if _puerto_ocupado(puerto):
        return {**m, "estado": "corriendo", "url": url, "pid": None, "externo": True}
    return {**m, "estado": "detenido", "url": url}


def listar_estados() -> list[dict[str, Any]]:
    return [estado_servicio(m["id"]) for m in catalog.MODULOS_SISTEMA if m.get("tipo_acceso") == "streamlit"]


def iniciar(modulo_id: str) -> dict[str, Any]:
    m = _modulo_streamlit(modulo_id)
    if not m:
        return {"ok": False, "error": "Modulo Streamlit no valido"}

    if _api_en_nube():
        return {
            "ok": False,
            "error": (
                "No se puede iniciar Streamlit en el servidor cloud. "
                "Ejecute METGO en su computador (API + Vue local) o use solo la pestaña App Vue."
            ),
            **estado_servicio(modulo_id),
        }

    script = ROOT / m["script"]
    if not script.is_file():
        return {"ok": False, "error": f"Script no encontrado: {m['script']}"}

    puerto = int(m["puerto"])
    st = estado_servicio(modulo_id)
    if st["estado"] == "corriendo":
        return {"ok": True, "mensaje": "Ya estaba en ejecucion", **st}

    cmd = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        str(script),
        "--server.port",
        str(puerto),
        "--server.headless",
        "true",
        "--server.address",
        "127.0.0.1",
    ]
    proc = subprocess.Popen(
        cmd,
        cwd=str(ROOT),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == "win32" else 0,
    )
    _procesos[modulo_id] = proc

    for _ in range(15):
        time.sleep(0.4)
        if _puerto_ocupado(puerto):
            return {"ok": True, "mensaje": "Servicio iniciado", **estado_servicio(modulo_id)}
        if proc.poll() is not None:
            return {"ok": False, "error": "El proceso Streamlit termino inesperadamente"}

    return {"ok": True, "mensaje": "Iniciando (puede tardar unos segundos)", **estado_servicio(modulo_id)}


def detener(modulo_id: str) -> dict[str, Any]:
    m = _modulo_streamlit(modulo_id)
    if not m:
        return {"ok": False, "error": "Modulo no valido"}

    proc = _procesos.pop(modulo_id, None)
    if proc and proc.poll() is None:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()

    return {"ok": True, "mensaje": "Proceso detenido (si otro proceso usa el puerto, cierrelo manualmente)", **estado_servicio(modulo_id)}


def detener_todos() -> dict[str, int]:
    ids = list(_procesos.keys())
    for mid in ids:
        detener(mid)
    return {"detenidos": len(ids)}
