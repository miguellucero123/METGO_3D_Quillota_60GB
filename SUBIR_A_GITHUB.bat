@echo off
chcp 65001 >nul
REM Muestra comandos para subida MANUAL (recomendado)
cd /d "%~dp0"
call "%~dp0SUBIR_GITHUB_MANUAL.bat"
