#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MIGRADOR A GMAIL - METGO 3D
Sistema para migrar el proyecto METGO 3D via Gmail
"""

import os
import zipfile
import base64
import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from pathlib import Path
from datetime import datetime
import logging
from typing import List, Dict, Any
import getpass

class MigradorGmail:
    """Migrador del proyecto METGO 3D a Gmail"""
    
    def __init__(self):
        self.logger = logging.getLogger('MIGRADOR_GMAIL')
        self.proyecto_actual = Path.cwd()
        self.nombre_proyecto = "METGO_3D_Quillota"
        self.tamaño_maximo_adjunto = 25 * 1024 * 1024  # 25MB límite de Gmail
        
    def configurar_autenticacion(self):
        """Configurar autenticación para Gmail"""
        print("🔐 CONFIGURACIÓN DE AUTENTICACIÓN GMAIL")
        print("="*50)
        
        # Solicitar credenciales
        email = input("Ingrese su email de Gmail: ").strip()
        password = getpass.getpass("Ingrese su contraseña de aplicación (no la contraseña normal): ").strip()
        
        if not email or not password:
            print("❌ Email y contraseña son requeridos")
            return None
            
        return {
            'email': email,
            'password': password
        }
    
    def crear_paquete_para_gmail(self, tamaño_maximo_mb=20):
        """Crear paquete optimizado para Gmail"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            nombre_paquete = f"{self.nombre_proyecto}_gmail_{timestamp}.zip"
            ruta_paquete = self.proyecto_actual.parent / nombre_paquete
            
            self.logger.info(f"Creando paquete para Gmail: {ruta_paquete}")
            
            # Archivos esenciales para Gmail (más selectivos)
            archivos_esenciales = [
                'sistema_unificado_con_conectores.py',
                'auth_module.py',
                'integrador_modulos.py',
                'conector_iot_satelital.py',
                'conector_monitoreo_respaldos.py',
                'conector_apis_avanzadas.py',
                'optimizar_sistema_completo.py',
                'fix_ml_models.py',
                '00_Sistema_Principal_MIP_Quillota.ipynb',
                '01_Configuracion_e_imports.ipynb',
                '02_Carga_y_Procesamiento_Datos.ipynb',
                '03_Analisis_Meteorologico.ipynb',
                '04_Visualizaciones.ipynb',
                '05_Modelos_ML.ipynb',
                '06_Dashboard_Interactivo.ipynb',
                'config/',
                'modelos_ml_quillota/',
                'requirements.txt',
                'README.md',
                'LICENSE'
            ]
            
            # Excluir archivos pesados
            excluir = [
                '__pycache__/',
                '*.pyc',
                '*.pyo',
                '*.pyd',
                '.pytest_cache/',
                '.coverage',
                'htmlcov/',
                '.mypy_cache/',
                '.tox/',
                'dist/',
                'build/',
                '*.egg-info/',
                '*.log',
                '*.tmp',
                '*.temp',
                '*.bak',
                '*.swp',
                '*.swo',
                '*~',
                '.git/',
                '.vscode/',
                '.idea/',
                'node_modules/',
                'venv/',
                'env/',
                '.env',
                'data/respaldos/',
                '*.csv',  # Excluir archivos de datos grandes
                '*.xlsx',
                '*.png',
                '*.jpg',
                '*.jpeg',
                'backups/',
                'logs/',
                'artefactos/',
                'notebooks_corregidos/',
                'reportes_revision/',
                'resultados/',
                'graficos/',
                'static/',
                'templates/',
                'METGO_3D_OPERATIVO/'
            ]
            
            with zipfile.ZipFile(ruta_paquete, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as zipf:
                archivos_incluidos = 0
                tamaño_total = 0
                
                for patron in archivos_esenciales:
                    for archivo in self.proyecto_actual.glob(patron):
                        if archivo.is_file():
                            # Verificar exclusiones
                            excluir_archivo = False
                            for excluir_patron in excluir:
                                if excluir_patron.replace('*', '') in str(archivo):
                                    excluir_archivo = True
                                    break
                            
                            if not excluir_archivo:
                                try:
                                    arcname = archivo.relative_to(self.proyecto_actual)
                                    zipf.write(archivo, arcname)
                                    archivos_incluidos += 1
                                    tamaño_total += archivo.stat().st_size
                                    self.logger.info(f"Incluido: {arcname}")
                                except Exception as e:
                                    self.logger.warning(f"Error incluyendo {archivo}: {e}")
                        
                        elif archivo.is_dir():
                            # Procesar directorio
                            for subarchivo in archivo.rglob('*'):
                                if subarchivo.is_file():
                                    excluir_archivo = False
                                    for excluir_patron in excluir:
                                        if excluir_patron.replace('*', '') in str(subarchivo):
                                            excluir_archivo = True
                                            break
                                    
                                    if not excluir_archivo:
                                        try:
                                            arcname = subarchivo.relative_to(self.proyecto_actual)
                                            zipf.write(subarchivo, arcname)
                                            archivos_incluidos += 1
                                            tamaño_total += subarchivo.stat().st_size
                                        except Exception as e:
                                            self.logger.warning(f"Error incluyendo {subarchivo}: {e}")
            
            tamaño_final = ruta_paquete.stat().st_size
            tamaño_mb = tamaño_final / (1024**2)
            
            print(f"✅ Paquete creado: {archivos_incluidos} archivos")
            print(f"📦 Tamaño: {tamaño_mb:.2f} MB")
            
            if tamaño_mb > tamaño_maximo_mb:
                print(f"⚠️ Advertencia: El paquete ({tamaño_mb:.2f} MB) excede el límite recomendado ({tamaño_maximo_mb} MB)")
                print("   Se dividirá en múltiples partes para Gmail")
                return self.dividir_paquete_gmail(ruta_paquete, tamaño_maximo_mb)
            
            return [ruta_paquete]
            
        except Exception as e:
            self.logger.error(f"Error creando paquete para Gmail: {e}")
            return []
    
    def dividir_paquete_gmail(self, ruta_paquete, tamaño_maximo_mb):
        """Dividir paquete en partes para Gmail"""
        try:
            tamaño_maximo_bytes = tamaño_maximo_mb * 1024 * 1024
            archivos_divididos = []
            
            with open(ruta_paquete, 'rb') as f:
                contenido = f.read()
            
            tamaño_total = len(contenido)
            num_partes = (tamaño_total + tamaño_maximo_bytes - 1) // tamaño_maximo_bytes
            
            print(f"📦 Dividiendo en {num_partes} partes...")
            
            for i in range(num_partes):
                inicio = i * tamaño_maximo_bytes
                fin = min((i + 1) * tamaño_maximo_bytes, tamaño_total)
                
                parte_contenido = contenido[inicio:fin]
                nombre_parte = ruta_paquete.with_suffix(f'.part{i+1:02d}.zip')
                
                with open(nombre_parte, 'wb') as f:
                    f.write(parte_contenido)
                
                archivos_divididos.append(nombre_parte)
                print(f"   Parte {i+1}/{num_partes}: {nombre_parte.name} ({len(parte_contenido)/(1024**2):.2f} MB)")
            
            # Crear archivo de información
            info_particion = {
                'archivo_original': ruta_paquete.name,
                'total_partes': num_partes,
                'tamaño_original': tamaño_total,
                'tamaño_por_parte': tamaño_maximo_bytes,
                'fecha_creacion': datetime.now().isoformat(),
                'instrucciones': [
                    "1. Descargar todas las partes (.part01.zip, .part02.zip, etc.)",
                    "2. Combinar las partes en orden: copy /b *.part*.zip archivo_completo.zip",
                    "3. Extraer el archivo ZIP combinado",
                    "4. Seguir las instrucciones de instalación"
                ]
            }
            
            info_path = ruta_paquete.with_suffix('.info.json')
            with open(info_path, 'w', encoding='utf-8') as f:
                json.dump(info_particion, f, indent=2, ensure_ascii=False)
            
            archivos_divididos.append(info_path)
            return archivos_divididos
            
        except Exception as e:
            self.logger.error(f"Error dividiendo paquete: {e}")
            return []
    
    def enviar_por_gmail(self, archivos, credenciales, destinatario):
        """Enviar archivos por Gmail"""
        try:
            email = credenciales['email']
            password = credenciales['password']
            
            # Configurar servidor SMTP de Gmail
            servidor = smtplib.SMTP('smtp.gmail.com', 587)
            servidor.starttls()
            servidor.login(email, password)
            
            print(f"📧 Enviando {len(archivos)} archivo(s) a {destinatario}...")
            
            for i, archivo in enumerate(archivos, 1):
                if archivo.suffix == '.json':
                    continue  # Saltar archivos de información
                
                # Crear mensaje
                mensaje = MIMEMultipart()
                mensaje['From'] = email
                mensaje['To'] = destinatario
                mensaje['Subject'] = f"METGO 3D - Parte {i}/{len([a for a in archivos if a.suffix != '.json'])} - {archivo.name}"
                
                # Cuerpo del mensaje
                cuerpo = f"""
Hola,

Te envío el proyecto METGO 3D - Sistema Meteorológico Agrícola Quillota.

Archivo: {archivo.name}
Tamaño: {archivo.stat().st_size / (1024**2):.2f} MB
Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

INSTRUCCIONES DE INSTALACIÓN:
1. Descargar todas las partes del proyecto
2. Si hay múltiples partes, combinarlas en orden
3. Extraer el archivo ZIP
4. Instalar dependencias: pip install -r requirements.txt
5. Ejecutar: python -m streamlit run sistema_unificado_con_conectores.py

El dashboard estará disponible en: http://localhost:8501
Usuario: admin
Contraseña: admin123

Saludos,
Sistema METGO 3D
"""
                
                mensaje.attach(MIMEText(cuerpo, 'plain', 'utf-8'))
                
                # Adjuntar archivo
                with open(archivo, 'rb') as adjunto:
                    parte = MIMEBase('application', 'octet-stream')
                    parte.set_payload(adjunto.read())
                
                encoders.encode_base64(parte)
                parte.add_header(
                    'Content-Disposition',
                    f'attachment; filename= {archivo.name}'
                )
                mensaje.attach(parte)
                
                # Enviar email
                texto = mensaje.as_string()
                servidor.sendmail(email, destinatario, texto)
                print(f"   ✅ Parte {i} enviada: {archivo.name}")
            
            servidor.quit()
            print("✅ Todos los archivos enviados exitosamente")
            return True
            
        except Exception as e:
            self.logger.error(f"Error enviando por Gmail: {e}")
            print(f"❌ Error enviando por Gmail: {e}")
            return False
    
    def crear_instrucciones_descarga(self, archivos):
        """Crear instrucciones de descarga"""
        instrucciones = f"""# INSTRUCCIONES DE DESCARGA - METGO 3D

## Archivos Enviados
"""
        
        for i, archivo in enumerate(archivos, 1):
            if archivo.suffix != '.json':
                instrucciones += f"- Parte {i}: {archivo.name} ({archivo.stat().st_size / (1024**2):.2f} MB)\n"
        
        instrucciones += f"""
## Pasos para Reconstruir el Proyecto

### 1. Descargar Todos los Archivos
- Descargar todas las partes del proyecto desde Gmail
- Guardar en una carpeta temporal

### 2. Combinar las Partes (si es necesario)
Si hay múltiples partes (.part01.zip, .part02.zip, etc.):

**En Windows:**
```cmd
copy /b *.part*.zip METGO_3D_Completo.zip
```

**En Linux/Mac:**
```bash
cat *.part*.zip > METGO_3D_Completo.zip
```

### 3. Extraer el Proyecto
- Extraer el archivo ZIP combinado
- Crear una carpeta para el proyecto (ej: C:\\METGO_3D)

### 4. Instalar Dependencias
```bash
cd METGO_3D
pip install -r requirements.txt
```

### 5. Configurar Variables de Entorno
Crear archivo `.env` con:
```
OPENWEATHER_API_KEY=tu_clave_aqui
NASA_API_KEY=tu_clave_aqui
GOOGLE_MAPS_API_KEY=tu_clave_aqui
```

### 6. Ejecutar el Sistema
```bash
python -m streamlit run sistema_unificado_con_conectores.py
```

### 7. Acceder al Dashboard
- URL: http://localhost:8501
- Usuario: admin
- Contraseña: admin123

## Características del Sistema
- Sistema meteorológico agrícola completo
- Dashboard interactivo con visualizaciones 3D
- Machine Learning para predicciones
- APIs integradas (OpenWeather, NASA, etc.)
- Sistema de alertas automáticas
- Reportes automáticos

## Soporte
Para soporte técnico, contactar al equipo de desarrollo METGO 3D.

---
Fecha de migración: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        return instrucciones

def main():
    """Función principal para migración a Gmail"""
    print("📧 MIGRADOR A GMAIL - METGO 3D")
    print("Sistema Meteorológico Agrícola Quillota - Versión 2.0")
    print("="*70)
    
    try:
        migrador = MigradorGmail()
        
        # 1. Configurar autenticación
        print("\n1️⃣ Configurando autenticación Gmail...")
        credenciales = migrador.configurar_autenticacion()
        
        if not credenciales:
            print("❌ No se pudo configurar la autenticación")
            return False
        
        # 2. Crear paquete
        print("\n2️⃣ Creando paquete optimizado para Gmail...")
        archivos = migrador.crear_paquete_para_gmail()
        
        if not archivos:
            print("❌ No se pudo crear el paquete")
            return False
        
        # 3. Solicitar destinatario
        print("\n3️⃣ Configurando destinatario...")
        destinatario = input("Ingrese el email destinatario: ").strip()
        
        if not destinatario:
            print("❌ Email destinatario requerido")
            return False
        
        # 4. Enviar por Gmail
        print("\n4️⃣ Enviando por Gmail...")
        if migrador.enviar_por_gmail(archivos, credenciales, destinatario):
            print("\n✅ MIGRACIÓN A GMAIL COMPLETADA EXITOSAMENTE")
            
            # 5. Crear instrucciones
            print("\n5️⃣ Creando instrucciones de descarga...")
            instrucciones = migrador.crear_instrucciones_descarga(archivos)
            
            instrucciones_path = migrador.proyecto_actual / "INSTRUCCIONES_DESCARGA_GMAIL.md"
            with open(instrucciones_path, 'w', encoding='utf-8') as f:
                f.write(instrucciones)
            
            print(f"📄 Instrucciones guardadas en: {instrucciones_path}")
            
            print("\n📋 RESUMEN DE MIGRACIÓN:")
            print(f"   📧 Destinatario: {destinatario}")
            print(f"   📦 Archivos enviados: {len([a for a in archivos if a.suffix != '.json'])}")
            print(f"   📄 Instrucciones: {instrucciones_path}")
            
            return True
        else:
            print("❌ Error enviando por Gmail")
            return False
        
    except Exception as e:
        print(f"\n💥 ERROR EN MIGRACIÓN A GMAIL: {e}")
        return False

if __name__ == "__main__":
    main()

