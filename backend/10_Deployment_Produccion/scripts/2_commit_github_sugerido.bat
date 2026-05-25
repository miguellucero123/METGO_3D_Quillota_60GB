@echo off
chcp 65001 >nul
call "%~dp0_git_ir_a_raiz.bat" || exit /b 1

if not exist "%~dp0MENSAJE_COMMIT_SUGERIDO.txt" (
  echo [ERROR] Falta MENSAJE_COMMIT_SUGERIDO.txt
  exit /b 1
)

echo Commit con mensaje de MENSAJE_COMMIT_SUGERIDO.txt
echo.
type "%~dp0MENSAJE_COMMIT_SUGERIDO.txt"
echo.
set /p CONFIRM="¿Usar este mensaje? (S/N): "
if /i not "%CONFIRM%"=="S" exit /b 0

git diff --cached --quiet
if not errorlevel 1 (
  echo Ejecute antes: 1_preparar_staging_github.bat
  pause
  exit /b 1
)

git commit -F "%~dp0MENSAJE_COMMIT_SUGERIDO.txt"
if errorlevel 1 exit /b 1

echo.
echo OK. Siguiente: 3_push_github.bat
git log -1 --oneline
pause
