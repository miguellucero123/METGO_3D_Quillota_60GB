import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import random

# Configuración de la página optimizada para móviles
st.set_page_config(
    page_title="🔬 Sistema de Alertas Automáticas - METGO",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS personalizado para diseño móvil profesional
st.markdown("""
<style>
    /* Diseño móvil profesional para alertas */
    .alertas-header {
        background: linear-gradient(135deg, #e17055 0%, #d63031 100%);
        padding: 2rem 1rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    }
    
    .alerta-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        margin: 1rem 0;
        border-left: 5px solid;
        position: relative;
        overflow: hidden;
    }
    
    .alerta-critica {
        border-left-color: #e74c3c;
        background: linear-gradient(135deg, #fff5f5 0%, #ffeaea 100%);
    }
    
    .alerta-advertencia {
        border-left-color: #f39c12;
        background: linear-gradient(135deg, #fffbf0 0%, #fff7e6 100%);
    }
    
    .alerta-info {
        border-left-color: #3498db;
        background: linear-gradient(135deg, #f0f8ff 0%, #e6f3ff 100%);
    }
    
    .alerta-success {
        border-left-color: #27ae60;
        background: linear-gradient(135deg, #f0fff4 0%, #e6ffe6 100%);
    }
    
    .alerta-titulo {
        font-size: 1.2rem;
        font-weight: bold;
        color: #2c3e50;
        margin: 0 0 0.5rem 0;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .alerta-mensaje {
        color: #7f8c8d;
        margin: 0.5rem 0;
        line-height: 1.5;
    }
    
    .alerta-timestamp {
        color: #95a5a6;
        font-size: 0.9rem;
        margin-top: 0.5rem;
    }
    
    .alerta-accion {
        background: #2c3e50;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.9rem;
        margin-top: 1rem;
        display: inline-block;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .alerta-accion:hover {
        background: #34495e;
        transform: translateY(-2px);
    }
    
    .metric-alerta-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        margin: 0.5rem 0;
        text-align: center;
    }
    
    .metric-alerta-number {
        font-size: 2rem;
        font-weight: bold;
        color: #2c3e50;
        margin: 0;
    }
    
    .metric-alerta-label {
        color: #7f8c8d;
        font-size: 0.9rem;
        margin: 0.5rem 0;
    }
    
    .chart-alertas-container {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.08);
        margin: 1.5rem 0;
        border: 1px solid #e9ecef;
    }
    
    .section-title-alertas {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2c3e50;
        margin: 2rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 3px solid #e17055;
        display: inline-block;
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .alertas-header {
            padding: 1.5rem 0.5rem;
            margin-bottom: 1rem;
        }
        
        .alerta-card {
            padding: 1rem;
            margin: 0.5rem 0;
        }
        
        .metric-alerta-card {
            padding: 1rem;
        }
        
        .chart-alertas-container {
            padding: 1.5rem;
            margin: 1rem 0;
        }
    }
</style>
""", unsafe_allow_html=True)

# Header principal
st.markdown("""
<div class="alertas-header">
    <h1>🔬 Sistema de Alertas Automáticas</h1>
    <h3>Sistema METGO - Monitoreo Inteligente</h3>
    <p>Detección automática de anomalías, alertas inteligentes y respuesta inmediata</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### 🎛️ Panel de Control de Alertas")
    
    # Selector de tipo de alerta
    tipo_alerta = st.selectbox(
        "🚨 Tipo de Alerta:",
        ["Todas", "Críticas", "Advertencias", "Informativas", "Exitosas"],
        key="tipo_alerta"
    )
    
    # Selector de sistema
    sistema_alerta = st.selectbox(
        "🔧 Sistema:",
        ["Meteorológico", "Agrícola", "IoT", "Calidad", "Económico", "Todos"],
        key="sistema_alerta"
    )
    
    # Selector de período
    periodo_alerta = st.selectbox(
        "📅 Período:",
        ["Última hora", "Últimas 24 horas", "Última semana", "Último mes"],
        key="periodo_alerta"
    )

# Función para generar alertas automáticas
@st.cache_data
def generar_alertas_automaticas(tipo_alerta, sistema_alerta, periodo_alerta):
    """Genera alertas automáticas basadas en condiciones simuladas"""
    
    # Configuración de alertas
    tipos_alertas = {
        "Críticas": {
            "icono": "🔴",
            "color": "alerta-critica",
            "prioridad": 1,
            "umbral": 0.1
        },
        "Advertencias": {
            "icono": "🟡",
            "color": "alerta-advertencia",
            "prioridad": 2,
            "umbral": 0.3
        },
        "Informativas": {
            "icono": "🔵",
            "color": "alerta-info",
            "prioridad": 3,
            "umbral": 0.4
        },
        "Exitosas": {
            "icono": "🟢",
            "color": "alerta-success",
            "prioridad": 4,
            "umbral": 0.2
        }
    }
    
    # Configuración de sistemas
    sistemas_config = {
        "Meteorológico": {
            "alertas": [
                "Temperatura crítica detectada",
                "Precipitación intensa prevista",
                "Vientos fuertes en zona agrícola",
                "Humedad extrema registrada",
                "Presión atmosférica anómala"
            ]
        },
        "Agrícola": {
            "alertas": [
                "Rendimiento por debajo del umbral",
                "Plaga detectada en cultivos",
                "Enfermedad fúngica identificada",
                "Eficiencia de riego baja",
                "Calidad del producto comprometida"
            ]
        },
        "IoT": {
            "alertas": [
                "Sensor desconectado",
                "Batería baja en dispositivo",
                "Fallo de comunicación",
                "Temperatura del sensor alta",
                "Calibración requerida"
            ]
        },
        "Calidad": {
            "alertas": [
                "Parámetro fuera de rango",
                "Contaminación detectada",
                "Proceso fuera de control",
                "Calidad subóptima",
                "Desviación del estándar"
            ]
        },
        "Económico": {
            "alertas": [
                "Precio de mercado bajo",
                "Costo de producción alto",
                "Margen de ganancia crítico",
                "Demanda fluctuante",
                "Rentabilidad comprometida"
            ]
        }
    }
    
    # Generar alertas
    alertas = []
    timestamp_base = datetime.now()
    
    # Determinar cuántas alertas generar según el período
    periodos_map = {
        "Última hora": 1,
        "Últimas 24 horas": 24,
        "Última semana": 168,
        "Último mes": 720
    }
    
    horas_periodo = periodos_map[periodo_alerta]
    
    for i in range(random.randint(5, 15)):  # Entre 5 y 15 alertas
        # Seleccionar tipo de alerta
        tipo_seleccionado = random.choices(
            list(tipos_alertas.keys()),
            weights=[tipos_alertas[t]["umbral"] for t in tipos_alertas.keys()]
        )[0]
        
        # Seleccionar sistema
        sistema_seleccionado = random.choice(list(sistemas_config.keys()))
        
        # Verificar filtros
        if tipo_alerta != "Todas" and tipo_seleccionado != tipo_alerta:
            continue
        if sistema_alerta != "Todos" and sistema_seleccionado != sistema_alerta:
            continue
        
        # Seleccionar mensaje específico
        mensaje = random.choice(sistemas_config[sistema_seleccionado]["alertas"])
        
        # Generar timestamp aleatorio dentro del período
        horas_atras = random.uniform(0, horas_periodo)
        timestamp = timestamp_base - timedelta(hours=horas_atras)
        
        # Generar datos de la alerta
        alerta = {
            'timestamp': timestamp,
            'tipo': tipo_seleccionado,
            'sistema': sistema_seleccionado,
            'mensaje': mensaje,
            'prioridad': tipos_alertas[tipo_seleccionado]['prioridad'],
            'icono': tipos_alertas[tipo_seleccionado]['icono'],
            'color': tipos_alertas[tipo_seleccionado]['color'],
            'estado': random.choice(['Activa', 'Resuelta', 'En Proceso']),
            'responsable': random.choice(['Sistema Automático', 'Operador 1', 'Operador 2', 'Supervisor']),
            'accion_requerida': random.choice([
                'Verificación inmediata',
                'Acción correctiva',
                'Monitoreo continuo',
                'Notificación al equipo',
                'Intervención manual'
            ])
        }
        
        alertas.append(alerta)
    
    # Ordenar por timestamp (más recientes primero)
    alertas.sort(key=lambda x: x['timestamp'], reverse=True)
    
    return alertas

# Generar alertas
with st.spinner('🔬 Generando alertas automáticas...'):
    alertas = generar_alertas_automaticas(tipo_alerta, sistema_alerta, periodo_alerta)

# Métricas de alertas
st.markdown("### 📊 Métricas de Alertas")

col1, col2, col3, col4 = st.columns(4)

# Contar alertas por tipo
alertas_activas = len([a for a in alertas if a['estado'] == 'Activa'])
alertas_criticas = len([a for a in alertas if a['tipo'] == 'Críticas'])
alertas_resueltas = len([a for a in alertas if a['estado'] == 'Resuelta'])
tiempo_respuesta_promedio = random.uniform(15, 120)  # minutos

with col1:
    st.markdown(f"""
    <div class="metric-alerta-card">
        <div class="metric-alerta-number" style="color: #e74c3c;">{alertas_activas}</div>
        <div class="metric-alerta-label">🚨 Alertas Activas</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-alerta-card">
        <div class="metric-alerta-number" style="color: #f39c12;">{alertas_criticas}</div>
        <div class="metric-alerta-label">🔴 Críticas</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-alerta-card">
        <div class="metric-alerta-number" style="color: #27ae60;">{alertas_resueltas}</div>
        <div class="metric-alerta-label">✅ Resueltas</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="metric-alerta-card">
        <div class="metric-alerta-number" style="color: #3498db;">{tiempo_respuesta_promedio:.0f}m</div>
        <div class="metric-alerta-label">⏱️ Tiempo Respuesta</div>
    </div>
    """, unsafe_allow_html=True)

# Lista de alertas
st.markdown('<h2 class="section-title-alertas">🚨 Alertas Recientes</h2>', unsafe_allow_html=True)

# Mostrar alertas
for alerta in alertas[:10]:  # Mostrar las 10 más recientes
    st.markdown(f"""
    <div class="alerta-card {alerta['color']}">
        <div class="alerta-titulo">
            {alerta['icono']} {alerta['tipo']} - {alerta['sistema']}
        </div>
        <div class="alerta-mensaje">
            {alerta['mensaje']}
        </div>
        <div class="alerta-timestamp">
            📅 {alerta['timestamp'].strftime("%Y-%m-%d %H:%M:%S")} | 
            👤 {alerta['responsable']} | 
            📊 Estado: {alerta['estado']}
        </div>
        <div class="alerta-accion">
            🎯 {alerta['accion_requerida']}
        </div>
    </div>
    """, unsafe_allow_html=True)

# Análisis de tendencias de alertas
st.markdown('<h2 class="section-title-alertas">📈 Análisis de Tendencias</h2>', unsafe_allow_html=True)

# Generar datos de tendencias
fechas_tendencia = pd.date_range(end=datetime.now(), periods=24, freq='H')
tendencias_data = []

for fecha in fechas_tendencia:
    tendencias_data.append({
        'Hora': fecha,
        'Alertas_Criticas': random.randint(0, 5),
        'Alertas_Advertencia': random.randint(2, 8),
        'Alertas_Info': random.randint(1, 6),
        'Alertas_Exitosas': random.randint(0, 3)
    })

df_tendencias = pd.DataFrame(tendencias_data)

# Gráfico de tendencias
fig_tendencias = make_subplots(
    rows=2, cols=1,
    subplot_titles=('🚨 Alertas por Tipo - Últimas 24h', '📊 Distribución de Alertas'),
    vertical_spacing=0.1
)

# Líneas de tendencia
fig_tendencias.add_trace(
    go.Scatter(x=df_tendencias['Hora'], y=df_tendencias['Alertas_Criticas'],
              name='Críticas', line=dict(color='#e74c3c', width=3)),
    row=1, col=1
)

fig_tendencias.add_trace(
    go.Scatter(x=df_tendencias['Hora'], y=df_tendencias['Alertas_Advertencia'],
              name='Advertencias', line=dict(color='#f39c12', width=3)),
    row=1, col=1
)

fig_tendencias.add_trace(
    go.Scatter(x=df_tendencias['Hora'], y=df_tendencias['Alertas_Info'],
              name='Informativas', line=dict(color='#3498db', width=3)),
    row=1, col=1
)

# Gráfico de barras para distribución
tipos_distribucion = ['Críticas', 'Advertencias', 'Informativas', 'Exitosas']
cantidades_distribucion = [
    df_tendencias['Alertas_Criticas'].sum(),
    df_tendencias['Alertas_Advertencia'].sum(),
    df_tendencias['Alertas_Info'].sum(),
    df_tendencias['Alertas_Exitosas'].sum()
]

fig_tendencias.add_trace(
    go.Bar(x=tipos_distribucion, y=cantidades_distribucion,
           name='Total por Tipo', marker_color=['#e74c3c', '#f39c12', '#3498db', '#27ae60']),
    row=2, col=1
)

fig_tendencias.update_layout(height=600, showlegend=False,
                           title_text="📈 Análisis de Tendencias de Alertas")
fig_tendencias.update_xaxes(title_text="Hora", row=1, col=1)
fig_tendencias.update_xaxes(title_text="Tipo de Alerta", row=2, col=1)
fig_tendencias.update_yaxes(title_text="Cantidad de Alertas", row=1, col=1)
fig_tendencias.update_yaxes(title_text="Total", row=2, col=1)

st.plotly_chart(fig_tendencias, use_container_width=True)

# Análisis por sistema
st.markdown('<h2 class="section-title-alertas">🔧 Análisis por Sistema</h2>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    # Alertas por sistema
    sistemas_alertas = {}
    for alerta in alertas:
        sistema = alerta['sistema']
        if sistema not in sistemas_alertas:
            sistemas_alertas[sistema] = 0
        sistemas_alertas[sistema] += 1
    
    fig_sistemas = px.pie(values=list(sistemas_alertas.values()),
                         names=list(sistemas_alertas.keys()),
                         title='🔧 Distribución de Alertas por Sistema',
                         color_discrete_sequence=px.colors.qualitative.Set3)
    st.plotly_chart(fig_sistemas, use_container_width=True)

with col2:
    # Estado de alertas
    estados_alertas = {}
    for alerta in alertas:
        estado = alerta['estado']
        if estado not in estados_alertas:
            estados_alertas[estado] = 0
        estados_alertas[estado] += 1
    
    fig_estados = px.bar(x=list(estados_alertas.keys()),
                        y=list(estados_alertas.values()),
                        title='📊 Estado de Alertas',
                        color=list(estados_alertas.keys()),
                        color_discrete_map={
                            'Activa': '#e74c3c',
                            'En Proceso': '#f39c12',
                            'Resuelta': '#27ae60'
                        })
    st.plotly_chart(fig_estados, use_container_width=True)

# Panel de control de alertas
st.markdown('<h2 class="section-title-alertas">🎛️ Panel de Control</h2>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("#### 🔧 Acciones del Sistema")
    
    if st.button("🔄 Actualizar Alertas"):
        st.success("Alertas actualizadas correctamente")
    
    if st.button("🔕 Silenciar Alertas"):
        st.warning("Alertas silenciadas por 1 hora")
    
    if st.button("📧 Enviar Reporte"):
        st.info("Reporte enviado por email")

with col2:
    st.markdown("#### ⚙️ Configuración")
    
    if st.button("🎯 Configurar Umbrales"):
        st.info("Panel de configuración abierto")
    
    if st.button("👥 Gestionar Usuarios"):
        st.info("Gestión de usuarios activada")
    
    if st.button("🔔 Configurar Notificaciones"):
        st.info("Configuración de notificaciones")

with col3:
    st.markdown("#### 📊 Reportes")
    
    if st.button("📈 Generar Reporte Diario"):
        st.success("Reporte diario generado")
    
    if st.button("📅 Reporte Semanal"):
        st.success("Reporte semanal generado")
    
    if st.button("📋 Exportar Datos"):
        st.success("Datos exportados correctamente")

# Información del sistema de alertas
st.markdown('<h2 class="section-title-alertas">ℹ️ Información del Sistema</h2>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.info(f"""
    **🚨 Tipo de Alerta:** {tipo_alerta}
    **🔧 Sistema:** {sistema_alerta}
    **📅 Período:** {periodo_alerta}
    **🕐 Total Alertas:** {len(alertas)}
    """)

with col2:
    st.info(f"""
    **📊 Datos Generados:** {datetime.now().strftime("%H:%M:%S")}
    **🔄 Actualización:** Automática
    **📱 Optimizado:** Móvil
    **🎨 Diseño:** Profesional Alertas
    """)

with col3:
    st.info(f"""
    **🚨 Activas:** {alertas_activas}
    **🔴 Críticas:** {alertas_criticas}
    **✅ Resueltas:** {alertas_resueltas}
    **⏱️ Respuesta Promedio:** {tiempo_respuesta_promedio:.0f} min
    """)

# Footer profesional
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 20px; background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); border-radius: 10px;">
    <p>🔬 <strong>Sistema METGO</strong> - Sistema de Alertas Automáticas</p>
    <p>Monitoreo inteligente con detección automática de anomalías</p>
    <p>Última actualización: {}</p>
</div>
""".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")), unsafe_allow_html=True)
