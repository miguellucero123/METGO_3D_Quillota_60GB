# Plan UX SPATI — Landing comercial + app móvil de izaje

> **Objetivo:** que un prospecto/cliente vea primero **características y valor** (landing), entre sin ser empujado a una mina concreta ni a un catálogo de 17 minas, y dentro de la app tenga **Ahora** (móvil) + **Informes** + sesión única.  
> **Precios:** Básico $300.000 · Pro $500.000 · Enterprise desde $1.200.000 /mes.  
> **Estado:** flujo unificado A–C implementado · 2026-07-30

Relacionado: [`PLAN_COMERCIAL_SPATI_3_PLANES.md`](PLAN_COMERCIAL_SPATI_3_PLANES.md) · `docs/comercial/spati/` · `FaenasHubView` · `AhoraView` · `InformesView` · `session_store.py`

---

## 1. Flujo real (implementado)

```text
PÚBLICO
  /                 → Landing comercial (CTA Ingresar → /login · Piloto → /registro)
  /login            → Login genérico (código de faena opcional; navy/emerald)
  /registro         → Registro + código de faena si no hay deep-link
  /f/:faena/login|registro  → deep-links campañas WordPress (se mantienen)

AUTENTICADO
  1 faena           → /f/{slug}/ahora
  N faenas          → /app («Mis faenas»; solo membresías)
  Admin             → /app con badge «Admin · catálogo completo» (17 faenas conscientes)
  /f/:faena/ahora   → decisión de izaje (mapa + timeline)
  /f/:faena/informes → PDF/CSV/HTML operación + reporte mensual (Pro+)
  /f/:faena/        → Panel técnico 72 h
```

### Reglas
1. Cliente normal: **nunca** lista de 17 minas.
2. Entrada a faena solo con membresía / código / deep-link.
3. Un solo JWT activo por usuario (`jti`); login nuevo → 401 `session_replaced` en el anterior.
4. Informes visibles en sidebar.

---

## 2. Checklist entrega A–C

### A — Accesos
- [x] Landing CTAs → `/login` y `/registro` (sin Quebrada Blanca forzada en URL).
- [x] Rutas top-level `/login` · `/registro`.
- [x] Post-login: `mis-faenas` → 1 → `/ahora`, N → `/app`.
- [x] Hub «Mis faenas» + badge Admin si `catalogo_completo`.

### B — Sesión única
- [x] Claim `jti` en `crear_token_*` + `session_store`.
- [x] `auth_required` → 401 `session_replaced`.
- [x] SPA: logout + mensaje «Sesión iniciada en otro dispositivo».
- [x] Test `test_sesion_unica_invalida_token_anterior` · OpenAPI documentado.

### C — Informes
- [x] Ruta `/f/:faena/informes` + sidebar **Informes**.
- [x] PDF / CSV / HTML operación (`urlInformeFaena`).
- [x] Reporte mensual HTML `GET /api/public/spati/{id}/reporte-mensual` (Pro+ en UI).
- [x] Enlace corto desde Ahora.

---

## 3. Problema histórico (diagnóstico)

| Qué pasaba | Por qué |
|------------|---------|
| `/` no era landing | Era hub de faenas |
| Login mandaba a Escondida / QB | Redirects hardcodeados |
| Admin veía 17 minas sin etiqueta | `catalogo_completo` sin copy Admin |
| Sin pestaña Informes | PDF solo en Ambiente |
| Multi-dispositivo concurrente | JWT sin `jti` |

---

## 4. Pestaña **Ahora** (móvil tipo Windy)

Implementado: badge nivel, mapa Leaflet, timeline, barras/tabla coloreada, link a Informes y panel 72 h.

Sidebar: **Ahora** · **Informes** · Pronóstico 72 h · Ambiente · Dron · Umbrales · Cuenta.

---

## 5. Precios (catálogo)

| Plan | Precio |
|------|--------|
| Piloto | $0 · 15 días |
| Básico (`starter`) | $300.000 CLP/mes |
| Pro | $500.000 CLP/mes |
| Enterprise | Desde $1.200.000 CLP/mes |

Detalle: [`PLAN_COMERCIAL_SPATI_3_PLANES.md`](PLAN_COMERCIAL_SPATI_3_PLANES.md).

---

## 6. Criterios de aceptación

1. Anónimo en `/` → Ingresar → `/login` (no mina forzada).
2. Usuario 1 faena → `/f/{slug}/ahora` sin catálogo 17.
3. Admin ve catálogo con etiqueta clara.
4. Sidebar **Informes** descarga PDF; Pro+ ve reporte mensual.
5. Segundo login misma cuenta invalida el primero (401 + mensaje en login).

## Fase documento

**UX-SPATI / A–C** · producto 2.x · F1–F3 + Informes + sesión única.
