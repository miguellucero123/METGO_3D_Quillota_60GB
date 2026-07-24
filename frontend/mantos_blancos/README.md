# METGO Mantos Blancos (E8)

SPA Vue 3 + Vite — **ventanas operacionales de faena** (tronadura, transporte, izaje).

## Desarrollo local

```powershell
cd d:\METGO_3D_Quillota_60GB\frontend\mantos_blancos
npm install
npm run dev
```

Puerto por defecto: **5176**.

API: `VITE_METGO_API` o fallback a `https://metgo-api.onrender.com/api`.

**Auth E9:** pantalla `/login` — demo `mantos`/`mantos123` o `admin`/`admin123`.

## Endpoints usados

- `GET /api/public/operaciones/alertas?sitio=mantos_blancos&turno=dia|noche`
- `GET /api/public/operaciones/{punto}/ventanas?horas=48`

## Identidad

Todo lo específico del sitio vive en `src/site.config.js` (tema cobre `#fb923c`).
