#!/usr/bin/env python3
"""
Dashboard Principal Integrado METGO 3D
Sistema unificado que combina todos los dashboards y funcionalidades
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import sqlite3
import json
import subprocess
import sys
import os
import sys
from pathlib import Path

_DASH = Path(__file__).resolve().parent
if str(_DASH) not in sys.path:
    sys.path.insert(0, str(_DASH))

from metgo_dashboard_init import page_config_and_theme

st, PLOTLY_CONFIG, plotly_layout = page_config_and_theme(
    "Dashboard Principal Integrado",
    "Hub METGO 3D · lanzador de módulos",
    module="unificado",
    page_icon="🌾",
)

class DashboardPrincipalIntegrado:
    def __init__(self):
        self.db_path = "datos_meteorologicos.db"
        self.estaciones = ['quillota_centro', 'la_cruz', 'nogueira', 'colliguay', 'hijuelas', 'calera']
        
        # Configuración de dashboards disponibles
        self.dashboards = {
            "meteorologico": {
                "nombre": "Dashboard Meteorológico",
                "archivo": "dashboard_meteorologico_final.py",
                "puerto": 8502,
                "descripcion": "Datos meteorológicos en tiempo real con pronósticos de 14 días"
            },
            "agricola": {
                "nombre": "Dashboard Agrícola",
                "archivo": "dashboard_agricola_avanzado.py",
                "puerto": 8501,
                "descripcion": "Recomendaciones agrícolas y análisis de cultivos"
            },
            "recomendaciones": {
                "nombre": "Dashboard de Recomendaciones",
                "archivo": "dashboard_integrado_recomendaciones_metgo.py",
                "puerto": 8510,
                "descripcion": "Recomendaciones integradas de riego, plagas y heladas"
            },
            "alertas": {
                "nombre": "Sistema de Alertas",
                "archivo": "sistema_alertas_visuales_integrado_metgo.py",
                "puerto": 8511,
                "descripcion": "Alertas visuales y recomendaciones de emergencia"
            }
        }
    
    def obtener_datos_actuales(self):
        """Obtener datos meteorológicos actuales de la última hora"""
        try:
            conn = sqlite3.connect(self.db_path)
            query = '''
                SELECT estacion, fecha, temperatura, humedad, presion, precipitacion,
                       velocidad_viento, direccion_viento, nubosidad, indice_uv
                FROM datos_meteorologicos
                WHERE fecha >= datetime('now', '-24 hours')
                ORDER BY fecha DESC
            '''
            df = pd.read_sql_query(query, conn)
            conn.close()
            
            if not df.empty:
                df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')
            
            return df
        except Exception as e:
            return pd.DataFrame()
    
    def analizar_estado_general(self, datos):
        """Analizar el estado general del sistema con información específica."""
        if datos.empty:
            return {
                "estado": "sin_datos",
                "mensaje": "No hay datos disponibles",
                "periodo": "Sin datos",
                "estaciones": [],
                "metricas": {},
                "alertas": [],
                "acciones": [],
                "riesgo_agronomico": {"puntaje": 0, "nivel": "sin_datos", "drivers": []},
            }

        fecha_min = datos['fecha'].min()
        fecha_max = datos['fecha'].max()
        estaciones = datos['estacion'].dropna().unique().tolist() if 'estacion' in datos.columns else []

        temp_promedio = float(datos['temperatura'].mean())
        temp_max = float(datos['temperatura'].max())
        temp_min = float(datos['temperatura'].min())
        humedad_promedio = float(datos['humedad'].mean())
        viento_promedio = float(datos['velocidad_viento'].mean())
        viento_max = float(datos['velocidad_viento'].max())
        precipitacion_total = float(datos['precipitacion'].sum())
        presion_promedio = float(datos['presion'].mean())
        uv_promedio = float(datos['indice_uv'].mean()) if 'indice_uv' in datos.columns else None

        estado_puntaje = 100
        alertas = []
        acciones = []
        drivers = []

        # Riesgo de heladas / estrés térmico
        if temp_min <= 2:
            estado_puntaje -= 30
            alertas.append("🚨 Heladas críticas detectadas")
            acciones.append("Activar protección antiheladas en sectores expuestos")
            drivers.append("mínima <= 2°C")
        elif temp_min <= 5:
            estado_puntaje -= 18
            alertas.append("⚠️ Riesgo de heladas")
            acciones.append("Preparar riego defensivo o cobertura térmica")
            drivers.append("mínima <= 5°C")

        if temp_max >= 35:
            estado_puntaje -= 20
            alertas.append("🌡️ Temperaturas altas")
            acciones.append("Revisar estrés térmico y ajustar riego/fertirriego")
            drivers.append("máxima >= 35°C")
        elif temp_promedio >= 30:
            estado_puntaje -= 10
            alertas.append("☀️ Estrés térmico probable")
            acciones.append("Priorizar riego de apoyo y ventilación si aplica")
            drivers.append("promedio >= 30°C")

        if viento_max >= 30:
            estado_puntaje -= 15
            alertas.append("💨 Vientos fuertes")
            acciones.append("Suspender pulverizaciones y revisar deriva")
            drivers.append("viento >= 30 km/h")

        if humedad_promedio >= 85:
            estado_puntaje -= 10
            alertas.append("💧 Humedad muy alta")
            acciones.append("Monitorear riesgo fungoso y ventilación del cultivo")
            drivers.append("humedad >= 85%")
        elif humedad_promedio <= 30:
            estado_puntaje -= 10
            alertas.append("🏜️ Humedad muy baja")
            acciones.append("Aumentar vigilancia de estrés hídrico")
            drivers.append("humedad <= 30%")

        if precipitacion_total > 0 and 15 <= temp_promedio <= 25 and humedad_promedio >= 80:
            estado_puntaje -= 12
            alertas.append("🦠 Riesgo elevado de enfermedades fúngicas")
            acciones.append("Revisar hoja mojada y aplicar manejo preventivo si corresponde")
            drivers.append("lluvia + humedad alta + temperatura templada")

        if uv_promedio is not None and uv_promedio >= 9:
            estado_puntaje -= 6
            alertas.append("🟣 Radiación UV muy alta")
            acciones.append("Evaluar protección de personal y tejidos expuestos")
            drivers.append("UV >= 9")

        if viento_promedio >= 22 and humedad_promedio <= 40:
            estado_puntaje -= 8
            alertas.append("🌬️ Alta evapotranspiración probable")
            acciones.append("Recalcular ventana de riego y evaporación")
            drivers.append("viento alto + humedad baja")

        riesgo = max(0, 100 - estado_puntaje)
        if riesgo >= 70:
            nivel_riesgo = "critico"
        elif riesgo >= 45:
            nivel_riesgo = "alto"
        elif riesgo >= 20:
            nivel_riesgo = "moderado"
        else:
            nivel_riesgo = "bajo"

        if not alertas:
            acciones.append("Mantener monitoreo y revisar próxima actualización")

        return {
            "estado": "normal" if estado_puntaje >= 80 else ("advertencia" if estado_puntaje >= 60 else "critico"),
            "puntaje": max(0, estado_puntaje),
            "periodo": f"Últimas 24h ({fecha_min.strftime('%H:%M')} - {fecha_max.strftime('%H:%M')})",
            "estaciones": estaciones,
            "fecha_actualizacion": fecha_max,
            "metricas": {
                "temperatura_promedio": temp_promedio,
                "temperatura_max": temp_max,
                "temperatura_min": temp_min,
                "humedad_promedio": humedad_promedio,
                "viento_promedio": viento_promedio,
                "viento_max": viento_max,
                "precipitacion_total": precipitacion_total,
                "presion_promedio": presion_promedio,
                "uv_promedio": uv_promedio,
                "estaciones_activas": len(estaciones),
            },
            "alertas": alertas,
            "acciones": acciones,
            "riesgo_agronomico": {
                "puntaje": riesgo,
                "nivel": nivel_riesgo,
                "drivers": drivers,
            },
        }

    def crear_grafico_estado_general(self, estado):
        """Crear gráfico ejecutivo del estado general del sistema."""
        metricas = estado.get('metricas', {})
        riesgo = estado.get('riesgo_agronomico', {})
        nivel = riesgo.get('nivel', 'bajo')
        color_riesgo = {
            'bajo': '#2ca25f',
            'moderado': '#fdae6b',
            'alto': '#fd8d3c',
            'critico': '#de2d26',
            'sin_datos': '#9e9e9e',
        }.get(nivel, '#2ca25f')

        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Temperatura', 'Humedad', 'Viento', 'Riesgo Agronómico'),
            specs=[[{"type": "indicator"}, {"type": "indicator"}],
                   [{"type": "indicator"}, {"type": "indicator"}]]
        )

        fig.add_trace(go.Indicator(
            mode="gauge+number+delta",
            value=metricas.get('temperatura_promedio', 0),
            number={"suffix": " °C", "font": {"size": 26}},
            title={'text': "Temperatura media"},
            delta={'reference': 25, 'increasing': {'color': '#d62728'}, 'decreasing': {'color': '#2ca25f'}},
            gauge={
                'axis': {'range': [0, 45]},
                'bar': {'color': '#1f77b4'},
                'bgcolor': 'white',
                'borderwidth': 1,
                'bordercolor': '#d9e2ec',
                'steps': [
                    {'range': [0, 10], 'color': '#dbe9f6'},
                    {'range': [10, 22], 'color': '#d9f0d3'},
                    {'range': [22, 30], 'color': '#fff2cc'},
                    {'range': [30, 45], 'color': '#f4cccc'}
                ],
                'threshold': {'line': {'color': '#d62728', 'width': 4}, 'thickness': 0.75, 'value': metricas.get('temperatura_max', 0)}
            }
        ), row=1, col=1)

        fig.add_trace(go.Indicator(
            mode="gauge+number",
            value=metricas.get('humedad_promedio', 0),
            number={"suffix": "%", "font": {"size": 26}},
            title={'text': "Humedad media"},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': '#2ca25f'},
                'bgcolor': 'white',
                'borderwidth': 1,
                'bordercolor': '#d9e2ec',
                'steps': [
                    {'range': [0, 30], 'color': '#f4cccc'},
                    {'range': [30, 55], 'color': '#fff2cc'},
                    {'range': [55, 80], 'color': '#d9f0d3'},
                    {'range': [80, 100], 'color': '#dbe9f6'}
                ]
            }
        ), row=1, col=2)

        fig.add_trace(go.Indicator(
            mode="gauge+number",
            value=metricas.get('viento_promedio', 0),
            number={"suffix": " km/h", "font": {"size": 26}},
            title={'text': "Viento medio"},
            gauge={
                'axis': {'range': [0, 50]},
                'bar': {'color': '#ff7f0e'},
                'bgcolor': 'white',
                'borderwidth': 1,
                'bordercolor': '#d9e2ec',
                'steps': [
                    {'range': [0, 10], 'color': '#d9f0d3'},
                    {'range': [10, 20], 'color': '#fff2cc'},
                    {'range': [20, 35], 'color': '#fdd49e'},
                    {'range': [35, 50], 'color': '#f4cccc'}
                ]
            }
        ), row=2, col=1)

        fig.add_trace(go.Indicator(
            mode="gauge+number",
            value=riesgo.get('puntaje', 0),
            number={"suffix": "/100", "font": {"size": 26}},
            title={'text': f"Riesgo {nivel.replace('_', ' ').title()}"},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': color_riesgo},
                'bgcolor': 'white',
                'borderwidth': 1,
                'bordercolor': '#d9e2ec',
                'steps': [
                    {'range': [0, 20], 'color': '#d9f0d3'},
                    {'range': [20, 45], 'color': '#fff2cc'},
                    {'range': [45, 70], 'color': '#fdd49e'},
                    {'range': [70, 100], 'color': '#f4cccc'}
                ]
            }
        ), row=2, col=2)

        fig.update_layout(
            height=620,
            title_text="Estado general del sistema METGO 3D",
            showlegend=False,
            template="plotly_white",
            paper_bgcolor="#ffffff",
            plot_bgcolor="#ffffff",
            margin=dict(l=20, r=20, t=70, b=20, showlegend=False),
            font=dict(family="Inter, Segoe UI, Arial, sans-serif", size=13),
        )
        return fig

    def crear_grafico_tendencias_agricolas(self, datos):
        """Tendencias operativas para agricultura con foco en decisión."""
        if datos.empty:
            return None

        df = datos.copy()
        if 'fecha' in df.columns:
            df = df.sort_values('fecha')
        for col in ['temperatura', 'humedad', 'precipitacion', 'velocidad_viento']:
            if col not in df.columns:
                df[col] = np.nan

        if 'fecha' in df.columns:
            df['hora'] = pd.to_datetime(df['fecha'], errors='coerce').dt.floor('H')
        else:
            df['hora'] = pd.RangeIndex(len(df))

        agg = df.groupby('hora', dropna=False).agg(
            temperatura=('temperatura', 'mean'),
            humedad=('humedad', 'mean'),
            precipitacion=('precipitacion', 'sum'),
            viento=('velocidad_viento', 'mean')
        ).reset_index().tail(48)

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=agg['hora'], y=agg['temperatura'],
            name='Temperatura', mode='lines+markers',
            line=dict(color='#1f77b4', width=3),
            marker=dict(size=6)
        ))
        fig.add_trace(go.Scatter(
            x=agg['hora'], y=agg['humedad'],
            name='Humedad', mode='lines+markers',
            yaxis='y2',
            line=dict(color='#2ca25f', width=3, dash='dot'),
            marker=dict(size=6)
        ))
        fig.add_trace(go.Bar(
            x=agg['hora'], y=agg['precipitacion'],
            name='Precipitación',
            marker_color='rgba(31, 119, 180, 0.25)',
            opacity=0.6
        ))
        fig.update_layout(
            template='plotly_white',
            title='Tendencias agrícolas de corto plazo',
            hovermode='x unified',
            height=420,
            margin=dict(l=30, r=30, t=60, b=35, showlegend=False, showlegend=False),
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
            xaxis=dict(title='Hora', showgrid=False),
            yaxis=dict(title='Precipitación (mm)', showgrid=False),
            yaxis2=dict(title='Temperatura / Humedad', overlaying='y', side='right', showgrid=False, range=[0, 100]),
            font=dict(family='Inter, Segoe UI, Arial, sans-serif', size=12),
        )
        return fig

    def crear_grafico_riesgo_agronomico(self, datos):
        """Mapa innovador de riesgo agronómico para detección temprana."""
        if datos.empty:
            return None

        df = datos.copy()
        for col in ['temperatura', 'humedad', 'precipitacion', 'velocidad_viento']:
            if col not in df.columns:
                df[col] = np.nan

        df['riesgo'] = 0.0
        df.loc[df['temperatura'] <= 5, 'riesgo'] += 35
        df.loc[df['temperatura'] >= 35, 'riesgo'] += 25
        df.loc[df['humedad'] <= 30, 'riesgo'] += 18
        df.loc[df['humedad'] >= 85, 'riesgo'] += 10
        df.loc[df['velocidad_viento'] >= 25, 'riesgo'] += 15
        df.loc[df['precipitacion'] > 0, 'riesgo'] += 4
        df['riesgo'] = df['riesgo'].clip(0, 100)

        if 'fecha' in df.columns:
            df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')
        fig = px.scatter(
            df,
            x='temperatura', y='humedad',
            color='riesgo', size=np.maximum(df['precipitacion'].fillna(0) + 1, 1),
            size_max=18,
            color_continuous_scale=['#2ca25f', '#fdae6b', '#fd8d3c', '#de2d26'],
            hover_data=[c for c in ['estacion', 'fecha', 'velocidad_viento', 'precipitacion'] if c in df.columns],
            title='Mapa de riesgo agronómico: temperatura vs humedad',
        )
        fig.update_layout(
            template='plotly_white',
            height=460,
            margin=dict(l=30, r=30, t=70, b=35, showlegend=False, showlegend=False),
            xaxis=dict(title='Temperatura (°C)', zeroline=False),
            yaxis=dict(title='Humedad relativa (%)', zeroline=False),
            coloraxis_colorbar=dict(title='Riesgo'),
            font=dict(family='Inter, Segoe UI, Arial, sans-serif', size=12),
        )
        fig.add_vline(x=25, line_width=1, line_dash='dash', line_color='#6c757d')
        fig.add_hline(y=70, line_width=1, line_dash='dash', line_color='#6c757d')
        fig.add_annotation(x=25.5, y=72, text='Zona fungosa / humedad alta', showarrow=False, font=dict(size=11, color='#495057'))
        fig.add_annotation(x=5.5, y=35, text='Zona heladas', showarrow=False, font=dict(size=11, color='#495057'))
        fig.add_annotation(x=34.5, y=25, text='Estrés térmico / hídrico', showarrow=False, font=dict(size=11, color='#495057'))
        return fig

    def _clasificar_alerta(self, alerta: str) -> tuple[str, int, str, str]:
        """Clasifica una alerta por prioridad para operación agrícola."""
        a = alerta.lower()
        if any(k in a for k in ["helada", "críticas", "crítico", "riesgo de heladas"]):
            return ("critico", 100, "🚨", "Heladas / daño inmediato")
        if any(k in a for k in ["temperaturas altas", "estrés térmico", "viento fuerte", "vientos fuertes"]):
            return ("alto", 85, "⚠️", "Estrés térmico / manejo")
        if any(k in a for k in ["fúng", "humedad muy alta", "alta evapotranspiración", "uv muy alta", "humedad muy baja"]):
            return ("moderado", 65, "🟡", "Riesgo agronómico / seguimiento")
        return ("bajo", 30, "✅", "Condición informativa")

    def _ordenar_alertas_operativas(self, alertas):
        orden = {"critico": 0, "alto": 1, "moderado": 2, "bajo": 3}
        salida = []
        for alerta in alertas or []:
            nivel, score, icono, etiqueta = self._clasificar_alerta(alerta)
            salida.append({
                "texto": alerta,
                "nivel": nivel,
                "score": score,
                "icono": icono,
                "etiqueta": etiqueta,
            })
        return sorted(salida, key=lambda x: (orden.get(x["nivel"], 9), -x["score"], x["texto"]))

    def _clasificar_recomendacion(self, rec: dict) -> tuple[str, str, str]:
        """Clasifica una recomendación agrícola por prioridad."""
        texto = f"{rec.get('accion', '')} {rec.get('motivo', '')}".lower()
        if any(k in texto for k in ['antihelada', 'helada', 'hielo', 'protección antihielo']):
            return ('critico', '🚨', 'Acción inmediata')
        if any(k in texto for k in ['suspender riego', 'pulverización', 'deriva', 'estrés térmico']):
            return ('alto', '⚠️', 'Prioridad alta')
        if any(k in texto for k in ['riego moderado', 'monitoreo', 'ventilación', 'seguimiento']):
            return ('moderado', '🟡', 'Vigilar')
        return ('bajo', '✅', 'Informativo')

    def mostrar_recomendaciones_agricolas(self, estacion_id: str, foco: str = ''):
        """Muestra recomendaciones agrícolas por cultivo con enfoque ejecutivo."""
        try:
            from api_rest import services
            recomendaciones = services.recomendaciones_agricolas(estacion_id)
        except Exception as e:
            st.warning(f"No fue posible cargar recomendaciones agrícolas: {e}")
            return

        st.markdown('### 🌿 Recomendaciones agrícolas por cultivo')
        if foco:
            st.caption(f"Estación foco: {foco}")

        if not recomendaciones:
            st.info('No hay recomendaciones disponibles para esta estación.')
            return

        # ordenar por prioridad
        orden = {'critico': 0, 'alto': 1, 'moderado': 2, 'bajo': 3}
        tarjetas = []
        for rec in recomendaciones:
            nivel, icono, etiqueta = self._clasificar_recomendacion(rec)
            tarjetas.append({**rec, 'nivel': nivel, 'icono': icono, 'etiqueta': etiqueta})
        tarjetas = sorted(tarjetas, key=lambda x: (orden.get(x['nivel'], 9), x.get('cultivo','')))

        cols = st.columns(3)
        for i, rec in enumerate(tarjetas[:6]):
            with cols[i % 3]:
                color = {'critico':'#b42318', 'alto':'#d97706', 'moderado':'#b08900', 'bajo':'#2e7d32'}.get(rec['nivel'], '#334155')
                st.markdown(
                    f"<div style='border:1px solid #e5e7eb;border-left:6px solid {color};border-radius:14px;padding:1rem;background:linear-gradient(180deg,#ffffff,#f8fafc);min-height:160px;'>"
                    f"<div style='font-size:0.8rem;font-weight:700;color:{color};margin-bottom:0.35rem;'>{rec['icono']} {rec['etiqueta']}</div>"
                    f"<div style='font-size:1.05rem;font-weight:700;color:#111827;margin-bottom:0.35rem;'>{rec.get('cultivo','General')}</div>"
                    f"<div style='font-size:0.95rem;color:#111827;margin-bottom:0.25rem;'><strong>{rec.get('accion','')}</strong></div>"
                    f"<div style='font-size:0.85rem;color:#64748b;'>{rec.get('motivo','')}</div>"
                    f"</div>",
                    unsafe_allow_html=True,
                )

        with st.expander('🔎 Ver recomendación completa'):
            for rec in tarjetas:
                st.markdown(f"- **[{rec['nivel'].upper()}]** {rec.get('cultivo','General')}: {rec.get('accion','')} — {rec.get('motivo','')}")

    def mostrar_horizontes_operativos(self, estado, estacion_id: str):
        """Muestra recomendaciones por horizonte temporal: ahora, 6h y 24h."""
        riesgo = estado.get('riesgo_agronomico', {})
        nivel = riesgo.get('nivel', 'bajo')
        puntaje = float(riesgo.get('puntaje', 0))
        alertas = estado.get('alertas', [])
        acciones = estado.get('acciones', [])

        if puntaje >= 80 or nivel == 'critico':
            ahora = ('critico', '🚨 Ahora', 'Intervenir de inmediato', alertas[:3] or ['Activar protocolo de emergencia'])
            h6 = ('alto', '⚠️ Próx. 6h', 'Mantener vigilancia intensiva', acciones[:3] or ['Revisar umbrales y personal'])
            h24 = ('moderado', '🟡 Próx. 24h', 'Planificar ajuste operativo', ['Revisar riego, protección y logística'])
        elif puntaje >= 45 or nivel == 'alto':
            ahora = ('alto', '⚠️ Ahora', 'Corregir condición crítica', alertas[:2] or ['Aplicar corrección operativa'])
            h6 = ('moderado', '🟡 Próx. 6h', 'Monitorear evolución', acciones[:2] or ['Revisar tendencia'])
            h24 = ('bajo', '✅ Próx. 24h', 'Planificar ejecución', ['Reprogramar labores sensibles'])
        else:
            ahora = ('bajo', '✅ Ahora', 'Operación normal', ['Seguimiento rutinario'])
            h6 = ('bajo', '✅ Próx. 6h', 'Seguimiento normal', ['Revisión periódica'])
            h24 = ('moderado', '🟡 Próx. 24h', 'Ajuste preventivo', ['Preparar plan si cambian las condiciones'])

        st.markdown('### ⏱️ Horizonte operativo')
        cols = st.columns(3)
        cards = [ahora, h6, h24]
        for col, card in zip(cols, cards):
            nivel_card, titulo, subtitulo, items = card
            color = {'critico':'#b42318', 'alto':'#d97706', 'moderado':'#b08900', 'bajo':'#2e7d32'}.get(nivel_card, '#334155')
            with col:
                st.markdown(
                    f"<div style='border:1px solid #e5e7eb;border-left:6px solid {color};border-radius:14px;padding:1rem;background:#fff;min-height:210px;'>"
                    f"<div style='font-size:0.8rem;font-weight:700;color:{color};margin-bottom:0.35rem;'>{titulo}</div>"
                    f"<div style='font-size:1rem;font-weight:700;color:#111827;margin-bottom:0.35rem;'>{subtitulo}</div>"
                    f"<ul style='margin:0;padding-left:1.1rem;color:#334155;'>" + ''.join(f'<li>{x}</li>' for x in items[:4]) + "</ul>"
                    f"</div>",
                    unsafe_allow_html=True,
                )

    def _clasificar_recomendacion(self, rec: dict) -> tuple[str, str, str]:
        """Clasifica una recomendación agrícola por prioridad."""
        texto = f"{rec.get('accion', '')} {rec.get('motivo', '')}".lower()
        if any(k in texto for k in ['antihelada', 'helada', 'hielo', 'protección antihielo']):
            return ('critico', '🚨', 'Acción inmediata')
        if any(k in texto for k in ['suspender riego', 'pulverización', 'deriva', 'estrés térmico']):
            return ('alto', '⚠️', 'Prioridad alta')
        if any(k in texto for k in ['riego moderado', 'monitoreo', 'ventilación', 'seguimiento']):
            return ('moderado', '🟡', 'Vigilar')
        return ('bajo', '✅', 'Informativo')

    def mostrar_recomendaciones_agricolas(self, estacion_id: str, foco: str = ''):
        """Muestra recomendaciones agrícolas por cultivo con enfoque ejecutivo."""
        alertas = estado.get('alertas', [])
        acciones = estado.get('acciones', [])
        riesgo = estado.get('riesgo_agronomico', {})
        nivel = riesgo.get('nivel', 'bajo')
        alertas_ordenadas = self._ordenar_alertas_operativas(alertas)

        encabezado = {
            'critico': '🚨 Estado crítico - acción inmediata',
            'alto': '⚠️ Riesgo alto - intervención recomendada',
            'moderado': '🟡 Riesgo moderado - monitoreo reforzado',
            'bajo': '✅ Riesgo bajo - operación normal',
            'sin_datos': 'ℹ️ Sin datos suficientes',
        }.get(nivel, '✅ Riesgo bajo - operación normal')

        st.markdown('### 🎯 Panel ejecutivo de alertas agrícolas')
        if nivel == 'critico':
            st.error(encabezado)
        elif nivel == 'alto':
            st.warning(encabezado)
        elif nivel == 'moderado':
            st.info(encabezado)
        else:
            st.success(encabezado)

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Riesgo agronómico", f"{riesgo.get('puntaje', 0):.0f}/100")
        c2.metric("Alertas activas", len(alertas))
        c3.metric("Acciones sugeridas", len(acciones))
        c4.metric("Ventana", "6 horas")

        if alertas_ordenadas:
            bandas = {"critico": [], "alto": [], "moderado": [], "bajo": []}
            for a in alertas_ordenadas:
                bandas[a["nivel"]].append(a)

            cols = st.columns(3)
            tarjetas = [
                ("critico", "🚨 Acción inmediata", "Daño potencial alto si no se interviene"),
                ("alto", "⚠️ Prioridad alta", "Requiere ajuste operativo hoy"),
                ("moderado", "🟡 Vigilar", "Conviene seguimiento reforzado"),
            ]
            for idx, (nivel_card, titulo, subtitulo) in enumerate(tarjetas):
                with cols[idx]:
                    st.markdown(f"**{titulo}**")
                    st.caption(subtitulo)
                    items = bandas[nivel_card]
                    if items:
                        for item in items[:4]:
                            st.markdown(
                                f"<div style='padding:0.6rem 0.75rem;border-radius:0.6rem;margin-bottom:0.5rem;"
                                f"border:1px solid #e6e9ef;background:#fff;'>"
                                f"<strong>{item['icono']} {item['texto']}</strong><br/>"
                                f"<span style='color:#667085;font-size:0.85rem;'>{item['etiqueta']}</span>"
                                f"</div>",
                                unsafe_allow_html=True,
                            )
                    else:
                        st.caption("Sin alertas en este nivel")

            with st.expander("🔎 Ver detalle completo de alertas"):
                for item in alertas_ordenadas:
                    st.markdown(f"- {item['icono']} **[{item['nivel'].upper()}]** {item['texto']}")
        else:
            st.info("No hay alertas activas en esta ventana operativa.")

        if acciones:
            st.markdown("**Acciones recomendadas**")
            for accion in acciones:
                st.markdown(f"- {accion}")

        drivers = riesgo.get('drivers', [])
        if drivers:
            with st.expander("📌 Qué disparó el riesgo"):
                for d in drivers:
                    st.write(f"- {d}")

    def ejecutar_dashboard(self, dashboard_id):
        """Ejecutar un dashboard específico"""
        dashboard = self.dashboards.get(dashboard_id)
        if not dashboard:
            st.error(f"Dashboard '{dashboard_id}' no encontrado")
            return
        
        try:
            # Verificar si el dashboard ya está ejecutándose
            try:
                import requests
                response = requests.get(f"http://localhost:{dashboard['puerto']}/_stcore/health", timeout=1)
                if response.status_code == 200:
                    st.info(f"✅ {dashboard['nombre']} ya está ejecutándose en http://localhost:{dashboard['puerto']}")
                    st.markdown(f"<a href='http://localhost:{dashboard['puerto']}' target='_blank'>Abrir {dashboard['nombre']}</a>", unsafe_allow_html=True)
                    return
            except:
                pass
            
            # Ejecutar el dashboard
            command = [sys.executable, "-m", "streamlit", "run", dashboard['archivo'], 
                      "--server.port", str(dashboard['puerto']), "--server.headless", "true"]
            
            process = subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            st.success(f"🚀 {dashboard['nombre']} iniciado en http://localhost:{dashboard['puerto']}")
            st.markdown(f"<a href='http://localhost:{dashboard['puerto']}' target='_blank'>Abrir {dashboard['nombre']}</a>", unsafe_allow_html=True)
            
        except Exception as e:
            st.error(f"❌ Error ejecutando {dashboard['nombre']}: {e}")
    
    def mostrar_menu_dashboards(self):
        """Mostrar menú de dashboards disponibles"""
        st.subheader("🎛️ Panel de Control de Dashboards")
        
        # Crear columnas para los botones de dashboard
        cols = st.columns(2)
        
        for i, (dashboard_id, dashboard) in enumerate(self.dashboards.items()):
            col = cols[i % 2]
            
            with col:
                st.markdown(f"### {dashboard['nombre']}")
                st.write(dashboard['descripcion'])
                
                if st.button(f"🚀 Ejecutar {dashboard['nombre']}", key=f"btn_{dashboard_id}"):
                    self.ejecutar_dashboard(dashboard_id)
                
                st.markdown(f"**Puerto:** {dashboard['puerto']}")
                st.markdown("---")

def main():
    """Función principal del dashboard"""
    
    # Título principal
    st.title("🌾 METGO 3D - Dashboard Principal Integrado")
    st.markdown("### Sistema Unificado de Gestión Meteorológica y Agrícola")
    
    # Inicializar dashboard
    dashboard = DashboardPrincipalIntegrado()
    
    # Sidebar con información del sistema
    with st.sidebar:
        st.header("ℹ️ Información del Sistema")
        st.write(f"**Versión:** METGO 3D v2.0")
        st.write(f"**Última actualización:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        st.write(f"**Base de datos:** {dashboard.db_path}")
        
        # Botón de actualización general
        if st.button("🔄 Actualizar Sistema"):
            st.rerun()
        
        st.markdown("---")
        
        # Enlaces rápidos
        st.header("🔗 Enlaces Rápidos")
        st.markdown("- [Dashboard Meteorológico](http://localhost:8502)")
        st.markdown("- [Dashboard Agrícola](http://localhost:8501)")
        st.markdown("- [Sistema de Autenticación](http://localhost:8500)")
        st.markdown("- [Dashboard Central](http://localhost:8509)")
    
    # Obtener datos actuales
    datos_actuales = dashboard.obtener_datos_actuales()
    
    if datos_actuales.empty:
        st.warning("⚠️ **No hay datos meteorológicos disponibles**")
        st.info("💡 **Recomendación:** Ejecuta el Dashboard Meteorológico para generar datos")
        
        # Mostrar solo el menú de dashboards
        dashboard.mostrar_menu_dashboards()
        return
    
    # Analizar estado general
    estado = dashboard.analizar_estado_general(datos_actuales)
    
    # Mostrar estado general
    st.subheader("📊 Estado General del Sistema")
    
    # Información específica del período y estaciones
    if estado.get('periodo') and estado.get('estaciones'):
        col_info1, col_info2, col_info3 = st.columns(3)
        
        with col_info1:
            st.info(f"📅 **Período:** {estado['periodo']}")
        
        with col_info2:
            estaciones_texto = ", ".join(estado['estaciones'][:3])  # Mostrar máximo 3 estaciones
            if len(estado['estaciones']) > 3:
                estaciones_texto += f" (+{len(estado['estaciones'])-3} más)"
            st.info(f"📍 **Estaciones:** {estaciones_texto}")
        
        with col_info3:
            if estado.get('fecha_actualizacion'):
                fecha_str = estado['fecha_actualizacion'].strftime('%H:%M:%S')
                st.info(f"🕐 **Última actualización:** {fecha_str}")
    
    estaciones_disponibles = sorted([e for e in datos_actuales['estacion'].dropna().unique().tolist()]) if 'estacion' in datos_actuales.columns else []
    estacion_foco = st.selectbox(
        "Estación foco para análisis agrícola",
        options=estaciones_disponibles or ["quillota"],
        index=0,
        help="Selecciona la estación para priorizar recomendaciones y gráficos.",
    )
    datos_foco = datos_actuales[datos_actuales['estacion'] == estacion_foco] if 'estacion' in datos_actuales.columns and estacion_foco in set(datos_actuales['estacion'].dropna()) else datos_actuales

    # Gráfico de estado general
    fig_estado = dashboard.crear_grafico_estado_general(estado)
    st.plotly_chart(fig_estado, config=PLOTLY_CONFIG, width='stretch')

    st.subheader("🌾 Inteligencia agrícola y alertas tempranas")
    col_a, col_b = st.columns([1, 1])
    with col_a:
        fig_tendencias = dashboard.crear_grafico_tendencias_agricolas(datos_foco)
        if fig_tendencias is not None:
            st.plotly_chart(fig_tendencias, config=PLOTLY_CONFIG, width='stretch')
    with col_b:
        fig_riesgo = dashboard.crear_grafico_riesgo_agronomico(datos_foco)
        if fig_riesgo is not None:
            st.plotly_chart(fig_riesgo, config=PLOTLY_CONFIG, width='stretch')

    # Panel de alertas
    st.caption("Cadencia operativa de alertas: actualización cada 6 horas por estación, con supresión de duplicados en la misma ventana.")
    dashboard.mostrar_panel_alertas(estado)

    dashboard.mostrar_recomendaciones_agricolas(estacion_foco, foco=estacion_foco)
    dashboard.mostrar_horizontes_operativos(estado, estacion_foco)

    with st.expander("💡 Interpretación operativa"):
        st.markdown("""
- La zona de riesgo cruza temperatura y humedad para anticipar heladas, hongos y estrés hídrico.
- El panel de tendencias ayuda a decidir ventanas de riego, ventilación y pulverización.
- Las alertas combinan umbrales simples con reglas de contexto para priorizar acciones agrícolas.
- La priorización separa alertas que requieren acción inmediata de las que solo requieren vigilancia.
- El horizonte operativo organiza qué hacer ahora, en 6 horas y en 24 horas.
""")

    # Métricas principales
    st.subheader("📈 Métricas Principales")
    metricas = estado.get('metricas', {})
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            "🌡️ Temperatura",
            f"{metricas.get('temperatura_promedio', 0):.1f}°C"
        )
    
    with col2:
        st.metric(
            "💧 Humedad",
            f"{metricas.get('humedad_promedio', 0):.1f}%"
        )
    
    with col3:
        st.metric(
            "💨 Viento",
            f"{metricas.get('viento_promedio', 0):.1f} km/h"
        )
    
    with col4:
        st.metric(
            "🌧️ Precipitación",
            f"{metricas.get('precipitacion_total', 0):.1f}mm"
        )
    
    with col5:
        st.metric(
            "📍 Estaciones",
            f"{metricas.get('estaciones_activas', 0)}/6"
        )
    
    # Menú de dashboards
    dashboard.mostrar_menu_dashboards()
    
    # Información adicional
    with st.expander("ℹ️ Información Técnica del Sistema"):
        st.write("**Arquitectura del Sistema:**")
        st.write("- Base de datos SQLite para almacenamiento")
        st.write("- APIs meteorológicas en tiempo real")
        st.write("- Dashboards Streamlit independientes")
        st.write("- Sistema de alertas integrado")
        st.write("- Recomendaciones agrícolas automatizadas")
        
        st.write("**Dashboards Disponibles:**")
        for dashboard_id, info in dashboard.dashboards.items():
            st.write(f"- **{info['nombre']}:** Puerto {info['puerto']}")
        
        st.write("**Última verificación de datos:**")
        if not datos_actuales.empty:
            ultima_fecha = datos_actuales['fecha'].max()
            st.write(f"- {ultima_fecha}")
        else:
            st.write("- No hay datos disponibles")

if __name__ == "__main__":
    main()
