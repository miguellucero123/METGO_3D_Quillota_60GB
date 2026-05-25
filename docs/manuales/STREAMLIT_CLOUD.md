# Despliegue en Streamlit Cloud

## Main file (obligatorio)

En **share.streamlit.io** → tu app → Settings:

| Campo | Valor |
|-------|--------|
| **Main file path** | `streamlit_app.py` (**obligatorio**; si usa `sistema_auth_dashboard_principal_metgo.py` verá el panel antiguo) |

`streamlit_app.py` es la **página de inicio (portal)** con enlaces a Vue (`index` en Netlify). Las vistas están en `pages/`:

| Archivo | Contenido |
|---------|-----------|
| `pages/1_Resumen_publico.py` | Dashboard público (`site-web/streamlit/dashboard_web_publico.py`) |
| `pages/2_Panel_operadores.py` | Panel con login (`frontend/dashboards/sistema_auth_dashboard_principal_metgo.py`) |

## Secrets

En **Settings → Secrets**, pegue (ajuste contraseñas):

```toml
METGO_PASSWORD_ADMIN = "su_password_admin"
METGO_PASSWORD_USER = "su_password_user"
METGO_PASSWORD_METGO = "su_password_metgo"
```

Mismos usuarios que la API Vue: `admin`, `user`, `metgo`.

## Requirements

Streamlit Cloud usa `requirements.txt` en la raíz del repositorio.

## Tras cada push a GitHub

1. **Main file** al crear la app: `streamlit_app.py` o `sistema_auth_dashboard_principal_metgo.py` (este último en la raíz **redirige** a `streamlit_app.py`).

   En **App settings → General** solo verá subdominio y Python; **no** se puede cambiar el Main file tras el deploy. Si la app es antigua, basta con el wrapper en la raíz + Reboot.
2. En la app → menú **⋮** → **Reboot app** (Streamlit Cloud no siempre recarga al instante).
3. Abra el menú lateral y elija **Resumen público** para ver los cambios de `site-web`.

Si solo ve el panel antiguo sin menú lateral, el despliegue sigue en caché: haga **Reboot** o **Clear cache**.

## URL de referencia

https://metgo-3d-quillota-60gb.streamlit.app
