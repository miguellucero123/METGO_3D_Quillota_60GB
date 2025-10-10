"""
ABRIR SISTEMA DE AUTENTICACIÓN METGO 3D
Script para abrir el sistema de autenticación con dashboard principal
"""

import webbrowser
import time

def abrir_sistema_auth():
    """Abrir el sistema de autenticación METGO 3D"""
    
    print("=" * 60)
    print("METGO 3D - SISTEMA DE AUTENTICACION Y DASHBOARD PRINCIPAL")
    print("=" * 60)
    
    # URL del sistema de autenticación
    url_auth = "http://localhost:8505"
    
    print(f"\nSistema de Autenticacion: {url_auth}")
    print("\nCredenciales por defecto:")
    print("  Usuario: admin")
    print("  Contraseña: admin123")
    
    print(f"\nAbriendo sistema de autenticacion...")
    webbrowser.open_new_tab(url_auth)
    
    print(f"\n" + "=" * 60)
    print("SISTEMA DE AUTENTICACION ABIERTO")
    print("=" * 60)
    
    print("\nINSTRUCCIONES:")
    print("1. Ingrese las credenciales en la pagina web")
    print("2. Despues del login, accedera al Dashboard Principal")
    print("3. Desde alli puede acceder a todos los dashboards")
    print("4. Los dashboards se organizan por categorias")
    print("5. Puede iniciar/abrir cualquier dashboard con un clic")
    
    print(f"\nDASHBOARDS DISPONIBLES:")
    print("  - 14 Dashboards principales integrados")
    print("  - Meteorologia, Agricultura, IA, Drones, etc.")
    print("  - Dashboards Python y HTML")
    print("  - Acciones masivas disponibles")

def main():
    abrir_sistema_auth()

if __name__ == "__main__":
    main()
