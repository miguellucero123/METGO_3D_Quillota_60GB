# Backend METGO

Servidor, datos, APIs, modelos ML, monitoreo, despliegue y respaldos.

## Módulos (01–12 en esta carpeta)

| Carpeta | Rol |
|---------|-----|
| `01_Sistema_Meteorologico/` | OpenMeteo, pronósticos, notebooks |
| `02_Sistema_Agricola/` | Gestión agrícola, riego |
| `03_Sistema_IoT_Drones/` | Sensores e IoT |
| `05_APIs_Externas/` | **API REST** (`api_rest/`) |
| `06_Modelos_ML_IA/` | Machine learning |
| `07_Sistema_Monitoreo/` | Alertas, `metgo_auth.py` |
| `08_Gestion_Datos/` | ETL, `datos/`, runtime |
| `09_Testing_Validacion/` | Pruebas |
| `10_Deployment_Produccion/` | Scripts `.bat`, deploy |
| `12_Respaldos_Archivos/` | Backups locales (no usar en código activo) |

**Nota:** Los módulos **04** (dashboards) y **11** (docs) no viven en `backend/`. Ver [`docs/roadmap/BACKEND_MODULOS_01-12_AUDITORIA.md`](../docs/roadmap/BACKEND_MODULOS_01-12_AUDITORIA.md).

## Arranque

| Componente | Comando |
|------------|---------|
| API REST | `python backend/10_Deployment_Produccion/scripts/iniciar_api_rest.py` |
| API + Vue | `backend/10_Deployment_Produccion/scripts/iniciar_metgo_desarrollo.bat` |
| Dashboard público | `backend/10_Deployment_Produccion/scripts/iniciar_site_web.bat` |

Capas hermanas: [`frontend/`](../frontend/README.md) · [`site-web/`](../site-web/README.md)

Rutas centralizadas: [`metgo_paths.py`](../metgo_paths.py) en la raíz del repo.
