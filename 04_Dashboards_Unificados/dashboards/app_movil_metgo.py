#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
📱 APLICACIÓN MÓVIL METGO 3D
Sistema Meteorológico Agrícola Quillota - Aplicación Móvil para Agricultores
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

# Flask para API móvil
try:
    from flask import Flask, request, jsonify, render_template, send_file
    from flask_cors import CORS
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False

# Kivy para aplicación móvil
try:
    from kivy.app import App
    from kivy.uix.boxlayout import BoxLayout
    from kivy.uix.gridlayout import GridLayout
    from kivy.uix.label import Label
    from kivy.uix.button import Button
    from kivy.uix.textinput import TextInput
    from kivy.uix.image import Image
    from kivy.uix.screenmanager import ScreenManager, Screen
    from kivy.clock import Clock
    from kivy.network.urlrequest import UrlRequest
    KIVY_AVAILABLE = True
except ImportError:
    KIVY_AVAILABLE = False

# Configuración
warnings.filterwarnings('ignore')

@dataclass
class UsuarioAgricultor:
    """Datos del usuario agricultor"""
    id: str
    nombre: str
    email: str
    telefono: str
    region: str
    cultivos: List[str]
    hectareas: float
    fecha_registro: str
    configuracion: Dict[str, Any]

@dataclass
class AlertaMovil:
    """Alerta para aplicación móvil"""
    id: str
    tipo: str
    severidad: str
    mensaje: str
    timestamp: str
    coordenadas: Tuple[float, float]
    accion_recomendada: str

class APIMovilMETGO:
    """API para aplicación móvil METGO 3D"""
    
    def __init__(self):
        self.app = Flask(__name__) if FLASK_AVAILABLE else None
        if self.app:
            CORS(self.app)
            self._configurar_rutas()
        
        self.configuracion = {
            'directorio_datos': 'data/movil',
            'directorio_usuarios': 'data/movil/usuarios',
            'directorio_alertas': 'data/movil/alertas',
            'directorio_logs': 'logs/movil',
            'directorio_reportes': 'reportes/movil',
            'version': '2.0',
            'timestamp': datetime.now().isoformat()
        }
        
        # Crear directorios
        self._crear_directorios()
        
        # Inicializar logger
        self.logger = logging.getLogger('METGO_MOVIL')
        
        # Configurar logging
        self._configurar_logging()
        
        # Base de datos
        self._inicializar_base_datos()
        
        # Usuarios y alertas
        self.usuarios = {}
        self.alertas = {}
        
        # Configuración de la app
        self.configuracion_app = {
            'titulo': 'METGO 3D - Agricultor',
            'version': '2.0',
            'descripcion': 'Sistema meteorológico agrícola para agricultores',
            'icono': 'icono_metgo.png',
            'colores': {
                'primario': '#2E8B57',
                'secundario': '#90EE90',
                'accento': '#FFD700',
                'texto': '#000000',
                'fondo': '#F5F5F5'
            },
            'funcionalidades': [
                'Pronósticos meteorológicos',
                'Alertas personalizadas',
                'Recomendaciones agrícolas',
                'Historial de datos',
                'Configuración de cultivos',
                'Notificaciones push',
                'Mapas interactivos',
                'Reportes de campo'
            ]
        }
    
    def _crear_directorios(self):
        """Crear directorios necesarios"""
        try:
            for directorio in self.configuracion.values():
                if isinstance(directorio, str) and '/' in directorio:
                    Path(directorio).mkdir(parents=True, exist_ok=True)
        except Exception as e:
            print(f"Error creando directorios: {e}")
            # Inicializar logger básico si hay error
            if not hasattr(self, 'logger'):
                self.logger = logging.getLogger('METGO_MOVIL')
    
    def _configurar_logging(self):
        """Configurar sistema de logging"""
        try:
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                handlers=[
                    logging.FileHandler(f"{self.configuracion['directorio_logs']}/movil.log"),
                    logging.StreamHandler()
                ]
            )
            self.logger = logging.getLogger('METGO_MOVIL')
            self.logger.info("Sistema de logging configurado")
        except Exception as e:
            print(f"Error configurando logging: {e}")
            self.logger = logging.getLogger('METGO_MOVIL')
    
    def _inicializar_base_datos(self):
        """Inicializar base de datos SQLite"""
        try:
            archivo_bd = f"{self.configuracion['directorio_datos']}/movil.db"
            
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
            # Tabla de usuarios
            self.cursor_bd.execute('''
                CREATE TABLE IF NOT EXISTS usuarios (
                    id TEXT PRIMARY KEY,
                    nombre TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    telefono TEXT,
                    region TEXT NOT NULL,
                    cultivos TEXT NOT NULL,
                    hectareas REAL NOT NULL,
                    fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP,
                    configuracion TEXT,
                    activo BOOLEAN DEFAULT TRUE
                )
            ''')
            
            # Tabla de alertas
            self.cursor_bd.execute('''
                CREATE TABLE IF NOT EXISTS alertas_movil (
                    id TEXT PRIMARY KEY,
                    usuario_id TEXT NOT NULL,
                    tipo TEXT NOT NULL,
                    severidad TEXT NOT NULL,
                    mensaje TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    coordenadas TEXT,
                    accion_recomendada TEXT,
                    leida BOOLEAN DEFAULT FALSE,
                    FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
                )
            ''')
            
            # Tabla de configuraciones
            self.cursor_bd.execute('''
                CREATE TABLE IF NOT EXISTS configuraciones_movil (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    usuario_id TEXT NOT NULL,
                    configuracion TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
                )
            ''')
            
            # Crear índices
            self.cursor_bd.execute('CREATE INDEX IF NOT EXISTS idx_usuarios_email ON usuarios(email)')
            self.cursor_bd.execute('CREATE INDEX IF NOT EXISTS idx_alertas_usuario ON alertas_movil(usuario_id)')
            self.cursor_bd.execute('CREATE INDEX IF NOT EXISTS idx_configuraciones_usuario ON configuraciones_movil(usuario_id)')
            
            self.conexion_bd.commit()
            self.logger.info("Tablas de base de datos creadas")
            
        except Exception as e:
            self.logger.error(f"Error creando tablas: {e}")
    
    def _configurar_rutas(self):
        """Configurar rutas de la API"""
        try:
            if not self.app:
                return
            
            @self.app.route('/')
            def index():
                return jsonify({
                    'mensaje': 'API METGO 3D Móvil',
                    'version': self.configuracion_app['version'],
                    'timestamp': datetime.now().isoformat()
                })
            
            @self.app.route('/usuarios', methods=['GET', 'POST'])
            def gestionar_usuarios():
                if request.method == 'GET':
                    return self._obtener_usuarios()
                elif request.method == 'POST':
                    return self._crear_usuario()
            
            @self.app.route('/usuarios/<usuario_id>', methods=['GET', 'PUT', 'DELETE'])
            def gestionar_usuario(usuario_id):
                if request.method == 'GET':
                    return self._obtener_usuario(usuario_id)
                elif request.method == 'PUT':
                    return self._actualizar_usuario(usuario_id)
                elif request.method == 'DELETE':
                    return self._eliminar_usuario(usuario_id)
            
            @self.app.route('/alertas', methods=['GET', 'POST'])
            def gestionar_alertas():
                if request.method == 'GET':
                    return self._obtener_alertas()
                elif request.method == 'POST':
                    return self._crear_alerta()
            
            @self.app.route('/alertas/<usuario_id>', methods=['GET'])
            def obtener_alertas_usuario(usuario_id):
                return self._obtener_alertas_usuario(usuario_id)
            
            @self.app.route('/pronostico/<usuario_id>', methods=['GET'])
            def obtener_pronostico(usuario_id):
                return self._obtener_pronostico_usuario(usuario_id)
            
            @self.app.route('/recomendaciones/<usuario_id>', methods=['GET'])
            def obtener_recomendaciones(usuario_id):
                return self._obtener_recomendaciones_usuario(usuario_id)
            
            @self.app.route('/configuracion/<usuario_id>', methods=['GET', 'PUT'])
            def gestionar_configuracion(usuario_id):
                if request.method == 'GET':
                    return self._obtener_configuracion(usuario_id)
                elif request.method == 'PUT':
                    return self._actualizar_configuracion(usuario_id)
            
            @self.app.route('/estadisticas', methods=['GET'])
            def obtener_estadisticas():
                return self._obtener_estadisticas()
            
            self.logger.info("Rutas de API configuradas")
            
        except Exception as e:
            self.logger.error(f"Error configurando rutas: {e}")
    
    def _obtener_usuarios(self):
        """Obtener todos los usuarios"""
        try:
            self.cursor_bd.execute('SELECT * FROM usuarios WHERE activo = TRUE')
            usuarios = self.cursor_bd.fetchall()
            
            usuarios_data = []
            for usuario in usuarios:
                usuarios_data.append({
                    'id': usuario[0],
                    'nombre': usuario[1],
                    'email': usuario[2],
                    'telefono': usuario[3],
                    'region': usuario[4],
                    'cultivos': json.loads(usuario[5]),
                    'hectareas': usuario[6],
                    'fecha_registro': usuario[7],
                    'configuracion': json.loads(usuario[8]) if usuario[8] else {}
                })
            
            return jsonify({
                'exitoso': True,
                'usuarios': usuarios_data,
                'total': len(usuarios_data)
            })
            
        except Exception as e:
            self.logger.error(f"Error obteniendo usuarios: {e}")
            return jsonify({'exitoso': False, 'error': str(e)}), 500
    
    def _crear_usuario(self):
        """Crear nuevo usuario"""
        try:
            data = request.get_json()
            
            usuario_id = f"user_{int(time.time())}"
            
            self.cursor_bd.execute('''
                INSERT INTO usuarios 
                (id, nombre, email, telefono, region, cultivos, hectareas, configuracion)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                usuario_id,
                data.get('nombre'),
                data.get('email'),
                data.get('telefono'),
                data.get('region'),
                json.dumps(data.get('cultivos', [])),
                data.get('hectareas', 0.0),
                json.dumps(data.get('configuracion', {}))
            ))
            
            self.conexion_bd.commit()
            
            return jsonify({
                'exitoso': True,
                'mensaje': 'Usuario creado exitosamente',
                'usuario_id': usuario_id
            })
            
        except Exception as e:
            self.logger.error(f"Error creando usuario: {e}")
            return jsonify({'exitoso': False, 'error': str(e)}), 500
    
    def _obtener_usuario(self, usuario_id):
        """Obtener usuario específico"""
        try:
            self.cursor_bd.execute('SELECT * FROM usuarios WHERE id = ? AND activo = TRUE', (usuario_id,))
            usuario = self.cursor_bd.fetchone()
            
            if usuario:
                return jsonify({
                    'exitoso': True,
                    'usuario': {
                        'id': usuario[0],
                        'nombre': usuario[1],
                        'email': usuario[2],
                        'telefono': usuario[3],
                        'region': usuario[4],
                        'cultivos': json.loads(usuario[5]),
                        'hectareas': usuario[6],
                        'fecha_registro': usuario[7],
                        'configuracion': json.loads(usuario[8]) if usuario[8] else {}
                    }
                })
            else:
                return jsonify({'exitoso': False, 'error': 'Usuario no encontrado'}), 404
                
        except Exception as e:
            self.logger.error(f"Error obteniendo usuario: {e}")
            return jsonify({'exitoso': False, 'error': str(e)}), 500
    
    def _actualizar_usuario(self, usuario_id):
        """Actualizar usuario"""
        try:
            data = request.get_json()
            
            # Construir query de actualización
            campos = []
            valores = []
            
            for campo, valor in data.items():
                if campo in ['nombre', 'telefono', 'region', 'hectareas']:
                    campos.append(f"{campo} = ?")
                    valores.append(valor)
                elif campo in ['cultivos', 'configuracion']:
                    campos.append(f"{campo} = ?")
                    valores.append(json.dumps(valor))
            
            if campos:
                valores.append(usuario_id)
                query = f"UPDATE usuarios SET {', '.join(campos)} WHERE id = ?"
                
                self.cursor_bd.execute(query, valores)
                self.conexion_bd.commit()
                
                return jsonify({
                    'exitoso': True,
                    'mensaje': 'Usuario actualizado exitosamente'
                })
            else:
                return jsonify({'exitoso': False, 'error': 'No hay campos para actualizar'}), 400
                
        except Exception as e:
            self.logger.error(f"Error actualizando usuario: {e}")
            return jsonify({'exitoso': False, 'error': str(e)}), 500
    
    def _eliminar_usuario(self, usuario_id):
        """Eliminar usuario (soft delete)"""
        try:
            self.cursor_bd.execute('UPDATE usuarios SET activo = FALSE WHERE id = ?', (usuario_id,))
            self.conexion_bd.commit()
            
            return jsonify({
                'exitoso': True,
                'mensaje': 'Usuario eliminado exitosamente'
            })
            
        except Exception as e:
            self.logger.error(f"Error eliminando usuario: {e}")
            return jsonify({'exitoso': False, 'error': str(e)}), 500
    
    def _obtener_alertas(self):
        """Obtener todas las alertas"""
        try:
            self.cursor_bd.execute('''
                SELECT a.*, u.nombre as usuario_nombre 
                FROM alertas_movil a 
                JOIN usuarios u ON a.usuario_id = u.id 
                WHERE u.activo = TRUE
                ORDER BY a.timestamp DESC
            ''')
            alertas = self.cursor_bd.fetchall()
            
            alertas_data = []
            for alerta in alertas:
                alertas_data.append({
                    'id': alerta[0],
                    'usuario_id': alerta[1],
                    'usuario_nombre': alerta[8],
                    'tipo': alerta[2],
                    'severidad': alerta[3],
                    'mensaje': alerta[4],
                    'timestamp': alerta[5],
                    'coordenadas': json.loads(alerta[6]) if alerta[6] else None,
                    'accion_recomendada': alerta[7],
                    'leida': bool(alerta[9])
                })
            
            return jsonify({
                'exitoso': True,
                'alertas': alertas_data,
                'total': len(alertas_data)
            })
            
        except Exception as e:
            self.logger.error(f"Error obteniendo alertas: {e}")
            return jsonify({'exitoso': False, 'error': str(e)}), 500
    
    def _crear_alerta(self):
        """Crear nueva alerta"""
        try:
            data = request.get_json()
            
            alerta_id = f"alerta_{int(time.time())}"
            
            self.cursor_bd.execute('''
                INSERT INTO alertas_movil 
                (id, usuario_id, tipo, severidad, mensaje, coordenadas, accion_recomendada)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                alerta_id,
                data.get('usuario_id'),
                data.get('tipo'),
                data.get('severidad'),
                data.get('mensaje'),
                json.dumps(data.get('coordenadas', [])),
                data.get('accion_recomendada', '')
            ))
            
            self.conexion_bd.commit()
            
            return jsonify({
                'exitoso': True,
                'mensaje': 'Alerta creada exitosamente',
                'alerta_id': alerta_id
            })
            
        except Exception as e:
            self.logger.error(f"Error creando alerta: {e}")
            return jsonify({'exitoso': False, 'error': str(e)}), 500
    
    def _obtener_alertas_usuario(self, usuario_id):
        """Obtener alertas de un usuario específico"""
        try:
            self.cursor_bd.execute('''
                SELECT * FROM alertas_movil 
                WHERE usuario_id = ? 
                ORDER BY timestamp DESC
            ''', (usuario_id,))
            alertas = self.cursor_bd.fetchall()
            
            alertas_data = []
            for alerta in alertas:
                alertas_data.append({
                    'id': alerta[0],
                    'usuario_id': alerta[1],
                    'tipo': alerta[2],
                    'severidad': alerta[3],
                    'mensaje': alerta[4],
                    'timestamp': alerta[5],
                    'coordenadas': json.loads(alerta[6]) if alerta[6] else None,
                    'accion_recomendada': alerta[7],
                    'leida': bool(alerta[9])
                })
            
            return jsonify({
                'exitoso': True,
                'alertas': alertas_data,
                'total': len(alertas_data)
            })
            
        except Exception as e:
            self.logger.error(f"Error obteniendo alertas de usuario: {e}")
            return jsonify({'exitoso': False, 'error': str(e)}), 500
    
    def _obtener_pronostico_usuario(self, usuario_id):
        """Obtener pronóstico para un usuario"""
        try:
            # Obtener datos del usuario
            self.cursor_bd.execute('SELECT * FROM usuarios WHERE id = ? AND activo = TRUE', (usuario_id,))
            usuario = self.cursor_bd.fetchone()
            
            if not usuario:
                return jsonify({'exitoso': False, 'error': 'Usuario no encontrado'}), 404
            
            # Generar pronóstico sintético
            pronostico = self._generar_pronostico_sintetico(usuario)
            
            return jsonify({
                'exitoso': True,
                'pronostico': pronostico,
                'usuario_id': usuario_id,
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            self.logger.error(f"Error obteniendo pronóstico: {e}")
            return jsonify({'exitoso': False, 'error': str(e)}), 500
    
    def _generar_pronostico_sintetico(self, usuario):
        """Generar pronóstico sintético para un usuario"""
        try:
            np.random.seed(42)
            
            # Pronóstico para los próximos 7 días
            dias = 7
            fechas = [(datetime.now() + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(dias)]
            
            pronostico = []
            for i, fecha in enumerate(fechas):
                # Generar datos meteorológicos sintéticos
                temperatura_min = 8 + np.random.randn() * 2
                temperatura_max = 22 + np.random.randn() * 3
                humedad = 60 + np.random.randn() * 15
                precipitacion = max(0, np.random.randn() * 5)
                viento = 5 + np.random.randn() * 3
                
                # Condiciones del día
                if precipitacion > 5:
                    condicion = 'Lluvia'
                elif temperatura_max > 25:
                    condicion = 'Soleado'
                elif temperatura_max < 15:
                    condicion = 'Nublado'
                else:
                    condicion = 'Parcialmente nublado'
                
                pronostico.append({
                    'fecha': fecha,
                    'temperatura_min': round(temperatura_min, 1),
                    'temperatura_max': round(temperatura_max, 1),
                    'humedad': round(humedad, 1),
                    'precipitacion': round(precipitacion, 1),
                    'viento': round(viento, 1),
                    'condicion': condicion
                })
            
            return pronostico
            
        except Exception as e:
            self.logger.error(f"Error generando pronóstico sintético: {e}")
            return []
    
    def _obtener_recomendaciones_usuario(self, usuario_id):
        """Obtener recomendaciones para un usuario"""
        try:
            # Obtener datos del usuario
            self.cursor_bd.execute('SELECT * FROM usuarios WHERE id = ? AND activo = TRUE', (usuario_id,))
            usuario = self.cursor_bd.fetchone()
            
            if not usuario:
                return jsonify({'exitoso': False, 'error': 'Usuario no encontrado'}), 404
            
            # Generar recomendaciones
            recomendaciones = self._generar_recomendaciones(usuario)
            
            return jsonify({
                'exitoso': True,
                'recomendaciones': recomendaciones,
                'usuario_id': usuario_id,
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            self.logger.error(f"Error obteniendo recomendaciones: {e}")
            return jsonify({'exitoso': False, 'error': str(e)}), 500
    
    def _generar_recomendaciones(self, usuario):
        """Generar recomendaciones para un usuario"""
        try:
            cultivos = json.loads(usuario[5])
            region = usuario[4]
            
            recomendaciones = []
            
            # Recomendaciones generales
            recomendaciones.append({
                'tipo': 'General',
                'titulo': 'Monitoreo del clima',
                'descripcion': 'Revise diariamente las condiciones meteorológicas para tomar decisiones informadas sobre sus cultivos.',
                'prioridad': 'Media',
                'accion': 'Consultar pronóstico diario'
            })
            
            # Recomendaciones por cultivo
            for cultivo in cultivos:
                if cultivo.lower() in ['tomate', 'tomates']:
                    recomendaciones.append({
                        'tipo': 'Cultivo',
                        'titulo': f'Cuidado del {cultivo}',
                        'descripcion': 'Los tomates requieren riego regular y protección contra heladas.',
                        'prioridad': 'Alta',
                        'accion': 'Verificar sistema de riego'
                    })
                elif cultivo.lower() in ['lechuga', 'lechugas']:
                    recomendaciones.append({
                        'tipo': 'Cultivo',
                        'titulo': f'Cuidado de la {cultivo}',
                        'descripcion': 'La lechuga necesita sombra parcial y riego frecuente.',
                        'prioridad': 'Media',
                        'accion': 'Ajustar sombreado'
                    })
            
            # Recomendaciones por región
            if region.lower() in ['quillota', 'valparaíso']:
                recomendaciones.append({
                    'tipo': 'Regional',
                    'titulo': 'Clima de la región',
                    'descripcion': 'La región de Quillota tiene un clima mediterráneo ideal para diversos cultivos.',
                    'prioridad': 'Baja',
                    'accion': 'Aprovechar condiciones climáticas'
                })
            
            return recomendaciones
            
        except Exception as e:
            self.logger.error(f"Error generando recomendaciones: {e}")
            return []
    
    def _obtener_configuracion(self, usuario_id):
        """Obtener configuración de un usuario"""
        try:
            self.cursor_bd.execute('SELECT configuracion FROM usuarios WHERE id = ? AND activo = TRUE', (usuario_id,))
            resultado = self.cursor_bd.fetchone()
            
            if resultado:
                configuracion = json.loads(resultado[0]) if resultado[0] else {}
                return jsonify({
                    'exitoso': True,
                    'configuracion': configuracion
                })
            else:
                return jsonify({'exitoso': False, 'error': 'Usuario no encontrado'}), 404
                
        except Exception as e:
            self.logger.error(f"Error obteniendo configuración: {e}")
            return jsonify({'exitoso': False, 'error': str(e)}), 500
    
    def _actualizar_configuracion(self, usuario_id):
        """Actualizar configuración de un usuario"""
        try:
            data = request.get_json()
            
            self.cursor_bd.execute('''
                UPDATE usuarios 
                SET configuracion = ? 
                WHERE id = ? AND activo = TRUE
            ''', (json.dumps(data), usuario_id))
            
            self.conexion_bd.commit()
            
            return jsonify({
                'exitoso': True,
                'mensaje': 'Configuración actualizada exitosamente'
            })
            
        except Exception as e:
            self.logger.error(f"Error actualizando configuración: {e}")
            return jsonify({'exitoso': False, 'error': str(e)}), 500
    
    def _obtener_estadisticas(self):
        """Obtener estadísticas de la aplicación móvil"""
        try:
            # Contar usuarios activos
            self.cursor_bd.execute('SELECT COUNT(*) FROM usuarios WHERE activo = TRUE')
            total_usuarios = self.cursor_bd.fetchone()[0]
            
            # Contar alertas
            self.cursor_bd.execute('SELECT COUNT(*) FROM alertas_movil')
            total_alertas = self.cursor_bd.fetchone()[0]
            
            # Contar alertas no leídas
            self.cursor_bd.execute('SELECT COUNT(*) FROM alertas_movil WHERE leida = FALSE')
            alertas_no_leidas = self.cursor_bd.fetchone()[0]
            
            # Estadísticas por región
            self.cursor_bd.execute('SELECT region, COUNT(*) FROM usuarios WHERE activo = TRUE GROUP BY region')
            usuarios_por_region = dict(self.cursor_bd.fetchall())
            
            # Estadísticas por cultivo
            self.cursor_bd.execute('SELECT cultivos FROM usuarios WHERE activo = TRUE')
            cultivos_data = self.cursor_bd.fetchall()
            
            cultivos_contador = {}
            for cultivos_json in cultivos_data:
                cultivos = json.loads(cultivos_json[0])
                for cultivo in cultivos:
                    cultivos_contador[cultivo] = cultivos_contador.get(cultivo, 0) + 1
            
            return jsonify({
                'exitoso': True,
                'estadisticas': {
                    'total_usuarios': total_usuarios,
                    'total_alertas': total_alertas,
                    'alertas_no_leidas': alertas_no_leidas,
                    'usuarios_por_region': usuarios_por_region,
                    'cultivos_populares': dict(sorted(cultivos_contador.items(), key=lambda x: x[1], reverse=True)[:5])
                },
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            self.logger.error(f"Error obteniendo estadísticas: {e}")
            return jsonify({'exitoso': False, 'error': str(e)}), 500
    
    def crear_datos_demo(self):
        """Crear datos de demostración"""
        try:
            self.logger.info("Creando datos de demostración...")
            
            # Usuarios demo
            usuarios_demo = [
                {
                    'nombre': 'Juan Pérez',
                    'email': 'juan.perez@email.com',
                    'telefono': '+56912345678',
                    'region': 'Quillota',
                    'cultivos': ['Tomate', 'Lechuga', 'Pimiento'],
                    'hectareas': 5.5,
                    'configuracion': {
                        'notificaciones': True,
                        'idioma': 'es',
                        'unidades': 'métrico'
                    }
                },
                {
                    'nombre': 'María González',
                    'email': 'maria.gonzalez@email.com',
                    'telefono': '+56987654321',
                    'region': 'Valparaíso',
                    'cultivos': ['Palta', 'Cítricos'],
                    'hectareas': 12.0,
                    'configuracion': {
                        'notificaciones': True,
                        'idioma': 'es',
                        'unidades': 'métrico'
                    }
                }
            ]
            
            # Crear usuarios
            for usuario_data in usuarios_demo:
                self._crear_usuario_demo(usuario_data)
            
            # Crear alertas demo
            self._crear_alertas_demo()
            
            self.logger.info("Datos de demostración creados exitosamente")
            
        except Exception as e:
            self.logger.error(f"Error creando datos demo: {e}")
    
    def _crear_usuario_demo(self, usuario_data):
        """Crear usuario de demostración"""
        try:
            usuario_id = f"demo_{int(time.time())}"
            
            self.cursor_bd.execute('''
                INSERT INTO usuarios 
                (id, nombre, email, telefono, region, cultivos, hectareas, configuracion)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                usuario_id,
                usuario_data['nombre'],
                usuario_data['email'],
                usuario_data['telefono'],
                usuario_data['region'],
                json.dumps(usuario_data['cultivos']),
                usuario_data['hectareas'],
                json.dumps(usuario_data['configuracion'])
            ))
            
            self.conexion_bd.commit()
            
        except Exception as e:
            self.logger.error(f"Error creando usuario demo: {e}")
    
    def _crear_alertas_demo(self):
        """Crear alertas de demostración"""
        try:
            # Obtener usuarios demo
            self.cursor_bd.execute('SELECT id FROM usuarios WHERE nombre LIKE "Juan%" OR nombre LIKE "María%"')
            usuarios_demo = self.cursor_bd.fetchall()
            
            alertas_demo = [
                {
                    'tipo': 'Helada',
                    'severidad': 'Alta',
                    'mensaje': 'Posible helada en las próximas 24 horas. Proteja sus cultivos sensibles.',
                    'accion_recomendada': 'Cubrir cultivos con mallas o plásticos'
                },
                {
                    'tipo': 'Sequía',
                    'severidad': 'Media',
                    'mensaje': 'Período de sequía prolongado. Considere aumentar el riego.',
                    'accion_recomendada': 'Aumentar frecuencia de riego'
                },
                {
                    'tipo': 'Lluvia',
                    'severidad': 'Baja',
                    'mensaje': 'Lluvia moderada esperada. Reduzca el riego programado.',
                    'accion_recomendada': 'Suspender riego automático'
                }
            ]
            
            for usuario in usuarios_demo:
                for alerta_data in alertas_demo:
                    alerta_id = f"demo_alerta_{int(time.time())}"
                    
                    self.cursor_bd.execute('''
                        INSERT INTO alertas_movil 
                        (id, usuario_id, tipo, severidad, mensaje, accion_recomendada)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (
                        alerta_id,
                        usuario[0],
                        alerta_data['tipo'],
                        alerta_data['severidad'],
                        alerta_data['mensaje'],
                        alerta_data['accion_recomendada']
                    ))
                    
                    time.sleep(0.1)  # Pequeña pausa para evitar IDs duplicados
            
            self.conexion_bd.commit()
            
        except Exception as e:
            self.logger.error(f"Error creando alertas demo: {e}")
    
    def generar_reporte_movil(self) -> str:
        """Generar reporte de la aplicación móvil"""
        try:
            self.logger.info("Generando reporte de aplicación móvil...")
            
            # Crear datos demo
            self.crear_datos_demo()
            
            # Obtener estadísticas
            estadisticas = self._obtener_estadisticas()
            
            reporte = {
                'timestamp': datetime.now().isoformat(),
                'sistema': 'METGO 3D - Aplicación Móvil',
                'version': self.configuracion_app['version'],
                'configuracion_app': self.configuracion_app,
                'estadisticas': estadisticas.get_json() if hasattr(estadisticas, 'get_json') else estadisticas,
                'funcionalidades_implementadas': [
                    'API REST para comunicación móvil',
                    'Gestión de usuarios agricultores',
                    'Sistema de alertas personalizadas',
                    'Pronósticos meteorológicos',
                    'Recomendaciones agrícolas',
                    'Configuración personalizada',
                    'Base de datos SQLite',
                    'Sistema de logging',
                    'Datos de demostración'
                ],
                'tecnologias_utilizadas': [
                    'Flask para API REST',
                    'SQLite para base de datos',
                    'JSON para intercambio de datos',
                    'CORS para comunicación móvil',
                    'Logging estructurado'
                ],
                'endpoints_disponibles': [
                    'GET / - Información general',
                    'GET/POST /usuarios - Gestión de usuarios',
                    'GET/PUT/DELETE /usuarios/<id> - Usuario específico',
                    'GET/POST /alertas - Gestión de alertas',
                    'GET /alertas/<usuario_id> - Alertas por usuario',
                    'GET /pronostico/<usuario_id> - Pronóstico personalizado',
                    'GET /recomendaciones/<usuario_id> - Recomendaciones',
                    'GET/PUT /configuracion/<usuario_id> - Configuración',
                    'GET /estadisticas - Estadísticas generales'
                ],
                'recomendaciones': [
                    'Implementar autenticación JWT',
                    'Agregar notificaciones push',
                    'Implementar sincronización offline',
                    'Agregar mapas interactivos',
                    'Implementar chat en tiempo real',
                    'Agregar análisis de rendimiento',
                    'Implementar backup automático',
                    'Agregar soporte multiidioma',
                    'Implementar modo oscuro',
                    'Agregar widgets para pantalla de inicio'
                ]
            }
            
            # Guardar reporte
            reportes_dir = Path("reportes")
            reportes_dir.mkdir(exist_ok=True)
            
            reporte_file = reportes_dir / f"app_movil_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(reporte_file, 'w', encoding='utf-8') as f:
                json.dump(reporte, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Reporte de aplicación móvil generado: {reporte_file}")
            return str(reporte_file)
            
        except Exception as e:
            self.logger.error(f"Error generando reporte: {e}")
            return ""
    
    def ejecutar_api(self, puerto: int = 5000, debug: bool = False):
        """Ejecutar la API móvil"""
        try:
            if not self.app:
                self.logger.error("Flask no disponible")
                return False
            
            self.logger.info(f"Iniciando API móvil en puerto {puerto}")
            
            # Crear datos demo
            self.crear_datos_demo()
            
            # Ejecutar aplicación
            self.app.run(host='0.0.0.0', port=puerto, debug=debug)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error ejecutando API: {e}")
            return False

def main():
    """Función principal de aplicación móvil"""
    print("APLICACION MOVIL METGO 3D")
    print("Sistema Meteorologico Agricola Quillota - App Movil para Agricultores")
    print("=" * 80)
    
    try:
        # Crear sistema de aplicación móvil
        app_movil = APIMovilMETGO()
        
        if not FLASK_AVAILABLE:
            print("Flask no disponible. Instalando...")
            print("pip install flask flask-cors")
            return False
        
        # Generar reporte
        print(f"\nGenerando reporte de aplicación móvil...")
        reporte = app_movil.generar_reporte_movil()
        
        if reporte:
            print(f"Reporte generado: {reporte}")
        else:
            print(f"Error generando reporte")
        
        # Mostrar información de la API
        print(f"\nAPI Móvil METGO 3D")
        print(f"Version: {app_movil.configuracion_app['version']}")
        print(f"Titulo: {app_movil.configuracion_app['titulo']}")
        print(f"Descripcion: {app_movil.configuracion_app['descripcion']}")
        
        print(f"\nFuncionalidades implementadas:")
        for func in app_movil.configuracion_app['funcionalidades']:
            print(f"   - {func}")
        
        print(f"\nEndpoints disponibles:")
        endpoints = [
            'GET / - Informacion general',
            'GET/POST /usuarios - Gestion de usuarios',
            'GET/PUT/DELETE /usuarios/<id> - Usuario especifico',
            'GET/POST /alertas - Gestion de alertas',
            'GET /alertas/<usuario_id> - Alertas por usuario',
            'GET /pronostico/<usuario_id> - Pronostico personalizado',
            'GET /recomendaciones/<usuario_id> - Recomendaciones',
            'GET/PUT /configuracion/<usuario_id> - Configuracion',
            'GET /estadisticas - Estadisticas generales'
        ]
        
        for endpoint in endpoints:
            print(f"   - {endpoint}")
        
        print(f"\nPara ejecutar la API:")
        print(f"   python app_movil_metgo.py --ejecutar")
        print(f"   La API estara disponible en: http://localhost:5000")
        
        return True
        
    except Exception as e:
        print(f"\nError en aplicación móvil: {e}")
        return False

if __name__ == "__main__":
    try:
        if len(sys.argv) > 1 and sys.argv[1] == '--ejecutar':
            # Ejecutar API
            app_movil = APIMovilMETGO()
            app_movil.ejecutar_api(debug=True)
        else:
            # Generar reporte
            exito = main()
            sys.exit(0 if exito else 1)
    except Exception as e:
        print(f"\nError inesperado: {e}")
        sys.exit(1)
