"""
EJECUTAR MACHINE LEARNING AVANZADO - METGO 3D QUILLOTA
Script para ejecutar el sistema de ML avanzado
"""

import subprocess
import sys
import os
import time
from datetime import datetime

def verificar_dependencias():
    """Verificar que las dependencias estén instaladas"""
    dependencias = [
        'streamlit', 'pandas', 'numpy', 'plotly', 
        'scikit-learn', 'joblib', 'sqlite3'
    ]
    
    print("Verificando dependencias...")
    
    for dep in dependencias:
        try:
            if dep == 'sqlite3':
                import sqlite3
            else:
                __import__(dep)
            print(f"[OK] {dep}")
        except ImportError:
            print(f"[ERROR] {dep} no está instalado")
            return False
    
    return True

def entrenar_modelos_inicial():
    """Entrenar modelos iniciales"""
    print("\nEntrenando modelos iniciales...")
    
    try:
        from ml_avanzado_agricola import MLAvanzadoAgricola
        
        ml_sistema = MLAvanzadoAgricola()
        
        print("Generando datos históricos simulados...")
        df_historico = ml_sistema.generar_datos_historicos_simulados(5)
        print(f"[OK] Datos generados: {len(df_historico)} registros")
        
        print("Entrenando modelos avanzados...")
        resultados = ml_sistema.entrenar_modelos_avanzados('temperatura_promedio')
        
        if resultados:
            print(f"[OK] Modelos entrenados: {len(resultados)}")
            return True
        else:
            print("[ERROR] Error entrenando modelos")
            return False
            
    except Exception as e:
        print(f"[ERROR] Error en entrenamiento inicial: {e}")
        return False

def ejecutar_dashboard():
    """Ejecutar dashboard de ML avanzado"""
    print("\nIniciando dashboard ML avanzado...")
    
    try:
        # Verificar que el archivo existe
        if not os.path.exists('dashboard_ml_avanzado.py'):
            print("[ERROR] dashboard_ml_avanzado.py no encontrado")
            return False
        
        # Ejecutar Streamlit
        comando = [
            sys.executable, '-m', 'streamlit', 'run', 
            'dashboard_ml_avanzado.py',
            '--server.port', '8520',
            '--server.headless', 'true',
            '--browser.gatherUsageStats', 'false'
        ]
        
        print(f"[EJECUTANDO] Comando: {' '.join(comando)}")
        
        proceso = subprocess.Popen(comando)
        
        print("\n" + "="*80)
        print("DASHBOARD ML AVANZADO INICIADO")
        print("="*80)
        print(f"[FECHA] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"[URL] http://localhost:8520")
        print(f"[PID] {proceso.pid}")
        print("="*80)
        print("\nPresiona Ctrl+C para detener el dashboard...")
        
        # Esperar a que termine
        proceso.wait()
        
        return True
        
    except KeyboardInterrupt:
        print("\n[INFO] Dashboard detenido por el usuario")
        return True
    except Exception as e:
        print(f"[ERROR] Error ejecutando dashboard: {e}")
        return False

def ejecutar_pruebas_ml():
    """Ejecutar pruebas del sistema ML"""
    print("\nEjecutando pruebas del sistema ML...")
    
    try:
        from ml_avanzado_agricola import MLAvanzadoAgricola
        
        ml_sistema = MLAvanzadoAgricola()
        
        print("1. Probando predicciones de heladas...")
        heladas = ml_sistema.predecir_heladas_7_dias('quillota_centro')
        print(f"   [OK] Predicciones generadas: {len(heladas)}")
        
        print("2. Probando optimización de cosecha...")
        cosecha = ml_sistema.optimizar_fechas_cosecha('paltos')
        print(f"   [OK] Optimización completada: {cosecha.get('fecha_optima', 'N/A')}")
        
        print("3. Probando detección de plagas...")
        plagas = ml_sistema.detectar_patrones_plagas('paltos')
        print(f"   [OK] Alertas detectadas: {len(plagas)}")
        
        print("4. Generando reporte...")
        reporte = ml_sistema.generar_reporte_ml_avanzado()
        print(f"   [OK] Reporte generado: {reporte.get('modelos_entrenados', 0)} modelos")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Error en pruebas: {e}")
        return False

def mostrar_menu():
    """Mostrar menú de opciones"""
    print("\n" + "="*80)
    print("MACHINE LEARNING AVANZADO - METGO 3D QUILLOTA")
    print("="*80)
    print("1. Entrenar Modelos Iniciales")
    print("2. Ejecutar Dashboard ML")
    print("3. Ejecutar Pruebas del Sistema")
    print("4. Ejecutar Todo (Entrenar + Dashboard)")
    print("5. Salir")
    print("="*80)

def main():
    """Función principal"""
    try:
        # Verificar dependencias
        if not verificar_dependencias():
            print("\n[ERROR] Faltan dependencias. Instálalas con:")
            print("pip install streamlit pandas numpy plotly scikit-learn joblib")
            return
        
        while True:
            mostrar_menu()
            
            try:
                opcion = input("\nSelecciona una opción (1-5): ").strip()
                
                if opcion == '1':
                    if entrenar_modelos_inicial():
                        print("\n[OK] Entrenamiento completado exitosamente")
                    else:
                        print("\n[ERROR] Error en el entrenamiento")
                
                elif opcion == '2':
                    if ejecutar_dashboard():
                        print("\n[OK] Dashboard ejecutado exitosamente")
                    else:
                        print("\n[ERROR] Error ejecutando dashboard")
                
                elif opcion == '3':
                    if ejecutar_pruebas_ml():
                        print("\n[OK] Pruebas completadas exitosamente")
                    else:
                        print("\n[ERROR] Error en las pruebas")
                
                elif opcion == '4':
                    print("\n[EJECUTANDO] Proceso completo...")
                    
                    if entrenar_modelos_inicial():
                        print("\n[OK] Modelos entrenados")
                        
                        print("\n[INICIANDO] Dashboard...")
                        if ejecutar_dashboard():
                            print("\n[OK] Proceso completo finalizado")
                        else:
                            print("\n[ERROR] Error en dashboard")
                    else:
                        print("\n[ERROR] Error en entrenamiento")
                
                elif opcion == '5':
                    print("\n[INFO] Saliendo...")
                    break
                
                else:
                    print("\n[ERROR] Opción no válida")
                
                input("\nPresiona Enter para continuar...")
                
            except KeyboardInterrupt:
                print("\n\n[INFO] Operación cancelada por el usuario")
                break
            except Exception as e:
                print(f"\n[ERROR] Error inesperado: {e}")
    
    except Exception as e:
        print(f"[ERROR] Error crítico: {e}")

if __name__ == "__main__":
    main()
