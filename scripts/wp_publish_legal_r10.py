#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""R10 Ley 21.719: publica/actualiza páginas Privacidad y Términos en metgo3d.com.

Uso (con WP_* en .env):
  python scripts/wp_publish_legal_r10.py
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.wp_rest import request  # noqa: E402

PRIVACY_SLUG = "privacidad"
TERMS_SLUG = "terminos"
CONTACT = "miguel.lucero@metgo3d.com"
SITE = "https://metgo3d.com"


def _wrap(title: str, body_html: str) -> str:
    return f"""<!-- wp:html -->
<div style="font-family:system-ui,-apple-system,sans-serif;background:#0f172a;color:#e2e8f0;padding:28px 16px;max-width:820px;margin:0 auto;box-sizing:border-box;line-height:1.65">
<h1 style="color:#fff;margin:0 0 8px;font-size:1.75rem">{title}</h1>
<p style="color:#94a3b8;margin:0 0 24px;font-size:0.9rem">METGO 3D SpA · {SITE} · Contacto: <a href="mailto:{CONTACT}" style="color:#fff">{CONTACT}</a></p>
{body_html}
<p style="color:#64748b;margin:32px 0 0;font-size:0.8rem">Documento orientativo alineado a la Ley N° 21.719 (Chile). Revisión legal externa recomendada antes del 1-dic-2026. Versión borrador 2026-09-04.</p>
</div>
<!-- /wp:html -->"""


PRIVACY_BODY = f"""
<h2 style="color:#fff;font-size:1.15rem;margin:28px 0 10px">1. Responsable del tratamiento</h2>
<p style="margin:0 0 12px">METGO 3D SpA (\"METGO\", \"nosotros\") es responsable del tratamiento de datos personales recolectados a través de {SITE} y las aplicaciones asociadas (Quillota, SPATI, VENTORA, Copiapó, Mantos Blancos, Paine y afines), salvo cuando actuemos como encargado por cuenta de un cliente B2B, en cuyo caso se documentará en el contrato correspondiente.</p>

<h2 style="color:#fff;font-size:1.15rem;margin:28px 0 10px">2. Datos que tratamos</h2>
<ul style="margin:0 0 12px;padding-left:1.2rem;color:#e2e8f0">
<li>Identificación y contacto: nombre, apellidos, correo, teléfono, RUT (hash) y datos de organización.</li>
<li>Credenciales y seguridad: contraseña hasheada, eventos de acceso (audit_auth), señales anti-abuso (p. ej. Turnstile).</li>
<li>Comerciales: plan, suscripción, preferencias de producto.</li>
<li>Datos técnicos del servicio (meteo, aire, faena): en general no son datos personales; se tratan para prestar el servicio.</li>
</ul>

<h2 style="color:#fff;font-size:1.15rem;margin:28px 0 10px">3. Finalidades y bases</h2>
<p style="margin:0 0 12px">Prestación del servicio SaaS, autenticación, facturación/planes, soporte, seguridad y mejora del producto. Bases típicas: ejecución de contrato o medidas precontractuales; consentimiento (cuando se solicita en el registro); interés legítimo en seguridad y prevención de abuso.</p>

<h2 style="color:#fff;font-size:1.15rem;margin:28px 0 10px">4. Conservación</h2>
<p style="margin:0 0 12px">Mientras la cuenta esté activa y plazos adicionales necesarios (p. ej. obligaciones contables o evidencias de consentimiento). Los registros de auditoría de autenticación se retienen según política interna (por defecto hasta ~18 meses) y luego se purgan.</p>

<h2 style="color:#fff;font-size:1.15rem;margin:28px 0 10px">5. Encargados y proveedores</h2>
<p style="margin:0 0 12px">Podemos usar proveedores de infraestructura y comunicaciones (p. ej. hosting API, base de datos, CDN/Pages, correo). Estos actúan según instrucciones y medidas de seguridad adecuadas.</p>

<h2 style="color:#fff;font-size:1.15rem;margin:28px 0 10px">6. Seguridad</h2>
<p style="margin:0 0 12px">Aplicamos medidas proporcionales al riesgo: HTTPS, autenticación por usuario (JWT), cifrado de campos personales en reposo, control de acceso a bases de datos (RLS / service role solo en servidor) y procedimientos de respuesta a incidentes.</p>

<h2 style="color:#fff;font-size:1.15rem;margin:28px 0 10px">7. Derechos (Ley 21.719)</h2>
<p style="margin:0 0 12px">Puede solicitar acceso, rectificación, cancelación/oposición, portabilidad y demás derechos que correspondan. En el producto autenticado:</p>
<ul style="margin:0 0 12px;padding-left:1.2rem">
<li>Portabilidad: exportación JSON de su cuenta (API autenticada).</li>
<li>Cancelación / olvido: solicitud de eliminación/anonimización de cuenta (API autenticada).</li>
</ul>
<p style="margin:0 0 12px">También puede escribir a <a href="mailto:{CONTACT}" style="color:#fff">{CONTACT}</a>. Responderemos en plazos razonables conforme a la normativa.</p>

<h2 style="color:#fff;font-size:1.15rem;margin:28px 0 10px">8. Cookies y similares</h2>
<p style="margin:0 0 12px">Usamos almacenamiento local/sesión necesarios para autenticación y preferencias. Servicios de seguridad (p. ej. Turnstile) pueden procesar datos técnicos según sus propias políticas.</p>

<h2 style="color:#fff;font-size:1.15rem;margin:28px 0 10px">9. Cambios</h2>
<p style="margin:0 0 12px">Podemos actualizar esta política; la versión vigente se publicará en esta URL. El uso continuado del servicio tras cambios relevantes implica toma de conocimiento, sin perjuicio de nuevos consentimientos cuando la ley lo exija.</p>
"""

TERMS_BODY = f"""
<h2 style="color:#fff;font-size:1.15rem;margin:28px 0 10px">1. Aceptación</h2>
<p style="margin:0 0 12px">Al crear una cuenta o usar las plataformas METGO 3D usted acepta estos Términos de uso y la <a href="{SITE}/privacidad/" style="color:#fff;text-decoration:underline">Política de privacidad</a>.</p>

<h2 style="color:#fff;font-size:1.15rem;margin:28px 0 10px">2. Servicio</h2>
<p style="margin:0 0 12px">METGO ofrece software de apoyo a la decisión agrometeorológica, ambiental y operacional (incluyendo verticales mineras/izaje según el producto contratado). Los pronósticos y alertas son herramientas de apoyo; no sustituyen criterio profesional ni garantías absolutas de predicción.</p>

<h2 style="color:#fff;font-size:1.15rem;margin:28px 0 10px">3. Cuentas</h2>
<p style="margin:0 0 12px">Usted es responsable de la veracidad de los datos entregados, de mantener la confidencialidad de sus credenciales y del uso de su cuenta. El auto-registro puede estar restringido o sujeto a verificación anti-abuso.</p>

<h2 style="color:#fff;font-size:1.15rem;margin:28px 0 10px">4. Planes y pagos</h2>
<p style="margin:0 0 12px">Los planes, precios y periodos de prueba se informan en el sitio o en cotización. Los servicios de pago pueden gestionarse mediante proveedores externos (p. ej. Stripe) cuando estén habilitados.</p>

<h2 style="color:#fff;font-size:1.15rem;margin:28px 0 10px">5. Uso aceptable</h2>
<p style="margin:0 0 12px">Está prohibido abusar de la API, intentar eludir controles de seguridad, redistribuir datos o el software sin autorización, o usar el servicio para fines ilícitos.</p>

<h2 style="color:#fff;font-size:1.15rem;margin:28px 0 10px">6. Propiedad intelectual</h2>
<p style="margin:0 0 12px">El software, marcas y contenidos de METGO son propiedad de METGO 3D SpA o de sus licenciantes. Se otorga una licencia limitada, no exclusiva y revocable de uso según el plan contratado.</p>

<h2 style="color:#fff;font-size:1.15rem;margin:28px 0 10px">7. Limitación de responsabilidad</h2>
<p style="margin:0 0 12px">En la máxima medida permitida por la ley aplicable, METGO no responde por daños indirectos, lucro cesante o decisiones operativas tomadas únicamente con base en alertas o modelos. La responsabilidad total, de existir, se limita a lo pagado por el servicio en los tres meses previos al reclamo, salvo norma imperativa en contrario.</p>

<h2 style="color:#fff;font-size:1.15rem;margin:28px 0 10px">8. Terminación</h2>
<p style="margin:0 0 12px">Puede solicitar el cierre de cuenta conforme a la política de privacidad. METGO puede suspender el acceso ante incumplimiento grave o riesgos de seguridad.</p>

<h2 style="color:#fff;font-size:1.15rem;margin:28px 0 10px">9. Ley aplicable</h2>
<p style="margin:0 0 12px">Estos términos se rigen por las leyes de la República de Chile. Controversias se someterán a los tribunales competentes de Chile, sin perjuicio de normas de protección al consumidor o de datos personales que resulten aplicables.</p>
"""


def _find_by_slug(slug: str) -> dict | None:
    pages = request("GET", f"/wp/v2/pages?slug={slug}&status=any&context=edit") or []
    return pages[0] if pages else None


def _upsert(slug: str, title: str, content: str) -> dict:
    existing = _find_by_slug(slug)
    body = {
        "title": title,
        "slug": slug,
        "status": "publish",
        "content": content,
    }
    if existing:
        out = request("POST", f"/wp/v2/pages/{existing['id']}", body)
        print(f"updated id={existing['id']} {out.get('link')}")
        return out or existing
    out = request("POST", "/wp/v2/pages", body)
    print(f"created id={(out or {}).get('id')} {(out or {}).get('link')}")
    return out or {}


def _patch_legal_hub() -> None:
    """Añade enlaces a /legal/ si existe."""
    p = request("GET", "/wp/v2/pages/362?context=edit")
    if not p:
        return
    raw = (p.get("content") or {}).get("raw") or ""
    if "/privacidad/" in raw and "/terminos/" in raw:
        print("legal hub ya enlaza privacidad/terminos")
        return
    extra = f"""
<h2 style="color:#ffffff;font-size:1.1rem;margin:24px 0 10px">Documentos</h2>
<ul style="color:#e2e8f0;line-height:1.8">
<li><a href="{SITE}/privacidad/" style="color:#ffffff;text-decoration:underline">Política de privacidad</a></li>
<li><a href="{SITE}/terminos/" style="color:#ffffff;text-decoration:underline">Términos de uso</a></li>
</ul>
"""
    # Insert before closing div if possible
    if "</div>" in raw:
        raw = raw.replace("</div>", extra + "</div>", 1)
    else:
        raw = raw + extra
    request("POST", "/wp/v2/pages/362", {"content": raw, "status": "publish"})
    print("updated Informacion legal (362) con enlaces")


def main() -> None:
    _upsert(PRIVACY_SLUG, "Política de privacidad", _wrap("Política de privacidad", PRIVACY_BODY))
    _upsert(TERMS_SLUG, "Términos de uso", _wrap("Términos de uso", TERMS_BODY))
    _patch_legal_hub()
    print("OK R10 — URLs:")
    print(f"  {SITE}/privacidad/")
    print(f"  {SITE}/terminos/")
    print(f"  {SITE}/legal/")


if __name__ == "__main__":
    main()
