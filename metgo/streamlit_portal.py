# -*- coding: utf-8 -*-
"""Portal ejecutivo METGO en Streamlit.

Capa operativa de entrada:
- Netlify/Vue como frontend principal
- API REST como fuente de verdad técnica
- Streamlit como consola ejecutiva y soporte legacy controlado
"""

from __future__ import annotations

import json
from typing import Any
from urllib.error import URLError
from urllib.request import urlopen

import streamlit as st

from metgo.streamlit_theme import (
    ACCENT,
    DANGER,
    PRIMARY,
    SUCCESS,
    TEXT_SECONDARY,
    WARNING,
    inject_theme,
    is_streamlit_cloud,
    module_card_html,
)
from metgo.vue_embed import get_vue_base_url

DEFAULT_VUE_PROD = "https://metgo3d.netlify.app"
DEFAULT_API_PROD = "https://metgo-api.onrender.com"
DEFAULT_API_DOCS = "https://metgo-api.onrender.com/api/docs"


def _vue_url() -> str:
    return get_vue_base_url() or DEFAULT_VUE_PROD


def _api_base() -> str:
    return DEFAULT_API_PROD.rstrip("/")


def _api_health_url() -> str:
    return f"{_api_base()}/api/health"


def _api_docs_url() -> str:
    return DEFAULT_API_DOCS


def _read_json(url: str, timeout: float = 3.0) -> dict[str, Any] | None:
    try:
        with urlopen(url, timeout=timeout) as resp:
            payload = resp.read().decode("utf-8", errors="replace")
        return json.loads(payload)
    except Exception:
        return None


def _status_badge(status: str) -> str:
    color = {
        "healthy": SUCCESS,
        "degraded": WARNING,
        "failed": DANGER,
        "unknown": TEXT_SECONDARY,
    }.get(status, TEXT_SECONDARY)
    label = {
        "healthy": "Operativo",
        "degraded": "Degradado",
        "failed": "Fallo",
        "unknown": "Desconocido",
    }.get(status, "Desconocido")
    return f'<span style="background:{color};color:white;padding:0.25rem 0.65rem;border-radius:999px;font-size:0.8rem;font-weight:700;">{label}</span>'


def _health_summary() -> dict[str, Any]:
    health = _read_json(_api_health_url()) or {}
    integ = health.get("integracion") or {}
    observ = health.get("observabilidad") or {}
    ml = integ.get("ml") or health.get("ml") or {}
    datos = integ.get("datos") or {}
    return {
        "api_status": health.get("status") or health.get("estado") or "unknown",
        "api_version": health.get("version") or "dev",
        "uptime_s": health.get("uptime_s") or 0,
        "models_total": ml.get("total") or ml.get("modelos_total") or 0,
        "models_ok": ml.get("servibles") or ml.get("ok") or 0,
        "data_freshness": datos.get("freshness") or datos.get("actualizacion") or health.get("updated_at") or "n/a",
        "observability": bool(observ),
        "health_raw": health,
    }


def _mostrar_modulo_activado() -> None:
    """Si la URL trae ?activar=id (desde Vue/API), muestra el módulo seleccionado."""
    try:
        from api_rest import catalog
    except ImportError:
        return
    activar = st.query_params.get("activar")
    if not activar:
        return
    m = catalog.obtener_modulo(str(activar))
    if not m:
        st.warning(f"Módulo «{activar}» no encontrado en el catálogo.")
        return
    puerto = m.get("puerto", "—")
    util = m.get("utilidad") or m.get("descripcion", "")
    st.info(
        f"**{m.get('nombre')}** · puerto local **:{puerto}** · {util}\n\n"
        "En la nube este portal no levanta ese puerto; use la app Vue o la API pública."
    )

    if m.get("ruta_vue_alternativa"):
        vue = _vue_url().rstrip("/") + m["ruta_vue_alternativa"]
        st.link_button("Abrir equivalente en Vue", vue, use_container_width=False)
    if st.button("Ir a catálogo y servicios", type="secondary"):
        st.switch_page("pages/0_Catalogo_y_servicios.py")


def _render_kpi_cards(summary: dict[str, Any]) -> None:
    status = str(summary["api_status"]).lower()
    if status not in {"healthy", "degraded", "failed"}:
        status = "unknown"
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">API / Salud</div>
                <div class="metric-number">{_status_badge(status)}</div>
                <div style="margin-top:0.35rem;color:{TEXT_SECONDARY};font-size:0.9rem;">v{summary['api_version']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Modelos activos</div>
                <div class="metric-number">{summary['models_ok']}/{summary['models_total']}</div>
                <div style="margin-top:0.35rem;color:{TEXT_SECONDARY};font-size:0.9rem;">registry + manifest</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Frescura de datos</div>
                <div class="metric-number" style="font-size:1.2rem;">{summary['data_freshness']}</div>
                <div style="margin-top:0.35rem;color:{TEXT_SECONDARY};font-size:0.9rem;">fuente real prioritaria</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c4:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Observabilidad</div>
                <div class="metric-number">{"Activa" if summary['observability'] else "Básica"}</div>
                <div style="margin-top:0.35rem;color:{TEXT_SECONDARY};font-size:0.9rem;">health + logs</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_inicio_page() -> None:
    """Portal ejecutivo: acceso a Vue, API, Streamlit y legacy controlado."""
    inject_theme()
    _mostrar_modulo_activado()
    vue = _vue_url()
    summary = _health_summary()

    st.markdown(
        """
<div class="main-header">
  <h1 style="margin:0;color:white;">METGO 3D — Portal Ejecutivo</h1>
  <p style="margin:0.5rem 0 0 0;opacity:0.9;">Quillota · Vue/Netlify + API/Render + Streamlit operativo</p>
</div>
        """,
        unsafe_allow_html=True,
    )

    _render_kpi_cards(summary)

    st.markdown("### Acceso oficial")
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown(
            module_card_html(
                "Frontend oficial Vue / Netlify",
                PRIMARY,
                "Interfaz principal del proyecto: módulos, navegación y experiencia empresarial.",
                url=vue.rstrip("/") + "/",
            ),
            unsafe_allow_html=True,
        )
        st.link_button("Abrir SPA principal", vue.rstrip("/") + "/", use_container_width=True)
        st.link_button("Ingresar al login", vue.rstrip("/") + "/login", use_container_width=True)
    with col_b:
        st.markdown(
            module_card_html(
                "API REST / Render",
                ACCENT,
                "Fuente de verdad técnica: datos, modelos, salud, integración y auth.",
                url=_api_health_url(),
            ),
            unsafe_allow_html=True,
        )
        st.link_button("Probar /api/health", _api_health_url(), use_container_width=True)
        st.link_button("Documentación API", _api_docs_url(), use_container_width=True)

    st.divider()
    st.markdown("### Atajos operativos")
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("Vue embebido (iframe)", use_container_width=True, type="secondary"):
            st.switch_page("pages/3_Panel_Vue_embebido.py")
    with c2:
        if st.button("Catálogo y servicios", use_container_width=True):
            st.switch_page("pages/0_Catalogo_y_servicios.py")
    with c3:
        if st.button("Resumen público", use_container_width=True):
            st.switch_page("pages/1_Resumen_publico.py")

    st.divider()
    st.markdown("### Estado operacional")
    left, right = st.columns([1.2, 0.8])
    with left:
        st.markdown(
            f"""
            <div class="dashboard-card">
              <h4 style="margin-top:0;">Lectura ejecutiva</h4>
              <ul>
                <li><strong>Frontend principal:</strong> Netlify / Vue</li>
                <li><strong>Consola operativa:</strong> Streamlit</li>
                <li><strong>Backend técnico:</strong> API REST</li>
                <li><strong>Modelos activos:</strong> {summary['models_ok']}/{summary['models_total']}</li>
                <li><strong>Datos:</strong> {summary['data_freshness']}</li>
              </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with right:
        st.markdown(
            f"""
            <div class="dashboard-card">
              <h4 style="margin-top:0;">Sesión / despliegue</h4>
              <p><strong>Modo:</strong> {"Streamlit Cloud" if is_streamlit_cloud() else "Local / servidor"}</p>
              <p><strong>Uptime API:</strong> {int(summary['uptime_s'])} s</p>
              <p><strong>Estado:</strong> {_status_badge(status)}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with st.expander("Credenciales de demostración"):
        st.markdown(
            """
| Usuario | Contraseña |
|---------|------------|
| `admin` | `admin123` |
| `user` | `user123` |
| `metgo` | `metgo2025` |
            """
        )

    st.divider()
    st.markdown("### Legacy / soporte")
    st.warning("Estos accesos se mantienen por compatibilidad, pero ya no son la experiencia principal.")
    col_l1, col_l2 = st.columns(2)
    with col_l1:
        st.markdown(
            module_card_html(
                "Panel Streamlit legacy",
                WARNING,
                "Dashboards antiguos, útiles para soporte o revisión histórica.",
                cloud=is_streamlit_cloud(),
            ),
            unsafe_allow_html=True,
        )
        if st.button("Abrir panel operadores (legacy)", use_container_width=True):
            st.switch_page("pages/2_Panel_operadores.py")
    with col_l2:
        st.markdown(
            module_card_html(
                "Soporte técnico",
                TEXT_SECONDARY,
                "Usar solo para diagnóstico, migración o revisión de módulos antiguos.",
                cloud=True,
            ),
            unsafe_allow_html=True,
        )

    st.caption(
        f"Cloud · Vue: `{vue}` · API: `{_api_base()}` · Secret opcional: `METGO_VUE_URL`"
        if is_streamlit_cloud()
        else "Local · Vue en frontend/vue y API en Render o entorno local según configuración."
    )
