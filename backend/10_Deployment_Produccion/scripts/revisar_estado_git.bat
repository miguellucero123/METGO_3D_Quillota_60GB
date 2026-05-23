@echo off
chcp 65001 >nul
setlocal EnableDelayedExpansion

REM Ir a la raíz del repo (layout capas o legacy)
if exist "%~dp0..\..\..\metgo_paths.py" (
  cd /d "%~dp0..\..\..\"
) else if exist "%~dp0..\..\metgo_paths.py" (
  cd /d "%~dp0..\..\"
) else (
  echo [ERROR] No se encontró metgo_paths.py. Ejecute desde el clon METGO.
  exit /b 1
)

echo ======================================================================
echo  METGO - Estado del repositorio Git
echo  Carpeta: %CD%
echo  Fecha:   %DATE% %TIME%
echo ======================================================================
echo.

git rev-parse --is-inside-work-tree >nul 2>&1
if errorlevel 1 (
  echo [ERROR] Esta carpeta NO es un repositorio Git.
  echo         Inicialice con: git init
  exit /b 1
)

echo --- Rama actual ---
git branch -vv
echo.

echo --- Remotos (GitHub) ---
git remote -v
if errorlevel 1 echo (sin remotos configurados)
echo.

echo --- Resumen (git status -sb) ---
git status -sb
echo.

echo --- Comparación con remoto ---
for /f "tokens=*" %%b in ('git branch --show-current 2^>nul') do set BRANCH=%%b
if not defined BRANCH set BRANCH=main
git rev-parse --abbrev-ref --symbolic-full-name "@{u}" >nul 2>&1
if errorlevel 1 (
  echo La rama '%BRANCH%' no tiene upstream. Aún no hay 'git push -u origin %BRANCH%'.
) else (
  git rev-list --left-right --count "@{u}"...HEAD 2>nul
  if not errorlevel 1 (
    for /f "tokens=1,2" %%a in ('git rev-list --left-right --count "@{u}"...HEAD 2^>nul') do (
      echo Detrás del remoto: %%a commits ^| Adelante del remoto: %%b commits
    )
  )
)
echo.

echo --- Últimos 5 commits ---
git log -5 --oneline --decorate
echo.

echo --- Archivos modificados (conteo) ---
git status --porcelain | find /c /v ""
echo líneas en 'git status --porcelain' ^(cada línea = un archivo^)
echo.

echo --- ¿Hay .env en staging? (no debería subirse) ---
git diff --cached --name-only 2>nul | findstr /i "\.env" >nul && (
  echo [AVISO] Hay archivos .env en el area de staging. Revise antes de publicar.
) || echo OK: no hay .env en staging.
git status --porcelain | findstr /i "\.env" >nul && (
  echo [AVISO] Hay cambios locales en .env ^(normalmente ignorado por .gitignore^).
)
echo.

echo ======================================================================
echo  Siguiente paso: publicar_github.bat
echo  Documentación: docs\manuales\PUBLICAR_GITHUB.md
echo ======================================================================
pause
