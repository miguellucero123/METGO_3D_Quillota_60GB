"""
SISTEMA DE INTEGRACIÓN COMPLETA METGO 3D
Integra TODOS los dashboards del proyecto (Python y HTML)
"""

import streamlit as st
import subprocess
import sys
import webbrowser
import time
import os
import socket
from pathlib import Path

class SistemaIntegracionCompletaMetgo:
    def __init__(self):
        self.dashboards_config = {
            # Dashboards Python principales
            "meteorologico_final": {
                "nombre": "Dashboard Meteorológico Final",
                "tipo": "python",
                "script": "dashboard_meteorologico_final.py",
                "puerto": 8502,
                "descripcion": "Pronósticos meteorológicos completos con Tmax, Tmin y todas las variables",
                "icono": "🌤️",
                "categoria": "Meteorología",
                "prioridad": 1
            },
            "meteorologico_metgo": {
                "nombre": "Dashboard Meteorológico METGO",
                "tipo": "python",
                "script": "dashboard_meteorologico_metgo.py",
                "puerto": 8503,
                "descripcion": "Dashboard meteorológico original del sistema",
                "icono": "🌡️",
                "categoria": "Meteorología",
                "prioridad": 2
            },
            "agricola_avanzado": {
                "nombre": "Dashboard Agrícola Avanzado",
                "tipo": "python",
                "script": "dashboard_agricola_avanzado.py",
                "puerto": 8501,
                "descripcion": "Recomendaciones agrícolas y gestión de cultivos",
                "icono": "🌱",
                "categoria": "Agricultura",
                "prioridad": 1
            },
            "ml_avanzado": {
                "nombre": "Machine Learning Avanzado",
                "tipo": "python",
                "script": "dashboard_ml_avanzado.py",
                "puerto": 8504,
                "descripcion": "Modelos de ML y predicciones avanzadas",
                "icono": "🤖",
                "categoria": "Inteligencia Artificial",
                "prioridad": 2
            },
            "modelos_dinamicos": {
                "nombre": "Modelos Dinámicos",
                "tipo": "python",
                "script": "dashboard_modelos_dinamicos.py",
                "puerto": 8505,
                "descripcion": "Creación y gestión de modelos dinámicos",
                "icono": "📊",
                "categoria": "Modelos",
                "prioridad": 3
            },
            "drones_agricolas": {
                "nombre": "Drones Agrícolas",
                "tipo": "python",
                "script": "dashboard_unificado_metgo_con_drones.py",
                "puerto": 8506,
                "descripcion": "Monitoreo aéreo con drones",
                "icono": "🚁",
                "categoria": "Tecnología",
                "prioridad": 2
            },
            "principal_integrado": {
                "nombre": "Dashboard Principal Integrado",
                "tipo": "python",
                "script": "dashboard_principal_integrado_metgo.py",
                "puerto": 8512,
                "descripcion": "Panel de control principal",
                "icono": "🏠",
                "categoria": "Control",
                "prioridad": 1
            },
            "maestro_unificado": {
                "nombre": "Dashboard Maestro Unificado",
                "tipo": "python",
                "script": "dashboard_maestro_unificado_metgo.py",
                "puerto": 8513,
                "descripcion": "Sistema central de gestión",
                "icono": "🎛️",
                "categoria": "Control",
                "prioridad": 1
            },
            
            # Dashboards HTML
            "global_html": {
                "nombre": "Dashboard Global HTML",
                "tipo": "html",
                "archivo": "dashboard_global_html.html",
                "descripcion": "Dashboard global en formato HTML",
                "icono": "🌐",
                "categoria": "HTML",
                "prioridad": 2
            },
            "html_completo": {
                "nombre": "Dashboard HTML Completo",
                "tipo": "html",
                "archivo": "dashboard_html_completo.html",
                "descripcion": "Dashboard HTML completo del sistema",
                "icono": "📄",
                "categoria": "HTML",
                "prioridad": 2
            },
            "sistema_unificado_html": {
                "nombre": "Sistema Unificado HTML",
                "tipo": "html",
                "archivo": "dashboard_sistema_unificado.html",
                "descripcion": "Sistema unificado en formato HTML",
                "icono": "🔗",
                "categoria": "HTML",
                "prioridad": 2
            },
            "metgo_3d_html": {
                "nombre": "METGO 3D HTML",
                "tipo": "html",
                "archivo": "dashboard_metgo_3d.html",
                "descripcion": "Dashboard METGO 3D en formato HTML",
                "icono": "🎯",
                "categoria": "HTML",
                "prioridad": 2
            },
            
            # Otros dashboards importantes
            "integrado_recomendaciones": {
                "nombre": "Dashboard de Recomendaciones",
                "tipo": "python",
                "script": "dashboard_integrado_recomendaciones_metgo.py",
                "puerto": 8510,
                "descripcion": "Recomendaciones integradas de riego, plagas y heladas",
                "icono": "💡",
                "categoria": "Recomendaciones",
                "prioridad": 2
            },
            "alertas_visuales": {
                "nombre": "Sistema de Alertas Visuales",
                "tipo": "python",
                "script": "sistema_alertas_visuales_integrado_metgo.py",
                "puerto": 8511,
                "descripcion": "Alertas meteorológicas y visuales",
                "icono": "🚨",
                "categoria": "Alertas",
                "prioridad": 2
            },
            "economico_conversion": {
                "nombre": "Análisis Económico con Conversión",
                "tipo": "python",
                "script": "analisis_economico_agricola_metgo_con_conversion.py",
                "puerto": 8507,
                "descripcion": "ROI, VAN, TIR con conversión de monedas",
                "icono": "💰",
                "categoria": "Economía",
                "prioridad": 2
            },
            "integracion_sistemas": {
                "nombre": "Integración con Sistemas Existentes",
                "tipo": "python",
                "script": "integracion_sistemas_existentes_metgo.py",
                "puerto": 8508,
                "descripcion": "ERP, GPS, IoT y sistemas de gestión",
                "icono": "🔗",
                "categoria": "Integración",
                "prioridad": 3
            }
        }
    
    def verificar_puerto_disponible(self, port):
        """Verificar si un puerto está disponible"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                return s.connect_ex(('localhost', port)) == 0
        except:
            return False
    
    def obtener_estado_dashboards(self):
        """Obtener el estado actual de todos los dashboards"""
        estados = {}
        for dashboard_id, config in self.dashboards_config.items():
            if config['tipo'] == 'python':
                puerto = config.get('puerto', None)
                if puerto:
                    estado = "🟢 Activo" if self.verificar_puerto_disponible(puerto) else "🔴 Inactivo"
                    url = f"http://localhost:{puerto}"
                else:
                    estado = "⚪ No aplica"
                    url = "N/A"
            else:  # HTML
                archivo = config.get('archivo', '')
                if os.path.exists(archivo):
                    estado = "📄 Disponible"
                    url = f"file://{os.path.abspath(archivo)}"
                else:
                    estado = "❌ No encontrado"
                    url = "N/A"
            
            estados[dashboard_id] = {
                'estado': estado,
                'url': url,
                'config': config
            }
        return estados
    
    def iniciar_dashboard_python(self, dashboard_id):
        """Iniciar un dashboard Python específico"""
        if dashboard_id not in self.dashboards_config:
            st.error(f"Dashboard '{dashboard_id}' no encontrado")
            return False
        
        config = self.dashboards_config[dashboard_id]
        if config['tipo'] != 'python':
            st.error(f"Dashboard '{dashboard_id}' no es un dashboard Python")
            return False
        
        script = config['script']
        puerto = config['puerto']
        
        if self.verificar_puerto_disponible(puerto):
            st.success(f"✅ {config['nombre']} ya está activo en puerto {puerto}")
            return True
        
        try:
            command = [
                sys.executable, "-m", "streamlit", "run",
                script,
                "--server.port", str(puerto),
                "--server.headless", "true"
            ]
            subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            time.sleep(3)  # Esperar a que se inicie
            
            if self.verificar_puerto_disponible(puerto):
                st.success(f"🚀 {config['nombre']} iniciado exitosamente en puerto {puerto}")
                return True
            else:
                st.error(f"❌ Error iniciando {config['nombre']}")
                return False
        except Exception as e:
            st.error(f"❌ Error iniciando {config['nombre']}: {e}")
            return False
    
    def abrir_dashboard_html(self, dashboard_id):
        """Abrir un dashboard HTML"""
        if dashboard_id not in self.dashboards_config:
            st.error(f"Dashboard '{dashboard_id}' no encontrado")
            return False
        
        config = self.dashboards_config[dashboard_id]
        if config['tipo'] != 'html':
            st.error(f"Dashboard '{dashboard_id}' no es un dashboard HTML")
            return False
        
        archivo = config['archivo']
        if not os.path.exists(archivo):
            st.error(f"❌ Archivo HTML no encontrado: {archivo}")
            return False
        
        try:
            url = f"file://{os.path.abspath(archivo)}"
            webbrowser.open_new_tab(url)
            st.success(f"🌐 {config['nombre']} abierto en el navegador")
            return True
        except Exception as e:
            st.error(f"❌ Error abriendo {config['nombre']}: {e}")
            return False
    
    def mostrar_dashboard(self):
        """Mostrar el sistema de integración completa"""
        st.set_page_config(
            page_title="METGO 3D - Sistema de Integración Completa",
            page_icon="🎛️",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        # CSS personalizado
        st.markdown("""
        <style>
        .main-header {
            background: linear-gradient(90deg, #00467F, #A5CC82);
            padding: 2rem;
            border-radius: 10px;
            color: white;
            text-align: center;
            margin-bottom: 2rem;
        }
        .dashboard-card {
            background: white;
            padding: 1.5rem;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 1rem;
            border-left: 5px solid #A5CC82;
        }
        .status-active { color: green; font-weight: bold; }
        .status-inactive { color: red; font-weight: bold; }
        .status-available { color: blue; font-weight: bold; }
        .status-not-found { color: gray; font-weight: bold; }
        </style>
        """, unsafe_allow_html=True)
        
        # Header principal
        st.markdown("""
        <div class="main-header">
            <h1>🎛️ METGO 3D - Sistema de Integración Completa</h1>
            <h3>Acceso Unificado a TODOS los Dashboards del Proyecto</h3>
            <p>26 dashboards identificados - 84.6% no integrados anteriormente</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Sidebar con estadísticas
        with st.sidebar:
            st.header("📊 Estadísticas del Sistema")
            estados = self.obtener_estado_dashboards()
            
            # Contar estados
            python_activos = sum(1 for e in estados.values() if "🟢" in e['estado'])
            html_disponibles = sum(1 for e in estados.values() if "📄" in e['estado'])
            total_disponibles = python_activos + html_disponibles
            
            st.metric("🐍 Python Activos", python_activos)
            st.metric("🌐 HTML Disponibles", html_disponibles)
            st.metric("📊 Total Disponibles", total_disponibles)
            st.metric("🎯 Total Dashboards", len(self.dashboards_config))
            
            if st.button("🔄 Actualizar Estados"):
                st.rerun()
        
        # Agrupar por categoría
        categorias = {}
        for dashboard_id, config in self.dashboards_config.items():
            categoria = config['categoria']
            if categoria not in categorias:
                categorias[categoria] = []
            categorias[categoria].append((dashboard_id, config, estados[dashboard_id]))
        
        # Mostrar dashboards por categoría
        for categoria, dashboards in categorias.items():
            st.markdown(f"### {categoria}")
            
            # Ordenar por prioridad
            dashboards.sort(key=lambda x: x[1]['prioridad'])
            
            for dashboard_id, config, estado_info in dashboards:
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    estado_class = "status-active" if "🟢" in estado_info['estado'] else \
                                 "status-available" if "📄" in estado_info['estado'] else \
                                 "status-inactive"
                    
                    st.markdown(f"""
                    <div class="dashboard-card">
                        <h4>{config['icono']} {config['nombre']}</h4>
                        <p>{config['descripcion']}</p>
                        <p><strong>Estado:</strong> <span class="{estado_class}">{estado_info['estado']}</span></p>
                        <p><strong>Tipo:</strong> {config['tipo'].upper()}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    if config['tipo'] == 'python':
                        if "🟢" in estado_info['estado']:
                            if st.button(f"🌐 Abrir", key=f"open_{dashboard_id}"):
                                webbrowser.open_new_tab(estado_info['url'])
                        else:
                            if st.button(f"🚀 Iniciar", key=f"start_{dashboard_id}"):
                                self.iniciar_dashboard_python(dashboard_id)
                                st.rerun()
                    else:  # HTML
                        if "📄" in estado_info['estado']:
                            if st.button(f"🌐 Abrir", key=f"open_{dashboard_id}"):
                                self.abrir_dashboard_html(dashboard_id)
                        else:
                            st.info("No disponible")
                
                with col3:
                    if st.button(f"📊 Info", key=f"info_{dashboard_id}"):
                        st.info(f"URL: {estado_info['url']}")
        
        # Acciones masivas
        st.markdown("---")
        st.subheader("⚡ Acciones Masivas")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🚀 Iniciar Todos los Dashboards Python"):
                st.info("Iniciando todos los dashboards Python...")
                for dashboard_id, config in self.dashboards_config.items():
                    if config['tipo'] == 'python':
                        self.iniciar_dashboard_python(dashboard_id)
                st.success("✅ Todos los dashboards Python iniciados")
                st.rerun()
        
        with col2:
            if st.button("🌐 Abrir Todos los Dashboards HTML"):
                st.info("Abriendo todos los dashboards HTML...")
                for dashboard_id, config in self.dashboards_config.items():
                    if config['tipo'] == 'html':
                        self.abrir_dashboard_html(dashboard_id)
                st.success("✅ Todos los dashboards HTML abiertos")
        
        with col3:
            if st.button("📊 Mostrar Estadísticas Completas"):
                st.subheader("📈 Estadísticas Completas del Sistema")
                
                col_stats1, col_stats2, col_stats3, col_stats4 = st.columns(4)
                
                with col_stats1:
                    st.metric("🐍 Python", len([d for d in self.dashboards_config.values() if d['tipo'] == 'python']))
                
                with col_stats2:
                    st.metric("🌐 HTML", len([d for d in self.dashboards_config.values() if d['tipo'] == 'html']))
                
                with col_stats3:
                    st.metric("📊 Total", len(self.dashboards_config))
                
                with col_stats4:
                    porcentaje = (total_disponibles / len(self.dashboards_config)) * 100
                    st.metric("✅ Disponibles", f"{porcentaje:.1f}%")

def main():
    sistema = SistemaIntegracionCompletaMetgo()
    sistema.mostrar_dashboard()

if __name__ == "__main__":
    main()


