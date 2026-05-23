@echo off
chcp 65001 >nul
setlocal EnableDelayedExpansion

if exist "%~dp0..\..\..\metgo_paths.py" (
  cd /d "%~dp0..\..\..\"
) else if exist "%~dp0..\..\metgo_paths.py" (
  cd /d "%~dp0..\..\"
) else (
  echo [ERROR] No se encontró metgo_paths.py.
  exit /b 1
)

set MSG=%~1
if "%MSG%"=="" (
  echo Mensaje de commit no indicado.
  set /p MSG="Escriba el mensaje de commit: "
)
if "!MSG!"=="" (
  echo [ERROR] Mensaje vacío. Cancelado.
  exit /b 1
)

echo ======================================================================
echo  METGO - Publicar cambios en GitHub
echo  Repo: %CD%
echo ======================================================================
echo.

git rev-parse --is-inside-work-tree >nul 2>&1
if errorlevel 1 (
  echo [ERROR] No es un repositorio Git.
  exit /b 1
)

echo [1/4] Estado actual...
git status -sb
echo.

echo [2/4] Agregando cambios (git add -A)...
echo [AVISO] No se subirán archivos listados en .gitignore (.env, node_modules, etc.)
git add -A
if errorlevel 1 (
  echo [ERROR] git add falló.
  exit /b 1
)

REM Quitar secretos del staging (.env.example NO se quita)
git rm --cached -f .env 2>nul
git reset HEAD .env 2>nul
git reset HEAD .env.local 2>nul
git reset HEAD .streamlit\secrets.toml 2>nul
git reset HEAD backend\12_Respaldos_Archivos\archivos_obsoletos\.env 2>nul

git diff --cached --name-only 2>nul | findstr /i /r "\\.env$ \\secrets\.toml$" >nul 2>&1
if not errorlevel 1 (
  echo.
  echo [ERROR] Aun hay credenciales en staging:
  git diff --cached --name-only | findstr /i /r "\\.env$ \\secrets\.toml$"
  echo Ejecute: quitar_secretos_del_staging.bat
  exit /b 1
)

git diff --cached --quiet
if not errorlevel 1 (
  echo.
  echo No hay cambios para commitear. Nada que publicar.
  exit /b 0
)

echo.
for /f %%c in ('git diff --cached --name-only 2^>nul ^| find /c /v ""') do set STAGED_COUNT=%%c
echo Archivos en staging: !STAGED_COUNT!  (lista completa omitida si son muchos)
git diff --cached --shortstat
if !STAGED_COUNT! LEQ 30 (
  git diff --cached --name-status
)
echo.
echo ======================================================================
echo  ATENCION: El script ESPERA su respuesta aqui abajo.
echo  Escriba S y pulse Enter para commit + push.
echo  Escriba N para cancelar.
echo  El commit puede tardar VARIOS MINUTOS si hay modelos .joblib grandes.
echo ======================================================================
echo.

set /p CONFIRM="¿Crear commit y push? (S/N): "
if /i not "!CONFIRM!"=="S" (
  echo Cancelado. Para deshacer staging: git reset HEAD
  exit /b 0
)

echo.
echo [3/4] Commit... (puede tardar 1-10 minutos, no cierre la ventana)
git commit -m "!MSG!"
if errorlevel 1 (
  echo [ERROR] git commit falló.
  exit /b 1
)

echo.
echo [4/4] Push... (subida a GitHub, puede tardar segun tamano del repo)
for /f "tokens=*" %%b in ('git branch --show-current 2^>nul') do set BRANCH=%%b
if not defined BRANCH set BRANCH=main

git rev-parse --abbrev-ref --symbolic-full-name "@{u}" >nul 2>&1
if errorlevel 1 (
  echo Primera vez en esta rama: git push -u origin !BRANCH!
  git push -u origin !BRANCH!
) else (
  git push origin !BRANCH!
)

if errorlevel 1 (
  echo.
  echo [ERROR] Push falló. Revise: revisar_estado_git.bat
  echo         ¿Tiene acceso al remoto? ¿GitHub Desktop / token configurado?
  exit /b 1
)

echo.
echo ======================================================================
echo  Listo. Cambios enviados a GitHub (rama !BRANCH!).
echo  Streamlit Cloud se actualizará si está vinculado al repo.
echo ======================================================================
pause
