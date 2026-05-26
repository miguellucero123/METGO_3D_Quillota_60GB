# Prompt MVP — METGO 3D Quillota

Documento maestro para alinear **desarrollo**, **agentes de IA (Cursor)** y **presentación del producto** como **MVP profesional** con propuestas de evolución.

---

## 1. Cómo usar este documento

| Uso | Acción |
|-----|--------|
| **agentes** | Leer **`AGENTS.md`** (raíz) y tareas en **`docs/roadmap/`**. |
| **agentes** | Copie la sección [Prompt listo para pegar](#prompt-listo-para-pegar) en reglas o chat. |
| **Equipo dev** | [Estado MVP actual](#estado-mvp-actual) + [roadmap por carpetas](roadmap/README.md). |
| **Demo / pitch** | [Narrativa del producto](#narrativa-del-producto-mvp) + URLs desplegadas. |
| **Nuevo contribuidor** | `README.md` → `docs/RAIZ_REPOSITORIO.md` → `docs/roadmap/fase-1/`. |
| **Escalar post-MVP (fases 1–10)** | **[`docs/PROMPT_ESCALAMIENTO_MVP.md`](PROMPT_ESCALAMIENTO_MVP.md)** — inventario completo + prompt para agentes. |

---

## 2. Narrativa del producto (MVP)

**METGO 3D** es un **MVP operativo** de plataforma agrometeorológica para el **Valle de Aconcagua (Chile)**, centrado en **Quillota** y estaciones vecinas. No es un prototipo visual: tiene **API REST con JWT**, **SPA Vue en producción (Netlify)**, **backend en Render**, **portal Streamlit** y un **Visor de Puertos** que unifica el acceso a dashboards analíticos legacy.

**Propuesta de valor del MVP**

- Un solo login y catálogo de módulos para operadores y agrónomos.
- Datos meteorológicos y recomendaciones agrícolas vía **OpenMeteo** y lógica de negocio en `backend/`.
- Despliegue real en la nube (no solo local) con documentación de límites (`docs/manuales/QUE_VER_EN_NUBE.md`).
- Base de código **por capas** (`backend` / `frontend` / `site-web` / `metgo/`) lista para escalar sin reescribir desde cero.

**Qué NO promete el MVP (honestidad técnica)**

- No hay 13 microservicios Streamlit en la nube (puertos 8501–8513 son **locales**; en nube hay **visor + Vue + portal**).
- No hay app móvil nativa en stores (hay base React Native en repo, fuera del MVP desplegado).
- ML en producción limitado a lo que esté cableado en API/notebooks; reentrenamiento automático es **fase posterior**.

---

## 3. Estado MVP actual

### 3.1 Entregables desplegables

| Componente | URL / entrada | Estado MVP |
|------------|---------------|------------|
| SPA Vue 3 | https://metgo3d.netlify.app | Producción |
| API Flask + JWT | https://metgo-api.onrender.com/api | Producción (cold start plan free) |
| Portal Streamlit | https://metgo-streamlit.onrender.com (Blueprint) | Opcional Render |
| Streamlit Cloud | metgo-3d-quillota-60gb.streamlit.app | Portal legacy |
| Desarrollo local | `iniciar_metgo_desarrollo.bat` → :5173 + :8080 | Documentado |

### 3.2 Funcionalidades incluidas en el MVP

- Autenticación JWT (`admin` / `user` / `metgo` demo).
- Módulos Vue: panel, meteo, agrícola, alertas, catálogo, configuración, **centro de servicios**, **visor de puertos** (`/puertos`).
- API: estaciones, meteo histórico/pronóstico, alertas, recomendaciones agrícolas, catálogo de módulos, orquestación Streamlit local, URLs de visor en nube.
- Visor de puertos: iframe `embed=true` + página `Visor_de_puerto` en Streamlit.
- Repo ordenado: `metgo/`, `scripts/compat/`, `scripts/git/`, raíz mínima (`docs/RAIZ_REPOSITORIO.md`).

### 3.3 Estándares “developer profesional” ya aplicados

- **Arquitectura por capas** y `metgo.paths.PROJECT_ROOT` centralizado.
- **Separación UI**: Vue (operación diaria) vs Streamlit (análisis profundo).
- **Seguridad**: JWT, `.env` fuera de Git, CORS configurable, sin secretos en staging.
- **Despliegue como código**: `render.yaml`, `netlify.toml`, `requirements.txt`.
- **Documentación operativa**: despliegue Vue/Netlify, API, Streamlit Cloud, visor, Git manual.
- **Convención de commits** y scripts de publicación manual.

### 3.4 Extensiones post-MVP (fases 4–10, ya en repo)

- Integración dinámica módulos 01–12: `GET /api/integracion/estado`, hub Vue `/integracion`.
- ETL nocturno → SQLite `meteo_historico.db`; workers MQTT y cola ML.
- Registro MLOps con modelos **servibles** vs no servibles (`/ml`).
- Notificaciones webhook + outbox (+ SMTP opcional); métricas `GET /api/metrics`.

Detalle completo: **[`PROMPT_ESCALAMIENTO_MVP.md`](PROMPT_ESCALAMIENTO_MVP.md)**.

### 3.5 Deuda técnica aceptada en MVP (explícita)

- Dual stack Vue + Streamlit (migración incompleta).
- Plan free Render → latencia y cold start.
- Dashboards Plotly completos solo en PC o vía visor (carga bajo demanda en nube).
- SMTP corporativo requiere plan de pago o webhook alternativo.

---

## 4. Propuestas de implementación (fases)

Priorizar **impacto usuario** y **reducción de complejidad operativa**.

### Fase 1 — Consolidar MVP (0–6 semanas)

| # | Iniciativa | Descripción | Criterio de éxito |
|---|------------|-------------|-------------------|
| 1.1 | **OpenAPI 3** | Documentar `/api/*` con Swagger UI o Redoc en ruta `/api/docs` | Tercero puede probar login + meteo sin leer código |
| 1.2 | **CI mínima** | GitHub Actions: `pytest tests/`, lint Python, `npm run build` en `frontend/vue` | PR bloqueado si falla smoke |
| 1.3 | **Health unificado** | `/api/health` + página estado en Vue (API, versión commit, latencia) | Operador ve “sistema OK” en 5 s |
| 1.4 | **Cache OpenMeteo** | Redis o cache en disco en `08_Gestion_Datos` (TTL 15 min) | Menos timeouts; menos cold pressure en Render |
| 1.5 | **Vue como única puerta** | Menú claro; Streamlit solo en visor/enlaces; copy consistente en español | Usuario netlify no intenta abrir :8506 local |

### Fase 2 — Producto ampliado (6–12 semanas)

| # | Iniciativa | Descripción | Criterio de éxito |
|---|------------|-------------|-------------------|
| 2.1 | **Migrar 3 dashboards críticos a Vue** | Visualizaciones, comparativo, métricas globales (charts Plotly → ECharts/Plotly.js) | Abandonar 3 puertos locales para esas funciones |
| 2.2 | **Alertas configurables** | Umbrales por estación/usuario en API + UI | Crear/editar alerta sin tocar código |
| 2.3 | **Roles RBAC** | `admin`, `agronomo`, `operador`, `lectura` en JWT claims | Rutas Vue y endpoints respetan rol |
| 2.4 | **PWA ligera** | Service worker + caché última estación | Consulta básica offline tras primera visita |
| 2.5 | **Docker Compose dev** | `api` + `vue` + opcional `redis` un comando | Onboarding dev &lt; 15 min |

### Fase 3 — Escala y datos propios (3–6 meses)

| # | Iniciativa | Descripción | Criterio de éxito |
|---|------------|-------------|-------------------|
| 3.1 | **Ingesta IoT / estaciones propias** | Módulo `03_Sistema_IoT_Drones` → cola + API | Al menos 1 fuente no solo OpenMeteo |
| 3.2 | **ML ops** | Reentrenamiento programado, registro de modelos, métricas | Modelo versionado desplegable en API |
| 3.3 | **Multi-tenant regional** | Casablanca / otras comunas como “organizaciones” | Config aisladas por tenant |
| 3.4 | **Observabilidad** | Logs estructurados, Sentry, uptime | Error en prod visible en &lt; 5 min |
| 3.5 | **Streamlit Cloud o Render dedicado por dashboard** | Solo si negocio exige Plotly server-side tal cual | SLA definido por dashboard |

### Fase 4 — Opcional / innovación

- App móvil React Native empaquetada (MVP actual solo web responsive).
- Gemelo digital / mapas 3D (alineado con nombre METGO 3D).
- Integración MINAGRI, DMC u otras APIs oficiales Chile.
- Marketplace de “módulos” instalables vía catálogo API.

---

## 5. Principios para todo desarrollo posterior

1. **No romper entrypoints de despliegue**: `streamlit_app.py` en raíz, `render.yaml`, `netlify.toml`.
2. **Rutas solo vía `metgo.paths`** (o `metgo_paths` shim); no hardcodear `04_Dashboards_Unificados`.
3. **Vue primero** para flujos nuevos; Streamlit solo si hay gráfico Python irreemplazable a corto plazo.
4. **API contract-first**: cambiar OpenAPI antes o junto al endpoint.
5. **Secrets solo en env** (Render, Netlify, Streamlit Secrets); nunca en repo.
6. **Documentar límites nube** al añadir features que usen puertos locales.
7. **Commits en español o inglés técnico**, mensajes con `feat|fix|chore|docs` + alcance.

---

## 6. Métricas de éxito del MVP

| Métrica | Objetivo MVP | Medición |
|---------|--------------|----------|
| Tiempo primer login → ver meteo | &lt; 90 s (incl. cold start Render) | Manual / analytics |
| Disponibilidad API health | &gt; 95 % mes (plan free) | UptimeRobot |
| Módulos Vue sin error 401 | 100 % rutas protegidas | E2E smoke |
| Onboarding desarrollador | README + bat → entorno local | Encuesta interna |
| Claridad puertos vs nube | 0 issues “:8506 no abre en Netlify” | Soporte / issues GitHub |

---

## 7. Prompt listo para pegar

Copie el bloque siguiente en **Cursor Rules**, **Chat**, o **`AGENTS.md`** en la raíz del repo.

```markdown
# Rol

Eres un ingeniero senior full-stack trabajando en **METGO 3D Quillota (MVP)**. Actúas con criterio de producto, arquitectura limpia y entregables desplegables. Respondes en **español** salvo que el código o commits requieran inglés técnico.

# Contexto del producto (MVP)

METGO 3D es un MVP agrometeorológico para el Valle de Aconcagua (Chile): monitoreo, pronóstico (OpenMeteo), recomendaciones agrícolas, alertas y catálogo de módulos.

**Producción actual:**
- Vue 3 SPA: https://metgo3d.netlify.app (Netlify)
- API REST Flask + JWT: https://metgo-api.onrender.com/api (Render)
- Portal/visor Streamlit: metgo-streamlit.onrender.com o Streamlit Cloud (`streamlit_app.py` en raíz)

**Arquitectura del repo:**
- `backend/` — módulos 01–12, `api_rest/`, ML, datos
- `frontend/vue/` — SPA principal (Vite, Pinia, axios)
- `frontend/dashboards/` — Streamlit legacy (puertos 8501–8513 solo en PC)
- `metgo/` — biblioteca compartida (paths, tema Streamlit, portal, vue_embed, dashboard_loader / visor)
- `pages/` — multipágina Streamlit (obligatorio en raíz)
- `scripts/compat/`, `scripts/git/`
- Raíz mínima: ver `docs/RAIZ_REPOSITORIO.md`

**Funcionalidades MVP ya implementadas:**
- Login JWT, módulos meteo/agricola/monitoreo, catálogo, centro de servicios, **visor de puertos** (`/puertos`, `GET /api/servicios/streamlit/{id}/visor`)
- Catálogo con utilidad por puerto; activación nube vs local documentada

# Restricciones técnicas (no negociables)

1. No mover ni renombrar `streamlit_app.py` de la raíz sin actualizar Streamlit Cloud y docs.
2. No commitear `.env`, `secrets.toml`, credenciales.
3. No prometer que los puertos 8501–8513 funcionen en Netlify; en nube usar Visor + Vue.
4. Usar `metgo.paths` / `metgo_paths` para rutas; extender `catalog.py` para nuevos módulos.
5. Cambios mínimos y coherentes con el estilo existente; sin sobre-ingeniería.
6. No hacer `git commit` salvo que el usuario lo pida explícitamente.

# Estándares profesionales que debes aplicar

- Contract-first API (proponer OpenAPI si añades endpoints).
- Vue para nuevas pantallas operativas; Streamlit solo para análisis Python pesado o legacy.
- Manejo explícito de errores API (cold start Render, 401, 504) en UI.
- Documentar en `docs/manuales/` si afecta despliegue o percepción del usuario.
- Tests smoke cuando toques `api_rest` o flujos críticos.

# Roadmap que debes priorizar al proponer trabajo

**Fase 1 (consolidar MVP):** OpenAPI/Swagger, CI GitHub Actions, health dashboard Vue, cache OpenMeteo, UX unificada sin confusión de puertos.

**Fase 2:** Migrar dashboards críticos a Vue, alertas configurables, RBAC, PWA ligera, Docker Compose dev.

**Fase 3:** IoT propio, MLOps, multi-tenant regional, observabilidad (Sentry/logs).

**Fase 4 (opcional):** app móvil, 3D/mapas, APIs institucionales Chile.

Cuando el usuario pida features, responde con: (1) encaje en MVP, (2) diseño breve, (3) archivos a tocar, (4) fase roadmap, (5) riesgos/límites nube.

# Formato de respuesta preferido

- Prosa clara en español, tablas o listas cuando ayuden.
- Diagramas mermaid solo para flujos no triviales.
- Rutas de archivos como `backend/05_APIs_Externas/api_rest/app.py`.
- Si propones implementación, dar pasos verificables (comandos, URLs de prueba).

# Referencias internas obligatorias antes de cambiar despliegue o puertos

- `docs/manuales/QUE_VER_EN_NUBE.md`
- `docs/manuales/VISOR_PUERTOS.md`
- `docs/manuales/DESPLIEGUE_VUE_NETLIFY.md`
- `docs/PROMPT_MVP_METGO.md` (este documento)
```

---

## 8. Variante corta 

```text
Proyecto: METGO 3D MVP (Quillota). Vue en Netlify, API Flask JWT en Render, Streamlit portal/visor. Repo por capas: backend/, frontend/vue/, metgo/, pages/. MVP incluye /puertos y catálogo con utilidad 8501-8513; en nube no hay procesos locales. Sigue docs/PROMPT_MVP_METGO.md, RAIZ_REPOSITORIO.md, QUE_VER_EN_NUBE.md. Estándar profesional: API-first, Vue para UI nueva, cambios mínimos, español, sin commit salvo pedido. Al proponer features, indica fase roadmap (1-4) y límites nube.
```

---

## 9. Enlace en README

Añada en la sección de documentación del `README.md`:

```markdown
- **[Prompt y roadmap MVP](docs/PROMPT_MVP_METGO.md)** — criterios profesionales y propuestas de implementación
```

---

*Última alineación con repo: visor de puertos, reorganización `metgo/` + `scripts/`, despliegue Netlify + Render.*
