@echo off
chcp 65001 >nul
setlocal EnableDelayedExpansion
call "%~dp0_git_ir_a_raiz.bat" || exit /b 1

echo ======================================================================
echo  PASO 3/3 — Solo PUSH a GitHub (sin commit)
echo ======================================================================
echo.

git rev-parse --is-inside-work-tree >nul 2>&1 || (
  echo [ERROR] No es un repositorio Git.
  exit /b 1
)

for /f "tokens=*" %%b in ('git branch --show-current 2^>nul') do set BRANCH=%%b
if not defined BRANCH set BRANCH=main

echo Rama: !BRANCH!
git remote -v
echo.

git status -sb
echo.

REM ¿Hay commits locales sin subir?
git rev-parse --abbrev-ref --symbolic-full-name "@{u}" >nul 2>&1
if errorlevel 1 (
  echo [AVISO] La rama no tiene upstream. Se usara: git push -u origin !BRANCH!
  set FIRST_PUSH=1
) else (
  for /f "tokens=2" %%a in ('git rev-list --left-right --count "@{u}"...HEAD 2^>nul') do set AHEAD=%%a
  if defined AHEAD if !AHEAD! EQU 0 (
    echo No hay commits locales por delante del remoto. Nada que subir.
    echo Si falta hacer commit: 1_preparar_staging_github.bat y 2_commit_github.bat
    pause
    exit /b 0
  )
  echo Commits por subir ^(adelante del remoto^): !AHEAD!
)

echo.
set /p CONFIRM="¿Hacer push a origin/!BRANCH!? (S/N): "
if /i not "!CONFIRM!"=="S" (
  echo Cancelado.
  exit /b 0
)

echo.
echo Subiendo... (puede tardar segun tamano del repo)
if defined FIRST_PUSH (
  git push -u origin !BRANCH!
) else (
  git push origin !BRANCH!
)

if errorlevel 1 (
  echo.
  echo [ERROR] Push fallo.
  echo  - Revise: revisar_estado_git.bat
  echo  - Si pide actualizar: git pull --rebase origin !BRANCH!
  exit /b 1
)

echo.
echo ======================================================================
echo  Listo. Cambios en GitHub (rama !BRANCH!).
echo  Netlify y Render se actualizan si estan vinculados al repo.
echo ======================================================================
pause
