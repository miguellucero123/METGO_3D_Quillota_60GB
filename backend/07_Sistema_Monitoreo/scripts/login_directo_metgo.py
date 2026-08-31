"""
LOGIN DIRECTO METGO 3D QUILLOTA
Sistema de login ultra-simple que funciona sin problemas
"""

import streamlit as st
import webbrowser

def main():
    """Sistema de login directo"""
    st.set_page_config(
        page_title="METGO 3D - Login",
        page_icon="🔐",
        layout="centered"
    )
    
    # CSS simple
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
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown("""
    <div class="title">METGO 3D</div>
    <div class="subtitle">Sistema de Gestión Agrícola Inteligente</div>
    """, unsafe_allow_html=True)
    
    # Verificar si ya está logueado
    if 'logueado' in st.session_state and st.session_state.logueado:
        mostrar_dashboards()
        return
    
    # Formulario de login
    with st.form("login"):
        st.markdown("### 🔐 Iniciar Sesión")
        
        usuario = st.text_input("Usuario", value="admin", help="Ingresa tu usuario")
        password = st.text_input("Contraseña", type="password", value="admin123", help="Ingresa tu contraseña")
        
        col1, col2 = st.columns(2)
        with col1:
            login_btn = st.form_submit_button("🚀 Iniciar Sesión", use_container_width=True)
        with col2:
            reset_btn = st.form_submit_button("🔄 Limpiar", use_container_width=True)
        
        if login_btn:
            # Validación simple
            usuarios_validos = {
                'admin': 'admin123',
                'ejecutivo': 'ejecutivo123',
                'agricultor': 'CHANGE_ME_DEMO_AGRICULTOR',
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
        
        if reset_btn:
            st.rerun()
    
    # Información de usuarios
    st.markdown("""
    ### 👥 Usuarios de Prueba
    
    | Usuario | Contraseña | Rol |
    |---------|------------|-----|
    | admin | admin123 | Administrador |
    | ejecutivo | ejecutivo123 | Ejecutivo |
    | agricultor | CHANGE_ME_DEMO_AGRICULTOR | Agricultor |
    | tecnico | tecnico123 | Técnico |
    | usuario | usuario123 | Usuario |
    """)

def mostrar_dashboards():
    """Mostrar dashboards disponibles"""
    st.markdown("""
    <div class="title">🎯 Dashboard Central</div>
    <div class="subtitle">Bienvenido, {} ({})</div>
    """.format(
        st.session_state.usuario.title(),
        st.session_state.usuario.title()
    ), unsafe_allow_html=True)
    
    st.success("✅ Sesión iniciada correctamente")
    
    # Dashboards disponibles
    dashboards = {
        'dashboard_empresarial': {
            'nombre': 'Dashboard Empresarial',
            'descripcion': 'Vista ejecutiva con métricas empresariales',
            'puerto': 8503,
            'roles': ['admin', 'ejecutivo']
        },
        'dashboard_agricola': {
            'nombre': 'Dashboard Agrícola',
            'descripcion': 'Gestión completa de cultivos y producción',
            'puerto': 8501,
            'roles': ['admin', 'ejecutivo', 'agricultor', 'tecnico', 'usuario']
        },
        'dashboard_meteorologico': {
            'nombre': 'Dashboard Meteorológico',
            'descripcion': 'Monitoreo climático en tiempo real',
            'puerto': 8502,
            'roles': ['admin', 'ejecutivo', 'agricultor', 'tecnico', 'usuario']
        },
        'dashboard_drones': {
            'nombre': 'Dashboard con Drones',
            'descripcion': 'Monitoreo aéreo y análisis de cultivos',
            'puerto': 8504,
            'roles': ['admin', 'agricultor', 'tecnico']
        },
        'sistema_economico': {
            'nombre': 'Sistema Económico',
            'descripcion': 'Análisis de ROI y rentabilidad',
            'puerto': 8506,
            'roles': ['admin', 'ejecutivo', 'agricultor']
        }
    }
    
    # Filtrar dashboards por rol
    usuario_actual = st.session_state.usuario
    dashboards_disponibles = []
    
    for dashboard_id, dashboard in dashboards.items():
        if usuario_actual in dashboard['roles'] or usuario_actual == 'admin':
            dashboards_disponibles.append((dashboard_id, dashboard))
    
    st.markdown("### 🚀 Dashboards Disponibles")
    
    for dashboard_id, dashboard in dashboards_disponibles:
        with st.expander(f"📊 {dashboard['nombre']}"):
            st.write(f"**Descripción:** {dashboard['descripcion']}")
            st.write(f"**Puerto:** {dashboard['puerto']}")
            
            url = f"http://localhost:{dashboard['puerto']}"
            
            if st.button(f"🌐 Abrir {dashboard['nombre']}", key=f"btn_{dashboard_id}"):
                st.success(f"✅ Abriendo {dashboard['nombre']}")
                st.info(f"**URL:** {url}")
                st.info("💡 Usa las mismas credenciales: {} / {}".format(
                    st.session_state.usuario, 
                    st.session_state.password
                ))
                
                # Intentar abrir en navegador
                try:
                    webbrowser.open(url)
                    st.success("🌐 Navegador abierto")
                except:
                    st.info("📋 Copia la URL manualmente")
    
    # Botón de logout
    st.markdown("---")
    if st.button("🚪 Cerrar Sesión", use_container_width=True):
        del st.session_state.logueado
        del st.session_state.usuario
        del st.session_state.password
        st.success("✅ Sesión cerrada")
        st.rerun()

if __name__ == "__main__":
    main()


