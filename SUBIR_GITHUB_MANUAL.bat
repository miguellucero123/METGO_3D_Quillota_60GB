@echo off
chcp 65001 >nul
cd /d "%~dp0"
cls
echo.
echo  METGO — Comandos para subir a GitHub (MANUAL)
echo  Copie y pegue en CMD o PowerShell.
echo  Guia completa: docs\manuales\SUBIR_GITHUB_MANUAL.md
echo.
echo  cd /d %CD%
echo.
echo  git status -sb
echo  git add -A
echo  git reset HEAD .env
echo  git reset HEAD .streamlit\secrets.toml
echo  git diff --cached --name-status
echo  git commit -m "feat: Visor de puertos integrado, utilidad por modulo y despliegue nube"
echo  git push origin master
echo.
echo  (Si su rama no es master, cambie la ultima linea:
echo   git branch --show-current)
echo.
pause
