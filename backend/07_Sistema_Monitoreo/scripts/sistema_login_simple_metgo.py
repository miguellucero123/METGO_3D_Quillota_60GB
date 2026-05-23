"""
SISTEMA DE LOGIN SIMPLE - METGO 3D QUILLOTA
Sistema de autenticacion simplificado que funciona correctamente
"""

import streamlit as st
import hashlib
import sqlite3
from datetime import datetime, timedelta
import os

class SistemaLoginSimple:
    def __init__(self):
        self.base_datos = "login_metgo.db"
        self.inicializar_base_datos()
    
    def inicializar_base_datos(self):
        """Inicializar base de datos de login"""
        try:
            conn = sqlite3.connect(self.base_datos)
            cursor = conn.cursor()
            
            # Tabla de usuarios
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS usuarios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    usuario TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    nombre_completo TEXT NOT NULL,
                    rol TEXT NOT NULL DEFAULT 'usuario',
                    activo BOOLEAN DEFAULT 1,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Insertar usuarios de prueba
            usuarios_por_defecto = [
                ('admin', 'admin123', 'Administrador del Sistema', 'admin'),
                ('ejecutivo', 'ejecutivo123', 'Ejecutivo METGO', 'ejecutivo'),
                ('agricultor', 'agricultor123', 'Agricultor Principal', 'agricultor'),
                ('tecnico', 'tecnico123', 'Tecnico Agricola', 'tecnico'),
                ('usuario', 'usuario123', 'Usuario General', 'usuario')
            ]
            
            for usuario, password, nombre, rol in usuarios_por_defecto:
                password_hash = hashlib.sha256(password.encode()).hexdigest()
                cursor.execute('''
                    INSERT OR REPLACE INTO usuarios 
                    (usuario, password_hash, nombre_completo, rol, activo)
                    VALUES (?, ?, ?, ?, 1)
                ''', (usuario, password_hash, nombre, rol))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            st.error(f"Error inicializando base de datos: {e}")
    
    def hash_password(self, password: str) -> str:
        """Crear hash de la contrasena"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def autenticar_usuario(self, usuario: str, password: str) -> dict:
        """Autenticar usuario"""
        try:
            conn = sqlite3.connect(self.base_datos)
            cursor = conn.cursor()
            
            password_hash = self.hash_password(password)
            
            cursor.execute('''
                SELECT id, usuario, nombre_completo, rol, activo
                FROM usuarios 
                WHERE usuario = ? AND password_hash = ? AND activo = 1
            ''', (usuario, password_hash))
            
            resultado = cursor.fetchone()
            conn.close()
            
            if resultado:
                return {
                    'id': resultado[0],
                    'usuario': resultado[1],
                    'nombre_completo': resultado[2],
                    'rol': resultado[3],
                    'activo': bool(resultado[4])
                }
            
            return None
            
        except Exception as e:
            st.error(f"Error autenticando usuario: {e}")
            return None

def render_login_page():
    """Renderizar pagina de login"""
    st.set_page_config(
        page_title="METGO 3D - Login",
        page_icon="🔐",
        layout="centered",
        initial_sidebar_state="collapsed"
    )
    
    # CSS para pagina de login
    st.markdown("""
    <style>
        .main {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        
        .login-container {
            max-width: 400px;
            margin: 0 auto;
            padding: 2rem;
            background: white;
            border-radius: 15px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        }
        
        .login-header {
            text-align: center;
            margin-bottom: 2rem;
        }
        
        .login-title {
            color: #667eea;
            font-size: 2.5rem;
            font-weight: 800;
            margin: 0;
        }
        
        .login-subtitle {
            color: #6c757d;
            font-size: 1rem;
            margin: 0.5rem 0 0 0;
        }
        
        .user-info {
            background: #f8f9fa;
            padding: 1rem;
            border-radius: 10px;
            margin-bottom: 1rem;
            border-left: 4px solid #667eea;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown("""
    <div class="login-header">
        <h1 class="login-title">METGO 3D</h1>
        <p class="login-subtitle">Sistema de Gestion Agricola Inteligente</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Inicializar sistema de login
    login_system = SistemaLoginSimple()
    
    # Verificar si ya esta autenticado
    if 'user_data' in st.session_state and st.session_state.user_data:
        render_dashboard_selector(login_system, st.session_state.user_data)
        return
    
    # Formulario de login
    with st.form("login_form"):
        st.markdown("### 🔐 Iniciar Sesion")
        
        usuario = st.text_input("👤 Usuario", placeholder="Ingresa tu usuario")
        password = st.text_input("🔑 Contrasena", type="password", placeholder="Ingresa tu contrasena")
        
        submit_button = st.form_submit_button("🚀 Iniciar Sesion", use_container_width=True)
        
        if submit_button:
            if usuario and password:
                user_data = login_system.autenticar_usuario(usuario, password)
                if user_data:
                    st.session_state.user_data = user_data
                    st.success("✅ ¡Inicio de sesion exitoso!")
                    st.rerun()
                else:
                    st.error("❌ Usuario o contrasena incorrectos")
            else:
                st.error("❌ Por favor, completa todos los campos")
    
    # Informacion de usuarios por defecto
    st.markdown("""
    <div class="user-info">
        <h4>👥 Usuarios de Prueba</h4>
        <p><strong>Administrador:</strong> admin / admin123</p>
        <p><strong>Ejecutivo:</strong> ejecutivo / ejecutivo123</p>
        <p><strong>Agricultor:</strong> agricultor / agricultor123</p>
        <p><strong>Tecnico:</strong> tecnico / tecnico123</p>
        <p><strong>Usuario:</strong> usuario / usuario123</p>
    </div>
    """, unsafe_allow_html=True)

def render_dashboard_selector(login_system, user_data):
    """Renderizar selector de dashboards para usuario autenticado"""
    st.markdown("""
    <style>
        .dashboard-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 2rem;
            border-radius: 15px;
            margin-bottom: 2rem;
            text-align: center;
            color: white;
        }
        
        .dashboard-title {
            font-size: 2.5rem;
            font-weight: 800;
            margin: 0;
        }
        
        .user-welcome {
            font-size: 1.2rem;
            margin: 0.5rem 0 0 0;
            opacity: 0.9;
        }
        
        .dashboard-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 1.5rem;
            margin: 2rem 0;
        }
        
        .dashboard-card {
            background: white;
            padding: 2rem;
            border-radius: 15px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
            border: 1px solid #e9ecef;
            transition: all 0.3s ease;
            text-align: center;
        }
        
        .dashboard-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 30px rgba(0,0,0,0.15);
        }
        
        .dashboard-icon {
            font-size: 3rem;
            margin-bottom: 1rem;
        }
        
        .dashboard-name {
            font-size: 1.5rem;
            font-weight: 700;
            color: #2c3e50;
            margin-bottom: 0.5rem;
        }
        
        .dashboard-description {
            color: #6c757d;
            font-size: 0.9rem;
            margin-bottom: 1.5rem;
            line-height: 1.4;
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
        }
        
        .launch-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Header con informacion del usuario
    st.markdown(f"""
    <div class="dashboard-header">
        <h1 class="dashboard-title">METGO 3D</h1>
        <p class="user-welcome">Bienvenido, {user_data['nombre_completo']} ({user_data['rol'].title()})</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Dashboards disponibles
    dashboards = {
        'dashboard_empresarial': {
            'nombre': 'Dashboard Empresarial',
            'descripcion': 'Vista ejecutiva con metricas empresariales',
            'icono': '📊',
            'archivo': 'dashboard_empresarial_unificado_metgo.py',
            'puerto': 8503,
            'color': '#667eea',
            'roles': ['admin', 'ejecutivo']
        },
        'dashboard_agricola': {
            'nombre': 'Dashboard Agricola',
            'descripcion': 'Gestion completa de cultivos y produccion',
            'icono': '🌱',
            'archivo': 'dashboard_agricola_avanzado_metgo.py',
            'puerto': 8501,
            'color': '#27ae60',
            'roles': ['admin', 'ejecutivo', 'agricultor', 'tecnico', 'usuario']
        },
        'dashboard_meteorologico': {
            'nombre': 'Dashboard Meteorologico',
            'descripcion': 'Monitoreo climatico en tiempo real',
            'icono': '🌤️',
            'archivo': 'dashboard_meteorologico_metgo.py',
            'puerto': 8502,
            'color': '#3498db',
            'roles': ['admin', 'ejecutivo', 'agricultor', 'tecnico', 'usuario']
        },
        'dashboard_drones': {
            'nombre': 'Dashboard con Drones',
            'descripcion': 'Monitoreo aereo y analisis de cultivos',
            'icono': '🚁',
            'archivo': 'dashboard_unificado_metgo_con_drones.py',
            'puerto': 8504,
            'color': '#9b59b6',
            'roles': ['admin', 'agricultor', 'tecnico']
        },
        'sistema_economico': {
            'nombre': 'Sistema Economico',
            'descripcion': 'Analisis de ROI y rentabilidad',
            'icono': '💰',
            'archivo': 'analisis_economico_agricola_metgo_con_conversion.py',
            'puerto': 8506,
            'color': '#f39c12',
            'roles': ['admin', 'ejecutivo', 'agricultor']
        },
        'sistema_integracion': {
            'nombre': 'Sistema de Integracion',
            'descripcion': 'ERP, GPS e IoT integrados',
            'icono': '🔗',
            'archivo': 'integracion_sistemas_existentes_metgo.py',
            'puerto': 8507,
            'color': '#34495e',
            'roles': ['admin', 'tecnico']
        },
        'reportes_avanzados': {
            'nombre': 'Reportes Avanzados',
            'descripcion': 'Generacion de reportes ejecutivos',
            'icono': '📈',
            'archivo': 'generador_reportes_avanzados.py',
            'puerto': 8508,
            'color': '#2c3e50',
            'roles': ['admin', 'ejecutivo']
        }
    }
    
    # Filtrar dashboards por rol
    dashboards_disponibles = []
    for dashboard_id, dashboard in dashboards.items():
        if user_data['rol'] in dashboard['roles']:
            dashboards_disponibles.append((dashboard_id, dashboard))
    
    if dashboards_disponibles:
        st.markdown("### 🚀 Dashboards Disponibles")
        
        # Crear grid de dashboards
        cols = st.columns(2)
        for i, (dashboard_id, dashboard) in enumerate(dashboards_disponibles):
            with cols[i % 2]:
                st.markdown(f"""
                <div class="dashboard-card">
                    <div class="dashboard-icon" style="color: {dashboard['color']};">{dashboard['icono']}</div>
                    <h3 class="dashboard-name">{dashboard['nombre']}</h3>
                    <p class="dashboard-description">{dashboard['descripcion']}</p>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button(f"🚀 Abrir {dashboard['nombre']}", key=f"btn_{dashboard_id}", use_container_width=True):
                    if dashboard['puerto']:
                        st.success(f"🚀 Abriendo {dashboard['nombre']} en puerto {dashboard['puerto']}")
                        st.markdown(f"**URL:** http://localhost:{dashboard['puerto']}")
                        st.info("💡 Usa el mismo usuario y contrasena para acceder al dashboard")
                    else:
                        st.info(f"📄 Ejecutando {dashboard['nombre']}...")
                        st.code(f"python {dashboard['archivo']}")
    
    else:
        st.warning("⚠️ No tienes permisos para acceder a ningun dashboard")
    
    # Informacion de la sesion
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Usuario", user_data['usuario'])
    with col2:
        st.metric("Rol", user_data['rol'].title())
    with col3:
        st.metric("Sesion", "Activa")
    
    # Boton de logout
    st.markdown('<div style="text-align: center; margin-top: 3rem; padding-top: 2rem; border-top: 1px solid #e9ecef;">', unsafe_allow_html=True)
    if st.button("🚪 Cerrar Sesion", use_container_width=True):
        del st.session_state.user_data
        st.success("✅ Sesion cerrada exitosamente")
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

def main():
    """Funcion principal del sistema de login"""
    render_login_page()

if __name__ == "__main__":
    main()


