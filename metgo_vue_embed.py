# -*- coding: utf-8 -*-
"""
Embeber la SPA Vue dentro de Streamlit (local o Cloud).

Requiere Vue publicado en una URL accesible (Vercel, Netlify, etc.).
En Streamlit Cloud: Secrets → METGO_VUE_URL = https://tu-app.vercel.app
"""

from __future__ import annotations

import os
from typing import Optional
from urllib.parse import urljoin

import streamlit as st
import streamlit.components.v1 as components

from metgo_streamlit_theme import is_streamlit_cloud

DEFAULT_LOCAL_VUE = "http://127.0.0.1:5173"

ROUTES = {
    "Centro de servicios": "/servicios",
    "Catálogo de módulos": "/modulos",
    "Panel general": "/",
    "Meteorología": "/meteo",
    "Agricultura": "/agricola",
    "Alertas": "/monitoreo",
    "Configuración": "/configuracion",
    "Ingresar": "/login",
}


def get_vue_base_url() -> str:
    """URL base de Vue (sin barra final). Vacío si no está configurada en Cloud."""
    url = (os.getenv("METGO_VUE_URL") or "").strip()
    if not url:
        try:
            url = (st.secrets.get("METGO_VUE_URL") or "").strip()
            if not url:
                general = st.secrets.get("general")
                if general and hasattr(general, "get"):
                    url = (general.get("METGO_VUE_URL") or "").strip()
        except Exception:
            url = ""
    if not url and not is_streamlit_cloud():
        return DEFAULT_LOCAL_VUE.rstrip("/")
    return url.rstrip("/")


def build_vue_url(path: str = "/servicios", *, embed: bool = True) -> str:
    base = get_vue_base_url()
    if not base:
        return ""
    if not path.startswith("/"):
        path = "/" + path
    url = urljoin(base + "/", path.lstrip("/"))
    if embed and "embed=1" not in url:
        sep = "&" if "?" in url else "?"
        url = f"{url}{sep}embed=1"
    return url


def render_vue_iframe(
    path: str = "/servicios",
    *,
    height: int = 820,
    scrolling: bool = True,
) -> bool:
    """
    Muestra Vue en un iframe. Devuelve True si se renderizó el iframe.
    """
    src = build_vue_url(path)
    if not src:
        st.error(
            "Vue no está publicado en internet. Streamlit Cloud no puede cargar "
            "`http://127.0.0.1:5173`."
        )
        st.markdown(
            """
**Pasos:**

1. Despliegue `frontend/vue` en [Netlify](https://www.netlify.com) (ver `docs/manuales/DESPLIEGUE_VUE_NETLIFY.md`).
2. En Streamlit Cloud → **Settings → Secrets** añada:

```toml
METGO_VUE_URL = "https://su-sitio.netlify.app"
```

3. **Reboot app** y abra esta página de nuevo.

La API REST (`:8080`) debe estar en un host público y `METGO_CORS_ORIGINS` debe incluir la URL de Vue.
            """
        )
        return False

    if is_streamlit_cloud():
        st.caption(f"Vista embebida: `{src}`")
    else:
        st.caption(
            f"Vista embebida: `{src}` — en local, ejecute `npm run dev` en `frontend/vue` "
            "y la API en el puerto 8080."
        )

    components.iframe(src, height=height, scrolling=scrolling)
    return True


def vue_url_config_hint() -> None:
    """Muestra ayuda si falta METGO_VUE_URL en Cloud."""
    if get_vue_base_url():
        return
    st.warning(
        "Configure `METGO_VUE_URL` en Secrets de Streamlit Cloud para ver Vue aquí."
    )


def show_vue_fullscreen_on_cloud(
    path: str = "/servicios",
    *,
    height: int = 900,
) -> None:
    """
    Si METGO_VUE_URL apunta a producción (https), muestra Vue a pantalla completa y
    detiene el resto del script (evita el panel legacy con graficas).
    """
    url = get_vue_base_url()
    if not url or "127.0.0.1" in url or "localhost" in url.lower():
        return
    on_cloud = is_streamlit_cloud()
    production_vue = url.startswith("https://")
    if on_cloud or production_vue:
        render_vue_iframe(path, height=height)
        st.stop()
