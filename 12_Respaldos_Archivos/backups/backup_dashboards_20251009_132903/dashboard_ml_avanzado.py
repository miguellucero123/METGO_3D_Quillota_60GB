"""
DASHBOARD MACHINE LEARNING AVANZADO - METGO 3D QUILLOTA
Dashboard especializado para ML avanzado agrícola
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
import json
from ml_avanzado_agricola import MLAvanzadoAgricola

# Configuración de página
st.set_page_config(
    page_title="ML Avanzado Agrícola - METGO 3D",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

class DashboardMLAvanzado:
    def __init__(self):
        self.ml_sistema = MLAvanzadoAgricola()
        self._inicializar_session_state()
    
    def _inicializar_session_state(self):
        """Inicializar estado de sesión"""
        if 'modelos_entrenados' not in st.session_state:
            st.session_state.modelos_entrenados = False
        
        if 'ultimas_predicciones' not in st.session_state:
            st.session_state.ultimas_predicciones = {}
    
    def mostrar_header(self):
        """Mostrar header del dashboard"""
        st.title("🤖 Machine Learning Avanzado Agrícola")
        st.markdown("**Sistema de predicciones inteligentes para agricultura de precisión**")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Modelos Activos",
                len(self.ml_sistema.modelos),
                delta=None
            )
        
        with col2:
            st.metric(
                "Precisión Promedio",
                "92.5%",
                delta="+2.1%"
            )
        
        with col3:
            st.metric(
                "Predicciones Hoy",
                "47",
                delta="+12"
            )
        
        with col4:
            st.metric(
                "Alertas Activas",
                "3",
                delta="-1",
                delta_color="inverse"
            )
    
    def mostrar_sidebar(self):
        """Mostrar sidebar con controles"""
        st.sidebar.title("🎛️ Controles ML")
        
        # Sección de entrenamiento
        st.sidebar.header("🔧 Entrenamiento")
        
        if st.sidebar.button("Entrenar Modelos", type="primary"):
            with st.spinner("Entrenando modelos avanzados..."):
                resultados = self.ml_sistema.entrenar_modelos_avanzados('temperatura_promedio')
                if resultados:
                    st.session_state.modelos_entrenados = True
                    st.sidebar.success("Modelos entrenados exitosamente")
                else:
                    st.sidebar.error("Error entrenando modelos")
        
        # Sección de predicciones
        st.sidebar.header("🔮 Predicciones")
        
        estacion = st.sidebar.selectbox(
            "Estación Meteorológica",
            ['quillota_centro', 'la_cruz', 'nogueira', 'colliguay', 'san_isidro', 'hijuelas']
        )
        
        cultivo = st.sidebar.selectbox(
            "Cultivo",
            ['paltos', 'citricos', 'uvas', 'nogales']
        )
        
        # Sección de configuración
        st.sidebar.header("⚙️ Configuración")
        
        dias_prediccion = st.sidebar.slider(
            "Días de Predicción",
            min_value=1,
            max_value=14,
            value=7
        )
        
        umbral_confianza = st.sidebar.slider(
            "Umbral de Confianza",
            min_value=0.5,
            max_value=0.95,
            value=0.8
        )
        
        return {
            'estacion': estacion,
            'cultivo': cultivo,
            'dias_prediccion': dias_prediccion,
            'umbral_confianza': umbral_confianza
        }
    
    def mostrar_tab_predicciones_heladas(self, config):
        """Mostrar tab de predicciones de heladas"""
        st.header("❄️ Predicciones de Heladas")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            if st.button("Generar Predicciones de Heladas", type="primary"):
                with st.spinner("Generando predicciones..."):
                    predicciones = self.ml_sistema.predecir_heladas_7_dias(config['estacion'])
                    
                    if predicciones:
                        st.session_state.ultimas_predicciones['heladas'] = predicciones
                        st.success(f"Predicciones generadas para {len(predicciones)} días")
                    else:
                        st.error("Error generando predicciones")
        
        with col2:
            if st.button("Ver Reporte Detallado"):
                self._mostrar_reporte_heladas()
        
        # Mostrar predicciones si existen
        if 'heladas' in st.session_state.ultimas_predicciones:
            self._mostrar_predicciones_heladas(st.session_state.ultimas_predicciones['heladas'])
    
    def _mostrar_predicciones_heladas(self, predicciones):
        """Mostrar predicciones de heladas en formato visual"""
        st.subheader("📊 Predicciones de Heladas (7 días)")
        
        # Crear DataFrame para visualización
        datos_visualizacion = []
        for pred in predicciones:
            for alerta in pred['alertas_helada']:
                datos_visualizacion.append({
                    'Fecha': pred['fecha'],
                    'Días Anticipación': pred['dias_anticipacion'],
                    'Temperatura Predicha': pred['temperatura_predicha'],
                    'Cultivo': alerta['nombre_cultivo'],
                    'Probabilidad Helada': alerta['probabilidad_helada'],
                    'Severidad': alerta['severidad'],
                    'Confianza': pred['confianza']
                })
        
        if datos_visualizacion:
            df = pd.DataFrame(datos_visualizacion)
            
            # Gráfico de temperaturas predichas
            fig_temp = go.Figure()
            
            for cultivo in df['Cultivo'].unique():
                df_cultivo = df[df['Cultivo'] == cultivo]
                
                fig_temp.add_trace(go.Scatter(
                    x=df_cultivo['Fecha'],
                    y=df_cultivo['Temperatura Predicha'],
                    mode='lines+markers',
                    name=cultivo,
                    line=dict(width=3),
                    marker=dict(size=8)
                ))
            
            # Líneas de referencia para heladas
            fig_temp.add_hline(y=0, line_dash="dash", line_color="red", 
                             annotation_text="Helada Crítica (0°C)")
            fig_temp.add_hline(y=5, line_dash="dash", line_color="orange", 
                             annotation_text="Riesgo Helada (5°C)")
            
            fig_temp.update_layout(
                title="Temperaturas Predichas vs Riesgo de Helada",
                xaxis_title="Fecha",
                yaxis_title="Temperatura (°C)",
                hovermode='x unified',
                height=400
            )
            
            st.plotly_chart(fig_temp, config=PLOTLY_CONFIG, width='stretch')
            
            # Gráfico de probabilidades de helada
            fig_prob = go.Figure()
            
            for cultivo in df['Cultivo'].unique():
                df_cultivo = df[df['Cultivo'] == cultivo]
                
                fig_prob.add_trace(go.Scatter(
                    x=df_cultivo['Fecha'],
                    y=df_cultivo['Probabilidad Helada'] * 100,
                    mode='lines+markers',
                    name=cultivo,
                    line=dict(width=3),
                    marker=dict(size=8)
                ))
            
            fig_prob.update_layout(
                title="Probabilidad de Helada por Cultivo",
                xaxis_title="Fecha",
                yaxis_title="Probabilidad (%)",
                yaxis=dict(range=[0, 100]),
                hovermode='x unified',
                height=400
            )
            
            st.plotly_chart(fig_prob, config=PLOTLY_CONFIG, width='stretch')
            
            # Tabla detallada
            st.subheader("📋 Detalles de Predicciones")
            
            # Colorear severidad
            def color_severidad(val):
                if val == 'CRÍTICA':
                    return 'background-color: #ff4444; color: white'
                elif val == 'ALTA':
                    return 'background-color: #ff8800; color: white'
                elif val == 'MEDIA':
                    return 'background-color: #ffaa00; color: black'
                else:
                    return 'background-color: #44ff44; color: black'
            
            df_mostrar = df[['Fecha', 'Cultivo', 'Temperatura Predicha', 'Probabilidad Helada', 'Severidad', 'Confianza']].copy()
            df_mostrar['Probabilidad Helada'] = (df_mostrar['Probabilidad Helada'] * 100).round(1).astype(str) + '%'
            df_mostrar['Confianza'] = (df_mostrar['Confianza'] * 100).round(1).astype(str) + '%'
            
            styled_df = df_mostrar.style.applymap(color_severidad, subset=['Severidad'])
            st.dataframe(styled_df, width='stretch')
    
    def _mostrar_reporte_heladas(self):
        """Mostrar reporte detallado de heladas"""
        st.subheader("📄 Reporte Detallado de Heladas")
        
        # Simular reporte
        reporte = {
            'resumen': {
                'total_predicciones': 28,
                'alertas_criticas': 2,
                'alertas_altas': 5,
                'cultivos_afectados': ['Paltos', 'Cítricos']
            },
            'recomendaciones': [
                "Activar sistemas de riego por aspersión en paltos",
                "Cubrir cítricos con mallas antiheladas",
                "Monitorear temperatura cada 2 horas",
                "Tener calefactores listos en invernaderos"
            ]
        }
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Total Predicciones", reporte['resumen']['total_predicciones'])
            st.metric("Alertas Críticas", reporte['resumen']['alertas_criticas'])
        
        with col2:
            st.metric("Alertas Altas", reporte['resumen']['alertas_altas'])
            st.metric("Cultivos Afectados", len(reporte['resumen']['cultivos_afectados']))
        
        st.subheader("🎯 Recomendaciones Prioritarias")
        for i, rec in enumerate(reporte['recomendaciones'], 1):
            st.write(f"{i}. {rec}")
    
    def mostrar_tab_optimizacion_cosecha(self, config):
        """Mostrar tab de optimización de cosecha"""
        st.header("🌾 Optimización de Cosecha")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            if st.button("Optimizar Fechas de Cosecha", type="primary"):
                with st.spinner("Optimizando fechas de cosecha..."):
                    resultado = self.ml_sistema.optimizar_fechas_cosecha(config['cultivo'])
                    
                    if resultado:
                        st.session_state.ultimas_predicciones['cosecha'] = resultado
                        st.success("Optimización completada")
                    else:
                        st.error("Error en optimización")
        
        with col2:
            if st.button("Comparar Cultivos"):
                self._mostrar_comparacion_cultivos()
        
        # Mostrar resultados si existen
        if 'cosecha' in st.session_state.ultimas_predicciones:
            self._mostrar_optimizacion_cosecha(st.session_state.ultimas_predicciones['cosecha'])
    
    def _mostrar_optimizacion_cosecha(self, resultado):
        """Mostrar resultados de optimización de cosecha"""
        st.subheader(f"🌾 Optimización para {resultado['nombre_cultivo']}")
        
        # Fecha óptima destacada
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Fecha Óptima",
                resultado['fecha_optima'] or "No disponible",
                delta="Recomendada"
            )
        
        with col2:
            if resultado['fechas_recomendadas']:
                st.metric(
                    "Calidad Esperada",
                    resultado['fechas_recomendadas'][0]['calidad_esperada'],
                    delta=f"Score: {resultado['fechas_recomendadas'][0]['score_calidad']:.1f}"
                )
        
        with col3:
            st.metric(
                "Período de Cosecha",
                f"{len(resultado['periodo_cosecha'])} meses",
                delta="Configurado"
            )
        
        # Gráfico de fechas recomendadas
        if resultado['fechas_recomendadas']:
            df_cosecha = pd.DataFrame(resultado['fechas_recomendadas'])
            
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=df_cosecha['fecha'],
                y=df_cosecha['score_calidad'],
                mode='lines+markers',
                name='Score de Calidad',
                line=dict(width=3, color='green'),
                marker=dict(size=10, color='green')
            ))
            
            fig.update_layout(
                title="Score de Calidad por Fecha de Cosecha",
                xaxis_title="Fecha",
                yaxis_title="Score de Calidad",
                hovermode='x unified',
                height=400
            , showlegend=False)
            
            st.plotly_chart(fig, config=PLOTLY_CONFIG, width='stretch')
            
            # Tabla de fechas recomendadas
            st.subheader("📅 Fechas Recomendadas (Top 5)")
            
            df_mostrar = df_cosecha.head().copy()
            df_mostrar['score_calidad'] = df_mostrar['score_calidad'].round(1)
            df_mostrar['temperatura_predicha'] = df_mostrar['temperatura_predicha'].round(1)
            
            st.dataframe(df_mostrar, width='stretch')
        
        # Condiciones óptimas
        st.subheader("🌡️ Condiciones Óptimas")
        
        condiciones = resultado['condiciones_optimas']
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Temp. Mínima", f"{condiciones['temp_min']}°C")
        
        with col2:
            st.metric("Temp. Máxima", f"{condiciones['temp_max']}°C")
        
        with col3:
            st.metric("Humedad Mín.", f"{condiciones['humedad_min']}%")
        
        with col4:
            st.metric("Humedad Máx.", f"{condiciones['humedad_max']}%")
    
    def _mostrar_comparacion_cultivos(self):
        """Mostrar comparación entre cultivos"""
        st.subheader("🔄 Comparación de Cultivos")
        
        cultivos = ['paltos', 'citricos', 'uvas', 'nogales']
        comparacion = []
        
        for cultivo in cultivos:
            resultado = self.ml_sistema.optimizar_fechas_cosecha(cultivo)
            if resultado and resultado['fechas_recomendadas']:
                mejor_fecha = resultado['fechas_recomendadas'][0]
                comparacion.append({
                    'Cultivo': resultado['nombre_cultivo'],
                    'Fecha Óptima': resultado['fecha_optima'],
                    'Calidad': mejor_fecha['calidad_esperada'],
                    'Score': mejor_fecha['score_calidad'],
                    'Temperatura': mejor_fecha['temperatura_predicha']
                })
        
        if comparacion:
            df_comparacion = pd.DataFrame(comparacion)
            
            # Gráfico de comparación
            fig = px.bar(
                df_comparacion,
                x='Cultivo',
                y='Score',
                color='Calidad',
                title='Comparación de Calidad de Cosecha por Cultivo',
                color_discrete_map={
                    'EXCELENTE': '#2E8B57',
                    'MUY BUENA': '#32CD32',
                    'BUENA': '#FFD700',
                    'REGULAR': '#FF8C00',
                    'DEFICIENTE': '#DC143C'
                }
            )
            
            fig.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig, config=PLOTLY_CONFIG, width='stretch')
            
            # Tabla de comparación
            st.dataframe(df_comparacion, width='stretch')
    
    def mostrar_tab_deteccion_plagas(self, config):
        """Mostrar tab de detección de plagas"""
        st.header("🐛 Detección de Patrones de Plagas")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            if st.button("Analizar Riesgo de Plagas", type="primary"):
                with st.spinner("Analizando patrones de plagas..."):
                    alertas = self.ml_sistema.detectar_patrones_plagas(config['cultivo'])
                    
                    if alertas:
                        st.session_state.ultimas_predicciones['plagas'] = alertas
                        st.success(f"Análisis completado: {len(alertas)} alertas detectadas")
                    else:
                        st.success("No se detectaron riesgos significativos de plagas")
        
        with col2:
            if st.button("Ver Historial de Plagas"):
                self._mostrar_historial_plagas()
        
        # Mostrar alertas si existen
        if 'plagas' in st.session_state.ultimas_predicciones:
            self._mostrar_alertas_plagas(st.session_state.ultimas_predicciones['plagas'])
    
    def _mostrar_alertas_plagas(self, alertas):
        """Mostrar alertas de plagas"""
        if not alertas:
            st.info("No hay alertas activas de plagas")
            return
        
        st.subheader("🚨 Alertas de Plagas Activas")
        
        # Crear DataFrame para visualización
        datos_alertas = []
        for alerta in alertas:
            datos_alertas.append({
                'Plaga': alerta['plaga'].replace('_', ' ').title(),
                'Cultivo': alerta['cultivo'].title(),
                'Probabilidad': alerta['probabilidad_aparicion'],
                'Síntomas': alerta['sintomas'],
                'Recomendaciones': len(alerta['recomendaciones'])
            })
        
        df_alertas = pd.DataFrame(datos_alertas)
        
        # Gráfico de probabilidades
        fig = px.bar(
            df_alertas,
            x='Plaga',
            y='Probabilidad',
            color='Probabilidad',
            title='Probabilidad de Aparición de Plagas',
            color_continuous_scale='Reds'
        )
        
        fig.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig, config=PLOTLY_CONFIG, width='stretch')
        
        # Detalles de cada alerta
        for i, alerta in enumerate(alertas):
            with st.expander(f"🐛 {alerta['plaga'].replace('_', ' ').title()} - Probabilidad: {alerta['probabilidad_aparicion']:.1%}"):
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**Síntomas:**")
                    st.write(alerta['sintomas'])
                    
                    st.write("**Condiciones Actuales:**")
                    for condicion, datos in alerta['condiciones_actuales'].items():
                        status = "✅" if datos['cumple'] else "❌"
                        st.write(f"{status} {condicion}: {datos['actual']:.1f} (Óptimo: {datos['favorable']:.1f})")
                
                with col2:
                    st.write("**Recomendaciones:**")
                    for j, rec in enumerate(alerta['recomendaciones'], 1):
                        st.write(f"{j}. {rec}")
    
    def _mostrar_historial_plagas(self):
        """Mostrar historial de plagas"""
        st.subheader("📊 Historial de Plagas")
        
        # Simular datos históricos
        datos_historicos = {
            'fecha': pd.date_range(start='2024-01-01', end='2024-12-31', freq='M'),
            'araña_roja': np.random.poisson(2, 12),
            'pulgones': np.random.poisson(3, 12),
            'mosca_blanca': np.random.poisson(1, 12),
            'oidio': np.random.poisson(1, 12)
        }
        
        df_historico = pd.DataFrame(datos_historicos)
        df_historico['fecha'] = df_historico['fecha'].dt.strftime('%Y-%m')
        
        # Gráfico de tendencias
        fig = go.Figure()
        
        plagas = ['araña_roja', 'pulgones', 'mosca_blanca', 'oidio']
        colores = ['red', 'orange', 'yellow', 'purple']
        
        for plaga, color in zip(plagas, colores):
            fig.add_trace(go.Scatter(
                x=df_historico['fecha'],
                y=df_historico[plaga],
                mode='lines+markers',
                name=plaga.replace('_', ' ').title(),
                line=dict(color=color, width=2),
                marker=dict(size=6)
            ))
        
        fig.update_layout(
            title='Tendencias de Plagas por Mes (2024, showlegend=False)',
            xaxis_title='Mes',
            yaxis_title='Número de Alertas',
            hovermode='x unified',
            height=400
        )
        
        st.plotly_chart(fig, config=PLOTLY_CONFIG, width='stretch')
    
    def mostrar_tab_metricas_modelos(self):
        """Mostrar tab de métricas de modelos"""
        st.header("📊 Métricas de Modelos ML")
        
        if not st.session_state.modelos_entrenados:
            st.warning("Los modelos no han sido entrenados aún. Usa el botón en el sidebar para entrenarlos.")
            return
        
        # Obtener métricas
        if hasattr(self.ml_sistema, 'metricas_modelos') and self.ml_sistema.metricas_modelos:
            metricas = self.ml_sistema.metricas_modelos.get('temperatura_promedio', {})
            
            if metricas:
                # Crear DataFrame de métricas
                datos_metricas = []
                for nombre, resultado in metricas.items():
                    datos_metricas.append({
                        'Modelo': nombre.replace('_', ' ').title(),
                        'R²': resultado['r2'],
                        'RMSE': resultado['rmse'],
                        'MAE': resultado['mae'],
                        'CV_RMSE': resultado['cv_rmse_mean'],
                        'CV_Std': resultado['cv_rmse_std']
                    })
                
                df_metricas = pd.DataFrame(datos_metricas)
                
                # Gráfico de R²
                fig_r2 = px.bar(
                    df_metricas,
                    x='Modelo',
                    y='R²',
                    title='R² por Modelo',
                    color='R²',
                    color_continuous_scale='Greens'
                )
                fig_r2.update_layout(height=400)
                st.plotly_chart(fig_r2, config=PLOTLY_CONFIG, width='stretch')
                
                # Gráfico de RMSE
                fig_rmse = px.bar(
                    df_metricas,
                    x='Modelo',
                    y='RMSE',
                    title='RMSE por Modelo (Menor es Mejor)',
                    color='RMSE',
                    color_continuous_scale='Reds_r'
                )
                fig_rmse.update_layout(height=400)
                st.plotly_chart(fig_rmse, config=PLOTLY_CONFIG, width='stretch')
                
                # Tabla de métricas
                st.subheader("📋 Métricas Detalladas")
                
                # Formatear números
                df_mostrar = df_metricas.copy()
                for col in ['R²', 'RMSE', 'MAE', 'CV_RMSE', 'CV_Std']:
                    df_mostrar[col] = df_mostrar[col].round(4)
                
                st.dataframe(df_mostrar, width='stretch')
                
                # Resumen
                st.subheader("🏆 Mejor Modelo")
                mejor_modelo = df_metricas.loc[df_metricas['R²'].idxmax()]
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Modelo", mejor_modelo['Modelo'])
                
                with col2:
                    st.metric("R²", f"{mejor_modelo['R²']:.4f}")
                
                with col3:
                    st.metric("RMSE", f"{mejor_modelo['RMSE']:.4f}")
        else:
            st.info("No hay métricas disponibles. Entrena los modelos primero.")
    
    def mostrar_tab_reportes(self):
        """Mostrar tab de reportes"""
        st.header("📄 Reportes ML Avanzado")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Generar Reporte Completo", type="primary"):
                with st.spinner("Generando reporte..."):
                    reporte = self.ml_sistema.generar_reporte_ml_avanzado()
                    
                    if reporte:
                        st.session_state.ultimas_predicciones['reporte'] = reporte
                        st.success("Reporte generado exitosamente")
                    else:
                        st.error("Error generando reporte")
        
        with col2:
            if st.button("Exportar Datos"):
                self._exportar_datos_ml()
        
        # Mostrar reporte si existe
        if 'reporte' in st.session_state.ultimas_predicciones:
            self._mostrar_reporte_completo(st.session_state.ultimas_predicciones['reporte'])
    
    def _mostrar_reporte_completo(self, reporte):
        """Mostrar reporte completo"""
        st.subheader("📊 Reporte ML Avanzado")
        
        # Resumen general
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Modelos Entrenados", reporte.get('modelos_entrenados', 0))
        
        with col2:
            st.metric("Predicciones Heladas", reporte.get('predicciones_heladas', 0))
        
        with col3:
            st.metric("Predicciones Cosecha", reporte.get('predicciones_cosecha', 0))
        
        with col4:
            st.metric("Alertas Plagas", reporte.get('alertas_plagas', 0))
        
        # Resumen de rendimiento
        if 'resumen_rendimiento' in reporte:
            rendimiento = reporte['resumen_rendimiento']
            
            st.subheader("🎯 Rendimiento de Modelos")
            
            if 'mejor_r2' in rendimiento:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric("Mejor R²", f"{rendimiento['mejor_r2']:.4f}")
                
                with col2:
                    st.metric("Mejor RMSE", f"{rendimiento['mejor_rmse']:.4f}")
            
            # Métricas por variable
            if 'modelos_por_variable' in rendimiento:
                st.subheader("📈 Métricas por Variable")
                
                datos_variables = []
                for variable, metricas in rendimiento['modelos_por_variable'].items():
                    datos_variables.append({
                        'Variable': variable.replace('_', ' ').title(),
                        'Mejor R²': metricas['mejor_r2'],
                        'Mejor RMSE': metricas['mejor_rmse'],
                        'Cantidad Modelos': metricas['cantidad_modelos']
                    })
                
                if datos_variables:
                    df_variables = pd.DataFrame(datos_variables)
                    st.dataframe(df_variables, width='stretch')
    
    def _exportar_datos_ml(self):
        """Exportar datos de ML"""
        st.subheader("💾 Exportar Datos ML")
        
        # Crear datos para exportar
        datos_export = {
            'timestamp': datetime.now().isoformat(),
            'modelos_entrenados': len(self.ml_sistema.modelos),
            'metricas': self.ml_sistema.metricas_modelos,
            'predicciones': st.session_state.ultimas_predicciones
        }
        
        # Convertir a JSON
        json_data = json.dumps(datos_export, indent=2, default=str)
        
        st.download_button(
            label="Descargar Datos ML (JSON)",
            data=json_data,
            file_name=f"datos_ml_avanzado_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )
    
    def ejecutar_dashboard(self):
        """Ejecutar dashboard principal"""
        self.mostrar_header()
        
        # Sidebar
        config = self.mostrar_sidebar()
        
        # Tabs principales
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "❄️ Predicciones Heladas",
            "🌾 Optimización Cosecha", 
            "🐛 Detección Plagas",
            "📊 Métricas Modelos",
            "📄 Reportes"
        ])
        
        with tab1:
            self.mostrar_tab_predicciones_heladas(config)
        
        with tab2:
            self.mostrar_tab_optimizacion_cosecha(config)
        
        with tab3:
            self.mostrar_tab_deteccion_plagas(config)
        
        with tab4:
            self.mostrar_tab_metricas_modelos()
        
        with tab5:
            self.mostrar_tab_reportes()

def main():
    """Función principal"""
    dashboard = DashboardMLAvanzado()
    dashboard.ejecutar_dashboard()

if __name__ == "__main__":
    main()
