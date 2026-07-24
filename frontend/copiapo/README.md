# METGO Copiapó (E7)

SPA Vue 3 — **calidad del aire** (ICAP, PM2.5/PM10, recomendaciones de salud).

- Identidad: ámbar `#fbbf24` en `src/site.config.js`
- API: `https://metgo-api.onrender.com/api/public/aire/*`
- Estaciones: malla 7 puntos (ver `site.config.js`)
- **Auth E9:** login JWT (`/login`) — demo `copiapo`/`copiapo123` o `admin`/`admin123`

## Local

```bash
cd frontend/copiapo
cp .env.example .env   # opcional
npm install
npm run dev            # http://localhost:5175
```

## Netlify

- Base directory: `frontend/copiapo`
- Build: `npm ci && npm run build`
- Publish: `dist`
- Env: `VITE_METGO_API=https://metgo-api.onrender.com/api`
- Añadir origen del sitio a `METGO_CORS_ORIGINS` en Render

## Verificación

```bash
curl -s "https://metgo-api.onrender.com/api/public/aire/copiapo_centro"
curl -s "https://metgo-api.onrender.com/api/public/estaciones?sitio=copiapo"
npm run build
```

## Fase

**E7** + auth **E9** — `docs/roadmap/PLAN_MAESTRO_METGO_MULTISITIO.md`
