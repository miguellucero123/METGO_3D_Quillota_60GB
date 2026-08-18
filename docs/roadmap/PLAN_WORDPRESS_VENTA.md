# Plan completo — venta en WordPress + innovaciones visibles

> Corte: 2026-08-11 · Contacto comercial: **miguel.lucero@metgo3d.com**  
> Relacionado: [`PRECIOS_VALOR_VS_LISTA.md`](PRECIOS_VALOR_VS_LISTA.md) · [`CATALOGO_INNOVACIONES_VENDIBLES.md`](CATALOGO_INNOVACIONES_VENDIBLES.md)

---

## 0. ¿Puede Cursor editar WordPress desde aquí?

**Sí, vía REST** con Application Password (local: `WP_USER` / `WP_APP_PASSWORD` en `.env`, nunca en git). Script: `scripts/wp_rest.py`.

| Qué sí se puede hacer aquí | Qué sigue en panel WP |
|----------------------------|------------------------|
| Crear/editar/papelera páginas y posts | Menús visuales / bloques Cover finos |
| Textos de venta + innovaciones | Widgets / footer del theme |
| Enlaces a `*.pages.dev` en contenido | Diseño fino Gutenberg si hace falta |

**Hecho 2026-08-11 (REST):**
- post `hello-world` (id 2) y página **CV** (id 206) → papelera  
- Portada = página Inicio (211); ya no muestra posts  
- Home venta v3 (hero + 3 columnas + precios + demo)  
- Páginas nuevas: `/planes/` (351), `/innovaciones/` (352), `/contacto/` (353)  
- Navegación 203: menú fijo (sin `page-list`)  
- Script: `scripts/wp_apply_venta.py`

**Hecho 2026-08-11 (REST comercial v5):**
- Header sin “En creación” / Turismo / MJO / links rotos; menú Productos + precios  
- Footer con giro canónico, productos activos, sin GitHub personal ni WIP  
- Signup/CTA oscuros (sin Netlify / fondo claro CoachBen)  
- Home v5 con 4 productos + planes ancla + VENTORA destacado  
- Página nueva `/izaje-ventora/` (374)  
- Banners comerciales en Agricultura (204) y Minería/Aire (213)  
- Script: `scripts/wp_apply_comercial_v5.py`

---

## 1. Objetivo (30 días)

Visitante en `metgo3d.com` → entiende el valor en 5 s → ve **precio o “desde USD”** → pide demo → mail a **miguel.lucero@metgo3d.com** → piloto en Pages → cobro.

---

## 2. Checklist WordPress (día a día)

### Día 1 — Higiene (30–45 min)

| # | Acción | Dónde en WP |
|---|--------|-------------|
| 1 | Mover a papelera el post **Hello World** | Entradas → Hello World → Papelera |
| 2 | Quitar **CV** del menú principal | Apariencia → Menús |
| 3 | Quitar del menú todo “en creación / en desarrollo” | Menús |
| 4 | Sustituir enlaces Netlify por Pages | Menús / botones |
| 5 | Un solo email visible: `miguel.lucero@metgo3d.com` | Widgets / Contacto / footer |

**URLs canónicas de producto (no mezclar):**

- Agricultura: https://metgo-quillota.pages.dev  
- Izaje / VENTORA: https://metgo-spati.pages.dev  
- Aire Copiapó: https://metgo-copiapo.pages.dev  
- Mantos: https://metgo-mantos.pages.dev  
- Paine: https://metgo-paine.pages.dev  
- Planes Quillota: https://metgo-quillota.pages.dev/planes  
- Contacto: https://metgo-quillota.pages.dev/contacto  

### Día 2–3 — Home (hero + venta)

Bloque **Cover** fondo navy `#0f172a`, texto blanco.

**H1:** Evita pérdidas por clima en tu faena  

**Subtítulo:** Pronósticos hiperlocales y alertas para agricultura, minería e izaje en Chile. Si hay riesgo de helada o viento, te avisa a tiempo — no al día siguiente.  

**Botón primario:** Solicitar demo gratis → `/contacto/` (o mailto:`miguel.lucero@metgo3d.com`)  
**Botón secundario:** Ver panel en vivo → `https://metgo-quillota.pages.dev`  

**Eliminar de la home:** roadmap 2025–2026, módulos incompletos, widget “app del clima” como producto principal, footer duplicado.

**3 columnas (por qué METGO):**

1. **Agricultura** — Una helada mal anticipada puede costar la temporada. Alerta 12–24 h antes para tu zona, no solo la estación DMC más cercana.  
2. **Izaje / minería** — Una grúa o faena parada por viento cuesta miles de USD/hora. Semáforo horario para programar con margen.  
3. **Calidad del aire** — Cumplir DS 59 / DS 138 sin monitoreo continuo es operar a ciegas. Panel + informes para fiscalización.

### Día 3–4 — Página `/planes/`

Usar precios de lista (no el techo):

| Plan | Desde | CTA |
|------|-------|-----|
| Campo (agro) | **USD 99**/mes | Solicitar acceso → contacto |
| Faena (izaje/minería) | **USD 299**/mes | Demo faena → spati + contacto |
| Municipio (aire) | **USD 399**/mes | Cotización → contacto |

Texto garantía: *Primer piloto 15 días sin costo. Si no sirve para tu operación, no pagas.*

Detalle: [`PRECIOS_VALOR_VS_LISTA.md`](PRECIOS_VALOR_VS_LISTA.md).

### Día 4–5 — Menú + páginas por sector

Menú sugerido:

```
Inicio | Servicios ▾ | Innovaciones | Planes | Nosotros | Contacto
              Agricultura
              Izaje / VENTORA
              Minería
              Calidad del aire
```

- **Sin** CV, sin GitHub personal, sin “Hello World”.  
- Cada servicio: problema → qué incluye → link al panel Pages → CTA demo.  
- Página **Innovaciones** (nueva): pegar resumen de [`CATALOGO_INNOVACIONES_VENDIBLES.md`](CATALOGO_INNOVACIONES_VENDIBLES.md) — así se ve qué se puede **ampliar y vender**.

### Día 5–7 — Contacto + credibilidad

Formulario WP (o enlace a https://metgo-quillota.pages.dev/contacto):

- Nombre, empresa, sector, email, teléfono, mensaje  
- Notificación a **miguel.lucero@metgo3d.com**  

Nosotros: misión empresa + perfil corto fundador (no CV completo) + mail comercial.

Blog: 0 posts basura. Cuando haya 3 artículos útiles, relanzar.

---

## 3. Copy contacto (mailto rápido)

```
mailto:miguel.lucero@metgo3d.com?subject=Demo%20METGO%203D&body=Nombre%3A%0AEmpresa%3A%0ASector%20(agricultura%2Fminer%C3%ADa%2Fizaje%2Faire)%3A%0AFaena%20o%20zona%3A%0A
```

---

## 4. Por qué “no se ven” las innovaciones

Porque estaban como **módulos técnicos / demos / roadmap**, no como **SKU vendibles** con precio y CTA.

| Innovación (ya existe o casi) | Dónde vive hoy | Cómo venderla |
|-------------------------------|----------------|---------------|
| Semáforo izaje + umbrales | SPATI Pages | Plan Faena / Pro |
| ICAP + dispersión aire | Copiapó / Mantos | Plan Municipio / Faena |
| Helada + panel agro | Quillota | Plan Campo |
| Ops board multi-faena | SPATI `/ops` | Enterprise |
| Calibración dron | SPATI Pro+ | Add-on / Pro |
| Pronóstico extendido (MJO) | WP / investigación | Página comercial “tendencia 20–90 días” |
| Alertas WhatsApp | Código parcial | Activar conector → producto “Alertas” |
| API datos | API Flask | Tier freemium (después del 1er pago) |
| White-label municipio | Docs | Cotización anual |
| Digital Twin / seguro | Idea | Año 1–2, no home |

El catálogo comercial de innovaciones está en **`CATALOGO_INNOVACIONES_VENDIBLES.md`**.

---

## 5. Qué hace el monorepo en paralelo (Cursor sí puede)

1. Contacto SPA → email **miguel.lucero@metgo3d.com** + lead API.  
2. Hero Quillota con CTA a `/contacto`.  
3. Doc innovaciones + precios alineados.  
4. (Opcional) notificar por SMTP cada lead nuevo.

---

## 6. Lo que NO hacer en la home WP

- Mostrar “en creación”.  
- Precio techo ($1.800) como lista.  
- Digital Twin / seguro como si ya se vendiera.  
- CV o GitHub personal en menú.  
- 8 dominios distintos sin hub claro: en WP solo 1 CTA + links a Pages.

---

## Fase

**Ops comercial WP (humano)** + **Producto 2.x (código en Pages)** · primer lead a `miguel.lucero@metgo3d.com` en &lt;7 días.
