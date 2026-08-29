"""METGO WP comercial v5.1 (paleta sobria) — header/footer/signup/home/productos sin 'en creación'.

Requiere WP_USER + WP_APP_PASSWORD (.env).
"""
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
GIRO = (
    "Servicios de análisis meteorológico, inteligencia climática y desarrollo "
    "de plataformas tecnológicas para la gestión de riesgos ambientales y operacionales."
)

BTN_P = (
    "display:inline-block;padding:14px 18px;border-radius:8px;font-weight:700;"
    "text-decoration:none;font-size:15px;margin:0 8px 10px 0;background:#4b5563;color:#ffffff"
)
BTN_S = (
    "display:inline-block;padding:14px 18px;border-radius:8px;font-weight:700;"
    "text-decoration:none;font-size:15px;margin:0 8px 10px 0;background:#1e293b;"
    "color:#e2e8f0;border:1px solid #334155"
)
CARD = (
    "background:#1a2030;border:1px solid rgba(255,255,255,.08);border-radius:12px;"
    "padding:18px;box-sizing:border-box;margin:0 0 12px;width:100%"
)


def header_content() -> str:
    """Header limpio: solo productos activos + Planes/Contacto. Sin 'en creación'."""
    return f"""<!-- METGO header comercial v5.1 paleta sobria · 2026-08-11 -->
<!-- wp:group {{"align":"full","style":{{"color":{{"background":"#121826","text":"#ffffff"}},"spacing":{{"padding":{{"top":"0px","bottom":"0px","right":"0px","left":"0px"}}}}}},"layout":{{"type":"constrained"}}}} -->
<div class="wp-block-group alignfull has-text-color has-background" style="color:#ffffff;background-color:#121826">
<!-- wp:html -->
<nav style="background:#121826;padding:0 20px;display:flex;align-items:center;justify-content:space-between;min-height:64px;position:relative;font-family:system-ui,-apple-system,Segoe UI,sans-serif;gap:12px;flex-wrap:wrap">
  <a href="https://metgo3d.com/" style="color:#fff;font-weight:800;font-size:15px;letter-spacing:1.5px;text-transform:uppercase;white-space:nowrap;text-decoration:none;flex-shrink:0">METGO 3D</a>
  <ul id="mg-menu" style="display:flex;align-items:center;gap:2px;list-style:none;margin:0;padding:0;flex:1;justify-content:center;flex-wrap:wrap">
    <li><a href="https://metgo3d.com/" style="color:#cbd5e1;font-size:13px;font-weight:600;padding:8px 10px;display:block;border-radius:6px;text-decoration:none;white-space:nowrap">Inicio</a></li>
    <li style="position:relative">
      <span onclick="mgToggle(this.parentElement)" style="color:#cbd5e1;font-size:13px;font-weight:600;padding:8px 10px;display:flex;align-items:center;gap:4px;border-radius:6px;cursor:pointer;white-space:nowrap">Productos <span class="mg-chev">▾</span></span>
      <div class="mg-drop" style="display:none;position:absolute;top:calc(100% + 6px);left:0;background:#1e293b;border:1px solid #334155;border-radius:8px;min-width:260px;z-index:9999;overflow:hidden;box-shadow:0 12px 32px rgba(0,0,0,.35)">
        <a href="https://metgo3d.com/agricultura-de-precision/" style="display:block;padding:11px 14px;color:#e2e8f0;text-decoration:none;font-size:13px;font-weight:600;border-bottom:1px solid #2d3c50">Agricultura · Quillota <span style="color:#8a9a8c;font-size:11px">desde USD 99</span></a>
        <a href="https://ventora-izaje-mar.pages.dev/" target="_blank" rel="noopener" style="display:block;padding:11px 14px;color:#e2e8f0;text-decoration:none;font-size:13px;font-weight:600;border-bottom:1px solid #2d3c50">VENTORA · Izaje <span style="color:#b0a48c;font-size:11px">desde USD 299</span></a>
        <a href="https://metgo3d.com/mineria-y-calidad-del-aire/" style="display:block;padding:11px 14px;color:#e2e8f0;text-decoration:none;font-size:13px;font-weight:600;border-bottom:1px solid #2d3c50">Minería y aire <span style="color:#8494a7;font-size:11px">desde USD 199</span></a>
        <a href="{PAINE}" target="_blank" rel="noopener" style="display:block;padding:11px 14px;color:#e2e8f0;text-decoration:none;font-size:13px;font-weight:600">Paine / terreno <span style="color:#a49eb0;font-size:11px">desde USD 49</span></a>
      </div>
    </li>
    <li><a href="https://metgo3d.com/planes/" style="color:#cbd5e1;font-size:13px;font-weight:600;padding:8px 10px;display:block;border-radius:6px;text-decoration:none;white-space:nowrap">Planes</a></li>
    <li><a href="https://metgo3d.com/innovaciones/" style="color:#cbd5e1;font-size:13px;font-weight:600;padding:8px 10px;display:block;border-radius:6px;text-decoration:none;white-space:nowrap">Innovaciones</a></li>
    <li><a href="https://metgo3d.com/nosotros/" style="color:#cbd5e1;font-size:13px;font-weight:600;padding:8px 10px;display:block;border-radius:6px;text-decoration:none;white-space:nowrap">Nosotros</a></li>
    <li><a href="https://metgo3d.com/contacto/" style="color:#cbd5e1;font-size:13px;font-weight:600;padding:8px 10px;display:block;border-radius:6px;text-decoration:none;white-space:nowrap">Contacto</a></li>
  </ul>
  <div id="mg-acceder" style="position:relative;flex-shrink:0">
    <button type="button" onclick="mgToggleAcceder()" style="background:#4b5563;color:#fff;border:none;border-radius:6px;padding:9px 16px;font-weight:700;font-size:13px;cursor:pointer;white-space:nowrap">Acceder ▾</button>
    <div id="mg-adrop" style="display:none;position:absolute;right:0;top:calc(100% + 6px);background:#1e293b;border:1px solid #334155;border-radius:8px;min-width:240px;z-index:9999;overflow:hidden;box-shadow:0 12px 32px rgba(0,0,0,.35)">
      <a href="{QUILLOTA}" target="_blank" rel="noopener" style="display:block;padding:11px 14px;color:#fff;text-decoration:none;font-size:13px;font-weight:600;border-bottom:1px solid #334155">Quillota · Agro</a>
      <a href="{SPATI}" target="_blank" rel="noopener" style="display:block;padding:11px 14px;color:#fff;text-decoration:none;font-size:13px;font-weight:600;border-bottom:1px solid #334155">VENTORA · Izaje</a>
      <a href="{COPIAPO}" target="_blank" rel="noopener" style="display:block;padding:11px 14px;color:#fff;text-decoration:none;font-size:13px;font-weight:600;border-bottom:1px solid #334155">Copiapó · Aire</a>
      <a href="{MANTOS}" target="_blank" rel="noopener" style="display:block;padding:11px 14px;color:#fff;text-decoration:none;font-size:13px;font-weight:600;border-bottom:1px solid #334155">Mantos Blancos</a>
      <a href="{PAINE}" target="_blank" rel="noopener" style="display:block;padding:11px 14px;color:#fff;text-decoration:none;font-size:13px;font-weight:600">Paine</a>
    </div>
  </div>
</nav>
<script>
function mgToggle(li) {{
  var drops = document.querySelectorAll('#mg-menu .mg-drop');
  var myDrop = li.querySelector('.mg-drop');
  var isOpen = myDrop.style.display === 'block';
  drops.forEach(function(d){{ d.style.display='none'; }});
  var ad = document.getElementById('mg-adrop'); if (ad) ad.style.display = 'none';
  if (!isOpen) myDrop.style.display = 'block';
}}
function mgToggleAcceder() {{
  var d = document.getElementById('mg-adrop');
  document.querySelectorAll('#mg-menu .mg-drop').forEach(function(x){{ x.style.display='none'; }});
  d.style.display = d.style.display === 'block' ? 'none' : 'block';
}}
document.addEventListener('click', function(e) {{
  if (!e.target.closest('#mg-menu') && !e.target.closest('#mg-acceder')) {{
    document.querySelectorAll('#mg-menu .mg-drop').forEach(function(d){{ d.style.display='none'; }});
    var ad = document.getElementById('mg-adrop'); if (ad) ad.style.display = 'none';
  }}
}});
</script>
<!-- /wp:html -->
</div>
<!-- /wp:group -->
"""


def footer_content() -> str:
    return f"""<!-- METGO footer comercial v5.1 paleta sobria · 2026-08-11 -->
<!-- wp:group {{"align":"full","style":{{"color":{{"background":"#0e121a","text":"#64748b"}},"spacing":{{"padding":{{"top":"48px","bottom":"28px","right":"24px","left":"24px"}}}}}},"layout":{{"type":"constrained","contentSize":"1100px"}}}} -->
<div class="wp-block-group alignfull has-text-color has-background" style="color:#64748b;background-color:#0e121a;padding-top:48px;padding-right:24px;padding-bottom:28px;padding-left:24px">
<!-- wp:html -->
<div style="font-family:system-ui,-apple-system,Segoe UI,sans-serif;line-height:1.55">
<div style="display:flex;flex-wrap:wrap;gap:10px;margin:0 0 36px">
  <a href="{QUILLOTA}" target="_blank" rel="noopener" style="background:#8a9a8c;color:#fff;padding:8px 14px;border-radius:6px;text-decoration:none;font-size:12px;font-weight:700">Quillota</a>
  <a href="{SPATI}" target="_blank" rel="noopener" style="background:#9a8f78;color:#121826;padding:8px 14px;border-radius:6px;text-decoration:none;font-size:12px;font-weight:700">VENTORA</a>
  <a href="{COPIAPO}" target="_blank" rel="noopener" style="background:#8494a7;color:#fff;padding:8px 14px;border-radius:6px;text-decoration:none;font-size:12px;font-weight:700">Copiapó</a>
  <a href="{MANTOS}" target="_blank" rel="noopener" style="background:#1e293b;color:#a3b0a6;padding:8px 14px;border-radius:6px;text-decoration:none;font-size:12px;font-weight:700;border:1px solid #334155">Mantos</a>
  <a href="{PAINE}" target="_blank" rel="noopener" style="background:#1e293b;color:#a49eb0;padding:8px 14px;border-radius:6px;text-decoration:none;font-size:12px;font-weight:700;border:1px solid #334155">Paine</a>
</div>
<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:28px;margin-bottom:32px">
  <div>
    <p style="color:#fff;font-weight:800;letter-spacing:1px;text-transform:uppercase;font-size:14px;margin:0 0 12px">METGO 3D SpA</p>
    <p style="color:#64748b;font-size:13px;line-height:1.7;margin:0 0 14px">{GIRO}</p>
    <p style="margin:0"><a href="https://metgo3d.com/legal/" style="color:#94a3b8;font-size:12px;text-decoration:underline">Información legal</a></p>
  </div>
  <div>
    <p style="color:#fff;font-size:11px;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;margin:0 0 12px">Productos</p>
    <a href="https://metgo3d.com/agricultura-de-precision/" style="color:#94a3b8;text-decoration:none;display:block;font-size:13px;margin:0 0 8px">Agricultura</a>
    <a href="https://ventora-izaje-mar.pages.dev/" target="_blank" rel="noopener" style="color:#94a3b8;text-decoration:none;display:block;font-size:13px;margin:0 0 8px">VENTORA Izaje</a>
    <a href="https://metgo3d.com/mineria-y-calidad-del-aire/" style="color:#94a3b8;text-decoration:none;display:block;font-size:13px;margin:0 0 8px">Minería y aire</a>
    <a href="https://metgo3d.com/planes/" style="color:#94a3b8;text-decoration:none;display:block;font-size:13px;margin:0 0 8px">Planes</a>
    <a href="https://metgo3d.com/innovaciones/" style="color:#94a3b8;text-decoration:none;display:block;font-size:13px">Innovaciones</a>
  </div>
  <div>
    <p style="color:#fff;font-size:11px;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;margin:0 0 12px">Contacto</p>
    <a href="{MAILTO}" style="color:#cbd5e1;text-decoration:none;display:block;font-size:13px;margin:0 0 8px;font-weight:600">{MAIL}</a>
    <a href="https://metgo3d.com/contacto/" style="color:#94a3b8;text-decoration:none;display:block;font-size:13px;margin:0 0 8px">Solicitar demo</a>
    <a href="{CONTACTO}" target="_blank" rel="noopener" style="color:#94a3b8;text-decoration:none;display:block;font-size:13px;margin:0 0 12px">Formulario</a>
    <a href="https://www.linkedin.com/in/metgo3d/" target="_blank" rel="noopener" style="color:#a8b4c0;text-decoration:none;font-size:12px;margin-right:12px">LinkedIn</a>
    <a href="https://www.instagram.com/metgo.3d/" target="_blank" rel="noopener" style="color:#a49eb0;text-decoration:none;font-size:12px">Instagram</a>
  </div>
</div>
<hr style="border:none;border-top:1px solid #1e293b;margin:0 0 20px"/>
<p style="color:#475569;font-size:12px;margin:0">© METGO 3D SpA · Clima operacional Chile · Piloto 15 días sin costo</p>
</div>
<!-- /wp:html -->
</div>
<!-- /wp:group -->
"""


def signup_content() -> str:
    """CTA oscuro comercial — reemplaza bloque claro + Netlify del tema CoachBen."""
    return f"""<!-- METGO signup/CTA comercial v5 -->
<!-- wp:group {{"align":"full","style":{{"color":{{"background":"#121826","text":"#e2e8f0"}},"spacing":{{"padding":{{"top":"48px","bottom":"48px","left":"24px","right":"24px"}}}}}},"layout":{{"type":"constrained","contentSize":"800px"}}}} -->
<div class="wp-block-group alignfull has-text-color has-background" style="color:#e2e8f0;background-color:#121826;padding-top:48px;padding-right:24px;padding-bottom:48px;padding-left:24px">
<!-- wp:heading {{"textAlign":"center","level":2,"style":{{"color":{{"text":"#ffffff"}}}}}} -->
<h2 class="wp-block-heading has-text-align-center has-text-color" style="color:#ffffff">Piloto 15 días. Si no sirve para tu operación, no pagas.</h2>
<!-- /wp:heading -->
<!-- wp:paragraph {{"align":"center","style":{{"color":{{"text":"#94a3b8"}}}}}} -->
<p class="has-text-align-center has-text-color" style="color:#94a3b8">Paneles vivos para agricultura, izaje, minería y calidad del aire. Escribe a {MAIL} o pide una demo.</p>
<!-- /wp:paragraph -->
<!-- wp:buttons {{"layout":{{"type":"flex","justifyContent":"center","flexWrap":"wrap"}}}} -->
<div class="wp-block-buttons">
<!-- wp:button {{"style":{{"color":{{"background":"#4b5563","text":"#ffffff"}},"border":{{"radius":"8px"}}}}}} -->
<div class="wp-block-button"><a class="wp-block-button__link has-text-color has-background wp-element-button" href="{CONTACTO}" style="border-radius:8px;color:#ffffff;background-color:#4b5563" target="_blank" rel="noopener">Solicitar demo</a></div>
<!-- /wp:button -->
<!-- wp:button {{"className":"is-style-outline","style":{{"color":{{"text":"#a8b4c0"}},"border":{{"radius":"8px"}}}}}} -->
<div class="wp-block-button is-style-outline"><a class="wp-block-button__link has-text-color wp-element-button" href="https://metgo3d.com/planes/" style="border-radius:8px;color:#a8b4c0">Ver planes</a></div>
<!-- /wp:button -->
</div>
<!-- /wp:buttons -->
</div>
<!-- /wp:group -->
"""


def page_template() -> str:
    return """<!-- wp:template-part {"slug":"header","tagName":"header","theme":"coachben"} /-->

<!-- wp:group {"tagName":"main","metadata":{"name":"Content"},"style":{"spacing":{"padding":{"top":"0","bottom":"0"}},"color":{"background":"#121826"}},"layout":{"type":"default"}} -->
<main class="wp-block-group has-background" style="background-color:#121826;padding-top:0;padding-bottom:0"><!-- wp:post-content {"lock":{"move":false,"remove":false},"align":"full","layout":{"type":"default"}} /-->

<!-- wp:template-part {"slug":"signup","align":"full","theme":"coachben"} /--></main>
<!-- /wp:group -->

<!-- wp:template-part {"slug":"footer","area":"footer","theme":"coachben"} /-->
"""


def home_content() -> str:
    return f"""<!-- METGO home comercial v5.1 paleta sobria · 2026-08-11 -->
<!-- wp:html -->
<div style="font-family:system-ui,-apple-system,Segoe UI,sans-serif;line-height:1.55;color:#e2e8f0;background-color:#121826;margin:0;width:100%;max-width:100%;box-sizing:border-box;overflow-x:hidden;padding:0">
<div style="max-width:1100px;margin:0 auto;padding:28px 16px 48px;box-sizing:border-box">

<div style="padding:28px 0 12px">
<p style="color:#8a9a8c;font-size:12px;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;margin:0 0 10px">METGO 3D · Clima operacional Chile</p>
<h1 style="font-size:clamp(1.75rem,6vw,2.9rem);font-weight:800;line-height:1.12;color:#ffffff;margin:0 0 14px">Evita pérdidas por clima en tu faena</h1>
<p style="font-size:17px;color:#94a3b8;margin:0 0 22px;max-width:42rem">Pronósticos hiperlocales y alertas para agricultura, minería e izaje. Si hay riesgo de helada o viento, te avisa a tiempo — no al día siguiente.</p>
<p style="margin:0 0 8px">
<a href="{CONTACTO}" style="{BTN_P}" target="_blank" rel="noopener">Solicitar demo gratis</a>
<a href="https://metgo3d.com/planes/" style="{BTN_S}">Ver planes</a>
</p>
</div>

<div style="padding:32px 0 8px">
<h2 style="font-size:1.35rem;font-weight:800;color:#ffffff;margin:0 0 6px">Productos que puedes contratar hoy</h2>
<p style="font-size:14px;color:#64748b;margin:0 0 16px">Cada línea tiene panel en vivo, precio de lista y piloto de 15 días.</p>

<div style="{CARD};border-left:4px solid #8a9a8c">
<p style="margin:0 0 4px;color:#8a9a8c;font-size:11px;font-weight:700;letter-spacing:1px;text-transform:uppercase">Agricultura</p>
<a href="https://metgo3d.com/agricultura-de-precision/" style="color:#ffffff;font-weight:800;font-size:18px;text-decoration:none">Panel Quillota</a>
<p style="margin:8px 0;font-size:14px;color:#94a3b8">Helada, riego y microclima del valle. Alerta 12–24 h antes para tu zona.</p>
<p style="margin:0 0 10px;color:#e2e8f0;font-size:15px"><strong style="color:#8a9a8c">Desde USD 99</strong>/mes</p>
<a href="{QUILLOTA}" style="color:#a8b4c0;font-weight:700;text-decoration:none;margin-right:14px" target="_blank" rel="noopener">Abrir panel →</a>
<a href="{CONTACTO}" style="color:#cbd5e1;font-weight:700;text-decoration:none" target="_blank" rel="noopener">Pedir demo →</a>
</div>

<div style="{CARD};border-left:4px solid #b0a48c">
<p style="margin:0 0 4px;color:#b0a48c;font-size:11px;font-weight:700;letter-spacing:1px;text-transform:uppercase">Izaje / minería</p>
<a href="https://ventora-izaje-mar.pages.dev/" target="_blank" rel="noopener" style="color:#ffffff;font-weight:800;font-size:18px;text-decoration:none">VENTORA · SPATI Izajes</a>
<p style="margin:8px 0;font-size:14px;color:#94a3b8">Viento en altura, umbrales 26/31/36 km/h, alertas y PDF por operación.</p>
<p style="margin:0 0 10px;color:#e2e8f0;font-size:15px"><strong style="color:#b0a48c">Desde USD 299</strong>/mes</p>
<a href="{SPATI}" style="color:#a8b4c0;font-weight:700;text-decoration:none;margin-right:14px" target="_blank" rel="noopener">Abrir panel →</a>
<a href="{CONTACTO}" style="color:#cbd5e1;font-weight:700;text-decoration:none" target="_blank" rel="noopener">Pedir demo →</a>
</div>

<div style="{CARD};border-left:4px solid #8494a7">
<p style="margin:0 0 4px;color:#8494a7;font-size:11px;font-weight:700;letter-spacing:1px;text-transform:uppercase">Calidad del aire</p>
<a href="https://metgo3d.com/mineria-y-calidad-del-aire/" style="color:#ffffff;font-weight:800;font-size:18px;text-decoration:none">Copiapó · Mantos Blancos</a>
<p style="margin:8px 0;font-size:14px;color:#94a3b8">ICAP, episodios y semáforo de turno para cumplimiento DS 59 / DS 138.</p>
<p style="margin:0 0 10px;color:#e2e8f0;font-size:15px"><strong style="color:#8494a7">Desde USD 199</strong>/mes</p>
<a href="{COPIAPO}" style="color:#a8b4c0;font-weight:700;text-decoration:none;margin-right:14px" target="_blank" rel="noopener">Copiapó →</a>
<a href="{MANTOS}" style="color:#a8b4c0;font-weight:700;text-decoration:none" target="_blank" rel="noopener">Mantos →</a>
</div>

<div style="{CARD};border-left:4px solid #a49eb0">
<p style="margin:0 0 4px;color:#a49eb0;font-size:11px;font-weight:700;letter-spacing:1px;text-transform:uppercase">Terreno / outdoor</p>
<a href="{PAINE}" style="color:#ffffff;font-weight:800;font-size:18px;text-decoration:none" target="_blank" rel="noopener">Paine</a>
<p style="margin:8px 0;font-size:14px;color:#94a3b8">Clima usable en ruta y operaciones outdoor.</p>
<p style="margin:0 0 10px;color:#e2e8f0;font-size:15px"><strong style="color:#a49eb0">Desde USD 49</strong>/mes</p>
<a href="{PAINE}" style="color:#a8b4c0;font-weight:700;text-decoration:none" target="_blank" rel="noopener">Abrir panel →</a>
</div>
</div>

<div style="padding:20px 0 8px">
<h2 style="font-size:1.25rem;font-weight:800;color:#ffffff;margin:0 0 14px">Planes ancla</h2>
<div style="{CARD}"><strong style="color:#fff">Campo (agro)</strong> · <span style="color:#8a9a8c;font-weight:700">USD 99</span>/mes · <a href="{CONTACTO}" style="color:#cbd5e1;font-weight:700;text-decoration:none" target="_blank" rel="noopener">Solicitar acceso</a></div>
<div style="{CARD}"><strong style="color:#fff">Faena (izaje/minería)</strong> · <span style="color:#b0a48c;font-weight:700">USD 299</span>/mes · <a href="{CONTACTO}" style="color:#cbd5e1;font-weight:700;text-decoration:none" target="_blank" rel="noopener">Demo faena</a></div>
<div style="{CARD}"><strong style="color:#fff">Municipio (aire)</strong> · <span style="color:#8494a7;font-weight:700">USD 399</span>/mes · <a href="{CONTACTO}" style="color:#cbd5e1;font-weight:700;text-decoration:none" target="_blank" rel="noopener">Cotización</a></div>
<p style="margin:8px 0 0"><a href="https://metgo3d.com/planes/" style="color:#a8b4c0;font-weight:700;text-decoration:none">Ver detalle de planes →</a></p>
</div>

<div style="background:#121826;border-radius:12px;padding:28px 18px;text-align:center;margin:24px 0 8px">
<h2 style="font-size:clamp(1.3rem,4.5vw,1.85rem);font-weight:800;color:#ffffff;margin:0 0 12px">Piloto 15 días. Si no sirve, no pagas.</h2>
<p style="color:#94a3b8;font-size:15px;margin:0 0 18px">Contacto: <a href="{MAILTO}" style="color:#ffffff;font-weight:700;text-decoration:underline">{MAIL}</a></p>
<a href="{CONTACTO}" style="{BTN_P}" target="_blank" rel="noopener">Solicitar demo</a>
</div>

</div>
</div>
<!-- /wp:html -->
"""


def izaje_content() -> str:
    return f"""<!-- METGO producto VENTORA · 2026-08-11 -->
<!-- wp:html -->
<div style="font-family:system-ui,-apple-system,Segoe UI,sans-serif;line-height:1.55;color:#e2e8f0;background:#121826;padding:32px 16px 48px">
<div style="max-width:900px;margin:0 auto">
<p style="color:#b0a48c;font-size:12px;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;margin:0 0 10px">Producto · Izaje</p>
<h1 style="color:#fff;font-size:clamp(1.7rem,5vw,2.6rem);font-weight:800;margin:0 0 14px;line-height:1.15">VENTORA — viento hiperlocal para izaje seguro</h1>
<p style="color:#94a3b8;font-size:16px;margin:0 0 22px">Semáforo operativo en el punto GPS de la faena. Pronóstico 72 h, umbrales 26/31/36 km/h, alertas y PDF con sello de tiempo para mandantes.</p>
<p style="margin:0 0 28px">
<a href="{SPATI}" style="{BTN_P}" target="_blank" rel="noopener">Abrir panel en vivo</a>
<a href="{CONTACTO}" style="{BTN_S}" target="_blank" rel="noopener">Pedir piloto 15 días</a>
</p>
<div style="{CARD}"><strong style="color:#fff">Qué incluye</strong>
<ul style="margin:10px 0 0;padding-left:18px;color:#94a3b8;font-size:14px">
<li>Viento en altura (anclas 10 / 80 / 100 m + perfil a pluma)</li>
<li>Vista Ahora + panel 72 h</li>
<li>Alertas email (WhatsApp en Pro/Enterprise)</li>
<li>Informes PDF por operación</li>
</ul></div>
<div style="{CARD}"><strong style="color:#fff">Planes (lista USD / mes, sin IVA)</strong>
<p style="margin:10px 0 0;color:#e2e8f0;font-size:15px">Básico <strong style="color:#b0a48c">299</strong> · Pro <strong style="color:#b0a48c">499</strong> · Enterprise desde <strong style="color:#b0a48c">1.199</strong></p>
<p style="margin:8px 0 0;font-size:13px;color:#64748b">Piloto 15 días sin costo ni tarjeta.</p></div>
<p style="margin:16px 0 0;color:#94a3b8;font-size:14px">Contacto: <a href="{MAILTO}" style="color:#cbd5e1;font-weight:700">{MAIL}</a></p>
</div>
</div>
<!-- /wp:html -->
"""


def planes_content() -> str:
    return f"""<!-- wp:html -->
<div style="font-family:system-ui,sans-serif;background:#121826;color:#e2e8f0;padding:40px 16px;max-width:900px;margin:0 auto;box-sizing:border-box">
<h1 style="color:#fff;font-size:2rem;font-weight:800;margin:0 0 10px">Planes METGO</h1>
<p style="color:#94a3b8;margin:0 0 24px">Precios de lista en USD / mes. Primer piloto 15 días sin costo.</p>
<div style="{CARD}"><strong style="color:#fff">Campo (agro)</strong><p style="margin:8px 0;color:#8a9a8c;font-weight:700;font-size:1.25rem">USD 99/mes</p><a href="{CONTACTO}" style="color:#cbd5e1;font-weight:700;text-decoration:none" target="_blank" rel="noopener">Solicitar acceso →</a></div>
<div style="{CARD}"><strong style="color:#fff">Faena (izaje / minería)</strong><p style="margin:8px 0;color:#b0a48c;font-weight:700;font-size:1.25rem">USD 299/mes</p><a href="{CONTACTO}" style="color:#cbd5e1;font-weight:700;text-decoration:none" target="_blank" rel="noopener">Demo faena →</a></div>
<div style="{CARD}"><strong style="color:#fff">Municipio (aire)</strong><p style="margin:8px 0;color:#8494a7;font-weight:700;font-size:1.25rem">USD 399/mes</p><a href="{CONTACTO}" style="color:#cbd5e1;font-weight:700;text-decoration:none" target="_blank" rel="noopener">Cotización →</a></div>
<p style="color:#64748b;font-size:14px;margin:16px 0">Detalle por sitio: Quillota desde 99 · VENTORA desde 299 · Copiapó desde 199 · Mantos desde 249 · Paine desde 49.</p>
<p style="color:#e2e8f0">Contacto: <a href="{MAILTO}" style="color:#cbd5e1">{MAIL}</a></p>
</div>
<!-- /wp:html -->
"""


def innovaciones_content() -> str:
    return f"""<!-- wp:html -->
<div style="font-family:system-ui,sans-serif;background:#121826;color:#e2e8f0;padding:40px 16px;max-width:900px;margin:0 auto">
<h1 style="color:#fff;font-size:2rem;font-weight:800;margin:0 0 10px">Innovaciones que ya puedes contratar</h1>
<p style="color:#94a3b8;margin:0 0 24px">SKUs concretos con panel, precio y CTA — no roadmap técnico.</p>
<h2 style="color:#fff;font-size:1.15rem;margin:0 0 12px">Operar hoy</h2>
<div style="{CARD}"><a href="{QUILLOTA}" style="color:#8a9a8c;font-weight:700;text-decoration:none" target="_blank" rel="noopener">Panel agrícola Quillota</a> — desde USD 99</div>
<div style="{CARD}"><a href="{SPATI}" style="color:#b0a48c;font-weight:700;text-decoration:none" target="_blank" rel="noopener">VENTORA izaje</a> — desde USD 299</div>
<div style="{CARD}"><a href="{COPIAPO}" style="color:#8494a7;font-weight:700;text-decoration:none" target="_blank" rel="noopener">Calidad del aire Copiapó</a> — desde USD 199</div>
<div style="{CARD}"><a href="{MANTOS}" style="color:#a3b0a6;font-weight:700;text-decoration:none" target="_blank" rel="noopener">Semáforo Mantos Blancos</a> — desde USD 249</div>
<div style="{CARD}"><a href="{PAINE}" style="color:#a49eb0;font-weight:700;text-decoration:none" target="_blank" rel="noopener">Paine / terreno</a> — desde USD 49</div>
<h2 style="color:#fff;font-size:1.15rem;margin:20px 0 12px">Ampliar el plan</h2>
<ul style="color:#94a3b8;line-height:1.9;font-size:15px;margin:0 0 20px;padding-left:18px">
<li>Alertas correo / WhatsApp</li>
<li>Umbrales editables por faena</li>
<li>Calibración dron · board multi-faena · PDF operación</li>
</ul>
<p style="color:#e2e8f0">CTA: <a href="{MAILTO}" style="color:#cbd5e1">{MAIL}</a> · <a href="{CONTACTO}" style="color:#a8b4c0" target="_blank" rel="noopener">formulario demo</a></p>
</div>
<!-- /wp:html -->
"""


def contacto_content() -> str:
    return f"""<!-- wp:html -->
<div style="font-family:system-ui,sans-serif;background:#121826;color:#e2e8f0;padding:40px 16px;max-width:700px;margin:0 auto">
<h1 style="color:#fff;font-size:2rem;font-weight:800;margin:0 0 12px">Contacto / Demo</h1>
<p style="color:#94a3b8;margin:0 0 22px">Cuéntanos tu faena o predio. Respondemos a <strong style="color:#e2e8f0">{MAIL}</strong>.</p>
<p style="margin:0 0 12px"><a href="{CONTACTO}" style="{BTN_P}" target="_blank" rel="noopener">Abrir formulario METGO</a></p>
<p style="margin:0 0 20px"><a href="{MAILTO}" style="{BTN_S}">Escribir por email</a></p>
<p style="color:#64748b;font-size:14px">Incluye: nombre, empresa, sector (agricultura / minería / izaje / aire), faena o zona.</p>
</div>
<!-- /wp:html -->
"""


def product_banner(accent: str, title: str, price: str, panel: str, more: str) -> str:
    return f"""<!-- METGO commercial banner v5 -->
<!-- wp:html -->
<div style="font-family:system-ui,sans-serif;background:#121826;border-bottom:1px solid #1e293b;padding:18px 16px">
<div style="max-width:1100px;margin:0 auto;display:flex;flex-wrap:wrap;gap:12px;align-items:center;justify-content:space-between">
<div>
<p style="margin:0;color:{accent};font-size:11px;font-weight:700;letter-spacing:1px;text-transform:uppercase">Producto METGO</p>
<p style="margin:4px 0 0;color:#fff;font-weight:800;font-size:16px">{title} · <span style="color:{accent}">{price}</span></p>
</div>
<div>
<a href="{panel}" target="_blank" rel="noopener" style="display:inline-block;margin:0 8px 0 0;padding:10px 14px;border-radius:6px;background:#1e293b;color:#e2e8f0;text-decoration:none;font-weight:700;font-size:13px;border:1px solid #334155">Abrir panel</a>
<a href="{CONTACTO}" target="_blank" rel="noopener" style="display:inline-block;padding:10px 14px;border-radius:6px;background:#4b5563;color:#fff;text-decoration:none;font-weight:700;font-size:13px">Demo 15 días</a>
<a href="{more}" style="display:inline-block;margin-left:8px;color:#a8b4c0;font-size:13px;font-weight:700;text-decoration:none">Más info →</a>
</div>
</div>
</div>
<!-- /wp:html -->
"""


def nav_content() -> str:
    links = [
        ("Inicio", "https://metgo3d.com/"),
        ("Agricultura", "https://metgo3d.com/agricultura-de-precision/"),
        ("VENTORA Izaje", "https://ventora-izaje-mar.pages.dev/"),
        ("Minería / Aire", "https://metgo3d.com/mineria-y-calidad-del-aire/"),
        ("Planes", "https://metgo3d.com/planes/"),
        ("Innovaciones", "https://metgo3d.com/innovaciones/"),
        ("Nosotros", "https://metgo3d.com/nosotros/"),
        ("Contacto", "https://metgo3d.com/contacto/"),
    ]
    parts = []
    for label, url in links:
        new_tab = ',"opensInNewTab":true' if url == "https://ventora-izaje-mar.pages.dev/" else ''
        parts.append(
            f'<!-- wp:navigation-link {{"label":{json.dumps(label)},"type":"custom","url":{json.dumps(url)},"kind":"custom"{new_tab}}} /-->'
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
        if existing[0].get("status") == "trash":
            request("POST", f"/wp/v2/pages/{pid}", {"status": "publish"})
        request("POST", f"/wp/v2/pages/{pid}", body)
        print(f"updated page {slug} id={pid}")
        return pid
    out = request("POST", "/wp/v2/pages", body)
    print(f"created page {slug} id={out['id']}")
    return out["id"]


def patch_template_part(slug: str, content: str) -> None:
    tid = f"coachben//{slug}"
    request("POST", f"/wp/v2/template-parts/{tid}", {"content": content, "status": "publish"})
    print(f"updated template-part {tid}")


def upsert_banner(page_id: int, banner: str, marker: str = "METGO commercial banner v5") -> None:
    """Insert or replace the commercial banner block at the top of a page."""
    import re

    p = request("GET", f"/wp/v2/pages/{page_id}?context=edit")
    raw = (p.get("content") or {}).get("raw") or ""
    # Strip previous banner (html comment + following wp:html block)
    stripped = re.sub(
        r"<!--\s*" + re.escape(marker) + r".*?<!-- /wp:html -->\s*",
        "",
        raw,
        count=1,
        flags=re.S,
    )
    request(
        "POST",
        f"/wp/v2/pages/{page_id}",
        {"content": banner + "\n" + stripped.lstrip(), "status": "publish"},
    )
    print(f"upserted commercial banner on page {page_id}")


def main() -> None:
    print("=== METGO WP comercial v5.1 (paleta sobria) ===")

    print("1) Settings brand")
    request(
        "POST",
        "/wp/v2/settings",
        {
            "title": "METGO 3D",
            "description": GIRO,
            "show_on_front": "page",
            "page_on_front": 211,
            "page_for_posts": 0,
        },
    )

    print("2) Header / Footer / Signup / Page template")
    patch_template_part("header", header_content())
    patch_template_part("footer", footer_content())
    patch_template_part("signup", signup_content())
    patch_template_part(
        "cta",
        f"""<!-- METGO CTA v5.1 sobria -->
<!-- wp:group {{"align":"wide","style":{{"color":{{"background":"#121826","text":"#e2e8f0"}},"spacing":{{"padding":{{"top":"40px","bottom":"40px","left":"24px","right":"24px"}}}},"border":{{"radius":"12px"}}}},"layout":{{"type":"constrained"}}}} -->
<div class="wp-block-group alignwide has-text-color has-background" style="border-radius:12px;color:#e2e8f0;background-color:#121826;padding-top:40px;padding-right:24px;padding-bottom:40px;padding-left:24px">
<!-- wp:heading {{"textAlign":"center","level":2,"style":{{"color":{{"text":"#e5e7eb"}}}}}} -->
<h2 class="wp-block-heading has-text-align-center has-text-color" style="color:#e5e7eb">Listo para un piloto en tu faena?</h2>
<!-- /wp:heading -->
<!-- wp:paragraph {{"align":"center","style":{{"color":{{"text":"#9ca3af"}}}}}} -->
<p class="has-text-align-center has-text-color" style="color:#9ca3af">15 dias sin costo. Acceso a panel real.</p>
<!-- /wp:paragraph -->
<!-- wp:buttons {{"layout":{{"type":"flex","justifyContent":"center"}}}} -->
<div class="wp-block-buttons">
<!-- wp:button {{"style":{{"color":{{"background":"#4b5563","text":"#f8fafc"}},"border":{{"radius":"8px"}}}}}} -->
<div class="wp-block-button"><a class="wp-block-button__link has-text-color has-background wp-element-button" href="{CONTACTO}" style="border-radius:8px;color:#f8fafc;background-color:#4b5563" target="_blank" rel="noopener">Solicitar demo</a></div>
<!-- /wp:button -->
</div>
<!-- /wp:buttons -->
</div>
<!-- /wp:group -->
""",
    )
    request(
        "POST",
        "/wp/v2/templates/coachben//page",
        {"content": page_template(), "status": "publish"},
    )
    print("updated template coachben//page")

    print("3) Home + páginas venta")
    request(
        "POST",
        "/wp/v2/pages/211",
        {"title": "Inicio", "content": home_content(), "status": "publish", "menu_order": 1},
    )
    print("updated home 211")
    upsert_page("izaje-ventora", "VENTORA Izaje", izaje_content(), 15)
    upsert_page("planes", "Planes", planes_content(), 40)
    upsert_page("innovaciones", "Innovaciones", innovaciones_content(), 30)
    upsert_page("contacto", "Contacto", contacto_content(), 50)

    print("4) Banners comerciales en páginas sector")
    upsert_banner(
        204,
        product_banner("#8a9a8c", "Quillota Agro", "desde USD 99/mes", QUILLOTA, "https://metgo3d.com/agricultura-de-precision/"),
    )
    upsert_banner(
        213,
        product_banner("#8494a7", "Minería y aire", "desde USD 199/mes", COPIAPO, "https://ventora-izaje-mar.pages.dev/"),
    )

    print("5) Navigation block")
    request(
        "POST",
        "/wp/v2/navigation/203",
        {"title": "Navegación", "status": "publish", "content": nav_content()},
    )

    print("DONE")


if __name__ == "__main__":
    main()
