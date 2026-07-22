# Plan de trabajo — Calidad Vue en todos los módulos + solo datos reales

> Fecha: 2026-07-21 · Actualizado: 2026-07-21 (noche) · En ejecución por etapas.
> Complementa `docs/PROMPT_UNIFICACION_FORMATO_UI.md` (tema oscuro) con los
> requisitos nuevos: nivel de calidad de la SPA Vue/Netlify en TODOS los
> módulos, sin emojis/iconos de texto, gráficos interactivos (estilo Ensemble),
> cero datos sintéticos y series históricas oficiales por estación.

---

## Principios (decididos por el usuario, no renegociar)

1. **La referencia visual es la SPA Vue en Netlify** (https://metgo3d.netlify.app).
2. **La referencia de gráficos es el "Motor Predictivo Multi-Modelo (Ensemble)"**
   (ECharts en Vue / Plotly + `plotly_layout` en Streamlit).
3. **Cero datos sintéticos/ilustrativos.**
4. **Históricos oficiales por estación** vía OpenMeteo Archive (inmediato) y Agromet/DMC (después).

## Etapas

### Etapa A — Corrección de errores en producción (HECHA)

- [x] `plotly_layout()` sin kwargs duplicados
- [x] Dashboards con `update_layout` corregidos
- [x] Precipitación Vue (Pronóstico / Histórico / Heladas) en ECharts estilo Ensemble

### Etapa B — Vue: migrar SVG a ECharts (AVANZADA)

- [x] `TimeSeriesChart.vue`, `HorizontalBarChart.vue`, `WindRoseChart.vue` → ECharts
- [x] Composable `frontend/vue/src/composables/useEchartsTheme.js` + `utils/echartsTheme.js`
- [x] `npm run build` OK (2026-07-21)
- [ ] Pendiente: migrar SVG restantes en meteo avanzada
  (`ComboMeteoChart`, `AnalizadorNubosidad`, `PredictorNiebla`, `ComparacionModelosChart`,
  `PronosticoHeladaAvanzado`, `SparklineGrid`, `MlProjectionChart`)

### Etapa C — Streamlit sin emojis (PARCIAL)

- [ ] Strip masivo de emojis **aplazado**: un script agresivo corrompió sintaxis Python
  (docstrings pegados a `def`). Se revirtió; hay que hacer strip **manual archivo a archivo**.
- [x] `dashboard_ia_ml_avanzado.py` reescrito sin emojis en modo producción
- [ ] Resto 8501–8513: quitar emojis de `st.metric` / headers de forma segura

### Etapa D — Eliminar datos sintéticos (HECHA en puertos prioritarios)

- [x] `dashboard_visualizaciones_avanzadas.py` — sin `generar_datos_simulados`
- [x] `dashboard_global_metricas.py` — histórico real vía `historico_meteo` (máx. 92 d hasta Archive)
- [x] `dashboard_agricola_inteligente.py` — sin KPIs/historial ilustrativos
- [x] `dashboard_ia_ml_avanzado.py` — solo registry (sin demo np.random)
- [x] `dashboard_monitoreo_tiempo_real.py` — solo API estaciones (sin simulación IoT)
- [x] `dashboard_analisis_comparativo.py` — solo API valle (sin series 5 años simuladas)
- [x] Guardarraíl CI: `tests/test_ui_theme.py` (2 tests verdes)
- [ ] Pendiente: `dashboard_agricultura_precision.py`, `dashboard_alertas_automaticas.py`,
  `dashboard_unificado_diferenciado.py`, `dashboard_simple_optimizado.py`,
  `dashboard_mobile_optimizado.py` (aún tienen `np.random` / ilustrativo)

### Etapa E — Históricos OpenMeteo Archive (HECHA en código)

- [x] `OpenMeteoData.obtener_datos_archive` + helper módulo
- [x] CLI `backend/08_Gestion_Datos/scripts/etl_archive_openmeteo.py`
- [x] `sincronizar_estaciones(..., incluir_archive=True, anios_archive=5)`
- [x] `POST /api/datos/etl/sync` acepta `incluir_archive` / `anios_archive` (+ OpenAPI)
- [x] Doc `docs/roadmap/fase-3/estaciones_oficiales_mapeo.md`
- [ ] Operativo: ejecutar SQL Supabase + un sync con `incluir_archive: true` en Render
- [ ] Ampliar `/api/meteo/{id}/historico` para rangos multi-año solo-store
- [ ] Agromet/DMC (segunda iteración, requiere registro usuario)

### Etapa F — Limpieza (PARCIAL)

- [ ] Mover dashboards legacy no catalogados a `archivos_obsoletos/`
- [x] Actualizar este plan con el estado real
- [ ] Commit + push cuando el usuario lo pida

## Criterios de éxito (estado)

| Criterio | Estado |
|----------|--------|
| Sin `np.random`/`ilustrativo` en 8502–8507 + 8509 | OK (test CI) |
| Sin emoji en todos los módulos | Pendiente (C) |
| Gráficos Vue ECharts (charts base) | OK TimeSeries/HBar/WindRose + precip |
| `/metricas` y 8507 con 5 años reales | Código Archive listo; falta poblar Supabase |
| CI guardarraíl | OK `tests/test_ui_theme.py` |

**Fase del roadmap:** DT-x + 2.x + 3.x
