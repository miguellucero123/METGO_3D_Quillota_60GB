# Subir cambios a GitHub (manual)

Guía corta: **usted ejecuta cada comando** en CMD o PowerShell.  
Carpeta del proyecto:

```text
D:\METGO_3D_Quillota_60GB
```

---

## 1. Abrir terminal en el proyecto

**CMD o PowerShell:**

```bat
cd /d D:\METGO_3D_Quillota_60GB
```

---

## 2. Revisar (opcional)

```bat
git status -sb
git remote -v
git branch --show-current
git log -3 --oneline
```

---

## 3. Añadir archivos al commit (staging)

```bat
git add -A
```

Quitar secretos del staging (si aparecen):

```bat
git reset HEAD .env
git reset HEAD .env.local
git reset HEAD .streamlit\secrets.toml
```

Ver qué se va a commitear:

```bat
git diff --cached --name-status
git diff --cached --shortstat
```

**No debe aparecer** `.env` ni `secrets.toml` en la lista.

---

## 4. Commit (usted elige el mensaje)

Ejemplo para esta versión (Visor de puertos):

```bat
git commit -m "feat: Visor de puertos integrado, utilidad por modulo y despliegue nube"
```

O mensaje más largo (varias líneas):

```bat
git commit -m "feat: Visor de puertos integrado" -m "- Vue /puertos con iframe y API visor" -m "- Streamlit Visor_de_puerto en Render" -m "- Centro de servicios y docs"
```

Si Git dice *nothing to commit*: no hay cambios en staging; repita el paso 3.

---

## 5. Push a GitHub

Ver rama actual:

```bat
git branch --show-current
```

Subir (cambie `master` por su rama si es otra, por ejemplo `main`):

```bat
git push origin master
```

Primera vez en esa rama:

```bat
git push -u origin master
```

---

## 6. Después del push

- **Netlify** (Vue): redeploy si no es automático.
- **Render** (`metgo-api`, `metgo-streamlit`): redeploy manual o auto según el panel.
- **Streamlit Cloud**: actualiza solo si el repo está conectado.

---

## Problemas frecuentes

| Mensaje | Qué hacer |
|---------|-----------|
| `rejected (fetch first)` | `git pull --rebase origin master` y luego `git push origin master` |
| `failed to push` / auth | Iniciar sesión en GitHub Desktop o configurar token (PAT) |
| `.env` en staging | `git reset HEAD .env` y no volver a añadirlo |
| `nothing to commit` | `git add -A` y revisar `git status` |
| Rama distinta | Use el nombre que devuelve `git branch --show-current` en el push |

---

## Referencia rápida (todo seguido)

```bat
cd /d D:\METGO_3D_Quillota_60GB
git status -sb
git add -A
git reset HEAD .env
git reset HEAD .streamlit\secrets.toml
git diff --cached --name-status
git commit -m "feat: Visor de puertos integrado, utilidad por modulo y despliegue nube"
git push origin master
```

---

Los `.bat` automáticos siguen en `backend\10_Deployment_Produccion\scripts\` por si los necesita; **esta guía es la forma recomendada**.
