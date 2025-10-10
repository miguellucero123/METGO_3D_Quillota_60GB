"""
DASHBOARD UNIFICADO METGO 3D QUILLOTA CON INTEGRACIÓN DE DRONES
Dashboard principal que integra todos los sistemas: meteorológico, ML, riego, drones y expansión regional
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import json
import sqlite3
from datetime import datetime, timedelta
import os
import sys

# Importar sistemas
from sistema_drones_agricolas_metgo_optimizado import SistemaDronesAgricolasMetgoOptimizado
from expansion_regional_casablanca_metgo import ExpansionRegionalCasablancaMetgo

# Configuración de la página
st.set_page_config(
    page_title="METGO 3D - Dashboard Unificado",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        border-left: 4px solid #2E8B57;
    }
    
    .drone-card {
        background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    
    .status-excellent { color: #4CAF50; font-weight: bold; }
    .status-good { color: #8BC34A; font-weight: bold; }
    .status-regular { color: #FF9800; font-weight: bold; }
    .status-bad { color: #F44336; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

class DashboardUnificadoMetgo:
    def __init__(self):
        self.sistema_drones = SistemaDronesAgricolasMetgoOptimizado()
        self.expansion_casablanca = ExpansionRegionalCasablancaMetgo()
        
    def mostrar_header(self):
        """Mostrar header principal del dashboard"""
        st.markdown("""
        <div class="main-header">
            <h1>🌱 METGO 3D QUILLOTA - DASHBOARD UNIFICADO</h1>
            <p>Sistema Integrado de Monitoreo Agrícola con Drones, ML y Expansión Regional</p>
            <p>Actualizado: """ + datetime.now().strftime("%d/%m/%Y %H:%M") + """</p>
        </div>
        """, unsafe_allow_html=True)
    
    def mostrar_sidebar(self):
        """Mostrar sidebar con navegación"""
        st.sidebar.title("🧭 Navegación")
        
        opciones = [
            "🏠 Dashboard Principal",
            "🛰️ Sistema de Drones",
            "🌍 Expansión Casablanca",
            "📊 Análisis Meteorológico",
            "🤖 Machine Learning",
            "💧 Riego Inteligente",
            "📱 Aplicación Móvil",
            "📈 Reportes"
        ]
        
        seleccion = st.sidebar.selectbox("Seleccionar módulo:", opciones)
        
        # Información del sistema
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 📊 Estado del Sistema")
        
        # Verificar estado de componentes
        estado_drones = self.verificar_estado_drones()
        estado_casablanca = self.verificar_estado_casablanca()
        
        st.sidebar.markdown(f"🛰️ Drones: {estado_drones}")
        st.sidebar.markdown(f"🌍 Casablanca: {estado_casablanca}")
        st.sidebar.markdown(f"📊 Base de datos: ✅ Activa")
        
        return seleccion
    
    def verificar_estado_drones(self):
        """Verificar estado del sistema de drones"""
        try:
            if os.path.exists("sistema_drones_agricolas_optimizado.db"):
                return "✅ Activo"
            else:
                return "⚠️ Inactivo"
        except:
            return "❌ Error"
    
    def verificar_estado_casablanca(self):
        """Verificar estado de la expansión Casablanca"""
        try:
            if os.path.exists("expansion_casablanca_metgo.db"):
                return "✅ Activo"
            else:
                return "⚠️ Inactivo"
        except:
            return "❌ Error"
    
    def mostrar_dashboard_principal(self):
        """Mostrar dashboard principal con resumen de todos los sistemas"""
        st.header("🏠 Dashboard Principal")
        
        # Métricas principales
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="🛰️ Vuelos de Drones",
                value=self.obtener_total_vuelos(),
                delta="+3 hoy"
            )
        
        with col2:
            st.metric(
                label="🌍 Estaciones Casablanca",
                value="5",
                delta="Nuevas"
            )
        
        with col3:
            st.metric(
                label="📊 Cultivos Monitoreados",
                value="8",
                delta="+2 esta semana"
            )
        
        with col4:
            st.metric(
                label="🎯 Recomendaciones",
                value=self.obtener_total_recomendaciones(),
                delta="+12 hoy"
            )
        
        # Gráficos principales
        st.markdown("### 📊 Resumen de Actividad")
        
        col1, col2 = st.columns(2)
        
        with col1:
            self.mostrar_grafico_vuelos_recientes()
        
        with col2:
            self.mostrar_grafico_salud_cultivos()
        
        # Alertas y notificaciones
        st.markdown("### 🚨 Alertas y Notificaciones")
        self.mostrar_alertas_activas()
    
    def mostrar_sistema_drones(self):
        """Mostrar interfaz del sistema de drones"""
        st.header("🛰️ Sistema de Drones Agrícolas")
        
        # Panel de control de drones
        st.markdown("### 🎮 Panel de Control")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("#### Programar Nuevo Vuelo")
            
            col_drone, col_cultivo = st.columns(2)
            
            with col_drone:
                drone_seleccionado = st.selectbox(
                    "Seleccionar Drone:",
                    ["dji_mini_3", "dji_air_2s", "dji_phantom_4"],
                    format_func=lambda x: {
                        "dji_mini_3": "DJI Mini 3",
                        "dji_air_2s": "DJI Air 2S", 
                        "dji_phantom_4": "DJI Phantom 4"
                    }[x]
                )
            
            with col_cultivo:
                cultivo_seleccionado = st.selectbox(
                    "Tipo de Cultivo:",
                    ["palto", "uva", "citricos"],
                    format_func=lambda x: {
                        "palto": "Palto (Aguacate)",
                        "uva": "Uva de Mesa",
                        "citricos": "Cítricos"
                    }[x]
                )
            
            ubicacion = st.text_input("Ubicación:", value="Quillota Centro")
            area_hectareas = st.slider("Área (hectáreas):", 1.0, 50.0, 5.0)
            
            if st.button("🚀 Ejecutar Vuelo", type="primary"):
                with st.spinner("Ejecutando vuelo de drone..."):
                    resultado = self.sistema_drones.simular_vuelo_drone_rapido(
                        drone_seleccionado,
                        ubicacion,
                        cultivo_seleccionado,
                        area_hectareas
                    )
                    
                    if 'error' not in resultado:
                        st.success("✅ Vuelo completado exitosamente!")
                        
                        # Mostrar resultados
                        col_resultado1, col_resultado2 = st.columns(2)
                        
                        with col_resultado1:
                            st.markdown("#### 📊 Resultados del Vuelo")
                            st.write(f"**Duración:** {resultado['duracion_vuelo_minutos']} minutos")
                            st.write(f"**Fotos capturadas:** {resultado['numero_fotos']}")
                            st.write(f"**Área monitoreada:** {resultado['area_hectareas']} hectáreas")
                        
                        with col_resultado2:
                            st.markdown("#### 🌱 Análisis de Salud")
                            salud = resultado['analisis']['salud_general']
                            ndvi = resultado['analisis']['ndvi_promedio']
                            
                            if salud == "Excelente":
                                st.markdown(f"**Estado:** <span class='status-excellent'>{salud}</span>", unsafe_allow_html=True)
                            elif salud == "Buena":
                                st.markdown(f"**Estado:** <span class='status-good'>{salud}</span>", unsafe_allow_html=True)
                            elif salud == "Regular":
                                st.markdown(f"**Estado:** <span class='status-regular'>{salud}</span>", unsafe_allow_html=True)
                            else:
                                st.markdown(f"**Estado:** <span class='status-bad'>{salud}</span>", unsafe_allow_html=True)
                            
                            st.write(f"**NDVI:** {ndvi:.3f}")
                            st.write(f"**% Saludable:** {resultado['analisis']['porcentaje_saludable']:.1f}%")
                        
                        # Mostrar recomendaciones
                        st.markdown("#### 💡 Recomendaciones")
                        for rec in resultado['recomendaciones']:
                            prioridad_color = {
                                'alta': '🔴',
                                'media': '🟡', 
                                'baja': '🟢'
                            }
                            st.write(f"{prioridad_color.get(rec['prioridad'], '⚪')} **{rec['tipo_recomendacion'].title()}:** {rec['mensaje']}")
                            st.write(f"   *Acción:* {rec['accion_requerida']}")
                    
                    else:
                        st.error(f"❌ Error en el vuelo: {resultado['error']}")
        
        with col2:
            st.markdown("#### 📋 Drones Disponibles")
            
            drones_info = {
                "dji_mini_3": {
                    "nombre": "DJI Mini 3",
                    "autonomia": "25 min",
                    "cobertura": "20 ha",
                    "resolucion": "4K"
                },
                "dji_air_2s": {
                    "nombre": "DJI Air 2S",
                    "autonomia": "31 min", 
                    "cobertura": "30 ha",
                    "resolucion": "5.4K"
                },
                "dji_phantom_4": {
                    "nombre": "DJI Phantom 4",
                    "autonomia": "28 min",
                    "cobertura": "50 ha", 
                    "resolucion": "4K"
                }
            }
            
            for drone_id, info in drones_info.items():
                with st.container():
                    st.markdown(f"""
                    <div class="drone-card">
                        <h4>{info['nombre']}</h4>
                        <p>⏱️ Autonomía: {info['autonomia']}</p>
                        <p>📏 Cobertura: {info['cobertura']}</p>
                        <p>📹 Resolución: {info['resolucion']}</p>
                    </div>
                    """, unsafe_allow_html=True)
        
        # Historial de vuelos
        st.markdown("### 📈 Historial de Vuelos")
        self.mostrar_historial_vuelos()
    
    def mostrar_expansion_casablanca(self):
        """Mostrar interfaz de la expansión Casablanca"""
        st.header("🌍 Expansión Regional - Valle de Casablanca")
        
        # Información general
        st.markdown("### 🍇 Viñedos de Uva Blanca")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("""
            #### Características Específicas de Casablanca:
            - **Clima:** Mediterráneo con influencia costera
            - **Cultivo principal:** Uva blanca para vino
            - **Influencia marina:** Brisas costeras del Pacífico
            - **Variedades:** Chardonnay, Sauvignon Blanc, Pinot Grigio, Riesling, Viognier
            """)
        
        with col2:
            st.metric("🌊 Estaciones Costeras", "3")
            st.metric("🏔️ Estaciones Interiores", "2")
            st.metric("🍇 Variedades de Uva", "6")
        
        # Estaciones meteorológicas
        st.markdown("### 📡 Estaciones Meteorológicas")
        
        estaciones = {
            "Casablanca Centro": {"influencia": "Media", "cultivo": "Chardonnay"},
            "Collihuay": {"influencia": "Alta", "cultivo": "Sauvignon Blanc"},
            "Lagunillas": {"influencia": "Baja", "cultivo": "Pinot Grigio"},
            "Algarrobo": {"influencia": "Muy Alta", "cultivo": "Riesling"},
            "Curacaví": {"influencia": "Muy Baja", "cultivo": "Viognier"}
        }
        
        for estacion, info in estaciones.items():
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.write(f"**{estacion}**")
            
            with col2:
                st.write(f"🌊 {info['influencia']}")
            
            with col3:
                st.write(f"🍇 {info['cultivo']}")
        
        # Análisis de brisas marinas
        st.markdown("### 🌊 Análisis de Brisas Marinas")
        
        if st.button("📊 Generar Análisis de Brisas", type="primary"):
            with st.spinner("Analizando brisas marinas..."):
                # Simular análisis de brisas
                brisas_data = {
                    'Muy Alta': {'velocidad': 22.5, 'beneficio': 85.2},
                    'Alta': {'velocidad': 18.3, 'beneficio': 72.1},
                    'Media': {'velocidad': 14.7, 'beneficio': 58.9},
                    'Baja': {'velocidad': 11.2, 'beneficio': 45.3},
                    'Muy Baja': {'velocidad': 7.8, 'beneficio': 32.1}
                }
                
                fig = px.bar(
                    x=list(brisas_data.keys()),
                    y=[data['beneficio'] for data in brisas_data.values()],
                    title='Beneficio de Brisas Marinas para Uvas',
                    labels={'x': 'Influencia Marina', 'y': 'Beneficio (%)'}
                )
                
                st.plotly_chart(fig, config=PLOTLY_CONFIG, width='stretch')
                
                st.success("✅ Análisis de brisas marinas completado")
    
    def mostrar_historial_vuelos(self):
        """Mostrar historial de vuelos de drones"""
        try:
            conn = sqlite3.connect("sistema_drones_agricolas_optimizado.db")
            query = """
                SELECT v.vuelo_id, v.drone_tipo, v.ubicacion, v.cultivo_tipo, 
                       v.area_hectareas, v.duracion_vuelo, v.numero_fotos, v.fecha_vuelo,
                       a.ndvi_promedio, a.salud_general
                FROM vuelos_drones_optimizado v
                LEFT JOIN analisis_drones_optimizado a ON v.vuelo_id = a.vuelo_id
                ORDER BY v.fecha_vuelo DESC
                LIMIT 10
            """
            
            df = pd.read_sql_query(query, conn)
            conn.close()
            
            if not df.empty:
                # Formatear datos
                df['fecha_vuelo'] = pd.to_datetime(df['fecha_vuelo'])
                df['drone_nombre'] = df['drone_tipo'].map({
                    'dji_mini_3': 'DJI Mini 3',
                    'dji_air_2s': 'DJI Air 2S',
                    'dji_phantom_4': 'DJI Phantom 4'
                })
                
                # Mostrar tabla
                st.dataframe(
                    df[['fecha_vuelo', 'drone_nombre', 'ubicacion', 'cultivo_tipo', 
                        'area_hectareas', 'duracion_vuelo', 'salud_general', 'ndvi_promedio']],
                    width='stretch'
                )
            else:
                st.info("No hay vuelos registrados aún. Ejecuta tu primer vuelo arriba.")
                
        except Exception as e:
            st.error(f"Error cargando historial: {e}")
    
    def obtener_total_vuelos(self):
        """Obtener total de vuelos realizados"""
        try:
            conn = sqlite3.connect("sistema_drones_agricolas_optimizado.db")
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM vuelos_drones_optimizado")
            total = cursor.fetchone()[0]
            conn.close()
            return total
        except:
            return 0
    
    def obtener_total_recomendaciones(self):
        """Obtener total de recomendaciones generadas"""
        try:
            conn = sqlite3.connect("sistema_drones_agricolas_optimizado.db")
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM recomendaciones_drones_optimizado")
            total = cursor.fetchone()[0]
            conn.close()
            return total
        except:
            return 0
    
    def mostrar_grafico_vuelos_recientes(self):
        """Mostrar gráfico de vuelos recientes"""
        try:
            conn = sqlite3.connect("sistema_drones_agricolas_optimizado.db")
            query = """
                SELECT DATE(fecha_vuelo) as fecha, COUNT(*) as vuelos
                FROM vuelos_drones_optimizado
                WHERE fecha_vuelo >= date('now', '-7 days')
                GROUP BY DATE(fecha_vuelo)
                ORDER BY fecha
            """
            
            df = pd.read_sql_query(query, conn)
            conn.close()
            
            if not df.empty:
                fig = px.bar(df, x='fecha', y='vuelos', title='Vuelos de Drones (Últimos 7 días)')
                st.plotly_chart(fig, config=PLOTLY_CONFIG, width='stretch')
            else:
                st.info("No hay datos de vuelos recientes")
                
        except Exception as e:
            st.info("Ejecuta vuelos para ver el gráfico")
    
    def mostrar_grafico_salud_cultivos(self):
        """Mostrar gráfico de salud de cultivos"""
        try:
            conn = sqlite3.connect("sistema_drones_agricolas_optimizado.db")
            query = """
                SELECT v.cultivo_tipo, a.salud_general, COUNT(*) as cantidad
                FROM vuelos_drones_optimizado v
                JOIN analisis_drones_optimizado a ON v.vuelo_id = a.vuelo_id
                GROUP BY v.cultivo_tipo, a.salud_general
            """
            
            df = pd.read_sql_query(query, conn)
            conn.close()
            
            if not df.empty:
                fig = px.bar(df, x='cultivo_tipo', y='cantidad', color='salud_general',
                           title='Estado de Salud por Cultivo')
                st.plotly_chart(fig, config=PLOTLY_CONFIG, width='stretch')
            else:
                st.info("No hay análisis de salud disponibles")
                
        except Exception as e:
            st.info("Ejecuta vuelos para ver el análisis de salud")
    
    def mostrar_alertas_activas(self):
        """Mostrar alertas activas del sistema"""
        alertas = [
            {"tipo": "info", "mensaje": "Sistema de drones optimizado activo", "tiempo": "2 min"},
            {"tipo": "success", "mensaje": "Expansión Casablanca operativa", "tiempo": "5 min"},
            {"tipo": "warning", "mensaje": "Revisar recomendaciones pendientes", "tiempo": "10 min"}
        ]
        
        for alerta in alertas:
            if alerta["tipo"] == "info":
                st.info(f"ℹ️ {alerta['mensaje']} ({alerta['tiempo']} atrás)")
            elif alerta["tipo"] == "success":
                st.success(f"✅ {alerta['mensaje']} ({alerta['tiempo']} atrás)")
            elif alerta["tipo"] == "warning":
                st.warning(f"⚠️ {alerta['mensaje']} ({alerta['tiempo']} atrás)")

def main():
    """Función principal del dashboard"""
    dashboard = DashboardUnificadoMetgo()
    
    # Mostrar header
    dashboard.mostrar_header()
    
    # Mostrar sidebar y obtener selección
    seleccion = dashboard.mostrar_sidebar()
    
    # Mostrar contenido según selección
    if seleccion == "🏠 Dashboard Principal":
        dashboard.mostrar_dashboard_principal()
    elif seleccion == "🛰️ Sistema de Drones":
        dashboard.mostrar_sistema_drones()
    elif seleccion == "🌍 Expansión Casablanca":
        dashboard.mostrar_expansion_casablanca()
    elif seleccion == "📊 Análisis Meteorológico":
        st.info("Módulo de análisis meteorológico - En desarrollo")
    elif seleccion == "🤖 Machine Learning":
        st.info("Módulo de Machine Learning - En desarrollo")
    elif seleccion == "💧 Riego Inteligente":
        st.info("Módulo de riego inteligente - En desarrollo")
    elif seleccion == "📱 Aplicación Móvil":
        st.info("Módulo de aplicación móvil - En desarrollo")
    elif seleccion == "📈 Reportes":
        st.info("Módulo de reportes - En desarrollo")

if __name__ == "__main__":
    main()

