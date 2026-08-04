# Facturación electrónica Chile (SII) — scaffold METGO

> **Estado:** preparado / sin credenciales. No emitir DTE reales hasta certificación SII.  
> **Separación:** Stripe = cobro de tarjeta; SII = boleta/factura electrónica post-pago.

## Objetivo

Scripts Python para:

1. Validar payload comercial (RUT emisor/receptor, montos, tipo DTE).
2. Generar XML DTE **placeholder** en modo `--dry-run`.
3. Dejar hooks para firma (certificado `.p12`) y envío a SII (certificación → producción).

Tipos habituales:

| Código | Documento |
|--------|-----------|
| 33 | Factura electrónica |
| 34 | Factura exenta |
| 39 | Boleta electrónica |
| 41 | Boleta exenta |

## Variables de entorno (nunca en git)

```bash
SII_AMBIENTE=cert          # cert | prod
SII_RUT_EMISOR=76XXXXXX-K  # RUT METGO 3D SpA
SII_RAZON_EMISOR="METGO 3D SpA"
SII_GIRO_EMISOR="..."
SII_DIRECCION_EMISOR="..."
SII_COMUNA_EMISOR="..."
SII_CERT_PATH=/secretos/metgo-sii.p12
SII_CERT_PASSWORD=         # solo env / secret manager
SII_CAF_PATH=/secretos/caf-39.xml   # opcional por tipo
SII_RESOLUCION_NUM=
SII_RESOLUCION_FECHA=
```

Copiar `.env.sii.example` → `.env.sii` (ignorado).

## Uso

```powershell
cd D:\METGO_3D_Quillota_60GB
python scripts/sii/emit_dte.py --dry-run --tipo 39 --ejemplo
python scripts/sii/emit_dte.py --dry-run --tipo 33 --input scripts/sii/examples/factura_ejemplo.json
python scripts/sii/validate_payload.py --input scripts/sii/examples/boleta_ejemplo.json
```

Sin certificado o sin `SII_CERT_PATH`, **solo dry-run** (no firma / no envío).

## Integración futura con billing

Tras `POST /api/billing/webhook` (Stripe o mock):

1. Encolar job `emitir_dte(org_id, plan_code, monto_clp)`.
2. Leer RUT/razón de la org (identity Supabase).
3. Emitir boleta 39 (B2C) o factura 33 (B2B con RUT receptor).
4. Guardar track ID / PDF en storage (Supabase) y notificar por email (SMTP).

## Dependencias opcionales

Ver `requirements-sii.txt` (comentadas). No instalar en la API Render hasta certificación.

## Referencias

- SII facturación electrónica (ambiente de certificación).
- Alternativas de industria: LibreDTE, OpenFactura, facturadores autorizados — evaluar en fase comercial; este scaffold es **agnóstico**.
