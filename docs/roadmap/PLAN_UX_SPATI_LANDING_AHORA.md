# Plan UX SPATI — Landing comercial + app móvil de izaje

> **Objetivo:** que un prospecto/cliente vea primero **características y valor** (landing), entre sin ser empujado a Escondida ni a un catálogo de 17 minas, y dentro de la app tenga una **pestaña simple tipo Windy** (móvil primero) con lo crítico del izaje.  
> **Precios:** sin tarifa mínima por informe · **Básico $300.000**/mes · **Pro $500.000**/mes · **Enterprise desde $1.200.000**/mes (a medida).  
> **Estado:** catálogo API + pestaña Ahora + **landing `/`** · hub en `/app` · 2026-07-30

Relacionado: [`PLAN_COMERCIAL_SPATI_3_PLANES.md`](PLAN_COMERCIAL_SPATI_3_PLANES.md) · `docs/comercial/spati/` · `FaenasHubView` · `SpatiPanelView` · `plans_catalog.py`

---

## 1. Problema actual (diagnóstico)

| Qué pasa hoy | Por qué |
|--------------|---------|
| `/` no es landing de producto | Es hub de faenas / código de mina |
| Login manda a Escondida | Redirects hardcodeados `/login` → `/f/escondida/login` |
| Tras login con 1 faena → panel denso | `FaenasHubView` hace `replace(/f/{slug}/)` al panel completo |
| Admin / multi ve “todas las mineras” al final | `catalogo_completo` lista el catálogo comercial |
| Panel 72 h es potente pero **no móvil-first** | `SpatiPanelView` es dashboard de escritorio (charts pesados) |
| Precios en API (antes 149k/399k) | Actualizado: 300k / 500k / desde 1.2M — ver catálogo comercial |

El HTML que enviaste es el **tono correcto** para marketing (hero, wind widget, alertas, planes, FAQ). No debe mezclarse con la app operativa.

---

## 2. Arquitectura de pantallas (propuesta)

```text
PÚBLICO (sin JWT)
  /                 → Landing comercial SPATI (características, precios, CTA)
  /login            → Login genérico (sitio=spati; faena se resuelve después)
  /registro         → Registro (faena opcional o código de faena contratada)
  /f/:faena/login   → sigue existiendo (deep-link por mina / WordPress)

AUTENTICADO
  /app              → Shell post-login: “Mis faenas” (solo las contratadas)
  /f/:faena/ahora   → NUEVA pestaña: vista móvil tipo Windy (default al entrar)
  /f/:faena/        → Panel experto 72 h (detalle actual, desktop)
  /f/:faena/ambiente|dron|umbrales|cuenta  → igual que hoy (entitlements)
  /ops              → Board multi-faena (solo admin / multi_faena)
```

### Regla de oro
- **Landing** = marketing (público).
- **App** = operativa (JWT). Nunca listar las 17 minas a un cliente normal.
- Al entrar a una faena, abrir **`/ahora`** (simple), no el panel denso.

---

## 3. Flujos de usuario

### 3.1 Prospecto (sin cuenta)
1. Entra a `metgo-spati.pages.dev/` → **Landing** (hero + wind widget + cómo funciona + alertas + precios + FAQ).
2. CTA → `/registro` o `mailto` / “Piloto 15 días”.
3. Tras registro + verify → `/app` (sus faenas; si 1 → `/f/{faena}/ahora`).

### 3.2 Cliente con 1 faena (caso típico)
1. Login en `/login` (sin “elige industria”).
2. Sistema lee `mis-faenas` → 1 slug → **redirige a `/f/{slug}/ahora`**.
3. Sidebar: **Ahora** (default) · Pronóstico 72 h · Ambiente · … según plan.
4. No ve catálogo de otras minas.

### 3.3 Admin / Enterprise multi_faena
1. Login → `/app` con lista de faenas contratadas (o catálogo si admin).
2. Elige faena → `/f/{id}/ahora`.
3. Link opcional a `/ops` (board).

### 3.4 Deep-link WordPress
`/f/escondida/registro` y `/f/escondida/login` se mantienen para campañas por mina.

---

## 4. Landing comercial (`/`)

### Contenido (del HTML del cliente, adaptado a Vue)
1. Nav: Cómo funciona · Alertas · Precios · FAQ · **Ingresar** · Demo.
2. Hero: “El viento no avisa. SPATI sí.” + CTAs.
3. **Wind widget** animado (firma visual; datos demo o live de una faena demo pública).
4. Stats (72 h, 18+ h, exactitud, &lt;5 min).
5. Pasos 1–5.
6. Umbrales 26 / 31 / 36 km/h (configurables; copy comercial).
7. **Precios nuevos** (ver §6).
8. FAQ (Windy vs SPATI, alta montaña, PDF, piloto).
9. CTA + footer METGO 3D SpA.

### Técnico
- Nueva vista `LandingSpatiView.vue` (tema navy/emerald del mock; **público** `meta.public`).
- Quitar LinkedIn switcher del producto (ese HTML es herramienta de marketing interna; opcional en `docs/` o página aparte no enlazada).
- `FaenasHubView` pasa a ruta `/app` (autenticado) o se refactoriza.

### Qué NO poner en el landing
- Selector “¿a qué industria vas?”.
- Lista de 17 mineras.
- Entrada automática a Escondida.

---

## 5. Pestaña **Ahora** (móvil tipo Windy)

### Objetivo
Una sola pantalla, usable con el pulgar, con la **decisión de izaje** en &lt; 3 segundos.

### Layout móvil (primera viewport)
```text
┌─────────────────────────┐
│ Escondida · Ahora  07:20│
│ ● NARANJA  31–35 km/h   │  ← nivel + umbral
│ Rafaga actual  XX km/h  │
│ Pico +18h    YY km/h    │
│ Dir NNO · Vis · Nieve   │
├─────────────────────────┤
│ [Gráfico viento 72h]    │  ← serie simplificada (SVG/ECharts lite)
│ ──26── ──31── ──36──    │  ← umbrales
├─────────────────────────┤
│ Recomendación           │
│ “Postergar izaje 09:00” │
├─────────────────────────┤
│ [PDF] [72h detalle]     │
└─────────────────────────┘
```

### Datos (reutilizar API existente)
| Bloque UI | Fuente |
|-----------|--------|
| Nivel / badge | `GET /public/spati/{id}/pronostico` → `nivel_maximo` / serie |
| Actual / pico / dir | mismos campos del panel |
| Umbrales | `GET …/umbrales` |
| PDF | enlace informe ya existente |
| Aviso degradado | `aviso` / NWP si aplica |

### Render móvil
- Ruta default post-login: `/f/:faena/ahora`.
- CSS mobile-first; en desktop puede ser columna estrecha centrada o split (widget + detalle).
- El panel actual (`SpatiPanelView`) queda como pestaña **“72 h” / “Detalle”** (experto).
- Entitlement: misma feature `panel` (router trata `ahora` como `panel`).

### Layout implementado (estilo Windy simplificado)
1. Badge nivel + recomendación de izaje  
2. **Mapa** Leaflet (tiles oscuros) + pill de viento/dirección  
3. **Timeline** de horas (slider)  
4. **Gráfico de barras** 72 h coloreado verde / amarillo / naranja / rojo  
5. **Tabla** viento · ráfaga · dirección por hora (celdas coloreadas)

### Nombre en sidebar
- **Ahora** (mapa) — primero en la lista · ruta `/f/:faena/ahora`
- **Pronóstico 72 h** — panel experto
- Resto igual (Ambiente, Dron, Umbrales, Cuenta).

**Estado F3:** implementado en código SPA (pendiente deploy Pages).
---

## 6. Precios (catálogo)

### Oferta comercial (landing + API)

| Plan | Precio | Notas |
|------|--------|--------|
| Piloto / trial | $0 · 15 días | Sin tarjeta; sin “mínimo por informe” |
| **Básico** (`starter`) | **$300.000** CLP/mes | 1 faena · 2 grúas · email |
| **Pro** | **$500.000** CLP/mes | Hasta 3 faenas · WA · reporte mensual |
| **Enterprise** | **Desde $1.200.000** CLP/mes | Multi-faena · API · SLA 99.5% · AM 24/7 |

Detalle de features / entregables: [`PLAN_COMERCIAL_SPATI_3_PLANES.md`](PLAN_COMERCIAL_SPATI_3_PLANES.md).

### Cambios de código
1. ~~`plans_catalog.py` → 300_000 / 500_000 / desde 1_200_000~~ (hecho).
2. Landing y `CuentaView` leen `GET /api/public/planes?sitio=spati` (una sola fuente de verdad).
3. Quitar del copy cualquier “desde $X por informe” / valor mínimo.
4. Stripe Price IDs (cuando existan) deben alinearse a 300k / 500k / Enterprise custom.

### Confirmación pendiente contigo
- ¿IVA: mostrar “+ IVA” en landing? (API: `iva: no_incluido`)

---

## 7. Cambios de router / redirects (críticos)

| Hoy | Nuevo |
|-----|--------|
| `/` = hub faenas | `/` = Landing |
| `/login` → Escondida | `/login` = LoginView sin faena fija |
| 1 faena → `/f/x/` panel | 1 faena → `/f/x/ahora` |
| Redirects `/dron` etc. → escondida | → `/login?redirect=…` o última faena en localStorage |

---

## 8. Fases de implementación

### F0 — Alineación (1 día, sin código)
- [ ] Confirmar precios 300k / 500k (roles Básico/Pro).
- [ ] Confirmar copy legal del PDF / SUSESO (del HTML).
- [ ] Decidir si wind widget del landing usa **demo estático** o faena pública demo.

### F1 — Landing + precios (2–3 días) ← **prioridad comercial**
- [ ] `LandingSpatiView.vue` + estilos del mock.
- [ ] Router: `/` público landing; hub → `/app`.
- [ ] Actualizar `plans_catalog.py` (300k / 500k).
- [ ] CTAs Ingresar / Registro / Demo.
- [ ] Deploy Pages.

### F2 — Entrada sin Escondida (1 día)
- [ ] Login/registro globales.
- [ ] Quitar auto-jump a panel denso; ir a `/ahora`.
- [ ] Hub `/app` solo faenas de membresía (admin: catálogo consciente, no “sorpresa”).

### F3 — Pestaña **Ahora** móvil (3–4 días)
- [ ] `AhoraIzajeView.vue` (mobile-first).
- [ ] Gráfico simplificado + badges + recomendación.
- [ ] Sidebar + entitlement.
- [ ] Tests smoke + QA en viewport 390px.

### F4 — Pulido demo cliente (1–2 días)
- [ ] Copy landing = HTML cliente (precios nuevos).
- [ ] PDF CTA desde Ahora.
- [ ] Checklist aceptación con el interesado.

**Total estimado:** ~1.5–2 semanas a ritmo parcial.

---

## 9. Archivos a tocar (F1–F3)

| Archivo | Cambio |
|---------|--------|
| `frontend/spati/src/views/LandingSpatiView.vue` | **nuevo** landing |
| `frontend/spati/src/views/AhoraIzajeView.vue` | **nuevo** móvil |
| `frontend/spati/src/views/FaenasHubView.vue` | mover a `/app`, sin redirect agresivo |
| `frontend/spati/src/router/index.js` | rutas + defaults |
| `frontend/spati/src/components/layout/AppSidebar.vue` | ítem Ahora primero |
| `frontend/spati/src/services/spatiApi.js` | sin cambio mayor (reusa pronóstico) |
| `backend/.../identity/plans_catalog.py` | 300k / 500k |
| `docs/roadmap/PLAN_REGISTRO…` + OpenAPI planes | documentar precios |
| `tests/test_identity_s1.py` | precios / rutas si aplica |

---

## 10. Criterios de aceptación (demo al interesado)

1. Anónimo en `/` ve landing con características y precios **300k / 500k** (sin $6.000).
2. “Ingresar” no pregunta industria ni abre Escondida a ciegas.
3. Usuario de 1 faena cae en **`/ahora`**: nivel, ráfaga, gráfico, recomendación, usable en celular.
4. “72 h” sigue disponible con el detalle actual.
5. Cliente normal **no** ve las 17 minas.
6. Admin puede ver multi-faena / `/ops` sin romper el flujo del cliente.

---

## 11. Fuera de alcance de este plan

- Ops P0 Render/SMTP/Stripe (sigue en `GUIA_ARRANQUE_OPS_P0.md`).
- Posts LinkedIn (herramienta aparte, no en la SPA de producción).
- Reescribir el motor NWP (solo presentación).

---

## Decisión que necesito de ti para empezar a codear

1. **$500.000** = ¿plan **Pro**? (Básico 300k / Pro 500k)
2. ¿Empezamos por **F1 Landing + precios** esta semana (recomendado para el interesado)?
3. Wind widget del landing: ¿**demo estático** (como el HTML) o datos live de una faena?

## Fase documento

**UX-SPATI / F0–F4** · producto 2.x · priorizar F1 comercial.
