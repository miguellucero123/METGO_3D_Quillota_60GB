# Mejora integral METGO 3D: datos reales, modelos activos y dashboards empresariales

> **For Hermes:** Use subagent-driven-development skill to implement this plan task-by-task.

**Goal:** Migrar el ecosistema de modelos para trabajar con datos reales de forma controlada, mantener activos los modelos útiles, modernizar la capa de dashboards con estándar profesional/empresarial y ordenar el proyecto para operación óptima.

**Architecture:**
- La fuente de verdad para inferencia y entrenamiento será el pipeline real ya existente en `backend/05_APIs_Externas/api_rest/integracion/ml_train_runner.py` y el manifest de `backend/06_Modelos_ML_IA/modelos/model_manifest.json`.
- Los dashboards profesionales consumirán APIs y datos normalizados, no datos sintéticos embebidos en los paneles.
- El código legacy se aislará como compatibilidad o archivo, dejando un camino claro para operación, mantenimiento y despliegue.

**Tech Stack:**
- Python 3.11
- Streamlit
- Flask API REST
- pandas / numpy / scikit-learn / joblib
- Plotly
- SQLite
- Vue 3 + Vite

---

### Task 1: Auditar y clasificar modelos activos vs legacy

**Objective:** Identificar qué artefactos de `backend/06_Modelos_ML_IA/modelos/` deben seguir activos y cuáles deben pasar a legacy/archivo.

**Files:**
- Modify: `backend/06_Modelos_ML_IA/README.md`
- Modify: `backend/06_Modelos_ML_IA/modelos/model_manifest.json`
- Modify: `backend/06_Modelos_ML_IA/scripts/auditar_carpeta_modelos.py`
- Test: `backend/06_Modelos_ML_IA/scripts/auditar_carpeta_modelos.py`

**Step 1: Write failing test / assertion**
- Add manifest-level checks in the auditor so it fails when a model is referenced but missing, or when a model is present but not declared servible.

**Step 2: Run audit to verify baseline**
- Run: `python backend/06_Modelos_ML_IA/scripts/auditar_carpeta_modelos.py`
- Expected: report of active, orphaned and legacy artifacts.

**Step 3: Minimal implementation**
- Make the auditor emit a clear classification:
  - `activo`
  - `legacy`
  - `archivo`
- Ensure the README documents the rule: active models live under `modelos/` and are described in the manifest.

**Step 4: Verify**
- Run: `python backend/06_Modelos_ML_IA/scripts/auditar_carpeta_modelos.py`
- Expected: all servible models pass, legacy items are explicitly flagged.

---

### Task 2: Consolidar datos reales para entrenamiento e inferencia

**Objective:** Ensure the ML stack uses real historical data by default and synthetic data only for tests/CI.

**Files:**
- Modify: `backend/05_APIs_Externas/api_rest/integracion/ml_train_runner.py`
- Modify: `backend/05_APIs_Externas/api_rest/ml_registry_core.py`
- Modify: `backend/05_APIs_Externas/api_rest/integracion/ml_registry.py`
- Modify: `backend/08_Gestion_Datos/scripts/gestion_datos.py`
- Modify: `backend/06_Modelos_ML_IA/README.md`
- Test: `tests/` (new or existing integration tests)

**Step 1: Write failing test**
- Add a test that verifies training refuses synthetic input unless `METGO_ML_ALLOW_SYNTHETIC=1`.
- Add a test that verifies registry payload exposes real-data provenance.

**Step 2: Run test to verify failure**
- Run: `python -m pytest tests -q`
- Expected: failures until real-data flag handling is implemented.

**Step 3: Minimal implementation**
- Make the training runner default to real sources:
  - SQLite / CSV histórico / OpenMeteo cache
- Keep synthetic generation only as an opt-in fallback for CI.
- Persist provenance into the registry: source, date range, rows, model version, training timestamp.

**Step 4: Verify**
- Run the training runner and registry inspection.
- Expected: manifest stays populated, provenance is explicit, and no model is demoted accidentally.

---

### Task 3: Diseñar una capa de dashboards empresarial

**Objective:** Replace demo-style dashboards with a professional hub that separates executive view, operational view, and detailed analytics.

**Files:**
- Modify: `metgo/streamlit_portal.py`
- Modify: `metgo/dashboard_loader.py`
- Modify: `metgo/streamlit_theme.py`
- Modify: `frontend/dashboards/dashboard_unificado_metgo_integrado.py`
- Modify: `frontend/dashboards/dashboard_principal_integrado_metgo.py`
- Modify: `frontend/dashboards/dashboard_unificado_metgo.py`
- Modify: `frontend/dashboards/dashboard_simple_metgo.py`
- Modify: `streamlit_app.py`
- Modify: `sistema_auth_dashboard_principal_metgo.py`

**Step 1: Write failing visual/structure expectation**
- Define a target layout:
  - executive KPIs
  - status cards
  - module navigation
  - alerts area
  - data source health
  - model health
- Add a smoke test or launch check that the main portal renders without exceptions.

**Step 2: Run current portal**
- Run the Streamlit entrypoint and identify the current UX gaps.

**Step 3: Minimal implementation**
- Centralize style tokens in `metgo/streamlit_theme.py`.
- Standardize cards, spacing, typography, and status badges.
- Replace synthetic demo charts with API-backed metrics where possible.
- Keep legacy dashboards behind a clear “legacy” section.

**Step 4: Verify**
- Main portal loads and clearly separates:
  - empresarial
  - operativo
  - analítico
  - legacy

---

### Task 4: Eliminar contaminación de scripts obsoletos y backups

**Objective:** Stop treating backups and obsolete code as active runtime content.

**Files:**
- Modify: `.gitignore`
- Modify: `docs/RAIZ_REPOSITORIO.md`
- Modify: `backend/06_Modelos_ML_IA/README.md`
- Modify: `frontend/dashboards/DISENO_UNIFICADO.md`
- Potentially move/remove: `backend/12_Respaldos_Archivos/`

**Step 1: Write failing policy check**
- Add a repo hygiene check that warns if runtime imports resolve into backup folders.

**Step 2: Run scan**
- Identify runtime imports or references into `12_Respaldos_Archivos`.

**Step 3: Minimal implementation**
- Mark backup folders as archive-only.
- Add explicit documentation for active vs archive paths.
- Prevent new runtime imports from backup locations.

**Step 4: Verify**
- Core app paths resolve only from active source folders.

---

### Task 5: Agregar health, observabilidad y verificación operativa

**Objective:** Make it easy to know if the project is actually healthy.

**Files:**
- Modify: `backend/05_APIs_Externas/api_rest/health.py`
- Modify: `backend/05_APIs_Externas/api_rest/app.py`
- Modify: `backend/05_APIs_Externas/api_rest/observability.py`
- Modify: `frontend/dashboards/dashboard_global_metgo.py`
- Modify: `tests/`

**Step 1: Write failing test**
- Add tests for health payload fields:
  - uptime
  - version
  - model registry status
  - data source status
  - dashboard status

**Step 2: Implement minimal health enrichment**
- Include counts for active models, deprecated models, and last training date.
- Add data-source freshness and API reachability.

**Step 3: Verify**
- `/api/health` returns useful operational metadata.

---

### Task 6: Final integration and regression pass

**Objective:** Confirm that the improved stack still boots and that the key paths are intact.

**Files:**
- `streamlit_app.py`
- `backend/05_APIs_Externas/api_rest/app.py`
- `frontend/vue/package.json`
- `backend/06_Modelos_ML_IA/modelos/model_manifest.json`

**Step 1: Run core checks**
- API health
- Streamlit main entrypoint
- model audit
- minimal tests

**Step 2: Verify no regressions**
- Ensure the main entrypoints still work.

**Step 3: Document the result**
- Update README or docs with the new operating model.

---

## Acceptance criteria

- Los modelos útiles quedan declarados, auditados y operativos con datos reales por defecto.
- Los datos sintéticos quedan limitados a tests/CI o entornos controlados.
- El portal y dashboards muestran una estética profesional, con navegación clara y métricas de negocio.
- Los backups y legacy quedan aislados del runtime activo.
- Hay una forma simple de verificar salud, entrenamiento y estado del sistema.
- El proyecto queda más fácil de operar, mantener y escalar.
