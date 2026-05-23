@echo off
chcp 65001 >nul
setlocal

if exist "%~dp0..\..\..\metgo_paths.py" (
  cd /d "%~dp0..\..\..\"
) else (
  cd /d "%~dp0..\..\"
)

echo Quitando archivos sensibles del staging (no se suben a GitHub)...
echo.

REM Dejar de rastrear .env en raíz si ya estaba en Git
git rm --cached -f .env 2>nul
git reset HEAD .env 2>nul
git reset HEAD .env.local 2>nul
git reset HEAD .streamlit\secrets.toml 2>nul
git reset HEAD backend\12_Respaldos_Archivos\archivos_obsoletos\.env 2>nul

REM .env.example SÍ debe poder subirse
echo.
echo Archivos .env aún en staging (deberia estar vacio):
git diff --cached --name-only 2>nul | findstr /i /r "\\.env$ \secrets\.toml$"
if errorlevel 1 (
  echo   (ninguno - OK)
) else (
  git diff --cached --name-only 2>nul | findstr /i /r "\\.env$ \secrets\.toml$"
  echo.
  echo Si aparece .env arriba, NO haga push hasta quitarlo.
)

echo.
echo Listo. Puede ejecutar de nuevo: publicar_github.bat
pause
