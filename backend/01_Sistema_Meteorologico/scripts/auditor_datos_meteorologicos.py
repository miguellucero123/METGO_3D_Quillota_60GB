#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Auditor de Datos Meteorológicos METGO 3D
Script para auditar y identificar problemas en los datos existentes
"""

import sqlite3
import pandas as pd
import numpy as np
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
import logging

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AuditorDatosMeteorologicos:
    """Auditor completo para datos meteorológicos"""
    
    def __init__(self):
        self.resultados_auditoria = {}
        self.problemas_encontrados = []
        self.recomendaciones = []
        
    def ejecutar_auditoria_completa(self):
        """Ejecutar auditoría completa del sistema de datos"""
        print("INICIANDO AUDITORIA COMPLETA DE DATOS METEOROLOGICOS")
        print("=" * 70)
        
        # 1. Auditar bases de datos
        self._auditar_bases_datos()
        
        # 2. Auditar archivos JSON
        self._auditar_archivos_json()
        
        # 3. Auditar configuración de APIs
        self._auditar_configuracion_apis()
        
        # 4. Auditar estructura de archivos
        self._auditar_estructura_archivos()
        
        # 5. Generar reporte
        self._generar_reporte_auditoria()
        
        return self.resultados_auditoria
    
    def _auditar_bases_datos(self):
        """Auditar bases de datos SQLite"""
        print("\nAUDITANDO BASES DE DATOS...")
        
        bases_datos = [
            "scripts/datos_meteorologicos.db",
            "scripts/datos_meteorologicos_reales.db",
            "datos/datos_meteorologicos.db",
            "data/datos_meteorologicos.db"
        ]
        
        for db_path in bases_datos:
            if os.path.exists(db_path):
                print(f"\n🗄️ Analizando: {db_path}")
                self._analizar_base_datos(db_path)
            else:
                print(f"❌ No encontrada: {db_path}")
    
    def _analizar_base_datos(self, db_path):
        """Analizar una base de datos específica"""
        try:
            conn = sqlite3.connect(db_path)
            
            # Obtener información de tablas
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tablas = [row[0] for row in cursor.fetchall()]
            
            print(f"   📋 Tablas encontradas: {tablas}")
            
            for tabla in tablas:
                if 'meteorologico' in tabla.lower() or 'datos' in tabla.lower():
                    self._analizar_tabla_datos(conn, tabla, db_path)
            
            conn.close()
            
        except Exception as e:
            print(f"   ❌ Error analizando {db_path}: {e}")
            self.problemas_encontrados.append(f"Error en BD {db_path}: {e}")
    
    def _analizar_tabla_datos(self, conn, tabla, db_path):
        """Analizar tabla específica de datos meteorológicos"""
        try:
            # Información básica
            cursor = conn.cursor()
            cursor.execute(f"SELECT COUNT(*) FROM {tabla}")
            total_registros = cursor.fetchone()[0]
            
            print(f"      📊 Tabla '{tabla}': {total_registros} registros")
            
            if total_registros == 0:
                self.problemas_encontrados.append(f"Tabla {tabla} en {db_path} está vacía")
                return
            
            # Estructura de la tabla
            cursor.execute(f"PRAGMA table_info({tabla})")
            columnas = cursor.fetchall()
            print(f"      📋 Columnas: {len(columnas)}")
            
            for col in columnas:
                print(f"         - {col[1]} ({col[2]})")
            
            # Análisis de datos
            df = pd.read_sql_query(f"SELECT * FROM {tabla} LIMIT 1000", conn)
            
            # Verificar campos críticos
            campos_criticos = ['fecha', 'temperatura', 'precipitacion', 'humedad']
            campos_faltantes = [campo for campo in campos_criticos 
                              if not any(campo in col.lower() for col in df.columns)]
            
            if campos_faltantes:
                self.problemas_encontrados.append(
                    f"Campos críticos faltantes en {tabla}: {campos_faltantes}"
                )
            
            # Análisis de calidad
            self._analizar_calidad_datos(df, tabla, db_path)
            
        except Exception as e:
            print(f"      ❌ Error analizando tabla {tabla}: {e}")
            self.problemas_encontrados.append(f"Error en tabla {tabla}: {e}")
    
    def _analizar_calidad_datos(self, df, tabla, db_path):
        """Analizar calidad de los datos"""
        print(f"      🔍 Analizando calidad de datos...")
        
        # Valores nulos
        nulos_por_columna = df.isnull().sum()
        columnas_con_nulos = nulos_por_columna[nulos_por_columna > 0]
        
        if len(columnas_con_nulos) > 0:
            print(f"         ⚠️ Valores nulos encontrados:")
            for col, nulos in columnas_con_nulos.items():
                porcentaje = (nulos / len(df)) * 100
                print(f"            {col}: {nulos} ({porcentaje:.1f}%)")
                if porcentaje > 20:
                    self.problemas_encontrados.append(
                        f"Muchos valores nulos en {col} ({porcentaje:.1f}%) en {tabla}"
                    )
        
        # Valores duplicados
        duplicados = df.duplicated().sum()
        if duplicados > 0:
            print(f"         ⚠️ Registros duplicados: {duplicados}")
            self.problemas_encontrados.append(
                f"{duplicados} registros duplicados en {tabla}"
            )
        
        # Análisis de rangos (si hay columnas numéricas)
        columnas_numericas = df.select_dtypes(include=[np.number]).columns
        for col in columnas_numericas:
            if 'temperatura' in col.lower():
                valores_extremos = df[col][(df[col] < -50) | (df[col] > 50)]
                if len(valores_extremos) > 0:
                    self.problemas_encontrados.append(
                        f"Temperaturas extremas en {col}: {valores_extremos.tolist()[:5]}"
                    )
            
            elif 'precipitacion' in col.lower():
                valores_negativos = df[col][df[col] < 0]
                if len(valores_negativos) > 0:
                    self.problemas_encontrados.append(
                        f"Precipitación negativa en {col}: {valores_negativos.tolist()[:5]}"
                    )
    
    def _auditar_archivos_json(self):
        """Auditar archivos JSON de datos"""
        print("\n📄 AUDITANDO ARCHIVOS JSON...")
        
        archivos_json = [
            "scripts/datos_meteorologicos_actualizados.json",
            "scripts/api_keys_meteorologicas.json"
        ]
        
        for json_path in archivos_json:
            if os.path.exists(json_path):
                print(f"\n📋 Analizando: {json_path}")
                self._analizar_archivo_json(json_path)
            else:
                print(f"❌ No encontrado: {json_path}")
    
    def _analizar_archivo_json(self, json_path):
        """Analizar archivo JSON específico"""
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if 'datos_meteorologicos' in json_path:
                # Analizar datos meteorológicos
                if isinstance(data, list) and len(data) > 0:
                    print(f"   📊 Registros JSON: {len(data)}")
                    
                    # Verificar estructura del primer registro
                    primer_registro = data[0]
                    print(f"   📋 Campos: {list(primer_registro.keys())}")
                    
                    # Verificar consistencia
                    campos_unicos = set()
                    for registro in data:
                        campos_unicos.update(registro.keys())
                    
                    if len(campos_unicos) > len(primer_registro):
                        self.problemas_encontrados.append(
                            f"Inconsistencia en campos JSON en {json_path}"
                        )
                else:
                    self.problemas_encontrados.append(
                        f"Archivo JSON vacío o mal formateado: {json_path}"
                    )
            
            elif 'api_keys' in json_path:
                # Analizar configuración de APIs
                print(f"   🔑 APIs configuradas: {len(data)}")
                apis_activas = [k for k, v in data.items() if isinstance(v, dict) and v.get('activa', False)]
                print(f"   ✅ APIs activas: {apis_activas}")
                
                if not apis_activas:
                    self.problemas_encontrados.append(
                        "Ninguna API meteorológica está activa"
                    )
        
        except Exception as e:
            print(f"   ❌ Error analizando {json_path}: {e}")
            self.problemas_encontrados.append(f"Error en JSON {json_path}: {e}")
    
    def _auditar_configuracion_apis(self):
        """Auditar configuración de APIs"""
        print("\n🔑 AUDITANDO CONFIGURACIÓN DE APIs...")
        
        api_config_path = "scripts/api_keys_meteorologicas.json"
        if os.path.exists(api_config_path):
            try:
                with open(api_config_path, 'r') as f:
                    config = json.load(f)
                
                print("   📋 APIs configuradas:")
                for api_name, api_config in config.items():
                    if isinstance(api_config, dict) and 'activa' in api_config:
                        estado = "✅ Activa" if api_config.get('activa', False) else "❌ Inactiva"
                        api_key = api_config.get('api_key', 'No configurada')
                        print(f"      {api_name}: {estado}")
                        if api_key == 'YOUR_API_KEY_HERE' or api_key is None:
                            self.problemas_encontrados.append(f"API {api_name} sin clave configurada")
                
                # Verificar configuración general
                config_general = config.get('configuracion', {})
                print(f"   ⚙️ Configuración general:")
                for key, value in config_general.items():
                    print(f"      {key}: {value}")
                    
            except Exception as e:
                print(f"   ❌ Error leyendo configuración: {e}")
                self.problemas_encontrados.append(f"Error en configuración de APIs: {e}")
        else:
            self.problemas_encontrados.append("Archivo de configuración de APIs no encontrado")
    
    def _auditar_estructura_archivos(self):
        """Auditar estructura de archivos y directorios"""
        print("\n📁 AUDITANDO ESTRUCTURA DE ARCHIVOS...")
        
        directorios_requeridos = [
            "scripts/",
            "datos/",
            "dashboards/",
            "notebooks/",
            "logs/"
        ]
        
        for directorio in directorios_requeridos:
            if os.path.exists(directorio):
                archivos = os.listdir(directorio)
                print(f"   📂 {directorio}: {len(archivos)} archivos")
                
                # Verificar archivos críticos
                if directorio == "scripts/":
                    archivos_criticos = [
                        "gestor_datos_meteorologicos.py",
                        "conector_apis_meteorologicas_reales.py",
                        "validador_datos_meteorologicos.py"
                    ]
                    for archivo in archivos_criticos:
                        if archivo in archivos:
                            print(f"      ✅ {archivo}")
                        else:
                            print(f"      ❌ {archivo} - FALTANTE")
                            self.problemas_encontrados.append(f"Archivo crítico faltante: {archivo}")
            else:
                print(f"   ❌ Directorio faltante: {directorio}")
                self.problemas_encontrados.append(f"Directorrio faltante: {directorio}")
    
    def _generar_reporte_auditoria(self):
        """Generar reporte final de auditoría"""
        print("\n📊 GENERANDO REPORTE DE AUDITORÍA")
        print("=" * 70)
        
        # Resumen de problemas
        print(f"\n🚨 PROBLEMAS ENCONTRADOS: {len(self.problemas_encontrados)}")
        if self.problemas_encontrados:
            for i, problema in enumerate(self.problemas_encontrados, 1):
                print(f"   {i}. {problema}")
        
        # Generar recomendaciones
        self._generar_recomendaciones()
        
        print(f"\n💡 RECOMENDACIONES: {len(self.recomendaciones)}")
        for i, recomendacion in enumerate(self.recomendaciones, 1):
            print(f"   {i}. {recomendacion}")
        
        # Guardar reporte
        self._guardar_reporte()
    
    def _generar_recomendaciones(self):
        """Generar recomendaciones basadas en los problemas encontrados"""
        
        if any("vacía" in problema for problema in self.problemas_encontrados):
            self.recomendaciones.append("Implementar sistema de recolección automática de datos")
        
        if any("nulos" in problema for problema in self.problemas_encontrados):
            self.recomendaciones.append("Implementar validación de datos en tiempo real")
        
        if any("duplicados" in problema for problema in self.problemas_encontrados):
            self.recomendaciones.append("Implementar sistema de deduplicación")
        
        if any("API" in problema for problema in self.problemas_encontrados):
            self.recomendaciones.append("Configurar APIs meteorológicas faltantes")
        
        if any("faltante" in problema for problema in self.problemas_encontrados):
            self.recomendaciones.append("Crear archivos y directorios faltantes")
        
        # Recomendaciones generales
        self.recomendaciones.extend([
            "Implementar esquema unificado de datos",
            "Crear sistema de backup automatizado",
            "Implementar monitoreo de calidad de datos",
            "Documentar procesos de gestión de datos"
        ])
    
    def _guardar_reporte(self):
        """Guardar reporte de auditoría"""
        reporte = {
            'fecha_auditoria': datetime.now().isoformat(),
            'problemas_encontrados': self.problemas_encontrados,
            'recomendaciones': self.recomendaciones,
            'total_problemas': len(self.problemas_encontrados),
            'total_recomendaciones': len(self.recomendaciones)
        }
        
        # Crear directorio de reportes si no existe
        os.makedirs('reportes', exist_ok=True)
        
        # Guardar reporte
        reporte_path = f"reportes/auditoria_datos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(reporte_path, 'w', encoding='utf-8') as f:
            json.dump(reporte, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Reporte guardado en: {reporte_path}")

def main():
    """Función principal"""
    auditor = AuditorDatosMeteorologicos()
    resultados = auditor.ejecutar_auditoria_completa()
    
    print("\n✅ AUDITORÍA COMPLETADA")
    print("=" * 70)
    
    return resultados

if __name__ == "__main__":
    main()
