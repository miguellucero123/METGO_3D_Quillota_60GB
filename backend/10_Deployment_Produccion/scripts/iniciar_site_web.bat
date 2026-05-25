@echo off
chcp 65001 >nul
if exist "%~dp0..\..\..\metgo_paths.py" (
  cd /d "%~dp0..\..\..\"
) else if exist "%~dp0..\..\metgo_paths.py" (
  cd /d "%~dp0..\..\"
) else (
  echo [ERROR] No se encontró metgo_paths.py.
  exit /b 1
)

set PORT=8505
echo ======================================================================
echo  METGO — Dashboard público (site-web) puerto %PORT%
echo ======================================================================
echo.
streamlit run site-web\streamlit\dashboard_web_publico.py --server.port %PORT%
pause
