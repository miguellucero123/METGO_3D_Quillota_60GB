"""
SISTEMA DE AUTENTICACIÓN Y DASHBOARD PRINCIPAL METGO 3D
Sistema que autentica usuarios y los redirige a un dashboard principal completo
"""

import streamlit as st
import hashlib
import sqlite3
import subprocess
import sys
import webbrowser
import time
import os
import socket
from pathlib import Path

class SistemaAuthDashboardPrincipalMetgo:
    def __init__(self):
        self.db_path = "usuarios_metgo.db"
        self.crear_base_datos()
        self.dashboards_config = self.obtener_configuracion_completa_dashboards()
    
    def crear_base_datos(self):
        """Crear base de datos de usuarios"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                rol TEXT DEFAULT 'usuario',
                fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Crear usuario por defecto si no existe
        cursor.execute('SELECT COUNT(*) FROM usuarios WHERE usuario = ?', ('admin',))
        if cursor.fetchone()[0] == 0:
            password_hash = hashlib.sha256('admin123'.encode()).hexdigest()
            cursor.execute('INSERT INTO usuarios (usuario, password_hash, rol) VALUES (?, ?, ?)', 
                         ('admin', password_hash, 'admin'))
        
        conn.commit()
        conn.close()
    
    def obtener_configuracion_completa_dashboards(self):
        """Obtener configuración completa de todos los dashboards"""
        return {
            # Dashboards principales
            "meteorologico_final": {
                "nombre": "Dashboard Meteorológico Final",
                "tipo": "python",
                "script": "dashboard_meteorologico_final.py",
                "puerto": 8502,
                "descripcion": "Pronósticos meteorológicos completos con Tmax, Tmin y todas las variables",
                "icono": "🌤️",
                "categoria": "Meteorología",
                "prioridad": 1,
                "requiere_auth": True
            },
            "meteorologico_metgo": {
                "nombre": "Dashboard Meteorológico METGO",
                "tipo": "python",
                "script": "dashboard_meteorologico_metgo.py",
                "puerto": 8503,
                "descripcion": "Dashboard meteorológico original del sistema",
                "icono": "🌡️",
                "categoria": "Meteorología",
                "prioridad": 2,
                "requiere_auth": True
            },
            "agricola_avanzado": {
                "nombre": "Dashboard Agrícola Avanzado",
                "tipo": "python",
                "script": "dashboard_agricola_avanzado_corregido.py",
                "puerto": 8509,
                "descripcion": "Recomendaciones agrícolas y gestión de cultivos (Versión Corregida)",
                "icono": "🌱",
                "categoria": "Agricultura",
                "prioridad": 1,
                "requiere_auth": True
            },
            "ml_avanzado": {
                "nombre": "Machine Learning Avanzado",
                "tipo": "python",
                "script": "dashboard_ml_avanzado.py",
                "puerto": 8504,
                "descripcion": "Modelos de ML y predicciones avanzadas",
                "icono": "🤖",
                "categoria": "Inteligencia Artificial",
                "prioridad": 2,
                "requiere_auth": True
            },
            "modelos_dinamicos": {
                "nombre": "Modelos Dinámicos",
                "tipo": "python",
                "script": "dashboard_modelos_dinamicos.py",
                "puerto": 8505,
                "descripcion": "Creación y gestión de modelos dinámicos",
                "icono": "📊",
                "categoria": "Modelos",
                "prioridad": 3,
                "requiere_auth": True
            },
            "drones_agricolas": {
                "nombre": "Drones Agrícolas",
                "tipo": "python",
                "script": "dashboard_unificado_metgo_con_drones.py",
                "puerto": 8506,
                "descripcion": "Monitoreo aéreo con drones",
                "icono": "🚁",
                "categoria": "Tecnología",
                "prioridad": 2,
                "requiere_auth": True
            },
            "economico_conversion": {
                "nombre": "Análisis Económico con Conversión",
                "tipo": "python",
                "script": "analisis_economico_agricola_metgo_con_conversion.py",
                "puerto": 8507,
                "descripcion": "ROI, VAN, TIR con conversión de monedas",
                "icono": "💰",
                "categoria": "Economía",
                "prioridad": 2,
                "requiere_auth": True
            },
            "integracion_sistemas": {
                "nombre": "Integración con Sistemas Existentes",
                "tipo": "python",
                "script": "integracion_sistemas_existentes_metgo.py",
                "puerto": 8508,
                "descripcion": "ERP, GPS, IoT y sistemas de gestión",
                "icono": "🔗",
                "categoria": "Integración",
                "prioridad": 3,
                "requiere_auth": True
            },
            "integrado_recomendaciones": {
                "nombre": "Dashboard de Recomendaciones",
                "tipo": "python",
                "script": "dashboard_integrado_recomendaciones_metgo.py",
                "puerto": 8510,
                "descripcion": "Recomendaciones integradas de riego, plagas y heladas",
                "icono": "💡",
                "categoria": "Recomendaciones",
                "prioridad": 2,
                "requiere_auth": True
            },
            "alertas_visuales": {
                "nombre": "Sistema de Alertas Visuales",
                "tipo": "python",
                "script": "sistema_alertas_visuales_integrado_metgo.py",
                "puerto": 8511,
                "descripcion": "Alertas meteorológicas y visuales",
                "icono": "🚨",
                "categoria": "Alertas",
                "prioridad": 2,
                "requiere_auth": True
            },
            "integracion_completa": {
                "nombre": "Sistema de Integración Completa",
                "tipo": "python",
                "script": "sistema_integracion_completo_metgo.py",
                "puerto": 8514,
                "descripcion": "Acceso a todos los 26 dashboards del sistema",
                "icono": "🎛️",
                "categoria": "Control",
                "prioridad": 1,
                "requiere_auth": True
            },
            
            # Dashboards HTML
            "global_html": {
                "nombre": "Dashboard Global HTML",
                "tipo": "html",
                "archivo": "dashboard_global_html.html",
                "descripcion": "Dashboard global en formato HTML",
                "icono": "🌐",
                "categoria": "HTML",
                "prioridad": 2,
                "requiere_auth": True
            },
            "html_completo": {
                "nombre": "Dashboard HTML Completo",
                "tipo": "html",
                "archivo": "dashboard_html_completo.html",
                "descripcion": "Dashboard HTML completo del sistema",
                "icono": "📄",
                "categoria": "HTML",
                "prioridad": 2,
                "requiere_auth": True
            },
            "sistema_unificado_html": {
                "nombre": "Sistema Unificado HTML",
                "tipo": "html",
                "archivo": "dashboard_sistema_unificado.html",
                "descripcion": "Sistema unificado en formato HTML",
                "icono": "🔗",
                "categoria": "HTML",
                "prioridad": 2,
                "requiere_auth": True
            },
            "metgo_3d_html": {
                "nombre": "METGO 3D HTML",
                "tipo": "html",
                "archivo": "dashboard_metgo_3d.html",
                "descripcion": "Dashboard METGO 3D en formato HTML",
                "icono": "🎯",
                "categoria": "HTML",
                "prioridad": 2,
                "requiere_auth": True
            }
        }
    
    def verificar_credenciales(self, usuario, password):
        """Verificar credenciales de usuario"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        cursor.execute('SELECT usuario, rol FROM usuarios WHERE usuario = ? AND password_hash = ?', 
                      (usuario, password_hash))
        resultado = cursor.fetchone()
        conn.close()
        return resultado
    
    def verificar_puerto_disponible(self, port):
        """Verificar si un puerto está disponible"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                return s.connect_ex(('localhost', port)) == 0
        except:
            return False
    
    def iniciar_dashboard_python(self, dashboard_id):
        """Iniciar un dashboard Python específico"""
        if dashboard_id not in self.dashboards_config:
            return False, f"Dashboard '{dashboard_id}' no encontrado"
        
        config = self.dashboards_config[dashboard_id]
        if config['tipo'] != 'python':
            return False, f"Dashboard '{dashboard_id}' no es un dashboard Python"
        
        script = config['script']
        puerto = config['puerto']
        
        if self.verificar_puerto_disponible(puerto):
            return True, f"✅ {config['nombre']} ya está activo en puerto {puerto}"
        
        try:
            command = [
                sys.executable, "-m", "streamlit", "run",
                script,
                "--server.port", str(puerto),
                "--server.headless", "true"
            ]
            subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            time.sleep(3)
            
            if self.verificar_puerto_disponible(puerto):
                return True, f"🚀 {config['nombre']} iniciado exitosamente en puerto {puerto}"
            else:
                return False, f"❌ Error iniciando {config['nombre']}"
        except Exception as e:
            return False, f"❌ Error iniciando {config['nombre']}: {e}"
    
    def abrir_dashboard_html(self, dashboard_id):
        """Abrir un dashboard HTML"""
        if dashboard_id not in self.dashboards_config:
            return False, f"Dashboard '{dashboard_id}' no encontrado"
        
        config = self.dashboards_config[dashboard_id]
        if config['tipo'] != 'html':
            return False, f"Dashboard '{dashboard_id}' no es un dashboard HTML"
        
        archivo = config['archivo']
        if not os.path.exists(archivo):
            return False, f"❌ Archivo HTML no encontrado: {archivo}"
        
        try:
            url = f"file://{os.path.abspath(archivo)}"
            webbrowser.open_new_tab(url)
            return True, f"🌐 {config['nombre']} abierto en el navegador"
        except Exception as e:
            return False, f"❌ Error abriendo {config['nombre']}: {e}"
    
    def mostrar_login(self):
        """Mostrar formulario de login"""
        st.markdown("""
        <div style="text-align: center; padding: 2rem; background: linear-gradient(90deg, #00467F, #A5CC82); 
                    border-radius: 10px; color: white; margin-bottom: 2rem;">
            <h1>🔐 METGO 3D - Sistema de Autenticación</h1>
            <h3>Acceso Seguro al Sistema Completo</h3>
            <p>Ingrese sus credenciales para acceder a todos los dashboards</p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("login_form"):
            st.subheader("Iniciar Sesión")
            usuario = st.text_input("Usuario", placeholder="Ingrese su usuario")
            password = st.text_input("Contraseña", type="password", placeholder="Ingrese su contraseña")
            
            col1, col2 = st.columns([1, 1])
            with col1:
                login_button = st.form_submit_button("🔑 Iniciar Sesión", use_container_width=True)
            with col2:
                register_button = st.form_submit_button("📝 Registrarse", use_container_width=True)
            
            if login_button:
                if usuario and password:
                    resultado = self.verificar_credenciales(usuario, password)
                    if resultado:
                        st.session_state['usuario_autenticado'] = True
                        st.session_state['usuario'] = resultado[0]
                        st.session_state['rol'] = resultado[1]
                        st.success(f"✅ Bienvenido, {resultado[0]}!")
                        st.rerun()
                    else:
                        st.error("❌ Usuario o contraseña incorrectos")
                else:
                    st.warning("⚠️ Por favor complete todos los campos")
            
            if register_button:
                if usuario and password:
                    try:
                        conn = sqlite3.connect(self.db_path)
                        cursor = conn.cursor()
                        password_hash = hashlib.sha256(password.encode()).hexdigest()
                        cursor.execute('INSERT INTO usuarios (usuario, password_hash) VALUES (?, ?)', 
                                     (usuario, password_hash))
                        conn.commit()
                        conn.close()
                        st.success(f"✅ Usuario '{usuario}' registrado exitosamente")
                    except sqlite3.IntegrityError:
                        st.error("❌ El usuario ya existe")
                    except Exception as e:
                        st.error(f"❌ Error registrando usuario: {e}")
                else:
                    st.warning("⚠️ Por favor complete todos los campos")
    
    def mostrar_dashboard_principal(self):
        """Mostrar el dashboard principal con acceso a todos los dashboards"""
        st.set_page_config(
            page_title="METGO 3D - Dashboard Principal",
            page_icon="🏠",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        # Header principal
        st.markdown("""
        <div style="background: linear-gradient(90deg, #00467F, #A5CC82); padding: 2rem; 
                    border-radius: 10px; color: white; text-align: center; margin-bottom: 2rem;">
            <h1>🏠 METGO 3D - Dashboard Principal</h1>
            <h3>Centro de Control Completo del Sistema</h3>
            <p>Usuario: <strong>{}</strong> | Rol: <strong>{}</strong></p>
        </div>
        """.format(st.session_state.get('usuario', 'N/A'), st.session_state.get('rol', 'N/A')), 
        unsafe_allow_html=True)
        
        # Sidebar con estadísticas
        with st.sidebar:
            st.header("📊 Estado del Sistema")
            
            # Contar dashboards por tipo
            python_count = len([d for d in self.dashboards_config.values() if d['tipo'] == 'python'])
            html_count = len([d for d in self.dashboards_config.values() if d['tipo'] == 'html'])
            total_count = len(self.dashboards_config)
            
            st.metric("🐍 Python", python_count)
            st.metric("🌐 HTML", html_count)
            st.metric("📊 Total", total_count)
            
            # Botón de logout
            if st.button("🚪 Cerrar Sesión", use_container_width=True):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()
            
            st.markdown("---")
            st.markdown("**Credenciales por defecto:**")
            st.code("Usuario: admin\nContraseña: admin123")
        
        # Agrupar dashboards por categoría
        categorias = {}
        for dashboard_id, config in self.dashboards_config.items():
            categoria = config['categoria']
            if categoria not in categorias:
                categorias[categoria] = []
            categorias[categoria].append((dashboard_id, config))
        
        # Mostrar dashboards por categoría
        for categoria, dashboards in categorias.items():
            st.markdown(f"### {categoria}")
            
            # Ordenar por prioridad
            dashboards.sort(key=lambda x: x[1]['prioridad'])
            
            # Crear columnas para los dashboards
            cols = st.columns(min(len(dashboards), 3))
            
            for i, (dashboard_id, config) in enumerate(dashboards):
                with cols[i % 3]:
                    with st.container():
                        st.markdown(f"""
                        <div style="background: white; padding: 1.5rem; border-radius: 10px; 
                                    box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin-bottom: 1rem;">
                            <h4>{config['icono']} {config['nombre']}</h4>
                            <p>{config['descripcion']}</p>
                            <p><strong>Tipo:</strong> {config['tipo'].upper()}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        if config['tipo'] == 'python':
                            if st.button(f"🚀 Iniciar", key=f"start_{dashboard_id}", use_container_width=True):
                                with st.spinner(f"Iniciando {config['nombre']}..."):
                                    success, message = self.iniciar_dashboard_python(dashboard_id)
                                    if success:
                                        st.success(message)
                                        time.sleep(1)
                                        webbrowser.open_new_tab(f"http://localhost:{config['puerto']}")
                                    else:
                                        st.error(message)
                        else:  # HTML
                            if st.button(f"🌐 Abrir", key=f"open_{dashboard_id}", use_container_width=True):
                                success, message = self.abrir_dashboard_html(dashboard_id)
                                if success:
                                    st.success(message)
                                else:
                                    st.error(message)
        
        # Acciones masivas
        st.markdown("---")
        st.subheader("⚡ Acciones Masivas")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🚀 Iniciar Todos los Dashboards Python", use_container_width=True):
                with st.spinner("Iniciando todos los dashboards Python..."):
                    for dashboard_id, config in self.dashboards_config.items():
                        if config['tipo'] == 'python':
                            success, message = self.iniciar_dashboard_python(dashboard_id)
                            if success:
                                st.success(message)
                            else:
                                st.warning(message)
        
        with col2:
            if st.button("🌐 Abrir Todos los Dashboards HTML", use_container_width=True):
                for dashboard_id, config in self.dashboards_config.items():
                    if config['tipo'] == 'html':
                        success, message = self.abrir_dashboard_html(dashboard_id)
                        if success:
                            st.success(message)
                        else:
                            st.warning(message)
        
        with col3:
            if st.button("📊 Mostrar Estadísticas", use_container_width=True):
                st.subheader("📈 Estadísticas Completas")
                
                col_stats1, col_stats2, col_stats3, col_stats4 = st.columns(4)
                
                with col_stats1:
                    st.metric("🐍 Python", python_count)
                
                with col_stats2:
                    st.metric("🌐 HTML", html_count)
                
                with col_stats3:
                    st.metric("📊 Total", total_count)
                
                with col_stats4:
                    categorias_count = len(categorias)
                    st.metric("📁 Categorías", categorias_count)
    
    def mostrar_interfaz(self):
        """Mostrar la interfaz principal"""
        if not st.session_state.get('usuario_autenticado', False):
            self.mostrar_login()
        else:
            self.mostrar_dashboard_principal()

def main():
    sistema = SistemaAuthDashboardPrincipalMetgo()
    sistema.mostrar_interfaz()

if __name__ == "__main__":
    main()
