"""Publica home + páginas producto con sistema mg-page (CSS sobrio embebido).

Requiere WP_USER + WP_APP_PASSWORD.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from wp_rest import request  # noqa: E402

HERE = os.path.dirname(__file__)
CSS_PATH = os.path.join(HERE, "_wp_pages", "metgo3d-css-adicional.css")

CONTACTO = "https://metgo3d.com/contacto/"
QUILLOTA = "https://metgo-quillota.pages.dev"
SPATI = "https://metgo-spati.pages.dev"
COPIAPO = "https://metgo-copiapo.pages.dev"
MANTOS = "https://metgo-mantos.pages.dev"
PAINE = "https://metgo-paine.pages.dev"
MAIL = "miguel.lucero@metgo3d.com"
MAILTO = (
    f"mailto:{MAIL}?subject=Demo%20METGO3D"
    "&body=Nombre%3A%0AEmpresa%3A%0ASector%3A%0AFaena%20o%20zona%3A%0A"
)


def load_css() -> str:
    with open(CSS_PATH, encoding="utf-8") as f:
        return f.read()


def nav_html(active: str = "") -> str:
    def a(key: str, href: str, label: str) -> str:
        cls = ' class="is-active"' if active == key else ""
        return f'<li><a href="{href}"{cls}>{label}</a></li>'

    return f"""
  <nav class="mg-nav">
    <a href="https://metgo3d.com/" class="mg-nav__logo">METGO3D</a>
    <ul class="mg-nav__links">
      {a("productos", "https://metgo3d.com/#productos", "Productos")}
      {a("mjo_chile", "https://metgo3d.com/mjo_chile/", "MJO Chile")}
      {a("izaje", "https://metgo3d.com/izaje-ventora/", "VENTORA")}
      {a("planes", "https://metgo3d.com/planes/", "Planes")}
      {a("nosotros", "https://metgo3d.com/nosotros/", "Nosotros")}
      {a("contacto", "https://metgo3d.com/contacto/", "Contacto")}
    </ul>
    <div style="display: flex; gap: 0.5rem; align-items: center;">
      <!-- Language Selector -->
      <div class="mg-nav__cta-wrap">
        <button type="button" class="mg-nav__cta" onclick="this.parentElement.classList.toggle('is-open')" title="Idioma">🌐 ES ▾</button>
        <div class="mg-nav__drop" style="min-width: 120px; right: auto; left: 0;">
          <a href="#" onclick="alert('Traducción a Inglés próximamente'); return false;">EN - English</a>
          <a href="#" onclick="alert('Traducción a Alemán próximamente'); return false;">DE - Deutsch</a>
          <a href="#" onclick="alert('Traducción a Francés próximamente'); return false;">FR - Français</a>
          <a href="#" onclick="alert('Traducción a Italiano próximamente'); return false;">IT - Italiano</a>
          <a href="#" onclick="alert('Traducción a Surcoreano próximamente'); return false;">KO - 한국어</a>
        </div>
      </div>
      <!-- Theme Toggle -->
      <button type="button" class="mg-nav__cta" onclick="window.mgToggleTheme && window.mgToggleTheme()" aria-label="Cambiar tema" style="padding: 6px 10px;" title="Modo Claro / Oscuro">
        ☀ / ☾
      </button>
      <div class="mg-nav__cta-wrap">
        <button type="button" class="mg-nav__cta" onclick="this.parentElement.classList.toggle('is-open')">Acceder ▾</button>
        <div class="mg-nav__drop">
          <a href="{QUILLOTA}" target="_blank" rel="noopener">Quillota · Agro</a>
          <a href="{SPATI}" target="_blank" rel="noopener">VENTORA · Izaje</a>
          <a href="{COPIAPO}" target="_blank" rel="noopener">Copiapó · Aire</a>
          <a href="{MANTOS}" target="_blank" rel="noopener">Mantos Blancos</a>
          <a href="{PAINE}" target="_blank" rel="noopener">Paine</a>
          <a href="https://metgo3d.com/mjo_chile/">MJO Chile · 7–90 d</a>
        </div>
      </div>
    </div>
  </nav>
"""


def ticker_html() -> str:
    """Cinta: placeholders; JS carga datos reales de la API METGO."""
    return """
  <div class="mg-ticker" aria-label="Datos operacionales en vivo" data-mg-ticker>
    <div class="mg-ticker__inner" id="mg-ticker-inner">
      <span class="mg-ticker__item"><span class="mg-ticker__dot mg-ticker__dot--agro"></span>Quillota · cargando datos…</span>
      <span class="mg-ticker__item"><span class="mg-ticker__dot mg-ticker__dot--izaje"></span>VENTORA · cargando datos…</span>
      <span class="mg-ticker__item"><span class="mg-ticker__dot mg-ticker__dot--aire"></span>Copiapó · cargando datos…</span>
      <a class="mg-ticker__item" href="https://metgo3d.com/mjo_chile/" style="text-decoration:none;color:inherit"><span class="mg-ticker__dot mg-ticker__dot--agro"></span>MJO Chile · <span class="mg-ticker__val" id="mg-mjo-status">cargando…</span></a>
    </div>
  </div>
"""


def ticker_script() -> str:
    return r"""
<script>
(function () {
  var API = 'https://metgo-api.onrender.com/api/public/marketing/ticker';
  var REFRESH_MS = 3600000; // 1 h

  function esc(s) {
    return String(s == null ? '' : s)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  function renderItems(items) {
    var inner = document.getElementById('mg-ticker-inner');
    if (!inner || !items || !items.length) return;
    var html = items.map(function (it) {
      var dot = esc(it.dot || 'agro');
      var label = esc(it.label || '');
      var val = esc(it.val || '');
      var detail = esc(it.detail || '');
      var href = esc(it.href || '#');
      return '<a class="mg-ticker__item" href="' + href + '" target="_blank" rel="noopener" style="text-decoration:none;color:inherit">' +
        '<span class="mg-ticker__dot mg-ticker__dot--' + dot + '"></span>' +
        label + ' <span class="mg-ticker__val">' + val + '</span> · ' +
        '<span class="mg-ticker__label">' + detail + '</span></a>';
    }).join('');
    inner.innerHTML = html + html;
  }

  function openMeteoFallback() {
    var pts = [
      { dot: 'agro', label: 'Quillota · Tº', lat: -32.8833, lon: -71.25, href: 'https://metgo-quillota.pages.dev', kind: 'meteo' },
      { dot: 'izaje', label: 'VENTORA · Viento 80 m', lat: -24.27, lon: -69.07, href: 'https://metgo-spati.pages.dev', kind: 'wind80' },
      { dot: 'aire', label: 'Copiapó · PM2.5', lat: -27.3668, lon: -70.3323, href: 'https://metgo-copiapo.pages.dev', kind: 'air' },
      { dot: 'outdoor', label: 'Paine · Tº', lat: -50.9417, lon: -72.9667, href: 'https://metgo-paine.pages.dev', kind: 'meteo' }
    ];
    return Promise.all(pts.map(function (p) {
      if (p.kind === 'air') {
        var u = 'https://air-quality-api.open-meteo.com/v1/air-quality?latitude=' + p.lat +
          '&longitude=' + p.lon + '&current=pm2_5,pm10';
        return fetch(u).then(function (r) { return r.json(); }).then(function (d) {
          var pm = d.current && d.current.pm2_5;
          return { dot: p.dot, label: p.label, val: pm != null ? (Math.round(pm * 10) / 10) + ' μg/m³' : '—', detail: 'Open-Meteo CAMS', href: p.href };
        }).catch(function () { return null; });
      }
      var vars = p.kind === 'wind80'
        ? 'current=wind_speed_10m&hourly=wind_speed_80m&forecast_days=1'
        : 'current=temperature_2m,wind_speed_10m';
      var u = 'https://api.open-meteo.com/v1/forecast?latitude=' + p.lat + '&longitude=' + p.lon + '&' + vars + '&wind_speed_unit=kmh';
      return fetch(u).then(function (r) { return r.json(); }).then(function (d) {
        if (p.kind === 'wind80') {
          var arr = (d.hourly && d.hourly.wind_speed_80m) || [];
          var v = arr.length ? arr[0] : (d.current && d.current.wind_speed_10m);
          return { dot: p.dot, label: p.label, val: v != null ? Math.round(v) + ' km/h' : '—', detail: 'Open-Meteo (fallback)', href: p.href };
        }
        var t = d.current && d.current.temperature_2m;
        var w = d.current && d.current.wind_speed_10m;
        return {
          dot: p.dot, label: p.label,
          val: t != null ? (Math.round(t * 10) / 10) + ' °C' : '—',
          detail: w != null ? ('Viento ' + Math.round(w) + ' km/h') : 'Open-Meteo',
          href: p.href
        };
      }).catch(function () { return null; });
    })).then(function (rows) { return rows.filter(Boolean); });
  }

  function load() {
    fetch(API, { credentials: 'omit' })
      .then(function (r) {
        if (!r.ok) throw new Error('ticker ' + r.status);
        return r.json();
      })
      .then(function (data) {
        if (data && data.items && data.items.length) {
          renderItems(data.items);
          return;
        }
        throw new Error('empty');
      })
      .catch(function () {
        openMeteoFallback().then(renderItems);
      });
  }

  load();
  setInterval(load, REFRESH_MS);
})();
</script>
<script>
(function () {
  var el = document.getElementById('mg-mjo-status');
  if (!el) return;
  fetch('https://metgo-mjo-chile.pages.dev/forecasts/metgo_bundle_latest.json')
    .then(function (r) { return r.ok ? r.json() : Promise.reject(r.status); })
    .then(function (b) {
      var phase = b.current_phase != null ? 'Fase ' + b.current_phase : '';
      var status = b.model_status || '';
      el.textContent = phase + (phase && status ? ' · ' : '') + status;
    })
    .catch(function () { el.textContent = 'A″ GO'; });
})();
</script>
"""


def footer_html() -> str:
    return f"""
  <div class="mg-footer-bar">
    <div>
      <p class="mg-footer-bar__text">Paneles en vivo · Agricultura · Izaje · Minería · Calidad del aire</p>
      <a href="{MAILTO}" class="mg-footer-bar__mail">{MAIL}</a>
    </div>
    <div class="mg-footer-bar__actions">
      <a href="{CONTACTO}" class="mg-footer-bar__btn" target="_blank" rel="noopener">Solicitar demo</a>
      <a href="https://metgo3d.com/planes/" class="mg-footer-bar__btn">Ver planes</a>
    </div>
  </div>
  <div class="mg-strip">
    <p>Piloto 15 días · <strong>Si no sirve para tu operación, no pagas.</strong></p>
  </div>
"""


def wrap(body: str, active: str = "", extra_head: str = "") -> str:
    css = load_css()
    return f"""<!-- METGO mg-page sobrio + ticker live · 2026-08-12 -->
<!-- wp:html -->
{extra_head}
<style>
{css}
</style>
<div class="mg-page">
{nav_html(active)}
{ticker_html()}
{body}
{footer_html()}
</div>
<script>
document.addEventListener('click', function(e) {{
  if (!e.target.closest('.mg-nav__cta-wrap')) {{
    document.querySelectorAll('.mg-nav__cta-wrap').forEach(function(w){{ w.classList.remove('is-open'); }});
  }}
}});
(function() {{
  var t = localStorage.getItem('mg-theme');
  if (t === 'light') document.querySelector('.mg-page').classList.add('mg-theme-light');
  window.mgToggleTheme = function() {{
    var p = document.querySelector('.mg-page');
    p.classList.toggle('mg-theme-light');
    localStorage.setItem('mg-theme', p.classList.contains('mg-theme-light') ? 'light' : 'dark');
  }};
}})();
</script>
{ticker_script()}
<!-- /wp:html -->
"""


def home_body() -> str:
    return f"""
  <section class="mg-hero">
    <p class="mg-eyebrow">Clima operacional · Chile</p>
    <h1 class="mg-hero__title">Evita pérdidas por clima<br>en <em>tu faena</em></h1>
    <p class="mg-hero__desc">
      Pronósticos hiperlocales para agricultura, minería e izaje.
      Si hay riesgo de helada o viento, te avisamos 12–24 h antes —
      no al día siguiente.
    </p>
    <div class="mg-hero__actions">
      <a href="{CONTACTO}" class="mg-btn--primary" target="_blank" rel="noopener">Solicitar demo gratis</a>
      <a href="https://metgo3d.com/planes/" class="mg-btn--ghost">Ver planes →</a>
      <a href="https://metgo3d.com/mjo_chile/" class="mg-btn--ghost">MJO Chile 7–90 d →</a>
    </div>
  </section>
  <hr class="mg-divider">
  <section class="mg-section" id="productos">
    <p class="mg-section__label">Productos disponibles</p>
    <p class="mg-section__subtitle">Cada panel tiene demo en vivo y piloto de 15 días. <span>Si no sirve, no pagas.</span></p>
    <div class="mg-products-grid">
      <div class="mg-card mg-card--agro">
        <span class="mg-badge mg-badge--agro">Agricultura</span>
        <p class="mg-card__title">Panel Quillota</p>
        <p class="mg-card__desc">Helada, riego y microclima del valle. Alerta anticipada 12–24 h antes por zona.</p>
        <p class="mg-card__price">Desde <strong>USD 99</strong>/mes</p>
        <div class="mg-card__links">
          <a href="{QUILLOTA}" class="mg-card-link mg-card-link--agro" target="_blank" rel="noopener">Panel en vivo →</a>
          <a href="https://metgo3d.com/agricultura-de-precision/" class="mg-card-link mg-card-link--agro">Más info</a>
        </div>
      </div>
      <div class="mg-card mg-card--izaje">
        <span class="mg-badge mg-badge--izaje">Izaje · Minería</span>
        <p class="mg-card__title">VENTORA · SPATI Izajes</p>
        <p class="mg-card__desc">Viento en altura, umbrales 26/31/36 km/h, alertas y PDF por operación.</p>
        <p class="mg-card__price">Desde <strong>USD 299</strong>/mes</p>
        <div class="mg-card__links">
          <a href="{SPATI}" class="mg-card-link mg-card-link--izaje" target="_blank" rel="noopener">Panel en vivo →</a>
          <a href="https://metgo3d.com/izaje-ventora/" class="mg-card-link mg-card-link--izaje">Más info</a>
        </div>
      </div>
      <div class="mg-card mg-card--aire">
        <span class="mg-badge mg-badge--aire">Calidad del aire</span>
        <p class="mg-card__title">Copiapó · Mantos Blancos</p>
        <p class="mg-card__desc">ICAP, episodios y semáforo de turno para cumplimiento DS 59 / DS 138.</p>
        <p class="mg-card__price">Desde <strong>USD 199</strong>/mes</p>
        <div class="mg-card__links">
          <a href="{COPIAPO}" class="mg-card-link mg-card-link--aire" target="_blank" rel="noopener">Copiapó →</a>
          <a href="{MANTOS}" class="mg-card-link mg-card-link--aire" target="_blank" rel="noopener">Mantos →</a>
        </div>
      </div>
      <div class="mg-card mg-card--outdoor">
        <span class="mg-badge mg-badge--outdoor">Terreno · Outdoor</span>
        <p class="mg-card__title">Panel Paine</p>
        <p class="mg-card__desc">Clima usable en ruta y operaciones outdoor. Viento, temperatura y visibilidad.</p>
        <p class="mg-card__price">Desde <strong>USD 49</strong>/mes</p>
        <div class="mg-card__links">
          <a href="{PAINE}" class="mg-card-link mg-card-link--outdoor" target="_blank" rel="noopener">Panel en vivo →</a>
        </div>
      </div>
      <div class="mg-card mg-card--agro">
        <span class="mg-badge mg-badge--agro">I+D · 7–90 días</span>
        <p class="mg-card__title">MJO Chile · ΨPSA-CL</p>
        <p class="mg-card__desc">Tendencia subestacional A″ + conformal. Régimen / terciles, no mm del día. Skill OOS CONFIRMADO h7/w1.</p>
        <p class="mg-card__price">Línea científica · <strong>A″ GO</strong></p>
        <div class="mg-card__links">
          <a href="https://metgo3d.com/mjo_chile/" class="mg-card-link mg-card-link--agro">Abrir MJO Chile →</a>
          <a href="https://metgo-mjo-chile.pages.dev/explorar" class="mg-card-link mg-card-link--agro" target="_blank" rel="noopener">Explorador</a>
        </div>
      </div>
    </div>
  </section>
  <hr class="mg-divider">
  <section class="mg-section" id="innovacion">
    <p class="mg-section__label">Innovación y Próximos Enfoques</p>
    <p class="mg-section__subtitle">Desarrollos tecnológicos en curso para abordar nuevos desafíos medioambientales.</p>
    <div class="mg-products-grid">
      <div class="mg-card mg-card--aire">
        <span class="mg-badge mg-badge--aire">I+D · Olores y SEIA</span>
        <p class="mg-card__title">Modelación con WRF</p>
        <p class="mg-card__desc">Uso del modelo WRF para procesos de informes requeridos por el SEIA respecto a la modelación y dispersión de olores.</p>
        <p class="mg-card__price"><strong>Próximamente</strong></p>
      </div>
      <div class="mg-card mg-card--agro">
        <span class="mg-badge mg-badge--agro">I+D · Sostenibilidad</span>
        <p class="mg-card__title">Huella de Carbono</p>
        <p class="mg-card__desc">Desarrollo de medición de huellas de carbono y proyecciones de cambio climático aplicadas a distintas industrias.</p>
        <p class="mg-card__price"><strong>Próximamente</strong></p>
      </div>
    </div>
  </section>
  <hr class="mg-divider">
  <section class="mg-section">
    <p class="mg-section__label">Planes ancla</p>
    <div class="mg-plans-grid">
      <div class="mg-plan">
        <p class="mg-plan__name">Campo · Agro</p>
        <p class="mg-plan__price">99</p>
        <p class="mg-plan__period">USD / mes</p>
        <a href="{CONTACTO}" class="mg-plan__link mg-plan__link--agro" target="_blank" rel="noopener">Solicitar acceso →</a>
      </div>
      <div class="mg-plan">
        <p class="mg-plan__name">Faena · Izaje / Minería</p>
        <p class="mg-plan__price">299</p>
        <p class="mg-plan__period">USD / mes</p>
        <a href="{CONTACTO}" class="mg-plan__link mg-plan__link--izaje" target="_blank" rel="noopener">Demo faena →</a>
      </div>
      <div class="mg-plan">
        <p class="mg-plan__name">Municipio · Aire</p>
        <p class="mg-plan__price">399</p>
        <p class="mg-plan__period">USD / mes</p>
        <a href="{CONTACTO}" class="mg-plan__link mg-plan__link--aire" target="_blank" rel="noopener">Pedir cotización →</a>
      </div>
    </div>
    <p class="mg-plans-note">Piloto 15 días · <a href="https://metgo3d.com/planes/">Ver detalle de planes →</a></p>
  </section>
  <hr class="mg-divider">
"""


def agro_body() -> str:
    return f"""
  <section class="mg-prod-hero">
    <div>
      <p class="mg-eyebrow" style="color:var(--mg-agro-text)">Agricultura de precisión · Quillota activo</p>
      <h1 class="mg-hero__title" style="margin-bottom:1rem">Control inteligente de heladas y microclima en predio</h1>
      <p class="mg-hero__desc">
        Modelos hiperlocales de temperatura, humedad y viento calibrados para la zona central de Chile.
        Alertas tempranas de helada, optimización de riego y recomendaciones operacionales al equipo de campo.
      </p>
      <div class="mg-hero__actions">
        <a href="{QUILLOTA}" class="mg-btn--primary mg-btn--agro" target="_blank" rel="noopener">Acceder al panel Quillota</a>
        <a href="{CONTACTO}" class="mg-btn--ghost" target="_blank" rel="noopener">Demo 15 días →</a>
      </div>
      <p class="mg-card__price" style="margin-top:1.25rem">Desde <strong>USD 99</strong>/mes · Piloto sin costo</p>
    </div>
    <div class="mg-readout" style="border-left:3px solid var(--mg-agro)">
      <p class="mg-eyebrow" style="color:var(--mg-agro-text);margin-bottom:0.35rem">Quillota · Valle del Aconcagua · En línea</p>
      <p class="mg-readout__status">Sin riesgo de helada</p>
      <p class="mg-readout__meta">T min proyectada: 11.9°C · Umbral crítico: 2°C</p>
      <div class="mg-readout__metrics">
        <div class="mg-metric"><p class="mg-metric__label">T media</p><p class="mg-metric__val mg-metric__val--soft">15.1°C</p></div>
        <div class="mg-metric"><p class="mg-metric__label">Humedad</p><p class="mg-metric__val">100%</p></div>
        <div class="mg-metric"><p class="mg-metric__label">Lluvia 7d</p><p class="mg-metric__val">70.2 mm</p></div>
      </div>
      <div class="mg-readout__flags">
        <span>● Helada: Sin riesgo</span>
        <span>● Riego: Humedad adecuada</span>
      </div>
    </div>
  </section>
  <hr class="mg-divider">
  <section class="mg-section">
    <p class="mg-section__label">Qué incluye</p>
    <div class="mg-products-grid">
      <div class="mg-card mg-card--agro"><p class="mg-card__title">Alerta de helada</p><p class="mg-card__desc">Aviso 12–24 h antes para tu zona, no solo la estación DMC más cercana.</p></div>
      <div class="mg-card mg-card--agro"><p class="mg-card__title">Riego y microclima</p><p class="mg-card__desc">Señales de humedad, temperatura y viento para decidir riego y labores.</p></div>
      <div class="mg-card mg-card--agro"><p class="mg-card__title">Panel + cuenta</p><p class="mg-card__desc">Acceso multi-usuario, piloto 15 días y planes Campo desde USD 99.</p></div>
    </div>
  </section>
  <hr class="mg-divider">
"""


def izaje_body() -> str:
    return f"""
  <section class="mg-prod-hero">
    <div>
      <p class="mg-eyebrow" style="color:var(--mg-izaje-text)">Producto · Izaje</p>
      <h1 class="mg-hero__title" style="margin-bottom:1rem">VENTORA — viento hiperlocal para izaje seguro</h1>
      <p class="mg-hero__desc">
        Semáforo operativo en el punto GPS de la faena. Pronóstico 72 h, umbrales 26/31/36 km/h,
        alertas y PDF con sello de tiempo para mandantes.
      </p>
      <div class="mg-hero__actions">
        <a href="{SPATI}" class="mg-btn--primary mg-btn--izaje" target="_blank" rel="noopener">Abrir panel en vivo</a>
        <a href="{CONTACTO}" class="mg-btn--ghost" target="_blank" rel="noopener">Pedir piloto 15 días →</a>
      </div>
      <p class="mg-card__price" style="margin-top:1.25rem">Desde <strong>USD 299</strong>/mes · Básico 299 · Pro 499 · Enterprise desde 1.199</p>
    </div>
    <div class="mg-readout" style="border-left:3px solid var(--mg-izaje)">
      <p class="mg-eyebrow" style="color:var(--mg-izaje-text);margin-bottom:0.35rem">VENTORA · Perfil de viento · En línea</p>
      <p class="mg-readout__status">Precaución</p>
      <p class="mg-readout__meta">Viento 29 km/h · Umbral suspensión 31 km/h</p>
      <div class="mg-readout__metrics">
        <div class="mg-metric"><p class="mg-metric__label">10 m</p><p class="mg-metric__val">22 km/h</p></div>
        <div class="mg-metric"><p class="mg-metric__label">80 m</p><p class="mg-metric__val" style="color:var(--mg-izaje-text)">29 km/h</p></div>
        <div class="mg-metric"><p class="mg-metric__label">100 m</p><p class="mg-metric__val">31 km/h</p></div>
      </div>
      <div class="mg-readout__flags">
        <span style="color:var(--mg-izaje-text)">● ≥26 precaución</span>
        <span style="color:var(--mg-izaje-text)">● ≥31 suspensión recomendada</span>
      </div>
    </div>
  </section>
  <hr class="mg-divider">
"""


def mineria_body() -> str:
    return f"""
  <section class="mg-prod-hero">
    <div>
      <p class="mg-eyebrow" style="color:var(--mg-aire-text)">Minería · Alta montaña · Calidad del aire</p>
      <h1 class="mg-hero__title" style="margin-bottom:1rem">Seguridad operativa y cumplimiento ambiental</h1>
      <p class="mg-hero__desc">
        Nowcasting, semáforo de turno y monitoreo de calidad del aire para faenas.
        Paneles Copiapó y Mantos Blancos listos para operar.
      </p>
      <div class="mg-hero__actions">
        <a href="{COPIAPO}" class="mg-btn--primary mg-btn--aire" target="_blank" rel="noopener">Ver panel Copiapó</a>
        <a href="{MANTOS}" class="mg-btn--ghost" target="_blank" rel="noopener">Mantos Blancos →</a>
      </div>
      <p class="mg-card__price" style="margin-top:1.25rem">Desde <strong>USD 199</strong>/mes · Municipio desde USD 399</p>
    </div>
    <div class="mg-readout" style="border-left:3px solid var(--mg-aire)">
      <p class="mg-eyebrow" style="color:var(--mg-aire-text);margin-bottom:0.35rem">Copiapó · Cuenca Atacama · En línea</p>
      <p class="mg-readout__status">ICAP: Buena</p>
      <p class="mg-readout__meta">MP10 dentro de norma · estaciones activas</p>
      <div class="mg-readout__metrics">
        <div class="mg-metric"><p class="mg-metric__label">MP10</p><p class="mg-metric__val" style="color:var(--mg-aire-text)">38 μg/m³</p></div>
        <div class="mg-metric"><p class="mg-metric__label">Norma 24h</p><p class="mg-metric__val">150 μg/m³</p></div>
        <div class="mg-metric"><p class="mg-metric__label">Estado</p><p class="mg-metric__val">OK</p></div>
      </div>
    </div>
  </section>
  <hr class="mg-divider">
  <section class="mg-section">
    <p class="mg-section__label">También para izaje</p>
    <p class="mg-section__subtitle">El viento en faena se cubre con <a href="https://metgo3d.com/izaje-ventora/" style="color:var(--mg-izaje-text)">VENTORA</a> desde USD 299/mes.</p>
  </section>
  <hr class="mg-divider">
"""


TABLER_CSS = (
    '<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@tabler/icons-webfont@3.34.0/'
    'dist/tabler-icons.min.css" crossorigin="anonymous">'
)


def planes_body() -> str:
    return f"""
  <h2 class="mg-sr-only">Página de planes METGO3D - comparación detallada por sector con precios y features técnicas</h2>

  <section class="plans-hero">
    <p class="eyebrow">Planes y precios</p>
    <h1>Inteligencia climática<br>para cada operación</h1>
    <p>Elige el plan según tu sector. Todos incluyen panel en vivo, alertas anticipadas y piloto de 15 días sin costo.</p>
    <div class="billing-toggle">
      <span class="toggle-label active" id="lbl-mes">Mensual</span>
      <div class="toggle-wrap" id="toggle" role="switch" aria-checked="false" tabindex="0" onclick="window.mgFlipBilling()" onkeydown="if(event.key==='Enter'||event.key===' '){{event.preventDefault();window.mgFlipBilling()}}">
        <div class="toggle-knob"></div>
      </div>
      <span class="toggle-label" id="lbl-año">Anual</span>
      <span class="toggle-badge" id="discount-badge">−15%</span>
    </div>
  </section>

  <hr class="mg-divider">

  <section class="plans-detail-sec">
    <div class="plans-detail-grid">

      <div class="plan-card agro">
        <p class="plan-sector agro">Agricultura</p>
        <p class="plan-name">Campo</p>
        <p class="plan-tagline">Helada, riego y microclima para valles agrícolas de Chile central.</p>
        <div class="plan-price-block">
          <div class="plan-price">
            <span class="plan-currency">USD</span>
            <span class="plan-amount" id="p-agro">99</span>
            <span class="plan-period">/mes</span>
          </div>
          <p class="plan-annual-note" id="note-agro">Facturado USD 1,010/año</p>
        </div>
        <div class="feat-group">
          <p class="feat-group-label">Pronóstico</p>
          <div class="feat-row"><i class="ti ti-clock feat-icon agro" aria-hidden="true"></i><span class="feat-text"><strong>Horizonte 72 h</strong> · actualización cada 3 h</span></div>
          <div class="feat-row"><i class="ti ti-map-pin feat-icon agro" aria-hidden="true"></i><span class="feat-text"><strong>Resolución 1 km²</strong> · microclima por zona</span></div>
          <div class="feat-row"><i class="ti ti-thermometer feat-icon agro" aria-hidden="true"></i><span class="feat-text">Tº suelo, Tº bulbo, humedad relativa, ETo</span></div>
        </div>
        <div class="feat-group">
          <p class="feat-group-label">Alertas</p>
          <div class="feat-row"><i class="ti ti-bell feat-icon agro" aria-hidden="true"></i><span class="feat-text"><strong>Alerta helada</strong> 12–24 h antes, umbral configurable</span></div>
          <div class="feat-row"><i class="ti ti-droplet feat-icon agro" aria-hidden="true"></i><span class="feat-text">Alerta lluvia y riesgo de riego ineficiente</span></div>
          <div class="feat-row"><i class="ti ti-mail feat-icon agro" aria-hidden="true"></i><span class="feat-text">Email + SMS + webhook</span></div>
        </div>
        <div class="feat-group">
          <p class="feat-group-label">Panel y acceso</p>
          <div class="feat-row"><i class="ti ti-chart-line feat-icon agro" aria-hidden="true"></i><span class="feat-text">Panel web en vivo · histórico 12 meses</span></div>
          <div class="feat-row"><i class="ti ti-users feat-icon agro" aria-hidden="true"></i><span class="feat-text">Hasta <strong>3 usuarios</strong></span></div>
          <div class="feat-row"><i class="ti ti-code feat-icon agro" aria-hidden="true"></i><span class="feat-text">API REST JSON (1,000 calls/mes)</span></div>
        </div>
        <div class="plan-tags">
          <span class="tag agro">Valle Quillota</span>
          <span class="tag agro">Aconcagua</span>
          <span class="tag agro">Maipo</span>
        </div>
        <a href="{CONTACTO}" class="plan-cta agro" target="_blank" rel="noopener">Iniciar piloto gratis</a>
        <p class="plan-cta-sub">15 días sin costo · sin tarjeta</p>
      </div>

      <div class="plan-card izaje">
        <p class="plan-sector izaje">Izaje · Minería alta</p>
        <p class="plan-name">Faena</p>
        <p class="plan-tagline">Viento en altura y umbrales críticos para operaciones de izaje y trabajos en cordillera.</p>
        <div class="plan-price-block">
          <div class="plan-price">
            <span class="plan-currency">USD</span>
            <span class="plan-amount" id="p-izaje">299</span>
            <span class="plan-period">/mes</span>
          </div>
          <p class="plan-annual-note" id="note-izaje">Facturado USD 3,050/año</p>
        </div>
        <div class="feat-group">
          <p class="feat-group-label">Pronóstico</p>
          <div class="feat-row"><i class="ti ti-clock feat-icon izaje" aria-hidden="true"></i><span class="feat-text"><strong>Horizonte 48 h</strong> · actualización cada 1 h</span></div>
          <div class="feat-row"><i class="ti ti-mountain feat-icon izaje" aria-hidden="true"></i><span class="feat-text"><strong>Perfil vertical</strong> 10/50/100/150 m sobre suelo</span></div>
          <div class="feat-row"><i class="ti ti-wind feat-icon izaje" aria-hidden="true"></i><span class="feat-text">Viento sostenido, ráfaga, dirección, turbulencia</span></div>
        </div>
        <div class="feat-group">
          <p class="feat-group-label">Alertas operacionales</p>
          <div class="feat-row"><i class="ti ti-alert-triangle feat-icon izaje" aria-hidden="true"></i><span class="feat-text"><strong>Umbrales 26 / 31 / 36 km/h</strong> configurables por grúa</span></div>
          <div class="feat-row"><i class="ti ti-file-text feat-icon izaje" aria-hidden="true"></i><span class="feat-text">PDF de turno con firma digital del meteorólogo</span></div>
          <div class="feat-row"><i class="ti ti-mail feat-icon izaje" aria-hidden="true"></i><span class="feat-text">Email + SMS + llamada automática en alerta roja</span></div>
        </div>
        <div class="feat-group">
          <p class="feat-group-label">Panel y acceso</p>
          <div class="feat-row"><i class="ti ti-chart-line feat-icon izaje" aria-hidden="true"></i><span class="feat-text">Panel SPATI · histórico 24 meses · exportación CSV</span></div>
          <div class="feat-row"><i class="ti ti-users feat-icon izaje" aria-hidden="true"></i><span class="feat-text">Hasta <strong>10 usuarios</strong> · roles operador/supervisor</span></div>
          <div class="feat-row"><i class="ti ti-code feat-icon izaje" aria-hidden="true"></i><span class="feat-text">API REST JSON (5,000 calls/mes) + Webhooks</span></div>
        </div>
        <div class="plan-tags">
          <span class="tag izaje">VENTORA</span>
          <span class="tag izaje">SPATI</span>
          <span class="tag izaje">Alta cordillera</span>
        </div>
        <a href="{SPATI}" class="plan-cta izaje" target="_blank" rel="noopener">Solicitar demo faena</a>
        <p class="plan-cta-sub">15 días sin costo · soporte prioritario</p>
      </div>

      <div class="plan-card aire">
        <p class="plan-sector aire">Calidad del aire</p>
        <p class="plan-name">Municipio</p>
        <p class="plan-tagline">ICAP, episodios críticos y cumplimiento normativo DS 59 / DS 138 para minería y municipios.</p>
        <div class="plan-price-block">
          <div class="plan-price">
            <span class="plan-currency">USD</span>
            <span class="plan-amount" id="p-aire">399</span>
            <span class="plan-period">/mes</span>
          </div>
          <p class="plan-annual-note" id="note-aire">Facturado USD 4,070/año</p>
        </div>
        <div class="feat-group">
          <p class="feat-group-label">Monitoreo</p>
          <div class="feat-row"><i class="ti ti-clock feat-icon aire" aria-hidden="true"></i><span class="feat-text"><strong>Datos en tiempo real</strong> · actualización cada 15 min</span></div>
          <div class="feat-row"><i class="ti ti-map-2 feat-icon aire" aria-hidden="true"></i><span class="feat-text">Mapa airshed con <strong>hasta 10 puntos</strong> de medición</span></div>
          <div class="feat-row"><i class="ti ti-atom feat-icon aire" aria-hidden="true"></i><span class="feat-text">PM2.5, PM10, CO, SO₂, NOₓ, ICAP horario</span></div>
        </div>
        <div class="feat-group">
          <p class="feat-group-label">Alertas y cumplimiento</p>
          <div class="feat-row"><i class="ti ti-traffic-lights feat-icon aire" aria-hidden="true"></i><span class="feat-text"><strong>Semáforo de turno</strong> · Pre-emergencia · Emergencia</span></div>
          <div class="feat-row"><i class="ti ti-certificate feat-icon aire" aria-hidden="true"></i><span class="feat-text">Informe diario DS 59 / DS 138 listo para Seremi</span></div>
          <div class="feat-row"><i class="ti ti-mail feat-icon aire" aria-hidden="true"></i><span class="feat-text">Alerta inmediata a jefe de turno + autoridad</span></div>
        </div>
        <div class="feat-group">
          <p class="feat-group-label">Panel y acceso</p>
          <div class="feat-row"><i class="ti ti-chart-line feat-icon aire" aria-hidden="true"></i><span class="feat-text">Panel público + privado · histórico 36 meses</span></div>
          <div class="feat-row"><i class="ti ti-users feat-icon aire" aria-hidden="true"></i><span class="feat-text">Usuarios <strong>ilimitados</strong> · acceso por rol</span></div>
          <div class="feat-row"><i class="ti ti-code feat-icon aire" aria-hidden="true"></i><span class="feat-text">API REST + exportación automática SMA</span></div>
        </div>
        <div class="plan-tags">
          <span class="tag aire">Copiapó</span>
          <span class="tag aire">Mantos Blancos</span>
          <span class="tag aire">DS 59 / DS 138</span>
        </div>
        <a href="{CONTACTO}" class="plan-cta aire" target="_blank" rel="noopener">Pedir cotización</a>
        <p class="plan-cta-sub">Incluye instalación y calibración</p>
      </div>

      <div class="plan-card out">
        <p class="plan-sector out">Terreno · Outdoor</p>
        <p class="plan-name">Ruta</p>
        <p class="plan-tagline">Clima operacional para trabajo en terreno, expediciones y operaciones outdoor.</p>
        <div class="plan-price-block">
          <div class="plan-price">
            <span class="plan-currency">USD</span>
            <span class="plan-amount" id="p-out">49</span>
            <span class="plan-period">/mes</span>
          </div>
          <p class="plan-annual-note" id="note-out">Facturado USD 500/año</p>
        </div>
        <div class="feat-group">
          <p class="feat-group-label">Pronóstico</p>
          <div class="feat-row"><i class="ti ti-clock feat-icon out" aria-hidden="true"></i><span class="feat-text"><strong>Horizonte 48 h</strong> · actualización cada 6 h</span></div>
          <div class="feat-row"><i class="ti ti-map-pin feat-icon out" aria-hidden="true"></i><span class="feat-text">Punto a punto por ruta o coordenada GPS</span></div>
          <div class="feat-row"><i class="ti ti-wind feat-icon out" aria-hidden="true"></i><span class="feat-text">Viento, Tº, precipitación, visibilidad, índice UV</span></div>
        </div>
        <div class="feat-group">
          <p class="feat-group-label">Alertas</p>
          <div class="feat-row"><i class="ti ti-bell feat-icon out" aria-hidden="true"></i><span class="feat-text">Alerta viento fuerte y precipitación intensa</span></div>
          <div class="feat-row"><i class="ti ti-mail feat-icon out" aria-hidden="true"></i><span class="feat-text">Email + notificación push (app móvil)</span></div>
        </div>
        <div class="feat-group">
          <p class="feat-group-label">Acceso</p>
          <div class="feat-row"><i class="ti ti-chart-line feat-icon out" aria-hidden="true"></i><span class="feat-text">Panel web + app móvil · histórico 3 meses</span></div>
          <div class="feat-row"><i class="ti ti-users feat-icon out" aria-hidden="true"></i><span class="feat-text">Hasta <strong>2 usuarios</strong></span></div>
        </div>
        <div class="plan-tags">
          <span class="tag out">Paine</span>
          <span class="tag out">Ruta</span>
          <span class="tag out">Outdoor</span>
        </div>
        <a href="{PAINE}" class="plan-cta out" target="_blank" rel="noopener">Iniciar piloto gratis</a>
        <p class="plan-cta-sub">15 días sin costo · sin tarjeta</p>
      </div>

    </div>
  </section>

  <hr class="mg-divider">

  <section class="compare-sec">
    <p class="compare-label">Comparación de planes</p>
    <div style="overflow-x:auto">
      <table class="compare-table">
        <thead>
          <tr>
            <th>Característica</th>
            <th>Campo · Agro</th>
            <th>Faena · Izaje</th>
            <th>Municipio · Aire</th>
            <th>Ruta · Outdoor</th>
          </tr>
        </thead>
        <tbody>
          <tr><td>Precio base (USD/mes)</td><td>99</td><td>299</td><td>399</td><td>49</td></tr>
          <tr><td>Horizonte de pronóstico</td><td>72 h</td><td>48 h</td><td>Tiempo real</td><td>48 h</td></tr>
          <tr><td>Actualización</td><td>Cada 3 h</td><td>Cada 1 h</td><td>Cada 15 min</td><td>Cada 6 h</td></tr>
          <tr><td>Resolución espacial</td><td>1 km²</td><td>Perfil vertical</td><td>Punto fijo</td><td>GPS</td></tr>
          <tr><td>Alerta por email</td><td class="yes">✓</td><td class="yes">✓</td><td class="yes">✓</td><td class="yes">✓</td></tr>
          <tr><td>Alerta por SMS</td><td class="yes">✓</td><td class="yes">✓</td><td class="yes">✓</td><td class="no">—</td></tr>
          <tr><td>Llamada automática alerta roja</td><td class="no">—</td><td class="yes">✓</td><td class="yes">✓</td><td class="no">—</td></tr>
          <tr><td>PDF de turno firmado</td><td class="no">—</td><td class="yes">✓</td><td class="yes">✓</td><td class="no">—</td></tr>
          <tr><td>Acceso API REST</td><td>1,000 calls/mes</td><td>5,000 calls/mes</td><td>Ilimitado</td><td class="no">—</td></tr>
          <tr><td>Histórico de datos</td><td>12 meses</td><td>24 meses</td><td>36 meses</td><td>3 meses</td></tr>
          <tr><td>Usuarios incluidos</td><td>3</td><td>10</td><td>Ilimitados</td><td>2</td></tr>
          <tr><td>Soporte</td><td>Email 48 h</td><td>Prioritario 4 h</td><td>Dedicado 1 h</td><td>Email 72 h</td></tr>
          <tr><td>Piloto gratuito</td><td>15 días</td><td>15 días</td><td>Instalación incluida</td><td>15 días</td></tr>
        </tbody>
      </table>
    </div>
  </section>

  <hr class="mg-divider">

  <div class="guarantee">
    <i class="ti ti-shield-check guarantee-icon" aria-hidden="true"></i>
    <p><strong>Piloto 15 días sin riesgo.</strong> Si el sistema no sirve para tu operación específica, no pagas. Sin letra chica, sin cargos automáticos. Cada piloto incluye una reunión de configuración con el equipo técnico para adaptar los umbrales a tu faena.</p>
  </div>

  <hr class="mg-divider">

  <div class="plans-custom-bar">
    <p>¿Necesitas algo distinto? Armamos planes a medida para flotas, municipios y grandes faenas.</p>
    <a href="{MAILTO}">Escribir a {MAIL} →</a>
  </div>

  <hr class="mg-divider">

<script>
(function () {{
  var anual = false;
  var precios = {{agro:[99,1010], izaje:[299,3050], aire:[399,4070], out:[49,500]}};
  var notas = {{
    agro:'Facturado USD 1,010/año',
    izaje:'Facturado USD 3,050/año',
    aire:'Facturado USD 4,070/año',
    out:'Facturado USD 500/año'
  }};
  window.mgFlipBilling = function () {{
    anual = !anual;
    var t = document.getElementById('toggle');
    if (t) {{
      t.classList.toggle('on', anual);
      t.setAttribute('aria-checked', anual ? 'true' : 'false');
    }}
    var lm = document.getElementById('lbl-mes');
    var la = document.getElementById('lbl-año');
    var badge = document.getElementById('discount-badge');
    if (lm) lm.classList.toggle('active', !anual);
    if (la) la.classList.toggle('active', anual);
    if (badge) badge.style.opacity = anual ? '1' : '0.4';
    ['agro','izaje','aire','out'].forEach(function (k) {{
      var el = document.getElementById('p-' + k);
      var note = document.getElementById('note-' + k);
      if (!el || !note) return;
      if (anual) {{
        el.textContent = Math.round(precios[k][1] / 12);
        note.style.opacity = '1';
        note.textContent = notas[k];
      }} else {{
        el.textContent = precios[k][0];
        note.style.opacity = '0';
      }}
    }});
  }};
}})();
</script>
"""


def contacto_body() -> str:
    return f"""
  <section class="mg-hero" style="padding-bottom:0">
    <p class="mg-eyebrow">Contacto / Demo</p>
    <h1 class="mg-hero__title">Hablemos de tu faena</h1>
    <p class="mg-hero__desc">Respondemos a <strong style="color:var(--mg-white);font-weight:500">{MAIL}</strong>. Incluye nombre, empresa, sector y zona.</p>
  </section>

  <section class="mg-section">
    <div style="display:flex;flex-wrap:wrap;gap:24px;align-items:flex-start">
      <!-- Formulario -->
      <div style="flex:2;min-width:300px;background:#161b22;border:1px solid rgba(255,255,255,0.07);border-radius:14px;padding:36px 32px">
        <h2 style="color:#ffffff;font-size:20px;font-weight:800;margin:0 0 8px;font-family:var(--mg-serif, 'DM Serif Display', serif)">Cuéntanos tu desafío</h2>
        <p style="color:#64748b;font-size:13px;margin:0 0 24px">Respondemos en menos de 48 horas hábiles.</p>
        <form action="https://formspree.io/f/mjybkaon" method="POST" style="display:flex;flex-direction:column;gap:14px;font-family:var(--mg-sans, 'DM Sans', sans-serif)">
          <div style="display:flex;flex-wrap:wrap;gap:14px">
            <div style="flex:1;min-width:180px">
              <label style="display:block;color:#475569;font-size:10px;font-weight:700;letter-spacing:1px;text-transform:uppercase;margin-bottom:6px">Nombre</label>
              <input type="text" name="nombre" required placeholder="Tu nombre"
                style="width:100%;background:#0d1117;border:1px solid rgba(255,255,255,0.1);border-radius:6px;color:#e2e8f0;font-size:14px;padding:10px 14px;box-sizing:border-box;outline:none">
            </div>
            <div style="flex:1;min-width:180px">
              <label style="display:block;color:#475569;font-size:10px;font-weight:700;letter-spacing:1px;text-transform:uppercase;margin-bottom:6px">Empresa / Organización</label>
              <input type="text" name="empresa" placeholder="Empresa u organización"
                style="width:100%;background:#0d1117;border:1px solid rgba(255,255,255,0.1);border-radius:6px;color:#e2e8f0;font-size:14px;padding:10px 14px;box-sizing:border-box;outline:none">
            </div>
          </div>
          <div>
            <label style="display:block;color:#475569;font-size:10px;font-weight:700;letter-spacing:1px;text-transform:uppercase;margin-bottom:6px">Email</label>
            <input type="email" name="email" required placeholder="tu@empresa.cl"
              style="width:100%;background:#0d1117;border:1px solid rgba(255,255,255,0.1);border-radius:6px;color:#e2e8f0;font-size:14px;padding:10px 14px;box-sizing:border-box;outline:none">
          </div>
          <div>
            <label style="display:block;color:#475569;font-size:10px;font-weight:700;letter-spacing:1px;text-transform:uppercase;margin-bottom:6px">Sector</label>
            <select name="sector"
              style="width:100%;background:#0d1117;border:1px solid rgba(255,255,255,0.1);border-radius:6px;color:#e2e8f0;font-size:14px;padding:10px 14px;box-sizing:border-box;outline:none">
              <option value="" style="background:#0d1117">Selecciona tu sector</option>
              <option value="mineria" style="background:#0d1117">Minería / Alta montaña</option>
              <option value="agricultura" style="background:#0d1117">Agricultura de precisión</option>
              <option value="calidad-aire" style="background:#0d1117">Calidad del aire / Ambiental</option>
              <option value="izaje" style="background:#0d1117">Izaje / Construcción</option>
              <option value="hidrico" style="background:#0d1117">Recursos hídricos</option>
              <option value="otro" style="background:#0d1117">Otro</option>
            </select>
          </div>
          <div>
            <label style="display:block;color:#475569;font-size:10px;font-weight:700;letter-spacing:1px;text-transform:uppercase;margin-bottom:6px">Mensaje</label>
            <textarea name="mensaje" required rows="4" placeholder="Describe tu desafío operativo o lo que necesitas..."
              style="width:100%;background:#0d1117;border:1px solid rgba(255,255,255,0.1);border-radius:6px;color:#e2e8f0;font-size:14px;padding:10px 14px;box-sizing:border-box;outline:none;resize:vertical"></textarea>
          </div>
          <input type="text" name="_gotcha" style="display:none">
          <input type="hidden" name="_next" value="https://metgo3d.com/contacto/?enviado=1">
          <button type="submit"
            style="background:#3D9B72;color:#ffffff;border:none;border-radius:6px;padding:13px 28px;font-weight:700;font-size:14px;cursor:pointer;text-align:center">
            Enviar mensaje →
          </button>
        </form>
      </div>

      <!-- Datos de contacto y redes -->
      <div style="flex:1;min-width:240px;display:flex;flex-direction:column;gap:12px;font-family:var(--mg-sans, 'DM Sans', sans-serif)">
        <div style="background:#161b22;border:1px solid rgba(255,255,255,0.07);border-left:3px solid #3D9B72;border-radius:10px;padding:20px">
          <p style="color:#3D9B72;font-size:9px;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;margin:0 0 8px">Email directo</p>
          <p style="color:#e2e8f0;font-size:14px;font-weight:600;margin:0 0 4px">
            <a href="mailto:{MAIL}" style="color:#e2e8f0;text-decoration:none">{MAIL}</a>
          </p>
          <p style="color:#475569;font-size:12px;margin:0">Respuesta en 48 h hábiles</p>
        </div>
        <div style="background:#161b22;border:1px solid rgba(255,255,255,0.07);border-left:3px solid #3b82f6;border-radius:10px;padding:20px">
          <p style="color:#3b82f6;font-size:9px;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;margin:0 0 8px">LinkedIn</p>
          <a href="https://www.linkedin.com/in/metgo3d/" target="_blank" rel="noopener"
            style="display:inline-block;color:#7dd3fc;font-size:14px;font-weight:600;text-decoration:none;margin-bottom:4px">linkedin.com/in/metgo3d</a>
          <p style="color:#475569;font-size:12px;margin:0">Actualizaciones de producto</p>
        </div>
      </div>
    </div>
  </section>
  <hr class="mg-divider">
"""


def nosotros_body() -> str:
    return f"""
<style>
.mg-nosotros-wrapper {{
  --bg: #060E1A; --border: #1B2D42; --card: #090F1B; --text: #D6E4F0; --soft: #6B83A0; --white: #EBF2FA;
  --agro: #3D9B72; --agro-t: #112A1D; --agro-b: #1A3D27; --agro-tx: #7ECFAA; --agro-br: #2A5C3A;
  --izaje: #C07D3A; --izaje-t: #271A0A; --izaje-b: #352009; --izaje-tx: #E8A860; --izaje-br: #4A3015;
  --aire: #4A7DC9; --aire-t: #101D35; --aire-b: #112040; --aire-tx: #7EAAEE; --aire-br: #1E3A6A;
  --out: #8B6FBA; --out-t: #1C1430; --out-b: #241540; --out-tx: #B49ADE; --out-br: #3A2565;
  --sans: 'DM Sans', sans-serif; --serif: 'DM Serif Display', serif;
  font-family: var(--sans); color: var(--text); line-height: 1.5;
}}
.mg-nosotros-wrapper * {{ box-sizing: border-box; margin: 0; padding: 0; }}
.mg-nosotros-wrapper a {{ text-decoration: none; }}
.mg-nosotros-wrapper .mg-sec {{ padding: 3rem 2rem; max-width: 960px; margin: 0 auto; }}
.mg-nosotros-wrapper .mg-sec-label {{ font-size: 10px; letter-spacing: .2em; color: var(--soft); text-transform: uppercase; margin-bottom: .4rem; }}
.mg-nosotros-wrapper .mg-sec-sub {{ font-size: 14px; color: var(--soft); margin-bottom: 2rem; font-weight: 300; line-height: 1.7; }}
.mg-nosotros-wrapper .mg-sec-sub span {{ color: var(--agro-tx); }}
.mg-mision-block {{ border-left: 2.5px solid var(--agro); padding: 1.25rem 1.5rem; background: var(--agro-t); margin-bottom: 2rem; }}
.mg-mision-block p {{ font-family: var(--serif); font-size: 1.1rem; font-weight: 400; color: var(--white); line-height: 1.7; font-style: italic; }}
.mg-mision-block cite {{ display: block; font-size: 11px; color: var(--agro-tx); letter-spacing: .1em; text-transform: uppercase; margin-top: .75rem; font-style: normal; }}
.mg-pilares-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); gap: 1px; background: var(--border); border: .5px solid var(--border); border-radius: 8px; overflow: hidden; }}
.mg-pilar {{ padding: 1.5rem 1.4rem; border-top: 2.5px solid transparent; background: var(--card); }}
.mg-pilar.mg-op {{ background: var(--agro-t); border-top-color: var(--agro); }}
.mg-pilar.mg-id {{ background: var(--aire-t); border-top-color: var(--aire); }}
.mg-pilar.mg-pr {{ background: var(--out-t); border-top-color: var(--out); }}
.mg-pilar-icon {{ font-size: 18px; margin-bottom: .65rem; display: block; }}
.mg-pilar-icon.mg-op {{ color: var(--agro-tx); }}
.mg-pilar-icon.mg-id {{ color: var(--aire-tx); }}
.mg-pilar-icon.mg-pr {{ color: var(--out-tx); }}
.mg-pilar-sector {{ font-size: 9px; letter-spacing: .18em; text-transform: uppercase; font-weight: 600; margin-bottom: .4rem; }}
.mg-pilar-sector.mg-op {{ color: var(--agro-tx); }}
.mg-pilar-sector.mg-id {{ color: var(--aire-tx); }}
.mg-pilar-sector.mg-pr {{ color: var(--out-tx); }}
.mg-pilar h3 {{ font-size: 14px; font-weight: 500; color: var(--white); margin-bottom: .5rem; line-height: 1.3; font-family: var(--sans); }}
.mg-pilar p {{ font-size: 12px; color: var(--soft); line-height: 1.65; font-weight: 300; }}
.mg-pilar a {{ color: var(--aire-tx); text-decoration: none; border-bottom: .5px solid var(--aire-br); }}
.mg-stack-sec {{ padding: 3rem 2rem; background: #050C17; border-top: .5px solid var(--border); border-bottom: .5px solid var(--border); }}
.mg-stack-inner {{ max-width: 960px; margin: 0 auto; }}
.mg-stack-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 1px; background: var(--border); border: .5px solid var(--border); border-radius: 8px; overflow: hidden; margin-top: 1.75rem; }}
.mg-stack-item {{ background: var(--card); padding: 1.1rem 1.25rem; }}
.mg-stack-item-icon {{ font-size: 16px; margin-bottom: .5rem; display: block; }}
.mg-stack-item-icon.mg-agro {{ color: var(--agro-tx); }}
.mg-stack-item-icon.mg-aire {{ color: var(--aire-tx); }}
.mg-stack-item-icon.mg-izaje {{ color: var(--izaje-tx); }}
.mg-stack-item-icon.mg-out {{ color: var(--out-tx); }}
.mg-stack-item-name {{ font-size: 12px; font-weight: 500; color: var(--white); margin-bottom: .2rem; }}
.mg-stack-item-desc {{ font-size: 11px; color: var(--soft); font-weight: 300; line-height: 1.5; }}
.mg-principios-list {{ border: .5px solid var(--border); border-radius: 8px; overflow: hidden; margin-top: 1.75rem; }}
.mg-principio {{ display: flex; align-items: flex-start; gap: 1rem; padding: 1rem 1.25rem; border-bottom: .5px solid var(--border); background: var(--card); }}
.mg-principio:last-child {{ border-bottom: none; }}
.mg-principio:hover {{ background: #0C1829; }}
.mg-pr-num {{ font-family: var(--serif); font-size: 1.1rem; color: var(--border); flex-shrink: 0; width: 24px; margin-top: 2px; }}
.mg-pr-title {{ font-size: 13px; font-weight: 500; color: var(--white); margin-bottom: .2rem; }}
.mg-pr-desc {{ font-size: 12px; color: var(--soft); line-height: 1.6; font-weight: 300; }}
.mg-equipo-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1px; background: var(--border); border: .5px solid var(--border); border-radius: 8px; overflow: hidden; margin-top: 1.75rem; }}
.mg-member {{ background: var(--card); padding: 1.25rem 1.4rem; }}
.mg-member-avatar {{ width: 36px; height: 36px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 13px; font-weight: 500; margin-bottom: .75rem; flex-shrink: 0; }}
.mg-member-avatar.mg-ml {{ background: var(--agro-b); color: var(--agro-tx); }}
.mg-member-avatar.mg-mt {{ background: var(--aire-b); color: var(--aire-tx); }}
.mg-member-name {{ font-size: 13px; font-weight: 500; color: var(--white); margin-bottom: .15rem; }}
.mg-member-role {{ font-size: 11px; color: var(--soft); margin-bottom: .6rem; font-weight: 300; }}
.mg-member-tags {{ display: flex; flex-wrap: wrap; gap: 3px; }}
.mg-member-tag {{ font-size: 10px; padding: 2px 6px; border-radius: 2px; border: .5px solid; }}
.mg-member-tag.mg-a {{ color: var(--agro-tx); border-color: var(--agro-br); background: var(--agro-b); }}
.mg-member-tag.mg-b {{ color: var(--aire-tx); border-color: var(--aire-br); background: var(--aire-b); }}
.mg-member-tag.mg-c {{ color: var(--out-tx); border-color: var(--out-br); background: var(--out-b); }}
.mg-cta-strip {{ padding: 3rem 2rem; max-width: 960px; margin: 0 auto; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 1.5rem; }}
.mg-cta-strip-text h3 {{ font-family: var(--serif); font-size: 1.3rem; font-weight: 400; color: var(--white); margin-bottom: .3rem; }}
.mg-cta-strip-text p {{ font-size: 13px; color: var(--soft); font-weight: 300; }}
.mg-cta-strip-actions {{ display: flex; gap: .6rem; flex-wrap: wrap; }}
.mg-nosotros-wrapper h1 {{ font-family: var(--serif); font-size: clamp(1.9rem, 4.5vw, 3rem); font-weight: 400; color: var(--white); line-height: 1.15; margin-bottom: 1rem; }}
.mg-nosotros-wrapper h1 em {{ font-style: italic; color: var(--agro-tx); }}
.mg-nosotros-wrapper .mg-hero-desc {{ font-size: 14px; color: var(--soft); line-height: 1.8; max-width: 560px; margin-bottom: 2rem; font-weight: 300; }}
</style>

<div class="mg-nosotros-wrapper">
  <section class="mg-hero" style="padding:4rem 2rem 3.5rem;max-width:820px;margin:0 auto">
    <p class="mg-eyebrow" style="font-size:10px;letter-spacing:.2em;color:var(--soft);text-transform:uppercase;margin-bottom:1rem">METGO3D SpA · Nosotros</p>
    <h1>Inteligencia climática<br>construida para <em>Chile</em></h1>
    <p class="mg-hero-desc">Los sistemas globales no están pensados para Atacama, Aconcagua o el Valle Central. METGO3D entrega datos útiles para decidir en faena y predio — alertas anticipadas, no dashboards para mirar.</p>
    <div style="display:flex;gap:.7rem;flex-wrap:wrap">
      <a href="https://metgo3d.com/planes/" class="mg-btn--primary mg-btn--agro">Ver planes</a>
      <a href="{CONTACTO}" class="mg-btn--ghost">Solicitar demo</a>
      <a href="https://metgo3d.com/mjo-chile/" class="mg-btn--ghost" style="color:var(--out-tx);border-color:var(--out-br)">Línea I+D MJO →</a>
    </div>
  </section>

  <hr class="mg-divider">

  <section class="mg-sec">
    <p class="mg-sec-label">Misión</p>
    <div class="mg-mision-block">
      <p>El clima de Chile no cabe en un modelo global. Cada valle, cada cuenca minera, cada ruta de cordillera tiene su propia firma meteorológica. METGO3D existe para convertir esa complejidad en una decisión concreta: izar o no, regar o no, salir o no.</p>
      <cite>Miguel Lucero · Fundador, METGO3D SpA</cite>
    </div>
    <p class="mg-sec-sub">Operamos en tres frentes: alertas operacionales en tiempo real, investigación subseasonal con validación OOS, y datos de calidad del aire para cumplimiento normativo. <span>Cada frente con su propio panel, su propio precio y su propio protocolo.</span></p>
  </section>

  <hr class="mg-divider">

  <section class="mg-sec">
    <p class="mg-sec-label">Tres pilares</p>
    <div class="mg-pilares-grid">
      <div class="mg-pilar mg-op">
        <i class="ti ti-bell mg-pilar-icon mg-op" aria-hidden="true"></i>
        <p class="mg-pilar-sector mg-op">Operación</p>
        <h3>Alertas que cambian la decisión</h3>
        <p>Panel + umbrales para helada, viento, lluvia y calidad del aire. Cuando cruza el límite, avisamos con 12–24 h de anticipación — no un reporte del día siguiente.</p>
      </div>
      <div class="mg-pilar mg-id">
        <i class="ti ti-wave-sine mg-pilar-icon mg-id" aria-hidden="true"></i>
        <p class="mg-pilar-sector mg-id">I+D · ΨPSA-CL</p>
        <h3>MJO con skill medido</h3>
        <p>Tendencia 7–90 días validada fuera de muestra. Horizonte H90 en régimen y terciles, no mm del día. Transparencia científica publicada en <a href="https://metgo3d.com/mjo-chile/">/mjo-chile/</a>.</p>
      </div>
      <div class="mg-pilar mg-pr">
        <i class="ti ti-certificate mg-pilar-icon mg-pr" aria-hidden="true"></i>
        <p class="mg-pilar-sector mg-pr">Principios</p>
        <h3>Solo lo operativo</h3>
        <p>Datos reales antes que demos. Alertas útiles antes que widgets. Claims con protocolo OOS. Precio fijo por zona, sin sorpresas — igual que en la página de planes.</p>
      </div>
    </div>
  </section>

  <hr class="mg-divider">

  <section class="mg-sec">
    <p class="mg-sec-label">Cómo trabajamos</p>
    <div class="mg-principios-list">
      <div class="mg-principio">
        <span class="mg-pr-num">1</span>
        <div>
          <p class="mg-pr-title">Piloto antes que contrato</p>
          <p class="mg-pr-desc">15 días de acceso completo al panel. Si el sistema no sirve para la operación específica, no se cobra. Sin tarjeta, sin letra chica.</p>
        </div>
      </div>
      <div class="mg-principio">
        <span class="mg-pr-num">2</span>
        <div>
          <p class="mg-pr-title">Umbrales configurados a la faena</p>
          <p class="mg-pr-desc">Cada cliente parte con una sesión de configuración técnica. Los umbrales de alerta se ajustan a la grúa, el cultivo o la cuenca — no son valores por defecto.</p>
        </div>
      </div>
      <div class="mg-principio">
        <span class="mg-pr-num">3</span>
        <div>
          <p class="mg-pr-title">Transparencia en los modelos</p>
          <p class="mg-pr-desc">Los datos de validación del sistema ΨPSA-CL son públicos. Cualquier claim de skill tiene su protocolo OOS documentado. No vendemos confianza ciega.</p>
        </div>
      </div>
      <div class="mg-principio">
        <span class="mg-pr-num">4</span>
        <div>
          <p class="mg-pr-title">Precio fijo, sin sorpresas</p>
          <p class="mg-pr-desc">Los planes publicados son los precios reales. No hay cargos por zonas adicionales ocultos ni tarifas por alertas enviadas. El plan Campo es USD 99/mes.</p>
        </div>
      </div>
      <div class="mg-principio">
        <span class="mg-pr-num">5</span>
        <div>
          <p class="mg-pr-title">Soporte del meteorólogo, no de un bot</p>
          <p class="mg-pr-desc">Las alertas críticas incluyen interpretación humana. El PDF de turno de izaje lleva firma del meteorólogo responsable, no solo un número automático.</p>
        </div>
      </div>
    </div>
  </section>

  <hr class="mg-divider">

  <section class="mg-stack-sec">
    <div class="mg-stack-inner">
      <p class="mg-sec-label">Stack técnico</p>
      <p class="mg-sec-sub" style="margin-bottom:0">Fuentes de datos, modelos y herramientas que sostienen los paneles en producción.</p>
      <div class="mg-stack-grid">
        <div class="mg-stack-item">
          <i class="ti ti-cloud-data-connection mg-stack-item-icon mg-agro" aria-hidden="true"></i>
          <p class="mg-stack-item-name">Open-Meteo</p>
          <p class="mg-stack-item-desc">Pronóstico numérico base · resolución 1–5 km · actualización horaria</p>
        </div>
        <div class="mg-stack-item">
          <i class="ti ti-database mg-stack-item-icon mg-aire" aria-hidden="true"></i>
          <p class="mg-stack-item-name">ERA5 · CR2MET</p>
          <p class="mg-stack-item-desc">Reanálisis histórico para calibración de umbrales y validación OOS</p>
        </div>
        <div class="mg-stack-item">
          <i class="ti ti-code mg-stack-item-icon mg-izaje" aria-hidden="true"></i>
          <p class="mg-stack-item-name">Python · ΨPSA-CL</p>
          <p class="mg-stack-item-desc">Modelación regional propia · predicción subseasonal MJO para Chile</p>
        </div>
        <div class="mg-stack-item">
          <i class="ti ti-world mg-stack-item-icon mg-agro" aria-hidden="true"></i>
          <p class="mg-stack-item-name">Cloudflare Pages</p>
          <p class="mg-stack-item-desc">Hosting de paneles · latencia mínima · despliege continuo por zona</p>
        </div>
        <div class="mg-stack-item">
          <i class="ti ti-api mg-stack-item-icon mg-out" aria-hidden="true"></i>
          <p class="mg-stack-item-name">API REST JSON</p>
          <p class="mg-stack-item-desc">Integración directa con SCADA, ERP y sistemas de operación de clientes</p>
        </div>
      </div>
    </div>
  </section>

  <hr class="mg-divider">

  <section class="mg-sec">
    <p class="mg-sec-label">Equipo</p>
    <div class="mg-equipo-grid">
      <div class="mg-member">
        <div class="mg-member-avatar mg-ml">ML</div>
        <p class="mg-member-name">Miguel Lucero</p>
        <p class="mg-member-role">Fundador · Meteorólogo y analista de datos</p>
        <div class="mg-member-tags">
          <span class="mg-member-tag mg-a">METGO3D SpA</span>
          <span class="mg-member-tag mg-b">ΨPSA-CL</span>
          <span class="mg-member-tag mg-c">Magíster Estadística</span>
        </div>
      </div>
      <div class="mg-member">
        <div class="mg-member-avatar mg-mt">MT</div>
        <p class="mg-member-name">Marcelo Tejos</p>
        <p class="mg-member-role">Colaborador · Plataforma y datos</p>
        <div class="mg-member-tags">
          <span class="mg-member-tag mg-b">NeuroGestión</span>
          <span class="mg-member-tag mg-a">Análisis laboral</span>
        </div>
      </div>
      <div class="mg-member" style="background:var(--agro-t);border-left:2.5px solid var(--agro)">
        <div style="font-size:18px;color:var(--agro-tx);margin-bottom:.5rem"><i class="ti ti-user-plus" aria-hidden="true"></i></div>
        <p class="mg-member-name">¿Tu nombre aquí?</p>
        <p class="mg-member-role" style="margin-bottom:.75rem">METGO3D está creciendo. Si trabajas en meteorología operacional, datos ambientales o desarrollo backend, escríbenos.</p>
        <a href="mailto:miguel.lucero@metgo3d.com" style="font-size:11px;color:var(--agro-tx);text-decoration:none;border-bottom:.5px solid var(--agro-br)">miguel.lucero@metgo3d.com</a>
      </div>
    </div>
  </section>

  <hr class="mg-divider">

  <div class="mg-cta-strip">
    <div class="mg-cta-strip-text">
      <h3>¿Listo para un piloto en tu zona?</h3>
      <p>15 días de acceso completo. Sin tarjeta ni compromiso.</p>
    </div>
    <div class="mg-cta-strip-actions">
      <a href="{CONTACTO}" class="mg-btn--primary">Solicitar demo gratis</a>
      <a href="https://metgo3d.com/planes/" class="mg-btn--ghost">Ver planes →</a>
    </div>
  </div>

</div>
"""


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
        print(f"updated {slug} id={pid}")
        return pid
    out = request("POST", "/wp/v2/pages", body)
    print(f"created {slug} id={out['id']}")
    return out["id"]


def try_custom_css(css: str) -> None:
    """Intenta Additional CSS / global styles; no falla el deploy si no hay endpoint."""
    # WordPress.com Jetpack custom CSS (si existe)
    for path, body in (
        ("/wp/v2/settings", {"custom_css": css}),
        ("/wpcom/v2/custom-css", {"css": css}),
    ):
        try:
            request("POST", path, body)
            print(f"custom css via {path}")
            return
        except SystemExit as e:
            print(f"skip {path}: {e}")
        except Exception as e:  # noqa: BLE001
            print(f"skip {path}: {e}")


def minimal_theme_chrome() -> None:
    """Header/footer del tema vacíos (el mg-page trae su propia nav)."""
    empty_header = '<!-- wp:html --><div style="display:none" aria-hidden="true"></div><!-- /wp:html -->'
    empty_footer = empty_header
    empty_signup = empty_header
    for slug, content in (
        ("header", empty_header),
        ("footer", empty_footer),
        ("signup", empty_signup),
    ):
        request(
            "POST",
            f"/wp/v2/template-parts/coachben//{slug}",
            {"content": content, "status": "publish"},
        )
        print(f"cleared theme part {slug}")


def main() -> None:
    print("=== METGO mg-page sobrio ===")
    css = load_css()
    try_custom_css(css)
    minimal_theme_chrome()

    request(
        "POST",
        "/wp/v2/settings",
        {
            "title": "METGO3D",
            "show_on_front": "page",
            "page_on_front": 211,
            "page_for_posts": 0,
        },
    )

    request(
        "POST",
        "/wp/v2/pages/211",
        {"title": "Inicio", "content": wrap(home_body()), "status": "publish", "menu_order": 1},
    )
    print("home 211")

    request(
        "POST",
        "/wp/v2/pages/204",
        {
            "title": "Agricultura de Precisión",
            "content": wrap(agro_body()),
            "status": "publish",
            "slug": "agricultura-de-precision",
            "menu_order": 10,
        },
    )
    print("agro 204")

    upsert_page("izaje-ventora", "VENTORA Izaje", wrap(izaje_body()), 15)

    request(
        "POST",
        "/wp/v2/pages/213",
        {
            "title": "Minería y Calidad del Aire",
            "content": wrap(mineria_body()),
            "status": "publish",
            "slug": "mineria-y-calidad-del-aire",
            "menu_order": 20,
        },
    )
    print("mineria 213")

    upsert_page(
        "planes",
        "Planes",
        wrap(planes_body(), active="planes", extra_head=TABLER_CSS),
        40,
    )
    
    FONT_CSS = '<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Serif+Display&display=swap" rel="stylesheet">'
    upsert_page(
        "nosotros",
        "Nosotros",
        wrap(nosotros_body(), active="nosotros", extra_head=TABLER_CSS + "\n" + FONT_CSS),
        45,
    )
    
    upsert_page("contacto", "Contacto", wrap(contacto_body(), active="contacto"), 50)

    print("DONE")


if __name__ == "__main__":
    main()
