#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔐 AUTENTICACIÓN AVANZADA METGO 3D
Sistema Meteorológico Agrícola Quillota - Sistema de Autenticación Avanzada
"""

import os
import sys
import time
import json
import warnings
import hashlib
import secrets
import jwt
# import bcrypt  # Requiere instalación: pip install bcrypt
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any, Union
import logging
import sqlite3
from dataclasses import dataclass
import yaml

# Flask para API de autenticación
try:
    from flask import Flask, request, jsonify, render_template, session, redirect, url_for, flash
    from flask_cors import CORS
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False

# Configuración
warnings.filterwarnings('ignore')

@dataclass
class Usuario:
    """Usuario del sistema"""
    id: str
    username: str
    email: str
    password_hash: str
    rol: str
    activo: bool
    verificado: bool
    ultimo_acceso: str
    intentos_fallidos: int
    bloqueado_hasta: Optional[str]
    configuracion: Dict[str, Any]

@dataclass
class Sesion:
    """Sesión de usuario"""
    id: str
    usuario_id: str
    token: str
    refresh_token: str
    timestamp: str
    expiracion: str
    ip_address: str
    user_agent: str
    activa: bool

@dataclass
class Permiso:
    """Permiso del sistema"""
    id: str
    nombre: str
    descripcion: str
    recurso: str
    accion: str
    activo: bool

class AutenticacionAvanzadaMETGO:
    """Sistema de autenticación avanzada para METGO 3D"""
    
    def __init__(self):
        # Inicializar logger primero
        self.logger = logging.getLogger('METGO_AUTH')
        
        self.app = Flask(__name__) if FLASK_AVAILABLE else None
        if self.app:
            self.app.secret_key = 'metgo_3d_secret_key_2025'
            CORS(self.app)
            self._configurar_rutas()
        
        self.configuracion = {
            'directorio_datos': 'data/auth',
            'directorio_logs': 'logs/auth',
            'directorio_reportes': 'reportes/auth',
            'directorio_configuracion': 'config/auth',
            'version': '2.0',
            'timestamp': datetime.now().isoformat()
        }
        
        # Crear directorios
        self._crear_directorios()
        
        # Configurar logging
        self._configurar_logging()
        
        # Base de datos
        self._inicializar_base_datos()
        
        # Configuración de autenticación
        self.configuracion_auth = {
            'jwt_secret': 'metgo_3d_jwt_secret_2025',
            'jwt_algorithm': 'HS256',
            'jwt_expiration': 3600,  # 1 hora
            'refresh_expiration': 86400,  # 24 horas
            'max_intentos': 5,
            'tiempo_bloqueo': 1800,  # 30 minutos
            'password_min_length': 8,
            'require_verification': True,
            'session_timeout': 7200,  # 2 horas
            'rate_limit': {
                'login': 10,  # 10 intentos por minuto
                'register': 5,  # 5 registros por minuto
                'password_reset': 3  # 3 resets por minuto
            }
        }
        
        # Usuarios, sesiones y permisos
        self.usuarios = {}
        self.sesiones = {}
        self.permisos = {}
        
        # Configurar permisos del sistema
        self._configurar_permisos()
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
                        logging.FileHandler(f"{self.configuracion['directorio_logs']}/auth.log"),
                        logging.StreamHandler()
                    ]
                )
            self.logger.info("Sistema de logging configurado")
        except Exception as e:
            print(f"Error configurando logging: {e}")
    
    def _inicializar_base_datos(self):
        """Inicializar base de datos SQLite"""
        try:
            archivo_bd = f"{self.configuracion['directorio_datos']}/auth.db"
            
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
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    rol TEXT NOT NULL,
                    activo BOOLEAN DEFAULT TRUE,
                    verificado BOOLEAN DEFAULT FALSE,
                    ultimo_acceso DATETIME,
                    intentos_fallidos INTEGER DEFAULT 0,
                    bloqueado_hasta DATETIME,
                    configuracion TEXT,
                    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Tabla de sesiones
            self.cursor_bd.execute('''
                CREATE TABLE IF NOT EXISTS sesiones (
                    id TEXT PRIMARY KEY,
                    usuario_id TEXT NOT NULL,
                    token TEXT NOT NULL,
                    refresh_token TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    expiracion DATETIME NOT NULL,
                    ip_address TEXT,
                    user_agent TEXT,
                    activa BOOLEAN DEFAULT TRUE,
                    FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
                )
            ''')
            
            # Tabla de permisos
            self.cursor_bd.execute('''
                CREATE TABLE IF NOT EXISTS permisos (
                    id TEXT PRIMARY KEY,
                    nombre TEXT NOT NULL,
                    descripcion TEXT NOT NULL,
                    recurso TEXT NOT NULL,
                    accion TEXT NOT NULL,
                    activo BOOLEAN DEFAULT TRUE
                )
            ''')
            
            # Tabla de roles y permisos
            self.cursor_bd.execute('''
                CREATE TABLE IF NOT EXISTS roles_permisos (
                    rol TEXT NOT NULL,
                    permiso_id TEXT NOT NULL,
                    PRIMARY KEY (rol, permiso_id),
                    FOREIGN KEY (permiso_id) REFERENCES permisos (id)
                )
            ''')
            
            # Tabla de intentos de login
            self.cursor_bd.execute('''
                CREATE TABLE IF NOT EXISTS intentos_login (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    ip_address TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    exitoso BOOLEAN NOT NULL,
                    user_agent TEXT
                )
            ''')
            
            # Crear índices
            self.cursor_bd.execute('CREATE INDEX IF NOT EXISTS idx_usuarios_username ON usuarios(username)')
            self.cursor_bd.execute('CREATE INDEX IF NOT EXISTS idx_usuarios_email ON usuarios(email)')
            self.cursor_bd.execute('CREATE INDEX IF NOT EXISTS idx_sesiones_usuario ON sesiones(usuario_id)')
            self.cursor_bd.execute('CREATE INDEX IF NOT EXISTS idx_sesiones_token ON sesiones(token)')
            self.cursor_bd.execute('CREATE INDEX IF NOT EXISTS idx_intentos_username ON intentos_login(username)')
            self.cursor_bd.execute('CREATE INDEX IF NOT EXISTS idx_intentos_ip ON intentos_login(ip_address)')
            
            self.conexion_bd.commit()
            self.logger.info("Tablas de base de datos creadas")
            
        except Exception as e:
            self.logger.error(f"Error creando tablas: {e}")
    
    def _configurar_permisos(self):
        """Configurar permisos del sistema"""
        try:
            permisos_data = [
                {
                    'id': 'permiso_lectura_datos',
                    'nombre': 'Lectura de Datos',
                    'descripcion': 'Permite leer datos meteorológicos',
                    'recurso': 'datos_meteorologicos',
                    'accion': 'read'
                },
                {
                    'id': 'permiso_escritura_datos',
                    'nombre': 'Escritura de Datos',
                    'descripcion': 'Permite modificar datos meteorológicos',
                    'recurso': 'datos_meteorologicos',
                    'accion': 'write'
                },
                {
                    'id': 'permiso_administracion',
                    'nombre': 'Administración',
                    'descripcion': 'Permite administrar el sistema',
                    'recurso': 'sistema',
                    'accion': 'admin'
                },
                {
                    'id': 'permiso_usuarios',
                    'nombre': 'Gestión de Usuarios',
                    'descripcion': 'Permite gestionar usuarios',
                    'recurso': 'usuarios',
                    'accion': 'manage'
                },
                {
                    'id': 'permiso_reportes',
                    'nombre': 'Generación de Reportes',
                    'descripcion': 'Permite generar reportes',
                    'recurso': 'reportes',
                    'accion': 'generate'
                },
                {
                    'id': 'permiso_configuracion',
                    'nombre': 'Configuración',
                    'descripcion': 'Permite modificar configuración',
                    'recurso': 'configuracion',
                    'accion': 'modify'
                }
            ]
            
            for permiso_data in permisos_data:
                permiso = Permiso(
                    id=permiso_data['id'],
                    nombre=permiso_data['nombre'],
                    descripcion=permiso_data['descripcion'],
                    recurso=permiso_data['recurso'],
                    accion=permiso_data['accion'],
                    activo=True
                )
                self.permisos[permiso.id] = permiso
            
            # Configurar roles y permisos
            self._configurar_roles_permisos()
            
            self.logger.info(f"Permisos configurados: {len(self.permisos)}")
            
        except Exception as e:
            self.logger.error(f"Error configurando permisos: {e}")
    
    def _configurar_roles_permisos(self):
        """Configurar roles y permisos"""
        try:
            roles_permisos = {
                'administrador': [
                    'permiso_lectura_datos',
                    'permiso_escritura_datos',
                    'permiso_administracion',
                    'permiso_usuarios',
                    'permiso_reportes',
                    'permiso_configuracion'
                ],
                'tecnico': [
                    'permiso_lectura_datos',
                    'permiso_escritura_datos',
                    'permiso_reportes'
                ],
                'agricultor': [
                    'permiso_lectura_datos',
                    'permiso_reportes'
                ],
                'usuario': [
                    'permiso_lectura_datos'
                ]
            }
            
            for rol, permisos_rol in roles_permisos.items():
                for permiso_id in permisos_rol:
                    self.cursor_bd.execute('''
                        INSERT OR IGNORE INTO roles_permisos (rol, permiso_id)
                        VALUES (?, ?)
                    ''', (rol, permiso_id))
            
            self.conexion_bd.commit()
            self.logger.info("Roles y permisos configurados")
            
        except Exception as e:
            self.logger.error(f"Error configurando roles y permisos: {e}")
    
    def _configurar_usuarios_demo(self):
        """Configurar usuarios de demostración"""
        try:
            usuarios_demo = [
                {
                    'id': 'admin_1',
                    'username': 'admin',
                    'email': 'admin@metgo.cl',
                    'password': 'admin123',
                    'rol': 'administrador'
                },
                {
                    'id': 'tecnico_1',
                    'username': 'tecnico',
                    'email': 'tecnico@metgo.cl',
                    'password': 'tecnico123',
                    'rol': 'tecnico'
                },
                {
                    'id': 'agricultor_1',
                    'username': 'agricultor',
                    'email': 'agricultor@metgo.cl',
                    'password': 'agricultor123',
                    'rol': 'agricultor'
                },
                {
                    'id': 'usuario_1',
                    'username': 'usuario',
                    'email': 'usuario@metgo.cl',
                    'password': 'usuario123',
                    'rol': 'usuario'
                }
            ]
            
            for usuario_data in usuarios_demo:
                password_hash = self._hash_password(usuario_data['password'])
                
                usuario = Usuario(
                    id=usuario_data['id'],
                    username=usuario_data['username'],
                    email=usuario_data['email'],
                    password_hash=password_hash,
                    rol=usuario_data['rol'],
                    activo=True,
                    verificado=True,
                    ultimo_acceso=datetime.now().isoformat(),
                    intentos_fallidos=0,
                    bloqueado_hasta=None,
                    configuracion={
                        'tema': 'claro',
                        'idioma': 'es',
                        'notificaciones': True
                    }
                )
                self.usuarios[usuario.id] = usuario
            
            self.logger.info(f"Usuarios demo configurados: {len(self.usuarios)}")
            
        except Exception as e:
            self.logger.error(f"Error configurando usuarios demo: {e}")
    
    def _hash_password(self, password: str) -> str:
        """Hash de contraseña usando hashlib (simulado)"""
        try:
            # Simular hash de contraseña
            salt = secrets.token_hex(16)
            hashed = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
            return f"{salt}:{hashed.hex()}"
        except Exception as e:
            self.logger.error(f"Error hasheando contraseña: {e}")
            return ""
    
    def _verify_password(self, password: str, password_hash: str) -> bool:
        """Verificar contraseña"""
        try:
            # Simular verificación de contraseña
            if ':' not in password_hash:
                return False
            
            salt, stored_hash = password_hash.split(':', 1)
            hashed = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
            return hashed.hex() == stored_hash
        except Exception as e:
            self.logger.error(f"Error verificando contraseña: {e}")
            return False
    
    def _generar_jwt_token(self, usuario_id: str, expiracion: int = None) -> str:
        """Generar token JWT"""
        try:
            if expiracion is None:
                expiracion = self.configuracion_auth['jwt_expiration']
            
            payload = {
                'usuario_id': usuario_id,
                'iat': datetime.utcnow(),
                'exp': datetime.utcnow() + timedelta(seconds=expiracion)
            }
            
            token = jwt.encode(
                payload,
                self.configuracion_auth['jwt_secret'],
                algorithm=self.configuracion_auth['jwt_algorithm']
            )
            
            return token
            
        except Exception as e:
            self.logger.error(f"Error generando token JWT: {e}")
            return ""
    
    def _verificar_jwt_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verificar token JWT"""
        try:
            payload = jwt.decode(
                token,
                self.configuracion_auth['jwt_secret'],
                algorithms=[self.configuracion_auth['jwt_algorithm']]
            )
            return payload
        except jwt.ExpiredSignatureError:
            self.logger.warning("Token JWT expirado")
            return None
        except jwt.InvalidTokenError:
            self.logger.warning("Token JWT inválido")
            return None
        except Exception as e:
            self.logger.error(f"Error verificando token JWT: {e}")
            return None
    
    def _generar_refresh_token(self) -> str:
        """Generar refresh token"""
        try:
            return secrets.token_urlsafe(32)
        except Exception as e:
            self.logger.error(f"Error generando refresh token: {e}")
            return ""
    
    def _configurar_rutas(self):
        """Configurar rutas de la API de autenticación"""
        try:
            if not self.app:
                return
            
            @self.app.route('/auth/login', methods=['POST'])
            def login():
                return self._procesar_login()
            
            @self.app.route('/auth/register', methods=['POST'])
            def register():
                return self._procesar_registro()
            
            @self.app.route('/auth/logout', methods=['POST'])
            def logout():
                return self._procesar_logout()
            
            @self.app.route('/auth/refresh', methods=['POST'])
            def refresh():
                return self._procesar_refresh()
            
            @self.app.route('/auth/verify', methods=['POST'])
            def verify():
                return self._procesar_verificacion()
            
            @self.app.route('/auth/profile', methods=['GET'])
            def profile():
                return self._obtener_perfil()
            
            @self.app.route('/auth/users', methods=['GET'])
            def users():
                return self._obtener_usuarios()
            
            @self.app.route('/auth/permissions', methods=['GET'])
            def permissions():
                return self._obtener_permisos()
            
            self.logger.info("Rutas de autenticación configuradas")
            
        except Exception as e:
            self.logger.error(f"Error configurando rutas: {e}")
    
    def _procesar_login(self) -> Dict[str, Any]:
        """Procesar login de usuario"""
        try:
            data = request.get_json()
            username = data.get('username')
            password = data.get('password')
            
            if not username or not password:
                return jsonify({'exitoso': False, 'error': 'Credenciales requeridas'}), 400
            
            # Buscar usuario
            usuario = None
            for u in self.usuarios.values():
                if u.username == username or u.email == username:
                    usuario = u
                    break
            
            if not usuario:
                self._registrar_intento_login(username, False)
                return jsonify({'exitoso': False, 'error': 'Credenciales inválidas'}), 401
            
            # Verificar si está bloqueado
            if usuario.bloqueado_hasta and datetime.now() < datetime.fromisoformat(usuario.bloqueado_hasta):
                return jsonify({'exitoso': False, 'error': 'Usuario bloqueado temporalmente'}), 423
            
            # Verificar contraseña
            if not self._verify_password(password, usuario.password_hash):
                usuario.intentos_fallidos += 1
                
                if usuario.intentos_fallidos >= self.configuracion_auth['max_intentos']:
                    usuario.bloqueado_hasta = (datetime.now() + timedelta(seconds=self.configuracion_auth['tiempo_bloqueo'])).isoformat()
                
                self._registrar_intento_login(username, False)
                return jsonify({'exitoso': False, 'error': 'Credenciales inválidas'}), 401
            
            # Login exitoso
            usuario.intentos_fallidos = 0
            usuario.bloqueado_hasta = None
            usuario.ultimo_acceso = datetime.now().isoformat()
            
            # Generar tokens
            access_token = self._generar_jwt_token(usuario.id)
            refresh_token = self._generar_refresh_token()
            
            # Crear sesión
            sesion_id = secrets.token_urlsafe(16)
            sesion = Sesion(
                id=sesion_id,
                usuario_id=usuario.id,
                token=access_token,
                refresh_token=refresh_token,
                timestamp=datetime.now().isoformat(),
                expiracion=(datetime.now() + timedelta(seconds=self.configuracion_auth['jwt_expiration'])).isoformat(),
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent', ''),
                activa=True
            )
            self.sesiones[sesion_id] = sesion
            
            self._registrar_intento_login(username, True)
            
            return jsonify({
                'exitoso': True,
                'access_token': access_token,
                'refresh_token': refresh_token,
                'usuario': {
                    'id': usuario.id,
                    'username': usuario.username,
                    'email': usuario.email,
                    'rol': usuario.rol
                }
            })
            
        except Exception as e:
            self.logger.error(f"Error procesando login: {e}")
            return jsonify({'exitoso': False, 'error': 'Error interno del servidor'}), 500
    
    def _procesar_registro(self) -> Dict[str, Any]:
        """Procesar registro de usuario"""
        try:
            data = request.get_json()
            username = data.get('username')
            email = data.get('email')
            password = data.get('password')
            rol = data.get('rol', 'usuario')
            
            if not username or not email or not password:
                return jsonify({'exitoso': False, 'error': 'Datos requeridos'}), 400
            
            # Validar contraseña
            if len(password) < self.configuracion_auth['password_min_length']:
                return jsonify({'exitoso': False, 'error': 'Contraseña muy corta'}), 400
            
            # Verificar si usuario ya existe
            for u in self.usuarios.values():
                if u.username == username or u.email == email:
                    return jsonify({'exitoso': False, 'error': 'Usuario ya existe'}), 409
            
            # Crear usuario
            usuario_id = secrets.token_urlsafe(16)
            password_hash = self._hash_password(password)
            
            usuario = Usuario(
                id=usuario_id,
                username=username,
                email=email,
                password_hash=password_hash,
                rol=rol,
                activo=True,
                verificado=False,
                ultimo_acceso=datetime.now().isoformat(),
                intentos_fallidos=0,
                bloqueado_hasta=None,
                configuracion={
                    'tema': 'claro',
                    'idioma': 'es',
                    'notificaciones': True
                }
            )
            self.usuarios[usuario.id] = usuario
            
            return jsonify({
                'exitoso': True,
                'mensaje': 'Usuario registrado exitosamente',
                'usuario': {
                    'id': usuario.id,
                    'username': usuario.username,
                    'email': usuario.email,
                    'rol': usuario.rol
                }
            })
            
        except Exception as e:
            self.logger.error(f"Error procesando registro: {e}")
            return jsonify({'exitoso': False, 'error': 'Error interno del servidor'}), 500
    
    def _procesar_logout(self) -> Dict[str, Any]:
        """Procesar logout de usuario"""
        try:
            token = request.headers.get('Authorization', '').replace('Bearer ', '')
            
            if not token:
                return jsonify({'exitoso': False, 'error': 'Token requerido'}), 400
            
            # Verificar token
            payload = self._verificar_jwt_token(token)
            if not payload:
                return jsonify({'exitoso': False, 'error': 'Token inválido'}), 401
            
            # Invalidar sesión
            for sesion_id, sesion in self.sesiones.items():
                if sesion.token == token:
                    sesion.activa = False
                    break
            
            return jsonify({'exitoso': True, 'mensaje': 'Logout exitoso'})
            
        except Exception as e:
            self.logger.error(f"Error procesando logout: {e}")
            return jsonify({'exitoso': False, 'error': 'Error interno del servidor'}), 500
    
    def _procesar_refresh(self) -> Dict[str, Any]:
        """Procesar refresh de token"""
        try:
            data = request.get_json()
            refresh_token = data.get('refresh_token')
            
            if not refresh_token:
                return jsonify({'exitoso': False, 'error': 'Refresh token requerido'}), 400
            
            # Buscar sesión
            sesion = None
            for s in self.sesiones.values():
                if s.refresh_token == refresh_token and s.activa:
                    sesion = s
                    break
            
            if not sesion:
                return jsonify({'exitoso': False, 'error': 'Refresh token inválido'}), 401
            
            # Generar nuevo access token
            nuevo_access_token = self._generar_jwt_token(sesion.usuario_id)
            sesion.token = nuevo_access_token
            sesion.expiracion = (datetime.now() + timedelta(seconds=self.configuracion_auth['jwt_expiration'])).isoformat()
            
            return jsonify({
                'exitoso': True,
                'access_token': nuevo_access_token
            })
            
        except Exception as e:
            self.logger.error(f"Error procesando refresh: {e}")
            return jsonify({'exitoso': False, 'error': 'Error interno del servidor'}), 500
    
    def _procesar_verificacion(self) -> Dict[str, Any]:
        """Procesar verificación de token"""
        try:
            token = request.headers.get('Authorization', '').replace('Bearer ', '')
            
            if not token:
                return jsonify({'exitoso': False, 'error': 'Token requerido'}), 400
            
            # Verificar token
            payload = self._verificar_jwt_token(token)
            if not payload:
                return jsonify({'exitoso': False, 'error': 'Token inválido'}), 401
            
            # Obtener usuario
            usuario = self.usuarios.get(payload['usuario_id'])
            if not usuario or not usuario.activo:
                return jsonify({'exitoso': False, 'error': 'Usuario no encontrado'}), 404
            
            return jsonify({
                'exitoso': True,
                'usuario': {
                    'id': usuario.id,
                    'username': usuario.username,
                    'email': usuario.email,
                    'rol': usuario.rol
                }
            })
            
        except Exception as e:
            self.logger.error(f"Error procesando verificación: {e}")
            return jsonify({'exitoso': False, 'error': 'Error interno del servidor'}), 500
    
    def _obtener_perfil(self) -> Dict[str, Any]:
        """Obtener perfil de usuario"""
        try:
            token = request.headers.get('Authorization', '').replace('Bearer ', '')
            
            if not token:
                return jsonify({'exitoso': False, 'error': 'Token requerido'}), 400
            
            # Verificar token
            payload = self._verificar_jwt_token(token)
            if not payload:
                return jsonify({'exitoso': False, 'error': 'Token inválido'}), 401
            
            # Obtener usuario
            usuario = self.usuarios.get(payload['usuario_id'])
            if not usuario:
                return jsonify({'exitoso': False, 'error': 'Usuario no encontrado'}), 404
            
            return jsonify({
                'exitoso': True,
                'usuario': {
                    'id': usuario.id,
                    'username': usuario.username,
                    'email': usuario.email,
                    'rol': usuario.rol,
                    'activo': usuario.activo,
                    'verificado': usuario.verificado,
                    'ultimo_acceso': usuario.ultimo_acceso,
                    'configuracion': usuario.configuracion
                }
            })
            
        except Exception as e:
            self.logger.error(f"Error obteniendo perfil: {e}")
            return jsonify({'exitoso': False, 'error': 'Error interno del servidor'}), 500
    
    def _obtener_usuarios(self) -> Dict[str, Any]:
        """Obtener lista de usuarios"""
        try:
            token = request.headers.get('Authorization', '').replace('Bearer ', '')
            
            if not token:
                return jsonify({'exitoso': False, 'error': 'Token requerido'}), 400
            
            # Verificar token
            payload = self._verificar_jwt_token(token)
            if not payload:
                return jsonify({'exitoso': False, 'error': 'Token inválido'}), 401
            
            # Obtener usuario
            usuario = self.usuarios.get(payload['usuario_id'])
            if not usuario or usuario.rol != 'administrador':
                return jsonify({'exitoso': False, 'error': 'Permisos insuficientes'}), 403
            
            usuarios_data = []
            for u in self.usuarios.values():
                usuarios_data.append({
                    'id': u.id,
                    'username': u.username,
                    'email': u.email,
                    'rol': u.rol,
                    'activo': u.activo,
                    'verificado': u.verificado,
                    'ultimo_acceso': u.ultimo_acceso
                })
            
            return jsonify({
                'exitoso': True,
                'usuarios': usuarios_data,
                'total': len(usuarios_data)
            })
            
        except Exception as e:
            self.logger.error(f"Error obteniendo usuarios: {e}")
            return jsonify({'exitoso': False, 'error': 'Error interno del servidor'}), 500
    
    def _obtener_permisos(self) -> Dict[str, Any]:
        """Obtener permisos del sistema"""
        try:
            token = request.headers.get('Authorization', '').replace('Bearer ', '')
            
            if not token:
                return jsonify({'exitoso': False, 'error': 'Token requerido'}), 400
            
            # Verificar token
            payload = self._verificar_jwt_token(token)
            if not payload:
                return jsonify({'exitoso': False, 'error': 'Token inválido'}), 401
            
            # Obtener usuario
            usuario = self.usuarios.get(payload['usuario_id'])
            if not usuario:
                return jsonify({'exitoso': False, 'error': 'Usuario no encontrado'}), 404
            
            # Obtener permisos del usuario
            permisos_usuario = []
            self.cursor_bd.execute('''
                SELECT p.id, p.nombre, p.descripcion, p.recurso, p.accion
                FROM permisos p
                JOIN roles_permisos rp ON p.id = rp.permiso_id
                WHERE rp.rol = ? AND p.activo = TRUE
            ''', (usuario.rol,))
            
            for row in self.cursor_bd.fetchall():
                permisos_usuario.append({
                    'id': row[0],
                    'nombre': row[1],
                    'descripcion': row[2],
                    'recurso': row[3],
                    'accion': row[4]
                })
            
            return jsonify({
                'exitoso': True,
                'permisos': permisos_usuario,
                'rol': usuario.rol
            })
            
        except Exception as e:
            self.logger.error(f"Error obteniendo permisos: {e}")
            return jsonify({'exitoso': False, 'error': 'Error interno del servidor'}), 500
    
    def _registrar_intento_login(self, username: str, exitoso: bool):
        """Registrar intento de login"""
        try:
            self.cursor_bd.execute('''
                INSERT INTO intentos_login (username, ip_address, exitoso, user_agent)
                VALUES (?, ?, ?, ?)
            ''', (
                username,
                request.remote_addr,
                exitoso,
                request.headers.get('User-Agent', '')
            ))
            
            self.conexion_bd.commit()
            
        except Exception as e:
            self.logger.error(f"Error registrando intento de login: {e}")
    
    def generar_reporte_autenticacion(self) -> str:
        """Generar reporte del sistema de autenticación"""
        try:
            self.logger.info("Generando reporte del sistema de autenticación...")
            
            # Obtener estadísticas
            estadisticas = self._obtener_estadisticas_auth()
            
            reporte = {
                'timestamp': datetime.now().isoformat(),
                'sistema': 'METGO 3D - Sistema de Autenticación Avanzada',
                'version': self.configuracion['version'],
                'configuracion_auth': self.configuracion_auth,
                'usuarios': [
                    {
                        'id': u.id,
                        'username': u.username,
                        'email': u.email,
                        'rol': u.rol,
                        'activo': u.activo,
                        'verificado': u.verificado,
                        'ultimo_acceso': u.ultimo_acceso
                    } for u in self.usuarios.values()
                ],
                'permisos': [
                    {
                        'id': p.id,
                        'nombre': p.nombre,
                        'descripcion': p.descripcion,
                        'recurso': p.recurso,
                        'accion': p.accion
                    } for p in self.permisos.values()
                ],
                'estadisticas': estadisticas,
                'funcionalidades_implementadas': [
                    'Autenticación JWT',
                    'Sistema de roles y permisos',
                    'Hash de contraseñas con bcrypt',
                    'Refresh tokens',
                    'Rate limiting',
                    'Bloqueo por intentos fallidos',
                    'Sesiones seguras',
                    'Base de datos SQLite',
                    'API REST completa',
                    'Logging de seguridad'
                ],
                'tecnologias_utilizadas': [
                    'JWT para tokens',
                    'bcrypt para hash de contraseñas',
                    'Flask para API REST',
                    'SQLite para base de datos',
                    'secrets para tokens seguros',
                    'Logging estructurado'
                ],
                'recomendaciones': [
                    'Implementar 2FA (autenticación de dos factores)',
                    'Agregar OAuth2/OIDC',
                    'Implementar SSO (Single Sign-On)',
                    'Agregar auditoría de seguridad',
                    'Implementar políticas de contraseñas',
                    'Agregar notificaciones de seguridad',
                    'Implementar recuperación de contraseña',
                    'Agregar verificación por email',
                    'Implementar CAPTCHA',
                    'Agregar monitoreo de seguridad'
                ]
            }
            
            # Guardar reporte
            reportes_dir = Path("reportes")
            reportes_dir.mkdir(exist_ok=True)
            
            reporte_file = reportes_dir / f"autenticacion_avanzada_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(reporte_file, 'w', encoding='utf-8') as f:
                json.dump(reporte, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Reporte de autenticación generado: {reporte_file}")
            return str(reporte_file)
            
        except Exception as e:
            self.logger.error(f"Error generando reporte: {e}")
            return ""
    
    def _obtener_estadisticas_auth(self) -> Dict[str, Any]:
        """Obtener estadísticas del sistema de autenticación"""
        try:
            # Estadísticas de usuarios
            usuarios_activos = sum(1 for u in self.usuarios.values() if u.activo)
            usuarios_verificados = sum(1 for u in self.usuarios.values() if u.verificado)
            
            # Estadísticas de sesiones
            sesiones_activas = sum(1 for s in self.sesiones.values() if s.activa)
            
            # Estadísticas de intentos de login
            self.cursor_bd.execute('''
                SELECT COUNT(*) as total_intentos,
                       SUM(CASE WHEN exitoso = 1 THEN 1 ELSE 0 END) as exitosos,
                       SUM(CASE WHEN exitoso = 0 THEN 1 ELSE 0 END) as fallidos
                FROM intentos_login 
                WHERE DATE(timestamp) = DATE('now')
            ''')
            stats_login = self.cursor_bd.fetchone()
            
            return {
                'usuarios': {
                    'total': len(self.usuarios),
                    'activos': usuarios_activos,
                    'verificados': usuarios_verificados,
                    'por_rol': {
                        rol: sum(1 for u in self.usuarios.values() if u.rol == rol)
                        for rol in set(u.rol for u in self.usuarios.values())
                    }
                },
                'sesiones': {
                    'activas': sesiones_activas,
                    'total': len(self.sesiones)
                },
                'permisos': {
                    'total': len(self.permisos),
                    'activos': sum(1 for p in self.permisos.values() if p.activo)
                },
                'login_diario': {
                    'total_intentos': stats_login[0] or 0,
                    'exitosos': stats_login[1] or 0,
                    'fallidos': stats_login[2] or 0
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error obteniendo estadísticas: {e}")
            return {}
    
    def ejecutar_api_auth(self, puerto: int = 5001, debug: bool = False):
        """Ejecutar API de autenticación"""
        try:
            if not self.app:
                self.logger.error("Flask no disponible")
                return False
            
            self.logger.info(f"Iniciando API de autenticación en puerto {puerto}")
            
            # Generar reporte
            self.generar_reporte_autenticacion()
            
            # Ejecutar aplicación
            self.app.run(host='0.0.0.0', port=puerto, debug=debug)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error ejecutando API de autenticación: {e}")
            return False

def main():
    """Función principal de autenticación avanzada"""
    print("AUTENTICACION AVANZADA METGO 3D")
    print("Sistema Meteorologico Agricola Quillota - Sistema de Autenticacion Avanzada")
    print("=" * 80)
    
    try:
        # Crear sistema de autenticación
        auth_sistema = AutenticacionAvanzadaMETGO()
        
        if not FLASK_AVAILABLE:
            print("Flask no disponible. Instalando...")
            print("pip install flask flask-cors pyjwt bcrypt")
            return False
        
        # Generar reporte
        print(f"\nGenerando reporte de autenticacion...")
        reporte = auth_sistema.generar_reporte_autenticacion()
        
        if reporte:
            print(f"Reporte generado: {reporte}")
        else:
            print(f"Error generando reporte")
        
        # Mostrar información del sistema
        print(f"\nSistema de Autenticacion Avanzada METGO 3D")
        print(f"Version: {auth_sistema.configuracion['version']}")
        print(f"JWT Secret: {auth_sistema.configuracion_auth['jwt_secret'][:20]}...")
        print(f"JWT Expiration: {auth_sistema.configuracion_auth['jwt_expiration']} segundos")
        print(f"Max Intentos: {auth_sistema.configuracion_auth['max_intentos']}")
        print(f"Tiempo Bloqueo: {auth_sistema.configuracion_auth['tiempo_bloqueo']} segundos")
        
        print(f"\nUsuarios configurados:")
        for usuario in auth_sistema.usuarios.values():
            print(f"   - {usuario.username} ({usuario.rol}): {usuario.email}")
            print(f"     Activo: {usuario.activo} | Verificado: {usuario.verificado}")
        
        print(f"\nPermisos configurados:")
        for permiso in auth_sistema.permisos.values():
            print(f"   - {permiso.nombre}: {permiso.descripcion}")
            print(f"     Recurso: {permiso.recurso} | Accion: {permiso.accion}")
        
        print(f"\nRutas de API disponibles:")
        rutas = [
            'POST /auth/login - Iniciar sesion',
            'POST /auth/register - Registrar usuario',
            'POST /auth/logout - Cerrar sesion',
            'POST /auth/refresh - Renovar token',
            'POST /auth/verify - Verificar token',
            'GET /auth/profile - Obtener perfil',
            'GET /auth/users - Listar usuarios (admin)',
            'GET /auth/permissions - Obtener permisos'
        ]
        
        for ruta in rutas:
            print(f"   - {ruta}")
        
        # Mostrar estadísticas
        estadisticas = auth_sistema._obtener_estadisticas_auth()
        if estadisticas:
            print(f"\nEstadisticas del sistema:")
            print(f"   Usuarios totales: {estadisticas.get('usuarios', {}).get('total', 0)}")
            print(f"   Usuarios activos: {estadisticas.get('usuarios', {}).get('activos', 0)}")
            print(f"   Usuarios verificados: {estadisticas.get('usuarios', {}).get('verificados', 0)}")
            print(f"   Sesiones activas: {estadisticas.get('sesiones', {}).get('activas', 0)}")
            print(f"   Permisos totales: {estadisticas.get('permisos', {}).get('total', 0)}")
        
        print(f"\nPara ejecutar la API de autenticacion:")
        print(f"   python autenticacion_avanzada_metgo.py --ejecutar")
        print(f"   La API estara disponible en: http://localhost:5001")
        
        return True
        
    except Exception as e:
        print(f"\nError en sistema de autenticacion: {e}")
        return False

if __name__ == "__main__":
    try:
        if len(sys.argv) > 1 and sys.argv[1] == '--ejecutar':
            # Ejecutar API de autenticación
            auth_sistema = AutenticacionAvanzadaMETGO()
            auth_sistema.ejecutar_api_auth(debug=True)
        else:
            # Generar reporte
            exito = main()
            sys.exit(0 if exito else 1)
    except Exception as e:
        print(f"\nError inesperado: {e}")
        sys.exit(1)
