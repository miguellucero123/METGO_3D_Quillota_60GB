# Despliegue en Streamlit Cloud

## Main file (obligatorio)

En **share.streamlit.io** → tu app → Settings:

| Campo | Valor |
|-------|--------|
| **Main file path** | `streamlit_app.py` |

`streamlit_app.py` carga rutas con `metgo_paths` y ejecuta el dashboard en  
`04_Dashboards_Unificados/dashboards/sistema_auth_dashboard_principal_metgo.py`.

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

## Tras cambiar el main file

1. Guarde `streamlit_app.py` en la raíz del repo en GitHub.
2. En Streamlit Cloud, confirme **Main file path** = `streamlit_app.py`.
3. **Reboot app** desde el menú de la app.

## URL de referencia

https://metgo-3d-quillota-60gb.streamlit.app
