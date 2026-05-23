"""
SISTEMA DE AUTENTICACIÓN - METGO 3D QUILLOTA
Sistema de autenticación para acceso seguro a dashboards
Incluye: Login, registro, gestión de usuarios, roles y permisos
"""

import streamlit as st
import hashlib
import sqlite3
import json
from datetime import datetime, timedelta
import os
import uuid
from typing import Dict, List, Optional

class SistemaAutenticacionMetgo:
    def __init__(self):
        self.base_datos = "autenticacion_metgo.db"
        self.session_timeout = 3600  # 1 hora
        self.inicializar_base_datos()
        self.crear_usuarios_por_defecto()
    
    def inicializar_base_datos(self):
        """Inicializar base de datos de autenticación"""
        try:
            conn = sqlite3.connect(self.base_datos)
            cursor = conn.cursor()
            
            # Tabla de usuarios
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS usuarios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    usuario TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    nombre_completo TEXT NOT NULL,
                    rol TEXT NOT NULL DEFAULT 'usuario',
                    activo BOOLEAN DEFAULT 1,
                    ultimo_acceso DATETIME,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Tabla de sesiones
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sesiones (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT UNIQUE NOT NULL,
                    usuario_id INTEGER NOT NULL,
                    fecha_inicio DATETIME DEFAULT CURRENT_TIMESTAMP,
                    fecha_expiracion DATETIME NOT NULL,
                    activa BOOLEAN DEFAULT 1,
                    ip_address TEXT,
                    user_agent TEXT,
                    FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
                )
            ''')
            
            # Tabla de permisos por rol
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS permisos_rol (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    rol TEXT NOT NULL,
                    modulo TEXT NOT NULL,
                    permiso TEXT NOT NULL,
                    activo BOOLEAN DEFAULT 1,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Insertar permisos por defecto
            self.insertar_permisos_por_defecto(cursor)
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            st.error(f"Error inicializando base de datos de autenticación: {e}")
    
    def insertar_permisos_por_defecto(self, cursor):
        """Insertar permisos por defecto para cada rol"""
        permisos = [
            # Administrador - acceso completo
            ('admin', 'dashboard_empresarial', 'read', 1),
            ('admin', 'dashboard_agricola', 'read', 1),
            ('admin', 'dashboard_meteorologico', 'read', 1),
            ('admin', 'dashboard_drones', 'read', 1),
            ('admin', 'sistema_economico', 'read', 1),
            ('admin', 'sistema_integracion', 'read', 1),
            ('admin', 'reportes', 'read', 1),
            ('admin', 'reportes', 'write', 1),
            ('admin', 'configuracion', 'read', 1),
            ('admin', 'configuracion', 'write', 1),
            
            # Ejecutivo - acceso a dashboards y reportes
            ('ejecutivo', 'dashboard_empresarial', 'read', 1),
            ('ejecutivo', 'dashboard_agricola', 'read', 1),
            ('ejecutivo', 'dashboard_meteorologico', 'read', 1),
            ('ejecutivo', 'sistema_economico', 'read', 1),
            ('ejecutivo', 'reportes', 'read', 1),
            ('ejecutivo', 'reportes', 'write', 1),
            
            # Agricultor - acceso a módulos agrícolas
            ('agricultor', 'dashboard_agricola', 'read', 1),
            ('agricultor', 'dashboard_meteorologico', 'read', 1),
            ('agricultor', 'dashboard_drones', 'read', 1),
            ('agricultor', 'sistema_economico', 'read', 1),
            
            # Técnico - acceso a sistemas técnicos
            ('tecnico', 'dashboard_agricola', 'read', 1),
            ('tecnico', 'dashboard_meteorologico', 'read', 1),
            ('tecnico', 'dashboard_drones', 'read', 1),
            ('tecnico', 'sistema_integracion', 'read', 1),
            ('tecnico', 'sistema_integracion', 'write', 1),
            ('tecnico', 'configuracion', 'read', 1),
            
            # Usuario - acceso básico
            ('usuario', 'dashboard_agricola', 'read', 1),
            ('usuario', 'dashboard_meteorologico', 'read', 1),
        ]
        
        for permiso in permisos:
            cursor.execute('''
                INSERT OR IGNORE INTO permisos_rol (rol, modulo, permiso, activo)
                VALUES (?, ?, ?, ?)
            ''', permiso)
    
    def crear_usuarios_por_defecto(self):
        """Crear usuarios por defecto del sistema"""
        usuarios_por_defecto = [
            {
                'usuario': 'admin',
                'email': 'admin@metgo3d.com',
                'password': 'admin123',
                'nombre_completo': 'Administrador del Sistema',
                'rol': 'admin'
            },
            {
                'usuario': 'ejecutivo',
                'email': 'ejecutivo@metgo3d.com',
                'password': 'ejecutivo123',
                'nombre_completo': 'Ejecutivo METGO',
                'rol': 'ejecutivo'
            },
            {
                'usuario': 'agricultor',
                'email': 'agricultor@metgo3d.com',
                'password': 'agricultor123',
                'nombre_completo': 'Agricultor Principal',
                'rol': 'agricultor'
            },
            {
                'usuario': 'tecnico',
                'email': 'tecnico@metgo3d.com',
                'password': 'tecnico123',
                'nombre_completo': 'Técnico Agrícola',
                'rol': 'tecnico'
            },
            {
                'usuario': 'usuario',
                'email': 'usuario@metgo3d.com',
                'password': 'usuario123',
                'nombre_completo': 'Usuario General',
                'rol': 'usuario'
            }
        ]
        
        for usuario_data in usuarios_por_defecto:
            self.crear_usuario(
                usuario_data['usuario'],
                usuario_data['email'],
                usuario_data['password'],
                usuario_data['nombre_completo'],
                usuario_data['rol']
            )
    
    def hash_password(self, password: str) -> str:
        """Crear hash de la contraseña"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def crear_usuario(self, usuario: str, email: str, password: str, nombre_completo: str, rol: str = 'usuario') -> bool:
        """Crear nuevo usuario"""
        try:
            conn = sqlite3.connect(self.base_datos)
            cursor = conn.cursor()
            
            password_hash = self.hash_password(password)
            
            cursor.execute('''
                INSERT OR REPLACE INTO usuarios 
                (usuario, email, password_hash, nombre_completo, rol, activo)
                VALUES (?, ?, ?, ?, ?, 1)
            ''', (usuario, email, password_hash, nombre_completo, rol))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            st.error(f"Error creando usuario: {e}")
            return False
    
    def autenticar_usuario(self, usuario: str, password: str) -> Optional[Dict]:
        """Autenticar usuario"""
        try:
            conn = sqlite3.connect(self.base_datos)
            cursor = conn.cursor()
            
            password_hash = self.hash_password(password)
            
            cursor.execute('''
                SELECT id, usuario, email, nombre_completo, rol, activo
                FROM usuarios 
                WHERE usuario = ? AND password_hash = ? AND activo = 1
            ''', (usuario, password_hash))
            
            resultado = cursor.fetchone()
            
            if resultado:
                # Actualizar último acceso
                cursor.execute('''
                    UPDATE usuarios 
                    SET ultimo_acceso = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (resultado[0],))
                
                conn.commit()
                conn.close()
                
                return {
                    'id': resultado[0],
                    'usuario': resultado[1],
                    'email': resultado[2],
                    'nombre_completo': resultado[3],
                    'rol': resultado[4],
                    'activo': bool(resultado[5])
                }
            
            conn.close()
            return None
            
        except Exception as e:
            st.error(f"Error autenticando usuario: {e}")
            return None
    
    def crear_sesion(self, usuario_id: int, ip_address: str = None, user_agent: str = None) -> str:
        """Crear nueva sesión para el usuario"""
        try:
            session_id = str(uuid.uuid4())
            fecha_expiracion = datetime.now() + timedelta(seconds=self.session_timeout)
            
            conn = sqlite3.connect(self.base_datos)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO sesiones 
                (session_id, usuario_id, fecha_expiracion, ip_address, user_agent, activa)
                VALUES (?, ?, ?, ?, ?, 1)
            ''', (session_id, usuario_id, fecha_expiracion, ip_address, user_agent))
            
            conn.commit()
            conn.close()
            
            return session_id
            
        except Exception as e:
            st.error(f"Error creando sesión: {e}")
            return None
    
    def validar_sesion(self, session_id: str) -> Optional[Dict]:
        """Validar sesión activa"""
        try:
            conn = sqlite3.connect(self.base_datos)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT s.session_id, s.usuario_id, s.fecha_expiracion, 
                       u.usuario, u.email, u.nombre_completo, u.rol
                FROM sesiones s
                JOIN usuarios u ON s.usuario_id = u.id
                WHERE s.session_id = ? AND s.activa = 1 AND u.activo = 1
                AND s.fecha_expiracion > CURRENT_TIMESTAMP
            ''', (session_id,))
            
            resultado = cursor.fetchone()
            
            if resultado:
                return {
                    'session_id': resultado[0],
                    'usuario_id': resultado[1],
                    'fecha_expiracion': resultado[2],
                    'usuario': resultado[3],
                    'email': resultado[4],
                    'nombre_completo': resultado[5],
                    'rol': resultado[6]
                }
            
            conn.close()
            return None
            
        except Exception as e:
            st.error(f"Error validando sesión: {e}")
            return None
    
    def verificar_sesion(self, session_id: str) -> Optional[Dict]:
        """Verificar sesión (alias de validar_sesion)"""
        return self.validar_sesion(session_id)
    
    def cerrar_sesion(self, session_id: str) -> bool:
        """Cerrar sesión"""
        try:
            conn = sqlite3.connect(self.base_datos)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE sesiones 
                SET activa = 0
                WHERE session_id = ?
            ''', (session_id,))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            st.error(f"Error cerrando sesión: {e}")
            return False
    
    def verificar_permiso(self, rol: str, modulo: str, permiso: str = 'read') -> bool:
        """Verificar si el rol tiene permiso para acceder al módulo"""
        try:
            conn = sqlite3.connect(self.base_datos)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT COUNT(*) 
                FROM permisos_rol 
                WHERE rol = ? AND modulo = ? AND permiso = ? AND activo = 1
            ''', (rol, modulo, permiso))
            
            resultado = cursor.fetchone()
            conn.close()
            
            return resultado[0] > 0
            
        except Exception as e:
            st.error(f"Error verificando permiso: {e}")
            return False
    
    def obtener_dashboards_disponibles(self, rol: str) -> List[Dict]:
        """Obtener dashboards disponibles para el rol"""
        dashboards = {
            'dashboard_maestro': {
                'nombre': 'Dashboard Maestro Unificado',
                'descripcion': 'Sistema central que integra todos los dashboards',
                'icono': '🏠',
                'archivo': 'dashboard_maestro_unificado_metgo.py',
                'puerto': 8513,
                'color': '#2ecc71'
            },
            'dashboard_principal': {
                'nombre': 'Dashboard Principal Integrado',
                'descripcion': 'Sistema unificado con todas las funcionalidades',
                'icono': '🌾',
                'archivo': 'dashboard_principal_integrado_metgo.py',
                'puerto': 8512,
                'color': '#3498db'
            },
            'dashboard_meteorologico_mejorado': {
                'nombre': 'Dashboard Meteorológico Mejorado',
                'descripcion': 'Datos meteorológicos con métricas y pronósticos de 14 días',
                'icono': '🌤️',
                'archivo': 'dashboard_meteorologico_final.py',
                'puerto': 8502,
                'color': '#3498db'
            },
            'dashboard_recomendaciones': {
                'nombre': 'Dashboard de Recomendaciones',
                'descripcion': 'Recomendaciones integradas de riego, plagas y heladas',
                'icono': '💡',
                'archivo': 'dashboard_integrado_recomendaciones_metgo.py',
                'puerto': 8510,
                'color': '#f39c12'
            },
            'sistema_alertas': {
                'nombre': 'Sistema de Alertas Visuales',
                'descripcion': 'Alertas meteorológicas y recomendaciones de emergencia',
                'icono': '🚨',
                'archivo': 'sistema_alertas_visuales_integrado_metgo.py',
                'puerto': 8511,
                'color': '#e74c3c'
            },
            'dashboard_empresarial': {
                'nombre': 'Dashboard Empresarial',
                'descripcion': 'Vista ejecutiva con métricas empresariales',
                'icono': '📊',
                'archivo': 'dashboard_empresarial_unificado_metgo.py',
                'puerto': 8503,
                'color': '#667eea'
            },
            'dashboard_agricola': {
                'nombre': 'Dashboard Agrícola',
                'descripcion': 'Gestión completa de cultivos y producción',
                'icono': '🌱',
                'archivo': 'dashboard_agricola_avanzado_metgo.py',
                'puerto': 8501,
                'color': '#27ae60'
            },
            'dashboard_drones': {
                'nombre': 'Dashboard con Drones',
                'descripcion': 'Monitoreo aéreo y análisis de cultivos',
                'icono': '🚁',
                'archivo': 'dashboard_unificado_metgo_con_drones.py',
                'puerto': 8504,
                'color': '#9b59b6'
            },
            'sistema_economico': {
                'nombre': 'Sistema Económico',
                'descripcion': 'Análisis de ROI y rentabilidad',
                'icono': '💰',
                'archivo': 'analisis_economico_agricola_metgo_con_conversion.py',
                'puerto': None,
                'color': '#f39c12'
            },
            'sistema_integracion': {
                'nombre': 'Sistema de Integración',
                'descripcion': 'ERP, GPS e IoT integrados',
                'icono': '🔗',
                'archivo': 'integracion_sistemas_existentes_metgo.py',
                'puerto': None,
                'color': '#34495e'
            },
            'reportes': {
                'nombre': 'Reportes',
                'descripcion': 'Generación de reportes ejecutivos',
                'icono': '📈',
                'archivo': 'generador_reportes_avanzados.py',
                'puerto': None,
                'color': '#2c3e50'
            },
            'configuracion': {
                'nombre': 'Configuración',
                'descripcion': 'Configuración del sistema',
                'icono': '⚙️',
                'archivo': 'configuracion_sistema.py',
                'puerto': None,
                'color': '#95a5a6'
            }
        }
        
        dashboards_disponibles = []
        for modulo_id, dashboard in dashboards.items():
            if self.verificar_permiso(rol, modulo_id, 'read'):
                dashboards_disponibles.append({
                    'id': modulo_id,
                    **dashboard
                })
        
        return dashboards_disponibles

def render_login_page():
    """Renderizar página de login"""
    st.set_page_config(
        page_title="METGO 3D - Login",
        page_icon="🔐",
        layout="centered",
        initial_sidebar_state="collapsed"
    )
    
    # Crear instancia del sistema de autenticación
    auth_system = SistemaAutenticacionMetgo()
    
    # CSS para página de login
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
        
        .login-form {
            margin-top: 2rem;
        }
        
        .login-button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 10px;
            padding: 0.8rem 2rem;
            font-weight: 600;
            font-size: 1rem;
            width: 100%;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .login-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        }
        
        .user-info {
            background: #f8f9fa;
            padding: 1rem;
            border-radius: 10px;
            margin-bottom: 1rem;
            border-left: 4px solid #667eea;
        }
        
        .error-message {
            background: #f8d7da;
            color: #721c24;
            padding: 1rem;
            border-radius: 10px;
            border: 1px solid #f5c6cb;
            margin-bottom: 1rem;
        }
        
        .success-message {
            background: #d4edda;
            color: #155724;
            padding: 1rem;
            border-radius: 10px;
            border: 1px solid #c3e6cb;
            margin-bottom: 1rem;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown("""
    <div class="login-header">
        <h1 class="login-title">METGO 3D</h1>
        <p class="login-subtitle">Sistema de Gestión Agrícola Inteligente</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Inicializar sistema de autenticación
    auth_system = SistemaAutenticacionMetgo()
    
    # Verificar si ya está autenticado
    if 'session_id' in st.session_state and st.session_state.session_id:
        session_data = auth_system.validar_sesion(st.session_state.session_id)
        if session_data:
            # Usuario ya autenticado, mostrar dashboard
            render_dashboard_selector(auth_system, session_data)
            return
    
    # Formulario de login
    with st.form("login_form"):
        st.markdown("### 🔐 Iniciar Sesión")
        
        usuario = st.text_input("👤 Usuario", placeholder="Ingresa tu usuario")
        password = st.text_input("🔑 Contraseña", type="password", placeholder="Ingresa tu contraseña")
        
        col1, col2 = st.columns(2)
        with col1:
            submit_button = st.form_submit_button("🚀 Iniciar Sesión", use_container_width=True)
        with col2:
            register_button = st.form_submit_button("📝 Registrarse", use_container_width=True)
        
        if submit_button:
            if usuario and password:
                user_data = auth_system.autenticar_usuario(usuario, password)
                if user_data:
                    # Crear sesión
                    session_id = auth_system.crear_sesion(user_data['id'])
                    if session_id:
                        st.session_state.session_id = session_id
                        st.session_state.user_data = user_data
                        st.success("✅ ¡Inicio de sesión exitoso!")
                        st.rerun()
                    else:
                        st.error("❌ Error creando sesión")
                else:
                    st.error("❌ Usuario o contraseña incorrectos")
            else:
                st.error("❌ Por favor, completa todos los campos")
        
        if register_button:
            st.info("📝 Función de registro en desarrollo")
    
    # Verificar si el usuario acaba de hacer login exitoso
    if 'session_id' in st.session_state and st.session_state.session_id:
        st.markdown("### 🚀 Acceso a Dashboards")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🏠 Dashboard Principal", use_container_width=True):
                st.markdown("[Abrir Dashboard Principal](http://localhost:8512)")
        with col2:
            if st.button("🌤️ Dashboard Meteorológico", use_container_width=True):
                st.markdown("[Abrir Dashboard Meteorológico](http://localhost:8502)")
        
        # Enlaces directos
        st.markdown("### 📋 Enlaces Directos")
        st.markdown("**Dashboard Principal Integrado:** [http://localhost:8512](http://localhost:8512)")
        st.markdown("**Dashboard Meteorológico:** [http://localhost:8502](http://localhost:8502)")
        st.markdown("**Dashboard Agrícola:** [http://localhost:8501](http://localhost:8501)")
        st.markdown("**Dashboard Empresarial:** [http://localhost:8503](http://localhost:8503)")
        
        st.markdown("---")
    
    # Información de usuarios por defecto
    st.markdown("""
    <div class="user-info">
        <h4>👥 Usuarios de Prueba</h4>
        <p><strong>Administrador:</strong> admin / admin123</p>
        <p><strong>Ejecutivo:</strong> ejecutivo / ejecutivo123</p>
        <p><strong>Agricultor:</strong> agricultor / agricultor123</p>
        <p><strong>Técnico:</strong> tecnico / tecnico123</p>
        <p><strong>Usuario:</strong> usuario / usuario123</p>
    </div>
    """, unsafe_allow_html=True)

def render_dashboard_selector(auth_system, session_data):
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
        
        .logout-section {
            text-align: center;
            margin-top: 3rem;
            padding-top: 2rem;
            border-top: 1px solid #e9ecef;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Header con información del usuario
    st.markdown(f"""
    <div class="dashboard-header">
        <h1 class="dashboard-title">METGO 3D</h1>
        <p class="user-welcome">Bienvenido, {session_data['nombre_completo']} ({session_data['rol'].title()})</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Obtener dashboards disponibles para el rol
    dashboards = auth_system.obtener_dashboards_disponibles(session_data['rol'])
    
    if dashboards:
        st.markdown("### 🚀 Dashboards Disponibles")
        
        # Crear grid de dashboards
        cols = st.columns(2)
        for i, dashboard in enumerate(dashboards):
            with cols[i % 2]:
                st.markdown(f"""
                <div class="dashboard-card">
                    <div class="dashboard-icon" style="color: {dashboard['color']};">{dashboard['icono']}</div>
                    <h3 class="dashboard-name">{dashboard['nombre']}</h3>
                    <p class="dashboard-description">{dashboard['descripcion']}</p>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button(f"🚀 Abrir {dashboard['nombre']}", key=f"btn_{dashboard['id']}", use_container_width=True):
                    if dashboard['puerto']:
                        st.success(f"🚀 Abriendo {dashboard['nombre']} en puerto {dashboard['puerto']}")
                        st.markdown(f"**URL:** http://localhost:{dashboard['puerto']}")
                        st.info("💡 Usa el mismo usuario y contraseña para acceder al dashboard")
                    else:
                        st.info(f"📄 Ejecutando {dashboard['nombre']}...")
                        st.code(f"python {dashboard['archivo']}")
    
    else:
        st.warning("⚠️ No tienes permisos para acceder a ningún dashboard")
    
    # Información de la sesión
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Usuario", session_data['usuario'])
    with col2:
        st.metric("Rol", session_data['rol'].title())
    with col3:
        st.metric("Sesión", "Activa")
    
    # Botón de logout
    st.markdown('<div class="logout-section">', unsafe_allow_html=True)
    if st.button("🚪 Cerrar Sesión", use_container_width=True):
        auth_system.cerrar_sesion(st.session_state.session_id)
        del st.session_state.session_id
        del st.session_state.user_data
        st.success("✅ Sesión cerrada exitosamente")
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

def main():
    """Función principal del sistema de autenticación"""
    auth_system = SistemaAutenticacionMetgo()
    
    # Verificar si hay una sesión activa
    if 'session_id' in st.session_state and st.session_state.session_id:
        session_data = auth_system.verificar_sesion(st.session_state.session_id)
        if session_data:
            # Usuario autenticado, mostrar selector de dashboards
            render_dashboard_selector(auth_system, session_data)
        else:
            # Sesión inválida, limpiar y mostrar login
            if 'session_id' in st.session_state:
                del st.session_state.session_id
            if 'user_data' in st.session_state:
                del st.session_state.user_data
            render_login_page()
    else:
        # No hay sesión, mostrar página de login
        render_login_page()

if __name__ == "__main__":
    main()
