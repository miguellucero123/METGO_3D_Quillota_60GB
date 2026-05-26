@echo off
chcp 65001 >nul
cd /d "%~dp0..\.."
echo.
echo  PASO 3 — Hacer commit (guardar cambios en Git local)
echo.
git diff --cached --quiet
if %ERRORLEVEL%==0 (
  echo  No hay archivos preparados. Ejecute primero: 2_subir_agregar_archivos.bat
  pause
  exit /b 1
)
echo  Archivos en este commit:
git diff --cached --name-status
echo.
set /p MENSAJE=Escriba el mensaje del commit: 
if "%MENSAJE%"=="" (
  echo  Cancelado: mensaje vacio.
  pause
  exit /b 1
)
git commit -m "%MENSAJE%"
echo.
if %ERRORLEVEL%==0 (
  echo  Commit listo. Siguiente: 4_subir_push_github.bat
) else (
  echo  Error al hacer commit.
)
pause
