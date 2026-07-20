import requests

try:
    # Use local flask API to get the response.
    # We will simulate the local server or directly use the gestor.
    import sys
    import os
    sys.path.append('d:/METGO_3D_Quillota_60GB/backend/01_Sistema_Meteorologico/scripts')
    from gestor_datos_meteorologicos import gestor
    import json
    
    # Try fetching meteo calibrada equivalent from the gestor
    datos = gestor.obtener_datos_estacion('quillota')
    
    if 'precipitacion' in datos:
        print("PRECIPITATION FROM GESTOR:")
        print(datos['precipitacion'][:24])
    else:
        print("NO PRECIPITATION IN GESTOR:", datos.keys())

    # Try hitting the local API directly if running.
    # Otherwise just use gestor's openmeteo payload directly.
except Exception as e:
    print("Error:", e)
