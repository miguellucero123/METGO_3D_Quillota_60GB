# METGO 3D — Quillota

Sistema integrado de monitoreo meteorológico y gestión agrícola (MIP) para el Valle de Quillota, Chile.

**Actualización:** 2026-05-23 — Raíz organizada en **backend · frontend · site-web · docs**.

---

## Estructura de la raíz

```text
METGO_3D_Quillota_60GB/
├── backend/          # Módulos 01–12 (API, datos, ML, deploy…)
├── frontend/         # Vue 3 + dashboards Streamlit
├── site-web/         # Capa pública (dashboard web público)
├── docs/             # Documentación del proyecto
├── streamlit_app.py  # Entrypoint Streamlit Cloud
├── metgo_paths.py    # Rutas centralizadas (layout capas + legacy)
├── requirements.txt
└── README.md
```

| Carpeta | Contenido |
|---------|-----------|
| [`backend/`](backend/README.md) | `01` meteo, `05` API REST, `07` auth, `08` datos, `10` deploy… |
| [`frontend/`](frontend/README.md) | `vue/` (app principal), `dashboards/` (Streamlit) |
| [`site-web/`](site-web/README.md) | Exposición pública |
| [`docs/`](docs/INDICE_MODULOS.md) | Manuales, estructura, propuesta de layout |

---

## Inicio rápido

### Windows (recomendado)

```bat
backend\10_Deployment_Produccion\scripts\iniciar_metgo_desarrollo.bat
```

Abrir **http://127.0.0.1:5173** — API en **:8080**, Vue en **:5173**.

### Manual

```bash
pip install -r requirements.txt

python backend/10_Deployment_Produccion/scripts/iniciar_api_rest.py

cd frontend/vue && npm install && npm run dev
```

### Streamlit

```bash
streamlit run streamlit_app.py
```

Centro de servicios en Vue (`/servicios`) para iniciar otros dashboards Streamlit bajo demanda.

---

## Arquitectura

```text
  frontend/vue (:5173)  ──JWT──►  backend/05_APIs_Externas (:8080)
                                        │
                    backend/01, 07, 08, 06…
  frontend/dashboards (:8501+)  ◄── Streamlit bajo demanda
  site-web/streamlit            ◄── Acceso público
```

---

## Variables de entorno

`METGO_PASSWORD_ADMIN`, `METGO_PASSWORD_USER`, `METGO_PASSWORD_METGO`, `METGO_JWT_SECRET`, `METGO_API_PORT` (default `8080`).

Copiar `.env.example` → `.env` en la raíz.

---

## Documentación

- [Índice de módulos](docs/INDICE_MODULOS.md)
- [Estructura y reglas](docs/ESTRUCTURA_PROYECTO_METGO.md)
- [Propuesta layout capas](docs/PROPUSTA_LAYOUT_CAPAS.md)
- [API REST](docs/manuales/API_REST.md)
- [Streamlit Cloud](docs/manuales/STREAMLIT_CLOUD.md)

---

## Publicar en GitHub

1. **Revisar estado:** `backend\10_Deployment_Produccion\scripts\revisar_estado_git.bat`  
2. **Subir cambios:** `publicar_github.bat "Descripción del cambio"`  

Guía completa: [`docs/manuales/PUBLICAR_GITHUB.md`](docs/manuales/PUBLICAR_GITHUB.md)

---

## Mantener el orden

```bash
python backend/10_Deployment_Produccion/scripts/reorganizar_proyecto_v2.py --dry-run
python backend/10_Deployment_Produccion/scripts/reorganizar_proyecto_v3.py --dry-run
python backend/10_Deployment_Produccion/scripts/reorganizar_layout_capas_v4.py --dry-run
```

Cierre editores/terminales que usen `frontend/vue` antes de v4 si Windows bloquea archivos.

---

## Streamlit Cloud

- **Main file:** `streamlit_app.py` (raíz)
- **Secrets:** contraseñas `METGO_PASSWORD_*`

---

## Licencia

MIT — ver `LICENSE`.
