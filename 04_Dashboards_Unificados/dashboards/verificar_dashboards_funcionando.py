"""
VERIFICAR DASHBOARDS FUNCIONANDO - METGO 3D QUILLOTA
Script para verificar que los dashboards estén funcionando correctamente
"""

import os
import requests
import webbrowser

def verificar_dashboards():
    """Verificar que los dashboards estén funcionando"""
    print("="*70)
    print("VERIFICANDO DASHBOARDS METGO 3D QUILLOTA")
    print("="*70)
    
    # Verificar archivos existentes
    dashboards = {
        'dashboard_empresarial': {
            'archivo': 'dashboard_empresarial_unificado_metgo.py',
            'puerto': 8503,
            'nombre': 'Dashboard Empresarial'
        },
        'dashboard_agricola': {
            'archivo': 'dashboard_agricola_avanzado.py',
            'puerto': 8501,
            'nombre': 'Dashboard Agricola'
        },
        'dashboard_meteorologico': {
            'archivo': 'dashboard_meteorologico_metgo.py',
            'puerto': 8502,
            'nombre': 'Dashboard Meteorologico'
        },
        'dashboard_drones': {
            'archivo': 'dashboard_unificado_metgo_con_drones.py',
            'puerto': 8504,
            'nombre': 'Dashboard con Drones'
        },
        'sistema_economico': {
            'archivo': 'analisis_economico_agricola_metgo_con_conversion.py',
            'puerto': 8506,
            'nombre': 'Sistema Economico'
        }
    }
    
    print("\n[FILES] VERIFICANDO ARCHIVOS DE DASHBOARDS:")
    archivos_ok = 0
    archivos_faltantes = 0
    
    for dashboard_id, info in dashboards.items():
        if os.path.exists(info['archivo']):
            print(f"   [OK] {info['nombre']}: {info['archivo']}")
            archivos_ok += 1
        else:
            print(f"   [ERROR] {info['nombre']}: {info['archivo']} - NO ENCONTRADO")
            archivos_faltantes += 1
    
    print(f"\n[SUMMARY] ARCHIVOS: {archivos_ok} OK, {archivos_faltantes} FALTANTES")
    
    # Verificar sistema principal
    print("\n[WEB] VERIFICANDO SISTEMA PRINCIPAL:")
    try:
        response = requests.get("http://localhost:8500", timeout=5)
        if response.status_code == 200:
            print("   [OK] Sistema principal funcionando en puerto 8500")
            print("   [URL] http://localhost:8500")
        else:
            print(f"   [ERROR] Sistema principal respondio con codigo {response.status_code}")
    except Exception as e:
        print(f"   [ERROR] No se puede conectar al sistema principal: {e}")
    
    print("\n[INFO] INSTRUCCIONES DE USO:")
    print("   1. Ve a http://localhost:8500")
    print("   2. Inicia sesion con admin / admin123")
    print("   3. Veras la lista de dashboards disponibles")
    print("   4. Haz clic en 'Iniciar' para activar un dashboard")
    print("   5. Espera a que aparezca 'ACTIVO' en verde")
    print("   6. Haz clic en 'Abrir' para acceder al dashboard")
    print("   7. Usa las mismas credenciales en el dashboard especifico")
    
    print("\n[DASHBOARDS] DASHBOARDS DISPONIBLES:")
    for dashboard_id, info in dashboards.items():
        if os.path.exists(info['archivo']):
            print(f"   [OK] {info['nombre']} (Puerto {info['puerto']})")
        else:
            print(f"   [ERROR] {info['nombre']} (Puerto {info['puerto']}) - ARCHIVO FALTANTE")
    
    print("\n[USERS] USUARIOS DE PRUEBA:")
    print("   [ADMIN] admin / admin123")
    print("   [EXEC] ejecutivo / ejecutivo123")
    print("   [AGRI] agricultor / agricultor123")
    print("   [TECH] tecnico / tecnico123")
    print("   [USER] usuario / usuario123")
    
    print("\n[HELP] SOLUCION DE PROBLEMAS:")
    if archivos_faltantes > 0:
        print("   [WARNING] Algunos archivos de dashboards no existen")
        print("   [SOLUTION] Los dashboards con archivos faltantes no se podran iniciar")
    
    print("   [TIP] Usa el sistema principal para controlar todos los dashboards")
    print("   [TIP] Cada dashboard se ejecuta en su propio puerto")
    print("   [TIP] El sistema principal (puerto 8500) controla todo")
    
    print("\n" + "="*70)
    print("VERIFICACION COMPLETADA")
    print("="*70)

if __name__ == "__main__":
    verificar_dashboards()


