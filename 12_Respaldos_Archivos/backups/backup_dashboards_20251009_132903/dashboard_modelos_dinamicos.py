"""
DASHBOARD MODELOS DINÁMICOS - METGO 3D QUILLOTA
Dashboard interactivo para crear, entrenar y ejecutar modelos de ML dinámicamente
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
import json
from sistema_modelos_dinamicos import SistemaModelosDinamicos

# Configuración de página
st.set_page_config(
    page_title="Modelos Dinámicos - METGO 3D",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

class DashboardModelosDinamicos:
    def __init__(self):
        self.sistema = SistemaModelosDinamicos()
        self._inicializar_session_state()
    
    def _inicializar_session_state(self):
        """Inicializar estado de sesión"""
        if 'modelos_creados' not in st.session_state:
            st.session_state.modelos_creados = []
        
        if 'proyecciones_generadas' not in st.session_state:
            st.session_state.proyecciones_generadas = {}
        
        if 'datos_historicos_cargados' not in st.session_state:
            st.session_state.datos_historicos_cargados = False
    
    def mostrar_header(self):
        """Mostrar header del dashboard"""
        st.title("🔬 Sistema de Modelos Dinámicos")
        st.markdown("**Crear, entrenar y ejecutar modelos de Machine Learning personalizados**")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Modelos Activos",
                len(self.sistema.modelos_activos),
                delta=None
            )
        
        with col2:
            st.metric(
                "Variables Disponibles",
                len(self.sistema.variables_objetivo),
                delta=None
            )
        
        with col3:
            st.metric(
                "Tipos de Modelos",
                len(self.sistema.catalogo_modelos),
                delta=None
            )
        
        with col4:
            st.metric(
                "Proyecciones Hoy",
                len(st.session_state.proyecciones_generadas),
                delta=None
            )
    
    def mostrar_sidebar(self):
        """Mostrar sidebar con controles"""
        st.sidebar.title("🎛️ Panel de Control")
        
        # Sección de datos históricos
        st.sidebar.header("📊 Datos Históricos")
        
        if st.sidebar.button("Generar Datos 3 Años", type="primary"):
            with st.spinner("Generando datos históricos de 3 años..."):
                df = self.sistema.generar_datos_historicos_3_anos()
                if not df.empty:
                    st.session_state.datos_historicos_cargados = True
                    st.sidebar.success(f"Datos generados: {len(df)} registros")
                else:
                    st.sidebar.error("Error generando datos")
        
        # Estado de datos
        if st.session_state.datos_historicos_cargados:
            st.sidebar.success("✅ Datos históricos listos")
        else:
            st.sidebar.warning("⚠️ Datos históricos no generados")
        
        # Sección de modelos
        st.sidebar.header("🤖 Gestión de Modelos")
        
        # Mostrar modelos activos
        modelos_activos = self.sistema.listar_modelos_activos()
        if modelos_activos:
            st.sidebar.write("**Modelos Activos:**")
            for modelo in modelos_activos:
                st.sidebar.write(f"• {modelo['nombre']} (R²={modelo['r2']:.3f})")
        else:
            st.sidebar.write("No hay modelos activos")
        
        # Sección de configuración
        st.sidebar.header("⚙️ Configuración")
        
        mostrar_detalles = st.sidebar.checkbox("Mostrar Detalles Técnicos", value=False)
        
        return {
            'mostrar_detalles': mostrar_detalles
        }
    
    def mostrar_tab_crear_modelo(self):
        """Mostrar tab para crear nuevos modelos"""
        st.header("🆕 Crear Nuevo Modelo")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Formulario para crear modelo
            with st.form("crear_modelo_form"):
                st.subheader("Configuración del Modelo")
                
                # Información básica
                col_nombre, col_tipo = st.columns(2)
                
                with col_nombre:
                    nombre_modelo = st.text_input(
                        "Nombre del Modelo",
                        placeholder="ej: RF_Temp_Avanzado",
                        help="Nombre único para identificar el modelo"
                    )
                
                with col_tipo:
                    tipos_modelo = list(self.sistema.catalogo_modelos.keys())
                    tipo_modelo = st.selectbox(
                        "Tipo de Modelo",
                        tipos_modelo,
                        help="Selecciona el algoritmo de Machine Learning"
                    )
                
                # Variable objetivo
                variables_objetivo = list(self.sistema.variables_objetivo.keys())
                variable_objetivo = st.selectbox(
                    "Variable Objetivo",
                    variables_objetivo,
                    format_func=lambda x: f"{x} ({self.sistema.variables_objetivo[x]['unidad']})",
                    help="Variable que el modelo va a predecir"
                )
                
                # Descripción
                descripcion = st.text_area(
                    "Descripción",
                    placeholder="Descripción opcional del modelo...",
                    help="Descripción del propósito del modelo"
                )
                
                # Parámetros personalizados
                st.subheader("Parámetros Personalizados")
                
                parametros_personalizados = {}
                config_modelo = self.sistema.catalogo_modelos[tipo_modelo]
                
                # Mostrar parámetros editables
                for param, valores in config_modelo['parametros_base'].items():
                    if param not in ['random_state', 'n_jobs']:
                        if isinstance(valores, list) and len(valores) > 1:
                            # Parámetro con múltiples opciones
                            valor_actual = valores[0] if isinstance(valores[0], (int, float)) else valores[0]
                            parametros_personalizados[param] = st.selectbox(
                                f"{param}",
                                valores,
                                index=0,
                                help=f"Parámetro {param} para {tipo_modelo}"
                            )
                        elif isinstance(valores, (int, float)):
                            # Parámetro numérico
                            parametros_personalizados[param] = st.number_input(
                                f"{param}",
                                value=valores,
                                help=f"Parámetro {param} para {tipo_modelo}"
                            )
                        else:
                            # Parámetro de texto
                            parametros_personalizados[param] = st.text_input(
                                f"{param}",
                                value=str(valores),
                                help=f"Parámetro {param} para {tipo_modelo}"
                            )
                
                # Botón de creación
                submitted = st.form_submit_button("Crear y Entrenar Modelo", type="primary")
                
                if submitted:
                    if nombre_modelo and tipo_modelo and variable_objetivo:
                        with st.spinner("Creando y entrenando modelo..."):
                            resultado = self.sistema.crear_nuevo_modelo(
                                nombre_modelo=nombre_modelo,
                                tipo_modelo=tipo_modelo,
                                variable_objetivo=variable_objetivo,
                                parametros_personalizados=parametros_personalizados,
                                descripcion=descripcion
                            )
                            
                            if 'error' not in resultado:
                                st.success(f"Modelo '{nombre_modelo}' creado exitosamente!")
                                
                                # Mostrar métricas
                                metricas = resultado['metricas']
                                col_metric1, col_metric2, col_metric3 = st.columns(3)
                                
                                with col_metric1:
                                    st.metric("R²", f"{metricas['r2']:.4f}")
                                
                                with col_metric2:
                                    st.metric("RMSE", f"{metricas['rmse']:.4f}")
                                
                                with col_metric3:
                                    st.metric("MAE", f"{metricas['mae']:.4f}")
                                
                                # Actualizar estado
                                st.session_state.modelos_creados.append(resultado)
                                st.rerun()
                            else:
                                st.error(f"Error creando modelo: {resultado['error']}")
                    else:
                        st.error("Por favor completa todos los campos obligatorios")
        
        with col2:
            # Información del tipo de modelo seleccionado
            if 'tipo_modelo' in locals():
                st.subheader(f"ℹ️ {tipo_modelo}")
                config = self.sistema.catalogo_modelos[tipo_modelo]
                st.write(f"**Descripción:** {config['descripcion']}")
                
                st.write("**Parámetros por defecto:**")
                for param, valor in config['parametros_base'].items():
                    if param not in ['random_state', 'n_jobs']:
                        st.write(f"• {param}: {valor}")
    
    def mostrar_tab_proyecciones(self):
        """Mostrar tab para generar proyecciones"""
        st.header("📈 Generar Proyecciones")
        
        # Seleccionar modelo
        modelos_activos = self.sistema.listar_modelos_activos()
        
        if not modelos_activos:
            st.warning("No hay modelos activos. Crea un modelo primero.")
            return
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("Configuración de Proyecciones")
            
            # Selector de modelo
            modelo_seleccionado = st.selectbox(
                "Seleccionar Modelo",
                [m['nombre'] for m in modelos_activos],
                format_func=lambda x: f"{x} ({next(m['tipo'] for m in modelos_activos if m['nombre'] == x)})"
            )
            
            # Información del modelo seleccionado
            modelo_info = next(m for m in modelos_activos if m['nombre'] == modelo_seleccionado)
            
            col_info1, col_info2, col_info3 = st.columns(3)
            
            with col_info1:
                st.metric("Tipo", modelo_info['tipo'])
            
            with col_info2:
                st.metric("Variable", modelo_info['variable_objetivo'])
            
            with col_info3:
                st.metric("R²", f"{modelo_info['r2']:.4f}")
            
            # Configuración de proyección
            col_config1, col_config2 = st.columns(2)
            
            with col_config1:
                horizonte_dias = st.slider(
                    "Horizonte de Proyección (días)",
                    min_value=1,
                    max_value=90,
                    value=30,
                    help="Número de días hacia el futuro para proyectar"
                )
            
            with col_config2:
                incluir_intervalos = st.checkbox(
                    "Incluir Intervalos de Confianza",
                    value=True,
                    help="Mostrar intervalos de confianza del 95%"
                )
            
            # Generar proyecciones
            if st.button("Generar Proyecciones", type="primary"):
                with st.spinner("Generando proyecciones..."):
                    proyecciones = self.sistema.generar_proyecciones(
                        modelo_seleccionado,
                        horizonte_dias,
                        incluir_intervalos
                    )
                    
                    if proyecciones:
                        st.session_state.proyecciones_generadas[modelo_seleccionado] = proyecciones
                        st.success(f"Proyecciones generadas: {len(proyecciones)} puntos")
                        st.rerun()
                    else:
                        st.error("Error generando proyecciones")
        
        with col2:
            # Mostrar proyecciones si existen
            if modelo_seleccionado in st.session_state.proyecciones_generadas:
                st.subheader("📊 Proyecciones Actuales")
                
                proyecciones = st.session_state.proyecciones_generadas[modelo_seleccionado]
                
                # Crear gráfico
                df_proyecciones = pd.DataFrame(proyecciones)
                df_proyecciones['fecha'] = pd.to_datetime(df_proyecciones['fecha'])
                
                fig = go.Figure()
                
                # Línea principal
                fig.add_trace(go.Scatter(
                    x=df_proyecciones['fecha'],
                    y=df_proyecciones['valor_proyectado'],
                    mode='lines+markers',
                    name='Proyección',
                    line=dict(color='blue', width=3),
                    marker=dict(size=6)
                ))
                
                # Intervalos de confianza
                if incluir_intervalos and 'intervalo_confianza_inferior' in df_proyecciones.columns:
                    fig.add_trace(go.Scatter(
                        x=df_proyecciones['fecha'],
                        y=df_proyecciones['intervalo_confianza_superior'],
                        mode='lines',
                        name='Confianza 95%',
                        line=dict(width=0),
                        showlegend=False
                    ))
                    
                    fig.add_trace(go.Scatter(
                        x=df_proyecciones['fecha'],
                        y=df_proyecciones['intervalo_confianza_inferior'],
                        mode='lines',
                        name='Intervalo Confianza',
                        line=dict(width=0),
                        fill='tonexty',
                        fillcolor='rgba(0,100,80,0.2)',
                        showlegend=True
                    ))
                
                fig.update_layout(
                    title=f"Proyecciones: {modelo_info['variable_objetivo']}",
                    xaxis_title="Fecha",
                    yaxis_title=f"{modelo_info['variable_objetivo']} ({self.sistema.variables_objetivo[modelo_info['variable_objetivo']]['unidad']}, showlegend=False)",
                    hovermode='x unified',
                    height=400
                )
                
                st.plotly_chart(fig, config=PLOTLY_CONFIG, width='stretch')
                
                # Tabla de proyecciones
                st.subheader("📋 Datos de Proyección")
                
                df_mostrar = df_proyecciones[['fecha', 'valor_proyectado', 'confianza']].copy()
                df_mostrar['fecha'] = df_mostrar['fecha'].dt.strftime('%Y-%m-%d')
                df_mostrar['valor_proyectado'] = df_mostrar['valor_proyectado'].round(2)
                df_mostrar['confianza'] = (df_mostrar['confianza'] * 100).round(1).astype(str) + '%'
                
                st.dataframe(df_mostrar, width='stretch')
    
    def mostrar_tab_analisis_modelos(self):
        """Mostrar tab de análisis de modelos"""
        st.header("📊 Análisis de Modelos")
        
        modelos_activos = self.sistema.listar_modelos_activos()
        
        if not modelos_activos:
            st.warning("No hay modelos para analizar. Crea algunos modelos primero.")
            return
        
        # Resumen de modelos
        st.subheader("📈 Resumen de Modelos")
        
        df_modelos = pd.DataFrame(modelos_activos)
        
        # Gráfico de comparación de R²
        fig_r2 = px.bar(
            df_modelos,
            x='nombre',
            y='r2',
            title='Comparación de R² por Modelo',
            color='r2',
            color_continuous_scale='Viridis'
        )
        fig_r2.update_layout(height=400)
        st.plotly_chart(fig_r2, config=PLOTLY_CONFIG, width='stretch')
        
        # Gráfico de comparación de RMSE
        fig_rmse = px.bar(
            df_modelos,
            x='nombre',
            y='rmse',
            title='Comparación de RMSE por Modelo (Menor es Mejor)',
            color='rmse',
            color_continuous_scale='Reds_r'
        )
        fig_rmse.update_layout(height=400)
        st.plotly_chart(fig_rmse, config=PLOTLY_CONFIG, width='stretch')
        
        # Tabla detallada
        st.subheader("📋 Métricas Detalladas")
        
        df_mostrar = df_modelos[['nombre', 'tipo', 'variable_objetivo', 'r2', 'rmse', 'fecha_creacion']].copy()
        df_mostrar['r2'] = df_mostrar['r2'].round(4)
        df_mostrar['rmse'] = df_mostrar['rmse'].round(4)
        
        st.dataframe(df_mostrar, width='stretch')
        
        # Análisis por tipo de modelo
        st.subheader("🔍 Análisis por Tipo de Modelo")
        
        tipo_stats = df_modelos.groupby('tipo').agg({
            'r2': ['mean', 'std', 'count'],
            'rmse': ['mean', 'std']
        }).round(4)
        
        st.dataframe(tipo_stats, width='stretch')
    
    def mostrar_tab_catalogo(self):
        """Mostrar tab del catálogo de modelos"""
        st.header("📚 Catálogo de Modelos Disponibles")
        
        catalogo = self.sistema.obtener_catalogo_modelos()
        variables = self.sistema.obtener_variables_objetivo()
        
        # Catálogo de tipos de modelos
        st.subheader("🤖 Tipos de Modelos")
        
        for tipo, config in catalogo.items():
            with st.expander(f"**{tipo}** - {config['descripcion']}"):
                st.write(f"**Descripción:** {config['descripcion']}")
                
                st.write("**Parámetros configurables:**")
                for param, valor in config['parametros_base'].items():
                    if param not in ['random_state', 'n_jobs']:
                        st.write(f"• `{param}`: {valor}")
                
                # Ejemplo de uso
                st.write("**Ejemplo de uso:**")
                st.code(f"""
sistema.crear_nuevo_modelo(
    nombre_modelo="Mi_{tipo}",
    tipo_modelo="{tipo}",
    variable_objetivo="temperatura_promedio",
    parametros_personalizados={{
        # Personalizar parámetros aquí
    }}
)
                """, language="python")
        
        # Variables objetivo
        st.subheader("🎯 Variables Objetivo")
        
        for variable, info in variables.items():
            with st.expander(f"**{info['nombre']}** ({info['unidad']})"):
                st.write(f"**Descripción:** {info['descripcion']}")
                st.write(f"**Unidad:** {info['unidad']}")
                st.write(f"**Variable:** `{variable}`")
    
    def ejecutar_dashboard(self):
        """Ejecutar dashboard principal"""
        self.mostrar_header()
        
        # Sidebar
        config = self.mostrar_sidebar()
        
        # Tabs principales
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "🆕 Crear Modelo",
            "📈 Proyecciones", 
            "📊 Análisis",
            "📚 Catálogo",
            "📄 Reportes"
        ])
        
        with tab1:
            self.mostrar_tab_crear_modelo()
        
        with tab2:
            self.mostrar_tab_proyecciones()
        
        with tab3:
            self.mostrar_tab_analisis_modelos()
        
        with tab4:
            self.mostrar_tab_catalogo()
        
        with tab5:
            self.mostrar_tab_reportes()

def main():
    """Función principal"""
    dashboard = DashboardModelosDinamicos()
    dashboard.ejecutar_dashboard()

if __name__ == "__main__":
    main()


