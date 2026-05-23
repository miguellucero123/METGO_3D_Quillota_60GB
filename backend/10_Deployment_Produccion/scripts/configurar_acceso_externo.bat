cd /d "%~dp0..\.."
@echo off
echo ========================================
echo    CONFIGURACION DE ACCESO EXTERNO
echo    Dashboard METGO - Quillota
echo ========================================
echo.

echo 🔧 Configurando firewall de Windows...
netsh advfirewall firewall add rule name="Streamlit Dashboard 8501" dir=in action=allow protocol=TCP localport=8501
netsh advfirewall firewall add rule name="Streamlit Dashboard 8502" dir=in action=allow protocol=TCP localport=8502
netsh advfirewall firewall add rule name="Streamlit Dashboard 8503" dir=in action=allow protocol=TCP localport=8503
netsh advfirewall firewall add rule name="Streamlit Dashboard 8504" dir=in action=allow protocol=TCP localport=8504
netsh advfirewall firewall add rule name="Streamlit Dashboard 8505" dir=in action=allow protocol=TCP localport=8505

echo.
echo ✅ Firewall configurado
echo.

echo 🌐 URLs Disponibles:
echo    🏠 Local:        http://localhost:8501
echo    🏢 Red Local:    http://192.168.1.7:8501
echo    🌍 Externa:      http://200.104.179.146:8501
echo.

echo ⚠️  IMPORTANTE PARA ACCESO EXTERNO:
echo.
echo 1. ACCESO AL ROUTER:
echo    - Abre tu navegador y ve a: http://192.168.1.1
echo    - Usuario/Password: admin/admin (o los de tu router)
echo.
echo 2. CONFIGURAR PORT FORWARDING:
echo    - Busca "Port Forwarding" o "Redirección de Puertos"
echo    - Agrega regla:
echo      * Puerto Externo: 8501
echo      * Puerto Interno: 8501
echo      * IP Interna: 192.168.1.7
echo      * Protocolo: TCP
echo.
echo 3. IP PUBLICA FIJA (OPCIONAL):
echo    - Contacta a tu ISP para IP fija
echo    - O usa servicios como No-IP, DynDNS
echo.
echo 🚀 Ejecutando dashboard...
echo    Presiona Ctrl+C para detener
echo.

python -m streamlit run sistema_auth_dashboard_principal_metgo.py --server.port 8501 --server.address 0.0.0.0 --server.headless true

pause
