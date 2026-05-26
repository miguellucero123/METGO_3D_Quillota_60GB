@echo off
chcp 65001 >nul
cd /d "%~dp0..\.."
echo.
echo  PASO 2 — Agregar archivos al commit (staging)
echo  NO hace commit ni push todavia.
echo.
git add -A
git reset HEAD .env 2>nul
git reset HEAD .env.local 2>nul
git reset HEAD .streamlit\secrets.toml 2>nul
git reset HEAD -- .pytest_cache 2>nul
echo.
echo  Archivos que SE VAN A SUBIR:
echo  -------------------------
git diff --cached --name-status
echo.
git diff --cached --shortstat
echo.
echo  Si ve .env o secrets.toml arriba, CANCELE y no use el paso 3.
echo  Siguiente: 3_subir_hacer_commit.bat
echo.
pause
