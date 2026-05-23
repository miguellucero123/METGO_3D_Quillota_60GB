@echo off
chcp 65001 >nul
setlocal

if exist "%~dp0..\..\..\metgo_paths.py" (
  cd /d "%~dp0..\..\..\"
) else (
  cd /d "%~dp0..\..\"
)

echo ======================================================================
echo  METGO - Configurar remoto GitHub (solo una vez)
echo ======================================================================
echo.
echo Ejemplo de URL:
echo   https://github.com/miguellucero123/METGO_3D_Quillota_60GB.git
echo   git@github.com:miguellucero123/METGO_3D_Quillota_60GB.git
echo.

set /p URL="URL del repositorio en GitHub: "
if "%URL%"=="" (
  echo Cancelado.
  exit /b 1
)

git remote get-url origin >nul 2>&1
if errorlevel 1 (
  git remote add origin "%URL%"
  echo Remoto 'origin' creado.
) else (
  echo Remoto 'origin' actual:
  git remote get-url origin
  set /p OK="¿Reemplazar por la nueva URL? (S/N): "
  if /i "%OK%"=="S" git remote set-url origin "%URL%"
)

echo.
git remote -v
echo.
for /f "tokens=*" %%b in ('git branch --show-current 2^>nul') do set BRANCH=%%b
if not defined BRANCH set BRANCH=main
echo Para el primer push use:
echo   git push -u origin %BRANCH%
echo o ejecute: publicar_github.bat "Su mensaje de commit"
echo.
pause
