@echo off
chcp 65001 >nul
REM Atajo legacy → menu manual actualizado
cd /d "%~dp0"
call "%~dp0SUBIR_GITHUB_MENU.bat"
