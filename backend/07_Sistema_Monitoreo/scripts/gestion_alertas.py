#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🌾 GESTIÓN DE ALERTAS DEL SISTEMA METGO 3D
Sistema Meteorológico Agrícola Quillota - Versión Operativa 2.0
"""

import os
import sys
import time
import json
import smtplib
import requests
from pathlib import Path
from datetime import datetime, timedelta

def print_header():
    """Imprimir encabezado"""
    print("🌾 GESTIÓN DE ALERTAS DEL SISTEMA METGO 3D")
    print("Sistema Meteorológico Agrícola Quillota - Versión Operativa 2.0")
    print("=" * 70)

def print_step(step, message):
    """Imprimir paso del proceso"""
    print(f"\n[{step}] {message}")
    print("-" * 50)

def print_success(message):
    """Imprimir mensaje de éxito")
    print(f"✅ {message}")

def print_error(message):
    """Imprimir mensaje de error")
    print(f"❌ {message}")

def print_warning(message):
    """Imprimir mensaje de advertencia")
    print(f"⚠️ {message}")

def print_info(message):
    """Imprimir mensaje informativo")
    print(f"ℹ️ {message}")

class GestorAlertas:
    """Clase para gestión de alertas del sistema"""
    
    def __init__(self):
        self.configuracion = {
            'directorio_alertas': 'alertas',
            'archivo_config': 'config/alertas.yaml',
            'archivo_alertas': 'alertas/alertas.json',
            'max_alertas': 1000,
            'timeout': 30  # segundos
        }
        
        self.alertas = []
        self.alertas_activas = []
        self.alertas_resueltas = []
        
        self.tipos_alertas = [
            'sistema',
            'meteorologico',
            'seguridad',
            'rendimiento',
            'datos',
            'conexion',
            'disco',
            'memoria'
        ]
        
        self.niveles_alertas = [
            'info',
            'warning',
            'error',
            'critical'
        ]
    
    def cargar_configuracion(self):
        """Cargar configuración de alertas"""
        try:
            print_info("Cargando configuración de alertas...")
            
            config_file = Path(self.configuracion['archivo_config'])
            if config_file.exists():
                print_success("Configuración cargada")
            else:
                print_warning("Archivo de configuración no encontrado")
            
            return True
            
        except Exception as e:
            print_error(f"Error cargando configuración: {e}")
            return False
    
    def crear_estructura_alertas(self):
        """Crear estructura de alertas"""
        try:
            print_info("Creando estructura de alertas...")
            
            # Crear directorio principal
            alertas_dir = Path(self.configuracion['directorio_alertas'])
            alertas_dir.mkdir(exist_ok=True)
            
            # Crear subdirectorios
            subdirs = ['activas', 'resueltas', 'archivadas']
            for subdir in subdirs:
                (alertas_dir / subdir).mkdir(exist_ok=True)
            
            # Crear archivo de alertas si no existe
            archivo_alertas = Path(self.configuracion['archivo_alertas'])
            if not archivo_alertas.exists():
                with open(archivo_alertas, 'w', encoding='utf-8') as f:
                    json.dump([], f, indent=2, ensure_ascii=False)
            
            print_success("Estructura de alertas creada")
            return True
            
        except Exception as e:
            print_error(f"Error creando estructura: {e}")
            return False
    
    def crear_alerta(self, tipo, nivel, mensaje, detalles=None, usuario=None):
        """Crear nueva alerta"""
        try:
            print_info(f"Creando alerta: {tipo} - {nivel}")
            
            # Verificar que el tipo y nivel sean válidos
            if tipo not in self.tipos_alertas:
                print_error(f"Tipo de alerta no válido: {tipo}")
                return False
            
            if nivel not in self.niveles_alertas:
                print_error(f"Nivel de alerta no válido: {nivel}")
                return False
            
            # Crear alerta
            alerta = {
                'id': f"alerta_{int(time.time())}",
                'tipo': tipo,
                'nivel': nivel,
                'mensaje': mensaje,
                'detalles': detalles or {},
                'usuario': usuario or 'sistema',
                'estado': 'activa',
                'creada': datetime.now().isoformat(),
                'resuelta': None,
                'notificada': False,
                'acknowledged': False
            }
            
            # Agregar alerta
            self.alertas.append(alerta)
            self.alertas_activas.append(alerta)
            
            # Guardar alertas
            self.guardar_alertas()
            
            # Enviar notificación si es crítica
            if nivel in ['error', 'critical']:
                self.enviar_notificacion(alerta)
            
            print_success(f"Alerta {alerta['id']} creada correctamente")
            return alerta['id']
            
        except Exception as e:
            print_error(f"Error creando alerta: {e}")
            return None
    
    def resolver_alerta(self, alerta_id, resolucion=None):
        """Resolver alerta"""
        try:
            print_info(f"Resolviendo alerta: {alerta_id}")
            
            # Buscar alerta
            alerta = next((a for a in self.alertas if a['id'] == alerta_id), None)
            if not alerta:
                print_error(f"Alerta {alerta_id} no encontrada")
                return False
            
            # Verificar estado
            if alerta['estado'] != 'activa':
                print_error(f"Alerta {alerta_id} no está activa")
                return False
            
            # Cambiar estado
            alerta['estado'] = 'resuelta'
            alerta['resuelta'] = datetime.now().isoformat()
            alerta['resolucion'] = resolucion or 'Resuelta por el usuario'
            
            # Mover a alertas resueltas
            self.alertas_activas = [a for a in self.alertas_activas if a['id'] != alerta_id]
            self.alertas_resueltas.append(alerta)
            
            # Guardar alertas
            self.guardar_alertas()
            
            print_success(f"Alerta {alerta_id} resuelta")
            return True
            
        except Exception as e:
            print_error(f"Error resolviendo alerta: {e}")
            return False
    
    def listar_alertas(self, estado=None, tipo=None, nivel=None):
        """Listar alertas"""
        try:
            print_info("Listando alertas...")
            
            # Filtrar alertas
            alertas_filtradas = self.alertas
            
            if estado:
                alertas_filtradas = [a for a in alertas_filtradas if a['estado'] == estado]
            
            if tipo:
                alertas_filtradas = [a for a in alertas_filtradas if a['tipo'] == tipo]
            
            if nivel:
                alertas_filtradas = [a for a in alertas_filtradas if a['nivel'] == nivel]
            
            if not alertas_filtradas:
                print_warning("No hay alertas para mostrar")
                return []
            
            print(f"\n📋 Alertas ({len(alertas_filtradas)}):")
            print("-" * 120)
            print(f"{'ID':<15} {'Tipo':<15} {'Nivel':<10} {'Estado':<10} {'Mensaje':<30} {'Creada':<20} {'Usuario':<15}")
            print("-" * 120)
            
            for alerta in alertas_filtradas:
                print(f"{alerta['id']:<15} {alerta['tipo']:<15} {alerta['nivel']:<10} {alerta['estado']:<10} {alerta['mensaje'][:30]:<30} {alerta['creada'][:19]:<20} {alerta['usuario']:<15}")
            
            return alertas_filtradas
            
        except Exception as e:
            print_error(f"Error listando alertas: {e}")
            return []
    
    def enviar_notificacion(self, alerta):
        """Enviar notificación de alerta"""
        try:
            print_info(f"Enviando notificación para alerta: {alerta['id']}")
            
            # Crear mensaje de notificación
            mensaje = f"""
ALERTA DEL SISTEMA METGO 3D

ID: {alerta['id']}
Tipo: {alerta['tipo']}
Nivel: {alerta['nivel']}
Mensaje: {alerta['mensaje']}
Usuario: {alerta['usuario']}
Fecha: {alerta['creada']}

Detalles: {json.dumps(alerta['detalles'], indent=2)}
"""
            
            # Enviar por email si está configurado
            if self._enviar_email(mensaje):
                print_success("Notificación por email enviada")
            
            # Enviar por webhook si está configurado
            if self._enviar_webhook(alerta):
                print_success("Notificación por webhook enviada")
            
            # Marcar como notificada
            alerta['notificada'] = True
            
            return True
            
        except Exception as e:
            print_error(f"Error enviando notificación: {e}")
            return False
    
    def _enviar_email(self, mensaje):
        """Enviar notificación por email"""
        try:
            # Verificar configuración de email
            config_email = self._obtener_config_email()
            if not config_email.get('habilitado', False):
                return True
            
            # Configurar servidor SMTP
            server = smtplib.SMTP(config_email['servidor'], config_email['puerto'])
            server.starttls()
            server.login(config_email['usuario'], config_email['password'])
            
            # Crear mensaje
            from email.mime.text import MIMEText
            msg = MIMEText(mensaje)
            msg['Subject'] = 'Alerta del Sistema METGO 3D'
            msg['From'] = config_email['usuario']
            msg['To'] = ', '.join(config_email['destinatarios'])
            
            # Enviar email
            server.send_message(msg)
            server.quit()
            
            return True
            
        except Exception as e:
            print_warning(f"Error enviando email: {e}")
            return False
    
    def _enviar_webhook(self, alerta):
        """Enviar notificación por webhook"""
        try:
            # Verificar configuración de webhook
            config_webhook = self._obtener_config_webhook()
            if not config_webhook.get('habilitado', False):
                return True
            
            # Preparar datos
            datos = {
                'alerta': alerta,
                'sistema': 'METGO 3D',
                'timestamp': datetime.now().isoformat()
            }
            
            # Enviar webhook
            response = requests.post(
                config_webhook['url'],
                json=datos,
                timeout=self.configuracion['timeout']
            )
            
            if response.status_code == 200:
                return True
            else:
                print_warning(f"Error en webhook: {response.status_code}")
                return False
            
        except Exception as e:
            print_warning(f"Error enviando webhook: {e}")
            return False
    
    def _obtener_config_email(self):
        """Obtener configuración de email"""
        try:
            config_file = Path('config/email.yaml')
            if config_file.exists():
                import yaml
                with open(config_file, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f)
            else:
                return {'habilitado': False}
        except Exception:
            return {'habilitado': False}
    
    def _obtener_config_webhook(self):
        """Obtener configuración de webhook"""
        try:
            config_file = Path('config/webhook.yaml')
            if config_file.exists():
                import yaml
                with open(config_file, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f)
            else:
                return {'habilitado': False}
        except Exception:
            return {'habilitado': False}
    
    def archivar_alertas_antiguas(self, dias=30):
        """Archivar alertas antiguas"""
        try:
            print_info(f"Archivando alertas antiguas (más de {dias} días)...")
            
            # Calcular fecha límite
            fecha_limite = datetime.now() - timedelta(days=dias)
            
            # Filtrar alertas antiguas
            alertas_antiguas = [a for a in self.alertas 
                              if datetime.fromisoformat(a['creada']) < fecha_limite]
            
            if not alertas_antiguas:
                print_info("No hay alertas antiguas para archivar")
                return True
            
            # Mover a archivo
            archivo_alertas = Path(f"alertas/archivadas/alertas_{datetime.now().strftime('%Y%m%d')}.json")
            archivo_alertas.parent.mkdir(parents=True, exist_ok=True)
            
            with open(archivo_alertas, 'w', encoding='utf-8') as f:
                json.dump(alertas_antiguas, f, indent=2, ensure_ascii=False)
            
            # Remover de alertas activas
            self.alertas = [a for a in self.alertas if a not in alertas_antiguas]
            self.alertas_activas = [a for a in self.alertas_activas if a not in alertas_antiguas]
            self.alertas_resueltas = [a for a in self.alertas_resueltas if a not in alertas_antiguas]
            
            # Guardar alertas
            self.guardar_alertas()
            
            print_success(f"Alertas archivadas: {len(alertas_antiguas)}")
            return True
            
        except Exception as e:
            print_error(f"Error archivando alertas: {e}")
            return False
    
    def guardar_alertas(self):
        """Guardar alertas en archivo"""
        try:
            archivo_alertas = Path(self.configuracion['archivo_alertas'])
            with open(archivo_alertas, 'w', encoding='utf-8') as f:
                json.dump(self.alertas, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            print_error(f"Error guardando alertas: {e}")
            return False
    
    def cargar_alertas(self):
        """Cargar alertas desde archivo"""
        try:
            archivo_alertas = Path(self.configuracion['archivo_alertas'])
            if archivo_alertas.exists():
                with open(archivo_alertas, 'r', encoding='utf-8') as f:
                    self.alertas = json.load(f)
                
                # Clasificar alertas
                self.alertas_activas = [a for a in self.alertas if a['estado'] == 'activa']
                self.alertas_resueltas = [a for a in self.alertas if a['estado'] == 'resuelta']
                
                print_success(f"Alertas cargadas: {len(self.alertas)}")
                return True
            else:
                print_warning("Archivo de alertas no encontrado")
                return False
            
        except Exception as e:
            print_error(f"Error cargando alertas: {e}")
            return False
    
    def generar_reporte_alertas(self):
        """Generar reporte de alertas"""
        try:
            print_info("Generando reporte de alertas...")
            
            # Crear reporte
            reporte = {
                'timestamp': datetime.now().isoformat(),
                'sistema': 'METGO 3D - Sistema Meteorológico Agrícola Quillota',
                'version': '2.0',
                'alertas': {
                    'total': len(self.alertas),
                    'activas': len(self.alertas_activas),
                    'resueltas': len(self.alertas_resueltas),
                    'por_tipo': {},
                    'por_nivel': {}
                },
                'detalles': self.alertas
            }
            
            # Contar por tipo
            for tipo in self.tipos_alertas:
                count = len([a for a in self.alertas if a['tipo'] == tipo])
                reporte['alertas']['por_tipo'][tipo] = count
            
            # Contar por nivel
            for nivel in self.niveles_alertas:
                count = len([a for a in self.alertas if a['nivel'] == nivel])
                reporte['alertas']['por_nivel'][nivel] = count
            
            # Guardar reporte
            reportes_dir = Path("reportes")
            reportes_dir.mkdir(exist_ok=True)
            
            reporte_file = reportes_dir / f"alertas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(reporte_file, 'w', encoding='utf-8') as f:
                json.dump(reporte, f, indent=2, ensure_ascii=False)
            
            print_success(f"Reporte de alertas generado: {reporte_file}")
            
            # Mostrar resumen
            print(f"\n📊 Resumen de alertas:")
            print(f"Total: {reporte['alertas']['total']}")
            print(f"Activas: {reporte['alertas']['activas']}")
            print(f"Resueltas: {reporte['alertas']['resueltas']}")
            
            return str(reporte_file)
            
        except Exception as e:
            print_error(f"Error generando reporte: {e}")
            return None

def mostrar_menu():
    """Mostrar menú de gestión de alertas"""
    print("\n" + "=" * 70)
    print("📋 MENÚ DE GESTIÓN DE ALERTAS - METGO 3D")
    print("=" * 70)
    
    print("\n1. 🔍 Cargar configuración")
    print("2. 📁 Crear estructura de alertas")
    print("3. 📝 Crear alerta")
    print("4. ✅ Resolver alerta")
    print("5. 📋 Listar alertas")
    print("6. 📧 Enviar notificación")
    print("7. 📦 Archivar alertas antiguas")
    print("8. 💾 Cargar alertas")
    print("9. 📊 Generar reporte")
    print("10. ❌ Salir")
    
    print("\n" + "=" * 70)

def main():
    """Función principal de gestión de alertas"""
    print_header()
    
    # Crear gestor de alertas
    gestor = GestorAlertas()
    
    while True:
        mostrar_menu()
        
        try:
            opcion = input("\n🔢 Selecciona una opción (1-10): ").strip()
            
            if opcion == "1":
                print_step("1", "Cargando configuración")
                if gestor.cargar_configuracion():
                    print_success("Configuración cargada correctamente")
                else:
                    print_error("Error cargando configuración")
                input("\n⏸️ Presiona Enter para continuar...")
            
            elif opcion == "2":
                print_step("2", "Creando estructura de alertas")
                if gestor.crear_estructura_alertas():
                    print_success("Estructura de alertas creada correctamente")
                else:
                    print_error("Error creando estructura")
                input("\n⏸️ Presiona Enter para continuar...")
            
            elif opcion == "3":
                print_step("3", "Creando alerta")
                try:
                    tipo = input(f"Tipo de alerta ({', '.join(gestor.tipos_alertas)}): ").strip()
                    nivel = input(f"Nivel de alerta ({', '.join(gestor.niveles_alertas)}): ").strip()
                    mensaje = input("Mensaje: ").strip()
                    detalles = input("Detalles (JSON opcional): ").strip()
                    usuario = input("Usuario (opcional): ").strip()
                    
                    if detalles:
                        try:
                            detalles = json.loads(detalles)
                        except json.JSONDecodeError:
                            print_warning("Detalles no válidos, ignorando")
                            detalles = None
                    
                    alerta_id = gestor.crear_alerta(tipo, nivel, mensaje, detalles, usuario)
                    if alerta_id:
                        print_success(f"Alerta creada: {alerta_id}")
                    else:
                        print_error("Error creando alerta")
                except Exception as e:
                    print_error(f"Error: {e}")
                input("\n⏸️ Presiona Enter para continuar...")
            
            elif opcion == "4":
                print_step("4", "Resolviendo alerta")
                try:
                    alerta_id = input("ID de la alerta: ").strip()
                    resolucion = input("Resolución (opcional): ").strip()
                    
                    if gestor.resolver_alerta(alerta_id, resolucion):
                        print_success("Alerta resuelta correctamente")
                    else:
                        print_error("Error resolviendo alerta")
                except Exception as e:
                    print_error(f"Error: {e}")
                input("\n⏸️ Presiona Enter para continuar...")
            
            elif opcion == "5":
                print_step("5", "Listando alertas")
                try:
                    estado = input("Estado (opcional): ").strip() or None
                    tipo = input("Tipo (opcional): ").strip() or None
                    nivel = input("Nivel (opcional): ").strip() or None
                    
                    alertas = gestor.listar_alertas(estado, tipo, nivel)
                    if alertas:
                        print_success(f"Alertas listadas: {len(alertas)}")
                    else:
                        print_warning("No hay alertas para mostrar")
                except Exception as e:
                    print_error(f"Error: {e}")
                input("\n⏸️ Presiona Enter para continuar...")
            
            elif opcion == "6":
                print_step("6", "Enviando notificación")
                try:
                    alerta_id = input("ID de la alerta: ").strip()
                    
                    alerta = next((a for a in gestor.alertas if a['id'] == alerta_id), None)
                    if alerta:
                        if gestor.enviar_notificacion(alerta):
                            print_success("Notificación enviada correctamente")
                        else:
                            print_error("Error enviando notificación")
                    else:
                        print_error("Alerta no encontrada")
                except Exception as e:
                    print_error(f"Error: {e}")
                input("\n⏸️ Presiona Enter para continuar...")
            
            elif opcion == "7":
                print_step("7", "Archivando alertas antiguas")
                try:
                    dias = int(input("Días (opcional, default 30): ").strip() or "30")
                    
                    if gestor.archivar_alertas_antiguas(dias):
                        print_success("Alertas archivadas correctamente")
                    else:
                        print_error("Error archivando alertas")
                except Exception as e:
                    print_error(f"Error: {e}")
                input("\n⏸️ Presiona Enter para continuar...")
            
            elif opcion == "8":
                print_step("8", "Cargando alertas")
                if gestor.cargar_alertas():
                    print_success("Alertas cargadas correctamente")
                else:
                    print_error("Error cargando alertas")
                input("\n⏸️ Presiona Enter para continuar...")
            
            elif opcion == "9":
                print_step("9", "Generando reporte de alertas")
                reporte = gestor.generar_reporte_alertas()
                if reporte:
                    print_success(f"Reporte generado: {reporte}")
                else:
                    print_error("Error generando reporte")
                input("\n⏸️ Presiona Enter para continuar...")
            
            elif opcion == "10":
                print_info("Saliendo del gestor de alertas...")
                print_success("¡Hasta luego! 🌾")
                break
            
            else:
                print_warning("Opción no válida. Selecciona 1-10.")
                time.sleep(1)
        
        except KeyboardInterrupt:
            print("\n⚠️ Gestión de alertas interrumpida por el usuario")
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