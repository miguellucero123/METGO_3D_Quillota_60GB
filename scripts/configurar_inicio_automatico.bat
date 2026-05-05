@echo off
echo ===============================================
echo   CONFIGURAR INICIO AUTOMÁTICO METGO_3D
echo ===============================================
echo.

REM Verificar permisos de administrador
net session >nul 2>&1
if errorlevel 1 (
    echo ERROR: Este script requiere permisos de administrador
    echo Haz clic derecho en el archivo y selecciona "Ejecutar como administrador"
    pause
    exit /b 1
)

echo ✅ Permisos de administrador verificados
echo.

REM Obtener ruta actual
set "RUTA_ACTUAL=%~dp0"
set "RUTA_ACTUAL=%RUTA_ACTUAL:~0,-1%"

echo 📁 Ruta del sistema: %RUTA_ACTUAL%
echo.

REM Crear tarea programada para inicio automático
echo 🔧 Configurando tarea programada...

schtasks /create /tn "METGO_3D_Sistema_Permanente" ^
    /tr "\"%RUTA_ACTUAL%\iniciar_sistema_permanente.bat\"" ^
    /sc onstart ^
    /ru "SYSTEM" ^
    /rl highest ^
    /f

if errorlevel 1 (
    echo ❌ Error al crear la tarea programada
    pause
    exit /b 1
)

echo ✅ Tarea programada creada exitosamente
echo.

REM Crear acceso directo en el escritorio
echo 🔧 Creando acceso directo en el escritorio...

set "DESKTOP=%USERPROFILE%\Desktop"
set "SCRIPT_PATH=%RUTA_ACTUAL%\iniciar_sistema_permanente.bat"

echo [InternetShortcut] > "%DESKTOP%\METGO_3D_Sistema_Permanente.url"
echo URL=file:///%SCRIPT_PATH% >> "%DESKTOP%\METGO_3D_Sistema_Permanente.url"
echo IconFile=%RUTA_ACTUAL%\icono_metgo.ico >> "%DESKTOP%\METGO_3D_Sistema_Permanente.url"
echo IconIndex=0 >> "%DESKTOP%\METGO_3D_Sistema_Permanente.url"

echo ✅ Acceso directo creado en el escritorio
echo.

REM Crear script de inicio en carpeta de inicio
echo 🔧 Configurando inicio automático del usuario...

set "STARTUP=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
copy "%RUTA_ACTUAL%\iniciar_sistema_permanente.bat" "%STARTUP%\METGO_3D_Inicio_Automatico.bat" >nul

echo ✅ Script de inicio automático configurado
echo.

echo ===============================================
echo   CONFIGURACIÓN COMPLETADA
echo ===============================================
echo.
echo ✅ Tarea programada creada: METGO_3D_Sistema_Permanente
echo ✅ Acceso directo creado en el escritorio
echo ✅ Inicio automático configurado
echo.
echo 📋 INFORMACIÓN IMPORTANTE:
echo.
echo 🔄 El sistema se iniciará automáticamente al encender el PC
echo 🌐 Todos los dashboards estarán disponibles en:
echo    - Dashboard Principal: http://localhost:8501
echo    - Dashboard Meteorológico: http://localhost:8502
echo    - Dashboard Agrícola: http://localhost:8503
echo    - Y otros dashboards en puertos 8504-8513
echo.
echo 🛑 Para detener el inicio automático:
echo    1. Abre "Programador de tareas" de Windows
echo    2. Busca "METGO_3D_Sistema_Permanente"
echo    3. Haz clic derecho y selecciona "Deshabilitar"
echo.
echo 📞 Para soporte técnico, contacta al administrador del sistema
echo.
pause
