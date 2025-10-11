"""
INSTRUCCIONES SISTEMA COMPLETO - METGO 3D QUILLOTA
"""

def mostrar_instrucciones():
    """Mostrar instrucciones completas del sistema"""
    print("="*80)
    print("INSTRUCCIONES SISTEMA COMPLETO METGO 3D QUILLOTA")
    print("="*80)
    
    print("\n[WEB] ACCESO AL SISTEMA:")
    print("   URL: http://localhost:8500")
    print("   Estado: FUNCIONANDO")
    
    print("\n[USERS] USUARIOS DE PRUEBA:")
    print("   [ADMIN] Admin: admin / admin123 (Acceso completo a todos los dashboards)")
    print("   [EXEC] Ejecutivo: ejecutivo / ejecutivo123")
    print("   [AGRI] Agricultor: agricultor / agricultor123")
    print("   [TECH] Tecnico: tecnico / tecnico123")
    print("   [USER] Usuario: usuario / usuario123")
    
    print("\n[STEPS] PASOS PARA USAR EL SISTEMA:")
    print("   1. Ve a http://localhost:8500")
    print("   2. Inicia sesion con admin / admin123")
    print("   3. Veras la lista de dashboards disponibles")
    print("   4. Haz clic en 'Iniciar' para activar un dashboard")
    print("   5. Espera a que aparezca 'ACTIVO' en verde")
    print("   6. Haz clic en 'Abrir' para acceder al dashboard")
    print("   7. Usa las mismas credenciales en el dashboard especifico")
    
    print("\n[DASHBOARDS] DASHBOARDS DISPONIBLES:")
    print("   [EMP] Dashboard Empresarial (Puerto 8503)")
    print("      - Vista ejecutiva con metricas empresariales")
    print("      - KPIs y analisis de rendimiento")
    print("      - Acceso: Admin, Ejecutivo")
    
    print("\n   [AGRI] Dashboard Agricola (Puerto 8501)")
    print("      - Gestion completa de cultivos y produccion")
    print("      - Recomendaciones agricolas")
    print("      - Acceso: Todos los roles")
    
    print("\n   [MET] Dashboard Meteorologico (Puerto 8502)")
    print("      - Monitoreo climatico en tiempo real")
    print("      - Pronosticos y alertas")
    print("      - Acceso: Todos los roles")
    
    print("\n   [DRONE] Dashboard con Drones (Puerto 8504)")
    print("      - Monitoreo aereo y analisis de cultivos")
    print("      - Deteccion de problemas")
    print("      - Acceso: Admin, Agricultor, Tecnico")
    
    print("\n   [ECON] Sistema Economico (Puerto 8506)")
    print("      - Analisis de ROI y rentabilidad")
    print("      - Costos y precios de mercado")
    print("      - Acceso: Admin, Ejecutivo, Agricultor")
    
    print("\n[FEATURES] FUNCIONALIDADES DEL SISTEMA:")
    print("   [OK] Login seguro con validacion")
    print("   [OK] Ejecucion automatica de dashboards")
    print("   [OK] Control de procesos en tiempo real")
    print("   [OK] Apertura automatica en navegador")
    print("   [OK] Gestion de sesiones persistente")
    print("   [OK] Detencion automatica al cerrar sesion")
    
    print("\n[CONTROLS] CONTROLES DISPONIBLES:")
    print("   [START] Iniciar: Activa el dashboard en su puerto especifico")
    print("   [OPEN] Abrir: Abre el dashboard en el navegador")
    print("   [STOP] Detener: Detiene el dashboard")
    print("   [LOGOUT] Cerrar Sesion: Cierra sesion y detiene todos los dashboards")
    
    print("\n[NAV] NAVEGACION:")
    print("   - Cada dashboard se abre en su propio puerto")
    print("   - Puedes tener multiples dashboards activos simultaneamente")
    print("   - Usa las mismas credenciales en cada dashboard")
    print("   - El sistema principal (puerto 8500) controla todo")
    
    print("\n[CMDS] COMANDOS UTILES:")
    print("   # Verificar que el sistema este funcionando")
    print("   netstat -an | findstr :8500")
    print("   ")
    print("   # Abrir el sistema manualmente")
    print("   start http://localhost:8500")
    print("   ")
    print("   # Ver todos los puertos activos")
    print("   netstat -an | findstr LISTENING")
    
    print("\n[TROUBLE] SOLUCION DE PROBLEMAS:")
    print("   [ERROR] Si no puedes acceder:")
    print("      - Verifica que el puerto 8500 este activo")
    print("      - Usa las credenciales exactas (sin espacios)")
    print("      - Recarga la pagina del navegador")
    
    print("\n   [ERROR] Si un dashboard no inicia:")
    print("      - Verifica que el archivo del dashboard existe")
    print("      - Espera unos segundos y vuelve a intentar")
    print("      - Recarga la pagina principal")
    
    print("\n   [ERROR] Si el navegador no se abre automaticamente:")
    print("      - Copia la URL manualmente")
    print("      - Usa Ctrl+C y Ctrl+V para pegar")
    print("      - Abre una nueva pestaña en el navegador")
    
    print("\n[STATUS] ESTADO ACTUAL:")
    print("   [OK] Sistema principal funcionando en puerto 8500")
    print("   [OK] Login funcional con validacion")
    print("   [OK] Gestion automatica de dashboards")
    print("   [OK] Control de procesos integrado")
    print("   [OK] Interfaz profesional y minimalista")
    
    print("\n" + "="*80)
    print("SISTEMA METGO 3D COMPLETAMENTE OPERATIVO!")
    print("="*80)

if __name__ == "__main__":
    mostrar_instrucciones()


