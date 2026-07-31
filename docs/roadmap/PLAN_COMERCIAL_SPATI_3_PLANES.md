# Catálogo comercial SPATI — 3 planes + Enterprise de alto valor

> **Fuente de verdad comercial** · METGO 3D SpA · Julio 2026  
> Precios **sin IVA** · Piloto 15 días $0 · Sin tarifa mínima por informe  
> Relacionado: [`PLAN_UX_SPATI_LANDING_AHORA.md`](PLAN_UX_SPATI_LANDING_AHORA.md) · `plans_catalog.py` · plantillas en `docs/comercial/spati/`

---

## 1. Posicionamiento de los 3 planes

| | **Básico** | **Pro** | **Enterprise** |
|--|------------|---------|----------------|
| **Código API** | `starter` | `pro` | `enterprise` |
| **Precio** | **$300.000**/mes | **$500.000**/mes | **Desde $1.200.000**/mes (a medida) |
| **Para quién** | 1 faena, pocas grúas, empezar | Flota operativa, alertas 24/7, ROI mensual | Corporativo multi-faena, API, SLA, legal |
| **Promesa** | Decidir izaje con datos en el punto GPS | Operar la flota con alertas + reporte mensual | Integrar SPATI al sistema de la empresa |

**Regla:** no existe plan “$6.000 por informe” ni “$120.000 Pro”. Esos valores quedan **obsoletos**.

---

## 2. Matriz de valor (qué incluye cada uno)

### 2.1 Pronóstico e izaje

| Capacidad | Básico | Pro | Enterprise |
|-----------|:------:|:---:|:----------:|
| Vista **Ahora** (móvil tipo Windy) | ✅ | ✅ | ✅ |
| Pronóstico 72 h / actualización ~3 h | ✅ | ✅ | ✅ |
| Panel experto 72 h (detalle) | ✅ | ✅ | ✅ |
| Umbrales 26 / 31 / 36 km/h | Fijos (defaults) | Editables | Editables + por faena/grúa |
| PDF por operación (respaldo) | ✅ | ✅ | ✅ + metadatos legales reforzados |
| Ambiente / aire / nieve (paquete) | Lectura | Lectura | Lectura + priorización ops |
| Calibración dron | — | ✅ | ✅ + multi-sitio |

### 2.2 Escala operacional

| Capacidad | Básico | Pro | Enterprise |
|-----------|--------|-----|------------|
| Faenas | **1** | Hasta **3** (misma zona/contrato) | **Ilimitadas** (`multi_faena`) |
| Grúas / puntos GPS | Hasta **2** | Hasta **5** | **Ilimitadas** |
| Usuarios (seats) | **3** | **10** | **Ilimitados** (+ SSO a convenir) |
| Destinatarios alerta | **2** (email) | **5** (email + WhatsApp) | Ilimitados + roles |
| Board ops `/ops` | — | — | ✅ |

### 2.3 Alertas y canales

| Capacidad | Básico | Pro | Enterprise |
|-----------|:------:|:---:|:----------:|
| Email | ✅ | ✅ | ✅ |
| WhatsApp | — | ✅ | ✅ |
| SMS (zonas sin datos) | — | Opcional | ✅ incluido |
| Latencia alerta | &lt; 5 min | &lt; 5 min | &lt; 5 min + escalamiento 24/7 |
| Anticipación mínima | 18 h | 18 h (configurable) | Configurable por faena |

### 2.4 Documentos y reporting (los HTML del cliente)

| Entregable | Básico | Pro | Enterprise |
|------------|:------:|:---:|:----------:|
| Informe PDF operación | ✅ | ✅ | ✅ certificado |
| **Reporte mensual ROI** (plantilla) | — | ✅ 1/mes | ✅ + personalizado / white-label |
| **Datasheet técnico** (adjunto venta) | PDF estático | PDF estático | + anexo SLA firmado |
| **Propuesta comercial** editable | — | Plantilla | Plantilla + account manager |
| **Kit alianza / canal** | — | — | ✅ (partners inspección) |

### 2.5 Integración y soporte (diferencia Enterprise)

| Capacidad | Básico | Pro | Enterprise |
|-----------|:------:|:---:|:----------:|
| API REST + OpenAPI | — | Lectura limitada (consulta) | ✅ completa + webhooks |
| Integración ERP / SAP | — | — | ✅ proyecto incluido (hasta N días) |
| SLA uptime | Best effort | 99% | **99.5%** contractual |
| Soporte | Email (horario hábil) | Email + WA prioritario | **24/7** + teléfono |
| Account manager | — | — | ✅ dedicado |
| Onboarding | Self-serve + video | Zoom 30–60 min | Capacitaciones + runbook |
| Alta montaña &gt;3000 msnm | Consultar | Consultar | ✅ evaluación incluida |
| Ambiente de prueba / sandbox API | — | — | ✅ |
| Informes white-label (logo cliente) | — | — | ✅ |
| Auditoría / export compliance | — | CSV básico | Pack compliance (CSV+PDF+log) |

---

## 3. Paquete Enterprise (detalle de alto valor)

Enterprise no es “Pro más caro”: es **plataforma corporativa**.

### Incluye (mínimo contractual “desde $1.200.000”)
1. Multi-faena ilimitada + board `/ops`.
2. API REST, webhooks de alerta, credenciales por ambiente (prod/sandbox).
3. Hasta **5 días-hombre** de integración ERP/SAP o conector Excel/Power BI (extra con cotización).
4. SLA 99.5% con créditos de servicio.
5. Account manager + canal 24/7.
6. **Reporte mensual ejecutivo** (KPIs, alertas, ROI) — plantilla `reporte-mensual.html`.
7. Informes PDF con firma digital y pack legal (SUSESO / mutualidades).
8. Configuración de umbrales y destinos **por faena y por grúa**.
9. Opción **alianza/canal** (comisiones) si el cliente es certificador/inspección.
10. Revisión trimestral de exactitud del modelo en sus coordenadas.

### Add-ons Enterprise (cotizan aparte)
| Add-on | Descripción | Precio ref. |
|--------|-------------|-------------|
| Días-hombre extra integración | Más allá del pack incluido | UF / día |
| White-label completo (dominio propio) | Branding SPA | Desde $400.000 setup |
| Sensor / IoT anemómetro | Assimilación observado | Cotización |
| Capacitaciones in-company | Media jornada | Desde $250.000 |
| Informe pericial / caso legal | Bajo demanda | Cotización |

### Argumento de venta Enterprise
> “No solo le avisamos del viento: dejamos SPATI dentro de su operación (API, flotas, legal y ROI medible cada mes).”

---

## 4. Copy de precios para landing / propuesta

```text
BÁSICO · $300.000 / mes
1 faena · hasta 2 grúas · Ahora + 72h · PDF · email
Ideal para empezar sin fricción.

PRO · $500.000 / mes  ← más popular
Hasta 3 faenas / 5 grúas · WhatsApp · umbrales editables · reporte mensual ROI
Ideal para jefes de operaciones con flota activa.

ENTERPRISE · desde $1.200.000 / mes
Multi-faena · API · SLA 99.5% · AM 24/7 · integración ERP · pack legal
Ideal para mandantes, EPC y empresas con varias faenas.
```

Piloto: **15 días gratis** (equivalente trial), sin tarjeta.

---

## 5. Documentos comerciales (uso de los HTML)

| Documento | Archivo | Quién lo usa | Qué actualizar |
|-----------|---------|--------------|----------------|
| Propuesta comercial | `docs/comercial/spati/propuesta-comercial.html` | Venta 1:1 | Planes 300k / 500k / desde 1.2M + matriz |
| Reporte mensual | `docs/comercial/spati/reporte-mensual.html` | Entregable Pro+ | Costo plan en ROI = 500k o Enterprise |
| Datasheet técnico | `docs/comercial/spati/datasheet-tecnico.html` | Preventa / IT | Canales por plan |
| Propuesta alianza | `docs/comercial/spati/propuesta-alianza.html` | Partners | Comisiones sobre 300k/500k/Ent |

### Comisiones alianza (sobre facturación neta mensual)
| Plan referido | Comisión aliado |
|---------------|-----------------|
| Básico | **15%** recurrente |
| Pro | **20%** recurrente |
| Enterprise | **≥15%** (caso a caso) |

---

## 6. Mapeo a producto (código)

| Feature key | Básico | Pro | Enterprise | UI / API |
|-------------|:------:|:---:|:----------:|----------|
| `panel` / `ahora` | ✅ | ✅ | ✅ | `/ahora`, `/` |
| `ambiente` | ✅ | ✅ | ✅ | Ambiente |
| `dron` | — | ✅ | ✅ | Dron |
| `umbrales` | — | ✅ | ✅ | Umbrales |
| `alertas` | email | email+WA | +SMS+escala | M9 |
| `reporte_mensual` | — | ✅ | ✅ | Nuevo endpoint F4 |
| `multi_faena` | — | limitado* | ✅ | Hub / ops |
| `api` | — | — | ✅ | OpenAPI keys |
| `sla` | — | — | ✅ | Contrato |

\*Pro: hasta 3 faenas vía reglas de org, no catálogo mundial.

---

## 7. ROI (actualizar números en plantillas)

Supuestos de venta (ajustar por cliente):

| Concepto | Valor ref. |
|----------|------------|
| Hora grúa detenida | $180.000 – $400.000 |
| Costo Pro | $500.000 (+ IVA si aplica) |
| Costo Enterprise desde | $1.200.000 |
| 1–2 incidentes evitados / mes | Ahorro $180k – $800k+ |

Con Pro a $500k, el pitch ROI sigue siendo: **1 hora evitada puede pagar el plan**.

---

## 8. Próximos pasos de implementación

1. Actualizar `plans_catalog.py` (precios + features + límites + textos).
2. Landing + propuesta HTML con los 3 precios.
3. Pestaña **Ahora** (plan UX).
4. (Pro/Ent) Generador de **reporte mensual** desde datos reales (alertas M9 + ops).

## Fase

**Comercial SPATI 3 planes** · producto 2.x · Enterprise alto valor.
