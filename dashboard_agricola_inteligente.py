import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import random

# Configuración de la página
st.set_page_config(
    page_title="🌾 Gestión Agrícola Inteligente - METGO",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Título principal
st.markdown("""
<div style="text-align: center; padding: 20px; background: linear-gradient(135deg, #4CAF50 0%, #2E7D32 100%); color: white; border-radius: 15px; margin-bottom: 30px;">
    <h1>🌾 Gestión Agrícola Inteligente</h1>
    <h3>Sistema METGO - Recomendaciones por IA</h3>
    <p>Análisis inteligente de cultivos, plagas, riego y factores climáticos</p>
</div>
""", unsafe_allow_html=True)

# Sidebar para controles
st.sidebar.markdown("### 🎛️ Panel de Control Agrícola")

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

cultivo_seleccionado = st.sidebar.selectbox("🌱 Cultivo:", list(cultivos_config.keys()))
fase_actual = st.sidebar.selectbox("📅 Fase Actual:", cultivos_config[cultivo_seleccionado]["fases"])
superficie = st.sidebar.number_input("📏 Superficie (hectáreas):", min_value=0.1, max_value=1000.0, value=1.0, step=0.1)

# Función para generar recomendaciones IA
def generar_recomendaciones_ia(cultivo, fase, superficie, temp_actual, humedad_actual, precipitacion_actual):
    """Genera recomendaciones inteligentes basadas en IA"""
    
    config = cultivos_config[cultivo]
    recomendaciones = []
    alertas = []
    
    # Análisis de temperatura
    temp_min, temp_max = config["temp_optima"]
    if temp_actual < temp_min:
        recomendaciones.append(f"🌡️ **Temperatura baja**: Considerar protección contra heladas o calefacción")
        alertas.append({"tipo": "Helada", "severidad": "Alta", "mensaje": "Riesgo de helada detectado"})
    elif temp_actual > temp_max:
        recomendaciones.append(f"🌡️ **Temperatura alta**: Incrementar riego y considerar sombreado")
        alertas.append({"tipo": "Calor", "severidad": "Media", "mensaje": "Estrés térmico en cultivos"})
    else:
        recomendaciones.append(f"🌡️ **Temperatura óptima**: Condiciones ideales para {cultivo}")
    
    # Análisis de humedad
    hum_min, hum_max = config["humedad_optima"]
    if humedad_actual < hum_min:
        recomendaciones.append(f"💧 **Humedad baja**: Incrementar frecuencia de riego")
        alertas.append({"tipo": "Sequía", "severidad": "Media", "mensaje": "Condiciones de sequía"})
    elif humedad_actual > hum_max:
        recomendaciones.append(f"💧 **Humedad alta**: Reducir riego y mejorar ventilación")
        alertas.append({"tipo": "Exceso Humedad", "severidad": "Baja", "mensaje": "Riesgo de enfermedades fúngicas"})
    
    # Recomendaciones de riego
    riego_cantidad = config["riego_cantidad"] * superficie
    riego_frecuencia = config["riego_frecuencia"]
    recomendaciones.append(f"💧 **Riego**: {riego_cantidad:.1f}L cada {riego_frecuencia} días")
    
    # Recomendaciones de plagas
    plagas_activas = random.sample(config["plagas_comunes"], min(2, len(config["plagas_comunes"])))
    for plaga in plagas_activas:
        recomendaciones.append(f"🐛 **Control de {plaga}**: Monitorear y aplicar tratamiento preventivo")
        alertas.append({"tipo": "Plaga", "severidad": "Media", "mensaje": f"Presencia de {plaga}"})
    
    # Recomendaciones de enfermedades
    enfermedades_activas = random.sample(config["enfermedades"], min(1, len(config["enfermedades"])))
    for enfermedad in enfermedades_activas:
        recomendaciones.append(f"🦠 **Prevención {enfermedad}**: Aplicar fungicida preventivo")
        alertas.append({"tipo": "Enfermedad", "severidad": "Alta", "mensaje": f"Riesgo de {enfermedad}"})
    
    # Recomendaciones específicas por fase
    if fase == "Floración":
        recomendaciones.append("🌸 **Fase de Floración**: Evitar riego excesivo y aplicar fertilizante rico en fósforo")
    elif fase == "Crecimiento":
        recomendaciones.append("🌱 **Fase de Crecimiento**: Mantener riego constante y aplicar fertilizante balanceado")
    elif fase == "Maduración":
        recomendaciones.append("🍎 **Fase de Maduración**: Reducir riego y preparar para cosecha")
    elif fase == "Cosecha":
        recomendaciones.append("🚜 **Cosecha**: Programar cosecha en condiciones óptimas de humedad")
    
    return recomendaciones, alertas

# Simular datos ambientales actuales
temp_actual = 22.5 + np.random.normal(0, 3)
humedad_actual = 65 + np.random.normal(0, 10)
precipitacion_actual = np.random.exponential(0.5)

# Generar recomendaciones
recomendaciones, alertas = generar_recomendaciones_ia(
    cultivo_seleccionado, fase_actual, superficie, 
    temp_actual, humedad_actual, precipitacion_actual
)

# Métricas principales
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="🌡️ Temperatura Actual",
        value=f"{temp_actual:.1f}°C",
        delta=f"{temp_actual - cultivos_config[cultivo_seleccionado]['temp_optima'][0]:.1f}°C"
    )

with col2:
    st.metric(
        label="💧 Humedad Relativa",
        value=f"{humedad_actual:.1f}%",
        delta=f"{humedad_actual - cultivos_config[cultivo_seleccionado]['humedad_optima'][0]:.1f}%"
    )

with col3:
    st.metric(
        label="🌧️ Precipitación 24h",
        value=f"{precipitacion_actual:.1f} mm",
        delta="+0.2 mm"
    )

with col4:
    config = cultivos_config[cultivo_seleccionado]
    riego_total = config["riego_cantidad"] * superficie
    st.metric(
        label="💧 Riego Recomendado",
        value=f"{riego_total:.1f} L",
        delta=f"Cada {config['riego_frecuencia']} días"
    )

# Sistema de Alertas y Recomendaciones Profesional
st.markdown("""
<div style="background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); color: white; padding: 20px; border-radius: 15px; margin: 20px 0;">
    <h2 style="margin: 0; text-align: center;">🚨 Sistema de Alertas y Recomendaciones Empresarial</h2>
    <p style="margin: 10px 0 0 0; text-align: center; opacity: 0.9;">Monitoreo inteligente y comunicación automatizada</p>
</div>
""", unsafe_allow_html=True)

# Panel de control de notificaciones
st.markdown("### 📱 Panel de Control de Notificaciones")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("#### 📧 Email")
    email_enabled = st.checkbox("Activar Email", value=True, key="email_alerts")
    email_address = st.text_input("Dirección Email", value="agricola@metgo.cl", key="email_address")

with col2:
    st.markdown("#### 📱 SMS")
    sms_enabled = st.checkbox("Activar SMS", value=True, key="sms_alerts")
    phone_number = st.text_input("Número Teléfono", value="+56 9 1234 5678", key="phone_number")

with col3:
    st.markdown("#### 💬 WhatsApp")
    whatsapp_enabled = st.checkbox("Activar WhatsApp", value=True, key="whatsapp_alerts")
    whatsapp_number = st.text_input("WhatsApp Business", value="+56 9 8765 4321", key="whatsapp_number")

with col4:
    st.markdown("#### ⚙️ Configuración")
    alert_frequency = st.selectbox("Frecuencia", ["Inmediata", "Cada hora", "Diaria", "Semanal"], key="alert_freq")
    priority_filter = st.selectbox("Prioridad Mínima", ["Alta", "Media", "Baja"], key="priority_filter")

# Dashboard de alertas profesional
st.markdown("### 📊 Dashboard de Alertas Empresarial")

# Métricas de alertas
col1, col2, col3, col4 = st.columns(4)

total_alertas = len(alertas)
alertas_altas = len([a for a in alertas if a["severidad"] == "Alta"])
alertas_medias = len([a for a in alertas if a["severidad"] == "Media"])
alertas_bajas = len([a for a in alertas if a["severidad"] == "Baja"])

with col1:
    st.metric("🚨 Total Alertas", total_alertas, delta=f"Últimas 24h")
    
with col2:
    st.metric("🔴 Críticas", alertas_altas, delta="Requieren acción inmediata" if alertas_altas > 0 else "Sin alertas críticas")
    
with col3:
    st.metric("🟡 Medias", alertas_medias, delta="Monitoreo recomendado" if alertas_medias > 0 else "Sistema estable")
    
with col4:
    st.metric("🟢 Bajas", alertas_bajas, delta="Rutina normal" if alertas_bajas > 0 else "Sin incidencias")

# Tabla profesional de alertas
st.markdown("#### 📋 Tabla de Alertas Detallada")

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
    st.success("✅ No hay alertas activas en este momento")

# Sistema de recomendaciones profesional
st.markdown("#### 🎯 Recomendaciones Estratégicas IA")

if recomendaciones:
    for i, rec in enumerate(recomendaciones, 1):
        with st.container():
            st.markdown(f"""
            <div style="border-left: 4px solid #4CAF50; padding: 15px; margin: 10px 0; background-color: #f8f9fa; border-radius: 5px;">
                <h4 style="margin: 0 0 10px 0; color: #2E7D32;">🎯 Recomendación #{i}</h4>
                <p style="margin: 0; color: #333;">{rec}</p>
            </div>
            """, unsafe_allow_html=True)

# Botones de acción empresarial
st.markdown("### 🚀 Acciones Empresariales")

col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("📧 Enviar Reporte por Email", type="primary", use_container_width=True):
        if email_enabled and email_address:
            st.success(f"✅ Reporte enviado a {email_address}")
        else:
            st.error("❌ Email no configurado")

with col2:
    if st.button("📱 Enviar Alerta SMS", type="secondary", use_container_width=True):
        if sms_enabled and phone_number:
            st.success(f"✅ SMS enviado a {phone_number}")
        else:
            st.error("❌ SMS no configurado")

with col3:
    if st.button("💬 Enviar por WhatsApp", type="secondary", use_container_width=True):
        if whatsapp_enabled and whatsapp_number:
            st.success(f"✅ Mensaje WhatsApp enviado a {whatsapp_number}")
        else:
            st.error("❌ WhatsApp no configurado")

with col4:
    if st.button("📊 Generar Reporte Ejecutivo", type="primary", use_container_width=True):
        st.success("✅ Reporte ejecutivo generado y guardado")

# Panel de configuración avanzada
with st.expander("⚙️ Configuración Avanzada de Notificaciones"):
    st.markdown("#### 🔧 Configuraciones Empresariales")
    
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
        plantilla_whatsapp = st.text_area("Plantilla WhatsApp", value="🚨 *Alerta METGO*\\n\\n*Tipo:* {tipo}\\n*Mensaje:* {mensaje}\\n*Fecha:* {fecha}")
    
    if st.button("💾 Guardar Configuración", type="primary"):
        st.success("✅ Configuración guardada correctamente")

# Análisis detallado de alertas y recomendaciones
st.markdown("### 🔍 Análisis Detallado de Alertas y Recomendaciones")

# Tabs para diferentes aspectos del análisis
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Estadísticas", "🎯 Recomendaciones Detalladas", "📈 Tendencias", "🔧 Acciones Automáticas", "📋 Historial"])

with tab1:
    st.markdown("#### 📊 Estadísticas Avanzadas de Alertas")
    
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
            st.plotly_chart(fig_tipos, use_container_width=True)
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
            st.plotly_chart(fig_severidad, use_container_width=True)
        else:
            st.info("No hay alertas para mostrar estadísticas")
    
    # Métricas adicionales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("⏱️ Tiempo Promedio Respuesta", "2.3h", delta="-15min vs ayer")
    
    with col2:
        st.metric("🎯 Tasa de Resolución", "87%", delta="+3% vs mes anterior")
    
    with col3:
        st.metric("🔄 Alertas Recurrentes", "12%", delta="-2% vs semana anterior")
    
    with col4:
        st.metric("⚡ Eficiencia Sistema", "94%", delta="+1% vs ayer")

with tab2:
    st.markdown("#### 🎯 Recomendaciones Estratégicas Detalladas")
    
    if recomendaciones:
        for i, rec in enumerate(recomendaciones, 1):
            with st.expander(f"🎯 Recomendación #{i}: {rec[:50]}..."):
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
                    if st.button(f"✅ Aplicar Rec #{i}", key=f"aplicar_{i}"):
                        st.success(f"Recomendación #{i} marcada como aplicada")
                
                with col2:
                    if st.button(f"⏰ Programar Rec #{i}", key=f"programar_{i}"):
                        st.info(f"Recomendación #{i} programada para revisión")
                
                with col3:
                    if st.button(f"❌ Descartar Rec #{i}", key=f"descartar_{i}"):
                        st.warning(f"Recomendación #{i} descartada")

with tab3:
    st.markdown("#### 📈 Tendencias y Patrones de Alertas")
    
    # Simulación de datos históricos para tendencias
    fechas = pd.date_range(start=datetime.now() - timedelta(days=30), end=datetime.now(), freq='D')
    
    # Generar datos de tendencia simulados
    alertas_historicas = []
    for fecha in fechas:
        alertas_historicas.append({
            'fecha': fecha,
            'alertas_criticas': random.randint(0, 3),
            'alertas_medias': random.randint(0, 5),
            'alertas_bajas': random.randint(0, 8),
            'temperatura': random.uniform(15, 25),
            'humedad': random.uniform(40, 80)
        })
    
    df_tendencias = pd.DataFrame(alertas_historicas)
    
    # Gráfico de tendencias de alertas
    fig_tendencias = go.Figure()
    
    fig_tendencias.add_trace(go.Scatter(
        x=df_tendencias['fecha'],
        y=df_tendencias['alertas_criticas'],
        mode='lines+markers',
        name='Alertas Críticas',
        line=dict(color='#F44336', width=3)
    ))
    
    fig_tendencias.add_trace(go.Scatter(
        x=df_tendencias['fecha'],
        y=df_tendencias['alertas_medias'],
        mode='lines+markers',
        name='Alertas Medias',
        line=dict(color='#FF9800', width=3)
    ))
    
    fig_tendencias.add_trace(go.Scatter(
        x=df_tendencias['fecha'],
        y=df_tendencias['alertas_bajas'],
        mode='lines+markers',
        name='Alertas Bajas',
        line=dict(color='#4CAF50', width=3)
    ))
    
    fig_tendencias.update_layout(
        title="Tendencia de Alertas - Últimos 30 Días",
        xaxis_title="Fecha",
        yaxis_title="Número de Alertas",
        height=400,
        hovermode='x unified'
    )
    
    st.plotly_chart(fig_tendencias, use_container_width=True)
    
    # Análisis de correlación
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Correlación con Variables Climáticas:**")
        
        # Correlación con temperatura
        corr_temp = df_tendencias['alertas_criticas'].corr(df_tendencias['temperatura'])
        st.metric("🌡️ Correlación con Temperatura", f"{corr_temp:.2f}", 
                 delta="Positiva" if corr_temp > 0 else "Negativa")
        
        # Correlación con humedad
        corr_hum = df_tendencias['alertas_medias'].corr(df_tendencias['humedad'])
        st.metric("💧 Correlación con Humedad", f"{corr_hum:.2f}", 
                 delta="Positiva" if corr_hum > 0 else "Negativa")
    
    with col2:
        st.markdown("**Patrones Identificados:**")
        
        # Análisis de patrones
        promedio_criticas = df_tendencias['alertas_criticas'].mean()
        st.metric("📊 Promedio Alertas Críticas/Día", f"{promedio_criticas:.1f}")
        
        dias_alta_actividad = len(df_tendencias[df_tendencias['alertas_criticas'] > promedio_criticas * 1.5])
        st.metric("⚠️ Días de Alta Actividad", f"{dias_alta_actividad} de 30")

with tab4:
    st.markdown("#### 🔧 Configuración de Acciones Automáticas")
    
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
            estado = "🟢 Activa" if regla['activa'] else "🔴 Inactiva"
            st.write(f"**Estado:** {estado}")
        
        with col4:
            if st.button("⚙️", key=f"config_regla_{i}"):
                st.info(f"Configurando regla #{i}")

with tab5:
    st.markdown("#### 📋 Historial de Alertas y Acciones")
    
    # Simulación de historial
    historial_data = []
    for i in range(50):
        fecha = datetime.now() - timedelta(days=random.randint(0, 30))
        historial_data.append({
            'Fecha': fecha.strftime('%d/%m/%Y %H:%M'),
            'Tipo': random.choice(['Temperatura', 'Humedad', 'Plagas', 'Riego', 'Fertilización']),
            'Severidad': random.choice(['Alta', 'Media', 'Baja']),
            'Mensaje': f"Alerta {i+1}: Condición detectada",
            'Estado': random.choice(['Resuelta', 'Pendiente', 'En Proceso']),
            'Acción Tomada': random.choice(['Notificación enviada', 'Riego activado', 'Técnico contactado', 'Sin acción']),
            'Tiempo Resolución': f"{random.randint(1, 24)}h"
        })
    
    df_historial = pd.DataFrame(historial_data)
    
    # Filtros para el historial
    col1, col2, col3 = st.columns(3)
    
    with col1:
        filtro_tipo = st.selectbox("Filtrar por Tipo", ["Todos"] + list(df_historial['Tipo'].unique()))
    
    with col2:
        filtro_severidad = st.selectbox("Filtrar por Severidad", ["Todos"] + list(df_historial['Severidad'].unique()))
    
    with col3:
        filtro_estado = st.selectbox("Filtrar por Estado", ["Todos"] + list(df_historial['Estado'].unique()))
    
    # Aplicar filtros
    df_filtrado = df_historial.copy()
    
    if filtro_tipo != "Todos":
        df_filtrado = df_filtrado[df_filtrado['Tipo'] == filtro_tipo]
    
    if filtro_severidad != "Todos":
        df_filtrado = df_filtrado[df_filtrado['Severidad'] == filtro_severidad]
    
    if filtro_estado != "Todos":
        df_filtrado = df_filtrado[df_filtrado['Estado'] == filtro_estado]
    
    # Mostrar historial filtrado
    st.dataframe(
        df_filtrado,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Fecha": "Fecha/Hora",
            "Tipo": "Tipo de Alerta",
            "Severidad": "Prioridad",
            "Mensaje": "Descripción",
            "Estado": "Estado",
            "Acción Tomada": "Acción Realizada",
            "Tiempo Resolución": "Tiempo de Resolución"
        }
    )
    
    # Estadísticas del historial
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📊 Total Registros", len(df_filtrado))
    
    with col2:
        resueltas = len(df_filtrado[df_filtrado['Estado'] == 'Resuelta'])
        st.metric("✅ Resueltas", resueltas)
    
    with col3:
        pendientes = len(df_filtrado[df_filtrado['Estado'] == 'Pendiente'])
        st.metric("⏳ Pendientes", pendientes)
    
    with col4:
        tiempo_promedio = df_filtrado[df_filtrado['Estado'] == 'Resuelta']['Tiempo Resolución'].str.extract('(\d+)').astype(int).mean()[0]
        st.metric("⏱️ Tiempo Promedio", f"{tiempo_promedio:.1f}h" if not pd.isna(tiempo_promedio) else "N/A")

# Análisis de cultivos
st.markdown("### 📊 Análisis de Cultivos")

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
    title=f'🌾 Condiciones para {cultivo_seleccionado} - {fase_actual}',
    barmode='group',
    height=400
)

st.plotly_chart(fig_condiciones, use_container_width=True)

# Análisis de plagas y enfermedades
col1, col2 = st.columns(2)

with col1:
    st.markdown("#### 🐛 Análisis de Plagas")
    
    plagas_data = []
    for plaga in config["plagas_comunes"]:
        riesgo = random.choice(["Bajo", "Medio", "Alto"])
        plagas_data.append({
            "Plaga": plaga,
            "Riesgo": riesgo,
            "Probabilidad": random.randint(20, 90)
        })
    
    df_plagas = pd.DataFrame(plagas_data)
    
    fig_plagas = px.bar(df_plagas, x='Plaga', y='Probabilidad', 
                       color='Riesgo', 
                       color_discrete_map={'Bajo': '#4CAF50', 'Medio': '#FF9800', 'Alto': '#F44336'},
                       title='Probabilidad de Aparición de Plagas')
    st.plotly_chart(fig_plagas, use_container_width=True)

with col2:
    st.markdown("#### 🦠 Análisis de Enfermedades")
    
    enfermedades_data = []
    for enfermedad in config["enfermedades"]:
        riesgo = random.choice(["Bajo", "Medio", "Alto"])
        enfermedades_data.append({
            "Enfermedad": enfermedad,
            "Riesgo": riesgo,
            "Probabilidad": random.randint(15, 85)
        })
    
    df_enfermedades = pd.DataFrame(enfermedades_data)
    
    fig_enfermedades = px.bar(df_enfermedades, x='Enfermedad', y='Probabilidad', 
                             color='Riesgo',
                             color_discrete_map={'Bajo': '#4CAF50', 'Medio': '#FF9800', 'Alto': '#F44336'},
                             title='Probabilidad de Aparición de Enfermedades')
    st.plotly_chart(fig_enfermedades, use_container_width=True)

# Cronograma de actividades
st.markdown("### 📅 Cronograma de Actividades Agrícolas")

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
    
    st.plotly_chart(fig_cronograma, use_container_width=True)

# Análisis de rendimiento
st.markdown("### 📈 Análisis de Rendimiento Predicho")

col1, col2 = st.columns(2)

with col1:
    # Factores que afectan el rendimiento
    factores = {
        'Temperatura': temp_actual,
        'Humedad': humedad_actual,
        'Precipitación': precipitacion_actual,
        'Control de Plagas': 85,
        'Fertilización': 90,
        'Riego': 88
    }
    
    fig_factores = px.pie(values=list(factores.values()), 
                         names=list(factores.keys()),
                         title='Factores de Rendimiento (%)')
    st.plotly_chart(fig_factores, use_container_width=True)

with col2:
    # Predicción de rendimiento
    rendimiento_base = {
        "Palta": 15,
        "Cítricos": 25,
        "Vid": 12,
        "Tomate": 40,
        "Lechuga": 30
    }
    
    rendimiento_estimado = rendimiento_base[cultivo_seleccionado] * (1 + random.uniform(-0.2, 0.3))
    
    st.markdown("#### 📊 Rendimiento Estimado")
    st.metric(
        label=f"Producción de {cultivo_seleccionado}",
        value=f"{rendimiento_estimado:.1f} ton/ha",
        delta=f"{rendimiento_estimado - rendimiento_base[cultivo_seleccionado]:.1f} ton/ha"
    )
    
    st.markdown("#### 💰 Análisis Económico")
    precio_estimado = random.uniform(800, 1500)  # $ por tonelada
    ingreso_estimado = rendimiento_estimado * precio_estimado * superficie
    
    st.metric(
        label="Ingreso Estimado",
        value=f"${ingreso_estimado:,.0f}",
        delta=f"Precio: ${precio_estimado:.0f}/ton"
    )

# Información del cultivo
st.markdown("### 🌱 Información del Cultivo Seleccionado")

col1, col2, col3 = st.columns(3)

with col1:
    st.info(f"""
    **🌱 Cultivo:** {cultivo_seleccionado}
    **📅 Fase Actual:** {fase_actual}
    **📏 Superficie:** {superficie} hectáreas
    **🌡️ Temp. Óptima:** {config['temp_optima'][0]}-{config['temp_optima'][1]}°C
    """)

with col2:
    st.info(f"""
    **💧 Humedad Óptima:** {config['humedad_optima'][0]}-{config['humedad_optima'][1]}%
    **🌧️ Precip. Anual:** {config['precipitacion_optima'][0]}-{config['precipitacion_optima'][1]} mm
    **💧 Riego:** {config['riego_cantidad']}L cada {config['riego_frecuencia']} días
    """)

with col3:
    st.info(f"""
    **🐛 Plagas Comunes:** {len(config['plagas_comunes'])}
    **🦠 Enfermedades:** {len(config['enfermedades'])}
    **📅 Fases:** {len(config['fases'])}
    **⏱️ Última Actualización:** {datetime.now().strftime("%H:%M")}
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 20px;">
    <p>🌾 <strong>Sistema METGO</strong> - Gestión Agrícola Inteligente</p>
    <p>Recomendaciones generadas por Inteligencia Artificial</p>
    <p>Última actualización: {}</p>
</div>
""".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")), unsafe_allow_html=True)
