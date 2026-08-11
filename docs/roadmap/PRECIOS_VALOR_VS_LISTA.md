# Precios METGO — valor del sistema vs lista (USD/mes)

> Corte: 2026-08-11 · Moneda de lista: **USD** sin IVA · Piloto 15 días $0  
> Código: `plans_catalog.py` · Landing hub: `PlanesView.vue`

## 1. Método

1. **Valor techo** = lo que el cliente *evitaría pagar* o *dejaría de perder* si usa todo el stack (dashboard + alertas + pronóstico + PDF + identity + ETL + ML + soporte).  
2. **Precio de lista** = **25–40 % del techo** (entrada accesible, margen para descuento anual / piloto).  
3. **Enterprise** = cotización; el número “desde” es ancla, no techo.

Regla: **no cobramos el valor completo** del sistema; cobramos una fracción para cerrar piloto y expandir seats/faenas.

---

## 2. Valor techo por servicio (referencia interna)

| Bloque de servicio | Valor techo aprox. USD/mes | Quién lo paga mentalmente |
|--------------------|----------------------------|---------------------------|
| Panel + API + identity multi-usuario | 150–300 | IT / ops |
| Pronóstico 72 h calibrado al punto | 100–250 | ops / agrónomo |
| Alertas email/WA/SMS + umbrales | 80–200 | HSEQ / turno |
| PDF / informe / respaldo legal | 50–150 | mandante / fiscalización |
| ETL + datos oficiales / aire | 100–200 | calidad / medioambiente |
| ML (helada, PM10, etc.) | 80–200 | planificación |
| Ops board multi-faena + SLA | 200–500 | gerencia |
| Dron / calibración / perfil viento | 150–400 | izaje |

**Suma “todo el stack” si se cobrara por piezas:** ~USD **900–2.200**/mes según vertical.

---

## 3. Por plataforma: techo → lista (más baja)

| Plataforma | Qué vende el sistema | Valor techo (todo) | Lista piloto (entrada / medio / enterprise desde) | % del techo (entrada) |
|------------|----------------------|--------------------|---------------------------------------------------|------------------------|
| **SPATI / VENTORA** | Izaje + Ahora + PDF + alertas + umbrales + (Pro) dron/ROI + (Ent) /ops | **1.800–3.000** | **299 / 499 / 1.199** | ~15–17 % |
| **Mantos Blancos** | Semáforo turno + ventanas + ambiente + aire | **1.200–2.200** | **249 / 449 / 999** | ~18–20 % |
| **Copiapó (aire)** | ICAP + pronóstico + dispersión + ops Paipote | **900–1.800** | **199 / 399 / 799** | ~18–22 % |
| **Quillota / agro** | Helada + riego + meteo + alertas + ML ligero | **400–800** | **99 / 179 / 399** | ~20–25 % |
| **Paine** (outdoor) | Meteo terreno / Carretera Austral | **200–500** | **49 / 99 / 249** | ~20–25 % |

### Lectura comercial

- **SPATI 299/499** es realista: el techo es alto (riesgo grúa); la lista queda **muy por debajo** del valor.  
- **Agro a 990** (landing antigua) estaba **por encima** del techo agro → se corrige a **99/179**.  
- **Municipio / aire:** preferir “desde 399–799” o cotización; no anclar 600 fijo si el comprador es público.

---

## 4. Landing hub Quillota (3 anclas)

Alinear marketing con techos:

| Ancla | Antes | Ahora (lista) | Mensaje |
|-------|-------|---------------|---------|
| Plan Campo (agro) | 990 | **desde 99** | Fundo / zona |
| Plan Faena (minería) | 1.800 | **desde 299** | Entra a SPATI Básico |
| Plan Municipio (aire) | 600 | **desde 399** | Cotización formal |

---

## 5. Descuentos sugeridos (sobre lista)

| Condición | Descuento |
|-----------|-----------|
| Contrato 12 meses prepago | 15 % |
| 2+ faenas mismo contrato | 10 % |
| Piloto → conversión &lt;30 días | 1er mes 50 % |
| Sector público / Mercado Público | Solo cotización (no self-serve) |

---

## 6. Qué no hacer

- No usar el mismo precio en agro y minería.  
- No publicar el **techo** al cliente (es interno).  
- No subir lista hasta demostrar ROI en 3–5 cuentas piloto.

## Fase

**Comercial 2.x** · lista = fracción del valor del stack · catálogo por `sitio` en API.
