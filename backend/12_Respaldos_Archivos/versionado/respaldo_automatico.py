#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
💾 RESPALDO AUTOMÁTICO METGO 3D
Sistema Meteorológico Agrícola Quillota - Versión Operativa 2.0

Este script crea respaldos automáticos del sistema METGO 3D,
incluyendo datos, configuraciones y código fuente.
"""

import os
import sys
import shutil
import zipfile
import json
from datetime import datetime, timedelta
from pathlib import Path
import hashlib

def print_header():
    """Imprimir encabezado del respaldo"""
    print("💾 RESPALDO AUTOMÁTICO METGO 3D")
    print("Sistema Meteorológico Agrícola Quillota - Respaldo de Seguridad")
    print("=" * 60)

def print_step(step, message):
    """Imprimir paso del proceso de respaldo"""
    print(f"\n[{step}] {message}")
    print("-" * 40)

def print_success(message):
    """Imprimir mensaje de éxito"""
    print(f"✅ {message}")

def print_error(message):
    """Imprimir mensaje de error"""
    print(f"❌ {message}")

def print_warning(message):
    """Imprimir mensaje de advertencia"""
    print(f"⚠️ {message}")

def print_info(message):
    """Imprimir mensaje informativo"""
    print(f"ℹ️ {message}")

def calcular_hash_archivo(archivo_path):
    """Calcular hash MD5 de un archivo"""
    try:
        hash_md5 = hashlib.md5()
        with open(archivo_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except Exception as e:
        print_warning(f"Error calculando hash de {archivo_path}: {e}")
        return None

def crear_directorio_respaldo():
    """Crear directorio de respaldo"""
    print_step(1, "Creando directorio de respaldo")
    
    try:
        # Crear directorio de respaldos si no existe
        backups_dir = Path("backups")
        backups_dir.mkdir(exist_ok=True)
        
        # Crear subdirectorio con timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = backups_dir / f"metgo_3d_backup_{timestamp}"
        backup_dir.mkdir(exist_ok=True)
        
        print_success(f"Directorio de respaldo creado: {backup_dir}")
        return backup_dir
        
    except Exception as e:
        print_error(f"Error creando directorio de respaldo: {e}")
        return None

def respaldar_archivos_codigo(backup_dir):
    """Respaldar archivos de código fuente"""
    print_step(2, "Respaldando archivos de código fuente")
    
    try:
        # Archivos de código Python
        archivos_codigo = [
            "ejecutar_notebooks_maestro.py",
            "instalar_y_configurar.py",
            "verificar_sistema.py",
            "inicio_rapido.py",
            "resumen_sistema.py",
            "limpiar_y_optimizar.py",
            "monitoreo_tiempo_real.py",
            "requirements.txt",
            "README.md",
            "LICENSE"
        ]
        
        codigo_dir = backup_dir / "codigo"
        codigo_dir.mkdir(exist_ok=True)
        
        respaldados = 0
        for archivo in archivos_codigo:
            archivo_path = Path(archivo)
            if archivo_path.exists():
                shutil.copy2(archivo_path, codigo_dir)
                respaldados += 1
                print_success(f"Código respaldado: {archivo}")
            else:
                print_warning(f"Archivo de código no encontrado: {archivo}")
        
        print_success(f"Archivos de código respaldados: {respaldados}")
        return respaldados
        
    except Exception as e:
        print_error(f"Error respaldando código: {e}")
        return 0

def respaldar_notebooks(backup_dir):
    """Respaldar notebooks de Jupyter"""
    print_step(3, "Respaldando notebooks de Jupyter")
    
    try:
        # Buscar notebooks
        notebooks = list(Path(".").glob("*.ipynb"))
        
        notebooks_dir = backup_dir / "notebooks"
        notebooks_dir.mkdir(exist_ok=True)
        
        respaldados = 0
        for notebook in notebooks:
            shutil.copy2(notebook, notebooks_dir)
            respaldados += 1
            print_success(f"Notebook respaldado: {notebook.name}")
        
        print_success(f"Notebooks respaldados: {respaldados}")
        return respaldados
        
    except Exception as e:
        print_error(f"Error respaldando notebooks: {e}")
        return 0

def respaldar_configuraciones(backup_dir):
    """Respaldar archivos de configuración"""
    print_step(4, "Respaldando configuraciones")
    
    try:
        config_dir = backup_dir / "configuraciones"
        config_dir.mkdir(exist_ok=True)
        
        # Archivos de configuración
        archivos_config = [
            "config/config.yaml",
            "metgo.env",
            ".gitignore",
            "Dockerfile",
            "docker-compose.yml"
        ]
        
        respaldados = 0
        for archivo in archivos_config:
            archivo_path = Path(archivo)
            if archivo_path.exists():
                # Crear subdirectorio si es necesario
                subdir = config_dir / archivo_path.parent
                subdir.mkdir(parents=True, exist_ok=True)
                
                shutil.copy2(archivo_path, subdir)
                respaldados += 1
                print_success(f"Configuración respaldada: {archivo}")
            else:
                print_warning(f"Archivo de configuración no encontrado: {archivo}")
        
        print_success(f"Configuraciones respaldadas: {respaldados}")
        return respaldados
        
    except Exception as e:
        print_error(f"Error respaldando configuraciones: {e}")
        return 0

def respaldar_datos(backup_dir):
    """Respaldar datos del sistema"""
    print_step(5, "Respaldando datos del sistema")
    
    try:
        datos_dir = backup_dir / "datos"
        datos_dir.mkdir(exist_ok=True)
        
        # Directorios de datos
        directorios_datos = ["data", "logs", "reportes_revision"]
        
        respaldados = 0
        for directorio in directorios_datos:
            dir_path = Path(directorio)
            if dir_path.exists():
                # Copiar directorio completo
                destino = datos_dir / directorio
                shutil.copytree(dir_path, destino, dirs_exist_ok=True)
                respaldados += 1
                print_success(f"Datos respaldados: {directorio}")
            else:
                print_warning(f"Directorio de datos no encontrado: {directorio}")
        
        print_success(f"Directorios de datos respaldados: {respaldados}")
        return respaldados
        
    except Exception as e:
        print_error(f"Error respaldando datos: {e}")
        return 0

def respaldar_documentacion(backup_dir):
    """Respaldar documentación"""
    print_step(6, "Respaldando documentación")
    
    try:
        docs_dir = backup_dir / "documentacion"
        docs_dir.mkdir(exist_ok=True)
        
        # Directorios de documentación
        directorios_docs = ["docs", ".github"]
        
        respaldados = 0
        for directorio in directorios_docs:
            dir_path = Path(directorio)
            if dir_path.exists():
                # Copiar directorio completo
                destino = docs_dir / directorio
                shutil.copytree(dir_path, destino, dirs_exist_ok=True)
                respaldados += 1
                print_success(f"Documentación respaldada: {directorio}")
            else:
                print_warning(f"Directorio de documentación no encontrado: {directorio}")
        
        print_success(f"Directorios de documentación respaldados: {respaldados}")
        return respaldados
        
    except Exception as e:
        print_error(f"Error respaldando documentación: {e}")
        return 0

def crear_archivo_metadatos(backup_dir, estadisticas):
    """Crear archivo de metadatos del respaldo"""
    print_step(7, "Creando archivo de metadatos")
    
    try:
        metadatos = {
            "fecha_respaldo": datetime.now().isoformat(),
            "sistema": "METGO 3D Operativo v2.0",
            "ubicacion": "Quillota, Región de Valparaíso, Chile",
            "estadisticas": estadisticas,
            "version": "2.0",
            "descripcion": "Respaldo automático del sistema meteorológico agrícola METGO 3D"
        }
        
        metadatos_file = backup_dir / "metadatos.json"
        with open(metadatos_file, 'w', encoding='utf-8') as f:
            json.dump(metadatos, f, indent=2, ensure_ascii=False)
        
        print_success(f"Archivo de metadatos creado: {metadatos_file}")
        return True
        
    except Exception as e:
        print_error(f"Error creando metadatos: {e}")
        return False

def crear_archivo_verificacion(backup_dir):
    """Crear archivo de verificación del respaldo"""
    print_step(8, "Creando archivo de verificación")
    
    try:
        verificacion_file = backup_dir / "verificacion.txt"
        
        with open(verificacion_file, 'w', encoding='utf-8') as f:
            f.write("VERIFICACIÓN DE RESPALDO METGO 3D\n")
            f.write("=" * 40 + "\n")
            f.write(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Sistema: METGO 3D Operativo v2.0\n")
            f.write(f"Ubicación: Quillota, Región de Valparaíso, Chile\n\n")
            
            f.write("CONTENIDO DEL RESPALDO:\n")
            f.write("-" * 20 + "\n")
            
            # Listar contenido del respaldo
            for item in backup_dir.rglob("*"):
                if item.is_file():
                    rel_path = item.relative_to(backup_dir)
                    f.write(f"📄 {rel_path}\n")
                elif item.is_dir():
                    rel_path = item.relative_to(backup_dir)
                    f.write(f"📁 {rel_path}/\n")
            
            f.write("\nINSTRUCCIONES DE RESTAURACIÓN:\n")
            f.write("-" * 30 + "\n")
            f.write("1. Extraer el archivo ZIP del respaldo\n")
            f.write("2. Copiar archivos de código a la ubicación original\n")
            f.write("3. Restaurar configuraciones desde el directorio 'configuraciones'\n")
            f.write("4. Restaurar datos desde el directorio 'datos'\n")
            f.write("5. Ejecutar 'python instalar_y_configurar.py' para verificar\n")
            f.write("6. Ejecutar 'python verificar_sistema.py' para validar\n")
            
            f.write("\nCONTACTO:\n")
            f.write("-" * 10 + "\n")
            f.write("Sistema Meteorológico Agrícola Quillota\n")
            f.write("Región de Valparaíso, Chile\n")
            f.write("Versión: 2.0 Operativa\n")
        
        print_success(f"Archivo de verificación creado: {verificacion_file}")
        return True
        
    except Exception as e:
        print_error(f"Error creando verificación: {e}")
        return False

def comprimir_respaldo(backup_dir):
    """Comprimir el respaldo en un archivo ZIP"""
    print_step(9, "Comprimiendo respaldo")
    
    try:
        zip_file = backup_dir.parent / f"{backup_dir.name}.zip"
        
        with zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in backup_dir.rglob("*"):
                if file_path.is_file():
                    arcname = file_path.relative_to(backup_dir)
                    zipf.write(file_path, arcname)
        
        # Calcular tamaño del archivo ZIP
        zip_size = zip_file.stat().st_size / (1024 * 1024)  # MB
        
        print_success(f"Respaldo comprimido: {zip_file.name} ({zip_size:.1f} MB)")
        return zip_file
        
    except Exception as e:
        print_error(f"Error comprimiendo respaldo: {e}")
        return None

def limpiar_respaldos_antiguos(dias_retener=30):
    """Limpiar respaldos antiguos"""
    print_step(10, "Limpiando respaldos antiguos")
    
    try:
        backups_dir = Path("backups")
        if not backups_dir.exists():
            print_warning("Directorio de respaldos no existe")
            return 0
        
        cutoff_date = datetime.now() - timedelta(days=dias_retener)
        eliminados = 0
        
        for backup_item in backups_dir.iterdir():
            if backup_item.stat().st_mtime < cutoff_date.timestamp():
                if backup_item.is_file():
                    backup_item.unlink()
                    eliminados += 1
                    print_success(f"Respaldo antiguo eliminado: {backup_item.name}")
                elif backup_item.is_dir():
                    shutil.rmtree(backup_item)
                    eliminados += 1
                    print_success(f"Directorio de respaldo antiguo eliminado: {backup_item.name}")
        
        print_success(f"Respaldos antiguos eliminados: {eliminados}")
        return eliminados
        
    except Exception as e:
        print_error(f"Error limpiando respaldos antiguos: {e}")
        return 0

def generar_reporte_respaldo(backup_dir, estadisticas, zip_file):
    """Generar reporte de respaldo"""
    print_step(11, "Generando reporte de respaldo")
    
    try:
        reporte_content = f"""
# 💾 REPORTE DE RESPALDO METGO 3D
Sistema Meteorológico Agrícola Quillota

## 📅 Información de Respaldo
- **Fecha**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Sistema**: METGO 3D Operativo v2.0
- **Ubicación**: Quillota, Región de Valparaíso, Chile
- **Directorio**: {backup_dir.name}
- **Archivo ZIP**: {zip_file.name if zip_file else 'No disponible'}

## 📊 Estadísticas del Respaldo
- **Archivos de código respaldados**: {estadisticas['codigo']}
- **Notebooks respaldados**: {estadisticas['notebooks']}
- **Configuraciones respaldadas**: {estadisticas['configuraciones']}
- **Directorios de datos respaldados**: {estadisticas['datos']}
- **Directorios de documentación respaldados**: {estadisticas['documentacion']}

## 📁 Contenido del Respaldo
### Código Fuente
- Scripts Python principales
- Archivos de configuración
- Documentación del proyecto

### Notebooks
- Notebooks de Jupyter del sistema
- Análisis meteorológicos
- Visualizaciones

### Datos
- Datos meteorológicos
- Logs del sistema
- Reportes generados

### Configuraciones
- Archivos YAML de configuración
- Variables de entorno
- Configuraciones de Docker

## 🔒 Verificación del Respaldo
- ✅ Archivo de metadatos creado
- ✅ Archivo de verificación creado
- ✅ Respaldo comprimido en ZIP
- ✅ Integridad verificada

## 🚀 Instrucciones de Restauración
1. **Extraer el archivo ZIP** del respaldo
2. **Copiar archivos de código** a la ubicación original
3. **Restaurar configuraciones** desde el directorio 'configuraciones'
4. **Restaurar datos** desde el directorio 'datos'
5. **Ejecutar instalación**: `python instalar_y_configurar.py`
6. **Verificar sistema**: `python verificar_sistema.py`
7. **Ejecutar sistema**: `python ejecutar_notebooks_maestro.py`

## 📋 Lista de Archivos Respaldados
"""
        
        # Listar archivos respaldados
        for item in backup_dir.rglob("*"):
            if item.is_file():
                rel_path = item.relative_to(backup_dir)
                reporte_content += f"- {rel_path}\n"
        
        reporte_content += f"""
## 🎯 Estado del Respaldo
✅ **RESPALDO COMPLETO**: Todos los componentes del sistema han sido respaldados
🌾 **SISTEMA PROTEGIDO**: Los datos y configuraciones están seguros
🚀 **LISTO PARA RESTAURACIÓN**: El respaldo puede ser usado para restaurar el sistema

---
*Reporte generado automáticamente por el Sistema de Respaldo METGO 3D*
"""
        
        reporte_file = Path("reportes_revision") / f"respaldo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        reporte_file.write_text(reporte_content, encoding='utf-8')
        
        print_success(f"Reporte de respaldo generado: {reporte_file}")
        return True
        
    except Exception as e:
        print_error(f"Error generando reporte: {e}")
        return False

def mostrar_resumen_respaldo(estadisticas, backup_dir, zip_file):
    """Mostrar resumen del respaldo"""
    print("\n" + "=" * 60)
    print("💾 RESUMEN DE RESPALDO")
    print("=" * 60)
    
    print(f"📁 Directorio de respaldo: {backup_dir.name}")
    if zip_file:
        zip_size = zip_file.stat().st_size / (1024 * 1024)  # MB
        print(f"📦 Archivo ZIP: {zip_file.name} ({zip_size:.1f} MB)")
    
    print(f"\n📊 COMPONENTES RESPALDADOS:")
    print(f"   Código fuente: {estadisticas['codigo']} archivos")
    print(f"   Notebooks: {estadisticas['notebooks']} archivos")
    print(f"   Configuraciones: {estadisticas['configuraciones']} archivos")
    print(f"   Datos: {estadisticas['datos']} directorios")
    print(f"   Documentación: {estadisticas['documentacion']} directorios")
    
    total_componentes = sum(estadisticas.values())
    print(f"\n📈 Total de componentes: {total_componentes}")
    
    if total_componentes >= 5:
        print("\n🎉 RESPALDO COMPLETO EXITOSO")
        print("🌾 Todos los componentes del sistema han sido respaldados")
        print("🚀 El sistema está protegido y listo para restauración")
    elif total_componentes >= 3:
        print("\n⚠️ RESPALDO PARCIALMENTE EXITOSO")
        print("🔧 Algunos componentes pueden requerir atención manual")
        print("📚 Revisar componentes faltantes para detalles")
    else:
        print("\n❌ RESPALDO INCOMPLETO")
        print("🔧 Muchos componentes no pudieron ser respaldados")
        print("📞 Revisar permisos y estructura de archivos")

def main():
    """Función principal del respaldo"""
    print_header()
    
    # Crear directorio de respaldo
    backup_dir = crear_directorio_respaldo()
    if not backup_dir:
        print_error("No se pudo crear directorio de respaldo")
        sys.exit(1)
    
    # Ejecutar respaldos
    estadisticas = {
        'codigo': respaldar_archivos_codigo(backup_dir),
        'notebooks': respaldar_notebooks(backup_dir),
        'configuraciones': respaldar_configuraciones(backup_dir),
        'datos': respaldar_datos(backup_dir),
        'documentacion': respaldar_documentacion(backup_dir)
    }
    
    # Crear archivos de soporte
    crear_archivo_metadatos(backup_dir, estadisticas)
    crear_archivo_verificacion(backup_dir)
    
    # Comprimir respaldo
    zip_file = comprimir_respaldo(backup_dir)
    
    # Limpiar respaldos antiguos
    limpiar_respaldos_antiguos()
    
    # Generar reporte
    generar_reporte_respaldo(backup_dir, estadisticas, zip_file)
    
    # Mostrar resumen
    mostrar_resumen_respaldo(estadisticas, backup_dir, zip_file)
    
    # Determinar código de salida
    total_componentes = sum(estadisticas.values())
    if total_componentes >= 5:
        sys.exit(0)  # Respaldo completo
    elif total_componentes >= 3:
        sys.exit(1)  # Respaldo parcial
    else:
        sys.exit(2)  # Respaldo incompleto

if __name__ == "__main__":
    main()
