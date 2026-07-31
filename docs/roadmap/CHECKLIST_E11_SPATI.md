# E11.1 — Calidad SPA VENTORA (PWA / a11y / i18n)

Slice 1 entregado 2026-07-31 en `frontend/spati/`.

## Hecho

- **PWA activa** (`vite-plugin-pwa`, sin `selfDestroying`): manifest VENTORA + workbox `NetworkFirst` para `/api/`.
- **a11y:** skip-link en shell público y autenticado; `<main>` en login/landing; labels/ARIA en login y Ahora; `:focus-visible` ya en `main.css`.
- **i18n ES/EN:** landing, login y Ahora (`src/i18n/locales/*.json` + toggle en landing/login).

## Verificar

```powershell
cd frontend/spati
npm run build
# Dist debe incluir manifest.webmanifest y sw / workbox
```

SPA: https://metgo-spati.pages.dev — instalar PWA; cambiar ES/EN en `/` y `/login`.

## Pendiente (E11 resto)

- Lighthouse CI ≥90 (a11y/performance) en pipeline
- Ampliar i18n a sidebar / informes / registro completo

## Fase

**E11.1** · calidad clase mundial II
