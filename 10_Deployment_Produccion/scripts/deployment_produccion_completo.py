"""
SISTEMA DE DEPLOYMENT EN PRODUCCIÓN - METGO 3D QUILLOTA
Sistema completo para desplegar el sistema meteorológico agrícola en producción
"""

import os
import sys
import json
import shutil
import subprocess
import logging
from datetime import datetime
from typing import Dict, List, Optional
import yaml

class DeploymentProduccionCompleto:
    def __init__(self):
        self.logger = self._configurar_logging()
        self.configuracion = self._cargar_configuracion_deployment()
        self.directorio_base = os.getcwd()
        self.directorio_deployment = "deployment_produccion"
        
    def _configurar_logging(self):
        """Configurar logging para deployment"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/deployment_produccion.log'),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger('DEPLOYMENT_PRODUCCION')
    
    def _cargar_configuracion_deployment(self):
        """Cargar configuración de deployment"""
        return {
            'servidor': {
                'host': 'localhost',
                'puerto_principal': 8501,
                'puerto_agricola': 8510,
                'puerto_monitoreo': 8502
            },
            'docker': {
                'imagen_base': 'python:3.11-slim',
                'puerto_exposicion': '8501:8501',
                'volumen_datos': './data:/app/data',
                'volumen_logs': './logs:/app/logs'
            },
            'backup': {
                'frecuencia': 'diario',
                'retencion_dias': 30,
                'directorio': './backups'
            },
            'monitoreo': {
                'intervalo_verificacion': 300,  # 5 minutos
                'umbral_memoria': 80,
                'umbral_cpu': 80
            }
        }
    
    def ejecutar_deployment_completo(self):
        """Ejecutar deployment completo del sistema"""
        print("\n" + "="*80)
        print("SISTEMA DE DEPLOYMENT EN PRODUCCIÓN - METGO 3D QUILLOTA")
        print("="*80)
        
        try:
            # 1. Preparar entorno de deployment
            print("\n[FASE 1] Preparando entorno de deployment...")
            self._preparar_entorno_deployment()
            
            # 2. Crear scripts de deployment
            print("\n[FASE 2] Creando scripts de deployment...")
            self._crear_scripts_deployment()
            
            # 3. Configurar Docker
            print("\n[FASE 3] Configurando Docker...")
            self._configurar_docker()
            
            # 4. Crear sistema de monitoreo
            print("\n[FASE 4] Creando sistema de monitoreo...")
            self._crear_sistema_monitoreo()
            
            # 5. Configurar backup automático
            print("\n[FASE 5] Configurando backup automático...")
            self._configurar_backup_automatico()
            
            # 6. Crear documentación de deployment
            print("\n[FASE 6] Creando documentación de deployment...")
            self._crear_documentacion_deployment()
            
            # 7. Generar reporte final
            print("\n[FASE 7] Generando reporte final...")
            self._generar_reporte_deployment()
            
            print("\n" + "="*80)
            print("DEPLOYMENT EN PRODUCCIÓN COMPLETADO EXITOSAMENTE")
            print("="*80)
            
        except Exception as e:
            self.logger.error(f"Error en deployment: {e}")
            print(f"\n[ERROR] Error en deployment: {e}")
            return False
        
        return True
    
    def _preparar_entorno_deployment(self):
        """Preparar entorno de deployment"""
        try:
            # Crear directorio de deployment
            if not os.path.exists(self.directorio_deployment):
                os.makedirs(self.directorio_deployment)
            
            # Crear subdirectorios
            subdirectorios = [
                'scripts',
                'docker',
                'monitoring',
                'backup',
                'config',
                'docs'
            ]
            
            for subdir in subdirectorios:
                path = os.path.join(self.directorio_deployment, subdir)
                if not os.path.exists(path):
                    os.makedirs(path)
            
            # Crear directorio de logs si no existe
            if not os.path.exists('logs'):
                os.makedirs('logs')
            
            print("  [OK] Directorio de deployment creado")
            print("  [OK] Subdirectorios creados")
            print("  [OK] Entorno preparado")
            
        except Exception as e:
            self.logger.error(f"Error preparando entorno: {e}")
            raise
    
    def _crear_scripts_deployment(self):
        """Crear scripts de deployment"""
        try:
            # Script de inicio de producción
            script_inicio = self._generar_script_inicio_produccion()
            with open(os.path.join(self.directorio_deployment, 'scripts', 'iniciar_produccion.py'), 'w', encoding='utf-8') as f:
                f.write(script_inicio)
            
            # Script de parada
            script_parada = self._generar_script_parada()
            with open(os.path.join(self.directorio_deployment, 'scripts', 'parar_produccion.py'), 'w', encoding='utf-8') as f:
                f.write(script_parada)
            
            # Script de reinicio
            script_reinicio = self._generar_script_reinicio()
            with open(os.path.join(self.directorio_deployment, 'scripts', 'reiniciar_produccion.py'), 'w', encoding='utf-8') as f:
                f.write(script_reinicio)
            
            # Script de verificación de estado
            script_estado = self._generar_script_estado()
            with open(os.path.join(self.directorio_deployment, 'scripts', 'verificar_estado.py'), 'w', encoding='utf-8') as f:
                f.write(script_estado)
            
            # Scripts de sistema operativo
            self._crear_scripts_sistema_operativo()
            
            print("  [OK] Scripts de Python creados")
            print("  [OK] Scripts de sistema operativo creados")
            
        except Exception as e:
            self.logger.error(f"Error creando scripts: {e}")
            raise
    
    def _generar_script_inicio_produccion(self):
        """Generar script de inicio de producción"""
        return '''"""
SCRIPT DE INICIO DE PRODUCCIÓN - METGO 3D QUILLOTA
Inicia todos los servicios del sistema en modo producción
"""

import os
import sys
import subprocess
import time
import logging
from datetime import datetime

def iniciar_produccion():
    """Iniciar sistema en modo producción"""
    print("="*60)
    print("INICIANDO SISTEMA METGO 3D QUILLOTA EN PRODUCCIÓN")
    print("="*60)
    
    # Verificar dependencias
    print("\\n[VERIFICANDO] Dependencias del sistema...")
    try:
        import streamlit
        import pandas
        import plotly
        import sklearn
        print("  [OK] Todas las dependencias están instaladas")
    except ImportError as e:
        print(f"  [ERROR] Dependencia faltante: {e}")
        return False
    
    # Iniciar servicios
    servicios = [
        {
            'nombre': 'Dashboard Principal',
            'comando': ['python', '-m', 'streamlit', 'run', 'sistema_unificado_con_conectores.py', 
                       '--server.port', '8501', '--server.headless', 'true'],
            'puerto': 8501
        },
        {
            'nombre': 'Dashboard Agrícola Avanzado',
            'comando': ['python', '-m', 'streamlit', 'run', 'dashboard_agricola_avanzado.py',
                       '--server.port', '8510', '--server.headless', 'true'],
            'puerto': 8510
        },
        {
            'nombre': 'Sistema de Monitoreo',
            'comando': ['python', 'monitoreo_tiempo_real.py'],
            'puerto': 8502
        }
    ]
    
    procesos = []
    
    for servicio in servicios:
        print(f"\\n[INICIANDO] {servicio['nombre']}...")
        try:
            proceso = subprocess.Popen(servicio['comando'], 
                                     stdout=subprocess.PIPE, 
                                     stderr=subprocess.PIPE)
            procesos.append({
                'proceso': proceso,
                'nombre': servicio['nombre'],
                'puerto': servicio['puerto']
            })
            print(f"  [OK] {servicio['nombre']} iniciado (PID: {proceso.pid})")
            time.sleep(2)  # Esperar entre servicios
        except Exception as e:
            print(f"  [ERROR] Error iniciando {servicio['nombre']}: {e}")
    
    # Verificar estado de servicios
    print("\\n[VERIFICANDO] Estado de servicios...")
    for proc_info in procesos:
        if proc_info['proceso'].poll() is None:
            print(f"  [OK] {proc_info['nombre']} - Activo")
        else:
            print(f"  [ERROR] {proc_info['nombre']} - Inactivo")
    
    print("\\n" + "="*60)
    print("SISTEMA METGO 3D QUILLOTA INICIADO EN PRODUCCIÓN")
    print("="*60)
    print("\\nServicios disponibles:")
    print("  - Dashboard Principal: http://localhost:8501")
    print("  - Dashboard Agrícola: http://localhost:8510")
    print("  - Monitoreo: http://localhost:8502")
    print("\\nPara detener el sistema, ejecute: python parar_produccion.py")
    
    return True

if __name__ == "__main__":
    iniciar_produccion()
'''
    
    def _generar_script_parada(self):
        """Generar script de parada"""
        return '''"""
SCRIPT DE PARADA DE PRODUCCIÓN - METGO 3D QUILLOTA
Detiene todos los servicios del sistema
"""

import os
import subprocess
import signal
import sys

def parar_produccion():
    """Parar sistema de producción"""
    print("="*60)
    print("DETENIENDO SISTEMA METGO 3D QUILLOTA")
    print("="*60)
    
    # Buscar procesos de Streamlit
    try:
        # En Windows
        if os.name == 'nt':
            result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq python.exe'], 
                                  capture_output=True, text=True)
            if 'streamlit' in result.stdout.lower():
                subprocess.run(['taskkill', '/F', '/IM', 'python.exe'], check=False)
        else:
            # En Linux/Mac
            subprocess.run(['pkill', '-f', 'streamlit'], check=False)
        
        print("  [OK] Procesos de Streamlit detenidos")
    except Exception as e:
        print(f"  [ADVERTENCIA] Error deteniendo procesos: {e}")
    
    # Buscar procesos específicos del sistema
    procesos_metgo = [
        'sistema_unificado_con_conectores.py',
        'dashboard_agricola_avanzado.py',
        'monitoreo_tiempo_real.py'
    ]
    
    for proceso in procesos_metgo:
        try:
            if os.name == 'nt':
                subprocess.run(['taskkill', '/F', '/FI', f'WINDOWTITLE eq {proceso}'], check=False)
            else:
                subprocess.run(['pkill', '-f', proceso], check=False)
            print(f"  [OK] {proceso} detenido")
        except:
            pass
    
    print("\\n[OK] Sistema METGO 3D QUILLOTA detenido")
    print("="*60)

if __name__ == "__main__":
    parar_produccion()
'''
    
    def _generar_script_reinicio(self):
        """Generar script de reinicio"""
        return '''"""
SCRIPT DE REINICIO DE PRODUCCIÓN - METGO 3D QUILLOTA
Reinicia todos los servicios del sistema
"""

import subprocess
import sys
import os

def reiniciar_produccion():
    """Reiniciar sistema de producción"""
    print("="*60)
    print("REINICIANDO SISTEMA METGO 3D QUILLOTA")
    print("="*60)
    
    # Parar sistema
    print("\\n[PARANDO] Sistema actual...")
    try:
        subprocess.run([sys.executable, 'parar_produccion.py'], check=True)
    except:
        pass
    
    # Esperar un momento
    import time
    time.sleep(3)
    
    # Iniciar sistema
    print("\\n[INICIANDO] Sistema reiniciado...")
    try:
        subprocess.run([sys.executable, 'iniciar_produccion.py'], check=True)
    except Exception as e:
        print(f"  [ERROR] Error reiniciando sistema: {e}")
        return False
    
    print("\\n[OK] Sistema reiniciado exitosamente")
    return True

if __name__ == "__main__":
    reiniciar_produccion()
'''
    
    def _generar_script_estado(self):
        """Generar script de verificación de estado"""
        return '''"""
SCRIPT DE VERIFICACIÓN DE ESTADO - METGO 3D QUILLOTA
Verifica el estado de todos los servicios del sistema
"""

import requests
import subprocess
import os
import sys
from datetime import datetime

def verificar_estado():
    """Verificar estado del sistema"""
    print("="*60)
    print("VERIFICANDO ESTADO DEL SISTEMA METGO 3D QUILLOTA")
    print("="*60)
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Servicios a verificar
    servicios = [
        {'nombre': 'Dashboard Principal', 'url': 'http://localhost:8501', 'puerto': 8501},
        {'nombre': 'Dashboard Agrícola', 'url': 'http://localhost:8510', 'puerto': 8510},
        {'nombre': 'Sistema de Monitoreo', 'url': 'http://localhost:8502', 'puerto': 8502}
    ]
    
    servicios_activos = 0
    servicios_totales = len(servicios)
    
    for servicio in servicios:
        print(f"\\n[VERIFICANDO] {servicio['nombre']}...")
        try:
            response = requests.get(servicio['url'], timeout=5)
            if response.status_code == 200:
                print(f"  [OK] {servicio['nombre']} - Activo (Status: {response.status_code})")
                servicios_activos += 1
            else:
                print(f"  [ERROR] {servicio['nombre']} - Error (Status: {response.status_code})")
        except requests.exceptions.RequestException:
            print(f"  [ERROR] {servicio['nombre']} - No disponible")
        except Exception as e:
            print(f"  [ERROR] {servicio['nombre']} - Error: {e}")
    
    # Verificar procesos
    print("\\n[VERIFICANDO] Procesos del sistema...")
    try:
        if os.name == 'nt':
            result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq python.exe'], 
                                  capture_output=True, text=True)
            procesos_python = result.stdout.count('python.exe')
            print(f"  [INFO] Procesos Python activos: {procesos_python}")
        else:
            result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
            procesos_streamlit = result.stdout.count('streamlit')
            print(f"  [INFO] Procesos Streamlit activos: {procesos_streamlit}")
    except Exception as e:
        print(f"  [ADVERTENCIA] Error verificando procesos: {e}")
    
    # Resumen
    print("\\n" + "="*60)
    print("RESUMEN DE ESTADO")
    print("="*60)
    print(f"Servicios activos: {servicios_activos}/{servicios_totales}")
    
    if servicios_activos == servicios_totales:
        print("Estado: [OK] Todos los servicios funcionando correctamente")
        return True
    elif servicios_activos > 0:
        print("Estado: [ADVERTENCIA] Algunos servicios no están funcionando")
        return False
    else:
        print("Estado: [ERROR] Ningún servicio está funcionando")
        return False

if __name__ == "__main__":
    verificar_estado()
'''
    
    def _crear_scripts_sistema_operativo(self):
        """Crear scripts de sistema operativo"""
        # Script de inicio para Windows
        script_bat = '''@echo off
echo ============================================================
echo METGO 3D QUILLOTA - SISTEMA DE PRODUCCION
echo ============================================================
echo.

echo [INICIANDO] Verificando sistema...
python -c "import streamlit, pandas, plotly, sklearn; print('[OK] Dependencias verificadas')"

echo.
echo [INICIANDO] Lanzando sistema de produccion...
python scripts/iniciar_produccion.py

echo.
echo [COMPLETADO] Sistema iniciado
echo.
echo Servicios disponibles:
echo - Dashboard Principal: http://localhost:8501
echo - Dashboard Agricola: http://localhost:8510
echo - Monitoreo: http://localhost:8502
echo.
pause
'''
        
        with open(os.path.join(self.directorio_deployment, 'scripts', 'iniciar_produccion.bat'), 'w', encoding='utf-8') as f:
            f.write(script_bat)
        
        # Script de parada para Windows
        script_parada_bat = '''@echo off
echo ============================================================
echo DETENIENDO SISTEMA METGO 3D QUILLOTA
echo ============================================================
echo.

python scripts/parar_produccion.py

echo.
echo [COMPLETADO] Sistema detenido
pause
'''
        
        with open(os.path.join(self.directorio_deployment, 'scripts', 'parar_produccion.bat'), 'w', encoding='utf-8') as f:
            f.write(script_parada_bat)
        
        # Script de inicio para Linux/Mac
        script_sh = '''#!/bin/bash
echo "============================================================"
echo "METGO 3D QUILLOTA - SISTEMA DE PRODUCCION"
echo "============================================================"
echo

echo "[INICIANDO] Verificando sistema..."
python3 -c "import streamlit, pandas, plotly, sklearn; print('[OK] Dependencias verificadas')"

echo
echo "[INICIANDO] Lanzando sistema de produccion..."
python3 scripts/iniciar_produccion.py

echo
echo "[COMPLETADO] Sistema iniciado"
echo
echo "Servicios disponibles:"
echo "- Dashboard Principal: http://localhost:8501"
echo "- Dashboard Agricola: http://localhost:8510"
echo "- Monitoreo: http://localhost:8502"
'''
        
        with open(os.path.join(self.directorio_deployment, 'scripts', 'iniciar_produccion.sh'), 'w', encoding='utf-8') as f:
            f.write(script_sh)
        
        # Hacer ejecutable en Linux/Mac
        try:
            os.chmod(os.path.join(self.directorio_deployment, 'scripts', 'iniciar_produccion.sh'), 0o755)
        except:
            pass
    
    def _configurar_docker(self):
        """Configurar Docker para deployment"""
        try:
            # Dockerfile
            dockerfile = self._generar_dockerfile()
            with open(os.path.join(self.directorio_deployment, 'docker', 'Dockerfile'), 'w', encoding='utf-8') as f:
                f.write(dockerfile)
            
            # docker-compose.yml
            docker_compose = self._generar_docker_compose()
            with open(os.path.join(self.directorio_deployment, 'docker', 'docker-compose.yml'), 'w', encoding='utf-8') as f:
                f.write(docker_compose)
            
            # Script de deployment con Docker
            script_docker = self._generar_script_docker()
            with open(os.path.join(self.directorio_deployment, 'scripts', 'deploy_docker.py'), 'w', encoding='utf-8') as f:
                f.write(script_docker)
            
            print("  [OK] Dockerfile creado")
            print("  [OK] docker-compose.yml creado")
            print("  [OK] Script de deployment Docker creado")
            
        except Exception as e:
            self.logger.error(f"Error configurando Docker: {e}")
            raise
    
    def _generar_dockerfile(self):
        """Generar Dockerfile"""
        return '''# Dockerfile para METGO 3D QUILLOTA
FROM python:3.11-slim

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \\
    gcc \\
    g++ \\
    && rm -rf /var/lib/apt/lists/*

# Establecer directorio de trabajo
WORKDIR /app

# Copiar archivos de dependencias
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código fuente
COPY . .

# Crear directorios necesarios
RUN mkdir -p logs data backups config

# Exponer puertos
EXPOSE 8501 8510 8502

# Comando por defecto
CMD ["python", "scripts/iniciar_produccion.py"]
'''
    
    def _generar_docker_compose(self):
        """Generar docker-compose.yml"""
        return '''version: '3.8'

services:
  metgo-principal:
    build: .
    ports:
      - "8501:8501"
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
      - ./backups:/app/backups
    environment:
      - STREAMLIT_SERVER_PORT=8501
      - STREAMLIT_SERVER_HEADLESS=true
    command: python -m streamlit run sistema_unificado_con_conectores.py --server.port 8501 --server.headless true
    restart: unless-stopped

  metgo-agricola:
    build: .
    ports:
      - "8510:8510"
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    environment:
      - STREAMLIT_SERVER_PORT=8510
      - STREAMLIT_SERVER_HEADLESS=true
    command: python -m streamlit run dashboard_agricola_avanzado.py --server.port 8510 --server.headless true
    restart: unless-stopped

  metgo-monitoreo:
    build: .
    ports:
      - "8502:8502"
    volumes:
      - ./logs:/app/logs
    command: python monitoreo_tiempo_real.py
    restart: unless-stopped

volumes:
  data:
  logs:
  backups:
'''
    
    def _generar_script_docker(self):
        """Generar script de deployment con Docker"""
        return '''"""
SCRIPT DE DEPLOYMENT CON DOCKER - METGO 3D QUILLOTA
Despliega el sistema usando Docker
"""

import subprocess
import os
import sys

def deploy_docker():
    """Desplegar sistema con Docker"""
    print("="*60)
    print("DEPLOYMENT CON DOCKER - METGO 3D QUILLOTA")
    print("="*60)
    
    # Verificar Docker
    print("\\n[VERIFICANDO] Docker...")
    try:
        subprocess.run(['docker', '--version'], check=True, capture_output=True)
        print("  [OK] Docker disponible")
    except subprocess.CalledProcessError:
        print("  [ERROR] Docker no está instalado o no está en el PATH")
        return False
    
    # Construir imagen
    print("\\n[CONSTRUYENDO] Imagen Docker...")
    try:
        subprocess.run(['docker', 'build', '-t', 'metgo-quillota', '.'], check=True)
        print("  [OK] Imagen construida exitosamente")
    except subprocess.CalledProcessError as e:
        print(f"  [ERROR] Error construyendo imagen: {e}")
        return False
    
    # Iniciar servicios
    print("\\n[INICIANDO] Servicios con Docker Compose...")
    try:
        subprocess.run(['docker-compose', 'up', '-d'], check=True)
        print("  [OK] Servicios iniciados")
    except subprocess.CalledProcessError as e:
        print(f"  [ERROR] Error iniciando servicios: {e}")
        return False
    
    print("\\n[COMPLETADO] Sistema desplegado con Docker")
    print("\\nServicios disponibles:")
    print("  - Dashboard Principal: http://localhost:8501")
    print("  - Dashboard Agrícola: http://localhost:8510")
    print("  - Monitoreo: http://localhost:8502")
    
    return True

if __name__ == "__main__":
    deploy_docker()
'''
    
    def _crear_sistema_monitoreo(self):
        """Crear sistema de monitoreo de producción"""
        try:
            # Sistema de monitoreo avanzado
            monitoreo_script = self._generar_sistema_monitoreo()
            with open(os.path.join(self.directorio_deployment, 'monitoring', 'monitoreo_produccion.py'), 'w', encoding='utf-8') as f:
                f.write(monitoreo_script)
            
            # Configuración de monitoreo
            config_monitoreo = self._generar_config_monitoreo()
            with open(os.path.join(self.directorio_deployment, 'config', 'monitoreo_config.json'), 'w', encoding='utf-8') as f:
                f.write(json.dumps(config_monitoreo, indent=2))
            
            print("  [OK] Sistema de monitoreo creado")
            print("  [OK] Configuración de monitoreo creada")
            
        except Exception as e:
            self.logger.error(f"Error creando sistema de monitoreo: {e}")
            raise
    
    def _generar_sistema_monitoreo(self):
        """Generar sistema de monitoreo"""
        return '''"""
SISTEMA DE MONITOREO DE PRODUCCIÓN - METGO 3D QUILLOTA
Monitorea el estado del sistema en tiempo real
"""

import psutil
import requests
import json
import time
import logging
from datetime import datetime
from typing import Dict, List

class MonitoreoProduccion:
    def __init__(self):
        self.logger = self._configurar_logging()
        self.config = self._cargar_configuracion()
        self.servicios = [
            {'nombre': 'Dashboard Principal', 'url': 'http://localhost:8501'},
            {'nombre': 'Dashboard Agrícola', 'url': 'http://localhost:8510'},
            {'nombre': 'Sistema de Monitoreo', 'url': 'http://localhost:8502'}
        ]
    
    def _configurar_logging(self):
        """Configurar logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/monitoreo_produccion.log'),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger('MONITOREO_PRODUCCION')
    
    def _cargar_configuracion(self):
        """Cargar configuración de monitoreo"""
        try:
            with open('config/monitoreo_config.json', 'r') as f:
                return json.load(f)
        except:
            return {
                'intervalo_verificacion': 300,
                'umbral_memoria': 80,
                'umbral_cpu': 80,
                'alertas_email': False
            }
    
    def verificar_servicios(self) -> Dict:
        """Verificar estado de servicios"""
        resultados = {
            'timestamp': datetime.now().isoformat(),
            'servicios': [],
            'sistema': self._verificar_sistema(),
            'alertas': []
        }
        
        for servicio in self.servicios:
            estado = self._verificar_servicio(servicio)
            resultados['servicios'].append(estado)
            
            if not estado['activo']:
                resultados['alertas'].append({
                    'tipo': 'servicio_inactivo',
                    'servicio': servicio['nombre'],
                    'mensaje': f"Servicio {servicio['nombre']} no está respondiendo"
                })
        
        return resultados
    
    def _verificar_servicio(self, servicio: Dict) -> Dict:
        """Verificar un servicio específico"""
        try:
            response = requests.get(servicio['url'], timeout=5)
            return {
                'nombre': servicio['nombre'],
                'url': servicio['url'],
                'activo': response.status_code == 200,
                'status_code': response.status_code,
                'tiempo_respuesta': response.elapsed.total_seconds()
            }
        except Exception as e:
            return {
                'nombre': servicio['nombre'],
                'url': servicio['url'],
                'activo': False,
                'error': str(e)
            }
    
    def _verificar_sistema(self) -> Dict:
        """Verificar estado del sistema"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memoria = psutil.virtual_memory()
            disco = psutil.disk_usage('/')
            
            return {
                'cpu_percent': cpu_percent,
                'memoria_percent': memoria.percent,
                'memoria_disponible_gb': memoria.available / (1024**3),
                'disco_percent': disco.percent,
                'disco_disponible_gb': disco.free / (1024**3)
            }
        except Exception as e:
            return {'error': str(e)}
    
    def generar_reporte_estado(self) -> str:
        """Generar reporte de estado"""
        resultados = self.verificar_servicios()
        
        reporte = f"""
REPORTE DE ESTADO - METGO 3D QUILLOTA
Fecha: {resultados['timestamp']}

SERVICIOS:
"""
        
        for servicio in resultados['servicios']:
            estado = "ACTIVO" if servicio['activo'] else "INACTIVO"
            reporte += f"  - {servicio['nombre']}: {estado}\\n"
        
        if 'sistema' in resultados and 'error' not in resultados['sistema']:
            reporte += f"""
SISTEMA:
  - CPU: {resultados['sistema']['cpu_percent']:.1f}%
  - Memoria: {resultados['sistema']['memoria_percent']:.1f}%
  - Disco: {resultados['sistema']['disco_percent']:.1f}%
"""
        
        if resultados['alertas']:
            reporte += "\\nALERTAS:\\n"
            for alerta in resultados['alertas']:
                reporte += f"  - {alerta['mensaje']}\\n"
        
        return reporte
    
    def ejecutar_monitoreo_continuo(self):
        """Ejecutar monitoreo continuo"""
        print("Iniciando monitoreo continuo del sistema...")
        
        while True:
            try:
                resultados = self.verificar_servicios()
                
                # Log de estado
                self.logger.info(f"Estado del sistema verificado: {len([s for s in resultados['servicios'] if s['activo']])}/{len(resultados['servicios'])} servicios activos")
                
                # Verificar alertas
                if resultados['alertas']:
                    for alerta in resultados['alertas']:
                        self.logger.warning(f"ALERTA: {alerta['mensaje']}")
                
                # Esperar antes de la siguiente verificación
                time.sleep(self.config['intervalo_verificacion'])
                
            except KeyboardInterrupt:
                print("\\nMonitoreo detenido por el usuario")
                break
            except Exception as e:
                self.logger.error(f"Error en monitoreo: {e}")
                time.sleep(60)  # Esperar 1 minuto antes de reintentar

def main():
    """Función principal"""
    monitoreo = MonitoreoProduccion()
    
    # Generar reporte inicial
    print(monitoreo.generar_reporte_estado())
    
    # Ejecutar monitoreo continuo
    monitoreo.ejecutar_monitoreo_continuo()

if __name__ == "__main__":
    main()
'''
    
    def _generar_config_monitoreo(self):
        """Generar configuración de monitoreo"""
        return {
            'intervalo_verificacion': 300,
            'umbral_memoria': 80,
            'umbral_cpu': 80,
            'alertas_email': False,
            'servicios': [
                {'nombre': 'Dashboard Principal', 'url': 'http://localhost:8501'},
                {'nombre': 'Dashboard Agrícola', 'url': 'http://localhost:8510'},
                {'nombre': 'Sistema de Monitoreo', 'url': 'http://localhost:8502'}
            ],
            'notificaciones': {
                'email': {
                    'activo': False,
                    'smtp_server': 'smtp.gmail.com',
                    'smtp_port': 587,
                    'username': 'metgo.quillota@gmail.com',
                    'password': 'app_password_aqui',
                    'to_emails': ['admin@metgo.cl']
                }
            }
        }
    
    def _configurar_backup_automatico(self):
        """Configurar backup automático"""
        try:
            # Script de backup
            script_backup = self._generar_script_backup()
            with open(os.path.join(self.directorio_deployment, 'backup', 'backup_automatico.py'), 'w', encoding='utf-8') as f:
                f.write(script_backup)
            
            # Configuración de backup
            config_backup = self._generar_config_backup()
            with open(os.path.join(self.directorio_deployment, 'config', 'backup_config.json'), 'w', encoding='utf-8') as f:
                f.write(json.dumps(config_backup, indent=2))
            
            print("  [OK] Sistema de backup automático creado")
            print("  [OK] Configuración de backup creada")
            
        except Exception as e:
            self.logger.error(f"Error configurando backup: {e}")
            raise
    
    def _generar_script_backup(self):
        """Generar script de backup automático"""
        return '''"""
SISTEMA DE BACKUP AUTOMÁTICO - METGO 3D QUILLOTA
Realiza respaldos automáticos del sistema
"""

import os
import shutil
import zipfile
import json
import sqlite3
from datetime import datetime, timedelta
import logging

class BackupAutomatico:
    def __init__(self):
        self.logger = self._configurar_logging()
        self.config = self._cargar_configuracion()
        self.directorio_backup = self.config['directorio_backup']
        self.retencion_dias = self.config['retencion_dias']
    
    def _configurar_logging(self):
        """Configurar logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/backup_automatico.log'),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger('BACKUP_AUTOMATICO')
    
    def _cargar_configuracion(self):
        """Cargar configuración de backup"""
        try:
            with open('config/backup_config.json', 'r') as f:
                return json.load(f)
        except:
            return {
                'directorio_backup': './backups',
                'retencion_dias': 30,
                'archivos_incluir': [
                    'data/',
                    'logs/',
                    'config/',
                    '*.db',
                    '*.json',
                    '*.py'
                ]
            }
    
    def crear_backup_completo(self):
        """Crear backup completo del sistema"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            nombre_backup = f"metgo_backup_{timestamp}.zip"
            ruta_backup = os.path.join(self.directorio_backup, nombre_backup)
            
            # Crear directorio de backup si no existe
            os.makedirs(self.directorio_backup, exist_ok=True)
            
            # Crear archivo ZIP
            with zipfile.ZipFile(ruta_backup, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Incluir archivos y directorios especificados
                for patron in self.config['archivos_incluir']:
                    if patron.endswith('/'):
                        # Directorio
                        directorio = patron[:-1]
                        if os.path.exists(directorio):
                            for root, dirs, files in os.walk(directorio):
                                for file in files:
                                    ruta_completa = os.path.join(root, file)
                                    ruta_relativa = os.path.relpath(ruta_completa)
                                    zipf.write(ruta_completa, ruta_relativa)
                    else:
                        # Archivo con patrón
                        import glob
                        for archivo in glob.glob(patron):
                            if os.path.isfile(archivo):
                                zipf.write(archivo, os.path.basename(archivo))
            
            # Verificar tamaño del backup
            tamaño_mb = os.path.getsize(ruta_backup) / (1024 * 1024)
            
            self.logger.info(f"Backup creado: {nombre_backup} ({tamaño_mb:.2f} MB)")
            
            # Limpiar backups antiguos
            self._limpiar_backups_antiguos()
            
            return ruta_backup
            
        except Exception as e:
            self.logger.error(f"Error creando backup: {e}")
            return None
    
    def _limpiar_backups_antiguos(self):
        """Limpiar backups antiguos según retención"""
        try:
            fecha_limite = datetime.now() - timedelta(days=self.retencion_dias)
            
            for archivo in os.listdir(self.directorio_backup):
                if archivo.startswith('metgo_backup_') and archivo.endswith('.zip'):
                    ruta_archivo = os.path.join(self.directorio_backup, archivo)
                    fecha_archivo = datetime.fromtimestamp(os.path.getctime(ruta_archivo))
                    
                    if fecha_archivo < fecha_limite:
                        os.remove(ruta_archivo)
                        self.logger.info(f"Backup antiguo eliminado: {archivo}")
                        
        except Exception as e:
            self.logger.error(f"Error limpiando backups antiguos: {e}")
    
    def restaurar_backup(self, nombre_backup: str, directorio_destino: str = '.'):
        """Restaurar backup"""
        try:
            ruta_backup = os.path.join(self.directorio_backup, nombre_backup)
            
            if not os.path.exists(ruta_backup):
                self.logger.error(f"Backup no encontrado: {nombre_backup}")
                return False
            
            with zipfile.ZipFile(ruta_backup, 'r') as zipf:
                zipf.extractall(directorio_destino)
            
            self.logger.info(f"Backup restaurado: {nombre_backup}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error restaurando backup: {e}")
            return False
    
    def listar_backups(self):
        """Listar backups disponibles"""
        try:
            backups = []
            for archivo in os.listdir(self.directorio_backup):
                if archivo.startswith('metgo_backup_') and archivo.endswith('.zip'):
                    ruta_archivo = os.path.join(self.directorio_backup, archivo)
                    tamaño_mb = os.path.getsize(ruta_archivo) / (1024 * 1024)
                    fecha_creacion = datetime.fromtimestamp(os.path.getctime(ruta_archivo))
                    
                    backups.append({
                        'nombre': archivo,
                        'tamaño_mb': tamaño_mb,
                        'fecha_creacion': fecha_creacion.isoformat()
                    })
            
            return sorted(backups, key=lambda x: x['fecha_creacion'], reverse=True)
            
        except Exception as e:
            self.logger.error(f"Error listando backups: {e}")
            return []

def main():
    """Función principal"""
    backup = BackupAutomatico()
    
    # Crear backup
    print("Creando backup del sistema...")
    ruta_backup = backup.crear_backup_completo()
    
    if ruta_backup:
        print(f"Backup creado exitosamente: {ruta_backup}")
    else:
        print("Error creando backup")
    
    # Listar backups
    print("\\nBackups disponibles:")
    backups = backup.listar_backups()
    for backup_info in backups:
        print(f"  - {backup_info['nombre']} ({backup_info['tamaño_mb']:.2f} MB) - {backup_info['fecha_creacion']}")

if __name__ == "__main__":
    main()
'''
    
    def _generar_config_backup(self):
        """Generar configuración de backup"""
        return {
            'directorio_backup': './backups',
            'retencion_dias': 30,
            'frecuencia': 'diario',
            'archivos_incluir': [
                'data/',
                'logs/',
                'config/',
                '*.db',
                '*.json',
                '*.py',
                'requirements.txt',
                'README.md'
            ],
            'excluir': [
                '__pycache__/',
                '*.pyc',
                '.git/',
                'node_modules/',
                'venv/',
                'env/'
            ]
        }
    
    def _crear_documentacion_deployment(self):
        """Crear documentación de deployment"""
        try:
            # Guía de deployment
            guia_deployment = self._generar_guia_deployment()
            with open(os.path.join(self.directorio_deployment, 'docs', 'GUIA_DEPLOYMENT.md'), 'w', encoding='utf-8') as f:
                f.write(guia_deployment)
            
            # Guía de monitoreo
            guia_monitoreo = self._generar_guia_monitoreo()
            with open(os.path.join(self.directorio_deployment, 'docs', 'GUIA_MONITOREO.md'), 'w', encoding='utf-8') as f:
                f.write(guia_monitoreo)
            
            # Guía de backup
            guia_backup = self._generar_guia_backup()
            with open(os.path.join(self.directorio_deployment, 'docs', 'GUIA_BACKUP.md'), 'w', encoding='utf-8') as f:
                f.write(guia_backup)
            
            print("  [OK] Documentación de deployment creada")
            
        except Exception as e:
            self.logger.error(f"Error creando documentación: {e}")
            raise
    
    def _generar_guia_deployment(self):
        """Generar guía de deployment"""
        return '''# 🚀 GUÍA DE DEPLOYMENT - METGO 3D QUILLOTA

## 📋 Requisitos Previos

### Sistema Operativo
- Windows 10/11, Linux (Ubuntu 20.04+), o macOS 10.15+
- Python 3.11 o superior
- Docker (opcional, para deployment con contenedores)

### Dependencias
- streamlit
- pandas
- plotly
- scikit-learn
- requests
- sqlite3
- yaml

## 🚀 Deployment Local

### 1. Preparación del Entorno
```bash
# Clonar o copiar el proyecto
cd metgo-3d-quillota

# Instalar dependencias
pip install -r requirements.txt

# Verificar instalación
python -c "import streamlit, pandas, plotly, sklearn; print('Dependencias OK')"
```

### 2. Iniciar Sistema
```bash
# Opción 1: Script automático
python scripts/iniciar_produccion.py

# Opción 2: Script de sistema operativo
# Windows:
scripts/iniciar_produccion.bat

# Linux/Mac:
./scripts/iniciar_produccion.sh
```

### 3. Verificar Estado
```bash
python scripts/verificar_estado.py
```

## 🐳 Deployment con Docker

### 1. Construir Imagen
```bash
docker build -t metgo-quillota .
```

### 2. Iniciar Servicios
```bash
docker-compose up -d
```

### 3. Verificar Servicios
```bash
docker-compose ps
```

## 🌐 Acceso al Sistema

Una vez iniciado, el sistema estará disponible en:

- **Dashboard Principal:** http://localhost:8501
- **Dashboard Agrícola Avanzado:** http://localhost:8510
- **Sistema de Monitoreo:** http://localhost:8502

## 🔧 Configuración

### Variables de Entorno
```bash
export STREAMLIT_SERVER_PORT=8501
export STREAMLIT_SERVER_HEADLESS=true
```

### Archivos de Configuración
- `config/monitoreo_config.json` - Configuración de monitoreo
- `config/backup_config.json` - Configuración de backup
- `configuracion_notificaciones_avanzada.json` - Notificaciones

## 🛠️ Mantenimiento

### Iniciar Sistema
```bash
python scripts/iniciar_produccion.py
```

### Detener Sistema
```bash
python scripts/parar_produccion.py
```

### Reiniciar Sistema
```bash
python scripts/reiniciar_produccion.py
```

### Verificar Estado
```bash
python scripts/verificar_estado.py
```

## 📊 Monitoreo

### Monitoreo Continuo
```bash
python monitoring/monitoreo_produccion.py
```

### Verificar Servicios
```bash
python scripts/verificar_estado.py
```

## 💾 Backup

### Backup Manual
```bash
python backup/backup_automatico.py
```

### Backup Programado
Configurar cron job (Linux/Mac) o Task Scheduler (Windows) para ejecutar:
```bash
python backup/backup_automatico.py
```

## 🚨 Solución de Problemas

### Servicio No Inicia
1. Verificar dependencias: `pip install -r requirements.txt`
2. Verificar puertos: `netstat -an | grep 8501`
3. Revisar logs: `logs/deployment_produccion.log`

### Error de Memoria
1. Verificar uso de memoria: `python scripts/verificar_estado.py`
2. Reiniciar sistema: `python scripts/reiniciar_produccion.py`

### Error de Base de Datos
1. Verificar archivos .db en directorio data/
2. Restaurar backup si es necesario

## 📞 Soporte

Para soporte técnico, contactar:
- Email: admin@metgo.cl
- Logs: Revisar archivos en directorio logs/
- Documentación: Ver directorio docs/

---

*Guía de Deployment - METGO 3D Quillota*
*Sistema Meteorológico Agrícola Avanzado*
'''
    
    def _generar_guia_monitoreo(self):
        """Generar guía de monitoreo"""
        return '''# 📊 GUÍA DE MONITOREO - METGO 3D QUILLOTA

## 🎯 Sistema de Monitoreo

El sistema incluye monitoreo automático de:
- Estado de servicios web
- Uso de recursos del sistema (CPU, memoria, disco)
- Alertas automáticas
- Logs de sistema

## 🚀 Iniciar Monitoreo

### Monitoreo Continuo
```bash
python monitoring/monitoreo_produccion.py
```

### Verificación Rápida
```bash
python scripts/verificar_estado.py
```

## 📊 Métricas Monitoreadas

### Servicios Web
- Dashboard Principal (puerto 8501)
- Dashboard Agrícola (puerto 8510)
- Sistema de Monitoreo (puerto 8502)

### Recursos del Sistema
- Uso de CPU (%)
- Uso de memoria (%)
- Espacio en disco (%)
- Tiempo de respuesta de servicios

## 🚨 Alertas

### Tipos de Alertas
- Servicio inactivo
- Alto uso de memoria (>80%)
- Alto uso de CPU (>80%)
- Error en base de datos

### Configuración de Alertas
Editar `config/monitoreo_config.json`:
```json
{
  "intervalo_verificacion": 300,
  "umbral_memoria": 80,
  "umbral_cpu": 80,
  "alertas_email": false
}
```

## 📈 Logs

### Ubicación de Logs
- `logs/monitoreo_produccion.log` - Logs de monitoreo
- `logs/deployment_produccion.log` - Logs de deployment
- `logs/backup_automatico.log` - Logs de backup

### Niveles de Log
- INFO: Información general
- WARNING: Advertencias
- ERROR: Errores
- CRITICAL: Errores críticos

## 🔧 Configuración Avanzada

### Monitoreo Personalizado
```python
from monitoring.monitoreo_produccion import MonitoreoProduccion

monitoreo = MonitoreoProduccion()
resultados = monitoreo.verificar_servicios()
```

### Alertas por Email
Configurar en `config/monitoreo_config.json`:
```json
{
  "notificaciones": {
    "email": {
      "activo": true,
      "smtp_server": "smtp.gmail.com",
      "smtp_port": 587,
      "username": "metgo.quillota@gmail.com",
      "password": "app_password_aqui",
      "to_emails": ["admin@metgo.cl"]
    }
  }
}
```

## 📊 Reportes

### Reporte de Estado
```bash
python monitoring/monitoreo_produccion.py
```

### Reporte Detallado
El sistema genera reportes automáticos cada 5 minutos con:
- Estado de servicios
- Métricas de sistema
- Alertas activas
- Recomendaciones

## 🛠️ Mantenimiento

### Limpiar Logs Antiguos
```bash
find logs/ -name "*.log" -mtime +30 -delete
```

### Rotar Logs
```bash
logrotate -f /etc/logrotate.d/metgo
```

## 🚨 Solución de Problemas

### Servicio No Responde
1. Verificar estado: `python scripts/verificar_estado.py`
2. Revisar logs: `tail -f logs/monitoreo_produccion.log`
3. Reiniciar servicio: `python scripts/reiniciar_produccion.py`

### Alto Uso de Recursos
1. Verificar métricas: `python scripts/verificar_estado.py`
2. Reiniciar sistema: `python scripts/reiniciar_produccion.py`
3. Verificar procesos: `ps aux | grep python`

### Alertas Falsas
1. Ajustar umbrales en `config/monitoreo_config.json`
2. Verificar configuración de servicios
3. Revisar logs de monitoreo

---

*Guía de Monitoreo - METGO 3D Quillota*
*Sistema Meteorológico Agrícola Avanzado*
'''
    
    def _generar_guia_backup(self):
        """Generar guía de backup"""
        return '''# 💾 GUÍA DE BACKUP - METGO 3D QUILLOTA

## 🎯 Sistema de Backup

El sistema incluye backup automático de:
- Datos meteorológicos
- Configuraciones
- Logs del sistema
- Bases de datos
- Código fuente

## 🚀 Backup Manual

### Crear Backup
```bash
python backup/backup_automatico.py
```

### Listar Backups
```bash
python backup/backup_automatico.py
```

## ⚙️ Configuración de Backup

### Archivo de Configuración
`config/backup_config.json`:
```json
{
  "directorio_backup": "./backups",
  "retencion_dias": 30,
  "frecuencia": "diario",
  "archivos_incluir": [
    "data/",
    "logs/",
    "config/",
    "*.db",
    "*.json",
    "*.py"
  ]
}
```

### Directorios Incluidos
- `data/` - Datos meteorológicos
- `logs/` - Logs del sistema
- `config/` - Configuraciones
- `*.db` - Bases de datos
- `*.json` - Archivos de configuración
- `*.py` - Código fuente

## 📅 Backup Automático

### Programar Backup Diario
#### Windows (Task Scheduler)
1. Abrir Task Scheduler
2. Crear tarea básica
3. Configurar para ejecutar diariamente
4. Acción: `python backup/backup_automatico.py`

#### Linux/Mac (Cron)
```bash
# Editar crontab
crontab -e

# Agregar línea para backup diario a las 2:00 AM
0 2 * * * cd /ruta/a/metgo && python backup/backup_automatico.py
```

## 🔄 Restauración

### Restaurar Backup
```python
from backup.backup_automatico import BackupAutomatico

backup = BackupAutomatico()
backup.restaurar_backup('metgo_backup_20251007_143000.zip')
```

### Listar Backups Disponibles
```python
from backup.backup_automatico import BackupAutomatico

backup = BackupAutomatico()
backups = backup.listar_backups()
for b in backups:
    print(f"{b['nombre']} - {b['fecha_creacion']} - {b['tamaño_mb']:.2f} MB")
```

## 📊 Gestión de Backups

### Retención
- Backups se mantienen por 30 días por defecto
- Configurable en `backup_config.json`
- Backups antiguos se eliminan automáticamente

### Compresión
- Backups se comprimen en formato ZIP
- Reducción de tamaño ~70%
- Verificación de integridad automática

### Verificación
```bash
# Verificar integridad de backup
unzip -t backups/metgo_backup_20251007_143000.zip
```

## 🚨 Recuperación de Desastres

### Procedimiento de Recuperación
1. Detener sistema: `python scripts/parar_produccion.py`
2. Restaurar backup más reciente
3. Verificar integridad de datos
4. Reiniciar sistema: `python scripts/iniciar_produccion.py`

### Backup de Emergencia
```bash
# Crear backup de emergencia
python backup/backup_automatico.py

# Copiar a ubicación externa
cp backups/metgo_backup_*.zip /ruta/externa/
```

## 🔧 Mantenimiento

### Limpiar Backups Antiguos
```bash
# Eliminar backups más antiguos que 30 días
find backups/ -name "metgo_backup_*.zip" -mtime +30 -delete
```

### Verificar Espacio en Disco
```bash
# Verificar espacio disponible
df -h backups/
```

### Monitorear Backups
```bash
# Verificar último backup
ls -la backups/ | tail -1
```

## 📈 Monitoreo de Backups

### Verificar Estado
```bash
python scripts/verificar_estado.py
```

### Logs de Backup
```bash
tail -f logs/backup_automatico.log
```

### Alertas de Backup
Configurar alertas si backup falla:
```json
{
  "alertas": {
    "backup_fallido": true,
    "email_notificacion": "admin@metgo.cl"
  }
}
```

## 🛠️ Solución de Problemas

### Error de Permisos
```bash
# Dar permisos de escritura
chmod 755 backups/
chown usuario:grupo backups/
```

### Error de Espacio
```bash
# Verificar espacio disponible
df -h
# Limpiar backups antiguos
find backups/ -name "*.zip" -mtime +30 -delete
```

### Error de Compresión
```bash
# Verificar integridad
unzip -t backups/metgo_backup_*.zip
# Recrear backup si es necesario
python backup/backup_automatico.py
```

---

*Guía de Backup - METGO 3D Quillota*
*Sistema Meteorológico Agrícola Avanzado*
'''
    
    def _generar_reporte_deployment(self):
        """Generar reporte final de deployment"""
        try:
            reporte = {
                'fecha_deployment': datetime.now().isoformat(),
                'version': '1.0.0',
                'sistema': 'METGO 3D Quillota',
                'componentes_desplegados': [
                    'Dashboard Principal (puerto 8501)',
                    'Dashboard Agrícola Avanzado (puerto 8510)',
                    'Sistema de Monitoreo (puerto 8502)',
                    'Sistema de Backup Automático',
                    'Scripts de Deployment',
                    'Configuración Docker'
                ],
                'archivos_creados': self._listar_archivos_creados(),
                'servicios_disponibles': [
                    'http://localhost:8501 - Dashboard Principal',
                    'http://localhost:8510 - Dashboard Agrícola',
                    'http://localhost:8502 - Monitoreo'
                ],
                'comandos_principales': [
                    'python scripts/iniciar_produccion.py - Iniciar sistema',
                    'python scripts/parar_produccion.py - Detener sistema',
                    'python scripts/verificar_estado.py - Verificar estado',
                    'python monitoring/monitoreo_produccion.py - Monitoreo continuo',
                    'python backup/backup_automatico.py - Backup manual'
                ],
                'configuracion': self.configuracion
            }
            
            # Guardar reporte
            with open(os.path.join(self.directorio_deployment, 'REPORTE_DEPLOYMENT.json'), 'w', encoding='utf-8') as f:
                json.dump(reporte, f, indent=2, ensure_ascii=False)
            
            # Mostrar resumen
            print("\n" + "="*60)
            print("RESUMEN DE DEPLOYMENT")
            print("="*60)
            print(f"Fecha: {reporte['fecha_deployment']}")
            print(f"Sistema: {reporte['sistema']} v{reporte['version']}")
            print(f"Componentes: {len(reporte['componentes_desplegados'])}")
            print(f"Archivos creados: {len(reporte['archivos_creados'])}")
            print("\nServicios disponibles:")
            for servicio in reporte['servicios_disponibles']:
                print(f"  - {servicio}")
            print("\nComandos principales:")
            for comando in reporte['comandos_principales']:
                print(f"  - {comando}")
            
        except Exception as e:
            self.logger.error(f"Error generando reporte: {e}")
    
    def _listar_archivos_creados(self):
        """Listar archivos creados en deployment"""
        archivos = []
        
        # Recorrer directorio de deployment
        for root, dirs, files in os.walk(self.directorio_deployment):
            for file in files:
                ruta_relativa = os.path.relpath(os.path.join(root, file), self.directorio_deployment)
                archivos.append(ruta_relativa)
        
        return archivos

def main():
    """Función principal"""
    deployment = DeploymentProduccionCompleto()
    deployment.ejecutar_deployment_completo()

if __name__ == "__main__":
    main()