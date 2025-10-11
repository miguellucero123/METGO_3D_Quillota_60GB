#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🌾 GESTIÓN DE USUARIOS DEL SISTEMA METGO 3D
Sistema Meteorológico Agrícola Quillota - Versión Operativa 2.0
"""

import os
import sys
import time
import json
import hashlib
import secrets
from pathlib import Path
from datetime import datetime

def print_header():
    """Imprimir encabezado"""
    print("🌾 GESTIÓN DE USUARIOS DEL SISTEMA METGO 3D")
    print("Sistema Meteorológico Agrícola Quillota - Versión Operativa 2.0")
    print("=" * 70)

def print_step(step, message):
    """Imprimir paso del proceso"""
    print(f"\n[{step}] {message}")
    print("-" * 50)

def print_success(message):
    """Imprimir mensaje de éxito"""
    print(f"✅ {message}")

def print_error(message):
    """Imprimir mensaje de error")
    print(f"❌ {message}")

def print_warning(message):
    """Imprimir mensaje de advertencia"""
    print(f"⚠️ {message}")

def print_info(message):
    """Imprimir mensaje informativo")
    print(f"ℹ️ {message}")

class GestorUsuarios:
    """Clase para gestión de usuarios del sistema"""
    
    def __init__(self):
        self.configuracion = {
            'directorio_usuarios': 'usuarios',
            'archivo_usuarios': 'usuarios/usuarios.json',
            'archivo_config': 'config/usuarios.yaml',
            'hash_algorithm': 'SHA-256',
            'salt_length': 32,
            'session_timeout': 3600  # segundos
        }
        
        self.roles = [
            'admin',
            'operador',
            'consultor',
            'auditor'
        ]
        
        self.permisos = {
            'admin': ['crear', 'leer', 'actualizar', 'eliminar', 'configurar', 'auditar'],
            'operador': ['crear', 'leer', 'actualizar'],
            'consultor': ['leer'],
            'auditor': ['leer', 'auditar']
        }
    
    def cargar_configuracion(self):
        """Cargar configuración de usuarios"""
        try:
            print_info("Cargando configuración de usuarios...")
            
            config_file = Path(self.configuracion['archivo_config'])
            if config_file.exists():
                print_success("Configuración cargada")
            else:
                print_warning("Archivo de configuración no encontrado")
            
            return True
            
        except Exception as e:
            print_error(f"Error cargando configuración: {e}")
            return False
    
    def crear_estructura_usuarios(self):
        """Crear estructura de usuarios"""
        try:
            print_info("Creando estructura de usuarios...")
            
            # Crear directorio principal
            usuarios_dir = Path(self.configuracion['directorio_usuarios'])
            usuarios_dir.mkdir(exist_ok=True)
            
            # Crear archivos de configuración
            self.crear_archivos_config()
            
            # Crear archivo de usuarios si no existe
            archivo_usuarios = Path(self.configuracion['archivo_usuarios'])
            if not archivo_usuarios.exists():
                self.crear_usuario_admin()
            
            print_success("Estructura de usuarios creada")
            return True
            
        except Exception as e:
            print_error(f"Error creando estructura: {e}")
            return False
    
    def crear_archivos_config(self):
        """Crear archivos de configuración"""
        try:
            # config/usuarios.yaml
            config_content = '''# Configuración de usuarios del sistema METGO 3D

usuarios:
  hash_algorithm: SHA-256
  salt_length: 32
  session_timeout: 3600  # segundos
  
  roles:
    admin:
      descripcion: "Administrador del sistema"
      permisos: ["crear", "leer", "actualizar", "eliminar", "configurar", "auditar"]
    operador:
      descripcion: "Operador del sistema"
      permisos: ["crear", "leer", "actualizar"]
    consultor:
      descripcion: "Consultor del sistema"
      permisos: ["leer"]
    auditor:
      descripcion: "Auditor del sistema"
      permisos: ["leer", "auditar"]
  
  politicas:
    longitud_minima_password: 8
    complejidad_password: true
    intentos_maximos: 3
    bloqueo_temporal: 300  # segundos
'''
            
            config_file = Path('config/usuarios.yaml')
            config_file.parent.mkdir(exist_ok=True)
            config_file.write_text(config_content)
            
            print_success("Archivos de configuración creados")
            return True
            
        except Exception as e:
            print_error(f"Error creando archivos de configuración: {e}")
            return False
    
    def crear_usuario_admin(self):
        """Crear usuario administrador por defecto"""
        try:
            print_info("Creando usuario administrador por defecto...")
            
            # Crear usuario admin
            usuario_admin = {
                'id': 'admin',
                'nombre': 'Administrador',
                'email': 'admin@metgo.local',
                'rol': 'admin',
                'activo': True,
                'creado': datetime.now().isoformat(),
                'ultimo_acceso': None,
                'intentos_fallidos': 0,
                'bloqueado_hasta': None
            }
            
            # Generar salt y hash para password por defecto
            password_default = 'admin123'
            salt = secrets.token_hex(self.configuracion['salt_length'])
            password_hash = hashlib.sha256((password_default + salt).encode()).hexdigest()
            
            usuario_admin['salt'] = salt
            usuario_admin['password_hash'] = password_hash
            
            # Guardar usuario
            usuarios = [usuario_admin]
            archivo_usuarios = Path(self.configuracion['archivo_usuarios'])
            archivo_usuarios.parent.mkdir(exist_ok=True)
            
            with open(archivo_usuarios, 'w', encoding='utf-8') as f:
                json.dump(usuarios, f, indent=2, ensure_ascii=False)
            
            print_success("Usuario administrador creado")
            print_warning("Password por defecto: admin123")
            print_warning("¡Cambia la password inmediatamente!")
            
            return True
            
        except Exception as e:
            print_error(f"Error creando usuario administrador: {e}")
            return False
    
    def crear_usuario(self, id_usuario, nombre, email, rol, password):
        """Crear nuevo usuario"""
        try:
            print_info(f"Creando usuario: {id_usuario}")
            
            # Verificar que el rol sea válido
            if rol not in self.roles:
                print_error(f"Rol no válido: {rol}")
                return False
            
            # Verificar que el usuario no exista
            usuarios = self.cargar_usuarios()
            if any(u['id'] == id_usuario for u in usuarios):
                print_error(f"Usuario {id_usuario} ya existe")
                return False
            
            # Generar salt y hash para password
            salt = secrets.token_hex(self.configuracion['salt_length'])
            password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
            
            # Crear usuario
            nuevo_usuario = {
                'id': id_usuario,
                'nombre': nombre,
                'email': email,
                'rol': rol,
                'activo': True,
                'creado': datetime.now().isoformat(),
                'ultimo_acceso': None,
                'intentos_fallidos': 0,
                'bloqueado_hasta': None,
                'salt': salt,
                'password_hash': password_hash
            }
            
            # Agregar usuario
            usuarios.append(nuevo_usuario)
            
            # Guardar usuarios
            archivo_usuarios = Path(self.configuracion['archivo_usuarios'])
            with open(archivo_usuarios, 'w', encoding='utf-8') as f:
                json.dump(usuarios, f, indent=2, ensure_ascii=False)
            
            print_success(f"Usuario {id_usuario} creado correctamente")
            return True
            
        except Exception as e:
            print_error(f"Error creando usuario: {e}")
            return False
    
    def cargar_usuarios(self):
        """Cargar lista de usuarios"""
        try:
            archivo_usuarios = Path(self.configuracion['archivo_usuarios'])
            if not archivo_usuarios.exists():
                return []
            
            with open(archivo_usuarios, 'r', encoding='utf-8') as f:
                usuarios = json.load(f)
            
            return usuarios
            
        except Exception as e:
            print_error(f"Error cargando usuarios: {e}")
            return []
    
    def autenticar_usuario(self, id_usuario, password):
        """Autenticar usuario"""
        try:
            print_info(f"Autenticando usuario: {id_usuario}")
            
            usuarios = self.cargar_usuarios()
            usuario = next((u for u in usuarios if u['id'] == id_usuario), None)
            
            if not usuario:
                print_error("Usuario no encontrado")
                return False
            
            if not usuario['activo']:
                print_error("Usuario inactivo")
                return False
            
            # Verificar si está bloqueado
            if usuario['bloqueado_hasta']:
                bloqueado_hasta = datetime.fromisoformat(usuario['bloqueado_hasta'])
                if datetime.now() < bloqueado_hasta:
                    print_error("Usuario bloqueado temporalmente")
                    return False
            
            # Verificar password
            salt = usuario['salt']
            password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
            
            if password_hash != usuario['password_hash']:
                # Incrementar intentos fallidos
                usuario['intentos_fallidos'] += 1
                
                # Bloquear si excede intentos máximos
                if usuario['intentos_fallidos'] >= 3:
                    usuario['bloqueado_hasta'] = (datetime.now() + 
                                                timedelta(seconds=300)).isoformat()
                    print_error("Usuario bloqueado por intentos fallidos")
                
                # Guardar cambios
                archivo_usuarios = Path(self.configuracion['archivo_usuarios'])
                with open(archivo_usuarios, 'w', encoding='utf-8') as f:
                    json.dump(usuarios, f, indent=2, ensure_ascii=False)
                
                print_error("Password incorrecta")
                return False
            
            # Resetear intentos fallidos y actualizar último acceso
            usuario['intentos_fallidos'] = 0
            usuario['bloqueado_hasta'] = None
            usuario['ultimo_acceso'] = datetime.now().isoformat()
            
            # Guardar cambios
            archivo_usuarios = Path(self.configuracion['archivo_usuarios'])
            with open(archivo_usuarios, 'w', encoding='utf-8') as f:
                json.dump(usuarios, f, indent=2, ensure_ascii=False)
            
            print_success(f"Usuario {id_usuario} autenticado correctamente")
            return True
            
        except Exception as e:
            print_error(f"Error autenticando usuario: {e}")
            return False
    
    def listar_usuarios(self):
        """Listar usuarios del sistema"""
        try:
            print_info("Listando usuarios del sistema...")
            
            usuarios = self.cargar_usuarios()
            
            if not usuarios:
                print_warning("No hay usuarios registrados")
                return []
            
            print(f"\n📋 Usuarios registrados ({len(usuarios)}):")
            print("-" * 80)
            print(f"{'ID':<15} {'Nombre':<20} {'Email':<25} {'Rol':<10} {'Estado':<8}")
            print("-" * 80)
            
            for usuario in usuarios:
                estado = "Activo" if usuario['activo'] else "Inactivo"
                print(f"{usuario['id']:<15} {usuario['nombre']:<20} {usuario['email']:<25} {usuario['rol']:<10} {estado:<8}")
            
            return usuarios
            
        except Exception as e:
            print_error(f"Error listando usuarios: {e}")
            return []
    
    def generar_reporte_usuarios(self):
        """Generar reporte de usuarios"""
        try:
            print_info("Generando reporte de usuarios...")
            
            usuarios = self.cargar_usuarios()
            
            # Crear reporte
            reporte = {
                'timestamp': datetime.now().isoformat(),
                'sistema': 'METGO 3D - Sistema Meteorológico Agrícola Quillota',
                'version': '2.0',
                'usuarios': {
                    'total': len(usuarios),
                    'activos': len([u for u in usuarios if u['activo']]),
                    'inactivos': len([u for u in usuarios if not u['activo']]),
                    'por_rol': {}
                },
                'detalles': usuarios
            }
            
            # Contar por rol
            for rol in self.roles:
                count = len([u for u in usuarios if u['rol'] == rol])
                reporte['usuarios']['por_rol'][rol] = count
            
            # Guardar reporte
            reportes_dir = Path("reportes")
            reportes_dir.mkdir(exist_ok=True)
            
            reporte_file = reportes_dir / f"usuarios_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(reporte_file, 'w', encoding='utf-8') as f:
                json.dump(reporte, f, indent=2, ensure_ascii=False)
            
            print_success(f"Reporte de usuarios generado: {reporte_file}")
            
            # Mostrar resumen
            print(f"\n📊 Resumen de usuarios:")
            print(f"Total: {reporte['usuarios']['total']}")
            print(f"Activos: {reporte['usuarios']['activos']}")
            print(f"Inactivos: {reporte['usuarios']['inactivos']}")
            
            return str(reporte_file)
            
        except Exception as e:
            print_error(f"Error generando reporte: {e}")
            return None

def mostrar_menu():
    """Mostrar menú de gestión de usuarios"""
    print("\n" + "=" * 70)
    print("📋 MENÚ DE GESTIÓN DE USUARIOS - METGO 3D")
    print("=" * 70)
    
    print("\n1. 🔍 Cargar configuración")
    print("2. 📁 Crear estructura de usuarios")
    print("3. 👤 Crear usuario")
    print("4. 🔐 Autenticar usuario")
    print("5. 📋 Listar usuarios")
    print("6. 📊 Generar reporte")
    print("7. ❌ Salir")
    
    print("\n" + "=" * 70)

def main():
    """Función principal de gestión de usuarios"""
    print_header()
    
    # Crear gestor de usuarios
    gestor = GestorUsuarios()
    
    while True:
        mostrar_menu()
        
        try:
            opcion = input("\n🔢 Selecciona una opción (1-7): ").strip()
            
            if opcion == "1":
                print_step("1", "Cargando configuración")
                if gestor.cargar_configuracion():
                    print_success("Configuración cargada correctamente")
                else:
                    print_error("Error cargando configuración")
                input("\n⏸️ Presiona Enter para continuar...")
            
            elif opcion == "2":
                print_step("2", "Creando estructura de usuarios")
                if gestor.crear_estructura_usuarios():
                    print_success("Estructura de usuarios creada correctamente")
                else:
                    print_error("Error creando estructura")
                input("\n⏸️ Presiona Enter para continuar...")
            
            elif opcion == "3":
                print_step("3", "Creando usuario")
                try:
                    id_usuario = input("ID del usuario: ").strip()
                    nombre = input("Nombre completo: ").strip()
                    email = input("Email: ").strip()
                    rol = input(f"Rol ({', '.join(gestor.roles)}): ").strip()
                    password = input("Password: ").strip()
                    
                    if gestor.crear_usuario(id_usuario, nombre, email, rol, password):
                        print_success("Usuario creado correctamente")
                    else:
                        print_error("Error creando usuario")
                except Exception as e:
                    print_error(f"Error: {e}")
                input("\n⏸️ Presiona Enter para continuar...")
            
            elif opcion == "4":
                print_step("4", "Autenticando usuario")
                try:
                    id_usuario = input("ID del usuario: ").strip()
                    password = input("Password: ").strip()
                    
                    if gestor.autenticar_usuario(id_usuario, password):
                        print_success("Usuario autenticado correctamente")
                    else:
                        print_error("Error autenticando usuario")
                except Exception as e:
                    print_error(f"Error: {e}")
                input("\n⏸️ Presiona Enter para continuar...")
            
            elif opcion == "5":
                print_step("5", "Listando usuarios")
                usuarios = gestor.listar_usuarios()
                if usuarios:
                    print_success(f"Usuarios listados: {len(usuarios)}")
                else:
                    print_error("Error listando usuarios")
                input("\n⏸️ Presiona Enter para continuar...")
            
            elif opcion == "6":
                print_step("6", "Generando reporte de usuarios")
                reporte = gestor.generar_reporte_usuarios()
                if reporte:
                    print_success(f"Reporte generado: {reporte}")
                else:
                    print_error("Error generando reporte")
                input("\n⏸️ Presiona Enter para continuar...")
            
            elif opcion == "7":
                print_info("Saliendo del gestor de usuarios...")
                print_success("¡Hasta luego! 🌾")
                break
            
            else:
                print_warning("Opción no válida. Selecciona 1-7.")
                time.sleep(1)
        
        except KeyboardInterrupt:
            print("\n⚠️ Gestión de usuarios interrumpida por el usuario")
            print_success("¡Hasta luego! 🌾")
            break
        except Exception as e:
            print_error(f"Error inesperado: {e}")
            input("\n⏸️ Presiona Enter para continuar...")
    
    return True

if __name__ == "__main__":
    try:
        exito = main()
        sys.exit(0 if exito else 1)
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        sys.exit(1)