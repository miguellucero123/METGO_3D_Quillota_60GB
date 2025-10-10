#!/usr/bin/env python3
"""
Script para preparar el dashboard para Streamlit Cloud (gratuito)
"""

import os
import shutil

def crear_requirements():
    """Crea archivo requirements.txt para Streamlit Cloud"""
    requirements = """streamlit==1.28.0
plotly==5.17.0
pandas==2.1.1
numpy==1.24.3
requests==2.31.0
"""
    
    with open('requirements.txt', 'w') as f:
        f.write(requirements)
    
    print("Archivo requirements.txt creado")

def crear_gitignore():
    """Crea archivo .gitignore"""
    gitignore = """# Streamlit
.streamlit/

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
env.bak/
venv.bak/

# Data
data/
*.db
*.csv
*.json

# Logs
logs/
*.log

# OS
.DS_Store
Thumbs.db
"""
    
    with open('.gitignore', 'w') as f:
        f.write(gitignore)
    
    print("Archivo .gitignore creado")

def crear_readme():
    """Crea README.md para GitHub"""
    readme = """# Dashboard METGO - Sistema Meteorologico y Agricola

## Descripcion
Dashboard integrado para monitoreo meteorologico y agricola en Quillota, Chile.

## Caracteristicas
- Sistema de autenticacion
- Datos meteorologicos en tiempo real
- Analisis agricola
- Alertas y recomendaciones ML
- Navegacion a todos los dashboards del sistema

## Instalacion Local
```bash
pip install -r requirements.txt
streamlit run sistema_auth_dashboard_principal_metgo.py
```

## Acceso
- Local: http://localhost:8501
- Streamlit Cloud: [URL se genera automaticamente]

## Autor
Sistema METGO - Quillota
"""
    
    with open('README.md', 'w') as f:
        f.write(readme)
    
    print("Archivo README.md creado")

def preparar_deploy():
    """Prepara archivos para deploy en Streamlit Cloud"""
    print("Preparando archivos para Streamlit Cloud...")
    
    # Crear archivos necesarios
    crear_requirements()
    crear_gitignore()
    crear_readme()
    
    # Crear directorio .streamlit si no existe
    if not os.path.exists('.streamlit'):
        os.makedirs('.streamlit')
    
    # Crear config.toml para Streamlit Cloud
    config_content = """[server]
port = 8501
address = "0.0.0.0"
headless = true
enableCORS = true
enableXsrfProtection = false

[browser]
gatherUsageStats = false
serverAddress = "0.0.0.0"
serverPort = 8501

[theme]
primaryColor = "#FF6B35"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"
"""
    
    with open('.streamlit/config.toml', 'w') as f:
        f.write(config_content)
    
    print("Configuracion de Streamlit creada")
    
    print()
    print("=" * 60)
    print("ARCHIVOS PREPARADOS PARA STREAMLIT CLOUD")
    print("=" * 60)
    print()
    print("Pasos para deployar:")
    print()
    print("1. Crear repositorio en GitHub:")
    print("   - Ve a https://github.com")
    print("   - Crea nuevo repositorio")
    print("   - Sube todos los archivos")
    print()
    print("2. Deployar en Streamlit Cloud:")
    print("   - Ve a https://share.streamlit.io")
    print("   - Conecta tu cuenta de GitHub")
    print("   - Selecciona tu repositorio")
    print("   - Archivo principal: sistema_auth_dashboard_principal_metgo.py")
    print()
    print("3. URLs que obtendras:")
    print("   - https://tu-usuario-streamlit-app.streamlit.app")
    print("   - Accesible desde cualquier lugar del mundo")
    print("   - Gratuito y permanente")
    print()
    print("Archivos creados:")
    print("- requirements.txt")
    print("- .gitignore")
    print("- README.md")
    print("- .streamlit/config.toml")
    print()
    print("Listo para subir a GitHub!")

if __name__ == "__main__":
    preparar_deploy()
