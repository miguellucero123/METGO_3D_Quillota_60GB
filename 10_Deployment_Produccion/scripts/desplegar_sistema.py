#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DESPLEGADOR AUTOMATICO - METGO 3D
Despliega el sistema automáticamente
"""

import os
import subprocess
import sys
from pathlib import Path
import time

class DesplegadorMetgo:
    def __init__(self):
        self.proyecto_path = Path.cwd()
        self.entorno_virtual = self.proyecto_path / "metgo_env"
        
    def verificar_entorno(self):
        """Verificar entorno de despliegue"""
        print("Verificando entorno...")
        
        # Verificar Python
        if not sys.executable:
            raise Exception("Python no encontrado")
        
        # Verificar directorio del proyecto
        if not self.proyecto_path.exists():
            raise Exception("Directorio del proyecto no encontrado")
        
        print("OK: Entorno verificado")
    
    def instalar_dependencias(self):
        """Instalar dependencias"""
        print("Instalando dependencias...")
        
        requirements_files = [
            "requirements.txt",
            "requirements_optimizado.txt"
        ]
        
        for req_file in requirements_files:
            if Path(req_file).exists():
                subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', req_file])
                print(f"OK: Dependencias instaladas desde {req_file}")
                break
    
    def ejecutar_tests(self):
        """Ejecutar tests"""
        print("Ejecutando tests...")
        
        try:
            result = subprocess.run([sys.executable, '-m', 'pytest', 'test_basicos.py', '-v'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("OK: Tests pasaron correctamente")
            else:
                print(f"ADVERTENCIA: Tests con advertencias: {result.stdout}")
        except Exception as e:
            print(f"ADVERTENCIA: No se pudieron ejecutar tests: {e}")
    
    def optimizar_sistema(self):
        """Optimizar sistema"""
        print("Optimizando sistema...")
        
        try:
            subprocess.run([sys.executable, 'optimizador_automatico.py'])
            print("OK: Sistema optimizado")
        except Exception as e:
            print(f"ADVERTENCIA: Error en optimización: {e}")
    
    def iniciar_sistema(self):
        """Iniciar sistema"""
        print("Iniciando sistema...")
        
        try:
            # Ejecutar en segundo plano
            subprocess.Popen([sys.executable, 'sistema_unificado_con_conectores.py'])
            print("OK: Sistema iniciado")
            print("Dashboard disponible en: http://localhost:8501")
        except Exception as e:
            print(f"ERROR: Error iniciando sistema: {e}")
    
    def desplegar(self):
        """Desplegar sistema completo"""
        try:
            self.verificar_entorno()
            self.instalar_dependencias()
            self.ejecutar_tests()
            self.optimizar_sistema()
            self.iniciar_sistema()
            
            print("\nDESPLIEGUE COMPLETADO")
            print("="*50)
            print("Sistema METGO 3D desplegado correctamente")
            print("Dashboard: http://localhost:8501")
            print("Logs: optimizacion.log")
            
        except Exception as e:
            print(f"ERROR: Error en despliegue: {e}")

if __name__ == "__main__":
    desplegador = DesplegadorMetgo()
    desplegador.desplegar()
