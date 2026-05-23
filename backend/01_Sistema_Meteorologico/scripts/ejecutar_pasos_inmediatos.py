#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ejecutor de Próximos Pasos Inmediatos - METGO 3D
Script para ejecutar todos los pasos inmediatos de optimización de datos
"""

import os
import sys
import subprocess
import json
from datetime import datetime
from pathlib import Path
import logging

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class EjecutorPasosInmediatos:
    """Ejecutor de pasos inmediatos para optimización de datos"""
    
    def __init__(self):
        self.pasos_completados = []
        self.pasos_fallidos = []
        self.resultados = {}
        
        # Crear directorios necesarios
        self._crear_directorios()
    
    def _crear_directorios(self):
        """Crear directorios necesarios"""
        directorios = [
            'logs',
            'reportes',
            'alertas',
            'docs',
            'scripts/backups'
        ]
        
        for directorio in directorios:
            Path(directorio).mkdir(parents=True, exist_ok=True)
            logger.info(f"✅ Directorio creado/verificado: {directorio}")
    
    def ejecutar_todos_los_pasos(self):
        """Ejecutar todos los pasos inmediatos"""
        print("🚀 INICIANDO PRÓXIMOS PASOS INMEDIATOS - OPTIMIZACIÓN DE DATOS")
        print("=" * 80)
        
        pasos = [
            ("Paso 1: Auditar Datos Existentes", self._paso_1_auditar_datos),
            ("Paso 2: Crear Esquema Unificado", self._paso_2_esquema_unificado),
            ("Paso 3: Implementar Validaciones", self._paso_3_validaciones),
            ("Paso 4: Configurar Monitoreo", self._paso_4_monitoreo),
            ("Paso 5: Documentar Procesos", self._paso_5_documentacion)
        ]
        
        for nombre_paso, funcion_paso in pasos:
            print(f"\n{'='*20} {nombre_paso} {'='*20}")
            
            try:
                resultado = funcion_paso()
                if resultado['exito']:
                    self.pasos_completados.append(nombre_paso)
                    logger.info(f"✅ {nombre_paso} completado exitosamente")
                else:
                    self.pasos_fallidos.append(nombre_paso)
                    logger.error(f"❌ {nombre_paso} falló: {resultado['error']}")
                
                self.resultados[nombre_paso] = resultado
                
            except Exception as e:
                self.pasos_fallidos.append(nombre_paso)
                logger.error(f"❌ Error en {nombre_paso}: {e}")
                self.resultados[nombre_paso] = {
                    'exito': False,
                    'error': str(e)
                }
        
        # Generar reporte final
        self._generar_reporte_final()
    
    def _paso_1_auditar_datos(self):
        """Paso 1: Auditar datos existentes"""
        try:
            # Ejecutar auditor de datos
            resultado = subprocess.run([
                sys.executable, 
                'scripts/auditor_datos_meteorologicos.py'
            ], capture_output=True, text=True, cwd='.')
            
            if resultado.returncode == 0:
                logger.info("📊 Auditoría de datos completada")
                
                # Buscar archivo de reporte generado
                reportes = list(Path('reportes').glob('auditoria_datos_*.json'))
                if reportes:
                    reporte_mas_reciente = max(reportes, key=os.path.getctime)
                    
                    with open(reporte_mas_reciente, 'r', encoding='utf-8') as f:
                        datos_auditoria = json.load(f)
                    
                    return {
                        'exito': True,
                        'archivo_reporte': str(reporte_mas_reciente),
                        'problemas_encontrados': datos_auditoria.get('total_problemas', 0),
                        'recomendaciones': len(datos_auditoria.get('recomendaciones', [])),
                        'output': resultado.stdout
                    }
                else:
                    return {
                        'exito': True,
                        'mensaje': 'Auditoría completada pero no se encontró reporte'
                    }
            else:
                return {
                    'exito': False,
                    'error': f"Error en auditoría: {resultado.stderr}"
                }
                
        except Exception as e:
            return {
                'exito': False,
                'error': f"Error ejecutando auditoría: {e}"
            }
    
    def _paso_2_esquema_unificado(self):
        """Paso 2: Crear esquema unificado"""
        try:
            # Ejecutar esquema unificado
            resultado = subprocess.run([
                sys.executable, 
                'scripts/esquema_datos_unificado.py'
            ], capture_output=True, text=True, cwd='.')
            
            # Verificar que se creó el archivo JSON
            archivo_esquema = Path('scripts/esquema_datos_unificado.json')
            
            if archivo_esquema.exists():
                with open(archivo_esquema, 'r', encoding='utf-8') as f:
                    esquema = json.load(f)
                
                return {
                    'exito': True,
                    'archivo_esquema': str(archivo_esquema),
                    'version': esquema.get('configuracion', {}).get('version', '1.0.0'),
                    'campos_definidos': len(esquema.get('rangos_validos', {})),
                    'output': resultado.stdout
                }
            else:
                return {
                    'exito': False,
                    'error': 'Archivo de esquema no se generó correctamente'
                }
                
        except Exception as e:
            return {
                'exito': False,
                'error': f"Error creando esquema: {e}"
            }
    
    def _paso_3_validaciones(self):
        """Paso 3: Implementar validaciones"""
        try:
            # Ejecutar validador avanzado
            resultado = subprocess.run([
                sys.executable, 
                'scripts/validador_datos_avanzado.py'
            ], capture_output=True, text=True, cwd='.')
            
            if resultado.returncode == 0:
                logger.info("🛡️ Validaciones implementadas correctamente")
                
                return {
                    'exito': True,
                    'mensaje': 'Sistema de validaciones implementado',
                    'output': resultado.stdout
                }
            else:
                return {
                    'exito': False,
                    'error': f"Error en validaciones: {resultado.stderr}"
                }
                
        except Exception as e:
            return {
                'exito': False,
                'error': f"Error implementando validaciones: {e}"
            }
    
    def _paso_4_monitoreo(self):
        """Paso 4: Configurar monitoreo"""
        try:
            # Crear archivo de configuración de monitoreo
            config_monitor = {
                'intervalo_monitoreo_segundos': 300,
                'umbrales_alertas': {
                    'calidad_minima': 80.0,
                    'disponibilidad_minima': 95.0,
                    'latencia_maxima': 30.0,
                    'errores_maximos_por_hora': 10,
                    'campos_faltantes_maximos': 5
                },
                'fuentes_datos': [
                    'openmeteo',
                    'openweathermap',
                    'sensor_local',
                    'simulado'
                ],
                'campos_criticos': [
                    'temperatura_promedio',
                    'humedad_relativa',
                    'precipitacion_diaria',
                    'timestamp'
                ],
                'base_datos': 'scripts/datos_meteorologicos.db',
                'retencion_metricas_dias': 30,
                'retencion_alertas_dias': 7
            }
            
            with open('scripts/config_monitor_calidad.json', 'w', encoding='utf-8') as f:
                json.dump(config_monitor, f, indent=2, ensure_ascii=False)
            
            # Ejecutar monitor de calidad
            resultado = subprocess.run([
                sys.executable, 
                'scripts/monitor_calidad_datos.py'
            ], capture_output=True, text=True, cwd='.')
            
            logger.info("📊 Sistema de monitoreo configurado")
            
            return {
                'exito': True,
                'archivo_config': 'scripts/config_monitor_calidad.json',
                'mensaje': 'Sistema de monitoreo implementado',
                'output': resultado.stdout
            }
            
        except Exception as e:
            return {
                'exito': False,
                'error': f"Error configurando monitoreo: {e}"
            }
    
    def _paso_5_documentacion(self):
        """Paso 5: Documentar procesos"""
        try:
            # Verificar que la documentación se creó
            archivo_docs = Path('docs/procesos_gestion_datos.md')
            
            if archivo_docs.exists():
                # Obtener tamaño del archivo
                tamaño_archivo = archivo_docs.stat().st_size
                
                logger.info("📚 Documentación de procesos creada")
                
                return {
                    'exito': True,
                    'archivo_documentacion': str(archivo_docs),
                    'tamaño_bytes': tamaño_archivo,
                    'mensaje': 'Documentación de procesos generada'
                }
            else:
                return {
                    'exito': False,
                    'error': 'Archivo de documentación no encontrado'
                }
                
        except Exception as e:
            return {
                'exito': False,
                'error': f"Error verificando documentación: {e}"
            }
    
    def _generar_reporte_final(self):
        """Generar reporte final de ejecución"""
        print("\n" + "="*80)
        print("📊 REPORTE FINAL DE EJECUCIÓN")
        print("="*80)
        
        # Estadísticas generales
        total_pasos = len(self.pasos_completados) + len(self.pasos_fallidos)
        pasos_exitosos = len(self.pasos_completados)
        pasos_fallidos = len(self.pasos_fallidos)
        
        print(f"📈 Estadísticas Generales:")
        print(f"   Total de pasos: {total_pasos}")
        print(f"   Pasos exitosos: {pasos_exitosos}")
        print(f"   Pasos fallidos: {pasos_fallidos}")
        print(f"   Tasa de éxito: {(pasos_exitosos/total_pasos)*100:.1f}%")
        
        # Pasos completados
        if self.pasos_completados:
            print(f"\n✅ Pasos Completados Exitosamente:")
            for paso in self.pasos_completados:
                print(f"   - {paso}")
        
        # Pasos fallidos
        if self.pasos_fallidos:
            print(f"\n❌ Pasos Fallidos:")
            for paso in self.pasos_fallidos:
                print(f"   - {paso}")
                if paso in self.resultados:
                    print(f"     Error: {self.resultados[paso].get('error', 'No especificado')}")
        
        # Resumen de archivos creados
        print(f"\n📁 Archivos Creados/Modificados:")
        archivos_importantes = [
            'scripts/auditor_datos_meteorologicos.py',
            'scripts/esquema_datos_unificado.py',
            'scripts/validador_datos_avanzado.py',
            'scripts/monitor_calidad_datos.py',
            'scripts/config_monitor_calidad.json',
            'docs/procesos_gestion_datos.md'
        ]
        
        for archivo in archivos_importantes:
            if Path(archivo).exists():
                print(f"   ✅ {archivo}")
            else:
                print(f"   ❌ {archivo} (no encontrado)")
        
        # Próximos pasos recomendados
        print(f"\n🚀 Próximos Pasos Recomendados:")
        recomendaciones = [
            "Ejecutar auditoría de datos: python scripts/auditor_datos_meteorologicos.py",
            "Probar validaciones: python scripts/validador_datos_avanzado.py",
            "Iniciar monitoreo: python scripts/monitor_calidad_datos.py",
            "Revisar documentación: docs/procesos_gestion_datos.md",
            "Configurar APIs meteorológicas en api_keys_meteorologicas.json"
        ]
        
        for i, recomendacion in enumerate(recomendaciones, 1):
            print(f"   {i}. {recomendacion}")
        
        # Guardar reporte en archivo
        reporte_final = {
            'fecha_ejecucion': datetime.now().isoformat(),
            'estadisticas': {
                'total_pasos': total_pasos,
                'pasos_exitosos': pasos_exitosos,
                'pasos_fallidos': pasos_fallidos,
                'tasa_exito': round((pasos_exitosos/total_pasos)*100, 1)
            },
            'pasos_completados': self.pasos_completados,
            'pasos_fallidos': self.pasos_fallidos,
            'resultados_detallados': self.resultados,
            'archivos_creados': archivos_importantes,
            'recomendaciones': recomendaciones
        }
        
        archivo_reporte = f"reportes/ejecucion_pasos_inmediatos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(archivo_reporte, 'w', encoding='utf-8') as f:
            json.dump(reporte_final, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Reporte guardado en: {archivo_reporte}")
        print("\n✅ EJECUCIÓN DE PRÓXIMOS PASOS INMEDIATOS COMPLETADA")

def main():
    """Función principal"""
    ejecutor = EjecutorPasosInmediatos()
    ejecutor.ejecutar_todos_los_pasos()

if __name__ == "__main__":
    main()

