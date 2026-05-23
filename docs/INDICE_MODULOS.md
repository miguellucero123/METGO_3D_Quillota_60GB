# Índice de módulos METGO

Los módulos numerados `01`–`12` viven bajo **`backend/`** (layout por capas v4).

| Carpeta en `backend/` | Rol |
|----------------------|-----|
| `01_Sistema_Meteorologico/` | OpenMeteo, pronósticos, notebooks |
| `02_Sistema_Agricola/` | Gestión agrícola |
| `03_Sistema_IoT_Drones/` | IoT y sensores |
| `05_APIs_Externas/` | **API REST** (`api_rest/`) |
| `06_Modelos_ML_IA/` | Machine learning |
| `07_Sistema_Monitoreo/` | Alertas, `metgo_auth.py` |
| `08_Gestion_Datos/` | Datos, ETL, runtime |
| `09_Testing_Validacion/` | Pruebas |
| `10_Deployment_Produccion/` | Deploy, `.bat`, reorganizadores |
| `12_Respaldos_Archivos/` | Backups |

## Capas en la raíz

| Carpeta | Rol |
|---------|-----|
| `frontend/vue/` | App Vue 3 (puerto 5173) |
| `frontend/dashboards/` | Streamlit operadores |
| `site-web/` | Dashboard público |
| `docs/` | Esta documentación |

## Arranque

```bash
python backend/10_Deployment_Produccion/scripts/iniciar_api_rest.py
cd frontend/vue && npm run dev
```

Ver [`PROPUSTA_LAYOUT_CAPAS.md`](PROPUSTA_LAYOUT_CAPAS.md) y [`ESTRUCTURA_PROYECTO_METGO.md`](ESTRUCTURA_PROYECTO_METGO.md).
