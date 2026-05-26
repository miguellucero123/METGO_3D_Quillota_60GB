# Subir el proyecto a GitHub (manual)

**Repositorio:** https://github.com/miguellucero123/METGO_3D_Quillota_60GB  
**Rama:** `master`

## Inicio (desde la raíz del proyecto)

Doble clic en:

```text
SUBIR_GITHUB_MANUAL.bat
```

Abre el **menú** en `backend/10_Deployment_Produccion/scripts/` con los pasos 1 → 2 → 3.

## Archivos importantes (misma carpeta de scripts)

| Archivo | Para qué |
|---------|----------|
| `INSTRUCCIONES_SUBIR_A_GITHUB.txt` | Guía en texto plano |
| `COMANDOS_GIT_MANUAL.txt` | Comandos para copiar/pegar |
| `MENSAJE_COMMIT_SUGERIDO.txt` | Mensaje listo para este commit (integración fases 4–10) |
| `1_preparar_staging_github.bat` | Paso 1: `git add` |
| `2_commit_github_sugerido.bat` | Paso 2: commit con mensaje sugerido |
| `3_push_github.bat` | Paso 3: `git push origin master` |

## Orden recomendado en el menú

1. **Revisar estado**  
2. **Preparar staging**  
3. **Commit** (opción 3 = mensaje sugerido actualizado)  
4. **Push**

## No subir

`.env`, `.streamlit/secrets.toml`, carpetas `datos_runtime/`.

Guía ampliada: [`PUBLICAR_GITHUB.md`](PUBLICAR_GITHUB.md)
