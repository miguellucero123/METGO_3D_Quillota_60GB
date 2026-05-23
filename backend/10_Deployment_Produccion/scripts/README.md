# Scripts de despliegue y arranque

Todos los comandos de ejecución local viven aquí. Los `.bat` hacen `cd` a la raíz del repo automáticamente (`%~dp0..\..`).

## Arranque diario (recomendado)

| Archivo | Uso |
|---------|-----|
| `iniciar_metgo_desarrollo.bat` | API :8080 + Vue :5173 |
| `iniciar_api_rest.py` | Solo API Flask |
| `iniciar_frontend_vue.bat` | Solo frontend Vue |

## GitHub

| Archivo | Uso |
|---------|-----|
| `revisar_estado_git.bat` | Ver rama, remoto, cambios pendientes |
| `configurar_remoto_github.bat` | Enlazar `origin` (primera vez) |
| `publicar_github.bat` | `git add`, commit y push |
| `publicar_github.ps1` | Igual en PowerShell (`-SoloRevisar`, `-Mensaje`) |

Guía: [`docs/manuales/PUBLICAR_GITHUB.md`](../../../docs/manuales/PUBLICAR_GITHUB.md)

## Reorganización del proyecto

| Script | Descripción |
|--------|-------------|
| `reorganizar_proyecto_v2.py` | Mueve archivos sueltos de raíz a módulos 01–12 |
| `reorganizar_proyecto_v3.py` | Runtime `data`/`logs`, respaldos, `metgo_auth`, limpieza duplicados |

```bash
python 10_Deployment_Produccion/scripts/reorganizar_proyecto_v3.py --dry-run
python 10_Deployment_Produccion/scripts/reorganizar_proyecto_v3.py
```

## Otros grupos (legacy / producción)

- **Acceso externo:** `configurar_acceso_externo*.bat`, `ejecutar_con_ngrok.py`
- **Sistema permanente:** `sistema_permanente_metgo.py`, `iniciar_sistema_automatico.py`
- **Streamlit Cloud:** `deploy_streamlit_cloud.py`
- **Mantenimiento:** `optimizar_*.py`, `monitorear_sistema.py`

Documentación: [`11_Documentacion/manuales/`](../../11_Documentacion/manuales/)
