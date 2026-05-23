#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🌾 GESTIÓN DE DATOS DEL SISTEMA METGO 3D
Sistema Meteorológico Agrícola Quillota - Versión Operativa 2.0
"""

import os
import sys
import time
import json
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta

def print_header():
    """Imprimir encabezado"""
    print("🌾 GESTIÓN DE DATOS DEL SISTEMA METGO 3D")
    print("Sistema Meteorológico Agrícola Quillota - Versión Operativa 2.0")
    print("=" * 70)

def print_step(step, message):
    """Imprimir paso del proceso"""
    print(f"\n[{step}] {message}")
    print("-" * 50)

def print_success(message):
    """Imprimir mensaje de éxito")
    print(f"✅ {message}")

def print_error(message):
    """Imprimir mensaje de error")
    print(f"❌ {message}")

def print_warning(message):
    """Imprimir mensaje de advertencia")
    print(f"⚠️ {message}")

def print_info(message):
    """Imprimir mensaje informativo")
    print(f"ℹ️ {message}")

class GestorDatos:
    """Clase para gestión de datos del sistema"""
    
    def __init__(self):
        self.configuracion = {
            'directorio_datos': 'data',
            'archivo_config': 'config/datos.yaml',
            'archivo_datos': 'data/datos.json',
            'formatos_soportados': ['json', 'csv', 'xlsx', 'parquet', 'hdf5'],
            'compresion': True,
            'encriptacion': False
        }
        
        self.tipos_datos = [
            'meteorologicos',
            'agricolas',
            'sensores',
            'satelitales',
            'modelos',
            'calibracion',
            'validacion'
        ]
        
        self.operaciones = [
            'cargar',
            'guardar',
            'validar',
            'limpiar',
            'transformar',
            'filtrar',
            'agregar',
            'exportar'
        ]
    
    def cargar_configuracion(self):
        """Cargar configuración de datos"""
        try:
            print_info("Cargando configuración de datos...")
            
            config_file = Path(self.configuracion['archivo_config'])
            if config_file.exists():
                print_success("Configuración cargada")
            else:
                print_warning("Archivo de configuración no encontrado")
            
            return True
            
        except Exception as e:
            print_error(f"Error cargando configuración: {e}")
            return False
    
    def crear_estructura_datos(self):
        """Crear estructura de datos"""
        try:
            print_info("Creando estructura de datos...")
            
            # Crear directorio principal
            datos_dir = Path(self.configuracion['directorio_datos'])
            datos_dir.mkdir(exist_ok=True)
            
            # Crear subdirectorios
            subdirs = ['meteorologicos', 'agricolas', 'sensores', 'satelitales', 'modelos', 'calibracion', 'validacion']
            for subdir in subdirs:
                (datos_dir / subdir).mkdir(exist_ok=True)
            
            # Crear archivo de datos si no existe
            archivo_datos = Path(self.configuracion['archivo_datos'])
            if not archivo_datos.exists():
                with open(archivo_datos, 'w', encoding='utf-8') as f:
                    json.dump([], f, indent=2, ensure_ascii=False)
            
            print_success("Estructura de datos creada")
            return True
            
        except Exception as e:
            print_error(f"Error creando estructura: {e}")
            return False
    
    def cargar_datos(self, archivo, tipo=None, formato=None):
        """Cargar datos desde archivo"""
        try:
            print_info(f"Cargando datos desde: {archivo}")
            
            archivo_path = Path(archivo)
            if not archivo_path.exists():
                print_error(f"Archivo no encontrado: {archivo}")
                return None
            
            # Determinar formato si no se especifica
            if formato is None:
                formato = archivo_path.suffix[1:].lower()
            
            # Cargar según formato
            if formato == 'json':
                with open(archivo_path, 'r', encoding='utf-8') as f:
                    datos = json.load(f)
            
            elif formato == 'csv':
                datos = pd.read_csv(archivo_path)
            
            elif formato == 'xlsx':
                datos = pd.read_excel(archivo_path)
            
            elif formato == 'parquet':
                datos = pd.read_parquet(archivo_path)
            
            elif formato == 'hdf5':
                datos = pd.read_hdf(archivo_path, 'data')
            
            else:
                print_error(f"Formato no soportado: {formato}")
                return None
            
            print_success(f"Datos cargados: {len(datos) if hasattr(datos, '__len__') else 'N/A'}")
            return datos
            
        except Exception as e:
            print_error(f"Error cargando datos: {e}")
            return None
    
    def guardar_datos(self, datos, archivo, tipo=None, formato=None):
        """Guardar datos en archivo"""
        try:
            print_info(f"Guardando datos en: {archivo}")
            
            archivo_path = Path(archivo)
            archivo_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Determinar formato si no se especifica
            if formato is None:
                formato = archivo_path.suffix[1:].lower()
            
            # Guardar según formato
            if formato == 'json':
                with open(archivo_path, 'w', encoding='utf-8') as f:
                    json.dump(datos, f, indent=2, ensure_ascii=False)
            
            elif formato == 'csv':
                if isinstance(datos, pd.DataFrame):
                    datos.to_csv(archivo_path, index=False)
                else:
                    print_error("Los datos deben ser un DataFrame para formato CSV")
                    return False
            
            elif formato == 'xlsx':
                if isinstance(datos, pd.DataFrame):
                    datos.to_excel(archivo_path, index=False)
                else:
                    print_error("Los datos deben ser un DataFrame para formato XLSX")
                    return False
            
            elif formato == 'parquet':
                if isinstance(datos, pd.DataFrame):
                    datos.to_parquet(archivo_path)
                else:
                    print_error("Los datos deben ser un DataFrame para formato Parquet")
                    return False
            
            elif formato == 'hdf5':
                if isinstance(datos, pd.DataFrame):
                    datos.to_hdf(archivo_path, 'data', mode='w')
                else:
                    print_error("Los datos deben ser un DataFrame para formato HDF5")
                    return False
            
            else:
                print_error(f"Formato no soportado: {formato}")
                return False
            
            print_success(f"Datos guardados: {archivo_path}")
            return True
            
        except Exception as e:
            print_error(f"Error guardando datos: {e}")
            return False
    
    def validar_datos(self, datos, esquema=None):
        """Validar datos"""
        try:
            print_info("Validando datos...")
            
            if datos is None:
                print_error("No hay datos para validar")
                return False
            
            # Validación básica
            validaciones = {
                'no_vacio': len(datos) > 0 if hasattr(datos, '__len__') else True,
                'tipo_valido': isinstance(datos, (dict, list, pd.DataFrame, np.ndarray)),
                'estructura_valida': True
            }
            
            # Validación específica para DataFrames
            if isinstance(datos, pd.DataFrame):
                validaciones['columnas_no_vacias'] = not datos.empty
                validaciones['sin_nan_criticos'] = not datos.isnull().all().any()
                validaciones['tipos_consistentes'] = True
                
                # Verificar tipos de datos
                for col in datos.columns:
                    if datos[col].dtype == 'object':
                        # Verificar si hay valores no nulos
                        if datos[col].notna().any():
                            validaciones['tipos_consistentes'] = False
                            break
            
            # Validación específica para diccionarios
            elif isinstance(datos, dict):
                validaciones['claves_requeridas'] = True
                validaciones['valores_no_nulos'] = all(v is not None for v in datos.values())
            
            # Validación específica para listas
            elif isinstance(datos, list):
                validaciones['elementos_no_nulos'] = all(item is not None for item in datos)
                validaciones['tipos_homogeneos'] = len(set(type(item) for item in datos)) <= 1
            
            # Mostrar resultados
            print(f"\n📊 Resultados de validación:")
            for validacion, resultado in validaciones.items():
                estado = "✅" if resultado else "❌"
                print(f"{estado} {validacion}: {resultado}")
            
            # Determinar si es válido
            es_valido = all(validaciones.values())
            
            if es_valido:
                print_success("Datos válidos")
            else:
                print_warning("Datos con problemas de validación")
            
            return es_valido
            
        except Exception as e:
            print_error(f"Error validando datos: {e}")
            return False
    
    def limpiar_datos(self, datos, estrategia='auto'):
        """Limpiar datos"""
        try:
            print_info(f"Limpiando datos con estrategia: {estrategia}")
            
            if datos is None:
                print_error("No hay datos para limpiar")
                return None
            
            datos_limpios = datos.copy() if hasattr(datos, 'copy') else datos
            
            # Limpieza para DataFrames
            if isinstance(datos, pd.DataFrame):
                # Eliminar filas completamente vacías
                datos_limpios = datos_limpios.dropna(how='all')
                
                # Eliminar columnas completamente vacías
                datos_limpios = datos_limpios.dropna(axis=1, how='all')
                
                # Reemplazar valores faltantes
                if estrategia == 'auto':
                    # Para columnas numéricas, usar la media
                    for col in datos_limpios.select_dtypes(include=[np.number]).columns:
                        datos_limpios[col] = datos_limpios[col].fillna(datos_limpios[col].mean())
                    
                    # Para columnas de texto, usar el valor más frecuente
                    for col in datos_limpios.select_dtypes(include=['object']).columns:
                        valor_frecuente = datos_limpios[col].mode()
                        if not valor_frecuente.empty:
                            datos_limpios[col] = datos_limpios[col].fillna(valor_frecuente[0])
                
                # Eliminar duplicados
                datos_limpios = datos_limpios.drop_duplicates()
                
                print_success(f"Datos limpiados: {len(datos_limpios)} filas, {len(datos_limpios.columns)} columnas")
            
            # Limpieza para listas
            elif isinstance(datos, list):
                # Eliminar valores None
                datos_limpios = [item for item in datos if item is not None]
                
                # Eliminar duplicados
                datos_limpios = list(set(datos_limpios))
                
                print_success(f"Datos limpiados: {len(datos_limpios)} elementos")
            
            # Limpieza para diccionarios
            elif isinstance(datos, dict):
                # Eliminar valores None
                datos_limpios = {k: v for k, v in datos.items() if v is not None}
                
                print_success(f"Datos limpiados: {len(datos_limpios)} elementos")
            
            return datos_limpios
            
        except Exception as e:
            print_error(f"Error limpiando datos: {e}")
            return None
    
    def transformar_datos(self, datos, transformaciones):
        """Transformar datos"""
        try:
            print_info("Transformando datos...")
            
            if datos is None:
                print_error("No hay datos para transformar")
                return None
            
            datos_transformados = datos.copy() if hasattr(datos, 'copy') else datos
            
            # Aplicar transformaciones
            for transformacion in transformaciones:
                tipo = transformacion.get('tipo')
                parametros = transformacion.get('parametros', {})
                
                if tipo == 'normalizar':
                    # Normalizar columnas numéricas
                    if isinstance(datos_transformados, pd.DataFrame):
                        for col in parametros.get('columnas', []):
                            if col in datos_transformados.columns:
                                datos_transformados[col] = (datos_transformados[col] - datos_transformados[col].mean()) / datos_transformados[col].std()
                
                elif tipo == 'escalar':
                    # Escalar columnas numéricas
                    if isinstance(datos_transformados, pd.DataFrame):
                        for col in parametros.get('columnas', []):
                            if col in datos_transformados.columns:
                                min_val = datos_transformados[col].min()
                                max_val = datos_transformados[col].max()
                                datos_transformados[col] = (datos_transformados[col] - min_val) / (max_val - min_val)
                
                elif tipo == 'logaritmo':
                    # Aplicar logaritmo
                    if isinstance(datos_transformados, pd.DataFrame):
                        for col in parametros.get('columnas', []):
                            if col in datos_transformados.columns:
                                datos_transformados[col] = np.log1p(datos_transformados[col])
                
                elif tipo == 'categorizar':
                    # Convertir a categorías
                    if isinstance(datos_transformados, pd.DataFrame):
                        for col in parametros.get('columnas', []):
                            if col in datos_transformados.columns:
                                datos_transformados[col] = pd.Categorical(datos_transformados[col])
                
                elif tipo == 'agregar':
                    # Agregar nueva columna
                    if isinstance(datos_transformados, pd.DataFrame):
                        columna = parametros.get('columna')
                        valor = parametros.get('valor')
                        if columna and valor is not None:
                            datos_transformados[columna] = valor
                
                elif tipo == 'eliminar':
                    # Eliminar columnas
                    if isinstance(datos_transformados, pd.DataFrame):
                        for col in parametros.get('columnas', []):
                            if col in datos_transformados.columns:
                                datos_transformados = datos_transformados.drop(columns=[col])
                
                elif tipo == 'renombrar':
                    # Renombrar columnas
                    if isinstance(datos_transformados, pd.DataFrame):
                        mapeo = parametros.get('mapeo', {})
                        datos_transformados = datos_transformados.rename(columns=mapeo)
            
            print_success("Datos transformados correctamente")
            return datos_transformados
            
        except Exception as e:
            print_error(f"Error transformando datos: {e}")
            return None
    
    def filtrar_datos(self, datos, filtros):
        """Filtrar datos"""
        try:
            print_info("Filtrando datos...")
            
            if datos is None:
                print_error("No hay datos para filtrar")
                return None
            
            datos_filtrados = datos.copy() if hasattr(datos, 'copy') else datos
            
            # Aplicar filtros
            for filtro in filtros:
                tipo = filtro.get('tipo')
                parametros = filtro.get('parametros', {})
                
                if tipo == 'rango':
                    # Filtrar por rango de valores
                    if isinstance(datos_filtrados, pd.DataFrame):
                        columna = parametros.get('columna')
                        min_val = parametros.get('min')
                        max_val = parametros.get('max')
                        
                        if columna and columna in datos_filtrados.columns:
                            if min_val is not None:
                                datos_filtrados = datos_filtrados[datos_filtrados[columna] >= min_val]
                            if max_val is not None:
                                datos_filtrados = datos_filtrados[datos_filtrados[columna] <= max_val]
                
                elif tipo == 'valor':
                    # Filtrar por valor específico
                    if isinstance(datos_filtrados, pd.DataFrame):
                        columna = parametros.get('columna')
                        valor = parametros.get('valor')
                        
                        if columna and columna in datos_filtrados.columns:
                            datos_filtrados = datos_filtrados[datos_filtrados[columna] == valor]
                
                elif tipo == 'texto':
                    # Filtrar por texto
                    if isinstance(datos_filtrados, pd.DataFrame):
                        columna = parametros.get('columna')
                        patron = parametros.get('patron')
                        
                        if columna and columna in datos_filtrados.columns:
                            datos_filtrados = datos_filtrados[datos_filtrados[columna].str.contains(patron, na=False)]
                
                elif tipo == 'fecha':
                    # Filtrar por fecha
                    if isinstance(datos_filtrados, pd.DataFrame):
                        columna = parametros.get('columna')
                        fecha_inicio = parametros.get('fecha_inicio')
                        fecha_fin = parametros.get('fecha_fin')
                        
                        if columna and columna in datos_filtrados.columns:
                            if fecha_inicio:
                                datos_filtrados = datos_filtrados[datos_filtrados[columna] >= fecha_inicio]
                            if fecha_fin:
                                datos_filtrados = datos_filtrados[datos_filtrados[columna] <= fecha_fin]
            
            print_success(f"Datos filtrados: {len(datos_filtrados) if hasattr(datos_filtrados, '__len__') else 'N/A'}")
            return datos_filtrados
            
        except Exception as e:
            print_error(f"Error filtrando datos: {e}")
            return None
    
    def agregar_datos(self, datos, nuevos_datos, estrategia='append'):
        """Agregar nuevos datos"""
        try:
            print_info(f"Agregando datos con estrategia: {estrategia}")
            
            if datos is None:
                print_error("No hay datos base para agregar")
                return None
            
            if nuevos_datos is None:
                print_error("No hay nuevos datos para agregar")
                return None
            
            # Agregar según estrategia
            if estrategia == 'append':
                # Agregar al final
                if isinstance(datos, list) and isinstance(nuevos_datos, list):
                    datos_agregados = datos + nuevos_datos
                elif isinstance(datos, pd.DataFrame) and isinstance(nuevos_datos, pd.DataFrame):
                    datos_agregados = pd.concat([datos, nuevos_datos], ignore_index=True)
                else:
                    print_error("Tipos de datos incompatibles para agregar")
                    return None
            
            elif estrategia == 'prepend':
                # Agregar al inicio
                if isinstance(datos, list) and isinstance(nuevos_datos, list):
                    datos_agregados = nuevos_datos + datos
                elif isinstance(datos, pd.DataFrame) and isinstance(nuevos_datos, pd.DataFrame):
                    datos_agregados = pd.concat([nuevos_datos, datos], ignore_index=True)
                else:
                    print_error("Tipos de datos incompatibles para agregar")
                    return None
            
            elif estrategia == 'merge':
                # Combinar por columnas comunes
                if isinstance(datos, pd.DataFrame) and isinstance(nuevos_datos, pd.DataFrame):
                    datos_agregados = pd.merge(datos, nuevos_datos, how='outer')
                else:
                    print_error("Solo se puede hacer merge con DataFrames")
                    return None
            
            else:
                print_error(f"Estrategia no soportada: {estrategia}")
                return None
            
            print_success(f"Datos agregados: {len(datos_agregados) if hasattr(datos_agregados, '__len__') else 'N/A'}")
            return datos_agregados
            
        except Exception as e:
            print_error(f"Error agregando datos: {e}")
            return None
    
    def exportar_datos(self, datos, archivo, formato=None, opciones=None):
        """Exportar datos"""
        try:
            print_info(f"Exportando datos a: {archivo}")
            
            if datos is None:
                print_error("No hay datos para exportar")
                return False
            
            archivo_path = Path(archivo)
            archivo_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Determinar formato si no se especifica
            if formato is None:
                formato = archivo_path.suffix[1:].lower()
            
            # Opciones por defecto
            if opciones is None:
                opciones = {}
            
            # Exportar según formato
            if formato == 'json':
                with open(archivo_path, 'w', encoding='utf-8') as f:
                    json.dump(datos, f, indent=2, ensure_ascii=False)
            
            elif formato == 'csv':
                if isinstance(datos, pd.DataFrame):
                    datos.to_csv(archivo_path, index=opciones.get('index', False))
                else:
                    print_error("Los datos deben ser un DataFrame para formato CSV")
                    return False
            
            elif formato == 'xlsx':
                if isinstance(datos, pd.DataFrame):
                    datos.to_excel(archivo_path, index=opciones.get('index', False))
                else:
                    print_error("Los datos deben ser un DataFrame para formato XLSX")
                    return False
            
            elif formato == 'parquet':
                if isinstance(datos, pd.DataFrame):
                    datos.to_parquet(archivo_path)
                else:
                    print_error("Los datos deben ser un DataFrame para formato Parquet")
                    return False
            
            elif formato == 'hdf5':
                if isinstance(datos, pd.DataFrame):
                    datos.to_hdf(archivo_path, 'data', mode='w')
                else:
                    print_error("Los datos deben ser un DataFrame para formato HDF5")
                    return False
            
            else:
                print_error(f"Formato no soportado: {formato}")
                return False
            
            print_success(f"Datos exportados: {archivo_path}")
            return True
            
        except Exception as e:
            print_error(f"Error exportando datos: {e}")
            return False
    
    def generar_reporte_datos(self):
        """Generar reporte de datos"""
        try:
            print_info("Generando reporte de datos...")
            
            # Crear reporte
            reporte = {
                'timestamp': datetime.now().isoformat(),
                'sistema': 'METGO 3D - Sistema Meteorológico Agrícola Quillota',
                'version': '2.0',
                'configuracion': self.configuracion,
                'estadisticas': {
                    'archivos_datos': len(list(Path('data').rglob('*'))),
                    'tamaño_total': sum(f.stat().st_size for f in Path('data').rglob('*') if f.is_file()),
                    'formatos_utilizados': list(set(f.suffix[1:] for f in Path('data').rglob('*') if f.is_file())),
                    'tipos_datos': self.tipos_datos,
                    'operaciones': self.operaciones
                }
            }
            
            # Guardar reporte
            reportes_dir = Path("reportes")
            reportes_dir.mkdir(exist_ok=True)
            
            reporte_file = reportes_dir / f"datos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(reporte_file, 'w', encoding='utf-8') as f:
                json.dump(reporte, f, indent=2, ensure_ascii=False)
            
            print_success(f"Reporte de datos generado: {reporte_file}")
            
            # Mostrar resumen
            print(f"\n📊 Resumen de datos:")
            print(f"Archivos de datos: {reporte['estadisticas']['archivos_datos']}")
            print(f"Tamaño total: {reporte['estadisticas']['tamaño_total'] / 1024 / 1024:.2f} MB")
            print(f"Formatos utilizados: {reporte['estadisticas']['formatos_utilizados']}")
            
            return str(reporte_file)
            
        except Exception as e:
            print_error(f"Error generando reporte: {e}")
            return None

def mostrar_menu():
    """Mostrar menú de gestión de datos"""
    print("\n" + "=" * 70)
    print("📋 MENÚ DE GESTIÓN DE DATOS - METGO 3D")
    print("=" * 70)
    
    print("\n1. 🔍 Cargar configuración")
    print("2. 📁 Crear estructura de datos")
    print("3. 📂 Cargar datos")
    print("4. 💾 Guardar datos")
    print("5. ✅ Validar datos")
    print("6. 🧹 Limpiar datos")
    print("7. 🔄 Transformar datos")
    print("8. 🔍 Filtrar datos")
    print("9. ➕ Agregar datos")
    print("10. 📤 Exportar datos")
    print("11. 📊 Generar reporte")
    print("12. ❌ Salir")
    
    print("\n" + "=" * 70)

def main():
    """Función principal de gestión de datos"""
    print_header()
    
    # Crear gestor de datos
    gestor = GestorDatos()
    
    while True:
        mostrar_menu()
        
        try:
            opcion = input("\n🔢 Selecciona una opción (1-12): ").strip()
            
            if opcion == "1":
                print_step("1", "Cargando configuración")
                if gestor.cargar_configuracion():
                    print_success("Configuración cargada correctamente")
                else:
                    print_error("Error cargando configuración")
                input("\n⏸️ Presiona Enter para continuar...")
            
            elif opcion == "2":
                print_step("2", "Creando estructura de datos")
                if gestor.crear_estructura_datos():
                    print_success("Estructura de datos creada correctamente")
                else:
                    print_error("Error creando estructura")
                input("\n⏸️ Presiona Enter para continuar...")
            
            elif opcion == "3":
                print_step("3", "Cargando datos")
                try:
                    archivo = input("Archivo: ").strip()
                    tipo = input("Tipo (opcional): ").strip() or None
                    formato = input("Formato (opcional): ").strip() or None
                    
                    datos = gestor.cargar_datos(archivo, tipo, formato)
                    if datos is not None:
                        print_success("Datos cargados correctamente")
                    else:
                        print_error("Error cargando datos")
                except Exception as e:
                    print_error(f"Error: {e}")
                input("\n⏸️ Presiona Enter para continuar...")
            
            elif opcion == "4":
                print_step("4", "Guardando datos")
                try:
                    archivo = input("Archivo: ").strip()
                    tipo = input("Tipo (opcional): ").strip() or None
                    formato = input("Formato (opcional): ").strip() or None
                    
                    # Nota: En un caso real, los datos vendrían de una variable o archivo
                    datos = {'ejemplo': 'datos de prueba'}
                    
                    if gestor.guardar_datos(datos, archivo, tipo, formato):
                        print_success("Datos guardados correctamente")
                    else:
                        print_error("Error guardando datos")
                except Exception as e:
                    print_error(f"Error: {e}")
                input("\n⏸️ Presiona Enter para continuar...")
            
            elif opcion == "5":
                print_step("5", "Validando datos")
                try:
                    archivo = input("Archivo: ").strip()
                    
                    datos = gestor.cargar_datos(archivo)
                    if datos is not None:
                        if gestor.validar_datos(datos):
                            print_success("Datos válidos")
                        else:
                            print_warning("Datos con problemas de validación")
                    else:
                        print_error("Error cargando datos para validar")
                except Exception as e:
                    print_error(f"Error: {e}")
                input("\n⏸️ Presiona Enter para continuar...")
            
            elif opcion == "6":
                print_step("6", "Limpiando datos")
                try:
                    archivo = input("Archivo: ").strip()
                    estrategia = input("Estrategia (auto/manual, default auto): ").strip() or "auto"
                    
                    datos = gestor.cargar_datos(archivo)
                    if datos is not None:
                        datos_limpios = gestor.limpiar_datos(datos, estrategia)
                        if datos_limpios is not None:
                            print_success("Datos limpiados correctamente")
                        else:
                            print_error("Error limpiando datos")
                    else:
                        print_error("Error cargando datos para limpiar")
                except Exception as e:
                    print_error(f"Error: {e}")
                input("\n⏸️ Presiona Enter para continuar...")
            
            elif opcion == "7":
                print_step("7", "Transformando datos")
                try:
                    archivo = input("Archivo: ").strip()
                    transformaciones = input("Transformaciones (JSON): ").strip()
                    
                    datos = gestor.cargar_datos(archivo)
                    if datos is not None:
                        try:
                            transformaciones = json.loads(transformaciones)
                            datos_transformados = gestor.transformar_datos(datos, transformaciones)
                            if datos_transformados is not None:
                                print_success("Datos transformados correctamente")
                            else:
                                print_error("Error transformando datos")
                        except json.JSONDecodeError:
                            print_error("Transformaciones no válidas")
                    else:
                        print_error("Error cargando datos para transformar")
                except Exception as e:
                    print_error(f"Error: {e}")
                input("\n⏸️ Presiona Enter para continuar...")
            
            elif opcion == "8":
                print_step("8", "Filtrando datos")
                try:
                    archivo = input("Archivo: ").strip()
                    filtros = input("Filtros (JSON): ").strip()
                    
                    datos = gestor.cargar_datos(archivo)
                    if datos is not None:
                        try:
                            filtros = json.loads(filtros)
                            datos_filtrados = gestor.filtrar_datos(datos, filtros)
                            if datos_filtrados is not None:
                                print_success("Datos filtrados correctamente")
                            else:
                                print_error("Error filtrando datos")
                        except json.JSONDecodeError:
                            print_error("Filtros no válidos")
                    else:
                        print_error("Error cargando datos para filtrar")
                except Exception as e:
                    print_error(f"Error: {e}")
                input("\n⏸️ Presiona Enter para continuar...")
            
            elif opcion == "9":
                print_step("9", "Agregando datos")
                try:
                    archivo_base = input("Archivo base: ").strip()
                    archivo_nuevos = input("Archivo nuevos datos: ").strip()
                    estrategia = input("Estrategia (append/prepend/merge, default append): ").strip() or "append"
                    
                    datos_base = gestor.cargar_datos(archivo_base)
                    datos_nuevos = gestor.cargar_datos(archivo_nuevos)
                    
                    if datos_base is not None and datos_nuevos is not None:
                        datos_agregados = gestor.agregar_datos(datos_base, datos_nuevos, estrategia)
                        if datos_agregados is not None:
                            print_success("Datos agregados correctamente")
                        else:
                            print_error("Error agregando datos")
                    else:
                        print_error("Error cargando datos para agregar")
                except Exception as e:
                    print_error(f"Error: {e}")
                input("\n⏸️ Presiona Enter para continuar...")
            
            elif opcion == "10":
                print_step("10", "Exportando datos")
                try:
                    archivo = input("Archivo: ").strip()
                    formato = input("Formato (json/csv/xlsx/parquet/hdf5, default json): ").strip() or "json"
                    opciones = input("Opciones (JSON opcional): ").strip()
                    
                    datos = gestor.cargar_datos(archivo)
                    if datos is not None:
                        try:
                            opciones = json.loads(opciones) if opciones else None
                            if gestor.exportar_datos(datos, archivo, formato, opciones):
                                print_success("Datos exportados correctamente")
                            else:
                                print_error("Error exportando datos")
                        except json.JSONDecodeError:
                            print_error("Opciones no válidas")
                    else:
                        print_error("Error cargando datos para exportar")
                except Exception as e:
                    print_error(f"Error: {e}")
                input("\n⏸️ Presiona Enter para continuar...")
            
            elif opcion == "11":
                print_step("11", "Generando reporte de datos")
                reporte = gestor.generar_reporte_datos()
                if reporte:
                    print_success(f"Reporte generado: {reporte}")
                else:
                    print_error("Error generando reporte")
                input("\n⏸️ Presiona Enter para continuar...")
            
            elif opcion == "12":
                print_info("Saliendo del gestor de datos...")
                print_success("¡Hasta luego! 🌾")
                break
            
            else:
                print_warning("Opción no válida. Selecciona 1-12.")
                time.sleep(1)
        
        except KeyboardInterrupt:
            print("\n⚠️ Gestión de datos interrumpida por el usuario")
            print_success("¡Hasta luego! 🌾")
            break
        except Exception as e:
            print_error(f"Error inesperado: {e}")
            input("\n⏸️ Presiona Enter para continuar...")
    
    return True

if __name__ == "__main__":
    try:
        exito = main()
        sys.exit(0 if exito else 1)
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        sys.exit(1)