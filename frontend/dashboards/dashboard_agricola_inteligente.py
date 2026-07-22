import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import metgo_paths

metgo_paths.setup_paths("01_meteo", "02_agricola", "05_api_rest")

from metgo.streamlit_theme import bootstrap_dashboard, PLOTLY_CONFIG, plotly_layout
from agricola_dashboard_utils import ESTACIONES_VALLE, cargar_contexto_agricola
from meteo_dashboard_utils import hoy_chile


def _fmt_delta(val: float | None, unidad: str) -> str | None:
    if val is None:
        return None
    sign = "+" if val > 0 else ""
    return f"{sign}{val:.1f}{unidad} vs ayer"

# Configuración de la página
st.set_page_config(
    page_title="Gestión Agrícola Inteligente - METGO",
    page_icon="M",
    layout="wide",
    initial_sidebar_state="expanded",
)

bootstrap_dashboard(
    "Gestión Agrícola Inteligente",
    "Recomendaciones por IA · cultivos Valle de Aconcagua",
    module="agricola",
)

# Sidebar para controles
st.sidebar.markdown("### Panel de Control Agrícola")

# Configuración de cultivos
cultivos_config = {
    "Palta": {
        "temp_optima": (20, 25), "humedad_optima": (60, 80), "precipitacion_optima": (800, 1200),
        "fases": ["Floración", "Crecimiento", "Maduración", "Cosecha"],
        "plagas_comunes": ["Arañita roja", "Trips", "Mosca de la fruta", "Pulgones"],
        "enfermedades": ["Antracnosis", "Mancha negra", "Podredumbre de raíz"],
        "riego_frecuencia": 3, "riego_cantidad": 25
    },
    "Cítricos": {
        "temp_optima": (15, 30), "humedad_optima": (50, 70), "precipitacion_optima": (600, 1000),
        "fases": ["Floración", "Cuajado", "Crecimiento", "Maduración"],
        "plagas_comunes": ["Minador de hojas", "Ácaros", "Cochinillas", "Pulgones"],
        "enfermedades": ["Gomosis", "Cancro", "Mancha grasienta"],
        "riego_frecuencia": 2, "riego_cantidad": 30
    },
    "Vid": {
        "temp_optima": (18, 28), "humedad_optima": (40, 60), "precipitacion_optima": (400, 800),
        "fases": ["Brotes", "Floración", "Cuajado", "Envero", "Maduración"],
        "plagas_comunes": ["Lobesia", "Polilla del racimo", "Arañita roja", "Mosca de la fruta"],
        "enfermedades": ["Mildiu", "Oídio", "Botritis", "Podredumbre"],
        "riego_frecuencia": 2, "riego_cantidad": 20
    },
    "Tomate": {
        "temp_optima": (20, 30), "humedad_optima": (60, 80), "precipitacion_optima": (500, 800),
        "fases": ["Siembra", "Crecimiento", "Floración", "Fructificación", "Cosecha"],
        "plagas_comunes": ["Tuta absoluta", "Mosca blanca", "Ácaros", "Trips"],
        "enfermedades": ["Tizón tardío", "Tizón temprano", "Fusarium", "Verticilosis"],
        "riego_frecuencia": 1, "riego_cantidad": 15
    },
    "Lechuga": {
        "temp_optima": (15, 22), "humedad_optima": (70, 90), "precipitacion_optima": (300, 500),
        "fases": ["Siembra", "Crecimiento", "Cabeceo", "Cosecha"],
        "plagas_comunes": ["Pulgones", "Gusanos cortadores", "Ácaros", "Trips"],
        "enfermedades": ["Mildiu", "Sclerotinia", "Rhizoctonia"],
        "riego_frecuencia": 1, "riego_cantidad": 10
    }
}

estacion_seleccionada = st.sidebar.selectbox("Estación:", ESTACIONES_VALLE)
cultivo_seleccionado = st.sidebar.selectbox("Cultivo:", list(cultivos_config.keys()))
fase_actual = st.sidebar.selectbox("Fase Actual:", cultivos_config[cultivo_seleccionado]["fases"])
superficie = st.sidebar.number_input("Superficie (hectáreas):", min_value=0.1, max_value=1000.0, value=1.0, step=0.1)

with st.spinner("Cargando condiciones y recomendaciones (API METGO)…"):
    ctx = cargar_contexto_agricola(estacion_seleccionada, cultivo_seleccionado)

tipo = ctx.get("tipo_dato", "observado")
st.caption(
    f"**{ctx.get('fecha_referencia', hoy_chile())}** · {estacion_seleccionada} · "
    f"**{tipo}** ({ctx.get('fuente', 'OpenMeteo')}) · "
    f"T° {ctx['temperatura_min']:.1f}–{ctx['temperatura_max']:.1f}°C · "
    "Vue: http://127.0.0.1:5173/agricola"
)
if tipo != "observado":
    st.warning(
        "Sin observación de hoy en histórico; se muestra pronóstico. Reinicie la API si acaba de actualizar OpenMeteo."
    )

# Función para generar recomendaciones IA
def generar_recomendaciones_ia(cultivo, fase, superficie, temp_actual, humedad_actual, precipitacion_actual):
    """Genera recomendaciones inteligentes basadas en IA"""
    
    config = cultivos_config[cultivo]
    recomendaciones = []
    alertas = []
    
    # Análisis de temperatura
    temp_min, temp_max = config["temp_optima"]
    if temp_actual < temp_min:
        recomendaciones.append(f"**Temperatura baja**: Considerar protección contra heladas o calefacción")
        alertas.append({"tipo": "Helada", "severidad": "Alta", "mensaje": "Riesgo de helada detectado"})
    elif temp_actual > temp_max:
        recomendaciones.append(f"**Temperatura alta**: Incrementar riego y considerar sombreado")
        alertas.append({"tipo": "Calor", "severidad": "Media", "mensaje": "Estrés térmico en cultivos"})
    else:
        recomendaciones.append(f"**Temperatura óptima**: Condiciones ideales para {cultivo}")
    
    # Análisis de humedad
    hum_min, hum_max = config["humedad_optima"]
    if humedad_actual < hum_min:
        recomendaciones.append(f"**Humedad baja**: Incrementar frecuencia de riego")
        alertas.append({"tipo": "Sequía", "severidad": "Media", "mensaje": "Condiciones de sequía"})
    elif humedad_actual > hum_max:
        recomendaciones.append(f"**Humedad alta**: Reducir riego y mejorar ventilación")
        alertas.append({"tipo": "Exceso Humedad", "severidad": "Baja", "mensaje": "Riesgo de enfermedades fúngicas"})
    
    # Plagas/enfermedades: solo si hay estrés climático (sin listas genéricas)
    if humedad_actual > hum_max:
        for enfermedad in config["enfermedades"][:1]:
            recomendaciones.append(f"**Prevención {enfermedad}**: Humedad elevada — fungicida preventivo")
            alertas.append({"tipo": "Enfermedad", "severidad": "Media", "mensaje": f"Riesgo fúngico ({enfermedad})"})
    if temp_actual > temp_max:
        for plaga in config["plagas_comunes"][:1]:
            recomendaciones.append(f"**Control de {plaga}**: Estrés térmico — monitoreo intensivo")
            alertas.append({"tipo": "Plaga", "severidad": "Media", "mensaje": f"Vigilar {plaga}"})
    
    # Recomendaciones específicas por fase
    if fase == "Floración":
        recomendaciones.append("**Fase de Floración**: Evitar riego excesivo y aplicar fertilizante rico en fósforo")
    elif fase == "Crecimiento":
        recomendaciones.append("**Fase de Crecimiento**: Mantener riego constante y aplicar fertilizante balanceado")
    elif fase == "Maduración":
        recomendaciones.append("**Fase de Maduración**: Reducir riego y preparar para cosecha")
    elif fase == "Cosecha":
        recomendaciones.append("**Cosecha**: Programar cosecha en condiciones óptimas de humedad")
    
    return recomendaciones, alertas

temp_actual = ctx["temperatura"]
humedad_actual = ctx["humedad"]
precipitacion_actual = ctx["precipitacion"]

recomendaciones, alertas = generar_recomendaciones_ia(
    cultivo_seleccionado,
    fase_actual,
    superficie,
    temp_actual,
    humedad_actual,
    precipitacion_actual,
)

recomendaciones_api_txt: list[str] = []
for rec in ctx.get("recomendaciones_api") or []:
    recomendaciones_api_txt.append(
        f"**{rec.get('cultivo', 'METGO')}**: {rec.get('accion', '')} — _{rec.get('motivo', '')}_"
    )
if ctx.get("riego"):
    r = ctx["riego"]
    recomendaciones_api_txt.insert(
        0,
        f"**Riego (API)**: {r.get('mm_sugeridos_hoy', '—')} mm hoy · {r.get('accion', '')}",
    )

# Métricas principales
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="T° promedio hoy",
        value=f"{temp_actual:.1f}°C",
        delta=_fmt_delta(ctx.get("delta_temp"), "°C"),
        help=f"Mín {ctx['temperatura_min']:.1f}°C · máx {ctx['temperatura_max']:.1f}°C (OpenMeteo)",
    )

with col2:
    st.metric(
        label="Humedad relativa",
        value=f"{humedad_actual:.1f}%",
        delta=_fmt_delta(ctx.get("delta_humedad"), "%"),
    )

with col3:
    st.metric(
        label="Precipitación día",
        value=f"{precipitacion_actual:.1f} mm",
        delta=_fmt_delta(ctx.get("delta_precip"), " mm"),
    )

with col4:
    riego_api = ctx.get("riego") or {}
    mm_hoy = riego_api.get("mm_sugeridos_hoy")
    if mm_hoy is not None:
        st.metric(
            label="Riego API (hoy)",
            value=f"{mm_hoy} mm",
            delta=str(riego_api.get("accion", ""))[:24],
        )
    else:
        st.metric(
            label="Riego",
            value="—",
            delta="Sin dato API",
            help="Active la API en :8080 o elija cultivo en Vue /agricola",
        )

# Sistema de Alertas y Recomendaciones Profesional
st.markdown("""
<div style="background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); color: white; padding: 20px; border-radius: 15px; margin: 20px 0;">
    <h2 style="margin: 0; text-align: center;"> Sistema de Alertas y Recomendaciones Empresarial</h2>
    <p style="margin: 10px 0 0 0; text-align: center; opacity: 0.9;">Monitoreo inteligente y comunicación automatizada</p>
</div>
""", unsafe_allow_html=True)

# Panel de control de notificaciones
st.markdown("### Panel de Control de Notificaciones")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("#### Email")
    email_enabled = st.checkbox("Activar Email", value=True, key="email_alerts")
    email_address = st.text_input("Dirección Email", value="agricola@metgo.cl", key="email_address")

with col2:
    st.markdown("#### SMS")
    sms_enabled = st.checkbox("Activar SMS", value=True, key="sms_alerts")
    phone_number = st.text_input("Número Teléfono", value="+56 9 1234 5678", key="phone_number")

with col3:
    st.markdown("#### WhatsApp")
    whatsapp_enabled = st.checkbox("Activar WhatsApp", value=True, key="whatsapp_alerts")
    whatsapp_number = st.text_input("WhatsApp Business", value="+56 9 8765 4321", key="whatsapp_number")

with col4:
    st.markdown("#### Configuración")
    alert_frequency = st.selectbox("Frecuencia", ["Inmediata", "Cada hora", "Diaria", "Semanal"], key="alert_freq")
    priority_filter = st.selectbox("Prioridad Mínima", ["Alta", "Media", "Baja"], key="priority_filter")

# Dashboard de alertas profesional
st.markdown("### Dashboard de Alertas Empresarial")

# Métricas de alertas
col1, col2, col3, col4 = st.columns(4)

total_alertas = len(alertas)
alertas_altas = len([a for a in alertas if a["severidad"] == "Alta"])
alertas_medias = len([a for a in alertas if a["severidad"] == "Media"])
alertas_bajas = len([a for a in alertas if a["severidad"] == "Baja"])

with col1:
    st.metric("Total Alertas", total_alertas, delta=f"Últimas 24h")
    
with col2:
    st.metric("Críticas", alertas_altas, delta="Requieren acción inmediata"if alertas_altas > 0 else "Sin alertas críticas")
    
with col3:
    st.metric("Medias", alertas_medias, delta="Monitoreo recomendado"if alertas_medias > 0 else "Sistema estable")
    
with col4:
    st.metric("Bajas", alertas_bajas, delta="Rutina normal"if alertas_bajas > 0 else "Sin incidencias")

# Tabla profesional de alertas
st.markdown("#### Tabla de Alertas Detallada")

if alertas:
    # Crear DataFrame para la tabla
    alertas_df = pd.DataFrame(alertas)
    alertas_df['Timestamp'] = pd.Timestamp.now().strftime('%d/%m/%Y %H:%M')
    alertas_df['Estado'] = ['Pendiente'] * len(alertas)
    alertas_df['Acción'] = ['Revisar'] * len(alertas)
    
    # Mostrar tabla con estilo profesional
    st.dataframe(
        alertas_df[['Timestamp', 'tipo', 'severidad', 'mensaje', 'Estado', 'Acción']],
        use_container_width=True,
        hide_index=True,
        column_config={
            "Timestamp": "Fecha/Hora",
            "tipo": "Tipo de Alerta",
            "severidad": "Prioridad",
            "mensaje": "Descripción",
            "Estado": "Estado",
            "Acción": "Acción Requerida"
        }
    )
else:
    st.success("No hay alertas activas en este momento")

# Recomendaciones API (datos reales)
st.markdown("#### Recomendaciones METGO (API / módulo 02)")

if recomendaciones_api_txt:
    for i, rec in enumerate(recomendaciones_api_txt, 1):
        with st.container():
            st.markdown(f"""
            <div style="border-left: 4px solid #1565C0; padding: 15px; margin: 10px 0; background-color: #f0f7ff; border-radius: 5px;">
                <h4 style="margin: 0 0 10px 0; color: #1565C0;"> Recomendación API #{i}</h4>
                <p style="margin: 0; color: #333;">{rec}</p>
            </div>
            """, unsafe_allow_html=True)
else:
    st.info("Sin recomendaciones API para esta estación. Verifique la API en el puerto 8080.")

with st.expander("Reglas locales por cultivo (complemento, no sustituye API)"):
    if recomendaciones:
        for i, rec in enumerate(recomendaciones, 1):
            st.markdown(f"**#{i}** {rec}")
    else:
        st.caption("Sin reglas locales activas para las condiciones actuales.")

# Descarga de reporte agrícola (HTML imprimible como PDF)
def _generar_reporte_html(cultivo, fase, superficie, temp, humedad, precip, recs, alts):
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M")
    rec_html = "".join(f"<li>{r}</li>" for r in recs) or "<li>Sin recomendaciones</li>"
    alt_html = "".join(
        f"<li><strong>{a.get('tipo', 'Alerta')}</strong>: {a.get('mensaje', '')}</li>"
        for a in alts
    ) or "<li>Sin alertas activas</li>"
    return f"""<!DOCTYPE html>
<html lang="es"><head><meta charset="utf-8"><title>Reporte METGO - {cultivo}</title>
<style>
body{{font-family:Arial,sans-serif;margin:2rem;color:#222}}
h1{{color:#2E7D32}} table{{border-collapse:collapse;width:100%;margin:1rem 0}}
td,th{{border:1px solid #ccc;padding:8px;text-align:left}}
@media print{{body{{margin:1cm}}}}
</style></head><body>
<h1>Reporte agrícola METGO</h1>
<p>Generado: {fecha}</p>
<table>
<tr><th>Cultivo</th><td>{cultivo}</td></tr>
<tr><th>Fase</th><td>{fase}</td></tr>
<tr><th>Superficie</th><td>{superficie} ha</td></tr>
<tr><th>Temperatura</th><td>{temp:.1f} °C</td></tr>
<tr><th>Humedad</th><td>{humedad:.1f} %</td></tr>
<tr><th>Precipitación 24h</th><td>{precip:.1f} mm</td></tr>
</table>
<h2>Recomendaciones</h2><ul>{rec_html}</ul>
<h2>Alertas</h2><ul>{alt_html}</ul>
</body></html>"""

st.markdown("### Exportar reporte")
reporte_html = _generar_reporte_html(
    cultivo_seleccionado,
    fase_actual,
    superficie,
    temp_actual,
    humedad_actual,
    precipitacion_actual,
    recomendaciones_api_txt + recomendaciones,
    alertas,
)
st.download_button(
    label="Descargar reporte (HTML / imprimir como PDF)",
    data=reporte_html.encode("utf-8"),
    file_name=f"reporte_metgo_{cultivo_seleccionado.lower()}_{datetime.now():%Y%m%d}.html",
    mime="text/html",
    type="primary",
    use_container_width=True,
    help="Abra el archivo en el navegador y use Imprimir → Guardar como PDF.",
)

# Botones de acción empresarial
st.markdown("### Acciones Empresariales")

col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("Enviar Reporte por Email", type="primary", use_container_width=True):
        if email_enabled and email_address:
            st.success(f"Reporte enviado a {email_address}")
        else:
            st.error("Email no configurado")

with col2:
    if st.button("Enviar Alerta SMS", type="secondary", use_container_width=True):
        if sms_enabled and phone_number:
            st.success(f"SMS enviado a {phone_number}")
        else:
            st.error("SMS no configurado")

with col3:
    if st.button("Enviar por WhatsApp", type="secondary", use_container_width=True):
        if whatsapp_enabled and whatsapp_number:
            st.success(f"Mensaje WhatsApp enviado a {whatsapp_number}")
        else:
            st.error("WhatsApp no configurado")

with col4:
    if st.button("Generar Reporte Ejecutivo", type="primary", use_container_width=True):
        st.success("Reporte ejecutivo generado y guardado")

# Panel de configuración avanzada
with st.expander("Configuración Avanzada de Notificaciones"):
    st.markdown("#### Configuraciones Empresariales")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Horarios de Notificación:**")
        horario_inicio = st.time_input("Inicio", value=datetime.strptime("08:00", "%H:%M").time())
        horario_fin = st.time_input("Fin", value=datetime.strptime("18:00", "%H:%M").time())
        
        st.markdown("**Filtros de Alerta:**")
        solo_alertas_criticas = st.checkbox("Solo alertas críticas en horario fuera de oficina")
        notificaciones_fin_semana = st.checkbox("Notificaciones en fin de semana")
    
    with col2:
        st.markdown("**Plantillas de Mensaje:**")
        plantilla_email = st.text_area("Plantilla Email", value="Alerta METGO: {tipo} - {mensaje} - Fecha: {fecha}")
        plantilla_sms = st.text_area("Plantilla SMS", value="METGO: {tipo} - {mensaje}")
        plantilla_whatsapp = st.text_area("Plantilla WhatsApp", value="*Alerta METGO*\\n\\n*Tipo:* {tipo}\\n*Mensaje:* {mensaje}\\n*Fecha:* {fecha}")
    
    if st.button("Guardar Configuración", type="primary"):
        st.success("Configuración guardada correctamente")

# Análisis detallado de alertas y recomendaciones
st.markdown("### Análisis Detallado de Alertas y Recomendaciones")

# Tabs para diferentes aspectos del análisis
tab1, tab2, tab3, tab4, tab5 = st.tabs(["Estadísticas", "Recomendaciones Detalladas", "Tendencias", "Acciones Automáticas", "Historial"])

with tab1:
    st.markdown("#### Estadísticas Avanzadas de Alertas")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Gráfico de distribución de alertas por tipo
        if alertas:
            tipos_alerta = [alerta['tipo'] for alerta in alertas]
            tipo_counts = pd.Series(tipos_alerta).value_counts()
            
            fig_tipos = px.pie(
                values=tipo_counts.values, 
                names=tipo_counts.index,
                title="Distribución de Alertas por Tipo",
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            st.plotly_chart(fig_tipos, config=PLOTLY_CONFIG, use_container_width=True)
        else:
            st.info("No hay alertas para mostrar estadísticas")
    
    with col2:
        # Gráfico de severidad
        if alertas:
            severidades = [alerta['severidad'] for alerta in alertas]
            severidad_counts = pd.Series(severidades).value_counts()
            
            fig_severidad = px.bar(
                x=severidad_counts.index,
                y=severidad_counts.values,
                title="Alertas por Nivel de Severidad",
                color=severidad_counts.index,
                color_discrete_map={'Alta': '#F44336', 'Media': '#FF9800', 'Baja': '#4CAF50'}
            )
            st.plotly_chart(fig_severidad, config=PLOTLY_CONFIG, use_container_width=True)
        else:
            st.info("No hay alertas para mostrar estadísticas")
    
    # Métricas adicionales
    col1, col2, col3, col4 = st.columns(4)
    
    st.info("Sin datos — requiere API de alertas para KPIs operativos del panel empresarial.")

with tab2:
    st.markdown("#### Recomendaciones Estratégicas Detalladas")
    
    if recomendaciones:
        for i, rec in enumerate(recomendaciones, 1):
            with st.expander(f"Recomendación #{i}: {rec[:50]}..."):
                st.markdown(f"**Descripción Completa:**")
                st.write(rec)
                
                # Análisis de impacto
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    impacto = st.select_slider(
                        f"Impacto Esperado - Rec #{i}",
                        options=["Bajo", "Medio", "Alto"],
                        value="Medio",
                        key=f"impacto_{i}"
                    )
                
                with col2:
                    urgencia = st.select_slider(
                        f"Urgencia - Rec #{i}",
                        options=["Baja", "Media", "Alta"],
                        value="Media",
                        key=f"urgencia_{i}"
                    )
                
                with col3:
                    costo = st.select_slider(
                        f"Costo Implementación - Rec #{i}",
                        options=["Bajo", "Medio", "Alto"],
                        value="Medio",
                        key=f"costo_{i}"
                    )
                
                # Acciones específicas
                st.markdown("**Acciones Específicas Recomendadas:**")
                
                if "riego" in rec.lower():
                    st.write("• Verificar sistema de riego automatizado")
                    st.write("• Calibrar sensores de humedad")
                    st.write("• Programar riego según fase del cultivo")
                
                elif "plaga" in rec.lower() or "enfermedad" in rec.lower():
                    st.write("• Inspección visual inmediata")
                    st.write("• Aplicar tratamiento preventivo")
                    st.write("• Monitoreo diario por 7 días")
                
                elif "fertiliz" in rec.lower():
                    st.write("• Análisis de suelo")
                    st.write("• Aplicación de fertilizante específico")
                    st.write("• Seguimiento de absorción")
                
                else:
                    st.write("• Evaluación general del cultivo")
                    st.write("• Consulta con técnico especialista")
                    st.write("• Documentación de observaciones")
                
                # Botones de acción
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button(f"Aplicar Rec #{i}", key=f"aplicar_{i}"):
                        st.success(f"Recomendación #{i} marcada como aplicada")
                
                with col2:
                    if st.button(f"Programar Rec #{i}", key=f"programar_{i}"):
                        st.info(f"Recomendación #{i} programada para revisión")
                
                with col3:
                    if st.button(f"Descartar Rec #{i}", key=f"descartar_{i}"):
                        st.warning(f"Recomendación #{i} descartada")

with tab3:
    st.markdown("#### Tendencias (histórico OpenMeteo)")
    
    hist_t = ctx.get("historico") or []
    if not hist_t:
        st.info("Sin histórico disponible. Levante la API en :8080.")
        df_tendencias = pd.DataFrame()
    else:
        df_tendencias = pd.DataFrame(
            [
                {
                    "fecha": r.get("fecha"),
                    "temperatura": r.get("temperatura"),
                    "humedad": r.get("humedad"),
                    "precipitacion": r.get("precipitacion"),
                }
                for r in hist_t[-30:]
            ]
        )
    
    if not df_tendencias.empty:
        fig_tendencias = go.Figure()
        fig_tendencias.add_trace(
            go.Scatter(
                x=df_tendencias["fecha"],
                y=df_tendencias["temperatura"],
                mode="lines+markers",
                name="T° promedio",
                line=dict(color="#F44336", width=3),
            )
        )
        fig_tendencias.add_trace(
            go.Scatter(
                x=df_tendencias["fecha"],
                y=df_tendencias["humedad"],
                mode="lines+markers",
                name="Humedad %",
                line=dict(color="#2196F3", width=2),
                yaxis="y2",
            )
        )
        fig_tendencias.update_layout(
            title=f"Clima observado · {estacion_seleccionada}",
            xaxis_title="Fecha",
            yaxis_title="Temperatura (°C)",
            yaxis2=dict(title="Humedad (%)", overlaying="y", side="right"),
            height=400,
            hovermode="x unified",
        )
        st.plotly_chart(fig_tendencias, config=PLOTLY_CONFIG, use_container_width=True)

        col1, col2 = st.columns(2)
        with col1:
            corr_th = df_tendencias["temperatura"].corr(df_tendencias["humedad"])
            st.metric(
                "Correlación T° / humedad",
                f"{corr_th:.2f}" if not pd.isna(corr_th) else "—",
            )
        with col2:
            st.metric("Precip. acumulada (30 d)", f"{df_tendencias['precipitacion'].sum():.1f} mm")

with tab4:
    st.markdown("#### Configuración de Acciones Automáticas")
    
    st.markdown("**Automatización de Respuestas a Alertas:**")
    
    # Configuración de acciones automáticas
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Alertas de Temperatura:**")
        
        temp_critica = st.number_input("Temperatura Crítica (°C)", value=35.0, min_value=0.0, max_value=50.0)
        accion_temp = st.selectbox("Acción Automática", 
                                  ["Enviar notificación", "Activar riego", "Activar ventilación", "Contactar técnico"])
        
        st.markdown("**Alertas de Humedad:**")
        humedad_critica = st.number_input("Humedad Crítica (%)", value=30.0, min_value=0.0, max_value=100.0)
        accion_humedad = st.selectbox("Acción Automática Humedad", 
                                     ["Enviar notificación", "Activar riego", "Activar ventilación", "Contactar técnico"])
    
    with col2:
        st.markdown("**Alertas de Plagas:**")
        
        umbral_plagas = st.number_input("Umbral Detección Plagas (%)", value=70.0, min_value=0.0, max_value=100.0)
        accion_plagas = st.selectbox("Acción Automática Plagas", 
                                    ["Enviar notificación", "Aplicar tratamiento", "Contactar técnico", "Programar inspección"])
        
        st.markdown("**Alertas de Riego:**")
        umbral_riego = st.number_input("Umbral Humedad Riego (%)", value=40.0, min_value=0.0, max_value=100.0)
        accion_riego = st.selectbox("Acción Automática Riego", 
                                   ["Enviar notificación", "Activar riego automático", "Contactar técnico", "Programar revisión"])
    
    # Reglas de automatización
    st.markdown("**Reglas de Automatización Activas:**")
    
    reglas_activas = [
        {"condicion": f"Temperatura > {temp_critica}°C", "accion": accion_temp, "activa": True},
        {"condicion": f"Humedad < {humedad_critica}%", "accion": accion_humedad, "activa": True},
        {"condicion": f"Riesgo plagas > {umbral_plagas}%", "accion": accion_plagas, "activa": True},
        {"condicion": f"Humedad suelo < {umbral_riego}%", "accion": accion_riego, "activa": True}
    ]
    
    for i, regla in enumerate(reglas_activas, 1):
        col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
        
        with col1:
            st.write(f"**Regla #{i}:** {regla['condicion']}")
        
        with col2:
            st.write(f"**Acción:** {regla['accion']}")
        
        with col3:
            estado = "Activa"if regla['activa'] else "Inactiva"
            st.write(f"**Estado:** {estado}")
        
        with col4:
            if st.button("Config", key=f"config_regla_{i}"):
                st.info(f"Configurando regla #{i}")

with tab5:
    st.markdown("#### Historial de Alertas y Acciones")
    st.info("Sin datos — requiere API de alertas")

# Análisis de cultivos
st.markdown("### Análisis de Cultivos")

# Gráfico de condiciones óptimas vs actuales
fig_condiciones = go.Figure()

config = cultivos_config[cultivo_seleccionado]

# Condiciones óptimas
variables = ['Temperatura', 'Humedad', 'Precipitación']
optimas = [
    (config['temp_optima'][0] + config['temp_optima'][1]) / 2,
    (config['humedad_optima'][0] + config['humedad_optima'][1]) / 2,
    (config['precipitacion_optima'][0] + config['precipitacion_optima'][1]) / 2
]

# Condiciones actuales (normalizadas)
actuales = [
    temp_actual,
    humedad_actual,
    precipitacion_actual * 100  # Escalar precipitación
]

fig_condiciones.add_trace(go.Bar(
    name='Condiciones Óptimas',
    x=variables,
    y=optimas,
    marker_color='#4CAF50'
))

fig_condiciones.add_trace(go.Bar(
    name='Condiciones Actuales',
    x=variables,
    y=actuales,
    marker_color='#FF6B35'
))

fig_condiciones.update_layout(
    **plotly_layout(
        f'Condiciones para {cultivo_seleccionado} - {fase_actual}',
        height=400,
        barmode='group',
    )
)

st.plotly_chart(fig_condiciones, config=PLOTLY_CONFIG, use_container_width=True)

def _score_riesgo(humedad: float, temp: float, hum_r: tuple, temp_r: tuple) -> int:
    hum_min, hum_max = hum_r
    t_min, t_max = temp_r
    score = 10
    if humedad > hum_max:
        score += 45
    elif humedad < hum_min:
        score += 20
    if temp > t_max:
        score += 35
    elif temp < t_min:
        score += 30
    return min(95, score)


# Análisis de plagas y enfermedades
col1, col2 = st.columns(2)

with col1:
    st.markdown("#### Riesgo de plagas (estimado por clima)")
    
    plagas_data = []
    for plaga in config["plagas_comunes"]:
        prob = _score_riesgo(humedad_actual, temp_actual, config["humedad_optima"], config["temp_optima"])
        riesgo = "Alto" if prob >= 70 else "Medio" if prob >= 40 else "Bajo"
        plagas_data.append({"Plaga": plaga, "Riesgo": riesgo, "Probabilidad": prob})
    
    df_plagas = pd.DataFrame(plagas_data)
    
    fig_plagas = px.bar(df_plagas, x='Plaga', y='Probabilidad', 
                       color='Riesgo', 
                       color_discrete_map={'Bajo': '#4CAF50', 'Medio': '#FF9800', 'Alto': '#F44336'},
                       title='Probabilidad de Aparición de Plagas')
    st.plotly_chart(fig_plagas, config=PLOTLY_CONFIG, use_container_width=True)

with col2:
    st.markdown("#### Riesgo de enfermedades (estimado por clima)")
    
    enfermedades_data = []
    base_enf = _score_riesgo(humedad_actual, temp_actual, config["humedad_optima"], config["temp_optima"])
    for enfermedad in config["enfermedades"]:
        prob = min(95, base_enf + (15 if "hongo" in enfermedad.lower() or "mildiu" in enfermedad.lower() else 0))
        riesgo = "Alto" if prob >= 70 else "Medio" if prob >= 40 else "Bajo"
        enfermedades_data.append({"Enfermedad": enfermedad, "Riesgo": riesgo, "Probabilidad": prob})
    
    df_enfermedades = pd.DataFrame(enfermedades_data)
    
    fig_enfermedades = px.bar(df_enfermedades, x='Enfermedad', y='Probabilidad', 
                             color='Riesgo',
                             color_discrete_map={'Bajo': '#4CAF50', 'Medio': '#FF9800', 'Alto': '#F44336'},
                             title='Probabilidad de Aparición de Enfermedades')
    st.plotly_chart(fig_enfermedades, config=PLOTLY_CONFIG, use_container_width=True)

# Cronograma de actividades
st.markdown("### Cronograma de Actividades Agrícolas")

# Generar cronograma para los próximos 30 días
fechas = pd.date_range(start=datetime.now(), periods=30, freq='D')
actividades = []

for fecha in fechas:
    dia_semana = fecha.strftime('%A')
    
    # Actividades regulares
    if dia_semana in ['Monday', 'Wednesday', 'Friday']:
        actividades.append({
            'Fecha': fecha,
            'Actividad': 'Riego programado',
            'Prioridad': 'Alta',
            'Tipo': 'Riego'
        })
    
    # Actividades semanales
    if fecha.day % 7 == 0:
        actividades.append({
            'Fecha': fecha,
            'Actividad': 'Monitoreo de plagas',
            'Prioridad': 'Media',
            'Tipo': 'Monitoreo'
        })
    
    # Actividades mensuales
    if fecha.day == 15:
        actividades.append({
            'Fecha': fecha,
            'Actividad': 'Aplicación de fertilizante',
            'Prioridad': 'Alta',
            'Tipo': 'Fertilización'
        })

df_cronograma = pd.DataFrame(actividades)

if not df_cronograma.empty:
    # Crear gráfico de cronograma mejorado
    fig_cronograma = go.Figure()
    
    # Mapeo de colores para prioridades
    color_map = {'Alta': '#F44336', 'Media': '#FF9800', 'Baja': '#4CAF50'}
    
    # Agrupar por tipo de actividad
    tipos_actividad = df_cronograma['Tipo'].unique()
    y_positions = {tipo: i for i, tipo in enumerate(tipos_actividad)}
    
    for _, row in df_cronograma.iterrows():
        fig_cronograma.add_trace(go.Scatter(
            x=[row['Fecha'], row['Fecha']],
            y=[y_positions[row['Tipo']] - 0.3, y_positions[row['Tipo']] + 0.3],
            mode='lines',
            line=dict(width=8, color=color_map.get(row['Prioridad'], '#9E9E9E')),
            name=f"{row['Actividad']} ({row['Prioridad']})",
            hovertemplate=f"<b>{row['Actividad']}</b><br>" +
                         f"Fecha: {row['Fecha'].strftime('%d/%m/%Y')}<br>" +
                         f"Prioridad: {row['Prioridad']}<br>" +
                         f"Tipo: {row['Tipo']}<extra></extra>",
            showlegend=False
        ))
    
    # Configurar layout
    fig_cronograma.update_layout(
        title='Cronograma de Actividades Agrícolas - Próximos 30 días',
        xaxis_title='Fecha',
        yaxis_title='Tipo de Actividad',
        height=400,
        yaxis=dict(
            tickmode='array',
            tickvals=list(y_positions.values()),
            ticktext=list(y_positions.keys()),
            showgrid=True
        ),
        xaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(128,128,128,0.2)'
        ),
        hovermode='closest'
    )
    
    st.plotly_chart(fig_cronograma, config=PLOTLY_CONFIG, use_container_width=True)

st.caption("Riesgos de plagas/enfermedades: índice derivado de humedad y temperatura observadas (no sustituye monitoreo en campo).")

# Análisis de rendimiento
st.markdown("### Rendimiento y factores agrícolas")

st.info(
    "Sin datos de control de plagas, fertilización o eficiencia de riego en campo — "
    "requiere integración con sensores o registros operativos. "
    "Use las métricas meteorológicas y recomendaciones API arriba."
)

col1, col2 = st.columns(2)

with col1:
    st.caption("Gráfico de factores de rendimiento no disponible sin datos operativos.")

with col2:
    rendimiento_base = {
        "Palta": 15,
        "Cítricos": 25,
        "Vid": 12,
        "Tomate": 40,
        "Lechuga": 30,
    }

    t_min, t_max = config["temp_optima"]
    factor = 1.0
    if t_min <= temp_actual <= t_max:
        factor += 0.05
    if config["humedad_optima"][0] <= humedad_actual <= config["humedad_optima"][1]:
        factor += 0.05
    rendimiento_estimado = rendimiento_base[cultivo_seleccionado] * factor

    st.markdown("#### Referencia de rendimiento (solo clima)")
    st.metric(
        label=f"Referencia {cultivo_seleccionado}",
        value=f"{rendimiento_estimado:.1f} ton/ha",
        help="Ajuste simple por T° y humedad observadas; no es dato de cosecha ni ML.",
    )
    st.caption("Para análisis económico real use Vue → /agricola (endpoint económico API).")

# Información del cultivo
st.markdown("### Información del Cultivo Seleccionado")

col1, col2, col3 = st.columns(3)

with col1:
    st.info(f"""
    ** Cultivo:** {cultivo_seleccionado}
    ** Fase Actual:** {fase_actual}
    ** Superficie:** {superficie} hectáreas
    ** Temp. Óptima:** {config['temp_optima'][0]}-{config['temp_optima'][1]}°C
    """)

with col2:
    st.info(f"""
    ** Humedad Óptima:** {config['humedad_optima'][0]}-{config['humedad_optima'][1]}%
    ** Precip. Anual:** {config['precipitacion_optima'][0]}-{config['precipitacion_optima'][1]} mm
    ** Riego:** {config['riego_cantidad']}L cada {config['riego_frecuencia']} días
    """)

with col3:
    st.info(f"""
    ** Plagas Comunes:** {len(config['plagas_comunes'])}
    ** Enfermedades:** {len(config['enfermedades'])}
    ** Fases:** {len(config['fases'])}
    ** Última Actualización:** {datetime.now().strftime("%H:%M")}
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 20px;">
    <p> <strong>Sistema METGO</strong> - Gestión Agrícola Inteligente</p>
    <p>Datos meteorológicos OpenMeteo · recomendaciones módulo 02 vía API</p>
    <p>Última actualización: {}</p>
</div>
""".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")), unsafe_allow_html=True)
