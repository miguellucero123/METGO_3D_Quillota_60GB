# DT-3 — Error handling Vue (`useApiCall`)

**Estado:** Cerrado · **Prioridad:** media

## Objetivo

Migrar vistas Vue restantes al composable `useApiCall` (loading / error / run unificados) en lugar de `try/catch` ad-hoc.

## Criterio de cierre

- [x] Vistas críticas (Dashboard, Meteo, Histórico, Comparativo, Métricas, Alertas) usan `useApiCall` o patrón equivalente
- [x] Mensajes de error visibles al usuario (sin `console.error` solo)
- [ ] Documentar patrón en `frontend/vue/README` o AGENTS

## Notas

Ya usado en `MetricasGlobalesView` y otras. Completar el resto de forma incremental.
No bloquea E0–E5 de integración Quillota–Paine.
