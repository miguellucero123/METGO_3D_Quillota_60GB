cd /d "%~dp0..\.."
@echo off
echo ===============================================
echo   SISTEMA PERMANENTE METGO_3D - DASHBOARDS
echo ===============================================
echo.
echo Iniciando sistema permanente de dashboards...
echo.

REM Verificar si Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python no está instalado o no está en el PATH
    echo Por favor instala Python 3.8 o superior
    pause
    exit /b 1
)

REM Crear directorio de logs si no existe
if not exist "logs" mkdir logs

REM Verificar archivo principal
if not exist "sistema_permanente_metgo.py" (
    echo ERROR: No se encuentra el archivo sistema_permanente_metgo.py
    echo Asegúrate de ejecutar este script desde el directorio correcto
    pause
    exit /b 1
)

echo ✅ Python detectado correctamente
echo ✅ Directorio de logs creado
echo ✅ Archivo del sistema encontrado
echo.

echo 🚀 Iniciando sistema permanente METGO...
echo.
echo El sistema mantendrá todos los dashboards activos automáticamente
echo Presiona Ctrl+C para detener el sistema
echo.

REM Iniciar el sistema permanente
python sistema_permanente_metgo.py iniciar

echo.
echo Sistema detenido.
pause
