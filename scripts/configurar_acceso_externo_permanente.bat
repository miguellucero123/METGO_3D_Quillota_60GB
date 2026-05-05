@echo off
echo ===============================================
echo   CONFIGURAR ACCESO EXTERNO PERMANENTE METGO
echo ===============================================
echo.

REM Verificar permisos de administrador
net session >nul 2>&1
if errorlevel 1 (
    echo ERROR: Este script requiere permisos de administrador
    echo Haz clic derecho en el archivo y selecciona "Ejecutar como administrador"
    pause
    exit /b 1
)

echo ✅ Permisos de administrador verificados
echo.

REM Obtener IP local
echo 🔍 Detectando dirección IP local...
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4"') do (
    for /f "tokens=1" %%b in ("%%a") do (
        set "IP_LOCAL=%%b"
        goto :ip_found
    )
)
:ip_found

echo 📡 IP Local detectada: %IP_LOCAL%
echo.

REM Configurar reglas de firewall para todos los puertos
echo 🔧 Configurando reglas de firewall...

REM Puertos de los dashboards (8501-8513)
for /L %%i in (8501,1,8513) do (
    echo Configurando puerto %%i...
    netsh advfirewall firewall add rule name="METGO_Dashboard_%%i" dir=in action=allow protocol=TCP localport=%%i
    netsh advfirewall firewall add rule name="METGO_Dashboard_%%i_Out" dir=out action=allow protocol=TCP localport=%%i
)

echo ✅ Reglas de firewall configuradas
echo.

REM Crear script de configuración de router
echo 🔧 Creando script de configuración de router...

(
echo @echo off
echo echo ===============================================
echo echo   CONFIGURACIÓN DE ROUTER PARA METGO_3D
echo echo ===============================================
echo echo.
echo echo 📋 INSTRUCCIONES PARA CONFIGURAR EL ROUTER:
echo echo.
echo echo 1. Abre el navegador y ve a: http://192.168.1.1
echo echo    ^(o la IP de tu router^)
echo echo.
echo echo 2. Inicia sesión con las credenciales del router
echo echo.
echo echo 3. Busca la sección "Port Forwarding" o "Redirección de puertos"
echo echo.
echo echo 4. Agrega las siguientes reglas:
echo echo.
for /L %%i in (8501,1,8513) do (
    echo echo    - Puerto: %%i
    echo echo      Protocolo: TCP
    echo echo      IP Interna: %IP_LOCAL%
    echo echo      Puerto Interno: %%i
    echo echo      Descripción: METGO Dashboard %%i
    echo echo.
)
echo echo 5. Guarda la configuración y reinicia el router
echo echo.
echo echo 🌐 DESPUÉS DE CONFIGURAR EL ROUTER:
echo echo.
echo echo Los dashboards estarán disponibles desde internet en:
for /L %%i in (8501,1,8513) do (
    echo echo    - Dashboard %%i: http://TU_IP_PUBLICA:%%i
)
echo echo.
echo echo 📱 Para acceso móvil desde cualquier lugar:
echo echo    1. Conecta tu dispositivo a la misma red WiFi
echo echo    2. Usa las URLs con la IP local: %IP_LOCAL%
echo echo    3. Ejemplo: http://%IP_LOCAL%:8501
echo echo.
echo pause
) > configurar_router_metgo.bat

echo ✅ Script de configuración de router creado
echo.

REM Crear archivo de información de acceso
echo 🔧 Creando archivo de información de acceso...

(
echo ===============================================
echo   INFORMACIÓN DE ACCESO METGO_3D
echo ===============================================
echo.
echo 📅 Configurado el: %date% %time%
echo 🌐 IP Local del servidor: %IP_LOCAL%
echo.
echo ===============================================
echo   DASHBOARDS DISPONIBLES
echo ===============================================
echo.
echo 🏠 Dashboard Principal: http://%IP_LOCAL%:8501
echo 🌤️ Dashboard Meteorológico: http://%IP_LOCAL%:8502
echo 🌾 Dashboard Agrícola: http://%IP_LOCAL%:8503
echo 🔍 Dashboard Monitoreo: http://%IP_LOCAL%:8504
echo 🤖 Dashboard IA/ML: http://%IP_LOCAL%:8505
echo 📊 Dashboard Visualizaciones: http://%IP_LOCAL%:8506
echo 📈 Dashboard Global: http://%IP_LOCAL%:8507
echo 🌾 Dashboard Agricultura Precisión: http://%IP_LOCAL%:8508
echo 📊 Dashboard Comparativo: http://%IP_LOCAL%:8509
echo 🔬 Dashboard Alertas: http://%IP_LOCAL%:8510
echo 📊 Dashboard Simple: http://%IP_LOCAL%:8511
echo 🔄 Dashboard Unificado: http://%IP_LOCAL%:8512
echo 📱 Dashboard Móvil: http://%IP_LOCAL%:8513
echo.
echo ===============================================
echo   CREDENCIALES DE ACCESO
echo ===============================================
echo.
echo 🔐 Usuario: admin
echo 🔑 Contraseña: admin123
echo.
echo 🔐 Usuario: user
echo 🔑 Contraseña: user123
echo.
echo 🔐 Usuario: metgo
echo 🔑 Contraseña: metgo2025
echo.
echo ===============================================
echo   ACCESO DESDE DISPOSITIVOS MÓVILES
echo ===============================================
echo.
echo 📱 Para acceder desde tu celular:
echo    1. Conecta tu celular a la misma red WiFi
echo    2. Abre el navegador
echo    3. Ve a: http://%IP_LOCAL%:8501
echo    4. Usa las credenciales de arriba
echo.
echo 🌐 Para acceso desde internet (requiere configuración de router):
echo    1. Configura el router siguiendo las instrucciones en:
echo       configurar_router_metgo.bat
echo    2. Usa tu IP pública en lugar de %IP_LOCAL%
echo.
echo ===============================================
echo   MANTENIMIENTO DEL SISTEMA
echo ===============================================
echo.
echo 🔄 El sistema se reinicia automáticamente si falla
echo 📊 Monitoreo continuo de todos los dashboards
echo 🛠️ Logs del sistema en: logs/sistema_permanente.log
echo.
echo 🛑 Para detener el sistema:
echo    1. Abre "Programador de tareas" de Windows
echo    2. Busca "METGO_3D_Sistema_Permanente"
echo    3. Haz clic derecho y selecciona "Deshabilitar"
echo.
echo 📞 Para soporte técnico, contacta al administrador
) > INFORMACION_ACCESO_METGO.txt

echo ✅ Archivo de información creado: INFORMACION_ACCESO_METGO.txt
echo.

REM Crear script de monitoreo de red
echo 🔧 Creando script de monitoreo de red...

(
echo @echo off
echo echo ===============================================
echo echo   MONITOR DE RED METGO_3D
echo echo ===============================================
echo echo.
echo echo 🔍 Verificando conectividad de dashboards...
echo echo.
echo.
echo for /L %%%%i in ^(8501,1,8513^) do ^(
echo     echo Verificando puerto %%%%i...
echo     netstat -an ^| findstr "%%%%i" ^| findstr "LISTENING" ^>nul
echo     if errorlevel 1 ^(
echo         echo ❌ Puerto %%%%i no está activo
echo     ^) else ^(
echo         echo ✅ Puerto %%%%i activo
echo     ^)
echo ^)
echo echo.
echo echo 📊 Estado de conexiones:
echo netstat -an ^| findstr "8501\|8502\|8503\|8504\|8505\|8506\|8507\|8508\|8509\|8510\|8511\|8512\|8513"
echo echo.
echo pause
) > monitorear_red_metgo.bat

echo ✅ Script de monitoreo creado: monitorear_red_metgo.bat
echo.

echo ===============================================
echo   CONFIGURACIÓN COMPLETADA
echo ===============================================
echo.
echo ✅ Reglas de firewall configuradas para puertos 8501-8513
echo ✅ Script de configuración de router creado
echo ✅ Archivo de información de acceso creado
echo ✅ Script de monitoreo de red creado
echo.
echo 📋 ARCHIVOS CREADOS:
echo    - configurar_router_metgo.bat
echo    - INFORMACION_ACCESO_METGO.txt
echo    - monitorear_red_metgo.bat
echo.
echo 🌐 ACCESO LOCAL DISPONIBLE EN:
echo    http://%IP_LOCAL%:8501 (Dashboard Principal)
echo.
echo 📱 Para acceso desde celular:
echo    1. Conecta tu celular a la misma red WiFi
echo    2. Ve a: http://%IP_LOCAL%:8501
echo    3. Usa las credenciales: admin/admin123
echo.
echo 📖 Lee INFORMACION_ACCESO_METGO.txt para más detalles
echo.
pause
