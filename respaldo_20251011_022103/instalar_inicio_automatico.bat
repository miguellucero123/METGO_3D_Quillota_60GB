@echo off
echo ============================================================
echo INSTALANDO INICIO AUTOMATICO DEL SISTEMA METGO
echo ============================================================
echo.

REM Crear el script de inicio
echo Creando script de inicio...
echo @echo off > "iniciar_metgo.bat"
echo cd /d "%~dp0" >> "iniciar_metgo.bat"
echo python iniciar_sistema_automatico.py >> "iniciar_metgo.bat"
echo pause >> "iniciar_metgo.bat"

REM Obtener la ruta actual
set "RUTA_ACTUAL=%~dp0"
set "RUTA_ACTUAL=%RUTA_ACTUAL:~0,-1%"

echo.
echo Ruta del sistema METGO: %RUTA_ACTUAL%
echo.

REM Crear entrada en el registro para inicio automático
echo Creando entrada en el registro...
reg add "HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run" /v "SistemaMETGO" /t REG_SZ /d "\"%RUTA_ACTUAL%\iniciar_metgo.bat\"" /f

if %errorlevel% == 0 (
    echo.
    echo ============================================================
    echo INSTALACION COMPLETADA EXITOSAMENTE
    echo ============================================================
    echo.
    echo El Sistema METGO se iniciara automaticamente al encender Windows.
    echo.
    echo Para desinstalar el inicio automatico, ejecuta:
    echo desinstalar_inicio_automatico.bat
    echo.
    echo Para iniciar manualmente ahora, ejecuta:
    echo iniciar_metgo.bat
    echo.
) else (
    echo.
    echo ============================================================
    echo ERROR EN LA INSTALACION
    echo ============================================================
    echo.
    echo No se pudo instalar el inicio automatico.
    echo Ejecuta este archivo como Administrador.
    echo.
)

pause
