"""
LOGIN CON DASHBOARDS METGO 3D QUILLOTA
Sistema que ejecuta automáticamente los dashboards cuando se seleccionan
"""

import streamlit as st
import subprocess
import sys
import os
import webbrowser
import threading
import time

class GestorDashboards:
    def __init__(self):
        self.dashboards = {
            'dashboard_empresarial': {
                'nombre': 'Dashboard Empresarial',
                'descripcion': 'Vista ejecutiva con métricas empresariales',
                'archivo': 'dashboard_empresarial_unificado_metgo.py',
                'puerto': 8503,
                'icono': '📊',
                'color': '#667eea',
                'roles': ['admin', 'ejecutivo']
            },
            'dashboard_agricola': {
                'nombre': 'Dashboard Agrícola',
                'descripcion': 'Gestión completa de cultivos y producción',
                'archivo': 'dashboard_agricola_avanzado.py',
                'puerto': 8501,
                'icono': '🌱',
                'color': '#27ae60',
                'roles': ['admin', 'ejecutivo', 'agricultor', 'tecnico', 'usuario']
            },
            'dashboard_meteorologico': {
                'nombre': 'Dashboard Meteorológico',
                'descripcion': 'Monitoreo climático en tiempo real',
                'archivo': 'dashboard_meteorologico_metgo.py',
                'puerto': 8502,
                'icono': '🌤️',
                'color': '#3498db',
                'roles': ['admin', 'ejecutivo', 'agricultor', 'tecnico', 'usuario']
            },
            'dashboard_drones': {
                'nombre': 'Dashboard con Drones',
                'descripcion': 'Monitoreo aéreo y análisis de cultivos',
                'archivo': 'dashboard_unificado_metgo_con_drones.py',
                'puerto': 8504,
                'icono': '🚁',
                'color': '#9b59b6',
                'roles': ['admin', 'agricultor', 'tecnico']
            },
            'sistema_economico': {
                'nombre': 'Sistema Económico',
                'descripcion': 'Análisis de ROI y rentabilidad',
                'archivo': 'analisis_economico_agricola_metgo_con_conversion.py',
                'puerto': 8506,
                'icono': '💰',
                'color': '#f39c12',
                'roles': ['admin', 'ejecutivo', 'agricultor']
            }
        }
        self.procesos_activos = {}
        
        # Inicializar estado de procesos
        if 'procesos_activos' not in st.session_state:
            st.session_state.procesos_activos = {}
    
    def verificar_archivo(self, archivo):
        """Verificar que el archivo existe"""
        return os.path.exists(archivo)
    
    def iniciar_dashboard(self, dashboard_id):
        """Iniciar un dashboard específico"""
        try:
            dashboard = self.dashboards[dashboard_id]
            
            if not self.verificar_archivo(dashboard['archivo']):
                return False, f"Archivo {dashboard['archivo']} no encontrado"
            
            # Comando para ejecutar Streamlit
            comando = [
                sys.executable, "-m", "streamlit", "run", 
                dashboard['archivo'], 
                "--server.port", str(dashboard['puerto']),
                "--server.headless", "true"
            ]
            
            # Ejecutar en proceso separado
            proceso = subprocess.Popen(comando, 
                                     stdout=subprocess.PIPE, 
                                     stderr=subprocess.PIPE)
            
            # Guardar proceso en session state
            st.session_state.procesos_activos[dashboard_id] = {
                'proceso': proceso,
                'puerto': dashboard['puerto'],
                'iniciado': time.time()
            }
            
            return True, f"Dashboard iniciado en puerto {dashboard['puerto']}"
            
        except Exception as e:
            return False, f"Error: {e}"
    
    def verificar_proceso_activo(self, dashboard_id):
        """Verificar si un proceso está activo"""
        if dashboard_id in st.session_state.procesos_activos:
            proceso = st.session_state.procesos_activos[dashboard_id]['proceso']
            return proceso.poll() is None
        return False
    
    def obtener_url_dashboard(self, dashboard_id):
        """Obtener URL del dashboard"""
        if dashboard_id in st.session_state.procesos_activos:
            puerto = st.session_state.procesos_activos[dashboard_id]['puerto']
            return f"http://localhost:{puerto}"
        return None

def main():
    """Sistema principal con dashboards integrados"""
    st.set_page_config(
        page_title="METGO 3D - Sistema Completo",
        page_icon="🎯",
        layout="wide"
    )
    
    # CSS
    st.markdown("""
    <style>
        .main {
            padding-top: 1rem;
            padding-bottom: 1rem;
        }
        .title {
            text-align: center;
            color: #667eea;
            font-size: 2.5rem;
            font-weight: 800;
            margin-bottom: 1rem;
        }
        .subtitle {
            text-align: center;
            color: #6c757d;
            margin-bottom: 2rem;
        }
        .dashboard-card {
            background: white;
            padding: 1.5rem;
            border-radius: 15px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
            border: 1px solid #e9ecef;
            margin-bottom: 1rem;
        }
        .status-activo {
            background: #d4edda;
            color: #155724;
            padding: 0.3rem 0.8rem;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 600;
        }
        .status-inactivo {
            background: #f8d7da;
            color: #721c24;
            padding: 0.3rem 0.8rem;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 600;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown("""
    <div class="title">METGO 3D</div>
    <div class="subtitle">Sistema de Gestión Agrícola Inteligente</div>
    """, unsafe_allow_html=True)
    
    # Inicializar gestor de dashboards
    gestor = GestorDashboards()
    
    # Verificar si está logueado
    if 'logueado' not in st.session_state or not st.session_state.logueado:
        mostrar_login(gestor)
    else:
        mostrar_dashboards(gestor)

def mostrar_login(gestor):
    """Mostrar formulario de login"""
    with st.form("login"):
        st.markdown("### 🔐 Iniciar Sesión")
        
        usuario = st.text_input("Usuario", value="admin", help="Ingresa tu usuario")
        password = st.text_input("Contraseña", type="password", value="admin123", help="Ingresa tu contraseña")
        
        login_btn = st.form_submit_button("🚀 Iniciar Sesión", use_container_width=True)
        
        if login_btn:
            # Validación simple
            usuarios_validos = {
                'admin': 'admin123',
                'ejecutivo': 'ejecutivo123',
                'agricultor': 'agricultor123',
                'tecnico': 'tecnico123',
                'usuario': 'usuario123'
            }
            
            if usuario in usuarios_validos and usuarios_validos[usuario] == password:
                st.session_state.logueado = True
                st.session_state.usuario = usuario
                st.session_state.password = password
                st.success("✅ ¡Login exitoso!")
                st.rerun()
            else:
                st.error("❌ Usuario o contraseña incorrectos")
    
    # Información de usuarios
    st.markdown("""
    ### 👥 Usuarios de Prueba
    
    | Usuario | Contraseña | Rol |
    |---------|------------|-----|
    | admin | admin123 | Administrador |
    | ejecutivo | ejecutivo123 | Ejecutivo |
    | agricultor | agricultor123 | Agricultor |
    | tecnico | tecnico123 | Técnico |
    | usuario | usuario123 | Usuario |
    """)

def mostrar_dashboards(gestor):
    """Mostrar dashboards disponibles"""
    st.markdown("""
    <div class="subtitle">Bienvenido, {} ({})</div>
    """.format(
        st.session_state.usuario.title(),
        st.session_state.usuario.title()
    ), unsafe_allow_html=True)
    
    # Filtrar dashboards por rol
    usuario_actual = st.session_state.usuario
    dashboards_disponibles = []
    
    for dashboard_id, dashboard in gestor.dashboards.items():
        if usuario_actual in dashboard['roles'] or usuario_actual == 'admin':
            dashboards_disponibles.append((dashboard_id, dashboard))
    
    st.markdown("### 🚀 Dashboards Disponibles")
    
    # Mostrar dashboards en columnas
    cols = st.columns(2)
    
    for i, (dashboard_id, dashboard) in enumerate(dashboards_disponibles):
        with cols[i % 2]:
            # Verificar estado del proceso
            proceso_activo = gestor.verificar_proceso_activo(dashboard_id)
            estado = "ACTIVO" if proceso_activo else "INACTIVO"
            estado_class = "status-activo" if proceso_activo else "status-inactivo"
            
            st.markdown(f"""
            <div class="dashboard-card">
                <div style="text-align: right;">
                    <span class="{estado_class}">{estado}</span>
                </div>
                <div style="text-align: center; font-size: 3rem; margin: 1rem 0; color: {dashboard['color']};">{dashboard['icono']}</div>
                <h3 style="text-align: center; color: #2c3e50; margin-bottom: 1rem;">{dashboard['nombre']}</h3>
                <p style="text-align: center; color: #6c757d; margin-bottom: 1.5rem;">{dashboard['descripcion']}</p>
                <p style="text-align: center; font-size: 0.9rem; color: #6c757d;">Puerto: {dashboard['puerto']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Botones de control
            col_btn1, col_btn2 = st.columns(2)
            
            with col_btn1:
                if proceso_activo:
                    url = gestor.obtener_url_dashboard(dashboard_id)
                    if st.button(f"🌐 Abrir", key=f"open_{dashboard_id}", use_container_width=True):
                        st.success(f"✅ Abriendo {dashboard['nombre']}")
                        st.info(f"**URL:** {url}")
                        st.info(f"**Credenciales:** {st.session_state.usuario} / {st.session_state.password}")
                        
                        try:
                            webbrowser.open(url)
                            st.success("🌐 Navegador abierto")
                        except:
                            st.info("📋 Copia la URL manualmente")
                else:
                    if st.button(f"🚀 Iniciar", key=f"start_{dashboard_id}", use_container_width=True):
                        with st.spinner(f"Iniciando {dashboard['nombre']}..."):
                            success, message = gestor.iniciar_dashboard(dashboard_id)
                            if success:
                                st.success(f"✅ {message}")
                                st.info("🔄 Recarga la página para ver el estado actualizado")
                                time.sleep(2)
                                st.rerun()
                            else:
                                st.error(f"❌ {message}")
            
            with col_btn2:
                if proceso_activo:
                    if st.button(f"🛑 Detener", key=f"stop_{dashboard_id}", use_container_width=True):
                        if dashboard_id in st.session_state.procesos_activos:
                            proceso = st.session_state.procesos_activos[dashboard_id]['proceso']
                            proceso.terminate()
                            del st.session_state.procesos_activos[dashboard_id]
                            st.success("✅ Dashboard detenido")
                            st.rerun()
    
    # Información del sistema
    st.markdown("---")
    
    col_info1, col_info2 = st.columns(2)
    
    with col_info1:
        st.markdown("### 📊 Estado del Sistema")
        procesos_activos = len(st.session_state.procesos_activos)
        st.metric("Dashboards Activos", procesos_activos)
        st.metric("Usuario", st.session_state.usuario)
        st.metric("Sesión", "Activa")
    
    with col_info2:
        st.markdown("### 💡 Instrucciones")
        st.info("""
        1. **Inicia** el dashboard que necesites
        2. **Abre** la URL que aparece
        3. **Usa las credenciales** en el dashboard
        4. **Detén** cuando termines de usar
        """)
    
    # Botón de logout
    if st.button("🚪 Cerrar Sesión", use_container_width=True):
        # Detener todos los procesos
        for dashboard_id in list(st.session_state.procesos_activos.keys()):
            proceso = st.session_state.procesos_activos[dashboard_id]['proceso']
            proceso.terminate()
        
        # Limpiar session state
        del st.session_state.logueado
        del st.session_state.usuario
        del st.session_state.password
        del st.session_state.procesos_activos
        
        st.success("✅ Sesión cerrada y dashboards detenidos")
        st.rerun()

if __name__ == "__main__":
    main()
