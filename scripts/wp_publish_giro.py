"""Publish METGO giro on WordPress (settings + /legal/ + home footer)."""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from wp_apply_venta import upsert_page  # noqa: E402
from wp_rest import request  # noqa: E402

GIRO = (
    "Servicios de análisis meteorológico, inteligencia climática y desarrollo "
    "de plataformas tecnológicas para la gestión de riesgos ambientales y operacionales."
)


def legal_content() -> str:
    return f"""<!-- wp:html -->
<div style="font-family:system-ui,sans-serif;background:#0f172a;color:#e2e8f0;padding:28px 16px;max-width:800px;margin:0 auto;box-sizing:border-box">
<h1 style="color:#ffffff;margin:0 0 16px">Información legal</h1>
<p style="color:#94a3b8;margin:0 0 8px"><strong style="color:#e2e8f0">Razón social:</strong> METGO 3D SpA</p>
<p style="color:#94a3b8;margin:0 0 8px"><strong style="color:#e2e8f0">Sitio:</strong> https://metgo3d.com</p>
<p style="color:#94a3b8;margin:0 0 16px"><strong style="color:#e2e8f0">Contacto:</strong> <a href="mailto:miguel.lucero@metgo3d.com" style="color:#ffffff;text-decoration:underline">miguel.lucero@metgo3d.com</a></p>
<h2 style="color:#ffffff;font-size:1.1rem;margin:24px 0 10px">Descripción de giro</h2>
<p style="color:#e2e8f0;line-height:1.7;margin:0">{GIRO}</p>
</div>
<!-- /wp:html -->
"""


def main() -> None:
    out = request("POST", "/wp/v2/settings", {"description": GIRO})
    print("tagline:", out.get("description"))

    pid = upsert_page("legal", "Información legal", legal_content(), 90)
    print("legal id:", pid)

    # Add Legal to navigation if missing
    nav = request("GET", "/wp/v2/navigation/203?context=edit")
    raw_nav = (nav.get("content") or {}).get("raw") or ""
    if "/legal/" not in raw_nav:
        link = (
            '<!-- wp:navigation-link {"label":"Legal","type":"custom",'
            '"url":"https://metgo3d.com/legal/","kind":"custom"} /-->'
        )
        request(
            "POST",
            "/wp/v2/navigation/203",
            {"content": raw_nav.rstrip() + "\n" + link, "status": "publish"},
        )
        print("nav: Legal added")
    else:
        print("nav: Legal already present")

    home = request("GET", "/wp/v2/pages/211?context=edit")
    raw = (home.get("content") or {}).get("raw") or ""
    marker = "<!-- metgo-giro -->"
    if marker not in raw:
        block = f"""
{marker}
<!-- wp:html -->
<p style="text-align:center;color:#64748b;font-size:12px;line-height:1.6;padding:8px 16px 24px;margin:0;background-color:#0f172a">{GIRO}<br><a href="/legal/" style="color:#94a3b8">Información legal</a></p>
<!-- /wp:html -->
"""
        request("POST", "/wp/v2/pages/211", {"content": raw + block, "status": "publish"})
        print("home: giro footer appended")
    else:
        print("home: giro already present")

    print("DONE")


if __name__ == "__main__":
    main()
