@echo off
chcp 65001 >nul
cd /d "%~dp0..\.."
:menu
cls
echo.
echo  ========================================
echo   METGO 3D — Subir a GitHub (MANUAL)
echo  ========================================
echo   Repo: miguellucero123/METGO_3D_Quillota_60GB
echo   Rama: master
echo   Carpeta: %CD%
echo  ========================================
echo.
echo   1  Revisar estado (status, log)
echo   2  Preparar staging (add + quitar secretos)
echo   3  Commit (usted escribe el mensaje)
echo   4  Push origin master
echo.
echo   5  Ver comandos para copiar/pegar (COMANDOS_GIT_MANUAL.txt)
echo   6  Abrir guia Markdown (docs)
echo   0  Salir
echo.
set /p OP=Opcion: 
if "%OP%"=="1" call "%~dp001_revisar_estado.bat" & goto menu
if "%OP%"=="2" call "%~dp002_preparar_staging.bat" & goto menu
if "%OP%"=="3" call "%~dp003_commit_manual.bat" & goto menu
if "%OP%"=="4" call "%~dp004_push_master.bat" & goto menu
if "%OP%"=="5" start notepad "%~dp0COMANDOS_GIT_MANUAL.txt" & goto menu
if "%OP%"=="6" start "" "%~dp0..\..\docs\manuales\SUBIR_GITHUB_MANUAL.md" & goto menu
if "%OP%"=="0" exit /b 0
goto menu
