"""
SISTEMA DE MODELOS ULTRA-OPTIMIZADO PARA SISTEMAS CON RECURSOS LIMITADOS
Optimizado específicamente para 8 núcleos CPU y 5GB RAM disponibles
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, ExtraTreesRegressor, VotingRegressor
from sklearn.linear_model import Ridge
from sklearn.preprocessing import RobustScaler
from sklearn.model_selection import TimeSeriesSplit, cross_val_score
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.feature_selection import SelectKBest, f_regression
import joblib
import sqlite3
import json
import logging
from datetime import datetime, timedelta
import warnings
from typing import Dict, List, Tuple, Optional, Any
import os
import gc  # Para liberar memoria
import psutil  # Para monitorear memoria

warnings.filterwarnings('ignore')

class SistemaModelosUltraOptimizado:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.base_datos = "modelos_ultra_optimizados.db"
        self.modelos_dir = "modelos_ultra_optimizados"
        self._crear_directorios()
        self._inicializar_base_datos()
        self.modelos_activos = {}
        
        # Configuración ultra-optimizada para sistemas con recursos limitados
        self.modelos_base_ultra_optimizados = {
            'RandomForest_Ultra': {
                'clase': RandomForestRegressor,
                'parametros': {
                    'n_estimators': 30,  # Muy reducido para velocidad
                    'max_depth': 10,     # Reducido para memoria
                    'min_samples_split': 10,
                    'max_features': 'sqrt',
                    'random_state': 42,
                    'n_jobs': 2  # Solo 2 núcleos para no saturar
                },
                'peso_inicial': 0.4
            },
            'GradientBoosting_Ultra': {
                'clase': GradientBoostingRegressor,
                'parametros': {
                    'n_estimators': 30,  # Muy reducido
                    'learning_rate': 0.2,
                    'max_depth': 6,
                    'random_state': 42
                },
                'peso_inicial': 0.3
            },
            'ExtraTrees_Ultra': {
                'clase': ExtraTreesRegressor,
                'parametros': {
                    'n_estimators': 30,  # Muy reducido
                    'max_depth': 10,
                    'min_samples_split': 10,
                    'max_features': 'sqrt',
                    'random_state': 42,
                    'n_jobs': 2  # Solo 2 núcleos
                },
                'peso_inicial': 0.2
            },
            'Ridge_Ultra': {
                'clase': Ridge,
                'parametros': {
                    'alpha': 1.0,
                    'solver': 'auto'
                },
                'peso_inicial': 0.1
            }
        }
    
    def _crear_directorios(self):
        """Crear directorios necesarios"""
        directorios = [self.modelos_dir, 'logs']
        for directorio in directorios:
            if not os.path.exists(directorio):
                os.makedirs(directorio)
    
    def _inicializar_base_datos(self):
        """Inicializar base de datos ultra-optimizada"""
        try:
            conn = sqlite3.connect(self.base_datos)
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS modelos_ultra_optimizados (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre_modelo TEXT UNIQUE NOT NULL,
                    variable_objetivo TEXT NOT NULL,
                    metricas TEXT NOT NULL,
                    tiempo_entrenamiento REAL,
                    memoria_usada REAL,
                    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
                    estado TEXT DEFAULT 'activo'
                )
            ''')
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error inicializando base de datos: {e}")
    
    def _monitorear_memoria(self) -> Dict[str, float]:
        """Monitorear uso de memoria"""
        try:
            memoria = psutil.virtual_memory()
            return {
                'total_gb': memoria.total / (1024**3),
                'disponible_gb': memoria.available / (1024**3),
                'usado_gb': memoria.used / (1024**3),
                'porcentaje': memoria.percent
            }
        except:
            return {'disponible_gb': 5.0}  # Valor por defecto
    
    def _liberar_memoria(self):
        """Liberar memoria no utilizada"""
        try:
            gc.collect()
        except:
            pass
    
    def crear_modelo_ultra_optimizado(self, nombre_modelo: str, variable_objetivo: str,
                                     descripcion: str = "") -> Dict:
        """Crear modelo ultra-optimizado para sistemas con recursos limitados"""
        try:
            print(f"[CREANDO] Modelo ultra-optimizado: {nombre_modelo}")
            
            # Monitorear memoria inicial
            memoria_inicial = self._monitorear_memoria()
            print(f"[MEMORIA] Inicial: {memoria_inicial['disponible_gb']:.1f}GB disponibles")
            
            if memoria_inicial['disponible_gb'] < 2.0:
                raise ValueError("Memoria insuficiente. Se requieren al menos 2GB disponibles.")
            
            inicio_tiempo = datetime.now()
            
            # Cargar datos con optimización de memoria
            df = self._cargar_datos_optimizados()
            if df.empty:
                raise ValueError("No hay datos disponibles")
            
            # Preparar datos ultra-optimizados
            X, y = self._preparar_datos_ultra_optimizados(df, variable_objetivo)
            
            if len(X) == 0 or len(y) == 0:
                raise ValueError("No hay datos válidos para entrenar")
            
            print(f"[DATOS] {len(X)} muestras, {X.shape[1]} características")
            
            # Liberar memoria después de preparar datos
            del df
            self._liberar_memoria()
            
            # Crear ensemble ultra-optimizado
            modelo_hibrido = self._crear_ensemble_ultra_optimizado(X, y, variable_objetivo)
            
            if modelo_hibrido is None:
                raise ValueError("Error creando modelo")
            
            # Evaluación rápida
            y_pred = modelo_hibrido.predict(X)
            r2 = r2_score(y, y_pred)
            rmse = np.sqrt(mean_squared_error(y, y_pred))
            mae = mean_absolute_error(y, y_pred)
            
            tiempo_entrenamiento = (datetime.now() - inicio_tiempo).total_seconds()
            
            # Monitorear memoria final
            memoria_final = self._monitorear_memoria()
            memoria_usada = memoria_inicial['disponible_gb'] - memoria_final['disponible_gb']
            
            metricas = {
                'r2': r2,
                'rmse': rmse,
                'mae': mae,
                'tiempo_entrenamiento': tiempo_entrenamiento,
                'memoria_usada_gb': memoria_usada,
                'memoria_inicial_gb': memoria_inicial['disponible_gb'],
                'memoria_final_gb': memoria_final['disponible_gb']
            }
            
            # Guardar modelo
            modelo_id = self._guardar_modelo_en_bd(nombre_modelo, variable_objetivo, metricas)
            
            # Guardar modelo en disco (con compresión)
            ruta_modelo = os.path.join(self.modelos_dir, f"{nombre_modelo}.joblib")
            joblib.dump(modelo_hibrido, ruta_modelo, compress=3)  # Compresión máxima
            
            # Actualizar modelos activos
            self.modelos_activos[nombre_modelo] = {
                'modelo': modelo_hibrido,
                'variable_objetivo': variable_objetivo,
                'metricas': metricas,
                'modelo_id': modelo_id,
                'fecha_creacion': datetime.now()
            }
            
            # Liberar memoria final
            self._liberar_memoria()
            
            print(f"[OK] Modelo ultra-optimizado '{nombre_modelo}' creado exitosamente")
            print(f"    R² = {r2:.6f}")
            print(f"    RMSE = {rmse:.6f}")
            print(f"    Tiempo = {tiempo_entrenamiento:.2f}s")
            print(f"    Memoria usada = {memoria_usada:.2f}GB")
            
            return {
                'modelo_id': modelo_id,
                'nombre_modelo': nombre_modelo,
                'variable_objetivo': variable_objetivo,
                'metricas': metricas,
                'estado': 'creado_exitosamente'
            }
            
        except Exception as e:
            print(f"[ERROR] Error creando modelo ultra-optimizado: {e}")
            return {'error': str(e)}
    
    def _cargar_datos_optimizados(self) -> pd.DataFrame:
        """Cargar datos con optimización de memoria"""
        try:
            # Intentar cargar datos existentes
            conn = sqlite3.connect("modelos_dinamicos.db")
            df = pd.read_sql_query(
                "SELECT * FROM datos_historicos_3_anos ORDER BY fecha LIMIT 1000",  # Limitar para memoria
                conn,
                parse_dates=['fecha']
            )
            conn.close()
            
            if not df.empty:
                return df
            
            # Si no hay datos, generar datos mínimos
            return self._generar_datos_minimos()
            
        except Exception as e:
            self.logger.error(f"Error cargando datos optimizados: {e}")
            return self._generar_datos_minimos()
    
    def _generar_datos_minimos(self) -> pd.DataFrame:
        """Generar datos mínimos para demostración"""
        try:
            print("[GENERANDO] Datos mínimos optimizados...")
            np.random.seed(42)
            
            # Generar solo 6 meses de datos para ahorrar memoria
            fecha_inicio = datetime.now() - timedelta(days=180)
            fechas = pd.date_range(start=fecha_inicio, end=datetime.now(), freq='D')
            
            datos = []
            estaciones = ['quillota_centro', 'la_cruz']  # Solo 2 estaciones
            
            for fecha in fechas:
                for estacion in estaciones:
                    mes = fecha.month
                    
                    # Datos básicos
                    temp_base = 16 + 7 * np.sin(2 * np.pi * (mes - 1) / 12)
                    temp_max = temp_base + np.random.normal(6, 2)
                    temp_min = temp_base - np.random.normal(6, 1.5)
                    temp_promedio = (temp_max + temp_min) / 2
                    
                    humedad = 75 - (temp_promedio - 15) * 1.5 + np.random.normal(0, 8)
                    humedad = np.clip(humedad, 25, 95)
                    
                    datos.append({
                        'fecha': fecha,
                        'estacion': estacion,
                        'temperatura_max': round(temp_max, 1),
                        'temperatura_min': round(temp_min, 1),
                        'temperatura_promedio': round(temp_promedio, 1),
                        'humedad_relativa': round(humedad, 1),
                        'velocidad_viento': round(max(0, 8 + np.random.normal(0, 4)), 1),
                        'precipitacion': round(np.random.exponential(3) if np.random.random() < 0.1 else 0, 1),
                        'presion_atmosferica': round(1013.25 + np.random.normal(0, 8), 1),
                        'nubosidad': round(min(100, max(0, humedad * 0.8 + np.random.normal(0, 15))), 1),
                        'radiacion_solar': round(max(0, 800 + np.random.normal(0, 50)), 1)
                    })
            
            df = pd.DataFrame(datos)
            print(f"[OK] Datos mínimos generados: {len(df)} registros")
            return df
            
        except Exception as e:
            self.logger.error(f"Error generando datos mínimos: {e}")
            return pd.DataFrame()
    
    def _preparar_datos_ultra_optimizados(self, df: pd.DataFrame, variable_objetivo: str) -> Tuple[np.ndarray, np.ndarray]:
        """Preparar datos ultra-optimizados para memoria"""
        try:
            # Características básicas mínimas
            df['año'] = df['fecha'].dt.year
            df['mes'] = df['fecha'].dt.month
            df['dia'] = df['fecha'].dt.day
            df['dia_semana'] = df['fecha'].dt.dayofweek
            
            # Características cíclicas básicas
            df['mes_sin'] = np.sin(2 * np.pi * df['mes'] / 12)
            df['mes_cos'] = np.cos(2 * np.pi * df['mes'] / 12)
            
            # Características derivadas básicas
            df['amplitud_termica'] = df['temperatura_max'] - df['temperatura_min']
            
            # Codificar estación (solo 2 estaciones)
            if 'estacion' in df.columns:
                estacion_encoded = pd.get_dummies(df['estacion'], prefix='estacion')
                df = pd.concat([df, estacion_encoded], axis=1)
            
            # Seleccionar características mínimas
            caracteristicas_base = [
                'temperatura_max', 'temperatura_min', 'temperatura_promedio',
                'humedad_relativa', 'velocidad_viento', 'precipitacion',
                'presion_atmosferica', 'nubosidad', 'radiacion_solar',
                'año', 'mes', 'dia', 'dia_semana',
                'mes_sin', 'mes_cos', 'amplitud_termica'
            ]
            
            # Agregar columnas de estación
            caracteristicas_estacion = [col for col in df.columns if col.startswith('estacion_')]
            caracteristicas = [col for col in caracteristicas_base if col in df.columns] + caracteristicas_estacion
            
            if not caracteristicas:
                raise ValueError("No se encontraron características válidas")
            
            X = df[caracteristicas].fillna(df[caracteristicas].mean())
            y = df[variable_objetivo].fillna(df[variable_objetivo].mean())
            
            # Escalar características
            scaler = RobustScaler()
            X_scaled = scaler.fit_transform(X)
            
            # Selección de características (máximo 20 para ahorrar memoria)
            if X_scaled.shape[1] > 20:
                selector = SelectKBest(score_func=f_regression, k=20)
                X_scaled = selector.fit_transform(X_scaled, y)
            
            return X_scaled, y.values
            
        except Exception as e:
            self.logger.error(f"Error preparando datos ultra-optimizados: {e}")
            return np.array([]), np.array([])
    
    def _crear_ensemble_ultra_optimizado(self, X: np.ndarray, y: np.ndarray, variable_objetivo: str):
        """Crear ensemble ultra-optimizado"""
        try:
            print("[CREANDO] Ensemble ultra-optimizado...")
            
            # Crear modelos base ultra-optimizados
            modelos_base = []
            for nombre, config in self.modelos_base_ultra_optimizados.items():
                modelo = config['clase'](**config['parametros'])
                modelos_base.append((nombre, modelo))
            
            # Crear VotingRegressor
            ensemble = VotingRegressor(estimators=modelos_base)
            
            # Entrenar ensemble
            ensemble.fit(X, y)
            
            return ensemble
            
        except Exception as e:
            self.logger.error(f"Error creando ensemble ultra-optimizado: {e}")
            return None
    
    def generar_proyecciones_ultra_rapidas(self, nombre_modelo: str, horizonte_dias: int = 15) -> List[Dict]:
        """Generar proyecciones ultra-rápidas"""
        try:
            print(f"[PROYECTANDO] Modelo ultra-optimizado '{nombre_modelo}' para {horizonte_dias} días...")
            
            if nombre_modelo not in self.modelos_activos:
                raise ValueError(f"Modelo '{nombre_modelo}' no está activo")
            
            modelo_info = self.modelos_activos[nombre_modelo]
            modelo = modelo_info['modelo']
            variable_objetivo = modelo_info['variable_objetivo']
            
            # Generar proyecciones
            proyecciones = []
            fecha_actual = datetime.now()
            
            for i in range(horizonte_dias):
                fecha_proyeccion = fecha_actual + timedelta(days=i)
                
                # Preparar características simplificadas
                X_pred = self._preparar_caracteristicas_proyeccion_simple(fecha_proyeccion)
                
                # Realizar predicción
                valor_proyectado = modelo.predict(X_pred.reshape(1, -1))[0]
                
                # Intervalo de confianza simplificado
                rmse = modelo_info['metricas']['rmse']
                confianza = max(0.1, 1.0 - (i / horizonte_dias) * 0.5)
                
                proyeccion = {
                    'fecha': fecha_proyeccion.strftime('%Y-%m-%d'),
                    'dias_futuro': i + 1,
                    'variable': variable_objetivo,
                    'valor_proyectado': round(valor_proyectado, 4),
                    'intervalo_inferior': round(valor_proyectado - rmse * confianza, 4),
                    'intervalo_superior': round(valor_proyectado + rmse * confianza, 4),
                    'confianza': round(confianza, 3),
                    'modelo_usado': nombre_modelo
                }
                
                proyecciones.append(proyeccion)
            
            print(f"[OK] {len(proyecciones)} proyecciones ultra-rápidas generadas")
            return proyecciones
            
        except Exception as e:
            print(f"[ERROR] Error generando proyecciones ultra-rápidas: {e}")
            return []
    
    def _preparar_caracteristicas_proyeccion_simple(self, fecha: datetime) -> np.ndarray:
        """Preparar características simplificadas para proyección"""
        try:
            # Características básicas (debe coincidir con el entrenamiento)
            caracteristicas = [
                20 + 5 * np.sin(2 * np.pi * fecha.month / 12) + np.random.normal(0, 2),  # temp_max
                15 + 5 * np.sin(2 * np.pi * fecha.month / 12) + np.random.normal(0, 1.5),  # temp_min
                17.5 + 5 * np.sin(2 * np.pi * fecha.month / 12) + np.random.normal(0, 1.5),  # temp_promedio
                70 + np.random.normal(0, 5),  # humedad_relativa
                10 + np.random.normal(0, 3),  # velocidad_viento
                0 if np.random.random() > 0.1 else np.random.exponential(2),  # precipitacion
                1013 + np.random.normal(0, 5),  # presion_atmosferica
                50 + np.random.normal(0, 15),  # nubosidad
                800 + np.random.normal(0, 50),  # radiacion_solar
                fecha.year,  # año
                fecha.month,  # mes
                fecha.day,  # dia
                fecha.weekday(),  # dia_semana
                np.sin(2 * np.pi * fecha.month / 12),  # mes_sin
                np.cos(2 * np.pi * fecha.month / 12),  # mes_cos
                5 + np.random.normal(0, 2),  # amplitud_termica
                1,  # estacion_quillota_centro
                0,  # estacion_la_cruz
                0,  # característica adicional para llegar a 20
                0   # característica adicional para llegar a 20
            ]
            
            return np.array(caracteristicas)
            
        except Exception as e:
            self.logger.error(f"Error preparando características simples: {e}")
            return np.array([])
    
    def listar_modelos_ultra_optimizados(self) -> List[Dict]:
        """Listar modelos ultra-optimizados activos"""
        try:
            modelos = []
            for nombre, info in self.modelos_activos.items():
                modelos.append({
                    'nombre': nombre,
                    'variable_objetivo': info['variable_objetivo'],
                    'r2': info['metricas']['r2'],
                    'rmse': info['metricas']['rmse'],
                    'tiempo_entrenamiento': info['metricas']['tiempo_entrenamiento'],
                    'memoria_usada': info['metricas']['memoria_usada_gb'],
                    'fecha_creacion': info['fecha_creacion'].strftime('%Y-%m-%d %H:%M:%S')
                })
            return modelos
        except Exception as e:
            self.logger.error(f"Error listando modelos ultra-optimizados: {e}")
            return []
    
    def _guardar_modelo_en_bd(self, nombre: str, variable: str, metricas: Dict) -> int:
        """Guardar modelo en base de datos"""
        try:
            conn = sqlite3.connect(self.base_datos)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO modelos_ultra_optimizados 
                (nombre_modelo, variable_objetivo, metricas, tiempo_entrenamiento, memoria_usada)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                nombre, variable,
                json.dumps(metricas),
                metricas['tiempo_entrenamiento'],
                metricas['memoria_usada_gb']
            ))
            
            modelo_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return modelo_id
            
        except Exception as e:
            self.logger.error(f"Error guardando modelo en BD: {e}")
            return 0

def main():
    """Función principal para demostración ultra-optimizada"""
    print("="*80)
    print("SISTEMA DE MODELOS ULTRA-OPTIMIZADO - METGO 3D QUILLOTA")
    print("Optimizado para sistemas con recursos limitados")
    print("="*80)
    
    # Inicializar sistema
    sistema = SistemaModelosUltraOptimizado()
    
    # Crear modelos ultra-optimizados
    print("\n[1] CREANDO MODELOS ULTRA-OPTIMIZADOS...")
    
    # Modelo 1: Temperatura
    resultado1 = sistema.crear_modelo_ultra_optimizado(
        nombre_modelo="Ultra_Temp_Optimizado",
        variable_objetivo="temperatura_promedio",
        descripcion="Modelo ultra-optimizado para temperatura con recursos limitados"
    )
    
    # Modelo 2: Humedad
    resultado2 = sistema.crear_modelo_ultra_optimizado(
        nombre_modelo="Ultra_Humedad_Optimizado",
        variable_objetivo="humedad_relativa",
        descripcion="Modelo ultra-optimizado para humedad con recursos limitados"
    )
    
    # Generar proyecciones ultra-rápidas
    print("\n[2] GENERANDO PROYECCIONES ULTRA-RÁPIDAS...")
    
    proyecciones_temp = sistema.generar_proyecciones_ultra_rapidas("Ultra_Temp_Optimizado", 15)
    proyecciones_humedad = sistema.generar_proyecciones_ultra_rapidas("Ultra_Humedad_Optimizado", 10)
    
    # Listar modelos
    print("\n[3] MODELOS ULTRA-OPTIMIZADOS ACTIVOS:")
    modelos = sistema.listar_modelos_ultra_optimizados()
    for modelo in modelos:
        print(f"    - {modelo['nombre']}: R²={modelo['r2']:.6f}, Tiempo={modelo['tiempo_entrenamiento']:.2f}s, Memoria={modelo['memoria_usada']:.2f}GB")
    
    print("\n" + "="*80)
    print("SISTEMA ULTRA-OPTIMIZADO COMPLETADO")
    print("="*80)
    print(f"Modelos creados: {len(modelos)}")
    print(f"Proyecciones temperatura: {len(proyecciones_temp)}")
    print(f"Proyecciones humedad: {len(proyecciones_humedad)}")
    
    # Resumen de rendimiento
    if modelos:
        r2_promedio = np.mean([m['r2'] for m in modelos])
        tiempo_promedio = np.mean([m['tiempo_entrenamiento'] for m in modelos])
        memoria_promedio = np.mean([m['memoria_usada'] for m in modelos])
        
        print(f"R² promedio: {r2_promedio:.6f}")
        print(f"Tiempo promedio: {tiempo_promedio:.2f}s")
        print(f"Memoria promedio: {memoria_promedio:.2f}GB")
        print("OPTIMIZADO PARA RECURSOS LIMITADOS")
    
    print("="*80)

if __name__ == "__main__":
    main()
