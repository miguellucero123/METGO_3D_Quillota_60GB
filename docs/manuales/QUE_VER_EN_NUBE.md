# Qué se ve en la nube (Netlify + Render) y qué no

## Idea clave

**Netlify y Render no replican los puertos 8501, 8502, 8506… de tu PC.**

En local, cada dashboard Streamlit es **otro proceso** en **otro puerto**. En la nube eso no existe así: hay **URLs HTTPS distintas**, no `:8506` en el mismo servidor.

## Qué tienes hoy desplegado

| Servicio | URL | Qué hace |
|----------|-----|----------|
| **Netlify** | https://metgo3d.netlify.app | App **Vue** (login, meteo, agrícola, alertas, catálogo) |
| **Render `metgo-api`** | https://metgo-api.onrender.com | **API REST** (datos, JWT, login) |
| **Streamlit Cloud** (opcional) | https://metgo3d.streamlit.app | Portal + iframe a Vue |

Vue en Netlify **ya usa** la API en Render. Eso **sí** es “ver METGO en la nube”.

## Qué NO hace la nube hoy

| En tu PC | En Netlify/Render |
|----------|-------------------|
| `http://127.0.0.1:8501` dashboard principal | No existe ese puerto en internet |
| `http://127.0.0.1:8506` visualizaciones | Idem |
| Botón **Iniciar** en Centro de servicios | Solo arranca procesos **en el servidor**; en Render free **no** hay 13 Streamlit |

Por eso ves el mensaje: *use App Vue o instale METGO en su PC*.

## Qué debes hacer según tu objetivo

### A) Quiero usar METGO desde cualquier lugar (recomendado)

1. Abre **https://metgo3d.netlify.app**
2. Login: `admin` / `admin123`
3. Use **Meteorología**, **Agricultura**, **Alertas** (todo vía API en Render).

No necesita puertos 850x en la nube.

### B) Quiero el portal Streamlit en la nube

1. Cuenta **Streamlit Cloud** → app con `streamlit_app.py` (ya configurado).
2. Secret: `METGO_VUE_URL = "https://metgo3d.netlify.app"`
3. Opcional: segundo servicio **Render `metgo-streamlit`** (ver `render.yaml`) → URL tipo `https://metgo-streamlit.onrender.com`

Sigue siendo **un** portal, no trece puertos.

### C) Quiero cada dashboard Streamlit (8502, 8506…) en internet

Hay que **desplegar cada uno aparte** (no un solo Netlify):

| Opción | Esfuerzo | Coste |
|--------|----------|-------|
| **Varias apps en Streamlit Cloud** (una por `.py`) | Alto (muchas apps) | Gratis limitado |
| **Varios servicios en Render** (uno por dashboard) | Muy alto | Varios “free” con cold start |
| **Migrar pantallas a Vue** (ya empezado) | Medio | Netlify + 1 API Render |

No hay un botón mágico en Netlify para “abrir :8506 en la nube”.

### D) Quiero desarrollar en PC con todos los puertos

```bat
backend\10_Deployment_Produccion\scripts\iniciar_metgo_desarrollo.bat
```

- Vue: http://127.0.0.1:5173  
- API: :8080  
- Streamlit bajo demanda: 8501–8513 (Centro de servicios, pestaña Streamlit, **solo local**)

## Checklist rápido

- [ ] Netlify **Published** (último push)
- [ ] Render **metgo-api** Live → `/api/health` OK
- [ ] Login en Netlify OK (tras despertar API ~1 min)
- [ ] No pulsar **Abrir :8501** desde Netlify (no funcionará)
- [ ] Streamlit Cloud: `streamlit_app.py` + secret `METGO_VUE_URL`

## Resumen en una frase

**Netlify = cara moderna (Vue). Render = cerebro (API). Los puertos 850x = taller en tu computador**, salvo que despliegue cada dashboard Streamlit como **otra app** en Streamlit Cloud o Render.
