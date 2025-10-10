#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SISTEMA UNIFICADO AUTENTICADO - METGO 3D
Sistema Completo con Autenticacion, Integracion de Todos los Notebooks y Archivos Python
"""

import streamlit as st
import sys
from pathlib import Path
import logging
import json
from datetime import datetime
import subprocess
import pandas as pd

# Importar modulos propios
from auth_module import SistemaAutenticacion
from integrador_modulos import IntegradorModulos

# Configuracion
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('SISTEMA_UNIFICADO_AUTENTICADO')

class SistemaUnificadoAutenticado:
    """Sistema Unificado con Autenticacion"""
    
    def __init__(self):
        self.auth = SistemaAutenticacion()
        self.integrador = IntegradorModulos()
        
        # Estado de sesion en Streamlit
        if 'autenticado' not in st.session_state:
            st.session_state.autenticado = False
        if 'token' not in st.session_state:
            st.session_state.token = None
        if 'usuario' not in st.session_state:
            st.session_state.usuario = None
    
    def mostrar_login(self):
        """Mostrar pantalla de login"""
        st.title("METGO 3D - Sistema Unificado")
        st.markdown("### Autenticacion de Usuario")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            st.info("Usuario: admin | Password: admin123")
            st.info("Usuario: usuario | Password: usuario123")
            
            usuario = st.text_input("Usuario")
            password = st.text_input("Password", type="password")
            
            if st.button("Iniciar Sesion", type="primary"):
                exito, resultado = self.auth.autenticar(usuario, password)
                
                if exito:
                    st.session_state.autenticado = True
                    st.session_state.token = resultado
                    st.session_state.usuario = usuario
                    st.success("Autenticacion exitosa")
                    st.rerun()
                else:
                    st.error(f"Error: {resultado}")
    
    def mostrar_dashboard(self):
        """Mostrar dashboard principal"""
        st.set_page_config(
            page_title="METGO 3D - Sistema Unificado",
            page_icon="🌐",
            layout="wide"
        )
        
        # Header
        col1, col2 = st.columns([3, 1])
        with col1:
            st.title("METGO 3D - Sistema Unificado Completo")
            st.markdown(f"**Usuario:** {st.session_state.usuario}")
        with col2:
            if st.button("Cerrar Sesion"):
                self.auth.cerrar_sesion(st.session_state.token)
                st.session_state.autenticado = False
                st.session_state.token = None
                st.session_state.usuario = None
                st.rerun()
        
        st.markdown("---")
        
        # Tabs
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "Dashboard",
            "Notebooks",
            "Archivos Python",
            "Ejecutar Modulo",
            "Estadisticas"
        ])
        
        with tab1:
            self._mostrar_tab_dashboard()
        
        with tab2:
            self._mostrar_tab_notebooks()
        
        with tab3:
            self._mostrar_tab_archivos_py()
        
        with tab4:
            self._mostrar_tab_ejecutar()
        
        with tab5:
            self._mostrar_tab_estadisticas()
    
    def _mostrar_tab_dashboard(self):
        """Mostrar tab de dashboard"""
        st.header("Dashboard del Sistema")
        
        resumen = self.integrador.obtener_resumen()
        
        # Metricas
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Notebooks", resumen['total_notebooks'])
        with col2:
            st.metric("Total Archivos .py", resumen['total_archivos_py'])
        with col3:
            st.metric("Total Modulos", resumen['total_modulos'])
        with col4:
            st.metric("Categorias", resumen['categorias'])
        
        st.markdown("---")
        
        # Modulos por categoria
        st.subheader("Modulos por Categoria")
        
        modulos_por_cat = resumen['modulos_por_categoria']
        df = pd.DataFrame.from_dict(modulos_por_cat, orient='index')
        st.dataframe(df, use_container_width=True)
    
    def _mostrar_tab_notebooks(self):
        """Mostrar tab de notebooks"""
        st.header("Notebooks del Proyecto")
        
        notebooks = self.integrador.notebooks
        
        if notebooks:
            # Filtrar por categoria
            categorias = sorted(set([nb['categoria'] for nb in notebooks]))
            categoria_seleccionada = st.selectbox("Filtrar por categoria", ["Todas"] + categorias)
            
            # Filtrar notebooks
            if categoria_seleccionada != "Todas":
                notebooks_filtrados = [nb for nb in notebooks if nb['categoria'] == categoria_seleccionada]
            else:
                notebooks_filtrados = notebooks
            
            st.write(f"**Total: {len(notebooks_filtrados)} notebooks**")
            
            # Mostrar notebooks
            for notebook in notebooks_filtrados:
                with st.expander(f"📓 {notebook['nombre']}", expanded=False):
                    st.write(f"**Categoria:** {notebook['categoria']}")
                    st.write(f"**Ruta:** {notebook['ruta']}")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button(f"Ver contenido", key=f"ver_{notebook['nombre']}"):
                            st.info("Funcion de visualizacion en desarrollo")
                    with col2:
                        if st.button(f"Ejecutar", key=f"ejecutar_{notebook['nombre']}"):
                            if self.auth.tiene_permiso(st.session_state.token, 'ejecutar'):
                                self._ejecutar_notebook(notebook['ruta'])
                            else:
                                st.error("No tienes permisos para ejecutar notebooks")
        else:
            st.warning("No se encontraron notebooks")
    
    def _mostrar_tab_archivos_py(self):
        """Mostrar tab de archivos Python"""
        st.header("Archivos Python del Proyecto")
        
        archivos = self.integrador.archivos_py
        
        if archivos:
            # Filtrar por categoria
            categorias = sorted(set([ar['categoria'] for ar in archivos]))
            categoria_seleccionada = st.selectbox("Filtrar por categoria", ["Todas"] + categorias, key="cat_py")
            
            # Filtrar archivos
            if categoria_seleccionada != "Todas":
                archivos_filtrados = [ar for ar in archivos if ar['categoria'] == categoria_seleccionada]
            else:
                archivos_filtrados = archivos
            
            st.write(f"**Total: {len(archivos_filtrados)} archivos Python**")
            
            # Mostrar archivos
            for archivo in archivos_filtrados:
                with st.expander(f"🐍 {archivo['nombre']}", expanded=False):
                    st.write(f"**Categoria:** {archivo['categoria']}")
                    st.write(f"**Ruta:** {archivo['ruta']}")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button(f"Ver codigo", key=f"ver_{archivo['nombre']}"):
                            self._ver_codigo(archivo['ruta'])
                    with col2:
                        if st.button(f"Ejecutar", key=f"ejecutar_{archivo['nombre']}"):
                            if self.auth.tiene_permiso(st.session_state.token, 'ejecutar'):
                                self._ejecutar_python(archivo['ruta'])
                            else:
                                st.error("No tienes permisos para ejecutar archivos")
        else:
            st.warning("No se encontraron archivos Python")
    
    def _mostrar_tab_ejecutar(self):
        """Mostrar tab de ejecucion"""
        st.header("Ejecutar Modulo")
        
        if not self.auth.tiene_permiso(st.session_state.token, 'ejecutar'):
            st.error("No tienes permisos para ejecutar modulos")
            return
        
        tipo = st.selectbox("Tipo de modulo", ["Notebook", "Python"])
        
        if tipo == "Notebook":
            notebooks = [nb['nombre'] for nb in self.integrador.notebooks]
            modulo = st.selectbox("Seleccionar notebook", notebooks)
            
            if st.button("Ejecutar Notebook"):
                notebook_info = next((nb for nb in self.integrador.notebooks if nb['nombre'] == modulo), None)
                if notebook_info:
                    self._ejecutar_notebook(notebook_info['ruta'])
        
        else:
            archivos = [ar['nombre'] for ar in self.integrador.archivos_py]
            modulo = st.selectbox("Seleccionar archivo Python", archivos)
            
            if st.button("Ejecutar Python"):
                archivo_info = next((ar for ar in self.integrador.archivos_py if ar['nombre'] == modulo), None)
                if archivo_info:
                    self._ejecutar_python(archivo_info['ruta'])
    
    def _mostrar_tab_estadisticas(self):
        """Mostrar tab de estadisticas"""
        st.header("Estadisticas del Sistema")
        
        resumen = self.integrador.obtener_resumen()
        
        # Grafico de modulos por categoria
        import plotly.express as px
        
        modulos_por_cat = resumen['modulos_por_categoria']
        df = pd.DataFrame.from_dict(modulos_por_cat, orient='index')
        df['categoria'] = df.index
        
        fig = px.bar(
            df,
            x='categoria',
            y=['notebooks', 'archivos_py'],
            title='Modulos por Categoria',
            labels={'value': 'Cantidad', 'categoria': 'Categoria'}
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Informacion adicional
        st.subheader("Informacion del Sistema")
        st.json(resumen)
    
    def _ejecutar_notebook(self, ruta: str):
        """Ejecutar un notebook"""
        try:
            with st.spinner(f"Ejecutando notebook..."):
                resultado = subprocess.run(
                    [sys.executable, "-m", "jupyter", "nbconvert", "--to", "notebook", "--execute", ruta],
                    capture_output=True,
                    text=True,
                    timeout=300
                )
                
                if resultado.returncode == 0:
                    st.success("Notebook ejecutado exitosamente")
                    with st.expander("Ver salida"):
                        st.text(resultado.stdout)
                else:
                    st.error("Error ejecutando notebook")
                    with st.expander("Ver errores"):
                        st.text(resultado.stderr)
        except subprocess.TimeoutExpired:
            st.error("Timeout: El notebook tardo mas de 5 minutos")
        except Exception as e:
            st.error(f"Error: {e}")
    
    def _ejecutar_python(self, ruta: str):
        """Ejecutar un archivo Python"""
        try:
            with st.spinner(f"Ejecutando archivo Python..."):
                resultado = subprocess.run(
                    [sys.executable, ruta],
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                
                if resultado.returncode == 0:
                    st.success("Archivo Python ejecutado exitosamente")
                    with st.expander("Ver salida"):
                        st.text(resultado.stdout)
                else:
                    st.error("Error ejecutando archivo Python")
                    with st.expander("Ver errores"):
                        st.text(resultado.stderr)
        except subprocess.TimeoutExpired:
            st.error("Timeout: El archivo tardo mas de 1 minuto")
        except Exception as e:
            st.error(f"Error: {e}")
    
    def _ver_codigo(self, ruta: str):
        """Ver codigo de un archivo"""
        try:
            with open(ruta, 'r', encoding='utf-8') as f:
                codigo = f.read()
            st.code(codigo, language='python')
        except Exception as e:
            st.error(f"Error leyendo archivo: {e}")
    
    def ejecutar(self):
        """Ejecutar sistema unificado"""
        if not st.session_state.autenticado:
            self.mostrar_login()
        else:
            self.mostrar_dashboard()

def main():
    """Funcion principal"""
    sistema = SistemaUnificadoAutenticado()
    sistema.ejecutar()

if __name__ == "__main__":
    main()



