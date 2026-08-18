"""Publish SPATI blog post to WordPress."""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from wp_rest import request  # noqa: E402

TITLE = "El viento invisible que paraliza los izajes — y cómo anticiparlo"

CONTENT = r"""<!-- ENTRADA BLOG METGO 3D — SPATI Izajes / VENTORA -->
<p>En las operaciones de izaje, el viento es el factor de riesgo más subestimado y, paradójicamente, uno de los más costosos. No se ve, pero está ahí: haciendo oscilar una carga de 50 toneladas, forzando correcciones constantes al operador y, en el peor escenario, provocando accidentes que paralizan faenas enteras y destruyen equipos valuados en millones de dólares.</p>

<p>El problema no es solo la seguridad — es la planificación. Sin un pronóstico preciso y localizado, las empresas de izaje operan a ciegas, absorbiendo costos de tiempo detenido que, según estudios internacionales, pueden representar entre el <strong>10 % y el 20 %</strong> del tiempo total de un proyecto de construcción.</p>

<hr>

<h2>Los números que respaldan la urgencia</h2>

<p>Datos recopilados por la Asociación Nacional de Normalización de Estados Unidos (ANSI) son contundentes:</p>

<ul>
  <li>Entre 2000 y 2010 se reportaron <strong>1.125 accidentes con grúas torre</strong> en todo el mundo.</li>
  <li>Esos accidentes resultaron en más de <strong>780 muertes</strong>.</li>
  <li>El <strong>23 %</strong> fue causado directamente por vientos fuertes.</li>
  <li>En 2023, de los 77 accidentes con grúas torre reportados globalmente, el <strong>17 %</strong> estuvo relacionado con el viento.</li>
</ul>

<p>El impacto económico es igual de claro. El costo promedio de un accidente con grúa — incluyendo responsabilidades legales, daños y retrasos — se estima en <strong>USD 100.000</strong>, pudiendo superar los <strong>USD 150.000</strong> por incidente cuando se suman honorarios legales. En el Reino Unido, el clima extremo extiende los plazos de proyectos hasta en un 21 %, con un costo anual de £2.200 millones para el país.</p>

<hr>

<h2>El caso chileno: una realidad que exige acción</h2>

<p>Chile no es ajeno a esta problemática. La diversidad geográfica y climática del país — sumada a la creciente altura de las estructuras y el tamaño de las cargas — hace que la incertidumbre del viento sea un factor crítico en faenas mineras, de construcción, portuarias e industriales.</p>

<p>La normativa y la práctica operacional en Chile trabajan con umbrales claros (alineados a la operación VENTORA / SPATI):</p>

<ul>
  <li>≥ <strong>26 km/h</strong> — precaución</li>
  <li>≥ <strong>31 km/h</strong> — suspensión recomendada</li>
  <li>≥ <strong>36 km/h</strong> — suspensión requerida</li>
</ul>

<p>Sin embargo, la mayoría de las empresas aún carece de herramientas para anticiparse a estas condiciones con la precisión y el tiempo necesarios. El resultado: paradas no programadas, horas de grúa detenidas, reprogramaciones de última hora y — en el peor caso — accidentes con consecuencias fatales.</p>

<hr>

<h2>La solución: VENTORA / SPATI Izajes, pronóstico hiperlocal para decisiones con tiempo</h2>

<p><strong>VENTORA</strong> (plataforma <strong>SPATI Izajes</strong> de METGO 3D) no es un pronóstico del tiempo genérico. Es una herramienta de planificación operacional que entrega datos de viento en el perfil vertical donde realmente importa: anclas a 10 / 80 / 100 m y perfil hasta la altura de pluma — justo donde opera la grúa.</p>

<p>La plataforma ofrece:</p>

<ul>
  <li><strong>Pronóstico con 72 horas de anticipación</strong> para programar izajes pesados en las ventanas de seguridad.</li>
  <li><strong>Alertas por umbrales críticos</strong> (26, 31 y 36 km/h), para que el equipo sepa con exactitud cuándo actuar.</li>
  <li><strong>Vista Ahora + panel web</strong> en el punto GPS de la faena.</li>
  <li><strong>Respaldo documental</strong> con reportes PDF descargables que certifican las condiciones climáticas al momento del izaje, útiles para el cumplimiento de protocolos y normativa.</li>
</ul>

<h2>Beneficios concretos para la operación</h2>

<ul>
  <li><strong>Reducción de tiempos muertos:</strong> al conocer con anticipación las ventanas de viento favorable, se minimizan las paradas no programadas y se optimiza el uso de grúa y personal.</li>
  <li><strong>Cumplimiento normativo asegurado:</strong> los reportes generados sirven como evidencia documental ante mandantes y organismos fiscalizadores.</li>
  <li><strong>Planificación anticipada:</strong> programar maniobras con hasta 3 días de antelación permite gestionar los recursos de forma mucho más eficiente.</li>
</ul>

<hr>

<h2>Del riesgo a la certidumbre</h2>

<p>El viento no va a desaparecer — pero la incertidumbre que genera sí puede reducirse. VENTORA / SPATI Izajes entrega a las empresas chilenas la capacidad de transformar un riesgo operacional en un dato planificable, reduciendo costos, mejorando la seguridad y aumentando la productividad.</p>

<p><strong>Pueden probar el sistema 15 días sin costo y sin tarjeta.</strong> Si no aporta a la operación, no continúan y no pagan.</p>

<p><strong>¿Estás listo para dejar de reaccionar al viento y empezar a planificar con él?</strong></p>

<p style="text-align:center; margin-top: 24px;">
  <a href="https://metgo-spati.pages.dev"
     style="display:inline-block; background-color:#10b981; color:#ffffff; padding:14px 28px; border-radius:6px; text-decoration:none; font-weight:700; font-size:16px;">
    Activar piloto gratuito 15 días →
  </a>
</p>
<p style="text-align:center; margin-top: 12px;">
  <a href="mailto:miguel.lucero@metgo3d.com?subject=Demo%20VENTORA%20SPATI"
     style="display:inline-block; background-color:#ea580c; color:#ffffff; padding:12px 24px; border-radius:6px; text-decoration:none; font-weight:700; font-size:15px;">
    Solicitar demo →
  </a>
</p>
"""


def main() -> None:
    # Avoid duplicate if same slug exists
    slug = "el-viento-invisible-que-paraliza-los-izajes-y-como-anticiparlo"
    existing = request("GET", f"/wp/v2/posts?slug={slug}&status=any&context=edit")
    body = {
        "title": TITLE,
        "content": CONTENT,
        "status": "publish",
        "slug": slug,
        "excerpt": (
            "El viento es el riesgo más subestimado en izaje. "
            "VENTORA / SPATI entrega pronóstico hiperlocal 72 h, umbrales 26/31/36 km/h "
            "y piloto gratuito de 15 días."
        ),
    }
    if existing:
        pid = existing[0]["id"]
        if existing[0].get("status") == "trash":
            request("POST", f"/wp/v2/posts/{pid}", {"status": "publish"})
        out = request("POST", f"/wp/v2/posts/{pid}", body)
        print("updated", out.get("id"), out.get("link"))
    else:
        out = request("POST", "/wp/v2/posts", body)
        print("created", out.get("id"), out.get("link"))


if __name__ == "__main__":
    main()
