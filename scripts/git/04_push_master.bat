@echo off
chcp 65001 >nul
cd /d "%~dp0..\.."
echo.
echo ===== METGO — Push a GitHub (rama master) =====
echo  Remoto: https://github.com/miguellucero123/METGO_3D_Quillota_60GB.git
echo.
for /f "delims=" %%b in ('git branch --show-current') do set RAMA=%%b
echo  Rama local: %RAMA%
echo.
if /i not "%RAMA%"=="master" (
  echo  AVISO: su rama es "%RAMA%", no "master".
  set /p OK=¿Push igual a origin %RAMA%? (S/N): 
  if /i not "!OK!"=="S" exit /b 0
  git push -u origin %RAMA%
) else (
  git push origin master
)
if %ERRORLEVEL%==0 (
  echo.
  echo  Push completado. Revise: https://github.com/miguellucero123/METGO_3D_Quillota_60GB
) else (
  echo.
  echo  Fallo el push. Pruebe:
  echo    git pull --rebase origin master
  echo    git push origin master
)
echo.
pause
