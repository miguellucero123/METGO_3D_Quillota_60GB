# Vue embebido en Streamlit (iframe)

Streamlit Cloud **no ejecuta** Vue. La solución es:

1. Publicar la SPA en **Netlify** (recomendado) o Vercel.
2. API REST en un host público (HTTPS).
3. Secret `METGO_VUE_URL` en Streamlit Cloud.
4. Menú lateral → **3 Panel Vue embebido**.

**Guía Netlify paso a paso:** [`DESPLIEGUE_VUE_NETLIFY.md`](DESPLIEGUE_VUE_NETLIFY.md)

## Netlify (resumen)

1. [netlify.com](https://www.netlify.com) → Import GitHub → repo METGO.
2. Usa `netlify.toml` en la raíz (base `frontend/vue`, publish `dist`).
3. Variable de entorno: `VITE_METGO_API=https://su-api.ejemplo.com/api`
4. URL del sitio → Secret Streamlit:

```toml
METGO_VUE_URL = "https://metgo-quillota.netlify.app"
```

## Vercel (alternativa)

1. Root Directory: `frontend/vue`
2. Build: `npm run build` · Output: `dist`
3. `VITE_METGO_API` en variables de entorno
4. `METGO_VUE_URL = "https://su-app.vercel.app"`

## API y CORS

```bash
METGO_CORS_ORIGINS=https://metgo-quillota.netlify.app,https://metgo-3d-quillota-60gb.streamlit.app
```

## Local

```powershell
python backend\10_Deployment_Produccion\scripts\iniciar_api_rest.py
cd frontend\vue && npm run dev
streamlit run streamlit_app.py
```

→ **3 Panel Vue embebido** usa `http://127.0.0.1:5173` por defecto.

## Limitaciones

- Iniciar/Detener Streamlit por puertos: solo en PC local.
- Login JWT en iframe: si falla, abrir Vue en pestaña nueva.
