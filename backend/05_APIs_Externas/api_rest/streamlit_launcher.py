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
    """En Render/Railway no se levantan procesos en 127.0.0.1 salvo modo worker explícito."""
    if os.getenv("METGO_STREAMLIT_LOCAL_ONLY", "").lower() in ("0", "false", "no"):
        return False
    if os.getenv("METGO_STREAMLIT_LOCAL_ONLY", "").lower() in ("1", "true", "yes"):
        return True
    return bool(os.getenv("RENDER") or os.getenv("RENDER_SERVICE_ID") or os.getenv("PORT"))


def _cloud_base() -> str | None:
    return catalog.streamlit_cloud_base()


def _url_nube_modulo(modulo_id: str) -> str | None:
    base = _cloud_base()
    if not base:
        return None
    return f"{base}/?activar={modulo_id}"


def _url_visor(modulo_id: str, *, embed: bool = True) -> str | None:
    base = _cloud_base()
    if not base:
        return None
    try:
        from metgo_dashboard_loader import url_visor as _uv
    except ImportError:
        slug = "Visor_de_puerto"
        q = f"id={modulo_id}"
        if embed:
            q += "&embed=true"
        return f"{base.rstrip('/')}/{slug}?{q}"
    return _uv(base, modulo_id, embed=embed)


def _url_local_embed(puerto: int, modulo_id: str) -> str:
    """URL para iframe cuando el proceso Streamlit corre en el puerto local."""
    return f"http://127.0.0.1:{puerto}/?embed=true"


def url_visor_modulo(modulo_id: str) -> dict[str, Any]:
    """URLs del sistema Visor de Puertos (Vue + iframe)."""
    st = estado_servicio(modulo_id)
    if st.get("estado") == "desconocido":
        return {"ok": False, "error": "Modulo no valido", **st}
    modo = "nube" if _api_en_nube() else "local"
    return {
        "ok": True,
        "modulo_id": modulo_id,
        "modo": modo,
        "url_embed": st.get("url_embed") or st.get("url_visor") or st.get("url"),
        "requiere_iniciar_local": modo == "local" and st.get("estado") == "detenido",
        **st,
    }


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


def _campos_comunes(m: dict[str, Any]) -> dict[str, Any]:
    return {
        "utilidad": m.get("utilidad") or m.get("descripcion", ""),
        "ruta_vue_alternativa": m.get("ruta_vue_alternativa"),
        "puerto_etiqueta": f":{m.get('puerto')}",
        "url_local": f"http://127.0.0.1:{m.get('puerto')}",
    }


def estado_servicio(modulo_id: str) -> dict[str, Any]:
    m = _modulo_streamlit(modulo_id)
    if not m:
        return {"id": modulo_id, "estado": "desconocido"}

    puerto = m["puerto"]
    extra = _campos_comunes(m)
    url_nube = _url_nube_modulo(modulo_id)

    url_visor = _url_visor(modulo_id)
    if _api_en_nube():
        if url_nube or url_visor:
            return {
                **m,
                **extra,
                "estado": "disponible_nube",
                "url": url_visor or url_nube,
                "url_nube": url_nube,
                "url_visor": url_visor,
                "url_embed": url_visor,
                "acceso": "nube",
                "mensaje_acceso": (
                    f"Puerto {puerto} en PC local = este módulo Streamlit. "
                    "En internet use el **Visor de puertos** (iframe) o la app Vue."
                ),
            }
        return {
            **m,
            **extra,
            "estado": "solo_local",
            "url": None,
            "url_nube": None,
            "acceso": "local",
            "mensaje_acceso": (
                "Configure METGO_STREAMLIT_CLOUD_URL en la API para abrir el portal en la nube. "
                f"En su PC use el puerto {puerto}."
            ),
        }

    proc = _procesos.get(modulo_id)
    url = f"{catalog.streamlit_host()}:{puerto}"

    url_visor = _url_visor(modulo_id)
    puerto_activo = _puerto_ocupado(puerto)
    url_embed_local = _url_local_embed(puerto, modulo_id) if puerto_activo else None

    if proc and proc.poll() is None:
        return {
            **m,
            **extra,
            "estado": "corriendo",
            "url": url,
            "url_nube": url_nube,
            "url_visor": url_visor,
            "url_embed": url_embed_local or url_visor,
            "pid": proc.pid,
            "acceso": "local",
        }
    if puerto_activo:
        return {
            **m,
            **extra,
            "estado": "corriendo",
            "url": url,
            "url_nube": url_nube,
            "url_visor": url_visor,
            "url_embed": url_embed_local or url_visor,
            "pid": None,
            "externo": True,
            "acceso": "local",
        }
    return {
        **m,
        **extra,
        "estado": "detenido",
        "url": url,
        "url_nube": url_nube,
        "url_visor": url_visor,
        "url_embed": url_visor or url_nube,
        "acceso": "local",
    }


def listar_estados() -> list[dict[str, Any]]:
    return [
        estado_servicio(m["id"])
        for m in catalog.MODULOS_SISTEMA
        if m.get("tipo_acceso") == "streamlit"
    ]


def iniciar(modulo_id: str) -> dict[str, Any]:
    m = _modulo_streamlit(modulo_id)
    if not m:
        return {"ok": False, "error": "Modulo Streamlit no valido"}

    if _api_en_nube():
        visor = _url_visor(modulo_id)
        url_nube = _url_nube_modulo(modulo_id)
        if visor or url_nube:
            st = estado_servicio(modulo_id)
            return {
                "ok": True,
                "modo": "nube",
                "mensaje": (
                    f"Visor listo en la nube (puerto de referencia {m['puerto']} en PC). "
                    "Abra /puertos en Vue para ver integrado."
                ),
                "url": visor or url_nube,
                "url_embed": visor,
                **st,
            }
        return {
            "ok": False,
            "error": (
                "No hay portal Streamlit en la nube configurado (METGO_STREAMLIT_CLOUD_URL). "
                "Use la app Vue o ejecute METGO en su PC."
            ),
            **estado_servicio(modulo_id),
        }

    script = ROOT / m["script"]
    if not script.is_file():
        return {"ok": False, "error": f"Script no encontrado: {m['script']}"}

    puerto = int(m["puerto"])
    st = estado_servicio(modulo_id)
    if st["estado"] == "corriendo":
        return {"ok": True, "mensaje": "Ya estaba en ejecucion", "modo": "local", **st}

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
            return {
                "ok": True,
                "mensaje": "Servicio iniciado",
                "modo": "local",
                **estado_servicio(modulo_id),
            }
        if proc.poll() is not None:
            return {"ok": False, "error": "El proceso Streamlit termino inesperadamente"}

    return {
        "ok": True,
        "mensaje": "Iniciando (puede tardar unos segundos)",
        "modo": "local",
        **estado_servicio(modulo_id),
    }


def detener(modulo_id: str) -> dict[str, Any]:
    m = _modulo_streamlit(modulo_id)
    if not m:
        return {"ok": False, "error": "Modulo no valido"}

    if _api_en_nube():
        return {
            "ok": True,
            "mensaje": "En la nube no hay proceso local que detener; cierre la pestaña del portal.",
            **estado_servicio(modulo_id),
        }

    proc = _procesos.pop(modulo_id, None)
    if proc and proc.poll() is None:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()

    return {
        "ok": True,
        "mensaje": "Proceso detenido (si otro proceso usa el puerto, cierrelo manualmente)",
        **estado_servicio(modulo_id),
    }


def detener_todos() -> dict[str, int]:
    if _api_en_nube():
        return {"detenidos": 0, "mensaje": "Modo nube: no aplica detener procesos locales."}
    ids = list(_procesos.keys())
    for mid in ids:
        detener(mid)
    return {"detenidos": len(ids)}
