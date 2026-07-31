# E11 — Calidad SPA VENTORA (PWA / a11y / i18n)

## E11.1 (2026-07-31)

- **PWA activa** (`vite-plugin-pwa`): manifest VENTORA + workbox `NetworkFirst` para `/api/`.
- **a11y:** skip-link; `<main>`; labels/ARIA login y Ahora; `:focus-visible`.
- **i18n ES/EN:** landing, login, Ahora.

## E11.2 (2026-07-31)

- **i18n ampliado:** sidebar, registro, informes (`nav.*`, `registro.*`, `informes.*`).
- **Lighthouse CI:** job `lighthouse-spati-a11y` en [`.github/workflows/ci.yml`](../../.github/workflows/ci.yml) — categoría **accessibility ≥ 0.9** en `/login`.
- Config: [`frontend/spati/lighthouserc.json`](../../frontend/spati/lighthouserc.json)
- Local: `cd frontend/spati && npm run lhci`

## Verificar

```powershell
cd frontend/spati
npm run build
npm run lhci
```

SPA: https://metgo-spati.pages.dev — ES/EN en `/`, `/login`, `/registro`, shell autenticado.

## Pendiente (E11 resto / E12)

- Ampliar i18n a umbrales / ambiente / ops (opcional)
- E12 datos oficiales + ML dominio

## Fase

**E11.2** · calidad clase mundial II
