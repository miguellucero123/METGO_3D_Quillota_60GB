import streamlit as st
import json
import pickle
import os
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

class OfflineCache:
    """Sistema de caché offline para dispositivos móviles"""
    
    def __init__(self, cache_dir="mobile_cache"):
        self.cache_dir = cache_dir
        self.ensure_cache_dir()
    
    def ensure_cache_dir(self):
        """Asegura que el directorio de caché existe"""
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
    
    def get_cache_path(self, key):
        """Obtiene la ruta del archivo de caché"""
        return os.path.join(self.cache_dir, f"{key}.pkl")
    
    def is_cache_valid(self, key, max_age_hours=1):
        """Verifica si el caché es válido"""
        cache_path = self.get_cache_path(key)
        
        if not os.path.exists(cache_path):
            return False
        
        # Verificar edad del archivo
        file_time = datetime.fromtimestamp(os.path.getmtime(cache_path))
        age = datetime.now() - file_time
        
        return age.total_seconds() < (max_age_hours * 3600)
    
    def get_cached_data(self, key):
        """Obtiene datos del caché"""
        cache_path = self.get_cache_path(key)
        
        try:
            with open(cache_path, 'rb') as f:
                return pickle.load(f)
        except:
            return None
    
    def cache_data(self, key, data, metadata=None):
        """Guarda datos en el caché"""
        cache_path = self.get_cache_path(key)
        
        cache_entry = {
            'data': data,
            'metadata': metadata or {},
            'timestamp': datetime.now(),
            'key': key
        }
        
        try:
            with open(cache_path, 'wb') as f:
                pickle.dump(cache_entry, f)
            return True
        except:
            return False
    
    def clear_cache(self, key=None):
        """Limpia el caché"""
        if key:
            cache_path = self.get_cache_path(key)
            if os.path.exists(cache_path):
                os.remove(cache_path)
        else:
            # Limpiar todo el caché
            for filename in os.listdir(self.cache_dir):
                if filename.endswith('.pkl'):
                    os.remove(os.path.join(self.cache_dir, filename))
    
    def get_cache_info(self):
        """Obtiene información del caché"""
        cache_files = []
        
        for filename in os.listdir(self.cache_dir):
            if filename.endswith('.pkl'):
                filepath = os.path.join(self.cache_dir, filename)
                file_time = datetime.fromtimestamp(os.path.getmtime(filepath))
                file_size = os.path.getsize(filepath)
                
                cache_files.append({
                    'key': filename[:-4],  # Remover .pkl
                    'timestamp': file_time,
                    'size': file_size,
                    'age': datetime.now() - file_time
                })
        
        return cache_files

def generate_sample_data():
    """Genera datos de muestra para el caché"""
    
    # Datos meteorológicos simulados
    dates = pd.date_range(start=datetime.now() - timedelta(days=30), end=datetime.now(), freq='h')
    
    meteorologicos_data = []
    for date in dates:
        meteorologicos_data.append({
            'fecha': date,
            'temperatura': 20 + np.sin(2 * np.pi * date.hour / 24) * 5 + np.random.normal(0, 2),
            'humedad': 65 + np.cos(2 * np.pi * date.hour / 24) * 10 + np.random.normal(0, 5),
            'precipitacion': max(0, np.random.exponential(0.3)),
            'viento': max(0, 8 + np.random.exponential(3)),
            'presion': 1013 + np.random.normal(0, 10)
        })
    
    # Datos agrícolas simulados
    agricolas_data = []
    for date in dates[::24]:  # Datos diarios
        agricolas_data.append({
            'fecha': date,
            'rendimiento': 20 + np.random.normal(0, 2),
            'calidad': 75 + np.random.normal(0, 5),
            'eficiencia_riego': 80 + np.random.normal(0, 5),
            'costo_produccion': 1000 + np.random.normal(0, 100)
        })
    
    return {
        'meteorologicos': pd.DataFrame(meteorologicos_data),
        'agricolas': pd.DataFrame(agricolas_data),
        'last_updated': datetime.now()
    }

def mostrar_cache_mobile():
    """Función principal para mostrar el sistema de caché móvil"""
    
    # Inicializar caché
    if 'offline_cache' not in st.session_state:
        st.session_state.offline_cache = OfflineCache()
    
    cache = st.session_state.offline_cache
    
    st.title("📱 Sistema de Caché Offline Móvil")
    
    # Información del caché
    st.markdown("### 📊 Estado del Caché")
    
    cache_info = cache.get_cache_info()
    
    if cache_info:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Archivos en Caché", len(cache_info))
        
        with col2:
            total_size = sum(info['size'] for info in cache_info)
            st.metric("Tamaño Total", f"{total_size / 1024:.1f} KB")
        
        with col3:
            oldest_file = min(cache_info, key=lambda x: x['timestamp'])
            st.metric("Archivo Más Antiguo", oldest_file['age'].days)
        
        # Lista de archivos en caché
        st.markdown("### 📁 Archivos en Caché")
        
        for info in cache_info:
            with st.expander(f"📄 {info['key']} - {info['age'].days} días"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.write(f"**Tamaño:** {info['size']} bytes")
                
                with col2:
                    st.write(f"**Última modificación:** {info['timestamp'].strftime('%Y-%m-%d %H:%M')}")
                
                with col3:
                    st.write(f"**Antigüedad:** {info['age'].days} días")
                
                if st.button(f"🗑️ Eliminar {info['key']}", key=f"delete_{info['key']}"):
                    cache.clear_cache(info['key'])
                    st.success(f"Archivo {info['key']} eliminado")
                    st.rerun()
    else:
        st.info("No hay archivos en caché")
    
    # Gestión del caché
    st.markdown("### ⚙️ Gestión del Caché")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Generar Datos de Prueba"):
            sample_data = generate_sample_data()
            
            # Guardar diferentes tipos de datos
            cache.cache_data('meteorologicos', sample_data['meteorologicos'], {
                'type': 'meteorologicos',
                'description': 'Datos meteorológicos de 30 días'
            })
            
            cache.cache_data('agricolas', sample_data['agricolas'], {
                'type': 'agricolas',
                'description': 'Datos agrícolas de 30 días'
            })
            
            cache.cache_data('configuracion', {
                'estaciones': ['Quillota', 'Los Nogales', 'Hijuelas'],
                'cultivos': ['Palta', 'Cítricos', 'Vid'],
                'alertas_activas': True
            }, {
                'type': 'configuracion',
                'description': 'Configuración del sistema'
            })
            
            st.success("Datos de prueba generados y guardados en caché")
            st.rerun()
    
    with col2:
        if st.button("🗑️ Limpiar Todo"):
            cache.clear_cache()
            st.success("Caché limpiado completamente")
            st.rerun()
    
    with col3:
        if st.button("🔄 Actualizar Válidos"):
            # Limpiar caché expirado
            for info in cache_info:
                if info['age'].days > 1:  # Más de 1 día
                    cache.clear_cache(info['key'])
            
            st.success("Caché actualizado")
            st.rerun()
    
    # Prueba de caché
    st.markdown("### 🧪 Prueba de Caché")
    
    test_key = "test_data"
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("💾 Guardar Datos de Prueba"):
            test_data = {
                'mensaje': 'Datos de prueba para caché móvil',
                'timestamp': datetime.now(),
                'numero': np.random.randint(1, 100)
            }
            
            if cache.cache_data(test_key, test_data, {'test': True}):
                st.success("Datos guardados en caché")
            else:
                st.error("Error al guardar datos")
    
    with col2:
        if st.button("📖 Leer Datos de Prueba"):
            cached_data = cache.get_cached_data(test_key)
            
            if cached_data:
                st.success("Datos leídos del caché:")
                st.json(cached_data)
            else:
                st.error("No hay datos en caché")
    
    # Información de caché válido
    if st.button("✅ Verificar Válidez"):
        is_valid = cache.is_cache_valid(test_key)
        
        if is_valid:
            st.success("Caché válido")
        else:
            st.warning("Caché expirado o no existe")
    
    # Configuración de caché
    st.markdown("### ⚙️ Configuración de Caché")
    
    max_age_hours = st.slider(
        "Máxima edad del caché (horas)",
        min_value=1,
        max_value=24,
        value=6,
        help="Tiempo máximo que los datos permanecen válidos en caché"
    )
    
    auto_cleanup = st.checkbox(
        "Limpieza automática",
        value=True,
        help="Limpiar automáticamente el caché expirado"
    )
    
    if auto_cleanup:
        st.info("La limpieza automática está activada")
    
    # Información del sistema
    st.markdown("### ℹ️ Información del Sistema")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info(f"""
        **📁 Directorio de Caché:** {cache.cache_dir}
        **🕐 Última Verificación:** {datetime.now().strftime('%H:%M:%S')}
        **📊 Estado:** {'🟢 Activo' if os.path.exists(cache.cache_dir) else '🔴 Inactivo'}
        """)
    
    with col2:
        st.info(f"""
        **⏱️ Máxima Edad:** {max_age_hours} horas
        **🧹 Limpieza Auto:** {'✅ Activada' if auto_cleanup else '❌ Desactivada'}
        **💾 Espacio Disponible:** {os.path.getsize('.') // 1024} KB
        """)

# Si se ejecuta directamente
if __name__ == "__main__":
    st.set_page_config(
        page_title="📱 Caché Offline - METGO Mobile",
        page_icon="📱",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    mostrar_cache_mobile()
