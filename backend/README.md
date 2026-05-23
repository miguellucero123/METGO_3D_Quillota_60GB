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
| `12_Respaldos_Archivos/` | Backups locales |

## Arranque API

```bash
# Desde la raíz del repositorio
python backend/10_Deployment_Produccion/scripts/iniciar_api_rest.py
```
