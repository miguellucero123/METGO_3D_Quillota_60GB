#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FIX STREAMLIT ERRORS - METGO 3D
Correccion de errores de Streamlit
"""

import re
import os
from pathlib import Path

class StreamlitErrorFixer:
    """Corrector de errores de Streamlit para METGO 3D"""
    
    def __init__(self):
        self.archivo_principal = 'sistema_unificado_con_conectores.py'
    
    def corregir_sliders_duplicados(self):
        """Corregir sliders duplicados agregando keys unicos"""
        try:
            if not os.path.exists(self.archivo_principal):
                print(f"Archivo {self.archivo_principal} no encontrado")
                return False
            
            # Leer archivo
            with open(self.archivo_principal, 'r', encoding='utf-8') as f:
                contenido = f.read()
            
            # Patrones de sliders a corregir
            patrones_sliders = [
                (r'st\.slider\("Dias de datos", 1, 30, 7\)', 'st.slider("Dias de datos", 1, 30, 7, key="meteorologico_dias")'),
                (r'st\.slider\("Dias de datos", 1, 30, 7, key="satelital_dias"\)', 'st.slider("Dias de datos", 1, 30, 7, key="satelital_dias")'),
                (r'st\.slider\("CPU Max \(%\)", 50, 100, 80, key="monitoreo_cpu"\)', 'st.slider("CPU Max (%)", 50, 100, 80, key="monitoreo_cpu")'),
                (r'st\.slider\("Memoria Max \(%\)", 50, 100, 85, key="monitoreo_memoria"\)', 'st.slider("Memoria Max (%)", 50, 100, 85, key="monitoreo_memoria")'),
                (r'st\.slider\("Disco Max \(%\)", 50, 100, 90, key="monitoreo_disco"\)', 'st.slider("Disco Max (%)", 50, 100, 90, key="monitoreo_disco")'),
                (r'st\.slider\("Dias a retener", 1, 90, 30, key="respaldo_dias"\)', 'st.slider("Dias a retener", 1, 90, 30, key="respaldo_dias")')
            ]
            
            # Aplicar correcciones
            contenido_corregido = contenido
            cambios_realizados = 0
            
            for patron, reemplazo in patrones_sliders:
                if re.search(patron, contenido_corregido):
                    contenido_corregido = re.sub(patron, reemplazo, contenido_corregido)
                    cambios_realizados += 1
                    print(f"Corregido: {patron}")
            
            # Escribir archivo corregido
            if cambios_realizados > 0:
                with open(self.archivo_principal, 'w', encoding='utf-8') as f:
                    f.write(contenido_corregido)
                print(f"Correcciones aplicadas: {cambios_realizados}")
                return True
            else:
                print("No se encontraron sliders duplicados para corregir")
                return True
                
        except Exception as e:
            print(f"Error corrigiendo sliders: {e}")
            return False
    
    def corregir_use_container_width(self):
        """Corregir warnings de use_container_width"""
        try:
            if not os.path.exists(self.archivo_principal):
                print(f"Archivo {self.archivo_principal} no encontrado")
                return False
            
            # Leer archivo
            with open(self.archivo_principal, 'r', encoding='utf-8') as f:
                contenido = f.read()
            
            # Patrones a corregir
            patrones = [
                (r'use_container_width=True', 'width="stretch"'),
                (r'use_container_width=False', 'width="content"')
            ]
            
            # Aplicar correcciones
            contenido_corregido = contenido
            cambios_realizados = 0
            
            for patron, reemplazo in patrones:
                if re.search(patron, contenido_corregido):
                    contenido_corregido = re.sub(patron, reemplazo, contenido_corregido)
                    cambios_realizados += 1
                    print(f"Corregido: {patron} -> {reemplazo}")
            
            # Escribir archivo corregido
            if cambios_realizados > 0:
                with open(self.archivo_principal, 'w', encoding='utf-8') as f:
                    f.write(contenido_corregido)
                print(f"Correcciones de use_container_width aplicadas: {cambios_realizados}")
                return True
            else:
                print("No se encontraron use_container_width para corregir")
                return True
                
        except Exception as e:
            print(f"Error corrigiendo use_container_width: {e}")
            return False
    
    def optimizar_rendimiento_streamlit(self):
        """Optimizar rendimiento de Streamlit"""
        try:
            if not os.path.exists(self.archivo_principal):
                print(f"Archivo {self.archivo_principal} no encontrado")
                return False
            
            # Leer archivo
            with open(self.archivo_principal, 'r', encoding='utf-8') as f:
                contenido = f.read()
            
            # Agregar configuracion de rendimiento al inicio del archivo
            config_rendimiento = '''
# Configuracion de rendimiento Streamlit
import streamlit as st

# Configurar pagina para mejor rendimiento
st.set_page_config(
    page_title="METGO 3D - Sistema Meteorologico Agricola",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configuracion de cache
@st.cache_data
def cargar_datos_cached():
    """Cargar datos con cache"""
    return None

'''
            
            # Verificar si ya existe la configuracion
            if 'st.set_page_config' not in contenido:
                # Insertar configuracion despues de los imports
                lines = contenido.split('\n')
                insert_index = 0
                
                for i, line in enumerate(lines):
                    if line.startswith('import streamlit as st'):
                        insert_index = i + 1
                        break
                
                lines.insert(insert_index, config_rendimiento)
                contenido_corregido = '\n'.join(lines)
                
                # Escribir archivo corregido
                with open(self.archivo_principal, 'w', encoding='utf-8') as f:
                    f.write(contenido_corregido)
                
                print("Configuracion de rendimiento agregada")
                return True
            else:
                print("Configuracion de rendimiento ya existe")
                return True
                
        except Exception as e:
            print(f"Error optimizando rendimiento: {e}")
            return False
    
    def corregir_todos_los_errores(self):
        """Corregir todos los errores de Streamlit"""
        try:
            print("Iniciando correccion de errores de Streamlit...")
            
            # 1. Corregir sliders duplicados
            print("\n1. Corrigiendo sliders duplicados...")
            if not self.corregir_sliders_duplicados():
                return False
            
            # 2. Corregir use_container_width
            print("\n2. Corrigiendo use_container_width...")
            if not self.corregir_use_container_width():
                return False
            
            # 3. Optimizar rendimiento
            print("\n3. Optimizando rendimiento...")
            if not self.optimizar_rendimiento_streamlit():
                return False
            
            print("\nTodos los errores de Streamlit corregidos exitosamente")
            return True
            
        except Exception as e:
            print(f"Error corrigiendo errores de Streamlit: {e}")
            return False

def main():
    """Funcion principal para corregir errores de Streamlit"""
    print("CORRECCION DE ERRORES STREAMLIT - METGO 3D")
    print("Sistema Meteorologico Agricola Quillota - Version 2.0")
    print("=" * 70)
    
    try:
        # Crear corrector
        fixer = StreamlitErrorFixer()
        
        # Corregir todos los errores
        if fixer.corregir_todos_los_errores():
            print("\nCorreccion de errores Streamlit completada exitosamente")
            return True
        else:
            print("\nError en la correccion de errores Streamlit")
            return False
        
    except Exception as e:
        print(f"\nError corrigiendo Streamlit: {e}")
        return False

if __name__ == "__main__":
    main()
