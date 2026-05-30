# Scripts legacy vs pipeline de producción (módulo 06)

## Problema: «modelos corruptos»

Los errores reportados (`monotonic_cst`, `_gb_losses`, `archivo no encontrado`) **no suelen ser corrupción de disco**, sino:

1. **Artefactos entrenados con sklearn antiguo** (< 1.4) incompatibles con sklearn 1.4+ en Render.
2. **Scripts legacy ejecutados desde el CWD equivocado**, que crean carpetas paralelas (`scripts/modelos_ml/`, raíz del repo, etc.) en lugar de `backend/06_Modelos_ML_IA/modelos/`.
3. **Formato de artefacto distinto al esperado por la API** (p. ej. `joblib.dump({...})` con dict en híbridos innovadores, `.pkl` mezclados con `.joblib`).
4. **Features de entrenamiento ≠ features de inferencia** en el registry antiguo (8 features genéricas vs 5–16 por modelo).

## Fuente de verdad en producción

| Qué | Dónde |
|-----|--------|
| Entrenamiento | `backend/05_APIs_Externas/api_rest/integracion/ml_train_runner.py` |
| Catálogo 43 modelos | `api_rest/integracion/ml_train_catalog.py` |
| Contrato features/R² | `modelos/model_manifest.json` |
| Inferencia API | `api_rest/ml_registry_core.py` (modo manifest) |

Comando recomendado (desde raíz del repo):

```bash
PYTHONPATH=backend/05_APIs_Externas python -c \
  "from api_rest.integracion.ml_train_runner import entrenar_todos; print(entrenar_todos())"
```

API (admin): `POST /api/ml/train/run`

## Scripts legacy — NO usar en producción

| Script | Riesgo principal |
|--------|------------------|
| `sistema_predicciones_ml_avanzado.py` | Escribe en `modelos_ml/` relativo al CWD |
| `sistema_modelos_dinamicos.py` | Idem + scalers separados |
| `sistema_modelos_ultra_optimizado.py` | Idem |
| `sistema_modelos_hibridos_innovadores.py` | Guarda **dict** en joblib, no estimador |
| `pipeline_ml_optimizado.py` | Sobrescribe `modelos_ml_quillota/` con nombres distintos |
| `fix_ml_models.py` | Datos sintéticos + rutas relativas; pisa modelos buenos |
| `ia_avanzada_metgo.py` / `deep_learning_avanzado_metgo.py` | TensorFlow `.h5` no integrados en API REST |

Todos bloquean ejecución directa salvo `METGO_ALLOW_LEGACY_ML=1`.

## Auditoría

```bash
python backend/06_Modelos_ML_IA/scripts/auditar_carpeta_modelos.py
```

## Residuos seguros de ignorar (no en manifest)

- `modelos_ml_quillota/*.pkl` — formatos antiguos, reemplazados por `.joblib` del manifest.
- `modelos/modelos/deep_learning/*.h5` — cuarentena documentada en `MIGRACION_MODELOS_NO_UTILIZABLES.md`.

No borrar manualmente los `.joblib` listados en `model_manifest.json` sin re-entrenar.
