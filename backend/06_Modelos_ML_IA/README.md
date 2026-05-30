# 06 — Modelos ML / IA

## Producción (usar siempre)

| Componente | Ruta |
|------------|------|
| Artefactos `.joblib` | `modelos/` (subcarpetas por paquete) |
| Contrato API | `modelos/model_manifest.json` |
| Entrenamiento unificado | `backend/05_APIs_Externas/api_rest/integracion/ml_train_runner.py` |
| Inferencia REST | `api_rest/ml_registry_core.py` |

Re-entrenar los 43 modelos (datos reales: CSV 5 años + OpenMeteo; sin sintético por defecto):

```bash
PYTHONPATH=backend/05_APIs_Externas python -c \
  "from api_rest.integracion.ml_train_runner import entrenar_todos; print(entrenar_todos())"
```

Solo tests/CI con datos sintéticos: `METGO_ML_ALLOW_SYNTHETIC=1`

Auditoría local de la carpeta `modelos/`:

```bash
python backend/06_Modelos_ML_IA/scripts/auditar_carpeta_modelos.py
```

## Scripts en `scripts/` (legacy)

Los scripts `sistema_*.py`, `pipeline_ml_optimizado.py`, `fix_ml_models.py`, etc. son **históricos del MVP**. Escriben rutas **relativas al directorio de trabajo** y pueden:

- Crear carpetas duplicadas fuera de `modelos/`
- Sobrescribir `.joblib` con formatos incompatibles (dict, sklearn viejo, `.pkl`)
- Romper el manifest que consume la API

Están bloqueados al ejecutarlos directamente. Ver `modelos/GUIA_SCRIPTS_LEGACY.md`.

Para forzar ejecución manual (solo desarrollo): `METGO_ALLOW_LEGACY_ML=1`

## Streamlit del módulo

`main.py` — panel demo; no entrena modelos reales.

## Fase roadmap

DT-x (deuda técnica ML) · 3.2 MLOps · 8.x train unificado
