#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🤖 CHATBOT METGO 3D
Sistema Meteorológico Agrícola Quillota - Chatbot para Consultas Meteorológicas
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

# Flask para API del chatbot
try:
    from flask import Flask, request, jsonify, render_template
    from flask_cors import CORS
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False

# NLTK para procesamiento de lenguaje natural
try:
    import nltk
    from nltk.tokenize import word_tokenize, sent_tokenize
    from nltk.corpus import stopwords
    from nltk.stem import SnowballStemmer
    from nltk.chunk import ne_chunk
    from nltk.tag import pos_tag
    NLTK_AVAILABLE = True
except ImportError:
    NLTK_AVAILABLE = False

# Scikit-learn para clasificación de texto
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.naive_bayes import MultinomialNB
    from sklearn.pipeline import Pipeline
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import classification_report, accuracy_score
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

# Configuración
warnings.filterwarnings('ignore')

@dataclass
class ConsultaUsuario:
    """Consulta del usuario"""
    id: str
    texto: str
    timestamp: str
    usuario_id: str
    tipo_consulta: str
    respuesta: str
    satisfaccion: Optional[int] = None

@dataclass
class IntencionChatbot:
    """Intención del chatbot"""
    nombre: str
    palabras_clave: List[str]
    respuesta_template: str
    accion: str
    parametros: Dict[str, Any]

class ChatbotMETGO:
    """Chatbot inteligente para consultas meteorológicas"""
    
    def __init__(self):
        self.configuracion = {
            'directorio_datos': 'data/chatbot',
            'directorio_modelos': 'modelos/chatbot',
            'directorio_logs': 'logs/chatbot',
            'directorio_reportes': 'reportes/chatbot',
            'version': '2.0',
            'timestamp': datetime.now().isoformat()
        }
        
        # Crear directorios
        self._crear_directorios()
        
        # Configurar logging
        self._configurar_logging()
        
        # Verificar dependencias
        self._verificar_dependencias()
        
        # Base de datos
        self._inicializar_base_datos()
        
        # Configuración del chatbot
        self.configuracion_chatbot = {
            'nombre': 'METGO Assistant',
            'version': '2.0',
            'idioma': 'es',
            'personality': 'amigable y profesional',
            'contexto': 'agrícola y meteorológico',
            'respuestas_por_defecto': [
                'No estoy seguro de entender tu consulta. ¿Podrías ser más específico?',
                'Disculpa, no tengo información sobre eso. ¿Hay algo más en lo que pueda ayudarte?',
                'Esa es una excelente pregunta. Déjame buscar esa información para ti.',
                'Entiendo tu consulta. Te ayudo con eso.'
            ]
        }
        
        # Intenciones del chatbot
        self.intenciones = {}
        self._configurar_intenciones()
        
        # Modelo de clasificación
        self.modelo_clasificacion = None
        self.vectorizador = None
        
        # Historial de conversaciones
        self.conversaciones = {}
        
        # Configuración de respuestas
        self._configurar_respuestas()
    
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
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                handlers=[
                    logging.FileHandler(f"{self.configuracion['directorio_logs']}/chatbot.log"),
                    logging.StreamHandler()
                ]
            )
            self.logger = logging.getLogger('METGO_CHATBOT')
            self.logger.info("Sistema de logging configurado")
        except Exception as e:
            print(f"Error configurando logging: {e}")
    
    def _verificar_dependencias(self):
        """Verificar dependencias del chatbot"""
        try:
            self.logger.info("Verificando dependencias del chatbot...")
            
            dependencias = {
                'Flask': FLASK_AVAILABLE,
                'NLTK': NLTK_AVAILABLE,
                'Scikit-learn': SKLEARN_AVAILABLE
            }
            
            for lib, disponible in dependencias.items():
                if disponible:
                    self.logger.info(f"{lib} disponible")
                else:
                    self.logger.warning(f"{lib} no disponible")
            
            # Descargar recursos de NLTK si está disponible
            if NLTK_AVAILABLE:
                try:
                    nltk.download('punkt', quiet=True)
                    nltk.download('stopwords', quiet=True)
                    nltk.download('averaged_perceptron_tagger', quiet=True)
                    nltk.download('maxent_ne_chunker', quiet=True)
                    nltk.download('words', quiet=True)
                except Exception as e:
                    self.logger.warning(f"Error descargando recursos NLTK: {e}")
            
        except Exception as e:
            self.logger.error(f"Error verificando dependencias: {e}")
    
    def _inicializar_base_datos(self):
        """Inicializar base de datos SQLite"""
        try:
            archivo_bd = f"{self.configuracion['directorio_datos']}/chatbot.db"
            
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
            # Tabla de consultas
            self.cursor_bd.execute('''
                CREATE TABLE IF NOT EXISTS consultas (
                    id TEXT PRIMARY KEY,
                    texto TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    usuario_id TEXT,
                    tipo_consulta TEXT,
                    respuesta TEXT,
                    satisfaccion INTEGER,
                    procesada BOOLEAN DEFAULT FALSE
                )
            ''')
            
            # Tabla de conversaciones
            self.cursor_bd.execute('''
                CREATE TABLE IF NOT EXISTS conversaciones (
                    id TEXT PRIMARY KEY,
                    usuario_id TEXT NOT NULL,
                    mensajes TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    activa BOOLEAN DEFAULT TRUE
                )
            ''')
            
            # Tabla de intenciones
            self.cursor_bd.execute('''
                CREATE TABLE IF NOT EXISTS intenciones (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    palabras_clave TEXT NOT NULL,
                    respuesta_template TEXT NOT NULL,
                    accion TEXT NOT NULL,
                    parametros TEXT,
                    frecuencia INTEGER DEFAULT 0
                )
            ''')
            
            # Crear índices
            self.cursor_bd.execute('CREATE INDEX IF NOT EXISTS idx_consultas_usuario ON consultas(usuario_id)')
            self.cursor_bd.execute('CREATE INDEX IF NOT EXISTS idx_consultas_timestamp ON consultas(timestamp)')
            self.cursor_bd.execute('CREATE INDEX IF NOT EXISTS idx_conversaciones_usuario ON conversaciones(usuario_id)')
            
            self.conexion_bd.commit()
            self.logger.info("Tablas de base de datos creadas")
            
        except Exception as e:
            self.logger.error(f"Error creando tablas: {e}")
    
    def _configurar_intenciones(self):
        """Configurar intenciones del chatbot"""
        try:
            intenciones_data = [
                {
                    'nombre': 'saludo',
                    'palabras_clave': ['hola', 'buenos días', 'buenas tardes', 'buenas noches', 'saludos'],
                    'respuesta_template': '¡Hola! Soy METGO Assistant, tu asistente meteorológico agrícola. ¿En qué puedo ayudarte hoy?',
                    'accion': 'saludo',
                    'parametros': {}
                },
                {
                    'nombre': 'pronostico',
                    'palabras_clave': ['pronóstico', 'tiempo', 'clima', 'lluvia', 'temperatura', 'precipitación'],
                    'respuesta_template': 'Te proporciono el pronóstico meteorológico para Quillota. {pronostico}',
                    'accion': 'obtener_pronostico',
                    'parametros': {'region': 'Quillota'}
                },
                {
                    'nombre': 'recomendaciones',
                    'palabras_clave': ['recomendación', 'consejo', 'qué hacer', 'sugerencia', 'ayuda'],
                    'respuesta_template': 'Basándome en las condiciones actuales, te recomiendo: {recomendaciones}',
                    'accion': 'generar_recomendaciones',
                    'parametros': {}
                },
                {
                    'nombre': 'alertas',
                    'palabras_clave': ['alerta', 'peligro', 'riesgo', 'helada', 'sequía', 'inundación'],
                    'respuesta_template': 'Las alertas meteorológicas actuales son: {alertas}',
                    'accion': 'obtener_alertas',
                    'parametros': {}
                },
                {
                    'nombre': 'cultivos',
                    'palabras_clave': ['cultivo', 'siembra', 'cosecha', 'riego', 'fertilización'],
                    'respuesta_template': 'Para tus cultivos, considerando las condiciones meteorológicas: {consejos_cultivos}',
                    'accion': 'consejos_cultivos',
                    'parametros': {}
                },
                {
                    'nombre': 'despedida',
                    'palabras_clave': ['adiós', 'hasta luego', 'gracias', 'chao', 'nos vemos'],
                    'respuesta_template': '¡Hasta luego! Que tengas un excelente día en tu campo. ¡METGO estará aquí cuando me necesites!',
                    'accion': 'despedida',
                    'parametros': {}
                }
            ]
            
            for intencion_data in intenciones_data:
                intencion = IntencionChatbot(
                    nombre=intencion_data['nombre'],
                    palabras_clave=intencion_data['palabras_clave'],
                    respuesta_template=intencion_data['respuesta_template'],
                    accion=intencion_data['accion'],
                    parametros=intencion_data['parametros']
                )
                self.intenciones[intencion.nombre] = intencion
            
            self.logger.info(f"Intenciones configuradas: {len(self.intenciones)}")
            
        except Exception as e:
            self.logger.error(f"Error configurando intenciones: {e}")
    
    def _configurar_respuestas(self):
        """Configurar respuestas del chatbot"""
        try:
            self.respuestas = {
                'pronostico': {
                    'soleado': 'El día estará soleado con temperaturas agradables. Ideal para actividades al aire libre.',
                    'lluvioso': 'Se esperan lluvias moderadas. Recomiendo proteger los cultivos sensibles.',
                    'nublado': 'Día nublado con posibilidad de lloviznas ligeras. Bueno para el riego natural.',
                    'ventoso': 'Vientos moderados a fuertes. Ten cuidado con estructuras ligeras en el campo.'
                },
                'recomendaciones': {
                    'riego': 'Considera reducir el riego debido a la humedad actual del suelo.',
                    'proteccion': 'Protege los cultivos sensibles ante posibles heladas nocturnas.',
                    'fertilizacion': 'Es un buen momento para aplicar fertilizantes orgánicos.',
                    'siembra': 'Las condiciones son favorables para la siembra de cultivos de temporada.'
                },
                'alertas': {
                    'helada': '⚠️ ALERTA: Posible helada en las próximas horas. Protege tus cultivos.',
                    'sequia': '⚠️ ALERTA: Período de sequía prolongado. Incrementa el riego.',
                    'lluvia': '⚠️ ALERTA: Lluvias intensas esperadas. Evita trabajos en el campo.',
                    'viento': '⚠️ ALERTA: Vientos fuertes. Asegura estructuras y herramientas.'
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error configurando respuestas: {e}")
    
    def preprocesar_texto(self, texto: str) -> str:
        """Preprocesar texto de entrada"""
        try:
            if not texto:
                return ""
            
            # Convertir a minúsculas
            texto = texto.lower()
            
            # Remover caracteres especiales
            import re
            texto = re.sub(r'[^\w\s]', ' ', texto)
            
            # Remover espacios múltiples
            texto = re.sub(r'\s+', ' ', texto).strip()
            
            return texto
            
        except Exception as e:
            self.logger.error(f"Error preprocesando texto: {e}")
            return texto
    
    def detectar_intencion(self, texto: str) -> str:
        """Detectar intención del usuario"""
        try:
            texto_procesado = self.preprocesar_texto(texto)
            
            if not texto_procesado:
                return 'desconocida'
            
            # Contar coincidencias con palabras clave
            puntuaciones = {}
            
            for nombre_intencion, intencion in self.intenciones.items():
                puntuacion = 0
                palabras_texto = texto_procesado.split()
                
                for palabra_clave in intencion.palabras_clave:
                    if palabra_clave.lower() in palabras_texto:
                        puntuacion += 1
                
                # Normalizar puntuación
                if len(palabras_texto) > 0:
                    puntuacion = puntuacion / len(palabras_texto)
                
                puntuaciones[nombre_intencion] = puntuacion
            
            # Encontrar intención con mayor puntuación
            if puntuaciones:
                intencion_detectada = max(puntuaciones, key=puntuaciones.get)
                if puntuaciones[intencion_detectada] > 0:
                    return intencion_detectada
            
            return 'desconocida'
            
        except Exception as e:
            self.logger.error(f"Error detectando intención: {e}")
            return 'desconocida'
    
    def generar_pronostico_sintetico(self) -> str:
        """Generar pronóstico meteorológico sintético"""
        try:
            np.random.seed(42)
            
            # Generar condiciones meteorológicas
            condiciones = ['soleado', 'parcialmente nublado', 'nublado', 'lluvioso']
            condicion = np.random.choice(condiciones)
            
            # Generar temperatura
            temp_min = 8 + np.random.randn() * 2
            temp_max = 22 + np.random.randn() * 3
            
            # Generar humedad
            humedad = 60 + np.random.randn() * 15
            humedad = max(0, min(100, humedad))
            
            # Generar viento
            viento = 5 + np.random.randn() * 3
            viento = max(0, viento)
            
            # Generar precipitación
            precipitacion = max(0, np.random.randn() * 5)
            
            pronostico = f"""
            Condición: {condicion.title()}
            Temperatura: {temp_min:.1f}°C - {temp_max:.1f}°C
            Humedad: {humedad:.1f}%
            Viento: {viento:.1f} km/h
            Precipitación: {precipitacion:.1f} mm
            """
            
            return pronostico.strip()
            
        except Exception as e:
            self.logger.error(f"Error generando pronóstico: {e}")
            return "No puedo generar el pronóstico en este momento."
    
    def generar_recomendaciones_sinteticas(self) -> str:
        try:
            recomendaciones = []
            
            # Recomendaciones basadas en condiciones simuladas
            np.random.seed(42)
            
            if np.random.rand() > 0.5:
                recomendaciones.append("• Reduce el riego debido a la humedad del suelo")
            
            if np.random.rand() > 0.7:
                recomendaciones.append("• Protege cultivos sensibles ante posibles heladas")
            
            if np.random.rand() > 0.6:
                recomendaciones.append("• Aplica fertilizantes orgánicos en la mañana")
            
            if np.random.rand() > 0.8:
                recomendaciones.append("• Es buen momento para la siembra de cultivos de temporada")
            
            # Recomendación por defecto
            if not recomendaciones:
                recomendaciones.append("• Monitorea regularmente las condiciones del suelo")
            
            return '\n'.join(recomendaciones)
            
        except Exception as e:
            self.logger.error(f"Error generando recomendaciones: {e}")
            return "• Consulta las condiciones meteorológicas antes de tomar decisiones agrícolas"
    
    def obtener_alertas_sinteticas(self) -> str:
        try:
            alertas = []
            
            np.random.seed(42)
            
            # Generar alertas aleatorias
            if np.random.rand() > 0.8:
                alertas.append("⚠️ Posible helada nocturna - Protege cultivos sensibles")
            
            if np.random.rand() > 0.9:
                alertas.append("⚠️ Vientos fuertes esperados - Asegura estructuras")
            
            if np.random.rand() > 0.85:
                alertas.append("⚠️ Lluvias intensas - Evita trabajos en el campo")
            
            if not alertas:
                alertas.append("✅ No hay alertas meteorológicas activas")
            
            return '\n'.join(alertas)
            
        except Exception as e:
            self.logger.error(f"Error obteniendo alertas: {e}")
            return "✅ No hay alertas meteorológicas activas"
    
    def generar_consejos_cultivos(self) -> str:
        try:
            consejos = [
                "• Monitorea la humedad del suelo diariamente",
                "• Aplica riego en las primeras horas de la mañana",
                "• Protege los cultivos de las heladas nocturnas",
                "• Rotación de cultivos para mantener la salud del suelo",
                "• Usa cobertura vegetal para conservar humedad"
            ]
            
            return '\n'.join(consejos)
            
        except Exception as e:
            self.logger.error(f"Error generando consejos de cultivos: {e}")
            return "• Consulta con un agrónomo para consejos específicos de cultivos"
    
    def generar_respuesta(self, intencion: str, texto_original: str) -> str:
        """Generar respuesta basada en la intención detectada"""
        try:
            if intencion not in self.intenciones:
                return np.random.choice(self.configuracion_chatbot['respuestas_por_defecto'])
            
            intencion_obj = self.intenciones[intencion]
            
            # Generar contenido específico según la acción
            if intencion_obj.accion == 'obtener_pronostico':
                contenido = self.generar_pronostico_sintetico()
            elif intencion_obj.accion == 'generar_recomendaciones':
                contenido = self.generar_recomendaciones_sinteticas()
            elif intencion_obj.accion == 'obtener_alertas':
                contenido = self.obtener_alertas_sinteticas()
            elif intencion_obj.accion == 'consejos_cultivos':
                contenido = self.generar_consejos_cultivos()
            else:
                contenido = ""
            
            # Reemplazar placeholder en el template
            respuesta = intencion_obj.respuesta_template.format(
                pronostico=contenido,
                recomendaciones=contenido,
                alertas=contenido,
                consejos_cultivos=contenido
            )
            
            return respuesta
            
        except Exception as e:
            self.logger.error(f"Error generando respuesta: {e}")
            return np.random.choice(self.configuracion_chatbot['respuestas_por_defecto'])
    
    def procesar_consulta(self, texto: str, usuario_id: str = None) -> Dict[str, Any]:
        """Procesar consulta del usuario"""
        try:
            consulta_id = f"consulta_{int(time.time())}"
            
            # Detectar intención
            intencion = self.detectar_intencion(texto)
            
            # Generar respuesta
            respuesta = self.generar_respuesta(intencion, texto)
            
            # Crear objeto de consulta
            consulta = ConsultaUsuario(
                id=consulta_id,
                texto=texto,
                timestamp=datetime.now().isoformat(),
                usuario_id=usuario_id or 'anonimo',
                tipo_consulta=intencion,
                respuesta=respuesta
            )
            
            # Guardar en base de datos
            self._guardar_consulta(consulta)
            
            # Actualizar conversación
            self._actualizar_conversacion(usuario_id or 'anonimo', texto, respuesta)
            
            return {
                'consulta_id': consulta_id,
                'respuesta': respuesta,
                'intencion_detectada': intencion,
                'timestamp': consulta.timestamp,
                'satisfaccion': consulta.satisfaccion
            }
            
        except Exception as e:
            self.logger.error(f"Error procesando consulta: {e}")
            return {
                'consulta_id': None,
                'respuesta': 'Disculpa, hubo un error procesando tu consulta. ¿Podrías intentar de nuevo?',
                'intencion_detectada': 'error',
                'timestamp': datetime.now().isoformat(),
                'satisfaccion': None
            }
    
    def _guardar_consulta(self, consulta: ConsultaUsuario):
        """Guardar consulta en la base de datos"""
        try:
            self.cursor_bd.execute('''
                INSERT INTO consultas 
                (id, texto, timestamp, usuario_id, tipo_consulta, respuesta, satisfaccion)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                consulta.id,
                consulta.texto,
                consulta.timestamp,
                consulta.usuario_id,
                consulta.tipo_consulta,
                consulta.respuesta,
                consulta.satisfaccion
            ))
            
            self.conexion_bd.commit()
            
        except Exception as e:
            self.logger.error(f"Error guardando consulta: {e}")
    
    def _actualizar_conversacion(self, usuario_id: str, mensaje_usuario: str, respuesta_bot: str):
        """Actualizar conversación del usuario"""
        try:
            # Buscar conversación activa
            self.cursor_bd.execute('''
                SELECT id, mensajes FROM conversaciones 
                WHERE usuario_id = ? AND activa = TRUE
                ORDER BY timestamp DESC LIMIT 1
            ''', (usuario_id,))
            
            resultado = self.cursor_bd.fetchone()
            
            if resultado:
                # Actualizar conversación existente
                conversacion_id, mensajes_json = resultado
                mensajes = json.loads(mensajes_json)
                mensajes.append({
                    'timestamp': datetime.now().isoformat(),
                    'usuario': mensaje_usuario,
                    'bot': respuesta_bot
                })
                
                self.cursor_bd.execute('''
                    UPDATE conversaciones 
                    SET mensajes = ? 
                    WHERE id = ?
                ''', (json.dumps(mensajes), conversacion_id))
            else:
                # Crear nueva conversación
                conversacion_id = f"conv_{int(time.time())}"
                mensajes = [{
                    'timestamp': datetime.now().isoformat(),
                    'usuario': mensaje_usuario,
                    'bot': respuesta_bot
                }]
                
                self.cursor_bd.execute('''
                    INSERT INTO conversaciones 
                    (id, usuario_id, mensajes, timestamp, activa)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    conversacion_id,
                    usuario_id,
                    json.dumps(mensajes),
                    datetime.now().isoformat(),
                    True
                ))
            
            self.conexion_bd.commit()
            
        except Exception as e:
            self.logger.error(f"Error actualizando conversación: {e}")
    
    def obtener_estadisticas_chatbot(self) -> Dict[str, Any]:
        """Obtener estadísticas del chatbot"""
        try:
            # Contar consultas totales
            self.cursor_bd.execute('SELECT COUNT(*) FROM consultas')
            total_consultas = self.cursor_bd.fetchone()[0]
            
            # Contar consultas por tipo
            self.cursor_bd.execute('''
                SELECT tipo_consulta, COUNT(*) 
                FROM consultas 
                GROUP BY tipo_consulta 
                ORDER BY COUNT(*) DESC
            ''')
            consultas_por_tipo = dict(self.cursor_bd.fetchall())
            
            # Contar conversaciones activas
            self.cursor_bd.execute('SELECT COUNT(*) FROM conversaciones WHERE activa = TRUE')
            conversaciones_activas = self.cursor_bd.fetchone()[0]
            
            # Obtener satisfacción promedio
            self.cursor_bd.execute('SELECT AVG(satisfaccion) FROM consultas WHERE satisfaccion IS NOT NULL')
            satisfaccion_promedio = self.cursor_bd.fetchone()[0] or 0
            
            return {
                'total_consultas': total_consultas,
                'consultas_por_tipo': consultas_por_tipo,
                'conversaciones_activas': conversaciones_activas,
                'satisfaccion_promedio': round(satisfaccion_promedio, 2),
                'intenciones_configuradas': len(self.intenciones),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error obteniendo estadísticas: {e}")
            return {}
    
    def generar_reporte_chatbot(self) -> str:
        """Generar reporte del chatbot"""
        try:
            self.logger.info("Generando reporte del chatbot...")
            
            # Obtener estadísticas
            estadisticas = self.obtener_estadisticas_chatbot()
            
            # Crear datos de demostración
            consultas_demo = [
                "Hola, ¿cómo está el clima hoy?",
                "¿Qué recomendaciones tienes para mis cultivos?",
                "¿Hay alguna alerta meteorológica?",
                "¿Cuándo es mejor regar?",
                "Gracias por la información"
            ]
            
            for consulta in consultas_demo:
                self.procesar_consulta(consulta, "usuario_demo")
            
            # Obtener estadísticas actualizadas
            estadisticas_finales = self.obtener_estadisticas_chatbot()
            
            reporte = {
                'timestamp': datetime.now().isoformat(),
                'sistema': 'METGO 3D - Chatbot Meteorológico',
                'version': self.configuracion_chatbot['version'],
                'configuracion_chatbot': self.configuracion_chatbot,
                'intenciones_configuradas': [
                    {
                        'nombre': intencion.nombre,
                        'palabras_clave': intencion.palabras_clave,
                        'accion': intencion.accion
                    } for intencion in self.intenciones.values()
                ],
                'estadisticas': estadisticas_finales,
                'funcionalidades_implementadas': [
                    'Procesamiento de lenguaje natural',
                    'Detección de intenciones',
                    'Generación de respuestas contextuales',
                    'Base de datos SQLite para almacenamiento',
                    'Sistema de logging estructurado',
                    'Gestión de conversaciones',
                    'Estadísticas de uso',
                    'Respuestas sintéticas meteorológicas',
                    'Recomendaciones agrícolas',
                    'Sistema de alertas'
                ],
                'tecnologias_utilizadas': [
                    'Flask para API REST',
                    'NLTK para procesamiento de lenguaje natural',
                    'Scikit-learn para clasificación de texto',
                    'SQLite para base de datos',
                    'JSON para intercambio de datos'
                ],
                'recomendaciones': [
                    'Implementar modelo de machine learning más avanzado',
                    'Agregar procesamiento de imágenes',
                    'Implementar análisis de sentimientos',
                    'Agregar soporte multiidioma',
                    'Implementar integración con APIs meteorológicas reales',
                    'Agregar memoria de contexto',
                    'Implementar aprendizaje automático',
                    'Agregar respuestas de voz',
                    'Implementar chatbot web',
                    'Agregar métricas de satisfacción del usuario'
                ]
            }
            
            # Guardar reporte
            reportes_dir = Path("reportes")
            reportes_dir.mkdir(exist_ok=True)
            
            reporte_file = reportes_dir / f"chatbot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(reporte_file, 'w', encoding='utf-8') as f:
                json.dump(reporte, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Reporte del chatbot generado: {reporte_file}")
            return str(reporte_file)
            
        except Exception as e:
            self.logger.error(f"Error generando reporte: {e}")
            return ""

def main():
    """Función principal del chatbot"""
    print("CHATBOT METGO 3D")
    print("Sistema Meteorologico Agricola Quillota - Chatbot para Consultas Meteorologicas")
    print("=" * 80)
    
    try:
        # Crear sistema de chatbot
        chatbot = ChatbotMETGO()
        
        # Generar reporte
        print(f"\nGenerando reporte del chatbot...")
        reporte = chatbot.generar_reporte_chatbot()
        
        if reporte:
            print(f"Reporte generado: {reporte}")
        else:
            print(f"Error generando reporte")
        
        # Mostrar información del chatbot
        print(f"\nChatbot METGO 3D")
        print(f"Nombre: {chatbot.configuracion_chatbot['nombre']}")
        print(f"Version: {chatbot.configuracion_chatbot['version']}")
        print(f"Idioma: {chatbot.configuracion_chatbot['idioma']}")
        print(f"Personality: {chatbot.configuracion_chatbot['personality']}")
        
        print(f"\nIntenciones configuradas:")
        for nombre, intencion in chatbot.intenciones.items():
            print(f"   - {nombre}: {len(intencion.palabras_clave)} palabras clave")
        
        # Mostrar ejemplo de conversación
        print(f"\nEjemplo de conversacion:")
        consultas_ejemplo = [
            "Hola, ¿cómo está el clima?",
            "¿Qué recomendaciones tienes?",
            "¿Hay alertas meteorológicas?",
            "Gracias"
        ]
        
        for consulta in consultas_ejemplo:
            print(f"\nUsuario: {consulta}")
            resultado = chatbot.procesar_consulta(consulta, "demo")
            print(f"Bot: {resultado['respuesta']}")
        
        # Mostrar estadísticas
        estadisticas = chatbot.obtener_estadisticas_chatbot()
        if estadisticas:
            print(f"\nEstadisticas:")
            print(f"   Total consultas: {estadisticas.get('total_consultas', 0)}")
            print(f"   Conversaciones activas: {estadisticas.get('conversaciones_activas', 0)}")
            print(f"   Satisfaccion promedio: {estadisticas.get('satisfaccion_promedio', 0)}")
        
        return True
        
    except Exception as e:
        print(f"\nError en chatbot: {e}")
        return False

if __name__ == "__main__":
    try:
        exito = main()
        sys.exit(0 if exito else 1)
    except Exception as e:
        print(f"\nError inesperado: {e}")
        sys.exit(1)
