# Publicar cambios en GitHub (METGO)

## Recomendado: subida manual

**Guía principal:** [`SUBIR_GITHUB_MANUAL.md`](SUBIR_GITHUB_MANUAL.md)

**Doble clic en la raíz:** `SUBIR_GITHUB_MANUAL.bat` → menú paso a paso.

**Instrucciones:** `backend/10_Deployment_Produccion/scripts/INSTRUCCIONES_SUBIR_A_GITHUB.txt`

**Mensaje de commit sugerido (integración actual):** `MENSAJE_COMMIT_SUGERIDO.txt`

**Comandos copiar/pegar:** `COMANDOS_GIT_MANUAL.txt`

Usted ejecuta `git add`, `git commit` y `git push` en su terminal.

---

## Scripts automáticos (opcional)

Si prefiere asistencia con `.bat`: carpeta `backend/10_Deployment_Produccion/scripts/` (`publicar_github.bat`, `1_preparar_staging_github.bat`, etc.).

---

## 1. Revisar dónde está el proyecto (siempre primero)

### Windows (doble clic)

```text
backend\10_Deployment_Produccion\scripts\revisar_estado_git.bat
```

Muestra:

- Rama actual y si sigue a `origin`
- URL del remoto (GitHub)
- `git status -sb` (archivos modificados)
- Cuántos commits va adelante/atras del remoto
- Últimos commits
- Aviso si hay `.env` en staging

### PowerShell (alternativa)

```powershell
cd D:\METGO_3D_Quillota_60GB
.\backend\10_Deployment_Produccion\scripts\publicar_github.ps1 -SoloRevisar
```

---

## 2. Configurar GitHub (solo la primera vez)

Si `revisar_estado_git.bat` dice **sin remotos**:

```text
backend\10_Deployment_Produccion\scripts\configurar_remoto_github.bat
```

Pegue la URL de su repo, por ejemplo:

`https://github.com/miguellucero123/METGO_3D_Quillota_60GB.git`

---

## 3. Preparar el commit (recomendado tras reorganizar carpetas)

```text
backend\10_Deployment_Produccion\scripts\preparar_commit_github.bat
```

Quita restos de `04_Dashboards_Unificados/` y muestra un resumen antes de publicar.

---

## 4. Subir cambios (commit + push en un solo script automático)

### Opción A — `.bat` con mensaje

```text
backend\10_Deployment_Produccion\scripts\publicar_github.bat "Reorganización: backend, frontend, site-web y docs"
```

Sin argumento, pedirá el mensaje de commit y confirmación **S/N** antes de subir.

### Opción B — PowerShell

```powershell
.\backend\10_Deployment_Produccion\scripts\publicar_github.ps1 -Mensaje "Actualización README y layout por capas"
```

---

## 6. Qué NO se sube (`.gitignore`)

- `.env` y secretos
- `node_modules/`, `frontend/vue/dist/` (si está ignorado)
- `data/`, `logs/`, respaldos pesados
- Caches y `__pycache__/`

Los scripts **bloquean** el push si detectan `.env` en el área de staging.

---

## 7. Streamlit Cloud (después del push)

- **Main file en GitHub:** `streamlit_app.py` (raíz del repo)
- **Secrets:** `METGO_PASSWORD_ADMIN`, `METGO_PASSWORD_USER`, `METGO_PASSWORD_METGO`
- Tras cada `push`, Streamlit Cloud redeploya solo (si el app está conectado al repo)

Guía detallada: [`STREAMLIT_CLOUD.md`](STREAMLIT_CLOUD.md)

---

## 8. Comandos Git manuales (referencia)

```bash
cd D:\METGO_3D_Quillota_60GB
git status -sb
git remote -v
git add -A
git commit -m "Su mensaje"
git push -u origin main
```

---

## 9. Problemas frecuentes

### Muchas líneas `deleted: respaldo_20251011_022103/...`

Es **normal**: ese respaldo salió de la raíz y fue a `backend/12_Respaldos_Archivos/backups/`. Git registra borrado en la ruta vieja (bien para aligerar el repo).

### `Untracked: backend/`, `frontend/`, `docs/`

Es la **nueva estructura** que aún no está en GitHub. Al hacer `publicar_github.bat` se añadirán.

### `no changes added to commit`

Aún no ejecutó `git add` / el script de publicar; o canceló la confirmación.

### `[ERROR] Detectado .env en staging`

Suele ser el archivo **`.env` de la raíz** (contraseñas), no `.env.example`.

```bat
backend\10_Deployment_Produccion\scripts\quitar_secretos_del_staging.bat
backend\10_Deployment_Produccion\scripts\publicar_github.bat "Su mensaje"
```

O manualmente:

```bat
git reset HEAD .env
git rm --cached .env
```

| Problema | Qué hacer |
|----------|-----------|
| `not a git repository` | `git init` o abrir la carpeta correcta del clon |
| `failed to push` | Ejecutar `configurar_remoto_github.bat` o revisar login (GitHub Desktop / PAT) |
| `rejected (fetch first)` | Hacer `git pull --rebase origin main` y volver a publicar |
| Commit vacío | No hay cambios; revise con `revisar_estado_git.bat` |
| Archivos enormes | No subir `12_Respaldos_Archivos/backups/`; ver `.gitignore` |

---

## 10. Orden recomendado tras reorganizar carpetas

1. `revisar_estado_git.bat`
2. Cerrar procesos que bloqueen archivos (Vue `npm run dev`, notebooks)
3. `publicar_github.bat "Layout v4: backend, frontend, site-web, docs"`
4. Comprobar en GitHub que `streamlit_app.py` y `README.md` están en la raíz del repo
