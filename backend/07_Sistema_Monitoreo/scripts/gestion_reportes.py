#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🌾 GESTIÓN DE REPORTES DEL SISTEMA METGO 3D
Sistema Meteorológico Agrícola Quillota - Versión Operativa 2.0
"""

import os
import sys
import time
import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from datetime import datetime, timedelta

def print_header():
    """Imprimir encabezado"""
    print("🌾 GESTIÓN DE REPORTES DEL SISTEMA METGO 3D")
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

class GestorReportes:
    """Clase para gestión de reportes del sistema"""
    
    def __init__(self):
        self.configuracion = {
            'directorio_reportes': 'reportes',
            'archivo_config': 'config/reportes.yaml',
            'archivo_reportes': 'reportes/reportes.json',
            'formatos_soportados': ['json', 'csv', 'xlsx', 'pdf', 'html'],
            'plantillas': True,
            'graficos': True
        }
        
        self.tipos_reportes = [
            'meteorologico',
            'agricola',
            'sistema',
            'rendimiento',
            'seguridad',
            'auditoria',
            'resumen',
            'detallado'
        ]
        
        self.plantillas = {
            'meteorologico': {
                'titulo': 'Reporte Meteorológico',
                'secciones': ['resumen', 'temperaturas', 'precipitacion', 'viento', 'humedad'],
                'graficos': ['lineas', 'barras', 'dispersion']
            },
            'agricola': {
                'titulo': 'Reporte Agrícola',
                'secciones': ['resumen', 'indices', 'recomendaciones', 'alertas'],
                'graficos': ['barras', 'torta', 'calendario']
            },
            'sistema': {
                'titulo': 'Reporte del Sistema',
                'secciones': ['resumen', 'metricas', 'errores', 'rendimiento'],
                'graficos': ['lineas', 'barras', 'indicadores']
            }
        }
    
    def cargar_configuracion(self):
        """Cargar configuración de reportes"""
        try:
            print_info("Cargando configuración de reportes...")
            
            config_file = Path(self.configuracion['archivo_config'])
            if config_file.exists():
                print_success("Configuración cargada")
            else:
                print_warning("Archivo de configuración no encontrado")
            
            return True
            
        except Exception as e:
            print_error(f"Error cargando configuración: {e}")
            return False
    
    def crear_estructura_reportes(self):
        """Crear estructura de reportes"""
        try:
            print_info("Creando estructura de reportes...")
            
            # Crear directorio principal
            reportes_dir = Path(self.configuracion['directorio_reportes'])
            reportes_dir.mkdir(exist_ok=True)
            
            # Crear subdirectorios
            subdirs = ['meteorologico', 'agricola', 'sistema', 'rendimiento', 'seguridad', 'auditoria', 'resumen', 'detallado']
            for subdir in subdirs:
                (reportes_dir / subdir).mkdir(exist_ok=True)
            
            # Crear archivo de reportes si no existe
            archivo_reportes = Path(self.configuracion['archivo_reportes'])
            if not archivo_reportes.exists():
                with open(archivo_reportes, 'w', encoding='utf-8') as f:
                    json.dump([], f, indent=2, ensure_ascii=False)
            
            print_success("Estructura de reportes creada")
            return True
            
        except Exception as e:
            print_error(f"Error creando estructura: {e}")
            return False
    
    def crear_reporte(self, tipo, titulo, datos, opciones=None):
        """Crear reporte"""
        try:
            print_info(f"Creando reporte: {tipo}")
            
            # Verificar que el tipo sea válido
            if tipo not in self.tipos_reportes:
                print_error(f"Tipo de reporte no válido: {tipo}")
                return False
            
            # Crear ID de reporte
            reporte_id = f"reporte_{tipo}_{int(time.time())}"
            
            # Crear directorio de reporte
            reporte_dir = Path(f"reportes/{tipo}/{reporte_id}")
            reporte_dir.mkdir(exist_ok=True)
            
            # Crear reporte según tipo
            if tipo == 'meteorologico':
                exito = self._crear_reporte_meteorologico(reporte_dir, titulo, datos, opciones)
            elif tipo == 'agricola':
                exito = self._crear_reporte_agricola(reporte_dir, titulo, datos, opciones)
            elif tipo == 'sistema':
                exito = self._crear_reporte_sistema(reporte_dir, titulo, datos, opciones)
            elif tipo == 'rendimiento':
                exito = self._crear_reporte_rendimiento(reporte_dir, titulo, datos, opciones)
            elif tipo == 'seguridad':
                exito = self._crear_reporte_seguridad(reporte_dir, titulo, datos, opciones)
            elif tipo == 'auditoria':
                exito = self._crear_reporte_auditoria(reporte_dir, titulo, datos, opciones)
            elif tipo == 'resumen':
                exito = self._crear_reporte_resumen(reporte_dir, titulo, datos, opciones)
            elif tipo == 'detallado':
                exito = self._crear_reporte_detallado(reporte_dir, titulo, datos, opciones)
            
            if not exito:
                print_error(f"Error creando reporte {tipo}")
                return False
            
            # Crear registro de reporte
            reporte = {
                'id': reporte_id,
                'tipo': tipo,
                'titulo': titulo,
                'directorio': str(reporte_dir),
                'creado': datetime.now().isoformat(),
                'estado': 'completado',
                'opciones': opciones or {}
            }
            
            # Agregar reporte
            self.reportes.append(reporte)
            
            # Guardar reportes
            self.guardar_reportes()
            
            print_success(f"Reporte {reporte_id} creado correctamente")
            return reporte_id
            
        except Exception as e:
            print_error(f"Error creando reporte: {e}")
            return None
    
    def _crear_reporte_meteorologico(self, reporte_dir, titulo, datos, opciones):
        """Crear reporte meteorológico"""
        try:
            print_info("Creando reporte meteorológico...")
            
            # Crear archivo de datos
            datos_file = reporte_dir / 'datos.json'
            with open(datos_file, 'w', encoding='utf-8') as f:
                json.dump(datos, f, indent=2, ensure_ascii=False)
            
            # Crear resumen
            resumen = {
                'titulo': titulo,
                'fecha': datetime.now().isoformat(),
                'tipo': 'meteorologico',
                'resumen': {
                    'temperatura_promedio': datos.get('temperatura_promedio', 0),
                    'precipitacion_total': datos.get('precipitacion_total', 0),
                    'humedad_promedio': datos.get('humedad_promedio', 0),
                    'viento_promedio': datos.get('viento_promedio', 0)
                }
            }
            
            # Guardar resumen
            resumen_file = reporte_dir / 'resumen.json'
            with open(resumen_file, 'w', encoding='utf-8') as f:
                json.dump(resumen, f, indent=2, ensure_ascii=False)
            
            # Crear gráficos si está habilitado
            if self.configuracion['graficos']:
                self._crear_graficos_meteorologicos(reporte_dir, datos)
            
            return True
            
        except Exception as e:
            print_error(f"Error creando reporte meteorológico: {e}")
            return False
    
    def _crear_reporte_agricola(self, reporte_dir, titulo, datos, opciones):
        """Crear reporte agrícola"""
        try:
            print_info("Creando reporte agrícola...")
            
            # Crear archivo de datos
            datos_file = reporte_dir / 'datos.json'
            with open(datos_file, 'w', encoding='utf-8') as f:
                json.dump(datos, f, indent=2, ensure_ascii=False)
            
            # Crear resumen
            resumen = {
                'titulo': titulo,
                'fecha': datetime.now().isoformat(),
                'tipo': 'agricola',
                'resumen': {
                    'indices_calculados': datos.get('indices_calculados', 0),
                    'recomendaciones': datos.get('recomendaciones', []),
                    'alertas': datos.get('alertas', [])
                }
            }
            
            # Guardar resumen
            resumen_file = reporte_dir / 'resumen.json'
            with open(resumen_file, 'w', encoding='utf-8') as f:
                json.dump(resumen, f, indent=2, ensure_ascii=False)
            
            # Crear gráficos si está habilitado
            if self.configuracion['graficos']:
                self._crear_graficos_agricolas(reporte_dir, datos)
            
            return True
            
        except Exception as e:
            print_error(f"Error creando reporte agrícola: {e}")
            return False
    
    def _crear_reporte_sistema(self, reporte_dir, titulo, datos, opciones):
        """Crear reporte del sistema"""
        try:
            print_info("Creando reporte del sistema...")
            
            # Crear archivo de datos
            datos_file = reporte_dir / 'datos.json'
            with open(datos_file, 'w', encoding='utf-8') as f:
                json.dump(datos, f, indent=2, ensure_ascii=False)
            
            # Crear resumen
            resumen = {
                'titulo': titulo,
                'fecha': datetime.now().isoformat(),
                'tipo': 'sistema',
                'resumen': {
                    'metricas': datos.get('metricas', {}),
                    'errores': datos.get('errores', []),
                    'rendimiento': datos.get('rendimiento', {})
                }
            }
            
            # Guardar resumen
            resumen_file = reporte_dir / 'resumen.json'
            with open(resumen_file, 'w', encoding='utf-8') as f:
                json.dump(resumen, f, indent=2, ensure_ascii=False)
            
            # Crear gráficos si está habilitado
            if self.configuracion['graficos']:
                self._crear_graficos_sistema(reporte_dir, datos)
            
            return True
            
        except Exception as e:
            print_error(f"Error creando reporte del sistema: {e}")
            return False
    
    def _crear_reporte_rendimiento(self, reporte_dir, titulo, datos, opciones):
        """Crear reporte de rendimiento"""
        try:
            print_info("Creando reporte de rendimiento...")
            
            # Crear archivo de datos
            datos_file = reporte_dir / 'datos.json'
            with open(datos_file, 'w', encoding='utf-8') as f:
                json.dump(datos, f, indent=2, ensure_ascii=False)
            
            # Crear resumen
            resumen = {
                'titulo': titulo,
                'fecha': datetime.now().isoformat(),
                'tipo': 'rendimiento',
                'resumen': {
                    'metricas_rendimiento': datos.get('metricas_rendimiento', {}),
                    'optimizaciones': datos.get('optimizaciones', []),
                    'recomendaciones': datos.get('recomendaciones', [])
                }
            }
            
            # Guardar resumen
            resumen_file = reporte_dir / 'resumen.json'
            with open(resumen_file, 'w', encoding='utf-8') as f:
                json.dump(resumen, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            print_error(f"Error creando reporte de rendimiento: {e}")
            return False
    
    def _crear_reporte_seguridad(self, reporte_dir, titulo, datos, opciones):
        """Crear reporte de seguridad"""
        try:
            print_info("Creando reporte de seguridad...")
            
            # Crear archivo de datos
            datos_file = reporte_dir / 'datos.json'
            with open(datos_file, 'w', encoding='utf-8') as f:
                json.dump(datos, f, indent=2, ensure_ascii=False)
            
            # Crear resumen
            resumen = {
                'titulo': titulo,
                'fecha': datetime.now().isoformat(),
                'tipo': 'seguridad',
                'resumen': {
                    'vulnerabilidades': datos.get('vulnerabilidades', []),
                    'alertas_seguridad': datos.get('alertas_seguridad', []),
                    'recomendaciones': datos.get('recomendaciones', [])
                }
            }
            
            # Guardar resumen
            resumen_file = reporte_dir / 'resumen.json'
            with open(resumen_file, 'w', encoding='utf-8') as f:
                json.dump(resumen, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            print_error(f"Error creando reporte de seguridad: {e}")
            return False
    
    def _crear_reporte_auditoria(self, reporte_dir, titulo, datos, opciones):
        """Crear reporte de auditoría"""
        try:
            print_info("Creando reporte de auditoría...")
            
            # Crear archivo de datos
            datos_file = reporte_dir / 'datos.json'
            with open(datos_file, 'w', encoding='utf-8') as f:
                json.dump(datos, f, indent=2, ensure_ascii=False)
            
            # Crear resumen
            resumen = {
                'titulo': titulo,
                'fecha': datetime.now().isoformat(),
                'tipo': 'auditoria',
                'resumen': {
                    'eventos_auditados': datos.get('eventos_auditados', 0),
                    'eventos_por_tipo': datos.get('eventos_por_tipo', {}),
                    'eventos_por_usuario': datos.get('eventos_por_usuario', {})
                }
            }
            
            # Guardar resumen
            resumen_file = reporte_dir / 'resumen.json'
            with open(resumen_file, 'w', encoding='utf-8') as f:
                json.dump(resumen, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            print_error(f"Error creando reporte de auditoría: {e}")
            return False
    
    def _crear_reporte_resumen(self, reporte_dir, titulo, datos, opciones):
        """Crear reporte resumen"""
        try:
            print_info("Creando reporte resumen...")
            
            # Crear archivo de datos
            datos_file = reporte_dir / 'datos.json'
            with open(datos_file, 'w', encoding='utf-8') as f:
                json.dump(datos, f, indent=2, ensure_ascii=False)
            
            # Crear resumen
            resumen = {
                'titulo': titulo,
                'fecha': datetime.now().isoformat(),
                'tipo': 'resumen',
                'resumen': {
                    'puntos_clave': datos.get('puntos_clave', []),
                    'metricas_principales': datos.get('metricas_principales', {}),
                    'recomendaciones': datos.get('recomendaciones', [])
                }
            }
            
            # Guardar resumen
            resumen_file = reporte_dir / 'resumen.json'
            with open(resumen_file, 'w', encoding='utf-8') as f:
                json.dump(resumen, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            print_error(f"Error creando reporte resumen: {e}")
            return False
    
    def _crear_reporte_detallado(self, reporte_dir, titulo, datos, opciones):
        """Crear reporte detallado"""
        try:
            print_info("Creando reporte detallado...")
            
            # Crear archivo de datos
            datos_file = reporte_dir / 'datos.json'
            with open(datos_file, 'w', encoding='utf-8') as f:
                json.dump(datos, f, indent=2, ensure_ascii=False)
            
            # Crear resumen
            resumen = {
                'titulo': titulo,
                'fecha': datetime.now().isoformat(),
                'tipo': 'detallado',
                'resumen': {
                    'secciones': datos.get('secciones', []),
                    'detalles': datos.get('detalles', {}),
                    'anexos': datos.get('anexos', [])
                }
            }
            
            # Guardar resumen
            resumen_file = reporte_dir / 'resumen.json'
            with open(resumen_file, 'w', encoding='utf-8') as f:
                json.dump(resumen, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            print_error(f"Error creando reporte detallado: {e}")
            return False
    
    def _crear_graficos_meteorologicos(self, reporte_dir, datos):
        """Crear gráficos meteorológicos"""
        try:
            print_info("Creando gráficos meteorológicos...")
            
            # Configurar matplotlib
            plt.style.use('seaborn-v0_8')
            fig, axes = plt.subplots(2, 2, figsize=(15, 10))
            fig.suptitle('Análisis Meteorológico', fontsize=16)
            
            # Gráfico de temperaturas
            if 'temperaturas' in datos:
                axes[0, 0].plot(datos['temperaturas'])
                axes[0, 0].set_title('Temperaturas')
                axes[0, 0].set_ylabel('Temperatura (°C)')
            
            # Gráfico de precipitación
            if 'precipitacion' in datos:
                axes[0, 1].bar(range(len(datos['precipitacion'])), datos['precipitacion'])
                axes[0, 1].set_title('Precipitación')
                axes[0, 1].set_ylabel('Precipitación (mm)')
            
            # Gráfico de humedad
            if 'humedad' in datos:
                axes[1, 0].plot(datos['humedad'])
                axes[1, 0].set_title('Humedad')
                axes[1, 0].set_ylabel('Humedad (%)')
            
            # Gráfico de viento
            if 'viento' in datos:
                axes[1, 1].plot(datos['viento'])
                axes[1, 1].set_title('Viento')
                axes[1, 1].set_ylabel('Velocidad (km/h)')
            
            # Ajustar layout
            plt.tight_layout()
            
            # Guardar gráfico
            grafico_file = reporte_dir / 'graficos_meteorologicos.png'
            plt.savefig(grafico_file, dpi=300, bbox_inches='tight')
            plt.close()
            
            print_success(f"Gráficos meteorológicos creados: {grafico_file}")
            return True
            
        except Exception as e:
            print_error(f"Error creando gráficos meteorológicos: {e}")
            return False
    
    def _crear_graficos_agricolas(self, reporte_dir, datos):
        """Crear gráficos agrícolas"""
        try:
            print_info("Creando gráficos agrícolas...")
            
            # Configurar matplotlib
            plt.style.use('seaborn-v0_8')
            fig, axes = plt.subplots(2, 2, figsize=(15, 10))
            fig.suptitle('Análisis Agrícola', fontsize=16)
            
            # Gráfico de índices
            if 'indices' in datos:
                indices = list(datos['indices'].keys())
                valores = list(datos['indices'].values())
                axes[0, 0].bar(indices, valores)
                axes[0, 0].set_title('Índices Agrícolas')
                axes[0, 0].set_ylabel('Valor')
                axes[0, 0].tick_params(axis='x', rotation=45)
            
            # Gráfico de recomendaciones
            if 'recomendaciones' in datos:
                recomendaciones = datos['recomendaciones']
                axes[0, 1].pie([1] * len(recomendaciones), labels=recomendaciones)
                axes[0, 1].set_title('Recomendaciones')
            
            # Gráfico de alertas
            if 'alertas' in datos:
                alertas = datos['alertas']
                axes[1, 0].bar(range(len(alertas)), [1] * len(alertas))
                axes[1, 0].set_title('Alertas')
                axes[1, 0].set_ylabel('Cantidad')
            
            # Gráfico de tendencias
            if 'tendencias' in datos:
                tendencias = datos['tendencias']
                axes[1, 1].plot(tendencias)
                axes[1, 1].set_title('Tendencias')
                axes[1, 1].set_ylabel('Valor')
            
            # Ajustar layout
            plt.tight_layout()
            
            # Guardar gráfico
            grafico_file = reporte_dir / 'graficos_agricolas.png'
            plt.savefig(grafico_file, dpi=300, bbox_inches='tight')
            plt.close()
            
            print_success(f"Gráficos agrícolas creados: {grafico_file}")
            return True
            
        except Exception as e:
            print_error(f"Error creando gráficos agrícolas: {e}")
            return False
    
    def _crear_graficos_sistema(self, reporte_dir, datos):
        """Crear gráficos del sistema"""
        try:
            print_info("Creando gráficos del sistema...")
            
            # Configurar matplotlib
            plt.style.use('seaborn-v0_8')
            fig, axes = plt.subplots(2, 2, figsize=(15, 10))
            fig.suptitle('Análisis del Sistema', fontsize=16)
            
            # Gráfico de métricas
            if 'metricas' in datos:
                metricas = datos['metricas']
                if 'cpu' in metricas:
                    axes[0, 0].plot(metricas['cpu'])
                    axes[0, 0].set_title('CPU')
                    axes[0, 0].set_ylabel('Uso (%)')
                
                if 'memoria' in metricas:
                    axes[0, 1].plot(metricas['memoria'])
                    axes[0, 1].set_title('Memoria')
                    axes[0, 1].set_ylabel('Uso (%)')
                
                if 'disco' in metricas:
                    axes[1, 0].plot(metricas['disco'])
                    axes[1, 0].set_title('Disco')
                    axes[1, 0].set_ylabel('Uso (%)')
                
                if 'red' in metricas:
                    axes[1, 1].plot(metricas['red'])
                    axes[1, 1].set_title('Red')
                    axes[1, 1].set_ylabel('Tráfico (MB)')
            
            # Ajustar layout
            plt.tight_layout()
            
            # Guardar gráfico
            grafico_file = reporte_dir / 'graficos_sistema.png'
            plt.savefig(grafico_file, dpi=300, bbox_inches='tight')
            plt.close()
            
            print_success(f"Gráficos del sistema creados: {grafico_file}")
            return True
            
        except Exception as e:
            print_error(f"Error creando gráficos del sistema: {e}")
            return False
    
    def listar_reportes(self, tipo=None):
        """Listar reportes"""
        try:
            print_info("Listando reportes...")
            
            # Filtrar reportes
            reportes_filtrados = self.reportes
            if tipo:
                reportes_filtrados = [r for r in self.reportes if r['tipo'] == tipo]
            
            if not reportes_filtrados:
                print_warning("No hay reportes para mostrar")
                return []
            
            print(f"\n📋 Reportes ({len(reportes_filtrados)}):")
            print("-" * 120)
            print(f"{'ID':<25} {'Tipo':<15} {'Título':<30} {'Creado':<20} {'Estado':<12} {'Directorio':<30}")
            print("-" * 120)
            
            for reporte in reportes_filtrados:
                print(f"{reporte['id']:<25} {reporte['tipo']:<15} {reporte['titulo'][:30]:<30} {reporte['creado'][:19]:<20} {reporte['estado']:<12} {Path(reporte['directorio']).name:<30}")
            
            return reportes_filtrados
            
        except Exception as e:
            print_error(f"Error listando reportes: {e}")
            return []
    
    def exportar_reporte(self, reporte_id, formato='json', archivo_salida=None):
        """Exportar reporte"""
        try:
            print_info(f"Exportando reporte: {reporte_id}")
            
            # Buscar reporte
            reporte = next((r for r in self.reportes if r['id'] == reporte_id), None)
            if not reporte:
                print_error(f"Reporte {reporte_id} no encontrado")
                return False
            
            # Determinar archivo de salida
            if archivo_salida is None:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                archivo_salida = f"reporte_{reporte_id}_{timestamp}.{formato}"
            
            archivo_salida = Path(archivo_salida)
            
            # Exportar según formato
            if formato == 'json':
                # Copiar archivo de datos
                datos_file = Path(reporte['directorio']) / 'datos.json'
                if datos_file.exists():
                    shutil.copy2(datos_file, archivo_salida)
                else:
                    print_error("Archivo de datos no encontrado")
                    return False
            
            elif formato == 'csv':
                # Convertir a CSV
                datos_file = Path(reporte['directorio']) / 'datos.json'
                if datos_file.exists():
                    with open(datos_file, 'r', encoding='utf-8') as f:
                        datos = json.load(f)
                    
                    if isinstance(datos, dict):
                        df = pd.DataFrame([datos])
                    elif isinstance(datos, list):
                        df = pd.DataFrame(datos)
                    else:
                        print_error("Formato de datos no soportado para CSV")
                        return False
                    
                    df.to_csv(archivo_salida, index=False)
                else:
                    print_error("Archivo de datos no encontrado")
                    return False
            
            elif formato == 'xlsx':
                # Convertir a XLSX
                datos_file = Path(reporte['directorio']) / 'datos.json'
                if datos_file.exists():
                    with open(datos_file, 'r', encoding='utf-8') as f:
                        datos = json.load(f)
                    
                    if isinstance(datos, dict):
                        df = pd.DataFrame([datos])
                    elif isinstance(datos, list):
                        df = pd.DataFrame(datos)
                    else:
                        print_error("Formato de datos no soportado para XLSX")
                        return False
                    
                    df.to_excel(archivo_salida, index=False)
                else:
                    print_error("Archivo de datos no encontrado")
                    return False
            
            else:
                print_error(f"Formato no soportado: {formato}")
                return False
            
            print_success(f"Reporte exportado: {archivo_salida}")
            return True
            
        except Exception as e:
            print_error(f"Error exportando reporte: {e}")
            return False
    
    def eliminar_reporte(self, reporte_id):
        """Eliminar reporte"""
        try:
            print_info(f"Eliminando reporte: {reporte_id}")
            
            # Buscar reporte
            reporte = next((r for r in self.reportes if r['id'] == reporte_id), None)
            if not reporte:
                print_error(f"Reporte {reporte_id} no encontrado")
                return False
            
            # Eliminar directorio
            directorio_reporte = Path(reporte['directorio'])
            if directorio_reporte.exists():
                shutil.rmtree(directorio_reporte)
                print_success(f"Directorio {directorio_reporte} eliminado")
            
            # Remover de lista
            self.reportes = [r for r in self.reportes if r['id'] != reporte_id]
            
            # Guardar reportes
            self.guardar_reportes()
            
            print_success(f"Reporte {reporte_id} eliminado correctamente")
            return True
            
        except Exception as e:
            print_error(f"Error eliminando reporte: {e}")
            return False
    
    def guardar_reportes(self):
        """Guardar reportes en archivo"""
        try:
            archivo_reportes = Path(self.configuracion['archivo_reportes'])
            with open(archivo_reportes, 'w', encoding='utf-8') as f:
                json.dump(self.reportes, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            print_error(f"Error guardando reportes: {e}")
            return False
    
    def cargar_reportes(self):
        """Cargar reportes desde archivo"""
        try:
            archivo_reportes = Path(self.configuracion['archivo_reportes'])
            if archivo_reportes.exists():
                with open(archivo_reportes, 'r', encoding='utf-8') as f:
                    self.reportes = json.load(f)
                
                print_success(f"Reportes cargados: {len(self.reportes)}")
                return True
            else:
                print_warning("Archivo de reportes no encontrado")
                return False
            
        except Exception as e:
            print_error(f"Error cargando reportes: {e}")
            return False
    
    def generar_reporte_reportes(self):
        """Generar reporte de reportes"""
        try:
            print_info("Generando reporte de reportes...")
            
            # Crear reporte
            reporte = {
                'timestamp': datetime.now().isoformat(),
                'sistema': 'METGO 3D - Sistema Meteorológico Agrícola Quillota',
                'version': '2.0',
                'reportes': {
                    'total': len(self.reportes),
                    'por_tipo': {},
                    'por_estado': {},
                    'mas_reciente': max([r['creado'] for r in self.reportes]) if self.reportes else None
                },
                'detalles': self.reportes
            }
            
            # Contar por tipo
            for tipo in self.tipos_reportes:
                count = len([r for r in self.reportes if r['tipo'] == tipo])
                reporte['reportes']['por_tipo'][tipo] = count
            
            # Contar por estado
            estados = set(r['estado'] for r in self.reportes)
            for estado in estados:
                count = len([r for r in self.reportes if r['estado'] == estado])
                reporte['reportes']['por_estado'][estado] = count
            
            # Guardar reporte
            reportes_dir = Path("reportes")
            reportes_dir.mkdir(exist_ok=True)
            
            reporte_file = reportes_dir / f"reportes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(reporte_file, 'w', encoding='utf-8') as f:
                json.dump(reporte, f, indent=2, ensure_ascii=False)
            
            print_success(f"Reporte de reportes generado: {reporte_file}")
            
            # Mostrar resumen
            print(f"\n📊 Resumen de reportes:")
            print(f"Total: {reporte['reportes']['total']}")
            print(f"Por tipo: {reporte['reportes']['por_tipo']}")
            print(f"Por estado: {reporte['reportes']['por_estado']}")
            
            return str(reporte_file)
            
        except Exception as e:
            print_error(f"Error generando reporte: {e}")
            return None

def mostrar_menu():
    """Mostrar menú de gestión de reportes"""
    print("\n" + "=" * 70)
    print("📋 MENÚ DE GESTIÓN DE REPORTES - METGO 3D")
    print("=" * 70)
    
    print("\n1. 🔍 Cargar configuración")
    print("2. 📁 Crear estructura de reportes")
    print("3. 📝 Crear reporte")
    print("4. 📋 Listar reportes")
    print("5. 📤 Exportar reporte")
    print("6. ❌ Eliminar reporte")
    print("7. 💾 Cargar reportes")
    print("8. 📊 Generar reporte")
    print("9. ❌ Salir")
    
    print("\n" + "=" * 70)

def main():
    """Función principal de gestión de reportes"""
    print_header()
    
    # Crear gestor de reportes
    gestor = GestorReportes()
    
    while True:
        mostrar_menu()
        
        try:
            opcion = input("\n🔢 Selecciona una opción (1-9): ").strip()
            
            if opcion == "1":
                print_step("1", "Cargando configuración")
                if gestor.cargar_configuracion():
                    print_success("Configuración cargada correctamente")
                else:
                    print_error("Error cargando configuración")
                input("\n⏸️ Presiona Enter para continuar...")
            
            elif opcion == "2":
                print_step("2", "Creando estructura de reportes")
                if gestor.crear_estructura_reportes():
                    print_success("Estructura de reportes creada correctamente")
                else:
                    print_error("Error creando estructura")
                input("\n⏸️ Presiona Enter para continuar...")
            
            elif opcion == "3":
                print_step("3", "Creando reporte")
                try:
                    tipo = input(f"Tipo de reporte ({', '.join(gestor.tipos_reportes)}): ").strip()
                    titulo = input("Título: ").strip()
                    datos = input("Datos (JSON): ").strip()
                    opciones = input("Opciones (JSON opcional): ").strip()
                    
                    try:
                        datos = json.loads(datos)
                        opciones = json.loads(opciones) if opciones else None
                        
                        reporte_id = gestor.crear_reporte(tipo, titulo, datos, opciones)
                        if reporte_id:
                            print_success(f"Reporte creado: {reporte_id}")
                        else:
                            print_error("Error creando reporte")
                    except json.JSONDecodeError:
                        print_error("Datos u opciones no válidos")
                except Exception as e:
                    print_error(f"Error: {e}")
                input("\n⏸️ Presiona Enter para continuar...")
            
            elif opcion == "4":
                print_step("4", "Listando reportes")
                try:
                    tipo = input("Tipo (opcional): ").strip() or None
                    reportes = gestor.listar_reportes(tipo)
                    if reportes:
                        print_success(f"Reportes listados: {len(reportes)}")
                    else:
                        print_warning("No hay reportes para mostrar")
                except Exception as e:
                    print_error(f"Error: {e}")
                input("\n⏸️ Presiona Enter para continuar...")
            
            elif opcion == "5":
                print_step("5", "Exportando reporte")
                try:
                    reporte_id = input("ID del reporte: ").strip()
                    formato = input("Formato (json/csv/xlsx, default json): ").strip() or "json"
                    archivo_salida = input("Archivo de salida (opcional): ").strip() or None
                    
                    if gestor.exportar_reporte(reporte_id, formato, archivo_salida):
                        print_success("Reporte exportado correctamente")
                    else:
                        print_error("Error exportando reporte")
                except Exception as e:
                    print_error(f"Error: {e}")
                input("\n⏸️ Presiona Enter para continuar...")
            
            elif opcion == "6":
                print_step("6", "Eliminando reporte")
                try:
                    reporte_id = input("ID del reporte: ").strip()
                    
                    if gestor.eliminar_reporte(reporte_id):
                        print_success("Reporte eliminado correctamente")
                    else:
                        print_error("Error eliminando reporte")
                except Exception as e:
                    print_error(f"Error: {e}")
                input("\n⏸️ Presiona Enter para continuar...")
            
            elif opcion == "7":
                print_step("7", "Cargando reportes")
                if gestor.cargar_reportes():
                    print_success("Reportes cargados correctamente")
                else:
                    print_error("Error cargando reportes")
                input("\n⏸️ Presiona Enter para continuar...")
            
            elif opcion == "8":
                print_step("8", "Generando reporte de reportes")
                reporte = gestor.generar_reporte_reportes()
                if reporte:
                    print_success(f"Reporte generado: {reporte}")
                else:
                    print_error("Error generando reporte")
                input("\n⏸️ Presiona Enter para continuar...")
            
            elif opcion == "9":
                print_info("Saliendo del gestor de reportes...")
                print_success("¡Hasta luego! 🌾")
                break
            
            else:
                print_warning("Opción no válida. Selecciona 1-9.")
                time.sleep(1)
        
        except KeyboardInterrupt:
            print("\n⚠️ Gestión de reportes interrumpida por el usuario")
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