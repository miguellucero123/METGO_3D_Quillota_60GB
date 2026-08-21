#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Motor de Restricciones Ambientales - Calidad del Aire (Copiapó / Paipote).
Implementa la clasificación de la atmósfera en Normal, Mala o Extrema
basado en variables meteorológicas, inversión térmica y variables sinópticas.
"""

from typing import Dict, Any

def evaluar_condicion_extrema(datos: Dict[str, Any]) -> bool:
    """
    Condición Meteorológica Extrema: Atmósfera en condiciones adversas para la dispersión de gases.
    - Condiciones estables/muy estables.
    - Vientos de componente Sur marcada (SSW-S-SSE), por un periodo >= 2-4 hr.
    - Intensidades de Viento ≈ 0,2 - 3,5 (m/s).
    - Viento en altura componente: SW-SSE.
    - Cielos despejados, bruma, niebla espesa (asociada a dorsal en altura).
    """
    estabilidad = datos.get("estabilidad", "neutra").lower()
    if estabilidad not in ["estable", "muy estable"]:
        return False
        
    viento_vel = datos.get("viento_sup_vel", 0.0)
    if not (0.2 <= viento_vel <= 3.5):
        return False
        
    viento_dir = datos.get("viento_sup_dir", "")
    if viento_dir not in ["SSW", "S", "SSE"]:
        return False
        
    horas_viento_sur = datos.get("horas_viento_sur", 0)
    # Se ajusta a 1-2 horas en invierno o episodios críticos según requerimiento
    if horas_viento_sur < 2:
        return False
        
    inversion_termica = datos.get("inversion_termica", False)
    dorsal_altura = datos.get("dorsal_altura", False)
    
    # Si hay inversión térmica fuerte y dorsal en altura, es un episodio crítico
    if inversion_termica and dorsal_altura:
        return True
        
    return False

def evaluar_condicion_mala(datos: Dict[str, Any]) -> bool:
    """
    Condición Meteorológica Mala: Atmósfera en condiciones desfavorables para la dispersión de gases.
    - Condiciones de estabilidad neutra/estable/neutra.
    - Vientos de dirección variando de W-WNW a SW-SE.
    - Intensidades de viento ≈ 1,0 - 3,5 (m/s).
    - Cielos parciales a despejados, bruma, niebla.
    """
    estabilidad = datos.get("estabilidad", "neutra").lower()
    if estabilidad not in ["neutra", "estable"]:
        return False
        
    viento_vel = datos.get("viento_sup_vel", 0.0)
    if not (1.0 <= viento_vel <= 3.5):
        return False
        
    viento_dir = datos.get("viento_sup_dir", "")
    dirs_malas = ["W", "WNW", "SW", "SSW", "S", "SSE", "SE"]
    if viento_dir not in dirs_malas:
        return False
        
    cielo = datos.get("cielo", "despejado").lower()
    if cielo in ["nublado", "cubierto", "lluvia", "llovizna"]:
        # Si llueve o está completamente cubierto por estratos, suele mejorar la dispersión o lavar material
        return False
        
    return True

def clasificar_condicion(datos: Dict[str, Any]) -> str:
    """
    Clasifica la condición atmosférica en base a los parámetros proporcionados.
    
    Args:
        datos (dict): Diccionario con las variables:
            - estabilidad (str)
            - viento_sup_dir (str)
            - viento_sup_vel (float) m/s
            - viento_altura_dir (str)
            - cielo (str)
            - horas_viento_sur (int)
            - inversion_termica (bool)
            - dorsal_altura (bool)
            
    Returns:
        str: "Extrema", "Mala" o "Normal"
    """
    if evaluar_condicion_extrema(datos):
        return "Extrema"
        
    if evaluar_condicion_mala(datos):
        return "Mala"
        
    # Por defecto, si no hay estancamiento severo ni persistencia de viento sur,
    # y los vientos permiten dispersión, es Normal.
    return "Normal"

# Ejemplo de uso interno / pruebas
if __name__ == "__main__":
    datos_prueba_extrema = {
        "estabilidad": "muy estable",
        "viento_sup_dir": "S",
        "viento_sup_vel": 1.5,
        "viento_altura_dir": "SW",
        "cielo": "niebla espesa",
        "horas_viento_sur": 3,
        "inversion_termica": True,
        "dorsal_altura": True
    }
    
    print(f"Resultado prueba: {clasificar_condicion(datos_prueba_extrema)}")
