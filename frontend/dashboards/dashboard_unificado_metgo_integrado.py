"""
DASHBOARD UNIFICADO INTEGRADO - METGO 3D QUILLOTA
Dashboard que integra todos los dashboards existentes en un punto central
Incluye: Acceso directo a todos los módulos, navegación unificada, diseño coherente
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import subprocess
import os
import sys
from pathlib import Path

_DASH = Path(__file__).resolve().parent
if str(_DASH) not in sys.path:
    sys.path.insert(0, str(_DASH))

from metgo.streamlit_theme import PLOTLY_CONFIG, plotly_layout
from metgo_dashboard_init import page_config_and_theme

from datetime import datetime
import webbrowser

st, _, _ = page_config_and_theme(
    "Dashboard Unificado Integrado",
    "Acceso central a todos los módulos Streamlit",
    module="unificado",
    page_icon="🌱",
)

# CSS para diseño profesional y minimalista
st.markdown("""
<style>
    .main {
        padding-top: 1rem;
    }
    
    .header-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    }
    
    .header-title {
        color: white;
        font-size: 3rem;
        font-weight: 800;
        margin: 0;
        text-shadow: 3px 3px 6px rgba(0,0,0,0.3);
        letter-spacing: 2px;
    }
    
    .header-subtitle {
        color: rgba(255, 255, 255, 0.9);
        font-size: 1.3rem;
        margin: 1rem 0 0 0;
        font-weight: 300;
        letter-spacing: 1px;
    }
    
    .module-card {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        border: 1px solid #e9ecef;
        transition: all 0.3s ease;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    
    .module-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 30px rgba(0,0,0,0.15);
    }
    
    .module-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
        text-align: center;
    }
    
    .module-title {
        font-size: 1.5rem;
        font-weight: 700;
        color: #2c3e50;
        margin-bottom: 0.5rem;
        text-align: center;
    }
    
    .module-description {
        color: #6c757d;
        font-size: 0.9rem;
        text-align: center;
        margin-bottom: 1.5rem;
        line-height: 1.4;
    }
    
    .module-status {
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        text-align: center;
        margin-bottom: 1rem;
    }
    
    .status-active {
        background-color: #d4edda;
        color: #155724;
        border: 1px solid #c3e6cb;
    }
    
    .status-development {
        background-color: #fff3cd;
        color: #856404;
        border: 1px solid #ffeaa7;
    }
    
    .launch-button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.8rem 1.5rem;
        font-weight: 600;
        font-size: 0.9rem;
        cursor: pointer;
        transition: all 0.3s ease;
        width: 100%;
        text-decoration: none;
        display: inline-block;
        text-align: center;
    }
    
    .launch-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    
    .stats-container {
        background: #f8f9fa;
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
    }
    
    .stat-item {
        text-align: center;
        padding: 1rem;
    }
    
    .stat-number {
        font-size: 2.5rem;
        font-weight: 800;
        color: #667eea;
        margin: 0;
    }
    
    .stat-label {
        font-size: 0.9rem;
        color: #6c757d;
        margin: 0;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .quick-access {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        margin-bottom: 2rem;
    }
    
    .footer {
        text-align: center;
        padding: 2rem;
        color: #6c757d;
        font-size: 0.9rem;
        border-top: 1px solid #e9ecef;
        margin-top: 3rem;
    }
    
    /* Responsive */
    @media (max-width: 768px) {
        .header-title {
            font-size: 2rem;
        }
        
        .module-card {
            margin-bottom: 1rem;
        }
    }
</style>
""", unsafe_allow_html=True)

class DashboardUnificadoIntegrado:
    def __init__(self):
        self.modulos_disponibles = {
            'dashboard_empresarial': {
                'nombre': 'Dashboard Empresarial',
                'descripcion': 'Vista ejecutiva con métricas empresariales y análisis consolidado',
                'icono': '📊',
                'archivo': 'dashboard_empresarial_unificado_metgo.py',
                'puerto': 8503,
                'estado': 'activo',
                'categoria': 'Principal'
            },
            'dashboard_agricola_avanzado': {
                'nombre': 'Dashboard Agrícola Avanzado',
                'descripcion': 'Gestión completa de cultivos, riego inteligente y recomendaciones',
                'icono': '🌱',
                'archivo': 'dashboard_agricola_avanzado_metgo.py',
                'puerto': 8501,
                'estado': 'activo',
                'categoria': 'Agrícola'
            },
            'dashboard_meteorologico': {
                'nombre': 'Dashboard Meteorológico',
                'descripcion': 'Monitoreo meteorológico en tiempo real y predicciones climáticas',
                'icono': '🌤️',
                'archivo': 'dashboard_meteorologico_metgo.py',
                'puerto': 8502,
                'estado': 'activo',
                'categoria': 'Meteorología'
            },
            'dashboard_unificado_con_drones': {
                'nombre': 'Dashboard con Drones',
                'descripcion': 'Integración de drones para monitoreo aéreo y análisis de cultivos',
                'icono': '🚁',
                'archivo': 'dashboard_unificado_metgo_con_drones.py',
                'puerto': 8504,
                'estado': 'activo',
                'categoria': 'Tecnología'
            },
            'dashboard_global': {
                'nombre': 'Dashboard Global',
                'descripcion': 'Vista global dinámica con métricas integradas',
                'icono': '🌍',
                'archivo': 'dashboard_global_html.py',
                'puerto': 8507,
                'estado': 'activo',
                'categoria': 'Global'
            },
            'sistema_economico': {
                'nombre': 'Sistema Económico',
                'descripcion': 'Análisis económico con ROI, VAN y conversión de monedas',
                'icono': '💰',
                'archivo': 'analisis_economico_agricola_metgo_con_conversion.py',
                'puerto': None,
                'estado': 'activo',
                'categoria': 'Financiero'
            },
            'sistema_integracion': {
                'nombre': 'Sistema de Integración',
                'descripcion': 'Integración con ERP, GPS e IoT para sincronización de datos',
                'icono': '🔗',
                'archivo': 'integracion_sistemas_existentes_metgo.py',
                'puerto': None,
                'estado': 'activo',
                'categoria': 'Integración'
            },
            'aplicacion_movil': {
                'nombre': 'Aplicación Móvil',
                'descripcion': 'App móvil React Native para agricultores en campo',
                'icono': '📱',
                'archivo': 'app_movil_metgo',
                'puerto': None,
                'estado': 'desarrollo',
                'categoria': 'Móvil'
            },
            'sistema_drones': {
                'nombre': 'Sistema de Drones',
                'descripcion': 'Monitoreo aéreo con drones y análisis de imágenes',
                'icono': '🚁',
                'archivo': 'sistema_drones_agricolas_metgo_optimizado.py',
                'puerto': None,
                'estado': 'activo',
                'categoria': 'Tecnología'
            },
            'expansion_regional': {
                'nombre': 'Expansión Regional',
                'descripcion': 'Sistema expandido para Casablanca y otras regiones',
                'icono': '🗺️',
                'archivo': 'expansion_regional_casablanca_metgo.py',
                'puerto': None,
                'estado': 'activo',
                'categoria': 'Regional'
            }
        }
    
    def render_header(self):
        """Renderizar header principal"""
        st.markdown("""
        <div class="header-container">
            <h1 class="header-title">METGO 3D</h1>
            <p class="header-subtitle">Sistema Unificado de Gestión Agrícola Inteligente</p>
        </div>
        """, unsafe_allow_html=True)
    
    def render_stats(self):
        """Renderizar estadísticas del sistema"""
        st.markdown("""
        <div class="stats-container">
            <div class="row">
        """, unsafe_allow_html=True)
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.markdown("""
            <div class="stat-item">
                <h2 class="stat-number">10</h2>
                <p class="stat-label">Módulos</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="stat-item">
                <h2 class="stat-number">8</h2>
                <p class="stat-label">Activos</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class="stat-item">
                <h2 class="stat-number">231%</h2>
                <p class="stat-label">ROI</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown("""
            <div class="stat-item">
                <h2 class="stat-number">450</h2>
                <p class="stat-label">Hectáreas</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col5:
            st.markdown("""
            <div class="stat-item">
                <h2 class="stat-number">12</h2>
                <p class="stat-label">IoT</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div></div>", unsafe_allow_html=True)
    
    def render_quick_access(self):
        """Renderizar acceso rápido"""
        st.markdown("## 🚀 Acceso Rápido")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📊 Dashboard Empresarial", width='stretch'):
                self.launch_module('dashboard_empresarial')
        
        with col2:
            if st.button("🌱 Dashboard Agrícola", width='stretch'):
                self.launch_module('dashboard_agricola_avanzado')
        
        with col3:
            if st.button("🌤️ Dashboard Meteorológico", width='stretch'):
                self.launch_module('dashboard_meteorologico')
    
    def launch_module(self, module_id):
        """Lanzar módulo específico"""
        modulo = self.modulos_disponibles.get(module_id)
        if not modulo:
            st.error(f"Módulo {module_id} no encontrado")
            return
        
        if modulo['puerto']:
            # Lanzar aplicación Streamlit
            url = f"http://localhost:{modulo['puerto']}"
            st.success(f"🚀 Lanzando {modulo['nombre']} en puerto {modulo['puerto']}")
            st.markdown(f"**URL:** {url}")
            
            # Intentar abrir en navegador
            try:
                webbrowser.open(url)
            except:
                st.info("Por favor, abre manualmente la URL en tu navegador")
        else:
            # Ejecutar script Python
            if modulo['archivo'].endswith('.py'):
                st.success(f"🚀 Ejecutando {modulo['nombre']}")
                try:
                    subprocess.run([sys.executable, modulo['archivo']], check=True)
                except subprocess.CalledProcessError as e:
                    st.error(f"Error ejecutando {modulo['nombre']}: {e}")
            else:
                st.info(f"Archivo {modulo['archivo']} disponible para visualización")
    
    def render_modules_grid(self):
        """Renderizar grid de módulos"""
        st.markdown("## 📋 Módulos del Sistema")
        
        # Agrupar módulos por categoría
        categorias = {}
        for module_id, modulo in self.modulos_disponibles.items():
            categoria = modulo['categoria']
            if categoria not in categorias:
                categorias[categoria] = []
            categorias[categoria].append((module_id, modulo))
        
        # Renderizar por categoría
        for categoria, modulos in categorias.items():
            st.markdown(f"### {categoria}")
            
            # Calcular número de columnas según cantidad de módulos
            num_modulos = len(modulos)
            if num_modulos <= 2:
                cols = st.columns(num_modulos)
            elif num_modulos <= 3:
                cols = st.columns(3)
            else:
                cols = st.columns(4)
            
            for i, (module_id, modulo) in enumerate(modulos):
                with cols[i % len(cols)]:
                    self.render_module_card(module_id, modulo)
    
    def render_module_card(self, module_id, modulo):
        """Renderizar tarjeta de módulo"""
        estado_class = "status-active" if modulo['estado'] == 'activo' else "status-development"
        estado_texto = "ACTIVO" if modulo['estado'] == 'activo' else "DESARROLLO"
        
        st.markdown(f"""
        <div class="module-card">
            <div class="module-icon">{modulo['icono']}</div>
            <h3 class="module-title">{modulo['nombre']}</h3>
            <p class="module-description">{modulo['descripcion']}</p>
            <div class="module-status {estado_class}">{estado_texto}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Botón de lanzamiento
        if st.button(f"🚀 Lanzar {modulo['nombre']}", key=f"btn_{module_id}", width='stretch'):
            self.launch_module(module_id)
    
    def render_system_status(self):
        """Renderizar estado del sistema"""
        st.markdown("## 🔧 Estado del Sistema")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("### 📊 Servicios Activos")
            servicios_activos = [m for m in self.modulos_disponibles.values() if m['estado'] == 'activo']
            st.metric("Servicios Activos", len(servicios_activos))
            st.metric("En Desarrollo", len(self.modulos_disponibles) - len(servicios_activos))
        
        with col2:
            st.markdown("### 🌐 Conectividad")
            st.metric("APIs Meteorológicas", "6", "Activas")
            st.metric("Sistemas ERP", "3", "Conectados")
            st.metric("Dispositivos IoT", "12", "Online")
        
        with col3:
            st.markdown("### 📈 Rendimiento")
            st.metric("Uptime", "99.8%", "Últimas 24h")
            st.metric("Latencia Promedio", "45ms", "API Calls")
            st.metric("Datos Procesados", "1.2M", "Registros/día")
    
    def render_footer(self):
        """Renderizar footer"""
        st.markdown("""
        <div class="footer">
            <p><strong>METGO 3D</strong> - Sistema Unificado de Gestión Agrícola Inteligente</p>
            <p>© 2025 METGO Technologies. Todos los derechos reservados.</p>
            <p>Última actualización: """ + datetime.now().strftime("%d/%m/%Y %H:%M") + """</p>
        </div>
        """, unsafe_allow_html=True)
    
    def run_dashboard(self):
        """Ejecutar dashboard unificado"""
        # Header
        self.render_header()
        
        # Estadísticas
        self.render_stats()
        
        # Acceso rápido
        self.render_quick_access()
        
        # Estado del sistema
        self.render_system_status()
        
        # Grid de módulos
        self.render_modules_grid()
        
        # Footer
        self.render_footer()

# Función principal
def main():
    """Función principal del dashboard unificado"""
    dashboard = DashboardUnificadoIntegrado()
    dashboard.run_dashboard()

if __name__ == "__main__":
    main()


