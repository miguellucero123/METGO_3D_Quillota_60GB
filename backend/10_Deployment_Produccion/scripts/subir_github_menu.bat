@echo off
chcp 65001 >nul
setlocal
call "%~dp0_git_ir_a_raiz.bat" || exit /b 1

:menu
cls
echo ======================================================================
echo  METGO — Subir cambios a GitHub
echo  Carpeta: %CD%
echo ======================================================================
echo.
echo  1  Revisar estado (sin cambiar nada)
echo  2  Preparar staging — git add (PASO 1, usted hara el commit)
echo  3  Commit con mensaje sugerido (archivo .txt, PASO 2)
echo  4  Commit con mensaje personalizado (PASO 2)
echo  5  Push a GitHub (PASO 3)
echo  6  Todo en uno: add + commit + push (publicar_github.bat)
echo  7  Quitar .env del staging (si fallo por secretos)
echo  0  Salir
echo.
set /p OPC="Elija opcion: "

if "%OPC%"=="1" call "%~dp0revisar_estado_git.bat" & goto menu
if "%OPC%"=="2" call "%~dp01_preparar_staging_github.bat" & goto menu
if "%OPC%"=="3" call "%~dp02_commit_github_sugerido.bat" & goto menu
if "%OPC%"=="4" (
  set /p MSG="Mensaje de commit: "
  call "%~dp02_commit_github.bat" "!MSG!"
  goto menu
)
if "%OPC%"=="5" call "%~dp03_push_github.bat" & goto menu
if "%OPC%"=="6" (
  call "%~dp0publicar_github.bat" "feat: integracion API-Vue fases 4-10 y escalamiento MVP"
  goto menu
)
if "%OPC%"=="7" call "%~dp0quitar_secretos_del_staging.bat" & goto menu
if "%OPC%"=="0" exit /b 0

echo Opcion no valida.
pause
goto menu
