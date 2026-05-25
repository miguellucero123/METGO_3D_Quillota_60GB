@echo off
REM Uso interno: deja el directorio actual en la raíz del repo METGO.
if exist "%~dp0..\..\..\metgo_paths.py" (
  cd /d "%~dp0..\..\..\"
  exit /b 0
)
if exist "%~dp0..\..\metgo_paths.py" (
  cd /d "%~dp0..\..\"
  exit /b 0
)
echo [ERROR] No se encontró metgo_paths.py
exit /b 1
