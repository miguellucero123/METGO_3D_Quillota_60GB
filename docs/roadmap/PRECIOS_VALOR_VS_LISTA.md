# Precios METGO — valor del sistema vs lista (USD/mes)

> Corte: **2026-08-31** · Moneda de lista: **USD** sin IVA · Piloto 15 días $0  
> Código: `plans_catalog.py` · Landing: `wp_apply_mg_page.py` + `PlanesView.vue`

## 1. Método (revisión early-adopter)

1. **Valor techo** = referencia interna (pérdida evitada / stack completo).  
2. **Precio de lista** = fracción **muy** baja del techo (~5–12 %) para **cerrar primeras conversaciones** mientras se validan costos reales (hosting, datos, personas).  
3. **Enterprise** = cotización; el “desde” es ancla, no techo.

Regla actual: **atraer piloto**, no maximizar margen en el paper. Subir lista solo tras 3–5 cuentas pagando.

---

## 2. Anclas landing (metgo3d.com/planes)

| Ancla | Antes | **Ahora** | ≈ CLP/mes (@950) |
|-------|-------|-----------|------------------|
| Campo (agro) | 99 | **39** | ~$37.000 |
| Faena (izaje) | 299 | **99** | ~$94.000 |
| Municipio (aire) | 399 | **149** | ~$141.000 |
| Ruta (outdoor) | 49 | **19** | ~$18.000 |

Anual: **−15 %** (prepago 12 meses).

---

## 3. Por plataforma: lista API (`/api/public/planes`)

| Plataforma | Entrada / Pro / Enterprise desde |
|------------|----------------------------------|
| **SPATI / VENTORA** | **99 / 179 / 449** |
| **Mantos Blancos** | **79 / 149 / 349** |
| **Copiapó** | **69 / 129 / 299** |
| **Quillota** | **39 / 69 / 149** |
| **Paine** | **19 / 39 / 79** |

Techos internos (no publicar): SPATI 1.800–3.000 · Mantos 1.200–2.200 · Copiapó 900–1.800 · Quillota 400–800 · Paine 200–500.

---

## 4. Descuentos sugeridos

| Condición | Descuento |
|-----------|-----------|
| Contrato 12 meses prepago | 15 % (ya en toggle landing) |
| 2+ faenas mismo contrato | 10 % |
| Piloto → conversión &lt;30 días | 1er mes 50 % |
| Sector público | Solo cotización |

## Fase

**Comercial / tracción** · DT precios early-adopter
