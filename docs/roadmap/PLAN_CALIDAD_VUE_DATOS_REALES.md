# Plan de trabajo — Calidad Vue en todos los módulos + solo datos reales

> Fecha: 2026-07-21 · Estado: aprobado por el usuario, en ejecución por etapas.
> Complementa `docs/PROMPT_UNIFICACION_FORMATO_UI.md` (tema oscuro) con los
> requisitos nuevos: nivel de calidad de la SPA Vue/Netlify en TODOS los
> módulos, sin emojis/iconos de texto, gráficos interactivos (estilo Ensemble),
> cero datos sintéticos y series históricas oficiales por estación.

---

## Principios (decididos por el usuario, no renegociar)

1. **La referencia visual es la SPA Vue en Netlify** (https://metgo3d.netlify.app):
   tipografía DM Sans, fondo `#0f172a`, superficie `#1e293b`, verde `#059669`/`#34d399`,
   celeste `#38bdf8`, sin emojis en títulos ni métricas.
2. **La referencia de gráficos es el "Motor Predictivo Multi-Modelo (Ensemble)"**
   (ECharts en Vue): barras con degradado azul, líneas suaves con glow,
   tooltip oscuro, leyenda superior, ejes múltiples, slider de zoom.
   - En Vue: ECharts (`vue-echarts`), como ya se hizo en
     `PronosticoPrecipitacionAvanzado.vue`. Nada de SVG dibujado a mano.
   - En Streamlit: Plotly SIEMPRE vía `plotly_layout(...)` de `metgo/streamlit_theme.py`.
3. **Cero datos sintéticos/ilustrativos.** Si un dato no es real se muestra
   el estado vacío ("Sin datos — requiere ETL") con el enlace a la fase que lo
   habilita; nunca `np.random`, listas hardcodeadas ni "datos ilustrativos".
4. **Históricos oficiales por estación** (Quillota, Los Nogales, Hijuelas,
   Limache, Olmué): incorporar fuentes oficiales chilenas además de OpenMeteo.

## Fuentes de datos reales a integrar (Etapa D)

| Fuente | Qué aporta | Acceso |
|--------|-----------|--------|
| **OpenMeteo Archive API** (`archive-api.open-meteo.com`) | Reanálisis ERA5 diario/horario desde 1940 por coordenadas — ya usado para hist. 30 días; extender a 5 años reales | HTTP gratis, sin key |
| **Agromet (INIA/Minagri)** — red agroclimática | Estaciones físicas en Quillota/La Cruz/Hijuelas (T°, HR, precip, viento, radiación) | https://agromet.cl — API/export CSV con registro |
| **DMC (Dirección Meteorológica de Chile)** | Datos oficiales normados (precip/T°) estación Quillota y cercanas | https://climatologia.meteochile.gob.cl — servicios abiertos |
| **DGA (Dirección General de Aguas)** | Precipitación y caudales históricos de largo plazo | https://snia.mop.gob.cl |
| **CR2 (Centro de Ciencia del Clima)** | Series depuradas de precip/T° por estación (CSV descargable) | https://www.cr2.cl/datos-de-precipitacion/ |

Estrategia: OpenMeteo Archive es la fuente programática inmediata (misma API,
datos ERA5 reales); Agromet/DMC se integran después como "fuente oficial de
estación física" con columna `fuente` diferenciada en `meteo_registros`.

## Etapas

### Etapa A — Corrección de errores en producción (HECHA 2026-07-21)

- [x] `plotly_layout()` acepta todos los kwargs dentro y no duplica `title`/`height`/`margin`
  (`metgo/streamlit_theme.py`).
- [x] Corregidos los `update_layout` con kwargs duplicados que rompían Render:
  `dashboard_meteorologico_profesional.py`, `dashboard_agricola_inteligente.py`,
  `dashboard_ia_ml_avanzado.py`, `dashboard_simple_optimizado.py`,
  `dashboard_unificado_metgo.py`, `dashboard_agricola_metgo.py`,
  `dashboard_meteorologico_metgo.py`, `dashboard_principal_integrado_metgo.py`,
  `dashboard_mobile_optimizado.py`, `dashboard_monitoreo_tiempo_real.py`.
- [x] Gráfico precipitación Vue migrado de SVG manual a ECharts estilo Ensemble
  (`frontend/vue/src/components/charts/PronosticoPrecipitacionAvanzado.vue`).

### Etapa B — Vue: migrar los SVG restantes a ECharts (1–2 días)

Auditar `frontend/vue/src/components/**` buscando gráficos SVG hechos a mano y
migrarlos a ECharts con el patrón del Ensemble:

- [ ] `TimeSeriesChart.vue`, `HorizontalBarChart.vue`, `WindRoseChart.vue` y
  cualquier `<svg>` con `viewBox` de datos (buscar `rg -l "viewBox" frontend/vue/src/components`).
- [ ] Extraer un composable `useEchartsTheme.js` con el tooltip/leyenda/ejes/dataZoom
  del Ensemble para no copiar el layout en cada componente.
- [ ] Verificación: `npm run build` + revisión visual de /meteo, /precipitacion,
  /metricas, /comparativo.

### Etapa C — Streamlit: paridad visual con Vue y sin emojis (2–3 días)

Para los 13 módulos del catálogo (8501–8513), en este orden
(8502, 8503, 8505, 8506, 8507 primero, que son los que el usuario revisó):

- [ ] Quitar TODOS los emojis de títulos, métricas, expanders y botones
  (`st.metric("🌡️ T° promedio…")` → `st.metric("Temperatura promedio…")`).
  Buscar: `rg -n "[\x{1F300}-\x{1FAFF}\x{2600}-\x{27BF}]" frontend/dashboards/*.py`.
- [ ] Reemplazar tarjetas/cabeceras ad-hoc por los helpers de
  `metgo/streamlit_theme.py` (`bootstrap_dashboard`, `metric-card`, `section-title`)
  para que la jerarquía visual sea la de Vue (tarjetas con borde `#334155`,
  labels uppercase muted, número grande).
- [ ] Todas las figuras con `fig.update_layout(**plotly_layout("Título", ...))`
  + `config=PLOTLY_CONFIG` (interactividad: zoom, hover unificado, export PNG).
- [ ] Verificación: captura por puerto y `python -m compileall frontend/dashboards`.

### Etapa D — Eliminar datos sintéticos (2–4 días, crítico)

Inventario conocido de sintéticos a erradicar (buscar `np.random`, `random.`,
"ilustrativo", "simulado", "generados"):

- [ ] `dashboard_visualizaciones_avanzadas.py` (8506): "Datos Generados: 63
  registros", precipitación 2000.8 mm imposible, rendimiento 34.8 t/ha inventado
  → reemplazar por API `/api/meteo/*` + estado vacío para lo agrícola.
- [ ] `dashboard_global_metricas.py` (8507): "tendencias multi-año ilustrativas",
  ingresos/eficiencia inventados → conectar al histórico real (ver Etapa E)
  y eliminar los KPI sin fuente.
- [ ] `dashboard_agricola_inteligente.py` (8503): "KPIs operativos ilustrativos
  (no conectados a API)" en estadísticas de alertas → conectar a
  `/api/alertas/historial` o mostrar vacío.
- [ ] Panel de notificaciones demo (emails/teléfonos hardcodeados) → leer de
  `/api/notificaciones/config` (fase 9) o marcar como configuración.
- [ ] Regla de guardarraíl en CI: test que falle si un dashboard activo contiene
  `np.random` o "ilustrativo" (extiende `tests/test_ui_theme.py` de la Fase E
  del prompt de unificación).

### Etapa E — Históricos oficiales por estación (3–5 días)

1. [ ] **ETL OpenMeteo Archive**: nuevo módulo
   `backend/08_Gestion_Datos/scripts/etl_archive_openmeteo.py` que baje 5 años
   diarios (ERA5) por estación y los persista en Supabase `meteo_registros`
   con `fuente="openmeteo_archive"`. Ejecutable on-demand y desde
   `/api/datos/etl/sync` con `incluir_archive=true`.
2. [ ] Endpoint `/api/meteo/{id}/historico` acepta `desde/hasta` de años y lee
   SOLO del store (sin llamadas OpenMeteo en caliente para rangos largos).
3. [ ] `dashboard_global_metricas.py` (8507) y `/metricas` en Vue pasan a leer
   ese histórico real (eliminar series ilustrativas de 5 años).
4. [ ] **Agromet/DMC** (segunda iteración): descarga CSV de estaciones físicas
   de Quillota/La Cruz, normalización a `meteo_registros` con
   `fuente="agromet"` — requiere registro del usuario en agromet.cl para API key.
5. [ ] Documentar en `docs/roadmap/fase-3/` el mapeo estación METGO ↔ estación
   oficial (código DMC/Agromet, distancia, altitud).

### Etapa F — Limpieza y verificación final (1 día)

- [ ] Mover dashboards legacy no catalogados a `backend/12_Respaldos_Archivos/archivos_obsoletos/`
  (Fase C del prompt de unificación).
- [ ] Recorrido completo 8501–8513 + Vue con checklist: sin emojis, sin blancos,
  sin sintéticos, gráficos interactivos, misma paleta.
- [ ] Actualizar `docs/PROMPT_UNIFICACION_FORMATO_UI.md` y roadmap con lo hecho.

## Criterios de éxito global

- `rg "np.random|ilustrativo" frontend/dashboards --glob '!*obsoleto*'` sin resultados en activos.
- Ningún emoji en títulos/métricas de los 13 módulos.
- Todos los gráficos Vue en ECharts y todos los Streamlit con `plotly_layout` + `PLOTLY_CONFIG`.
- `/metricas` y 8507 muestran 5 años de datos reales (ERA5/Agromet) con `fuente` visible.
- CI con guardarraíles de tema y de datos sintéticos en verde.

**Fase del roadmap:** DT-x (deuda UI/datos) + 2.x (producto ampliado) + 3.x (históricos oficiales).
