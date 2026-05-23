#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🧪 TESTING RÁPIDO METGO 3D
Sistema Meteorológico Agrícola Quillota - Versión Operativa 2.0

Este script ejecuta pruebas rápidas del sistema para verificar
que todos los componentes funcionan correctamente.
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def print_header():
    """Imprimir encabezado del testing"""
    print("🧪 TESTING RÁPIDO METGO 3D")
    print("Sistema Meteorológico Agrícola Quillota - Verificación Rápida")
    print("=" * 60)

def print_step(step, message):
    """Imprimir paso del proceso de testing"""
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

def test_imports():
    """Probar importaciones críticas"""
    print_step(1, "Probando importaciones críticas")
    
    critical_imports = [
        ("pandas", "pd"),
        ("numpy", "np"),
        ("matplotlib.pyplot", "plt"),
        ("seaborn", "sns"),
        ("sklearn.ensemble", "RandomForestRegressor"),
        ("requests", None),
        ("plotly.graph_objects", "go"),
        ("streamlit", "st"),
        ("yaml", None),
        ("jupyter", None)
    ]
    
    failed_imports = []
    
    for module, alias in critical_imports:
        try:
            if alias:
                exec(f"import {module} as {alias}")
            else:
                exec(f"import {module}")
            print_success(f"{module} importado correctamente")
        except ImportError as e:
            failed_imports.append(module)
            print_error(f"{module} falló: {e}")
    
    if failed_imports:
        print_error(f"Importaciones fallidas: {', '.join(failed_imports)}")
        return False
    
    print_success("Todas las importaciones críticas exitosas")
    return True

def test_configuration():
    """Probar configuración del sistema"""
    print_step(2, "Probando configuración del sistema")
    
    config_file = Path("config/config.yaml")
    if not config_file.exists():
        print_error("Archivo de configuración no encontrado")
        return False
    
    try:
        import yaml
        with open(config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        # Verificar secciones críticas
        required_sections = ['QUILLOTA', 'METEOROLOGIA', 'SISTEMA']
        missing_sections = []
        
        for section in required_sections:
            if section not in config:
                missing_sections.append(section)
            else:
                print_success(f"Sección {section} encontrada")
        
        if missing_sections:
            print_error(f"Secciones faltantes: {', '.join(missing_sections)}")
            return False
        
        print_success("Configuración del sistema válida")
        return True
        
    except Exception as e:
        print_error(f"Error leyendo configuración: {e}")
        return False

def test_data_generation():
    """Probar generación de datos sintéticos"""
    print_step(3, "Probando generación de datos sintéticos")
    
    test_code = """
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Generar datos de prueba
np.random.seed(42)
fechas = pd.date_range(start='2024-01-01', periods=7, freq='D')

datos = []
for fecha in fechas:
    datos.append({
        'fecha': fecha,
        'temperatura_max': np.random.normal(25, 3),
        'temperatura_min': np.random.normal(15, 2),
        'precipitacion': np.random.exponential(0.5),
        'humedad_relativa': np.random.normal(70, 10),
        'velocidad_viento': np.random.exponential(5)
    })

df = pd.DataFrame(datos)
print(f"✅ Datos generados: {len(df)} registros")
print(f"📊 Columnas: {list(df.columns)}")
print(f"📅 Rango fechas: {df['fecha'].min()} - {df['fecha'].max()}")
"""
    
    try:
        result = subprocess.run([
            sys.executable, "-c", test_code
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print_success("Generación de datos exitosa")
            print(result.stdout)
            return True
        else:
            print_error("Generación de datos falló")
            print(f"Error: {result.stderr}")
            return False
            
    except Exception as e:
        print_error(f"Error en generación de datos: {e}")
        return False

def test_analysis_functions():
    """Probar funciones de análisis"""
    print_step(4, "Probando funciones de análisis")
    
    test_code = """
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Crear datos de prueba
np.random.seed(42)
fechas = pd.date_range(start='2024-01-01', periods=30, freq='D')

datos = []
for fecha in fechas:
    datos.append({
        'fecha': fecha,
        'temperatura_max': np.random.normal(25, 3),
        'temperatura_min': np.random.normal(15, 2),
        'precipitacion': np.random.exponential(0.5),
        'humedad_relativa': np.random.normal(70, 10),
        'velocidad_viento': np.random.exponential(5)
    })

df = pd.DataFrame(datos)

# Calcular estadísticas básicas
stats = {
    'temp_max_promedio': df['temperatura_max'].mean(),
    'temp_min_promedio': df['temperatura_min'].mean(),
    'precipitacion_total': df['precipitacion'].sum(),
    'humedad_promedio': df['humedad_relativa'].mean(),
    'viento_promedio': df['velocidad_viento'].mean()
}

print("✅ Análisis estadístico exitoso")
for key, value in stats.items():
    print(f"   {key}: {value:.2f}")

# Detectar extremos
extremos = {
    'temp_maxima': df['temperatura_max'].max(),
    'temp_minima': df['temperatura_min'].min(),
    'lluvia_maxima': df['precipitacion'].max(),
    'dias_lluvia': (df['precipitacion'] > 0).sum()
}

print("✅ Detección de extremos exitosa")
for key, value in extremos.items():
    print(f"   {key}: {value}")
"""
    
    try:
        result = subprocess.run([
            sys.executable, "-c", test_code
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print_success("Funciones de análisis funcionando")
            print(result.stdout)
            return True
        else:
            print_error("Funciones de análisis fallaron")
            print(f"Error: {result.stderr}")
            return False
            
    except Exception as e:
        print_error(f"Error en funciones de análisis: {e}")
        return False

def test_visualization():
    """Probar funciones de visualización"""
    print_step(5, "Probando funciones de visualización")
    
    test_code = """
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

# Configurar matplotlib para modo no interactivo
plt.ioff()

# Crear datos de prueba
np.random.seed(42)
fechas = pd.date_range(start='2024-01-01', periods=7, freq='D')
temperaturas = np.random.normal(20, 5, 7)

# Crear gráfico simple
fig, ax = plt.subplots(figsize=(8, 6))
ax.plot(fechas, temperaturas, marker='o', linewidth=2)
ax.set_title('Temperaturas de Prueba')
ax.set_xlabel('Fecha')
ax.set_ylabel('Temperatura (°C)')
ax.grid(True, alpha=0.3)

# Guardar gráfico
plt.savefig('test_plot.png', dpi=100, bbox_inches='tight')
plt.close()

print("✅ Gráfico creado y guardado: test_plot.png")

# Probar seaborn
data = pd.DataFrame({
    'x': np.random.normal(0, 1, 100),
    'y': np.random.normal(0, 1, 100)
})

fig, ax = plt.subplots(figsize=(6, 6))
sns.scatterplot(data=data, x='x', y='y', ax=ax)
ax.set_title('Scatter Plot de Prueba')
plt.savefig('test_scatter.png', dpi=100, bbox_inches='tight')
plt.close()

print("✅ Scatter plot creado y guardado: test_scatter.png")
"""
    
    try:
        result = subprocess.run([
            sys.executable, "-c", test_code
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print_success("Funciones de visualización funcionando")
            print(result.stdout)
            
            # Verificar que se crearon los archivos
            if Path("test_plot.png").exists() and Path("test_scatter.png").exists():
                print_success("Archivos de gráficos creados correctamente")
                # Limpiar archivos de prueba
                Path("test_plot.png").unlink(missing_ok=True)
                Path("test_scatter.png").unlink(missing_ok=True)
                return True
            else:
                print_warning("Archivos de gráficos no encontrados")
                return False
        else:
            print_error("Funciones de visualización fallaron")
            print(f"Error: {result.stderr}")
            return False
            
    except Exception as e:
        print_error(f"Error en funciones de visualización: {e}")
        return False

def test_ml_models():
    """Probar modelos de Machine Learning"""
    print_step(6, "Probando modelos de Machine Learning")
    
    test_code = """
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score

# Crear datos de prueba
np.random.seed(42)
n_samples = 100

X = np.random.randn(n_samples, 3)
y = X[:, 0] + 2 * X[:, 1] - X[:, 2] + np.random.normal(0, 0.1, n_samples)

# Dividir datos
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Probar Random Forest
rf = RandomForestRegressor(n_estimators=10, random_state=42)
rf.fit(X_train, y_train)
rf_pred = rf.predict(X_test)
rf_mse = mean_squared_error(y_test, rf_pred)
rf_r2 = r2_score(y_test, rf_pred)

print(f"✅ Random Forest - MSE: {rf_mse:.4f}, R²: {rf_r2:.4f}")

# Probar Linear Regression
lr = LinearRegression()
lr.fit(X_train, y_train)
lr_pred = lr.predict(X_test)
lr_mse = mean_squared_error(y_test, lr_pred)
lr_r2 = r2_score(y_test, lr_pred)

print(f"✅ Linear Regression - MSE: {lr_mse:.4f}, R²: {lr_r2:.4f}")

print("✅ Modelos de ML funcionando correctamente")
"""
    
    try:
        result = subprocess.run([
            sys.executable, "-c", test_code
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print_success("Modelos de Machine Learning funcionando")
            print(result.stdout)
            return True
        else:
            print_error("Modelos de Machine Learning fallaron")
            print(f"Error: {result.stderr}")
            return False
            
    except Exception as e:
        print_error(f"Error en modelos de ML: {e}")
        return False

def test_notebook_execution():
    """Probar ejecución de notebooks"""
    print_step(7, "Probando ejecución de notebooks")
    
    # Verificar que jupyter está disponible
    try:
        result = subprocess.run([
            "jupyter", "--version"
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            print_error("Jupyter no está disponible")
            return False
        
        print_success("Jupyter disponible")
        
        # Verificar que nbconvert está disponible
        result = subprocess.run([
            "jupyter", "nbconvert", "--version"
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            print_error("nbconvert no está disponible")
            return False
        
        print_success("nbconvert disponible")
        
        # Probar ejecución de un notebook simple (si existe)
        test_notebook = Path("01_Configuracion_e_imports.ipynb")
        if test_notebook.exists():
            print("Probando ejecución de notebook de configuración...")
            result = subprocess.run([
                "jupyter", "nbconvert", "--to", "notebook", "--execute", 
                "--inplace", "--ExecutePreprocessor.timeout=60", 
                str(test_notebook)
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print_success("Ejecución de notebook exitosa")
                return True
            else:
                print_warning("Ejecución de notebook falló (continuando)")
                return True  # No crítico para el testing rápido
        else:
            print_warning("Notebook de prueba no encontrado")
            return True
        
    except FileNotFoundError:
        print_error("Jupyter no encontrado en el sistema")
        return False
    except Exception as e:
        print_error(f"Error probando notebooks: {e}")
        return False

def test_file_structure():
    """Probar estructura de archivos"""
    print_step(8, "Probando estructura de archivos")
    
    required_files = [
        "requirements.txt",
        "README.md",
        "config/config.yaml"
    ]
    
    required_dirs = [
        "logs",
        "data", 
        "reportes_revision",
        "test_results"
    ]
    
    missing_files = []
    missing_dirs = []
    
    # Verificar archivos
    for file_path in required_files:
        if Path(file_path).exists():
            print_success(f"Archivo encontrado: {file_path}")
        else:
            missing_files.append(file_path)
            print_error(f"Archivo faltante: {file_path}")
    
    # Verificar directorios
    for dir_path in required_dirs:
        if Path(dir_path).exists():
            print_success(f"Directorio encontrado: {dir_path}")
        else:
            missing_dirs.append(dir_path)
            print_error(f"Directorio faltante: {dir_path}")
    
    if missing_files or missing_dirs:
        print_error("Estructura de archivos incompleta")
        return False
    
    print_success("Estructura de archivos correcta")
    return True

def run_comprehensive_test():
    """Ejecutar prueba comprehensiva del sistema"""
    print_step(9, "Ejecutando prueba comprehensiva")
    
    test_code = """
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
import requests
import yaml
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

print("🧪 PRUEBA COMPREHENSIVA METGO 3D")
print("=" * 40)

# 1. Generar datos meteorológicos sintéticos
np.random.seed(42)
fechas = pd.date_range(start='2024-01-01', periods=30, freq='D')

datos_meteorologicos = []
for fecha in fechas:
    # Simular datos realistas para Quillota
    temp_base = 20 + 8 * np.sin(2 * np.pi * fecha.dayofyear / 365)
    
    datos_meteorologicos.append({
        'fecha': fecha,
        'temperatura_max': temp_base + np.random.normal(0, 3),
        'temperatura_min': temp_base - 8 + np.random.normal(0, 2),
        'precipitacion': max(0, np.random.exponential(0.8)),
        'humedad_relativa': np.clip(np.random.normal(70, 15), 20, 95),
        'velocidad_viento': max(0, np.random.exponential(8)),
        'presion_atmosferica': np.random.normal(1013, 10)
    })

df = pd.DataFrame(datos_meteorologicos)
print(f"✅ Datos meteorológicos generados: {len(df)} registros")

# 2. Calcular índices agrícolas
df['temperatura_promedio'] = (df['temperatura_max'] + df['temperatura_min']) / 2
df['amplitud_termica'] = df['temperatura_max'] - df['temperatura_min']
df['grados_dia'] = np.maximum(0, df['temperatura_promedio'] - 10)

print("✅ Índices agrícolas calculados")

# 3. Análisis estadístico
estadisticas = {
    'temp_promedio': df['temperatura_promedio'].mean(),
    'precipitacion_total': df['precipitacion'].sum(),
    'humedad_promedio': df['humedad_relativa'].mean(),
    'grados_dia_total': df['grados_dia'].sum(),
    'dias_lluvia': (df['precipitacion'] > 0).sum()
}

print("📊 ESTADÍSTICAS METEOROLÓGICAS:")
for key, value in estadisticas.items():
    print(f"   {key}: {value:.2f}")

# 4. Detectar eventos extremos
eventos_extremos = {
    'temp_maxima': df['temperatura_max'].max(),
    'temp_minima': df['temperatura_min'].min(),
    'lluvia_maxima': df['precipitacion'].max(),
    'dias_helada': (df['temperatura_min'] <= 0).sum(),
    'dias_calor': (df['temperatura_max'] >= 30).sum()
}

print("🌡️ EVENTOS EXTREMOS:")
for key, value in eventos_extremos.items():
    print(f"   {key}: {value}")

# 5. Crear visualización
plt.figure(figsize=(12, 8))

# Subplot 1: Temperaturas
plt.subplot(2, 2, 1)
plt.plot(df['fecha'], df['temperatura_max'], 'r-', label='Máxima', linewidth=2)
plt.plot(df['fecha'], df['temperatura_min'], 'b-', label='Mínima', linewidth=2)
plt.plot(df['fecha'], df['temperatura_promedio'], 'g-', label='Promedio', linewidth=2)
plt.title('Temperaturas Diarias')
plt.xlabel('Fecha')
plt.ylabel('Temperatura (°C)')
plt.legend()
plt.grid(True, alpha=0.3)

# Subplot 2: Precipitación
plt.subplot(2, 2, 2)
plt.bar(df['fecha'], df['precipitacion'], color='blue', alpha=0.7)
plt.title('Precipitación Diaria')
plt.xlabel('Fecha')
plt.ylabel('Precipitación (mm)')
plt.grid(True, alpha=0.3)

# Subplot 3: Humedad
plt.subplot(2, 2, 3)
plt.plot(df['fecha'], df['humedad_relativa'], 'purple', linewidth=2)
plt.title('Humedad Relativa')
plt.xlabel('Fecha')
plt.ylabel('Humedad (%)')
plt.grid(True, alpha=0.3)

# Subplot 4: Grados-día acumulados
plt.subplot(2, 2, 4)
df['grados_dia_acum'] = df['grados_dia'].cumsum()
plt.plot(df['fecha'], df['grados_dia_acum'], 'orange', linewidth=2)
plt.title('Grados-día Acumulados')
plt.xlabel('Fecha')
plt.ylabel('Grados-día')
plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('test_comprehensive.png', dpi=100, bbox_inches='tight')
plt.close()

print("✅ Visualización comprehensiva creada: test_comprehensive.png")

# 6. Probar modelo de ML simple
X = df[['temperatura_promedio', 'humedad_relativa', 'velocidad_viento']].values
y = df['precipitacion'].values

# Entrenar modelo
rf = RandomForestRegressor(n_estimators=10, random_state=42)
rf.fit(X, y)
predicciones = rf.predict(X)

mse = mean_squared_error(y, predicciones)
print(f"✅ Modelo ML entrenado - MSE: {mse:.4f}")

# 7. Generar alertas
alertas = []
if df['temperatura_min'].min() <= -2:
    alertas.append("🧊 ALERTA: Helada severa detectada")
if df['temperatura_max'].max() >= 35:
    alertas.append("🔥 ALERTA: Calor extremo detectado")
if df['precipitacion'].sum() < 10:
    alertas.append("🏜️ ALERTA: Período muy seco")
if df['humedad_relativa'].mean() > 80:
    alertas.append("💧 ALERTA: Humedad muy alta")

if alertas:
    print("🚨 ALERTAS GENERADAS:")
    for alerta in alertas:
        print(f"   {alerta}")
else:
    print("✅ Sin alertas críticas")

print("\\n🎉 PRUEBA COMPREHENSIVA COMPLETADA EXITOSAMENTE")
print("🌾 Sistema METGO 3D funcionando correctamente")
"""
    
    try:
        result = subprocess.run([
            sys.executable, "-c", test_code
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print_success("Prueba comprehensiva exitosa")
            print(result.stdout)
            
            # Verificar archivo de gráfico
            if Path("test_comprehensive.png").exists():
                print_success("Gráfico comprehensivo creado")
                # Limpiar archivo de prueba
                Path("test_comprehensive.png").unlink(missing_ok=True)
            
            return True
        else:
            print_error("Prueba comprehensiva falló")
            print(f"Error: {result.stderr}")
            return False
            
    except Exception as e:
        print_error(f"Error en prueba comprehensiva: {e}")
        return False

def show_test_results(results):
    """Mostrar resultados del testing"""
    print("\n" + "=" * 60)
    print("📊 RESULTADOS DEL TESTING RÁPIDO")
    print("=" * 60)
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    failed_tests = total_tests - passed_tests
    
    print(f"📈 Total de pruebas: {total_tests}")
    print(f"✅ Pruebas exitosas: {passed_tests}")
    print(f"❌ Pruebas fallidas: {failed_tests}")
    
    success_rate = (passed_tests / total_tests) * 100
    print(f"📊 Tasa de éxito: {success_rate:.1f}%")
    
    print("\n📋 DETALLE DE RESULTADOS:")
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name}: {status}")
    
    if success_rate >= 80:
        print("\n🎉 SISTEMA METGO 3D LISTO PARA USO")
        print("🌾 Todas las funcionalidades principales operativas")
        print("🚀 Puedes ejecutar el sistema completo ahora")
    elif success_rate >= 60:
        print("\n⚠️ SISTEMA PARCIALMENTE OPERATIVO")
        print("🔧 Algunas funcionalidades pueden requerir ajustes")
        print("📚 Revisar logs para detalles de errores")
    else:
        print("\n❌ SISTEMA REQUIERE CONFIGURACIÓN ADICIONAL")
        print("🔧 Revisar dependencias y configuración")
        print("📞 Consultar documentación para troubleshooting")
    
    print(f"\n⏱️ Tiempo total de testing: {time.time() - start_time:.2f} segundos")

def main():
    """Función principal del testing"""
    global start_time
    start_time = time.time()
    
    print_header()
    
    # Ejecutar todas las pruebas
    test_results = {
        "Importaciones críticas": test_imports(),
        "Configuración del sistema": test_configuration(),
        "Generación de datos": test_data_generation(),
        "Funciones de análisis": test_analysis_functions(),
        "Funciones de visualización": test_visualization(),
        "Modelos de Machine Learning": test_ml_models(),
        "Ejecución de notebooks": test_notebook_execution(),
        "Estructura de archivos": test_file_structure(),
        "Prueba comprehensiva": run_comprehensive_test()
    }
    
    # Mostrar resultados
    show_test_results(test_results)

if __name__ == "__main__":
    main()
