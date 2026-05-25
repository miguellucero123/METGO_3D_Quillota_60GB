@echo off
chcp 65001 >nul
setlocal EnableDelayedExpansion
call "%~dp0_git_ir_a_raiz.bat" || exit /b 1

set MSG=%~1
if "%MSG%"=="" (
  if exist "%~dp0MENSAJE_COMMIT_SUGERIDO.txt" (
    echo Mensaje sugerido en MENSAJE_COMMIT_SUGERIDO.txt:
    type "%~dp0MENSAJE_COMMIT_SUGERIDO.txt"
    echo.
  )
  set /p MSG="Escriba el mensaje de commit: "
)
if "!MSG!"=="" (
  echo [ERROR] Mensaje vacio. Cancelado.
  exit /b 1
)

echo ======================================================================
echo  PASO 2/3 — Solo COMMIT (sin push)
echo ======================================================================
echo.

git diff --cached --quiet
if not errorlevel 1 (
  echo [AVISO] No hay nada en staging.
  echo Ejecute primero: 1_preparar_staging_github.bat
  echo O: git add -A
  pause
  exit /b 1
)

echo Mensaje: !MSG!
echo.
git commit -m "!MSG!"
if errorlevel 1 (
  echo [ERROR] git commit fallo.
  exit /b 1
)

echo.
echo Commit creado. Siguiente paso:
echo   3_push_github.bat
echo.
git log -1 --oneline
pause
