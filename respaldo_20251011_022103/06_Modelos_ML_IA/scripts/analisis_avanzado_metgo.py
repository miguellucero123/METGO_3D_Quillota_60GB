#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
📊 ANÁLISIS AVANZADO PARA METGO 3D
Sistema Meteorológico Agrícola Quillota - Análisis Avanzado de Series Temporales
"""

import os
import sys
import time
import json
import numpy as np
import pandas as pd
import warnings
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from scipy.signal import find_peaks, periodogram
from scipy.fft import fft, fftfreq
from sklearn.cluster import KMeans, DBSCAN
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

# Configuración
warnings.filterwarnings('ignore')
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

class AnalisisAvanzadoMETGO:
    """Clase para análisis avanzado de series temporales meteorológicas"""
    
    def __init__(self):
        self.configuracion = {
            'directorio_datos': 'data/processed',
            'directorio_resultados': 'resultados/analisis_avanzado',
            'directorio_graficos': 'graficos/analisis_avanzado',
            'version': '2.0',
            'timestamp': datetime.now().isoformat()
        }
        
        # Crear directorios
        self._crear_directorios()
        
        # Variables meteorológicas
        self.variables_meteorologicas = [
            'temperatura', 'precipitacion', 'viento_velocidad', 'viento_direccion',
            'humedad', 'presion', 'radiacion_solar', 'punto_rocio'
        ]
        
        # Resultados del análisis
        self.resultados = {}
        self.graficos = {}
        self.estadisticas = {}
    
    def _crear_directorios(self):
        """Crear directorios necesarios"""
        try:
            for directorio in self.configuracion.values():
                if isinstance(directorio, str) and '/' in directorio:
                    Path(directorio).mkdir(parents=True, exist_ok=True)
        except Exception as e:
            print(f"Error creando directorios: {e}")
    
    def cargar_datos_meteorologicos(self, archivo: str = None) -> pd.DataFrame:
        """Cargar datos meteorológicos para análisis"""
        try:
            if archivo is None:
                archivo = f"{self.configuracion['directorio_datos']}/datos_meteorologicos_quillota.csv"
            
            if not Path(archivo).exists():
                print(f"Archivo no encontrado: {archivo}")
                return self._generar_datos_sinteticos()
            
            datos = pd.read_csv(archivo)
            datos['fecha'] = pd.to_datetime(datos['fecha'])
            datos.set_index('fecha', inplace=True)
            
            print(f"✅ Datos cargados: {len(datos)} registros")
            return datos
            
        except Exception as e:
            print(f"Error cargando datos: {e}")
            return self._generar_datos_sinteticos()
    
    def _generar_datos_sinteticos(self) -> pd.DataFrame:
        """Generar datos sintéticos para análisis"""
        try:
            print("🔄 Generando datos sintéticos...")
            
            # Generar fechas (2 años de datos)
            fechas = pd.date_range(
                start='2022-01-01',
                end='2024-01-01',
                freq='H'
            )
            
            # Generar datos sintéticos realistas
            np.random.seed(42)
            datos = pd.DataFrame(index=fechas)
            
            # Temperatura (patrón estacional + tendencia)
            tendencia = np.linspace(0, 2, len(fechas))  # Calentamiento global
            estacional = 10 * np.sin(2 * np.pi * fechas.dayofyear / 365)
            ruido = np.random.normal(0, 3, len(fechas))
            datos['temperatura'] = 15 + tendencia + estacional + ruido
            
            # Precipitación (eventos esporádicos)
            datos['precipitacion'] = np.random.exponential(0.5, len(fechas))
            datos['precipitacion'] = np.where(np.random.random(len(fechas)) > 0.9, datos['precipitacion'], 0)
            
            # Viento
            datos['viento_velocidad'] = np.random.gamma(2, 2, len(fechas))
            datos['viento_direccion'] = np.random.uniform(0, 360, len(fechas))
            
            # Humedad (inversamente relacionada con temperatura)
            datos['humedad'] = 80 - (datos['temperatura'] - 15) * 2 + np.random.normal(0, 5, len(fechas))
            datos['humedad'] = np.clip(datos['humedad'], 0, 100)
            
            # Presión
            datos['presion'] = 1013 + np.random.normal(0, 10, len(fechas))
            
            # Radiación solar
            datos['radiacion_solar'] = np.maximum(0, 800 * np.sin(np.pi * fechas.hour / 24) + np.random.normal(0, 50, len(fechas)))
            
            # Punto de rocío
            datos['punto_rocio'] = datos['temperatura'] - (100 - datos['humedad']) / 5
            
            print(f"✅ Datos sintéticos generados: {len(datos)} registros")
            return datos
            
        except Exception as e:
            print(f"Error generando datos sintéticos: {e}")
            return pd.DataFrame()
    
    def analisis_estacionalidad(self, datos: pd.DataFrame, variable: str) -> Dict:
        """Análisis de estacionalidad de una variable meteorológica"""
        try:
            print(f"📊 Analizando estacionalidad de {variable}...")
            
            if variable not in datos.columns:
                print(f"Variable {variable} no encontrada")
                return {}
            
            serie = datos[variable].dropna()
            
            # Análisis de estacionalidad
            resultado = {
                'variable': variable,
                'total_registros': len(serie),
                'estacionalidad': {}
            }
            
            # Estacionalidad mensual
            datos_mensuales = serie.groupby(serie.index.month).agg(['mean', 'std', 'min', 'max'])
            resultado['estacionalidad']['mensual'] = {
                'estadisticas': datos_mensuales.to_dict(),
                'mes_mas_calido': datos_mensuales['mean'].idxmax(),
                'mes_mas_frio': datos_mensuales['mean'].idxmin(),
                'variabilidad_mensual': datos_mensuales['std'].mean()
            }
            
            # Estacionalidad diaria
            datos_diarios = serie.groupby(serie.index.dayofyear).agg(['mean', 'std'])
            resultado['estacionalidad']['diaria'] = {
                'estadisticas': datos_diarios.to_dict(),
                'dia_pico': datos_diarios['mean'].idxmax(),
                'dia_minimo': datos_diarios['mean'].idxmin()
            }
            
            # Estacionalidad horaria
            datos_horarios = serie.groupby(serie.index.hour).agg(['mean', 'std'])
            resultado['estacionalidad']['horaria'] = {
                'estadisticas': datos_horarios.to_dict(),
                'hora_pico': datos_horarios['mean'].idxmax(),
                'hora_minima': datos_horarios['mean'].idxmin()
            }
            
            # Análisis de tendencia
            x = np.arange(len(serie))
            slope, intercept, r_value, p_value, std_err = stats.linregress(x, serie.values)
            resultado['tendencia'] = {
                'pendiente': slope,
                'intercepto': intercept,
                'r_cuadrado': r_value**2,
                'p_valor': p_value,
                'significancia': 'significativa' if p_value < 0.05 else 'no significativa'
            }
            
            self.resultados[f'estacionalidad_{variable}'] = resultado
            print(f"✅ Análisis de estacionalidad completado para {variable}")
            return resultado
            
        except Exception as e:
            print(f"Error analizando estacionalidad: {e}")
            return {}
    
    def analisis_frecuencias(self, datos: pd.DataFrame, variable: str) -> Dict:
        """Análisis de frecuencias y espectro de una variable"""
        try:
            print(f"📊 Analizando frecuencias de {variable}...")
            
            if variable not in datos.columns:
                print(f"Variable {variable} no encontrada")
                return {}
            
            serie = datos[variable].dropna()
            
            # Análisis de frecuencias
            resultado = {
                'variable': variable,
                'total_registros': len(serie),
                'frecuencias': {}
            }
            
            # Transformada de Fourier
            fft_resultado = fft(serie.values)
            frecuencias = fftfreq(len(serie), d=1)  # 1 hora entre muestras
            
            # Encontrar frecuencias dominantes
            magnitudes = np.abs(fft_resultado)
            frecuencias_dominantes = frecuencias[np.argsort(magnitudes)[-10:]]
            
            resultado['frecuencias']['dominantes'] = {
                'frecuencias': frecuencias_dominantes.tolist(),
                'magnitudes': magnitudes[np.argsort(magnitudes)[-10:]].tolist()
            }
            
            # Análisis de periodograma
            frecuencias_periodo, densidad_espectral = periodogram(serie.values, fs=1)
            
            # Encontrar picos en el periodograma
            picos, propiedades = find_peaks(densidad_espectral, height=np.mean(densidad_espectral))
            
            resultado['frecuencias']['periodograma'] = {
                'frecuencias_pico': frecuencias_periodo[picos].tolist(),
                'densidad_pico': densidad_espectral[picos].tolist(),
                'periodos_dominantes': (1 / frecuencias_periodo[picos]).tolist()
            }
            
            self.resultados[f'frecuencias_{variable}'] = resultado
            print(f"✅ Análisis de frecuencias completado para {variable}")
            return resultado
            
        except Exception as e:
            print(f"Error analizando frecuencias: {e}")
            return {}
    
    def analisis_correlaciones(self, datos: pd.DataFrame) -> Dict:
        """Análisis de correlaciones entre variables meteorológicas"""
        try:
            print("📊 Analizando correlaciones entre variables...")
            
            # Seleccionar variables numéricas
            variables_numericas = datos.select_dtypes(include=[np.number]).columns
            datos_numericos = datos[variables_numericas].dropna()
            
            # Matriz de correlación
            matriz_correlacion = datos_numericos.corr()
            
            # Análisis de correlaciones
            resultado = {
                'total_variables': len(variables_numericas),
                'matriz_correlacion': matriz_correlacion.to_dict(),
                'correlaciones_fuertes': [],
                'correlaciones_debiles': [],
                'correlaciones_negativas': []
            }
            
            # Identificar correlaciones fuertes (>0.7)
            for i in range(len(variables_numericas)):
                for j in range(i+1, len(variables_numericas)):
                    var1, var2 = variables_numericas[i], variables_numericas[j]
                    correlacion = matriz_correlacion.loc[var1, var2]
                    
                    if abs(correlacion) > 0.7:
                        resultado['correlaciones_fuertes'].append({
                            'variable1': var1,
                            'variable2': var2,
                            'correlacion': round(correlacion, 3)
                        })
                    elif abs(correlacion) < 0.3:
                        resultado['correlaciones_debiles'].append({
                            'variable1': var1,
                            'variable2': var2,
                            'correlacion': round(correlacion, 3)
                        })
                    
                    if correlacion < -0.5:
                        resultado['correlaciones_negativas'].append({
                            'variable1': var1,
                            'variable2': var2,
                            'correlacion': round(correlacion, 3)
                        })
            
            self.resultados['correlaciones'] = resultado
            print("✅ Análisis de correlaciones completado")
            return resultado
            
        except Exception as e:
            print(f"Error analizando correlaciones: {e}")
            return {}
    
    def analisis_clustering(self, datos: pd.DataFrame) -> Dict:
        """Análisis de clustering de patrones meteorológicos"""
        try:
            print("📊 Analizando clustering de patrones meteorológicos...")
            
            # Seleccionar variables numéricas
            variables_numericas = datos.select_dtypes(include=[np.number]).columns
            datos_numericos = datos[variables_numericas].dropna()
            
            # Normalizar datos
            scaler = StandardScaler()
            datos_normalizados = scaler.fit_transform(datos_numericos)
            
            # K-Means Clustering
            kmeans_resultados = {}
            for k in range(2, 8):
                kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
                clusters = kmeans.fit_predict(datos_normalizados)
                
                # Calcular silhouette score
                silhouette = silhouette_score(datos_normalizados, clusters)
                
                kmeans_resultados[k] = {
                    'silhouette_score': silhouette,
                    'inertia': kmeans.inertia_,
                    'centroides': kmeans.cluster_centers_.tolist()
                }
            
            # Encontrar número óptimo de clusters
            mejor_k = max(kmeans_resultados.keys(), key=lambda x: kmeans_resultados[x]['silhouette_score'])
            
            # Clustering final con mejor k
            kmeans_final = KMeans(n_clusters=mejor_k, random_state=42, n_init=10)
            clusters_final = kmeans_final.fit_predict(datos_normalizados)
            
            # DBSCAN Clustering
            dbscan = DBSCAN(eps=0.5, min_samples=5)
            clusters_dbscan = dbscan.fit_predict(datos_normalizados)
            
            # Análisis de clusters
            resultado = {
                'total_registros': len(datos_numericos),
                'variables_analizadas': variables_numericas.tolist(),
                'kmeans': {
                    'mejor_k': mejor_k,
                    'silhouette_score': kmeans_resultados[mejor_k]['silhouette_score'],
                    'resultados_por_k': kmeans_resultados,
                    'clusters': clusters_final.tolist(),
                    'centroides': kmeans_final.cluster_centers_.tolist()
                },
                'dbscan': {
                    'clusters': clusters_dbscan.tolist(),
                    'num_clusters': len(set(clusters_dbscan)) - (1 if -1 in clusters_dbscan else 0),
                    'puntos_ruido': list(clusters_dbscan).count(-1)
                }
            }
            
            self.resultados['clustering'] = resultado
            print("✅ Análisis de clustering completado")
            return resultado
            
        except Exception as e:
            print(f"Error analizando clustering: {e}")
            return {}
    
    def analisis_anomalias(self, datos: pd.DataFrame) -> Dict:
        """Análisis de anomalías en datos meteorológicos"""
        try:
            print("📊 Analizando anomalías en datos meteorológicos...")
            
            # Seleccionar variables numéricas
            variables_numericas = datos.select_dtypes(include=[np.number]).columns
            datos_numericos = datos[variables_numericas].dropna()
            
            resultado = {
                'total_registros': len(datos_numericos),
                'anomalias_por_variable': {}
            }
            
            for variable in variables_numericas:
                serie = datos_numericos[variable]
                
                # Método 1: Z-Score
                z_scores = np.abs(stats.zscore(serie))
                anomalias_zscore = z_scores > 3
                
                # Método 2: IQR
                Q1 = serie.quantile(0.25)
                Q3 = serie.quantile(0.75)
                IQR = Q3 - Q1
                limite_inferior = Q1 - 1.5 * IQR
                limite_superior = Q3 + 1.5 * IQR
                anomalias_iqr = (serie < limite_inferior) | (serie > limite_superior)
                
                # Método 3: Percentiles
                limite_inferior_pct = serie.quantile(0.01)
                limite_superior_pct = serie.quantile(0.99)
                anomalias_pct = (serie < limite_inferior_pct) | (serie > limite_superior_pct)
                
                resultado['anomalias_por_variable'][variable] = {
                    'zscore': {
                        'anomalias': anomalias_zscore.sum(),
                        'porcentaje': (anomalias_zscore.sum() / len(serie)) * 100,
                        'indices': anomalias_zscore[anomalias_zscore].index.tolist()
                    },
                    'iqr': {
                        'anomalias': anomalias_iqr.sum(),
                        'porcentaje': (anomalias_iqr.sum() / len(serie)) * 100,
                        'limite_inferior': limite_inferior,
                        'limite_superior': limite_superior,
                        'indices': anomalias_iqr[anomalias_iqr].index.tolist()
                    },
                    'percentiles': {
                        'anomalias': anomalias_pct.sum(),
                        'porcentaje': (anomalias_pct.sum() / len(serie)) * 100,
                        'limite_inferior': limite_inferior_pct,
                        'limite_superior': limite_superior_pct,
                        'indices': anomalias_pct[anomalias_pct].index.tolist()
                    }
                }
            
            self.resultados['anomalias'] = resultado
            print("✅ Análisis de anomalías completado")
            return resultado
            
        except Exception as e:
            print(f"Error analizando anomalías: {e}")
            return {}
    
    def analisis_pca(self, datos: pd.DataFrame) -> Dict:
        """Análisis de Componentes Principales (PCA)"""
        try:
            print("📊 Analizando PCA...")
            
            # Seleccionar variables numéricas
            variables_numericas = datos.select_dtypes(include=[np.number]).columns
            datos_numericos = datos[variables_numericas].dropna()
            
            # Normalizar datos
            scaler = StandardScaler()
            datos_normalizados = scaler.fit_transform(datos_numericos)
            
            # Aplicar PCA
            pca = PCA()
            componentes_principales = pca.fit_transform(datos_normalizados)
            
            # Análisis de varianza explicada
            varianza_explicada = pca.explained_variance_ratio_
            varianza_acumulada = np.cumsum(varianza_explicada)
            
            # Encontrar número de componentes para 95% de varianza
            componentes_95 = np.argmax(varianza_acumulada >= 0.95) + 1
            
            resultado = {
                'total_variables': len(variables_numericas),
                'total_registros': len(datos_numericos),
                'varianza_explicada': varianza_explicada.tolist(),
                'varianza_acumulada': varianza_acumulada.tolist(),
                'componentes_95_porciento': componentes_95,
                'componentes_principales': componentes_principales.tolist(),
                'loadings': pca.components_.tolist(),
                'variables_por_componente': {}
            }
            
            # Analizar contribución de variables por componente
            for i, componente in enumerate(pca.components_):
                contribuciones = np.abs(componente)
                indices_importantes = np.argsort(contribuciones)[-3:]  # Top 3
                
                resultado['variables_por_componente'][f'PC{i+1}'] = {
                    'variables_importantes': [variables_numericas[idx] for idx in indices_importantes],
                    'contribuciones': [contribuciones[idx] for idx in indices_importantes]
                }
            
            self.resultados['pca'] = resultado
            print("✅ Análisis PCA completado")
            return resultado
            
        except Exception as e:
            print(f"Error analizando PCA: {e}")
            return {}
    
    def crear_visualizaciones_avanzadas(self, datos: pd.DataFrame) -> bool:
        """Crear visualizaciones avanzadas del análisis"""
        try:
            print("📊 Creando visualizaciones avanzadas...")
            
            # 1. Gráfico de estacionalidad
            self._crear_grafico_estacionalidad(datos)
            
            # 2. Gráfico de correlaciones
            self._crear_grafico_correlaciones(datos)
            
            # 3. Gráfico de anomalías
            self._crear_grafico_anomalias(datos)
            
            # 4. Gráfico de clustering
            self._crear_grafico_clustering(datos)
            
            # 5. Gráfico de PCA
            self._crear_grafico_pca(datos)
            
            print("✅ Visualizaciones avanzadas creadas")
            return True
            
        except Exception as e:
            print(f"Error creando visualizaciones: {e}")
            return False
    
    def _crear_grafico_estacionalidad(self, datos: pd.DataFrame):
        """Crear gráfico de estacionalidad"""
        try:
            fig, axes = plt.subplots(2, 2, figsize=(15, 10))
            fig.suptitle('Análisis de Estacionalidad - METGO 3D', fontsize=16)
            
            # Temperatura mensual
            if 'temperatura' in datos.columns:
                datos_mensuales = datos['temperatura'].groupby(datos.index.month).mean()
                axes[0, 0].plot(datos_mensuales.index, datos_mensuales.values, 'o-', color='red')
                axes[0, 0].set_title('Temperatura Promedio Mensual')
                axes[0, 0].set_xlabel('Mes')
                axes[0, 0].set_ylabel('Temperatura (°C)')
                axes[0, 0].grid(True)
            
            # Precipitación mensual
            if 'precipitacion' in datos.columns:
                datos_mensuales = datos['precipitacion'].groupby(datos.index.month).sum()
                axes[0, 1].bar(datos_mensuales.index, datos_mensuales.values, color='blue', alpha=0.7)
                axes[0, 1].set_title('Precipitación Total Mensual')
                axes[0, 1].set_xlabel('Mes')
                axes[0, 1].set_ylabel('Precipitación (mm)')
                axes[0, 1].grid(True)
            
            # Humedad horaria
            if 'humedad' in datos.columns:
                datos_horarios = datos['humedad'].groupby(datos.index.hour).mean()
                axes[1, 0].plot(datos_horarios.index, datos_horarios.values, 'o-', color='green')
                axes[1, 0].set_title('Humedad Promedio Horaria')
                axes[1, 0].set_xlabel('Hora')
                axes[1, 0].set_ylabel('Humedad (%)')
                axes[1, 0].grid(True)
            
            # Viento direccional
            if 'viento_direccion' in datos.columns:
                datos_direccionales = datos['viento_direccion'].groupby(datos.index.hour).mean()
                axes[1, 1].plot(datos_direccionales.index, datos_direccionales.values, 'o-', color='orange')
                axes[1, 1].set_title('Dirección del Viento Promedio Horaria')
                axes[1, 1].set_xlabel('Hora')
                axes[1, 1].set_ylabel('Dirección (°)')
                axes[1, 1].grid(True)
            
            plt.tight_layout()
            plt.savefig(f"{self.configuracion['directorio_graficos']}/estacionalidad.png", dpi=300, bbox_inches='tight')
            plt.close()
            
        except Exception as e:
            print(f"Error creando gráfico de estacionalidad: {e}")
    
    def _crear_grafico_correlaciones(self, datos: pd.DataFrame):
        """Crear gráfico de correlaciones"""
        try:
            variables_numericas = datos.select_dtypes(include=[np.number]).columns
            datos_numericos = datos[variables_numericas].dropna()
            
            plt.figure(figsize=(12, 10))
            matriz_correlacion = datos_numericos.corr()
            
            sns.heatmap(matriz_correlacion, annot=True, cmap='coolwarm', center=0,
                       square=True, linewidths=0.5, cbar_kws={"shrink": 0.8})
            
            plt.title('Matriz de Correlaciones - Variables Meteorológicas', fontsize=16)
            plt.tight_layout()
            plt.savefig(f"{self.configuracion['directorio_graficos']}/correlaciones.png", dpi=300, bbox_inches='tight')
            plt.close()
            
        except Exception as e:
            print(f"Error creando gráfico de correlaciones: {e}")
    
    def _crear_grafico_anomalias(self, datos: pd.DataFrame):
        """Crear gráfico de anomalías"""
        try:
            if 'temperatura' not in datos.columns:
                return
            
            serie = datos['temperatura'].dropna()
            
            # Detectar anomalías con IQR
            Q1 = serie.quantile(0.25)
            Q3 = serie.quantile(0.75)
            IQR = Q3 - Q1
            limite_inferior = Q1 - 1.5 * IQR
            limite_superior = Q3 + 1.5 * IQR
            anomalias = (serie < limite_inferior) | (serie > limite_superior)
            
            plt.figure(figsize=(15, 8))
            
            # Gráfico de serie temporal
            plt.subplot(2, 1, 1)
            plt.plot(serie.index, serie.values, 'b-', alpha=0.7, label='Temperatura')
            plt.scatter(serie[anomalias].index, serie[anomalias].values, 
                       color='red', s=50, label='Anomalías', zorder=5)
            plt.axhline(y=limite_superior, color='red', linestyle='--', alpha=0.7, label='Límite Superior')
            plt.axhline(y=limite_inferior, color='red', linestyle='--', alpha=0.7, label='Límite Inferior')
            plt.title('Detección de Anomalías - Temperatura')
            plt.xlabel('Fecha')
            plt.ylabel('Temperatura (°C)')
            plt.legend()
            plt.grid(True)
            
            # Histograma
            plt.subplot(2, 1, 2)
            plt.hist(serie.values, bins=50, alpha=0.7, color='blue', label='Distribución')
            plt.axvline(x=limite_superior, color='red', linestyle='--', alpha=0.7, label='Límites')
            plt.axvline(x=limite_inferior, color='red', linestyle='--', alpha=0.7)
            plt.title('Distribución de Temperaturas')
            plt.xlabel('Temperatura (°C)')
            plt.ylabel('Frecuencia')
            plt.legend()
            plt.grid(True)
            
            plt.tight_layout()
            plt.savefig(f"{self.configuracion['directorio_graficos']}/anomalias.png", dpi=300, bbox_inches='tight')
            plt.close()
            
        except Exception as e:
            print(f"Error creando gráfico de anomalías: {e}")
    
    def _crear_grafico_clustering(self, datos: pd.DataFrame):
        """Crear gráfico de clustering"""
        try:
            variables_numericas = datos.select_dtypes(include=[np.number]).columns
            datos_numericos = datos[variables_numericas].dropna()
            
            # Normalizar datos
            scaler = StandardScaler()
            datos_normalizados = scaler.fit_transform(datos_numericos)
            
            # K-Means
            kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
            clusters = kmeans.fit_predict(datos_normalizados)
            
            # PCA para visualización 2D
            pca = PCA(n_components=2)
            datos_pca = pca.fit_transform(datos_normalizados)
            
            plt.figure(figsize=(12, 8))
            
            # Gráfico de clusters
            scatter = plt.scatter(datos_pca[:, 0], datos_pca[:, 1], c=clusters, cmap='viridis', alpha=0.6)
            plt.colorbar(scatter, label='Cluster')
            plt.title('Clustering de Patrones Meteorológicos (PCA 2D)')
            plt.xlabel(f'PC1 ({pca.explained_variance_ratio_[0]:.1%} varianza)')
            plt.ylabel(f'PC2 ({pca.explained_variance_ratio_[1]:.1%} varianza)')
            plt.grid(True)
            
            plt.tight_layout()
            plt.savefig(f"{self.configuracion['directorio_graficos']}/clustering.png", dpi=300, bbox_inches='tight')
            plt.close()
            
        except Exception as e:
            print(f"Error creando gráfico de clustering: {e}")
    
    def _crear_grafico_pca(self, datos: pd.DataFrame):
        """Crear gráfico de PCA"""
        try:
            variables_numericas = datos.select_dtypes(include=[np.number]).columns
            datos_numericos = datos[variables_numericas].dropna()
            
            # Normalizar datos
            scaler = StandardScaler()
            datos_normalizados = scaler.fit_transform(datos_numericos)
            
            # PCA
            pca = PCA()
            componentes_principales = pca.fit_transform(datos_normalizados)
            
            fig, axes = plt.subplots(2, 2, figsize=(15, 12))
            fig.suptitle('Análisis de Componentes Principales (PCA)', fontsize=16)
            
            # Varianza explicada
            varianza_explicada = pca.explained_variance_ratio_
            varianza_acumulada = np.cumsum(varianza_explicada)
            
            axes[0, 0].bar(range(1, len(varianza_explicada) + 1), varianza_explicada, alpha=0.7)
            axes[0, 0].set_title('Varianza Explicada por Componente')
            axes[0, 0].set_xlabel('Componente Principal')
            axes[0, 0].set_ylabel('Varianza Explicada')
            axes[0, 0].grid(True)
            
            # Varianza acumulada
            axes[0, 1].plot(range(1, len(varianza_acumulada) + 1), varianza_acumulada, 'o-')
            axes[0, 1].axhline(y=0.95, color='red', linestyle='--', alpha=0.7, label='95%')
            axes[0, 1].set_title('Varianza Acumulada')
            axes[0, 1].set_xlabel('Componente Principal')
            axes[0, 1].set_ylabel('Varianza Acumulada')
            axes[0, 1].legend()
            axes[0, 1].grid(True)
            
            # Loadings PC1 vs PC2
            loadings = pca.components_
            axes[1, 0].scatter(loadings[0], loadings[1], alpha=0.7)
            for i, variable in enumerate(variables_numericas):
                axes[1, 0].annotate(variable, (loadings[0, i], loadings[1, i]))
            axes[1, 0].set_title('Loadings PC1 vs PC2')
            axes[1, 0].set_xlabel('PC1')
            axes[1, 0].set_ylabel('PC2')
            axes[1, 0].grid(True)
            
            # Proyección 2D
            axes[1, 1].scatter(componentes_principales[:, 0], componentes_principales[:, 1], alpha=0.6)
            axes[1, 1].set_title('Proyección 2D de los Datos')
            axes[1, 1].set_xlabel(f'PC1 ({varianza_explicada[0]:.1%} varianza)')
            axes[1, 1].set_ylabel(f'PC2 ({varianza_explicada[1]:.1%} varianza)')
            axes[1, 1].grid(True)
            
            plt.tight_layout()
            plt.savefig(f"{self.configuracion['directorio_graficos']}/pca.png", dpi=300, bbox_inches='tight')
            plt.close()
            
        except Exception as e:
            print(f"Error creando gráfico de PCA: {e}")
    
    def generar_reporte_analisis_avanzado(self) -> str:
        """Generar reporte del análisis avanzado"""
        try:
            print("📋 Generando reporte del análisis avanzado...")
            
            reporte = {
                'timestamp': datetime.now().isoformat(),
                'sistema': 'METGO 3D - Análisis Avanzado',
                'version': self.configuracion['version'],
                'resumen': {
                    'total_analisis': len(self.resultados),
                    'variables_analizadas': len(self.variables_meteorologicas),
                    'graficos_generados': len(self.graficos)
                },
                'resultados': self.resultados,
                'recomendaciones': [
                    "Los patrones estacionales muestran variabilidad significativa",
                    "Las correlaciones entre variables pueden utilizarse para predicciones",
                    "El clustering identifica patrones meteorológicos distintivos",
                    "Las anomalías requieren atención especial para la calidad de datos",
                    "El PCA reduce la dimensionalidad manteniendo la información relevante"
                ]
            }
            
            # Guardar reporte
            reportes_dir = Path("reportes")
            reportes_dir.mkdir(exist_ok=True)
            
            reporte_file = reportes_dir / f"analisis_avanzado_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(reporte_file, 'w', encoding='utf-8') as f:
                json.dump(reporte, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Reporte de análisis avanzado generado: {reporte_file}")
            return str(reporte_file)
            
        except Exception as e:
            print(f"Error generando reporte: {e}")
            return ""

def main():
    """Función principal del análisis avanzado"""
    print("📊 ANÁLISIS AVANZADO PARA METGO 3D")
    print("Sistema Meteorológico Agrícola Quillota - Análisis Avanzado de Series Temporales")
    print("=" * 80)
    
    try:
        # Crear instancia de análisis avanzado
        analisis = AnalisisAvanzadoMETGO()
        
        # Cargar datos
        print("\n📊 Cargando datos meteorológicos...")
        datos = analisis.cargar_datos_meteorologicos()
        
        if datos.empty:
            print("❌ No se pudieron cargar los datos")
            return False
        
        # Análisis de estacionalidad
        print("\n📊 Analizando estacionalidad...")
        for variable in analisis.variables_meteorologicas:
            if variable in datos.columns:
                analisis.analisis_estacionalidad(datos, variable)
        
        # Análisis de frecuencias
        print("\n📊 Analizando frecuencias...")
        for variable in analisis.variables_meteorologicas:
            if variable in datos.columns:
                analisis.analisis_frecuencias(datos, variable)
        
        # Análisis de correlaciones
        print("\n📊 Analizando correlaciones...")
        analisis.analisis_correlaciones(datos)
        
        # Análisis de clustering
        print("\n📊 Analizando clustering...")
        analisis.analisis_clustering(datos)
        
        # Análisis de anomalías
        print("\n📊 Analizando anomalías...")
        analisis.analisis_anomalias(datos)
        
        # Análisis de PCA
        print("\n📊 Analizando PCA...")
        analisis.analisis_pca(datos)
        
        # Crear visualizaciones
        print("\n📊 Creando visualizaciones...")
        analisis.crear_visualizaciones_avanzadas(datos)
        
        # Generar reporte
        print("\n📋 Generando reporte...")
        reporte = analisis.generar_reporte_analisis_avanzado()
        
        if reporte:
            print(f"\n✅ Análisis avanzado completado exitosamente")
            print(f"📄 Reporte generado: {reporte}")
        else:
            print("\n⚠️ Error generando reporte")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error en análisis avanzado: {e}")
        return False

if __name__ == "__main__":
    try:
        exito = main()
        sys.exit(0 if exito else 1)
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        sys.exit(1)

