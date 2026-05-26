@echo off
chcp 65001 >nul
cd /d "%~dp0..\.."
echo.
echo  PASO 4 — Subir a GitHub (push)
echo  Destino: origin master
echo.
git push origin master
if %ERRORLEVEL%==0 (
  echo.
  echo  Listo. Ver en el navegador:
  echo  https://github.com/miguellucero123/METGO_3D_Quillota_60GB
) else (
  echo.
  echo  Si dice "rejected" o "fetch first", en PowerShell ejecute:
  echo    git pull --rebase origin master
  echo    git push origin master
  echo.
  echo  Si pide usuario/contrasena: use GitHub Desktop o inicie sesion en Git.
)
echo.
pause
