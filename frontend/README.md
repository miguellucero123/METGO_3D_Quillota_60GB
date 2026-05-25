# Frontend METGO

Capa de **presentación operativa**: SPA Vue 3 (uso diario) y dashboards Streamlit (análisis bajo demanda).

## Estructura

```text
frontend/
├── vue/                 # App principal Vue 3 + Vite (puerto 5173)
│   ├── src/views/       # Panel, meteo, agrícola, servicios, módulos…
│   └── src/api/         # Cliente hacia API REST (/api → :8080)
├── dashboards/          # Streamlit operativos (8501–8513 bajo demanda)
│   ├── sistema_auth_dashboard_principal_metgo.py
├── app_movil/           # App React Native (canónico)
└── config/              # Reservado: configuración compartida UI (futuro)
```

> Assets HTML públicos: [`site-web/static/html/`](../site-web/static/html/). Stub legacy: `dashboards/app_movil_metgo/`.

## Arranque rápido

### Vue (recomendado)

```bash
cd frontend/vue
npm install
cp .env.example .env.development   # si no existe
npm run dev
```

Abrir http://127.0.0.1:5173 — requiere API en **8080**.

### Streamlit principal (operadores)

```bash
# Desde la raíz del repo
streamlit run streamlit_app.py
```

### Stack desarrollo (API + Vue)

```bash
backend\10_Deployment_Produccion\scripts\iniciar_metgo_desarrollo.bat
```

### Centro de servicios Streamlit

Con API y Vue activos: menú **Centro de servicios** → iniciar dashboards en puertos 8502–8513.

## Puertos

| Servicio | Puerto |
|----------|--------|
| Vue (Vite) | 5173 |
| API REST | 8080 |
| Streamlit principal | 8501 |
| Otros Streamlit | 8502–8513 |

## Capas relacionadas

| Capa | Rol |
|------|-----|
| [`backend/`](../backend/README.md) | API, ML, datos |
| [`site-web/`](../site-web/README.md) | Dashboard público sin login |
