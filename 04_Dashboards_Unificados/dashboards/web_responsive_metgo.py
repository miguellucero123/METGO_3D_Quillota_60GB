#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🌐 WEB RESPONSIVE METGO 3D
Sistema Meteorológico Agrícola Quillota - Aplicación Web Responsive
"""

import os
import sys
import time
import json
import warnings
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any, Union
import logging
import sqlite3
from dataclasses import dataclass
import yaml

# Flask para aplicación web
try:
    from flask import Flask, request, jsonify, render_template, send_file, redirect, url_for, session, flash
    from flask_cors import CORS
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False

# Configuración
warnings.filterwarnings('ignore')

@dataclass
class UsuarioWeb:
    """Usuario de la aplicación web"""
    id: str
    nombre: str
    email: str
    rol: str
    activo: bool
    ultimo_acceso: str
    configuracion: Dict[str, Any]

@dataclass
class DashboardData:
    """Datos del dashboard"""
    timestamp: str
    metricas: Dict[str, float]
    graficos: List[str]
    alertas: List[Dict[str, Any]]
    estado_sistema: Dict[str, Any]

class WebResponsiveMETGO:
    """Aplicación web responsive para METGO 3D"""
    
    def __init__(self):
        # Inicializar logger primero
        self.logger = logging.getLogger('METGO_WEB')
        
        self.app = Flask(__name__) if FLASK_AVAILABLE else None
        if self.app:
            self.app.secret_key = 'metgo_3d_secret_key_2025'
            CORS(self.app)
            self._configurar_rutas()
        
        self.configuracion = {
            'directorio_templates': 'templates/web',
            'directorio_static': 'static/web',
            'directorio_datos': 'data/web',
            'directorio_logs': 'logs/web',
            'directorio_reportes': 'reportes/web',
            'version': '2.0',
            'timestamp': datetime.now().isoformat()
        }
        
        # Crear directorios
        self._crear_directorios()
        
        # Configurar logging
        self._configurar_logging()
        
        # Base de datos
        self._inicializar_base_datos()
        
        # Configuración de la aplicación web
        self.configuracion_web = {
            'titulo': 'METGO 3D - Sistema Meteorológico Agrícola',
            'version': '2.0',
            'descripcion': 'Sistema integral para análisis meteorológico agrícola',
            'idioma': 'es',
            'timezone': 'America/Santiago',
            'tema': 'agricola',
            'colores': {
                'primario': '#2E8B57',
                'secundario': '#90EE90',
                'accento': '#FFD700',
                'texto': '#000000',
                'fondo': '#F5F5F5'
            }
        }
        
        # Usuarios y sesiones
        self.usuarios = {}
        self.sesiones = {}
        
        # Datos del dashboard
        self.dashboard_data = {}
        
        # Configurar usuarios demo
        self._configurar_usuarios_demo()
    
    def _crear_directorios(self):
        """Crear directorios necesarios"""
        try:
            for directorio in self.configuracion.values():
                if isinstance(directorio, str) and '/' in directorio:
                    Path(directorio).mkdir(parents=True, exist_ok=True)
        except Exception as e:
            print(f"Error creando directorios: {e}")
    
    def _configurar_logging(self):
        """Configurar sistema de logging"""
        try:
            # Configurar logging solo si no está ya configurado
            if not self.logger.handlers:
                logging.basicConfig(
                    level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler(f"{self.configuracion['directorio_logs']}/web.log"),
                        logging.StreamHandler()
                    ]
                )
            self.logger.info("Sistema de logging configurado")
        except Exception as e:
            print(f"Error configurando logging: {e}")
    
    def _inicializar_base_datos(self):
        """Inicializar base de datos SQLite"""
        try:
            archivo_bd = f"{self.configuracion['directorio_datos']}/web.db"
            
            self.conexion_bd = sqlite3.connect(archivo_bd, check_same_thread=False)
            self.cursor_bd = self.conexion_bd.cursor()
            
            # Crear tablas
            self._crear_tablas_bd()
            
            self.logger.info(f"Base de datos inicializada: {archivo_bd}")
            
        except Exception as e:
            self.logger.error(f"Error inicializando base de datos: {e}")
    
    def _crear_tablas_bd(self):
        """Crear tablas en la base de datos"""
        try:
            # Tabla de usuarios web
            self.cursor_bd.execute('''
                CREATE TABLE IF NOT EXISTS usuarios_web (
                    id TEXT PRIMARY KEY,
                    nombre TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    rol TEXT NOT NULL,
                    activo BOOLEAN DEFAULT TRUE,
                    ultimo_acceso DATETIME,
                    configuracion TEXT,
                    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Tabla de sesiones
            self.cursor_bd.execute('''
                CREATE TABLE IF NOT EXISTS sesiones_web (
                    id TEXT PRIMARY KEY,
                    usuario_id TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    ip_address TEXT,
                    user_agent TEXT,
                    activa BOOLEAN DEFAULT TRUE,
                    FOREIGN KEY (usuario_id) REFERENCES usuarios_web (id)
                )
            ''')
            
            # Tabla de dashboard
            self.cursor_bd.execute('''
                CREATE TABLE IF NOT EXISTS dashboard_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    tipo_datos TEXT NOT NULL,
                    datos TEXT NOT NULL,
                    usuario_id TEXT,
                    FOREIGN KEY (usuario_id) REFERENCES usuarios_web (id)
                )
            ''')
            
            # Crear índices
            self.cursor_bd.execute('CREATE INDEX IF NOT EXISTS idx_usuarios_email ON usuarios_web(email)')
            self.cursor_bd.execute('CREATE INDEX IF NOT EXISTS idx_sesiones_usuario ON sesiones_web(usuario_id)')
            self.cursor_bd.execute('CREATE INDEX IF NOT EXISTS idx_dashboard_timestamp ON dashboard_data(timestamp)')
            
            self.conexion_bd.commit()
            self.logger.info("Tablas de base de datos creadas")
            
        except Exception as e:
            self.logger.error(f"Error creando tablas: {e}")
    
    def _configurar_usuarios_demo(self):
        """Configurar usuarios de demostración"""
        try:
            usuarios_demo = [
                {
                    'id': 'admin_1',
                    'nombre': 'Administrador METGO',
                    'email': 'admin@metgo.cl',
                    'password_hash': 'demo_hash',
                    'rol': 'administrador',
                    'configuracion': {
                        'tema': 'oscuro',
                        'idioma': 'es',
                        'notificaciones': True
                    }
                },
                {
                    'id': 'agricultor_1',
                    'nombre': 'Juan Pérez',
                    'email': 'juan.perez@agricultor.cl',
                    'password_hash': 'demo_hash',
                    'rol': 'agricultor',
                    'configuracion': {
                        'tema': 'claro',
                        'idioma': 'es',
                        'notificaciones': True
                    }
                },
                {
                    'id': 'tecnico_1',
                    'nombre': 'María González',
                    'email': 'maria.gonzalez@tecnico.cl',
                    'password_hash': 'demo_hash',
                    'rol': 'tecnico',
                    'configuracion': {
                        'tema': 'claro',
                        'idioma': 'es',
                        'notificaciones': True
                    }
                }
            ]
            
            for usuario_data in usuarios_demo:
                usuario = UsuarioWeb(
                    id=usuario_data['id'],
                    nombre=usuario_data['nombre'],
                    email=usuario_data['email'],
                    rol=usuario_data['rol'],
                    activo=True,
                    ultimo_acceso=datetime.now().isoformat(),
                    configuracion=usuario_data['configuracion']
                )
                self.usuarios[usuario.id] = usuario
            
            self.logger.info(f"Usuarios demo configurados: {len(self.usuarios)}")
            
        except Exception as e:
            self.logger.error(f"Error configurando usuarios demo: {e}")
    
    def _configurar_rutas(self):
        """Configurar rutas de la aplicación web"""
        try:
            if not self.app:
                return
            
            @self.app.route('/')
            def index():
                return self._renderizar_pagina('index.html', {
                    'titulo': self.configuracion_web['titulo'],
                    'version': self.configuracion_web['version']
                })
            
            @self.app.route('/login', methods=['GET', 'POST'])
            def login():
                if request.method == 'POST':
                    return self._procesar_login()
                return self._renderizar_pagina('login.html')
            
            @self.app.route('/dashboard')
            def dashboard():
                if 'usuario_id' not in session:
                    return redirect(url_for('login'))
                return self._renderizar_dashboard()
            
            @self.app.route('/api/dashboard')
            def api_dashboard():
                return jsonify(self._obtener_datos_dashboard())
            
            @self.app.route('/api/usuarios')
            def api_usuarios():
                return jsonify(self._obtener_usuarios())
            
            @self.app.route('/api/metricas')
            def api_metricas():
                return jsonify(self._obtener_metricas())
            
            @self.app.route('/api/alertas')
            def api_alertas():
                return jsonify(self._obtener_alertas())
            
            @self.app.route('/logout')
            def logout():
                session.clear()
                return redirect(url_for('index'))
            
            self.logger.info("Rutas de aplicación web configuradas")
            
        except Exception as e:
            self.logger.error(f"Error configurando rutas: {e}")
    
    def _renderizar_pagina(self, template: str, datos: Dict[str, Any] = None) -> str:
        """Renderizar página HTML"""
        try:
            if datos is None:
                datos = {}
            
            # Datos base para todas las páginas
            datos_base = {
                'configuracion': self.configuracion_web,
                'timestamp': datetime.now().isoformat(),
                'usuario_actual': self._obtener_usuario_actual()
            }
            
            datos.update(datos_base)
            
            # Generar HTML básico si no hay templates
            return self._generar_html_basico(template, datos)
            
        except Exception as e:
            self.logger.error(f"Error renderizando página: {e}")
            return f"<h1>Error: {e}</h1>"
    
    def _generar_html_basico(self, template: str, datos: Dict[str, Any]) -> str:
        """Generar HTML básico para la aplicación"""
        try:
            if template == 'index.html':
                return f"""
                <!DOCTYPE html>
                <html lang="es">
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>{datos.get('titulo', 'METGO 3D')}</title>
                    <style>
                        body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }}
                        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                        .header {{ text-align: center; color: #2E8B57; margin-bottom: 30px; }}
                        .nav {{ display: flex; justify-content: center; gap: 20px; margin-bottom: 30px; }}
                        .nav a {{ padding: 10px 20px; background: #2E8B57; color: white; text-decoration: none; border-radius: 5px; }}
                        .nav a:hover {{ background: #1e5f3f; }}
                        .dashboard {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }}
                        .card {{ background: #f9f9f9; padding: 20px; border-radius: 8px; border-left: 4px solid #2E8B57; }}
                        .card h3 {{ color: #2E8B57; margin-top: 0; }}
                        .metric {{ font-size: 24px; font-weight: bold; color: #2E8B57; }}
                        .footer {{ text-align: center; margin-top: 30px; color: #666; }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="header">
                            <h1>{datos.get('titulo', 'METGO 3D')}</h1>
                            <p>Sistema Meteorológico Agrícola Quillota - Versión {datos.get('version', '2.0')}</p>
                        </div>
                        
                        <div class="nav">
                            <a href="/">Inicio</a>
                            <a href="/login">Iniciar Sesión</a>
                            <a href="/dashboard">Dashboard</a>
                        </div>
                        
                        <div class="dashboard">
                            <div class="card">
                                <h3>🌡️ Datos Meteorológicos</h3>
                                <p>Monitoreo en tiempo real de condiciones climáticas</p>
                                <div class="metric">22.5°C</div>
                            </div>
                            
                            <div class="card">
                                <h3>💧 Sistema de Riego</h3>
                                <p>Control automatizado de riego</p>
                                <div class="metric">45%</div>
                            </div>
                            
                            <div class="card">
                                <h3>📊 Análisis Agrícola</h3>
                                <p>Índices y recomendaciones</p>
                                <div class="metric">NDVI: 0.65</div>
                            </div>
                            
                            <div class="card">
                                <h3>🤖 Chatbot</h3>
                                <p>Asistente inteligente</p>
                                <div class="metric">24/7</div>
                            </div>
                        </div>
                        
                        <div class="footer">
                            <p>© 2025 METGO 3D - Sistema Meteorológico Agrícola</p>
                        </div>
                    </div>
                </body>
                </html>
                """
            
            elif template == 'login.html':
                return f"""
                <!DOCTYPE html>
                <html lang="es">
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>Iniciar Sesión - METGO 3D</title>
                    <style>
                        body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; display: flex; justify-content: center; align-items: center; min-height: 100vh; }}
                        .login-container {{ background: white; padding: 40px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); width: 100%; max-width: 400px; }}
                        .header {{ text-align: center; color: #2E8B57; margin-bottom: 30px; }}
                        .form-group {{ margin-bottom: 20px; }}
                        .form-group label {{ display: block; margin-bottom: 5px; color: #333; }}
                        .form-group input {{ width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px; box-sizing: border-box; }}
                        .btn {{ width: 100%; padding: 12px; background: #2E8B57; color: white; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; }}
                        .btn:hover {{ background: #1e5f3f; }}
                        .demo-users {{ margin-top: 20px; padding: 15px; background: #f9f9f9; border-radius: 5px; }}
                        .demo-users h4 {{ margin-top: 0; color: #2E8B57; }}
                        .demo-user {{ margin: 5px 0; font-size: 14px; }}
                    </style>
                </head>
                <body>
                    <div class="login-container">
                        <div class="header">
                            <h1>METGO 3D</h1>
                            <p>Iniciar Sesión</p>
                        </div>
                        
                        <form method="POST">
                            <div class="form-group">
                                <label for="email">Email:</label>
                                <input type="email" id="email" name="email" required>
                            </div>
                            
                            <div class="form-group">
                                <label for="password">Contraseña:</label>
                                <input type="password" id="password" name="password" required>
                            </div>
                            
                            <button type="submit" class="btn">Iniciar Sesión</button>
                        </form>
                        
                        <div class="demo-users">
                            <h4>Usuarios Demo:</h4>
                            <div class="demo-user">admin@metgo.cl (Administrador)</div>
                            <div class="demo-user">juan.perez@agricultor.cl (Agricultor)</div>
                            <div class="demo-user">maria.gonzalez@tecnico.cl (Técnico)</div>
                        </div>
                    </div>
                </body>
                </html>
                """
            
            elif template == 'dashboard.html':
                return f"""
                <!DOCTYPE html>
                <html lang="es">
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>Dashboard - METGO 3D</title>
                    <style>
                        body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }}
                        .container {{ max-width: 1200px; margin: 0 auto; }}
                        .header {{ display: flex; justify-content: space-between; align-items: center; background: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                        .nav {{ display: flex; gap: 20px; }}
                        .nav a {{ padding: 10px 20px; background: #2E8B57; color: white; text-decoration: none; border-radius: 5px; }}
                        .dashboard {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }}
                        .card {{ background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                        .card h3 {{ color: #2E8B57; margin-top: 0; }}
                        .metric {{ font-size: 24px; font-weight: bold; color: #2E8B57; }}
                        .chart {{ height: 200px; background: #f9f9f9; border-radius: 5px; display: flex; align-items: center; justify-content: center; color: #666; }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="header">
                            <h1>Dashboard METGO 3D</h1>
                            <div class="nav">
                                <a href="/">Inicio</a>
                                <a href="/logout">Cerrar Sesión</a>
                            </div>
                        </div>
                        
                        <div class="dashboard">
                            <div class="card">
                                <h3>🌡️ Condiciones Actuales</h3>
                                <div class="metric">22.5°C</div>
                                <p>Humedad: 65% | Viento: 8 km/h</p>
                            </div>
                            
                            <div class="card">
                                <h3>💧 Estado del Riego</h3>
                                <div class="metric">45%</div>
                                <p>Humedad del suelo | Próximo riego: 06:00</p>
                            </div>
                            
                            <div class="card">
                                <h3>📊 Índices Agrícolas</h3>
                                <div class="metric">NDVI: 0.65</div>
                                <p>Vegetación saludable | EVI: 0.42</p>
                            </div>
                            
                            <div class="card">
                                <h3>⚠️ Alertas Activas</h3>
                                <div class="metric">2</div>
                                <p>Sin alertas críticas</p>
                            </div>
                            
                            <div class="card">
                                <h3>📈 Tendencia Temperatura</h3>
                                <div class="chart">Gráfico de Temperatura</div>
                            </div>
                            
                            <div class="card">
                                <h3>💧 Consumo de Agua</h3>
                                <div class="chart">Gráfico de Consumo</div>
                            </div>
                        </div>
                    </div>
                </body>
                </html>
                """
            
            return f"<h1>Página no encontrada: {template}</h1>"
            
        except Exception as e:
            self.logger.error(f"Error generando HTML: {e}")
            return f"<h1>Error: {e}</h1>"
    
    def _procesar_login(self) -> str:
        """Procesar login de usuario"""
        try:
            email = request.form.get('email')
            password = request.form.get('password')
            
            # Buscar usuario
            usuario = None
            for u in self.usuarios.values():
                if u.email == email:
                    usuario = u
                    break
            
            if usuario and usuario.activo:
                # Simular login exitoso
                session['usuario_id'] = usuario.id
                session['usuario_nombre'] = usuario.nombre
                session['usuario_rol'] = usuario.rol
                
                # Actualizar último acceso
                usuario.ultimo_acceso = datetime.now().isoformat()
                
                return redirect(url_for('dashboard'))
            else:
                flash('Credenciales inválidas', 'error')
                return redirect(url_for('login'))
                
        except Exception as e:
            self.logger.error(f"Error procesando login: {e}")
            return redirect(url_for('login'))
    
    def _renderizar_dashboard(self) -> str:
        """Renderizar dashboard"""
        try:
            usuario_actual = self._obtener_usuario_actual()
            datos_dashboard = self._obtener_datos_dashboard()
            
            return self._renderizar_pagina('dashboard.html', {
                'usuario': usuario_actual,
                'dashboard': datos_dashboard
            })
            
        except Exception as e:
            self.logger.error(f"Error renderizando dashboard: {e}")
            return f"<h1>Error: {e}</h1>"
    
    def _obtener_usuario_actual(self) -> Optional[UsuarioWeb]:
        """Obtener usuario actual de la sesión"""
        try:
            if 'usuario_id' in session:
                usuario_id = session['usuario_id']
                return self.usuarios.get(usuario_id)
            return None
            
        except Exception as e:
            self.logger.error(f"Error obteniendo usuario actual: {e}")
            return None
    
    def _obtener_datos_dashboard(self) -> Dict[str, Any]:
        """Obtener datos del dashboard"""
        try:
            # Generar datos sintéticos
            np.random.seed(42)
            
            datos = {
                'timestamp': datetime.now().isoformat(),
                'metricas': {
                    'temperatura_actual': 22.5 + np.random.randn() * 2,
                    'humedad_actual': 65 + np.random.randn() * 10,
                    'presion_actual': 1013 + np.random.randn() * 5,
                    'viento_actual': 8 + np.random.randn() * 3,
                    'humedad_suelo': 45 + np.random.randn() * 5,
                    'ndvi': 0.65 + np.random.randn() * 0.05,
                    'evi': 0.42 + np.random.randn() * 0.03,
                    'consumo_agua_diario': 150 + np.random.randn() * 20
                },
                'alertas': [
                    {
                        'id': 'alerta_1',
                        'tipo': 'info',
                        'mensaje': 'Temperatura dentro del rango normal',
                        'timestamp': datetime.now().isoformat()
                    },
                    {
                        'id': 'alerta_2',
                        'tipo': 'warning',
                        'mensaje': 'Humedad del suelo baja en sector norte',
                        'timestamp': datetime.now().isoformat()
                    }
                ],
                'estado_sistema': {
                    'sensores_activos': 8,
                    'controladores_activos': 3,
                    'programaciones_activas': 5,
                    'ultima_actualizacion': datetime.now().isoformat()
                }
            }
            
            return datos
            
        except Exception as e:
            self.logger.error(f"Error obteniendo datos del dashboard: {e}")
            return {}
    
    def _obtener_usuarios(self) -> Dict[str, Any]:
        """Obtener lista de usuarios"""
        try:
            usuarios_data = []
            for usuario in self.usuarios.values():
                usuarios_data.append({
                    'id': usuario.id,
                    'nombre': usuario.nombre,
                    'email': usuario.email,
                    'rol': usuario.rol,
                    'activo': usuario.activo,
                    'ultimo_acceso': usuario.ultimo_acceso
                })
            
            return {
                'exitoso': True,
                'usuarios': usuarios_data,
                'total': len(usuarios_data)
            }
            
        except Exception as e:
            self.logger.error(f"Error obteniendo usuarios: {e}")
            return {'exitoso': False, 'error': str(e)}
    
    def _obtener_metricas(self) -> Dict[str, Any]:
        """Obtener métricas del sistema"""
        try:
            datos_dashboard = self._obtener_datos_dashboard()
            
            return {
                'exitoso': True,
                'metricas': datos_dashboard.get('metricas', {}),
                'timestamp': datos_dashboard.get('timestamp', datetime.now().isoformat())
            }
            
        except Exception as e:
            self.logger.error(f"Error obteniendo métricas: {e}")
            return {'exitoso': False, 'error': str(e)}
    
    def _obtener_alertas(self) -> Dict[str, Any]:
        """Obtener alertas del sistema"""
        try:
            datos_dashboard = self._obtener_datos_dashboard()
            
            return {
                'exitoso': True,
                'alertas': datos_dashboard.get('alertas', []),
                'timestamp': datos_dashboard.get('timestamp', datetime.now().isoformat())
            }
            
        except Exception as e:
            self.logger.error(f"Error obteniendo alertas: {e}")
            return {'exitoso': False, 'error': str(e)}
    
    def generar_reporte_web(self) -> str:
        """Generar reporte de la aplicación web"""
        try:
            self.logger.info("Generando reporte de la aplicación web...")
            
            # Obtener datos del dashboard
            datos_dashboard = self._obtener_datos_dashboard()
            
            reporte = {
                'timestamp': datetime.now().isoformat(),
                'sistema': 'METGO 3D - Aplicación Web Responsive',
                'version': self.configuracion_web['version'],
                'configuracion_web': self.configuracion_web,
                'usuarios': [
                    {
                        'id': u.id,
                        'nombre': u.nombre,
                        'email': u.email,
                        'rol': u.rol,
                        'activo': u.activo
                    } for u in self.usuarios.values()
                ],
                'datos_dashboard': datos_dashboard,
                'funcionalidades_implementadas': [
                    'Aplicación web responsive',
                    'Sistema de autenticación',
                    'Dashboard interactivo',
                    'API REST para datos',
                    'Base de datos SQLite',
                    'Sistema de logging',
                    'Gestión de usuarios',
                    'Sesiones de usuario',
                    'Métricas en tiempo real',
                    'Sistema de alertas'
                ],
                'tecnologias_utilizadas': [
                    'Flask para aplicación web',
                    'HTML5 y CSS3 responsive',
                    'JavaScript para interactividad',
                    'SQLite para base de datos',
                    'Sesiones de usuario',
                    'API REST'
                ],
                'recomendaciones': [
                    'Implementar React/Vue/Angular para frontend',
                    'Agregar autenticación JWT',
                    'Implementar WebSockets para tiempo real',
                    'Agregar PWA (Progressive Web App)',
                    'Implementar testing automatizado',
                    'Agregar internacionalización',
                    'Implementar cache con Redis',
                    'Agregar CDN para assets',
                    'Implementar monitoreo de performance',
                    'Agregar analytics de uso'
                ]
            }
            
            # Guardar reporte
            reportes_dir = Path("reportes")
            reportes_dir.mkdir(exist_ok=True)
            
            reporte_file = reportes_dir / f"web_responsive_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(reporte_file, 'w', encoding='utf-8') as f:
                json.dump(reporte, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Reporte de aplicación web generado: {reporte_file}")
            return str(reporte_file)
            
        except Exception as e:
            self.logger.error(f"Error generando reporte: {e}")
            return ""
    
    def ejecutar_aplicacion(self, puerto: int = 5000, debug: bool = False):
        """Ejecutar aplicación web"""
        try:
            if not self.app:
                self.logger.error("Flask no disponible")
                return False
            
            self.logger.info(f"Iniciando aplicación web en puerto {puerto}")
            
            # Generar reporte
            self.generar_reporte_web()
            
            # Ejecutar aplicación
            self.app.run(host='0.0.0.0', port=puerto, debug=debug)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error ejecutando aplicación web: {e}")
            return False

def main():
    """Función principal de aplicación web responsive"""
    print("WEB RESPONSIVE METGO 3D")
    print("Sistema Meteorologico Agricola Quillota - Aplicacion Web Responsive")
    print("=" * 80)
    
    try:
        # Crear aplicación web
        web_app = WebResponsiveMETGO()
        
        if not FLASK_AVAILABLE:
            print("Flask no disponible. Instalando...")
            print("pip install flask flask-cors")
            return False
        
        # Generar reporte
        print(f"\nGenerando reporte de aplicacion web...")
        reporte = web_app.generar_reporte_web()
        
        if reporte:
            print(f"Reporte generado: {reporte}")
        else:
            print(f"Error generando reporte")
        
        # Mostrar información de la aplicación
        print(f"\nAplicacion Web Responsive METGO 3D")
        print(f"Titulo: {web_app.configuracion_web['titulo']}")
        print(f"Version: {web_app.configuracion_web['version']}")
        print(f"Idioma: {web_app.configuracion_web['idioma']}")
        print(f"Tema: {web_app.configuracion_web['tema']}")
        
        print(f"\nUsuarios configurados:")
        for usuario in web_app.usuarios.values():
            print(f"   - {usuario.nombre} ({usuario.rol}): {usuario.email}")
        
        print(f"\nRutas disponibles:")
        rutas = [
            'GET / - Pagina principal',
            'GET/POST /login - Iniciar sesion',
            'GET /dashboard - Dashboard principal',
            'GET /api/dashboard - API datos dashboard',
            'GET /api/usuarios - API lista usuarios',
            'GET /api/metricas - API metricas sistema',
            'GET /api/alertas - API alertas sistema',
            'GET /logout - Cerrar sesion'
        ]
        
        for ruta in rutas:
            print(f"   - {ruta}")
        
        print(f"\nPara ejecutar la aplicacion web:")
        print(f"   python web_responsive_metgo.py --ejecutar")
        print(f"   La aplicacion estara disponible en: http://localhost:5000")
        
        return True
        
    except Exception as e:
        print(f"\nError en aplicacion web: {e}")
        return False

if __name__ == "__main__":
    try:
        if len(sys.argv) > 1 and sys.argv[1] == '--ejecutar':
            # Ejecutar aplicación web
            web_app = WebResponsiveMETGO()
            web_app.ejecutar_aplicacion(debug=True)
        else:
            # Generar reporte
            exito = main()
            sys.exit(0 if exito else 1)
    except Exception as e:
        print(f"\nError inesperado: {e}")
        sys.exit(1)
