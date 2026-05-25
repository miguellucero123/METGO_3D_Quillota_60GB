@echo off
chcp 65001 >nul
if exist "%~dp0..\..\..\metgo_paths.py" (
  cd /d "%~dp0..\..\..\"
) else (
  cd /d "%~dp0..\..\"
)

echo METGO — Tests (python -m pytest)
echo %CD%
echo.

python -m pip install -q pytest PyYAML diskcache 2>nul
python -m pytest tests/ -q --tb=short %*
set EXIT=%ERRORLEVEL%

if %EXIT% NEQ 0 (echo [ERROR] Codigo %EXIT%) else (echo OK)
pause
exit /b %EXIT%
