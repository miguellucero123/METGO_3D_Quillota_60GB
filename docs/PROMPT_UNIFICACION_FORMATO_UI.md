# PROMPT — Unificación de formato visual METGO 3D (Vue + Streamlit)

> Copiar y pegar en Cursor (modo Agente) para ejecutar la unificación por fases.
> Objetivo: que TODO el sistema (SPA Vue, portal 8501 y módulos 8502–8513) se vea
> con el mismo formato oscuro METGO, como el gráfico del "Motor Predictivo
> Multi-Modelo (Ensemble)": fondo `#0f172a`, superficie `#1e293b`, verde `#059669`/`#34d399`,
> celeste `#38bdf8`, texto `#f8fafc`. Ningún gráfico ni módulo con fondo blanco.

---

## CONTEXTO — dónde está cada cosa

### Fuente única del tema (NO duplicar estilos)

| Recurso | Ruta | Qué define |
|---------|------|------------|
| Tema Streamlit global | `.streamlit/config.toml` | base dark, colores base |
| **Tema compartido** | `metgo/streamlit_theme.py` | paleta, CSS global (`METGO_THEME_CSS`), **`plotly_layout()`** (fondos/fuente/colorway Plotly), `PLOTLY_CONFIG`, `bootstrap_dashboard()`, `inject_theme()` |
| Wrapper dashboards | `frontend/dashboards/metgo_dashboard_init.py` | `page_config_and_theme()` → devuelve `(st, PLOTLY_CONFIG, plotly_layout)` |
| Tema Vue | `frontend/vue/src/` (estilos globales) | mismo esquema de colores |

### Mapeo puerto → script (definido en `backend/05_APIs_Externas/api_rest/catalog.py`, `MODULOS_SISTEMA`)

| Puerto | Script (`frontend/dashboards/`) | Módulo |
|--------|--------------------------------|--------|
| 8501 | `streamlit_app.py` (raíz del repo) | Portal ejecutivo |
| 8502 | `dashboard_meteorologico_profesional.py` | Análisis meteorológico (legado → Vue `/meteo/historico`) |
| 8503 | `dashboard_agricola_inteligente.py` | Gestión agrícola |
| 8504 | `dashboard_monitoreo_tiempo_real.py` | Monitoreo tiempo real |
| 8505 | `dashboard_ia_ml_avanzado.py` | IA / ML |
| 8506 | `dashboard_visualizaciones_avanzadas.py` | Visualizaciones |
| 8507 | `dashboard_global_metricas.py` | Métricas globales |
| 8508 | `dashboard_agricultura_precision.py` | Agricultura de precisión |
| 8509 | `dashboard_analisis_comparativo.py` | Análisis comparativo |
| 8510 | `dashboard_alertas_automaticas.py` | Alertas automáticas |
| 8511 | `dashboard_simple_optimizado.py` | Simple optimizado |
| 8512 | `dashboard_unificado_diferenciado.py` | Unificado |
| 8513 | `dashboard_mobile_optimizado.py` | Móvil |

El launcher (`backend/05_APIs_Externas/api_rest/streamlit_launcher.py`) lee ese catálogo y ejecuta `streamlit run <script> --server.port <puerto>`.

## REGLAS DE ORO (aplicar siempre)

1. **Todo dashboard Streamlit** arranca con:

```python
from metgo_dashboard_init import page_config_and_theme
st, PLOTLY_CONFIG, plotly_layout = page_config_and_theme("Título", "Subtítulo", module="...")
```

2. **Toda figura Plotly** aplica el layout del tema y el config compartido:

```python
fig.update_layout(**plotly_layout(height=400), title="...", ...)
st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)
```

3. **Prohibido**: `template="plotly_white"`, `paper_bgcolor="white"/"#ffffff"`, colores de texto oscuros sobre fondo oscuro, CSS ad-hoc que cambie el fondo. Los `px.line/px.bar/px.pie/px.histogram` también llevan `fig.update_layout(**plotly_layout(...))` después de crearse.
4. **Colores**: usar la paleta de `metgo/streamlit_theme.py` (no inventar hex nuevos). Acentos: verde `#34d399`, celeste `#38bdf8`, ámbar `#fbbf24`, rojo `#ef4444`.
5. **Nunca argumentos duplicados** en `update_layout` (p. ej. `height` dentro de `plotly_layout(...)` y también fuera, o `showlegend` dos veces): produce `TypeError`/`SyntaxError`.
6. **Vue primero**: pantallas nuevas van en Vue con el mismo esquema; Streamlit queda para análisis Python pesado (regla del proyecto).

## ESTADO ACTUAL (tras la corrección del 2026-07-21)

Ya corregidos (tema aplicado a figuras que estaban en blanco o con strings corruptos):
`dashboard_meteorologico_profesional.py` (8502), `dashboard_principal_integrado_metgo.py`,
`dashboard_unificado_metgo.py`, `dashboard_agricola_metgo.py`, `main_dashboard.py`,
`dashboard_integrado_recomendaciones_metgo.py`, `visualizacion_3d_metgo.py`,
`ejecutar_visualizaciones.py`, `dashboard_ia_ml_avanzado.py` (8505),
`dashboard_mobile_optimizado.py` (8513), `dashboard_metgo_3d.py`,
`dashboard_global_html.py`, `dashboard_meteorologico_metgo.py`.

## FASES DEL PLAN

### Fase A — Auditoría de lo restante (30 min)

1. Buscar restos de formato claro en dashboards activos (ignorar `*.backup`, `corregir_plotly_*.py`, notebooks):

```
rg -n "plotly_white|paper_bgcolor='white'|paper_bgcolor=\"#fff" frontend/dashboards pages metgo --glob '!*.backup'
rg -n "update_layout\(" frontend/dashboards --glob '!*.backup' | rg -v "plotly_layout"
```

2. Verificar que `pages/1_Resumen_publico.py` y `pages/2_Panel_operadores.py` llamen `inject_theme()` (hoy no lo hacen).
3. Compilar todo: `python -m py_compile <cada .py editado>`.

### Fase B — Módulos sin tema (1-2 h)

Aplicar regla 1 y 2 a los que no importan el tema: `chatbot_metgo.py`, `app_movil_metgo.py`, `sistema_unificado_metgo.py` (evaluar si están vivos; si son obsoletos, moverlos a `backend/12_Respaldos_Archivos/archivos_obsoletos/`).

### Fase C — Limpieza de legacy duplicado (2 h, reduce el desorden)

- `frontend/dashboards/` tiene ~2 generaciones de dashboards (p. ej. `dashboard_meteorologico_metgo.py` vs `dashboard_meteorologico_profesional.py`, `dashboard_unificado_metgo.py` vs `dashboard_unificado_diferenciado.py`, `*.backup`, `corregir_plotly_*.py`).
- Mantener SOLO los 13 del catálogo + helpers (`metgo_dashboard_init.py`); mover el resto a `archivos_obsoletos/`. Actualizar referencias en `dashboard_metgo_3d.py` (lista de módulos) y docs.
- Eliminar los scripts `corregir_plotly_*.py` (fueron los que inyectaron los strings corruptos `showlegend=False, showlegend=False`).

### Fase D — Verificación visual (1 h)

1. Levantar portal: `python -m streamlit run streamlit_app.py` (8501).
2. Desde Vue `/puertos` o el launcher, abrir cada módulo 8502–8513 y verificar: fondo oscuro uniforme, gráficos estilo Ensemble (colorway verde/celeste/ámbar), sin bloques blancos, textos legibles.
3. Captura por módulo y checklist en `docs/roadmap/deuda-tecnica/`.

### Fase E — Guardarraíl permanente (30 min)

Agregar test que impida regresiones (`tests/test_ui_theme.py`): escanear `frontend/dashboards/*.py` activos y fallar si aparece `plotly_white` o `paper_bgcolor='white'` o `update_layout(` sin `plotly_layout` en el mismo archivo. Integrarlo al CI existente (`.github/workflows/ci.yml`).

## CRITERIOS DE ÉXITO

- 13/13 módulos de puertos con `page_config_and_theme` + todas sus figuras con `plotly_layout`.
- `rg "plotly_white" frontend/dashboards --glob '!*.backup'` sin resultados en archivos activos.
- Ningún fondo blanco en portal, módulos ni Vue.
- Test de guardarraíl en CI verde.

**Fase del roadmap:** DT-x (deuda técnica UI) + 1.x (consolidar MVP).
