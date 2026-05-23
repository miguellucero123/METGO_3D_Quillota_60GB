# Propuesta: raíz en tres capas (backend · frontend · site-web)

**Versión:** 1.0 · **Fecha:** 2026-05-23  
**Estado:** Aplicada con script `reorganizar_layout_capas_v4.py` y `metgo_paths.py` con detección dual.

---

## 1. Objetivo

Que la carpeta raíz se vea **ordenada y profesional**, agrupando el proyecto en tres pilares claros, **sin romper**:

- Streamlit Cloud (`streamlit_app.py` en raíz)
- API REST Flask + Vue
- Scripts `.bat` y wrappers legacy
- Módulos numerados `01`–`12` (siguen existiendo **dentro** de `backend/`)

---

## 2. Vista de la raíz (después)

```text
METGO_3D_Quillota_60GB/
├── backend/              # Lógica, datos, API, ML, deploy, respaldos
├── frontend/             # Vue 3 + dashboards Streamlit operativos
├── site-web/             # Capa pública / exposición web
├── docs/                 # Documentación (antes 11_Documentacion)
├── README.md
├── streamlit_app.py      # Entrypoint Streamlit Cloud (no mover)
├── metgo_paths.py        # Resuelve rutas nueva + legacy
├── requirements.txt
├── .streamlit/
└── wrappers *.py         # Compatibilidad
```

---

## 3. Mapeo de carpetas actuales → nuevas

### backend/

| Origen (raíz) | Destino |
|---------------|---------|
| `01_Sistema_Meteorologico/` | `backend/01_Sistema_Meteorologico/` |
| `02_Sistema_Agricola/` | `backend/02_Sistema_Agricola/` |
| `03_Sistema_IoT_Drones/` | `backend/03_Sistema_IoT_Drones/` |
| `05_APIs_Externas/` | `backend/05_APIs_Externas/` |
| `06_Modelos_ML_IA/` | `backend/06_Modelos_ML_IA/` |
| `07_Sistema_Monitoreo/` | `backend/07_Sistema_Monitoreo/` |
| `08_Gestion_Datos/` | `backend/08_Gestion_Datos/` |
| `09_Testing_Validacion/` | `backend/09_Testing_Validacion/` |
| `10_Deployment_Produccion/` | `backend/10_Deployment_Produccion/` |
| `12_Respaldos_Archivos/` | `backend/12_Respaldos_Archivos/` |

### frontend/ (contenido de `04_Dashboards_Unificados/`)

| Origen | Destino |
|--------|---------|
| `04_.../frontend_vue/` | `frontend/vue/` |
| `04_.../dashboards/` | `frontend/dashboards/` |
| `04_.../config/` | `frontend/config/` |
| `04_.../static/` | `frontend/static/` |
| `04_.../templates/` | `frontend/templates/` |
| `04_.../app_movil_metgo/` | `frontend/app_movil/` |

### site-web/

| Contenido | Uso |
|-----------|-----|
| `site-web/streamlit/` | Dashboard web público (`dashboard_web_publico.py`) |
| `site-web/static/` | Assets públicos (futuro landing / marketing) |

El dashboard principal con login sigue en `frontend/dashboards/` (operadores).

### docs/

| Origen | Destino |
|--------|---------|
| `11_Documentacion/` | `docs/` |

---

## 4. Qué NO se mueve (y por qué)

| Elemento | Motivo |
|----------|--------|
| `streamlit_app.py` | Streamlit Cloud exige main file en raíz del repo |
| `metgo_paths.py` | Punto único de resolución de rutas |
| `requirements.txt` | Convención `pip install -r` |
| Wrappers en raíz | Compatibilidad con tutoriales y atajos |
| `.streamlit/` | Configuración Streamlit Cloud |

---

## 5. Compatibilidad técnica

1. **`metgo_paths.py`** — Detecta layout por capas (`backend/`, `frontend/`) o layout legacy (`01_`… en raíz).
2. **Wrappers** — Siguen en raíz; apuntan a rutas bajo `backend/` o `frontend/`.
3. **Junctions `data/` y `logs/`** — Redirigen a `backend/08_Gestion_Datos/*_runtime`.
4. **Catálogo API** — Rutas de scripts Streamlit actualizadas a `frontend/dashboards/...`.

---

## 6. Flujo de ejecución (sin cambios para el usuario)

```bat
backend\10_Deployment_Produccion\scripts\iniciar_metgo_desarrollo.bat
```

O desde raíz (wrapper / rutas antiguas en documentación redirigen vía `metgo_paths`):

```bash
python backend/10_Deployment_Produccion/scripts/iniciar_api_rest.py
cd frontend/vue && npm run dev
```

---

## 7. Fases de migración

| Fase | Acción |
|------|--------|
| **v4** | Mover carpetas + actualizar `metgo_paths`, API, Streamlit, `.bat` principales |
| **v5** (opcional) | Agrupar scripts deploy en `backend/10_.../scripts/arranque/` y `legacy/` |
| **v6** (opcional) | Unificar módulos `01`–`03` en `backend/sistemas/` (solo si se desea menos carpetas) |

---

## 8. Riesgos y mitigación

| Riesgo | Mitigación |
|--------|------------|
| Rutas hardcodeadas `04_Dashboards_...` | `metgo_paths` + actualización `catalog.py` |
| Streamlit Cloud | `streamlit_app.py` en raíz sin cambios de nombre |
| Enlaces en notebooks | Usar `import metgo_paths` o rutas relativas al repo |
| Git history | Movimientos con `git mv` recomendado en commit dedicado |

---

## 9. Criterio de éxito

- [ ] Raíz muestra solo `backend/`, `frontend/`, `site-web/`, `docs/` + entrypoints
- [ ] `python iniciar_api_rest.py` y Vue arrancan
- [ ] Login Vue + JWT operativos
- [ ] `streamlit run streamlit_app.py` funciona
- [ ] Centro de servicios inicia Streamlit bajo demanda
