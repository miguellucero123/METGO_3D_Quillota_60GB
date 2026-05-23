# 04 — Dashboards unificados

Capa de presentación del sistema METGO: interfaces web modernas y dashboards Streamlit legacy.

## Estructura

```text
04_Dashboards_Unificados/
├── frontend_vue/          # ★ App principal Vue 3 + Vite (puerto 5173)
│   ├── src/views/         # Panel, meteo, agrícola, servicios, módulos…
│   └── src/api/           # Cliente hacia API REST
├── dashboards/            # Dashboards Streamlit (8501–8513 bajo demanda)
│   ├── mobile/            # Config y caché móvil
│   └── sistema_auth_dashboard_principal_metgo.py
├── config/                # Configuración compartida
├── static/                # Assets estáticos legacy
└── templates/             # Plantillas HTML legacy
```

## Arranque rápido

### Vue (recomendado)

```bash
cd frontend_vue
npm install
npm run dev
```

Abrir http://127.0.0.1:5173 — requiere API en :8080.

### Streamlit principal

```bash
# Desde la raíz del repo
streamlit run streamlit_app.py
```

### Centro de servicios (Streamlit bajo demanda)

Con API y Vue activos: menú **Centro de servicios** → pestaña Streamlit → **Iniciar** / **Abrir**.

## Puertos habituales

| Servicio | Puerto |
|----------|--------|
| Vue (Vite) | 5173 |
| API REST | 8080 |
| Streamlit principal | 8501 |
| Otros dashboards Streamlit | 8502–8513 |
