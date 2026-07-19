import datetime
from typing import Dict, Any

class GeneradorInformesTecnicos:
    """
    Motor Text-to-Data.
    Toma los datos matemáticos del Ensemble y del histórico y los traduce a
    informes meteorológicos técnicos formales.
    """

    def generar_informe_precipitacion(self, observacion: float, pronostico_mediana: float, modelos_count: int, fecha_corte: datetime.datetime = None) -> str:
        if not fecha_corte:
            fecha_corte = datetime.datetime.now()
            
        fecha_str = fecha_corte.strftime("%A %d de %B de %Y, %H:%M UTC (%H:%M hora local)")
        
        # Algoritmo de evaluación semántica
        desviacion = observacion - pronostico_mediana
        if abs(desviacion) < 5.0:
            evaluacion = "capturado con alta precisión por el consenso de los modelos climáticos."
        elif desviacion > 0:
            evaluacion = f"superando las expectativas del consenso, el cual subestimó el evento por una desviación de {abs(desviacion):.1f} mm."
        else:
            evaluacion = f"estando por debajo de lo pronosticado, con una desviación de {abs(desviacion):.1f} mm respecto a la mediana."

        # Plantilla
        informe = f"""
INFORME METEOROLÓGICO TÉCNICO
Validación del Evento de Precipitación en Quillota — Pronóstico versus Observación
Corte de análisis: {fecha_str} | METGO 3D SpA

1. Resumen ejecutivo
A la fecha de corte de este informe, la estación Quillota Liceo Agrícola (Dirección Meteorológica de Chile) registra un acumulado de {observacion:.1f} mm.
Este evento fue simulado y monitoreado utilizando {modelos_count} Modelos de Circulación Global (incluyendo ECMWF, GFS e ICON).

2. Análisis de Rendimiento (Ensemble)
El ensamble multimodelo previó una mediana de precipitación de {pronostico_mediana:.1f} mm.
En conclusión, el evento fue {evaluacion}
La persistencia de la alta humedad y los patrones de nubosidad mantienen el riesgo en evaluación constante por la plataforma predictiva METGO 3D.
"""
        return informe.strip()

if __name__ == "__main__":
    import locale
    try:
        locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
    except:
        pass # Ignorar si no está instalado en el SO
        
    motor = GeneradorInformesTecnicos()
    print(motor.generar_informe_precipitacion(86.7, 85.0, 5))
