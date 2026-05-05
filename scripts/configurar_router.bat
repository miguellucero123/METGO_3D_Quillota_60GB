@echo off
echo ========================================
echo    CONFIGURACION ROUTER PARA WEB
echo    Dashboard METGO - Acceso Publico
echo ========================================
echo.

echo Paso 1: Configurando firewall de Windows...
netsh advfirewall firewall add rule name="METGO Dashboard 8501" dir=in action=allow protocol=TCP localport=8501
netsh advfirewall firewall add rule name="METGO Dashboard 8502" dir=in action=allow protocol=TCP localport=8502
netsh advfirewall firewall add rule name="METGO Dashboard 8503" dir=in action=allow protocol=TCP localport=8503
netsh advfirewall firewall add rule name="METGO Dashboard 8504" dir=in action=allow protocol=TCP localport=8504
netsh advfirewall firewall add rule name="METGO Dashboard 8505" dir=in action=allow protocol=TCP localport=8505

echo.
echo Firewall configurado correctamente
echo.

echo Paso 2: Informacion para configurar el router
echo.
echo IP Local: 192.168.1.7
echo Puerto: 8501
echo.
echo URLs que funcionaran:
echo Local:        http://localhost:8501
echo Red Local:    http://192.168.1.7:8501
echo Publica:      http://TU_IP_PUBLICA:8501
echo.

echo Paso 3: Configurar Router
echo.
echo 1. Abre tu navegador y ve a: http://192.168.1.1
echo 2. Usuario: admin
echo 3. Password: admin (o los de tu router)
echo 4. Busca "Port Forwarding" o "Redireccion de Puertos"
echo 5. Agrega regla:
echo    - Puerto Externo: 8501
echo    - Puerto Interno: 8501
echo    - IP Interna: 192.168.1.7
echo    - Protocolo: TCP
echo    - Estado: Habilitado
echo.

echo Paso 4: Obtener IP Publica
echo.
echo Ve a: http://whatismyipaddress.com
echo Tu IP publica sera: http://TU_IP_PUBLICA:8501
echo.

echo Paso 5: Ejecutar Dashboard
echo.
echo Ejecutando dashboard con acceso publico...
echo.

python -m streamlit run sistema_auth_dashboard_principal_metgo.py --server.port 8501 --server.address 0.0.0.0 --server.headless true

pause
