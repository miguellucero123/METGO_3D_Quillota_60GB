"""Apply METGO WordPress sales plan via REST. Requires WP_USER + WP_APP_PASSWORD."""
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from wp_rest import request  # noqa: E402

CONTACTO = "https://metgo-quillota.pages.dev/contacto"
QUILLOTA = "https://metgo-quillota.pages.dev"
SPATI = "https://metgo-spati.pages.dev"
COPIAPO = "https://metgo-copiapo.pages.dev"
MANTOS = "https://metgo-mantos.pages.dev"
PAINE = "https://metgo-paine.pages.dev"
MAIL = "miguel.lucero@metgo3d.com"
MAILTO = (
    f"mailto:{MAIL}?subject=Demo%20METGO%203D"
    "&body=Nombre%3A%0AEmpresa%3A%0ASector%20(agricultura%2Fminer%C3%ADa%2Fizaje%2Faire)%3A%0AFaena%20o%20zona%3A%0A"
)


def home_content() -> str:
    """Home mobile-first: HTML inline (sin <style>; WP.com/tema lo filtran)."""
    card = (
        "background:#161b22;border:1px solid rgba(255,255,255,.08);border-radius:12px;"
        "padding:18px;box-sizing:border-box;margin:0 0 12px;width:100%"
    )
    btn_p = (
        "display:inline-block;padding:14px 18px;border-radius:8px;font-weight:700;"
        "text-decoration:none;font-size:15px;margin:0 8px 10px 0;background:#ea580c;color:#ffffff"
    )
    btn_s = (
        "display:inline-block;padding:14px 18px;border-radius:8px;font-weight:700;"
        "text-decoration:none;font-size:15px;margin:0 8px 10px 0;background:#1e293b;"
        "color:#e2e8f0;border:1px solid #334155"
    )
    return f"""<!-- METGO home venta v4.1 mobile · 2026-08-11 -->
<!-- wp:html -->
<div style="font-family:system-ui,-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;line-height:1.55;color:#e2e8f0;background-color:#0f172a;margin:0;width:100%;max-width:100%;box-sizing:border-box;overflow-x:hidden;padding:0">
<div style="max-width:1100px;margin:0 auto;padding:28px 16px 40px;box-sizing:border-box">

<div style="padding:24px 0 8px">
<p style="color:#10b981;font-size:12px;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;margin:0 0 10px">METGO 3D · Clima operacional Chile</p>
<h1 style="font-size:clamp(1.7rem,6vw,2.8rem);font-weight:800;line-height:1.15;color:#ffffff;margin:0 0 14px">Evita pérdidas por clima en tu faena</h1>
<p style="font-size:16px;color:#94a3b8;margin:0 0 22px">Pronósticos hiperlocales y alertas para agricultura, minería e izaje en Chile. Si hay riesgo de helada o viento, te avisa a tiempo — no al día siguiente.</p>
<p style="margin:0 0 8px">
<a href="{CONTACTO}" style="{btn_p}" target="_blank" rel="noopener">Solicitar demo gratis</a>
<a href="{QUILLOTA}" style="{btn_s}" target="_blank" rel="noopener">Ver panel en vivo</a>
</p>
</div>

<div style="padding:28px 0 8px">
<h2 style="font-size:1.25rem;font-weight:800;color:#ffffff;margin:0 0 14px">Por qué METGO</h2>
<div style="{card};border-left:4px solid #10b981"><h3 style="font-size:16px;margin:0 0 8px;color:#ffffff">Agricultura</h3><p style="margin:0;font-size:14px;color:#94a3b8">Una helada mal anticipada puede costar la temporada. Alerta 12–24 h antes para tu zona.</p></div>
<div style="{card};border-left:4px solid #fbbf24"><h3 style="font-size:16px;margin:0 0 8px;color:#ffffff">Izaje / minería</h3><p style="margin:0;font-size:14px;color:#94a3b8">Una grúa o faena parada por viento cuesta miles de USD/hora. Semáforo horario para programar.</p></div>
<div style="{card};border-left:4px solid #3b82f6"><h3 style="font-size:16px;margin:0 0 8px;color:#ffffff">Calidad del aire</h3><p style="margin:0;font-size:14px;color:#94a3b8">Cumplir DS 59 / DS 138 sin monitoreo continuo es operar a ciegas.</p></div>
</div>

<div style="padding:20px 0 8px">
<h2 style="font-size:1.25rem;font-weight:800;color:#ffffff;margin:0 0 6px">Paneles operativos hoy</h2>
<p style="font-size:14px;color:#64748b;margin:0 0 14px">No es una app del tiempo: es el panel con el que tu turno decide.</p>
<div style="{card}"><a href="{QUILLOTA}" style="color:#10b981;font-weight:700;text-decoration:none;font-size:16px" target="_blank" rel="noopener">Quillota · Agro</a><p style="color:#e2e8f0;margin:8px 0;font-size:14px">Desde USD 99/mes</p><a href="{QUILLOTA}" style="color:#7dd3fc;font-weight:700;text-decoration:none" target="_blank" rel="noopener">Abrir panel →</a></div>
<div style="{card}"><a href="{SPATI}" style="color:#fbbf24;font-weight:700;text-decoration:none;font-size:16px" target="_blank" rel="noopener">VENTORA · Izaje</a><p style="color:#e2e8f0;margin:8px 0;font-size:14px">Desde USD 299/mes</p><a href="{SPATI}" style="color:#7dd3fc;font-weight:700;text-decoration:none" target="_blank" rel="noopener">Abrir panel →</a></div>
<div style="{card}"><a href="{COPIAPO}" style="color:#3b82f6;font-weight:700;text-decoration:none;font-size:16px" target="_blank" rel="noopener">Copiapó · Aire</a><p style="color:#e2e8f0;margin:8px 0;font-size:14px">Desde USD 199/mes</p><a href="{COPIAPO}" style="color:#7dd3fc;font-weight:700;text-decoration:none" target="_blank" rel="noopener">Abrir panel →</a></div>
<div style="{card}"><a href="{MANTOS}" style="color:#86efac;font-weight:700;text-decoration:none;font-size:16px" target="_blank" rel="noopener">Mantos Blancos</a><p style="color:#e2e8f0;margin:8px 0;font-size:14px">Desde USD 249/mes</p><a href="{MANTOS}" style="color:#7dd3fc;font-weight:700;text-decoration:none" target="_blank" rel="noopener">Abrir panel →</a></div>
<div style="{card}"><a href="{PAINE}" style="color:#c4b5fd;font-weight:700;text-decoration:none;font-size:16px" target="_blank" rel="noopener">Paine / terreno</a><p style="color:#e2e8f0;margin:8px 0;font-size:14px">Desde USD 49/mes</p><a href="{PAINE}" style="color:#7dd3fc;font-weight:700;text-decoration:none" target="_blank" rel="noopener">Abrir panel →</a></div>
<div style="{card}"><a href="/planes/" style="color:#ffffff;font-weight:700;text-decoration:none;font-size:16px">Ver todos los planes</a><p style="color:#e2e8f0;margin:8px 0;font-size:14px">Piloto 15 días sin costo</p><a href="{CONTACTO}" style="color:#fb923c;font-weight:700;text-decoration:none" target="_blank" rel="noopener">Pedir demo →</a></div>
</div>

<div style="background:#0a1628;border-radius:12px;padding:28px 18px;text-align:center;margin:16px 0 24px">
<h2 style="font-size:clamp(1.3rem,4.5vw,1.9rem);font-weight:800;color:#ffffff;margin:0 0 12px">Piloto 15 días. Si no sirve para tu operación, no pagas.</h2>
<p style="color:#e2e8f0;font-size:15px;margin:0 0 18px">Escribe a <a href="{MAILTO}" style="color:#ffffff;font-weight:700;text-decoration:underline">{MAIL}</a> o usa el formulario de contacto.</p>
<a href="{CONTACTO}" style="{btn_p}" target="_blank" rel="noopener">Solicitar demo</a>
</div>

</div>
</div>
<!-- /wp:html -->
"""


def planes_content() -> str:
    return f"""<!-- wp:group {{"align":"full","style":{{"color":{{"background":"#0f172a","text":"#e2e8f0"}},"spacing":{{"padding":{{"top":"56px","bottom":"56px","left":"24px","right":"24px"}}}}}},"layout":{{"type":"constrained","contentSize":"900px"}}}} -->
<div class="wp-block-group alignfull has-text-color has-background" style="color:#e2e8f0;background-color:#0f172a;padding-top:56px;padding-right:24px;padding-bottom:56px;padding-left:24px">
<!-- wp:heading {{"level":1,"style":{{"color":{{"text":"#ffffff"}}}}}} -->
<h1 class="wp-block-heading has-text-color" style="color:#ffffff">Planes METGO</h1>
<!-- /wp:heading -->
<!-- wp:paragraph {{"style":{{"color":{{"text":"#94a3b8"}}}}}} -->
<p class="has-text-color" style="color:#94a3b8">Precios de lista en USD / mes. Primer piloto 15 días sin costo. Si no sirve para tu operación, no pagas.</p>
<!-- /wp:paragraph -->
<!-- wp:html -->
<div style="overflow-x:auto;margin:24px 0">
<table style="width:100%;border-collapse:collapse;color:#e2e8f0;font-size:15px">
<thead><tr style="background:#161b22;text-align:left">
<th style="padding:12px 14px;border-bottom:1px solid #334155">Plan</th>
<th style="padding:12px 14px;border-bottom:1px solid #334155">Desde</th>
<th style="padding:12px 14px;border-bottom:1px solid #334155">CTA</th>
</tr></thead>
<tbody>
<tr><td style="padding:12px 14px;border-bottom:1px solid #1e293b">Campo (agro)</td><td style="padding:12px 14px;border-bottom:1px solid #1e293b"><strong style="color:#10b981">USD 99</strong>/mes</td><td style="padding:12px 14px;border-bottom:1px solid #1e293b"><a href="{CONTACTO}" style="color:#7dd3fc" target="_blank" rel="noopener">Solicitar acceso</a></td></tr>
<tr><td style="padding:12px 14px;border-bottom:1px solid #1e293b">Faena (izaje/minería)</td><td style="padding:12px 14px;border-bottom:1px solid #1e293b"><strong style="color:#fbbf24">USD 299</strong>/mes</td><td style="padding:12px 14px;border-bottom:1px solid #1e293b"><a href="{CONTACTO}" style="color:#7dd3fc" target="_blank" rel="noopener">Demo faena</a></td></tr>
<tr><td style="padding:12px 14px">Municipio (aire)</td><td style="padding:12px 14px"><strong style="color:#3b82f6">USD 399</strong>/mes</td><td style="padding:12px 14px"><a href="{CONTACTO}" style="color:#7dd3fc" target="_blank" rel="noopener">Cotización</a></td></tr>
</tbody></table>
</div>
<!-- /wp:html -->
<!-- wp:paragraph {{"style":{{"color":{{"text":"#94a3b8"}}}}}} -->
<p class="has-text-color" style="color:#94a3b8">Detalle por sitio: Quillota desde 99 · SPATI/VENTORA desde 299 · Copiapó desde 199 · Mantos desde 249 · Paine desde 49.</p>
<!-- /wp:paragraph -->
<!-- wp:paragraph {{"style":{{"color":{{"text":"#e2e8f0"}}}}}} -->
<p class="has-text-color" style="color:#e2e8f0">Contacto comercial: <a href="{MAILTO}" style="color:#fb923c">{MAIL}</a></p>
<!-- /wp:paragraph -->
</div>
<!-- /wp:group -->
"""


def innovaciones_content() -> str:
    return f"""<!-- wp:group {{"align":"full","style":{{"color":{{"background":"#0f172a","text":"#e2e8f0"}},"spacing":{{"padding":{{"top":"56px","bottom":"56px","left":"24px","right":"24px"}}}}}},"layout":{{"type":"constrained","contentSize":"900px"}}}} -->
<div class="wp-block-group alignfull has-text-color has-background" style="color:#e2e8f0;background-color:#0f172a;padding-top:56px;padding-right:24px;padding-bottom:56px;padding-left:24px">
<!-- wp:heading {{"level":1,"style":{{"color":{{"text":"#ffffff"}}}}}} -->
<h1 class="wp-block-heading has-text-color" style="color:#ffffff">Innovaciones que ya puedes contratar</h1>
<!-- /wp:heading -->
<!-- wp:paragraph {{"style":{{"color":{{"text":"#94a3b8"}}}}}} -->
<p class="has-text-color" style="color:#94a3b8">Además de los paneles, METGO empaqueta servicios concretos: alertas, izaje, aire, multi-faena y tendencias de temporada.</p>
<!-- /wp:paragraph -->
<!-- wp:heading {{"level":2,"style":{{"color":{{"text":"#ffffff"}}}}}} -->
<h2 class="wp-block-heading has-text-color" style="color:#ffffff">Operar hoy</h2>
<!-- /wp:heading -->
<!-- wp:html -->
<ul style="color:#e2e8f0;line-height:1.9;font-size:15px">
<li><a href="{QUILLOTA}" style="color:#10b981" target="_blank" rel="noopener">Panel agrícola Quillota</a> — desde USD 99</li>
<li><a href="{SPATI}" style="color:#fbbf24" target="_blank" rel="noopener">VENTORA izaje</a> — desde USD 299</li>
<li><a href="{COPIAPO}" style="color:#3b82f6" target="_blank" rel="noopener">Calidad del aire Copiapó</a> — desde USD 199</li>
<li><a href="{MANTOS}" style="color:#86efac" target="_blank" rel="noopener">Semáforo Mantos Blancos</a> — desde USD 249</li>
<li><a href="{PAINE}" style="color:#c4b5fd" target="_blank" rel="noopener">Paine / terreno</a> — desde USD 49</li>
</ul>
<!-- /wp:html -->
<!-- wp:heading {{"level":2,"style":{{"color":{{"text":"#ffffff"}}}}}} -->
<h2 class="wp-block-heading has-text-color" style="color:#ffffff">Ampliar el plan</h2>
<!-- /wp:heading -->
<!-- wp:html -->
<ul style="color:#e2e8f0;line-height:1.9;font-size:15px">
<li>Alertas correo / WhatsApp</li>
<li>Umbrales editables por faena</li>
<li>Calibración dron · board multi-faena · PDF operación</li>
</ul>
<!-- /wp:html -->
<!-- wp:heading {{"level":2,"style":{{"color":{{"text":"#ffffff"}}}}}} -->
<h2 class="wp-block-heading has-text-color" style="color:#ffffff">Próximo trimestre (cotizar)</h2>
<!-- /wp:heading -->
<!-- wp:html -->
<ul style="color:#e2e8f0;line-height:1.9;font-size:15px">
<li>Tendencia 20–90 días (ex-MJO comercial)</li>
<li>API de datos climáticos con token</li>
<li>White-label municipio / informe semanal PDF</li>
</ul>
<!-- /wp:html -->
<!-- wp:paragraph {{"style":{{"color":{{"text":"#e2e8f0"}}}}}} -->
<p class="has-text-color" style="color:#e2e8f0"><strong>CTA:</strong> escribe a <a href="{MAILTO}" style="color:#fb923c">{MAIL}</a> · <a href="{CONTACTO}" style="color:#7dd3fc" target="_blank" rel="noopener">formulario demo</a></p>
<!-- /wp:paragraph -->
</div>
<!-- /wp:group -->
"""


def contacto_content() -> str:
    return f"""<!-- wp:group {{"align":"full","style":{{"color":{{"background":"#0f172a","text":"#e2e8f0"}},"spacing":{{"padding":{{"top":"56px","bottom":"56px","left":"24px","right":"24px"}}}}}},"layout":{{"type":"constrained","contentSize":"700px"}}}} -->
<div class="wp-block-group alignfull has-text-color has-background" style="color:#e2e8f0;background-color:#0f172a;padding-top:56px;padding-right:24px;padding-bottom:56px;padding-left:24px">
<!-- wp:heading {{"level":1,"style":{{"color":{{"text":"#ffffff"}}}}}} -->
<h1 class="wp-block-heading has-text-color" style="color:#ffffff">Contacto / Demo</h1>
<!-- /wp:heading -->
<!-- wp:paragraph {{"style":{{"color":{{"text":"#94a3b8"}}}}}} -->
<p class="has-text-color" style="color:#94a3b8">Cuéntanos tu faena o predio. Respondemos a <strong style="color:#e2e8f0">{MAIL}</strong>.</p>
<!-- /wp:paragraph -->
<!-- wp:buttons -->
<div class="wp-block-buttons">
<!-- wp:button {{"style":{{"color":{{"background":"#ea580c","text":"#ffffff"}},"border":{{"radius":"6px"}}}}}} -->
<div class="wp-block-button"><a class="wp-block-button__link has-text-color has-background wp-element-button" href="{CONTACTO}" style="border-radius:6px;color:#ffffff;background-color:#ea580c" target="_blank" rel="noopener">Abrir formulario METGO</a></div>
<!-- /wp:button -->
<!-- wp:button {{"className":"is-style-outline","style":{{"color":{{"text":"#7dd3fc"}}}}}} -->
<div class="wp-block-button is-style-outline"><a class="wp-block-button__link has-text-color wp-element-button" href="{MAILTO}" style="color:#7dd3fc">Escribir por email</a></div>
<!-- /wp:button -->
</div>
<!-- /wp:buttons -->
<!-- wp:paragraph {{"style":{{"color":{{"text":"#64748b"}}}}}} -->
<p class="has-text-color" style="color:#64748b">Incluye: nombre, empresa, sector (agricultura / minería / izaje / aire), faena o zona.</p>
<!-- /wp:paragraph -->
</div>
<!-- /wp:group -->
"""


def nav_content() -> str:
    # Explicit links — no page-list (evita CV y basura)
    links = [
        ("Inicio", "https://metgo3d.com/"),
        ("Agricultura", "https://metgo3d.com/agricultura-de-precision/"),
        ("Minería / Aire", "https://metgo3d.com/mineria-y-calidad-del-aire/"),
        ("Innovaciones", "https://metgo3d.com/innovaciones/"),
        ("Planes", "https://metgo3d.com/planes/"),
        ("Nosotros", "https://metgo3d.com/nosotros/"),
        ("Contacto", "https://metgo3d.com/contacto/"),
    ]
    parts = []
    for label, url in links:
        parts.append(
            f'<!-- wp:navigation-link {{"label":{json.dumps(label)},"type":"custom","url":{json.dumps(url)},"kind":"custom"}} /-->'
        )
    return "\n".join(parts)


def upsert_page(slug: str, title: str, content: str, menu_order: int = 0) -> int:
    existing = request("GET", f"/wp/v2/pages?slug={slug}&status=any&context=edit")
    body = {
        "title": title,
        "content": content,
        "status": "publish",
        "slug": slug,
        "menu_order": menu_order,
    }
    if existing:
        pid = existing[0]["id"]
        # restore if trashed
        if existing[0].get("status") == "trash":
            request("POST", f"/wp/v2/pages/{pid}", {"status": "publish"})
        out = request("POST", f"/wp/v2/pages/{pid}", body)
        print(f"updated page {slug} id={pid}")
        return pid
    out = request("POST", "/wp/v2/pages", body)
    print(f"created page {slug} id={out['id']}")
    return out["id"]


def main() -> None:
    print("1) Front page = METGO3D (211)")
    request(
        "POST",
        "/wp/v2/settings",
        {
            "show_on_front": "page",
            "page_on_front": 211,
            "page_for_posts": 0,
        },
    )

    print("2) Home content + title")
    request(
        "POST",
        "/wp/v2/pages/211",
        {
            "title": "Inicio",
            "content": home_content(),
            "status": "publish",
            "menu_order": 1,
        },
    )

    print("3) Planes / Innovaciones / Contacto")
    upsert_page("planes", "Planes", planes_content(), 40)
    upsert_page("innovaciones", "Innovaciones", innovaciones_content(), 30)
    upsert_page("contacto", "Contacto", contacto_content(), 50)

    print("4) Navigation (sin page-list)")
    request(
        "POST",
        "/wp/v2/navigation/203",
        {
            "title": "Navegación",
            "status": "publish",
            "content": nav_content(),
        },
    )

    # Ensure MJO stays but not in primary nav (ok)
    print("5) Verify settings")
    s = request("GET", "/wp/v2/settings")
    print(
        "show_on_front=",
        s.get("show_on_front"),
        "page_on_front=",
        s.get("page_on_front"),
    )
    print("DONE")


if __name__ == "__main__":
    main()
