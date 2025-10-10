#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Modulo de Autenticacion - METGO 3D
"""

import json
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
import logging

class SistemaAutenticacion:
    """Sistema de autenticacion para METGO 3D"""
    
    def __init__(self):
        self.archivo_usuarios = Path("config/usuarios.json")
        self.archivo_sesiones = Path("config/sesiones.json")
        self.usuarios = self._cargar_usuarios()
        self.sesiones = {}
        self.logger = logging.getLogger('AUTENTICACION')
    
    def _cargar_usuarios(self):
        """Cargar usuarios desde archivo"""
        if self.archivo_usuarios.exists():
            with open(self.archivo_usuarios, 'r') as f:
                return json.load(f)
        return self._crear_usuarios_default()
    
    def _crear_usuarios_default(self):
        """Crear usuarios por defecto"""
        usuarios = {
            'admin': {
                'password': self._hash_password('admin123'),
                'rol': 'administrador',
                'permisos': ['ejecutar', 'ver', 'editar', 'eliminar'],
                'activo': True
            },
            'usuario': {
                'password': self._hash_password('usuario123'),
                'rol': 'usuario',
                'permisos': ['ejecutar', 'ver'],
                'activo': True
            }
        }
        
        self.archivo_usuarios.parent.mkdir(parents=True, exist_ok=True)
        with open(self.archivo_usuarios, 'w') as f:
            json.dump(usuarios, f, indent=2)
        
        return usuarios
    
    def _hash_password(self, password):
        """Hash de password con SHA256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def autenticar(self, usuario, password):
        """Autenticar usuario"""
        if usuario not in self.usuarios:
            return False, "Usuario no existe"
        
        if not self.usuarios[usuario]['activo']:
            return False, "Usuario inactivo"
        
        password_hash = self._hash_password(password)
        if password_hash != self.usuarios[usuario]['password']:
            return False, "Password incorrecta"
        
        # Crear sesion
        token = self._generar_token(usuario)
        self.sesiones[token] = {
            'usuario': usuario,
            'rol': self.usuarios[usuario]['rol'],
            'permisos': self.usuarios[usuario]['permisos'],
            'inicio': datetime.now().isoformat(),
            'expira': (datetime.now() + timedelta(hours=24)).isoformat()
        }
        
        self.logger.info(f"Usuario autenticado: {usuario}")
        return True, token
    
    def _generar_token(self, usuario):
        """Generar token de sesion"""
        timestamp = datetime.now().isoformat()
        data = f"{usuario}{timestamp}"
        return hashlib.sha256(data.encode()).hexdigest()
    
    def verificar_sesion(self, token):
        """Verificar si la sesion es valida"""
        if token not in self.sesiones:
            return False, "Token invalido"
        
        sesion = self.sesiones[token]
        expira = datetime.fromisoformat(sesion['expira'])
        
        if datetime.now() > expira:
            del self.sesiones[token]
            return False, "Sesion expirada"
        
        return True, sesion
    
    def cerrar_sesion(self, token):
        """Cerrar sesion"""
        if token in self.sesiones:
            del self.sesiones[token]
            return True
        return False
    
    def tiene_permiso(self, token, permiso):
        """Verificar si el usuario tiene un permiso"""
        valida, sesion_o_error = self.verificar_sesion(token)
        if not valida:
            return False
        
        sesion = sesion_o_error
        return permiso in sesion['permisos']



