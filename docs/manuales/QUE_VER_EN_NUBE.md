# Qué se ve en la nube (Netlify + Render) y qué no

## Idea clave

**Netlify y Render no replican los puertos 8501, 8502, 8506… de tu PC.**

En local, cada dashboard Streamlit es **otro proceso** en **otro puerto**. En la nube el número de puerto es una **etiqueta de utilidad** (qué hace ese módulo), no un servidor escuchando en `:8506`.

## Tabla rápida: ¿qué uso en la nube?

| Necesito… | Dónde en la app | ¿Puerto local? |
|-----------|-----------------|----------------|
| Trabajar a diario (meteo, riego, alertas) | Vue → menú **Meteorología** / **Agricultura** / **Alertas** | No |
| Ver estado API y servicios | Vue → **Estado sistema** (`/estado`) | No |
| Entender qué es el puerto 8506, 8502, etc. | **Centro de servicios** o **Visor de puertos** | Solo etiqueta en nube |
| Ver gráficos Plotly legacy en internet | **Visor de puertos** → activar en nube | No (visor Render) |
| Gráficos Plotly al 100 % como en el PC | Instalar METGO local + **Iniciar PC** | Sí (`8501–8513`) |
| Documentación API para integradores | https://metgo-api.onrender.com/api/docs | No |

## Qué tienes desplegado

| Servicio | URL | Qué hace |
|----------|-----|----------|
| **Netlify** | https://metgo3d.netlify.app | App **Vue** (login, meteo, agrícola, alertas, **Centro de servicios**) |
| **Render `metgo-api`** | https://metgo-api.onrender.com | **API REST** (catálogo, estados de puertos, login, **/api/docs**) |
| **Render `metgo-streamlit`** | https://metgo-streamlit.onrender.com | **Portal** Streamlit (catálogo, `?activar=modulo`) |
| **Streamlit Cloud** (opcional) | https://metgo-3d-quillota-60gb.streamlit.app | Mismo portal multipágina |

## Visor de puertos (recomendado)

En **https://metgo3d.netlify.app/puertos**:

- Lista **8501–8513** con utilidad de cada uno.
- **Iframe integrado**: carga el dashboard desde Render (`Visor_de_puerto`) sin usar `127.0.0.1`.
- Detalle técnico: `docs/manuales/VISOR_PUERTOS.md`.

## Centro de servicios (Vue)

En **https://metgo3d.netlify.app/servicios** verá:

- Cada módulo con **puerto**, **utilidad** y estado.
- **Ver en visor** → abre `/puertos?id=...` con iframe.
- **Ver en Vue** → meteo, agricultura, alertas sin Streamlit.
- **Iniciar PC** → solo en local.

La API en Render debe tener `METGO_STREAMLIT_CLOUD_URL=https://metgo-streamlit.onrender.com` (ya en `render.yaml`).

## Qué NO hace la nube hoy

| En tu PC | En Netlify |
|----------|------------|
| Proceso real en `:8506` con Plotly completo | No (salvo que despliegue esa app aparte) |
| Trece Streamlit simultáneos | Un portal + Vue |

## Qué debes hacer según tu objetivo

### A) Usar METGO desde cualquier lugar (recomendado)

1. SPA Cloudflare/Netlify → login con cuenta de Render (`METGO_PASSWORD_*`)
2. **Centro de servicios** o **Catálogo** → **Ver en Vue**

### B) Ver utilidad de cada puerto en la interfaz

1. **Servicios** en Vue (lista con descripción por módulo).
2. O portal Render / Streamlit Cloud → página **Catálogo y servicios**.

### C) Dashboard Streamlit Plotly completo en internet

Desplegar **cada** `.py` como app separada en Streamlit Cloud o Render, o migrar pantallas a Vue.

### D) Desarrollo local con todos los puertos

```bat
backend\10_Deployment_Produccion\scripts\iniciar_metgo_desarrollo.bat
```

- Vue: http://127.0.0.1:5173/servicios  
- API: :8080  
- **Iniciar PC** en cada fila → puertos 8501–8513

## Checklist

- [ ] Render **metgo-api** Live + variable `METGO_STREAMLIT_CLOUD_URL`
- [ ] Render **metgo-streamlit** Live (opcional, portal)
- [ ] Netlify publicado (último push)
- [ ] En Netlify: **Activar en nube**, no esperar que `:8506` abra en el navegador remoto

## Resumen

**Netlify = Vue + catálogo de puertos con utilidad. Render API = estados y enlaces. Puertos 850x = procesos en tu PC**; en nube se sustituyen por Vue y el portal `metgo-streamlit.onrender.com`.
