import sys
import os
sys.path.insert(0, os.path.abspath('backend/01_Sistema_Meteorologico/scripts'))
from datos_reales_openmeteo import OpenMeteoData

om = OpenMeteoData()
df = om.obtener_datos_pronostico('Quillota', 7)
if df is not None:
    print("Pronostico OK, filas:", len(df))
else:
    print("Pronostico FAILED (None)")

df2 = om.obtener_datos_historicos('Quillota', 14)
if df2 is not None:
    print("Historico OK, filas:", len(df2))
else:
    print("Historico FAILED (None)")
