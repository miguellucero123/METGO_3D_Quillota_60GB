#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VISUALIZADOR DE CHATS EXPORTADOS - METGO 3D
Sistema para visualizar y navegar por chats exportados
"""

import os
import re
from pathlib import Path
from datetime import datetime
import json

class VisualizadorChats:
    """Visualizador de chats exportados"""
    
    def __init__(self):
        self.proyecto_actual = Path.cwd()
        self.archivos_chat = []
        self.buscar_archivos_chat()
    
    def buscar_archivos_chat(self):
        """Buscar archivos de chat en el proyecto"""
        print("BUSCANDO ARCHIVOS DE CHAT")
        print("="*50)
        
        # Patrones de archivos de chat
        patrones = [
            "cursor_*.md",
            "*chat*.md",
            "*conversacion*.md",
            "*export*.md"
        ]
        
        for patron in patrones:
            for archivo in self.proyecto_actual.glob(patron):
                if archivo.is_file():
                    tamaño = archivo.stat().st_size
                    fecha_mod = datetime.fromtimestamp(archivo.stat().st_mtime)
                    
                    self.archivos_chat.append({
                        'nombre': archivo.name,
                        'ruta': str(archivo),
                        'tamaño': tamaño,
                        'fecha_modificacion': fecha_mod,
                        'tamaño_mb': tamaño / (1024**2)
                    })
        
        # Ordenar por fecha de modificación
        self.archivos_chat.sort(key=lambda x: x['fecha_modificacion'], reverse=True)
        
        print(f"Archivos de chat encontrados: {len(self.archivos_chat)}")
        for i, archivo in enumerate(self.archivos_chat, 1):
            print(f"   {i}. {archivo['nombre']} ({archivo['tamaño_mb']:.2f} MB) - {archivo['fecha_modificacion'].strftime('%Y-%m-%d %H:%M')}")
    
    def mostrar_menu_principal(self):
        """Mostrar menú principal"""
        while True:
            print("\n" + "="*60)
            print("VISUALIZADOR DE CHATS EXPORTADOS - METGO 3D")
            print("="*60)
            print("1. Listar archivos de chat")
            print("2. Abrir archivo de chat")
            print("3. Buscar en chats")
            print("4. Extraer conversaciones específicas")
            print("5. Crear resumen de chats")
            print("6. Exportar chat seleccionado")
            print("0. Salir")
            print("-"*60)
            
            opcion = input("Seleccione una opcion: ").strip()
            
            if opcion == "1":
                self.listar_archivos()
            elif opcion == "2":
                self.abrir_archivo()
            elif opcion == "3":
                self.buscar_en_chats()
            elif opcion == "4":
                self.extraer_conversaciones()
            elif opcion == "5":
                self.crear_resumen()
            elif opcion == "6":
                self.exportar_chat()
            elif opcion == "0":
                print("Hasta luego!")
                break
            else:
                print("Opcion no valida")
    
    def listar_archivos(self):
        """Listar archivos de chat con detalles"""
        print("\nARCHIVOS DE CHAT DISPONIBLES")
        print("-"*50)
        
        for i, archivo in enumerate(self.archivos_chat, 1):
            print(f"\n{i}. {archivo['nombre']}")
            print(f"   Ruta: {archivo['ruta']}")
            print(f"   Tamano: {archivo['tamaño_mb']:.2f} MB")
            print(f"   Modificado: {archivo['fecha_modificacion'].strftime('%Y-%m-%d %H:%M:%S')}")
    
    def abrir_archivo(self):
        """Abrir archivo de chat específico"""
        if not self.archivos_chat:
            print("No hay archivos de chat disponibles")
            return
        
        print("\nABRIR ARCHIVO DE CHAT")
        print("-"*30)
        
        for i, archivo in enumerate(self.archivos_chat, 1):
            print(f"{i}. {archivo['nombre']}")
        
        try:
            seleccion = int(input("\nSeleccione el numero del archivo: ")) - 1
            
            if 0 <= seleccion < len(self.archivos_chat):
                archivo_seleccionado = self.archivos_chat[seleccion]
                self.mostrar_contenido_archivo(archivo_seleccionado)
            else:
                print("Numero invalido")
        except ValueError:
            print("Por favor ingrese un numero valido")
    
    def mostrar_contenido_archivo(self, archivo):
        """Mostrar contenido del archivo seleccionado"""
        print(f"\nCONTENIDO DE: {archivo['nombre']}")
        print("="*60)
        
        try:
            with open(archivo['ruta'], 'r', encoding='utf-8') as f:
                contenido = f.read()
            
            # Mostrar primeras 50 líneas
            lineas = contenido.split('\n')
            print(f"Total de lineas: {len(lineas)}")
            print(f"Tamano: {archivo['tamaño_mb']:.2f} MB")
            print("\nPRIMERAS 50 LINEAS:")
            print("-"*40)
            
            for i, linea in enumerate(lineas[:50], 1):
                print(f"{i:3d}: {linea}")
            
            if len(lineas) > 50:
                print(f"\n... y {len(lineas) - 50} lineas mas")
            
            # Opciones adicionales
            print("\nOPCIONES:")
            print("1. Ver mas lineas")
            print("2. Buscar texto especifico")
            print("3. Extraer secciones")
            print("4. Volver al menu")
            
            opcion = input("Seleccione una opcion: ").strip()
            
            if opcion == "1":
                self.ver_mas_lineas(contenido)
            elif opcion == "2":
                self.buscar_texto_en_archivo(contenido, archivo['nombre'])
            elif opcion == "3":
                self.extraer_secciones(contenido, archivo['nombre'])
            
        except Exception as e:
            print(f"Error leyendo archivo: {e}")
    
    def ver_mas_lineas(self, contenido):
        """Ver más líneas del archivo"""
        lineas = contenido.split('\n')
        
        try:
            inicio = int(input(f"Ingrese linea de inicio (1-{len(lineas)}): ")) - 1
            fin = int(input(f"Ingrese linea final ({inicio+1}-{len(lineas)}): "))
            
            if 0 <= inicio < len(lineas) and inicio < fin <= len(lineas):
                print(f"\nLINEAS {inicio+1}-{fin}:")
                print("-"*40)
                
                for i, linea in enumerate(lineas[inicio:fin], inicio+1):
                    print(f"{i:3d}: {linea}")
            else:
                print("Rango invalido")
        except ValueError:
            print("Por favor ingrese numeros validos")
    
    def buscar_texto_en_archivo(self, contenido, nombre_archivo):
        """Buscar texto específico en el archivo"""
        print(f"\nBUSCAR EN: {nombre_archivo}")
        print("-"*40)
        
        termino = input("Ingrese termino a buscar: ").strip()
        
        if not termino:
            print("Termino de busqueda vacio")
            return
        
        lineas = contenido.split('\n')
        coincidencias = []
        
        for i, linea in enumerate(lineas, 1):
            if termino.lower() in linea.lower():
                coincidencias.append((i, linea))
        
        if coincidencias:
            print(f"\nEncontradas {len(coincidencias)} coincidencias:")
            print("-"*40)
            
            for i, (num_linea, linea) in enumerate(coincidencias[:20], 1):  # Mostrar máximo 20
                print(f"{i:2d}. Linea {num_linea}: {linea}")
            
            if len(coincidencias) > 20:
                print(f"... y {len(coincidencias) - 20} coincidencias mas")
        else:
            print("No se encontraron coincidencias")
    
    def extraer_secciones(self, contenido, nombre_archivo):
        """Extraer secciones específicas del archivo"""
        print(f"\nEXTRAER SECCIONES DE: {nombre_archivo}")
        print("-"*40)
        
        # Buscar secciones comunes
        secciones = {
            'migracion': ['migraci', 'migrar', 'migration'],
            'errores': ['error', 'fallo', 'problema', 'issue'],
            'mejoras': ['mejora', 'optimiz', 'mejorar', 'upgrade'],
            'instalacion': ['instalar', 'setup', 'configurar', 'instalacion'],
            'APIs': ['api', 'endpoint', 'request', 'response']
        }
        
        print("Secciones disponibles:")
        for i, (nombre, terminos) in enumerate(secciones.items(), 1):
            print(f"{i}. {nombre.title()}")
        
        try:
            seleccion = int(input("\nSeleccione seccion a extraer: ")) - 1
            secciones_lista = list(secciones.items())
            
            if 0 <= seleccion < len(secciones_lista):
                nombre_seccion, terminos = secciones_lista[seleccion]
                self.extraer_por_terminos(contenido, nombre_seccion, terminos, nombre_archivo)
            else:
                print("Seleccion invalida")
        except ValueError:
            print("Por favor ingrese un numero valido")
    
    def extraer_por_terminos(self, contenido, nombre_seccion, terminos, nombre_archivo):
        """Extraer contenido basado en términos específicos"""
        lineas = contenido.split('\n')
        lineas_extraidas = []
        
        for i, linea in enumerate(lineas, 1):
            for termino in terminos:
                if termino.lower() in linea.lower():
                    lineas_extraidas.append((i, linea))
                    break
        
        if lineas_extraidas:
            print(f"\nSECCION '{nombre_seccion.upper()}' EXTRAIDA:")
            print("-"*50)
            
            for num_linea, linea in lineas_extraidas[:30]:  # Mostrar máximo 30
                print(f"{num_linea:4d}: {linea}")
            
            if len(lineas_extraidas) > 30:
                print(f"\n... y {len(lineas_extraidas) - 30} lineas mas")
            
            # Guardar extracción
            guardar = input(f"\nGuardar extraccion en archivo? (s/n): ").strip().lower()
            if guardar == 's':
                self.guardar_extraccion(lineas_extraidas, nombre_seccion, nombre_archivo)
        else:
            print(f"No se encontraron lineas para la seccion '{nombre_seccion}'")
    
    def guardar_extraccion(self, lineas_extraidas, nombre_seccion, nombre_archivo):
        """Guardar extracción en archivo"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        nombre_archivo_salida = f"extraccion_{nombre_seccion}_{timestamp}.txt"
        
        try:
            with open(nombre_archivo_salida, 'w', encoding='utf-8') as f:
                f.write(f"EXTRACCION: {nombre_seccion.upper()}\n")
                f.write(f"ARCHIVO ORIGINAL: {nombre_archivo}\n")
                f.write(f"FECHA: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("="*60 + "\n\n")
                
                for num_linea, linea in lineas_extraidas:
                    f.write(f"{num_linea:4d}: {linea}\n")
            
            print(f"Extraccion guardada en: {nombre_archivo_salida}")
        except Exception as e:
            print(f"Error guardando extraccion: {e}")
    
    def buscar_en_chats(self):
        """Buscar texto en todos los chats"""
        print("\nBUSCAR EN TODOS LOS CHATS")
        print("-"*40)
        
        termino = input("Ingrese termino a buscar: ").strip()
        
        if not termino:
            print("Termino de busqueda vacio")
            return
        
        resultados = []
        
        for archivo in self.archivos_chat:
            try:
                with open(archivo['ruta'], 'r', encoding='utf-8') as f:
                    contenido = f.read()
                
                lineas = contenido.split('\n')
                coincidencias_archivo = []
                
                for i, linea in enumerate(lineas, 1):
                    if termino.lower() in linea.lower():
                        coincidencias_archivo.append((i, linea))
                
                if coincidencias_archivo:
                    resultados.append({
                        'archivo': archivo['nombre'],
                        'coincidencias': coincidencias_archivo
                    })
            
            except Exception as e:
                print(f"Error leyendo {archivo['nombre']}: {e}")
        
        if resultados:
            print(f"\nEncontradas coincidencias en {len(resultados)} archivo(s):")
            print("-"*50)
            
            for resultado in resultados:
                print(f"\n{resultado['archivo']} ({len(resultado['coincidencias'])} coincidencias):")
                for num_linea, linea in resultado['coincidencias'][:5]:  # Mostrar máximo 5 por archivo
                    print(f"   Linea {num_linea}: {linea}")
                
                if len(resultado['coincidencias']) > 5:
                    print(f"   ... y {len(resultado['coincidencias']) - 5} mas")
        else:
            print("No se encontraron coincidencias en ningun archivo")
    
    def extraer_conversaciones(self):
        """Extraer conversaciones específicas"""
        print("\nEXTRAER CONVERSACIONES ESPECIFICAS")
        print("-"*40)
        
        print("Tipos de conversaciones disponibles:")
        print("1. Migraciones")
        print("2. Errores y correcciones")
        print("3. Mejoras de rendimiento")
        print("4. Instalacion y configuracion")
        print("5. APIs y conectores")
        print("6. Personalizado")
        
        try:
            opcion = int(input("\nSeleccione tipo de conversacion: "))
            
            if opcion == 1:
                self.extraer_por_tipo('migracion', ['migraci', 'migrar', 'migration', 'disco', 'nube'])
            elif opcion == 2:
                self.extraer_por_tipo('errores', ['error', 'fallo', 'problema', 'issue', 'bug', 'fix'])
            elif opcion == 3:
                self.extraer_por_tipo('mejoras', ['mejora', 'optimiz', 'mejorar', 'upgrade', 'performance'])
            elif opcion == 4:
                self.extraer_por_tipo('instalacion', ['instalar', 'setup', 'configurar', 'instalacion', 'dependencias'])
            elif opcion == 5:
                self.extraer_por_tipo('APIs', ['api', 'endpoint', 'request', 'response', 'conector'])
            elif opcion == 6:
                terminos = input("Ingrese terminos separados por coma: ").split(',')
                terminos = [t.strip() for t in terminos if t.strip()]
                self.extraer_por_tipo('personalizado', terminos)
            else:
                print("Opcion invalida")
        except ValueError:
            print("Por favor ingrese un numero valido")
    
    def extraer_por_tipo(self, tipo, terminos):
        """Extraer conversaciones por tipo específico"""
        print(f"\nEXTRAYENDO CONVERSACIONES DE TIPO: {tipo.upper()}")
        print("-"*50)
        
        todas_las_lineas = []
        
        for archivo in self.archivos_chat:
            try:
                with open(archivo['ruta'], 'r', encoding='utf-8') as f:
                    contenido = f.read()
                
                lineas = contenido.split('\n')
                
                for i, linea in enumerate(lineas, 1):
                    for termino in terminos:
                        if termino.lower() in linea.lower():
                            todas_las_lineas.append({
                                'archivo': archivo['nombre'],
                                'linea': i,
                                'contenido': linea
                            })
                            break
            
            except Exception as e:
                print(f"Error procesando {archivo['nombre']}: {e}")
        
        if todas_las_lineas:
            print(f"Encontradas {len(todas_las_lineas)} lineas relacionadas con '{tipo}'")
            
            # Mostrar primeras 20
            print("\nPRIMERAS 20 LINEAS:")
            print("-"*40)
            
            for i, item in enumerate(todas_las_lineas[:20], 1):
                print(f"{i:2d}. [{item['archivo']}:{item['linea']}] {item['contenido']}")
            
            if len(todas_las_lineas) > 20:
                print(f"\n... y {len(todas_las_lineas) - 20} lineas mas")
            
            # Guardar extracción
            guardar = input(f"\nGuardar extraccion de '{tipo}'? (s/n): ").strip().lower()
            if guardar == 's':
                self.guardar_extraccion_completa(todas_las_lineas, tipo)
        else:
            print(f"No se encontraron lineas relacionadas con '{tipo}'")
    
    def guardar_extraccion_completa(self, lineas, tipo):
        """Guardar extracción completa"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        nombre_archivo = f"conversaciones_{tipo}_{timestamp}.txt"
        
        try:
            with open(nombre_archivo, 'w', encoding='utf-8') as f:
                f.write(f"CONVERSACIONES EXTRAIDAS: {tipo.upper()}\n")
                f.write(f"FECHA: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"TOTAL DE LINEAS: {len(lineas)}\n")
                f.write("="*60 + "\n\n")
                
                for item in lineas:
                    f.write(f"[{item['archivo']}:{item['linea']}] {item['contenido']}\n")
            
            print(f"Extraccion guardada en: {nombre_archivo}")
        except Exception as e:
            print(f"Error guardando extraccion: {e}")
    
    def crear_resumen(self):
        """Crear resumen de todos los chats"""
        print("\nCREANDO RESUMEN DE CHATS")
        print("-"*40)
        
        resumen = {
            'fecha_creacion': datetime.now().isoformat(),
            'total_archivos': len(self.archivos_chat),
            'archivos': [],
            'estadisticas': {
                'tamaño_total_mb': 0,
                'lineas_totales': 0,
                'terminos_comunes': {}
            }
        }
        
        terminos_comunes = {}
        
        for archivo in self.archivos_chat:
            try:
                with open(archivo['ruta'], 'r', encoding='utf-8') as f:
                    contenido = f.read()
                
                lineas = contenido.split('\n')
                resumen['estadisticas']['tamaño_total_mb'] += archivo['tamaño_mb']
                resumen['estadisticas']['lineas_totales'] += len(lineas)
                
                # Contar términos comunes
                palabras = re.findall(r'\b\w+\b', contenido.lower())
                for palabra in palabras:
                    if len(palabra) > 3:  # Solo palabras de más de 3 caracteres
                        terminos_comunes[palabra] = terminos_comunes.get(palabra, 0) + 1
                
                resumen['archivos'].append({
                    'nombre': archivo['nombre'],
                    'tamaño_mb': archivo['tamaño_mb'],
                    'lineas': len(lineas),
                    'fecha_modificacion': archivo['fecha_modificacion'].isoformat()
                })
            
            except Exception as e:
                print(f"Error procesando {archivo['nombre']}: {e}")
        
        # Top 20 términos más comunes
        resumen['estadisticas']['terminos_comunes'] = dict(
            sorted(terminos_comunes.items(), key=lambda x: x[1], reverse=True)[:20]
        )
        
        # Guardar resumen
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        nombre_resumen = f"resumen_chats_{timestamp}.json"
        
        try:
            with open(nombre_resumen, 'w', encoding='utf-8') as f:
                json.dump(resumen, f, indent=2, ensure_ascii=False)
            
            print(f"Resumen guardado en: {nombre_resumen}")
            
            # Mostrar resumen en pantalla
            print(f"\nRESUMEN DE CHATS:")
            print(f"   Total de archivos: {resumen['total_archivos']}")
            print(f"   Tamano total: {resumen['estadisticas']['tamaño_total_mb']:.2f} MB")
            print(f"   Lineas totales: {resumen['estadisticas']['lineas_totales']:,}")
            
            print(f"\nTERMINOS MAS COMUNES:")
            for i, (termino, frecuencia) in enumerate(list(resumen['estadisticas']['terminos_comunes'].items())[:10], 1):
                print(f"   {i:2d}. {termino}: {frecuencia}")
        
        except Exception as e:
            print(f"Error guardando resumen: {e}")
    
    def exportar_chat(self):
        """Exportar chat seleccionado en formato específico"""
        if not self.archivos_chat:
            print("No hay archivos de chat disponibles")
            return
        
        print("\nEXPORTAR CHAT")
        print("-"*30)
        
        for i, archivo in enumerate(self.archivos_chat, 1):
            print(f"{i}. {archivo['nombre']}")
        
        try:
            seleccion = int(input("\nSeleccione el numero del archivo: ")) - 1
            
            if 0 <= seleccion < len(self.archivos_chat):
                archivo_seleccionado = self.archivos_chat[seleccion]
                
                print("\nFormatos de exportacion:")
                print("1. TXT (texto plano)")
                print("2. HTML (formato web)")
                print("3. JSON (estructurado)")
                print("4. Markdown (formato documentacion)")
                
                formato = int(input("Seleccione formato: "))
                
                if formato in [1, 2, 3, 4]:
                    self.exportar_en_formato(archivo_seleccionado, formato)
                else:
                    print("Formato invalido")
            else:
                print("Numero invalido")
        except ValueError:
            print("Por favor ingrese un numero valido")
    
    def exportar_en_formato(self, archivo, formato):
        """Exportar archivo en formato específico"""
        try:
            with open(archivo['ruta'], 'r', encoding='utf-8') as f:
                contenido = f.read()
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            nombre_base = archivo['nombre'].replace('.md', '')
            
            if formato == 1:  # TXT
                nombre_archivo = f"{nombre_base}_exportado_{timestamp}.txt"
                with open(nombre_archivo, 'w', encoding='utf-8') as f:
                    f.write(contenido)
            
            elif formato == 2:  # HTML
                nombre_archivo = f"{nombre_base}_exportado_{timestamp}.html"
                html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Chat Exportado - {archivo['nombre']}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background-color: #f0f0f0; padding: 10px; border-radius: 5px; }}
        .content {{ white-space: pre-wrap; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Chat Exportado: {archivo['nombre']}</h1>
        <p>Fecha de exportacion: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p>Tamano original: {archivo['tamaño_mb']:.2f} MB</p>
    </div>
    <div class="content">{contenido}</div>
</body>
</html>"""
                with open(nombre_archivo, 'w', encoding='utf-8') as f:
                    f.write(html_content)
            
            elif formato == 3:  # JSON
                nombre_archivo = f"{nombre_base}_exportado_{timestamp}.json"
                data = {
                    'archivo_original': archivo['nombre'],
                    'fecha_exportacion': datetime.now().isoformat(),
                    'tamaño_original_mb': archivo['tamaño_mb'],
                    'contenido': contenido
                }
                with open(nombre_archivo, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
            
            elif formato == 4:  # Markdown
                nombre_archivo = f"{nombre_base}_exportado_{timestamp}.md"
                markdown_content = f"""# Chat Exportado: {archivo['nombre']}

**Fecha de exportacion:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Tamano original:** {archivo['tamaño_mb']:.2f} MB  
**Archivo original:** {archivo['ruta']}

---

{contenido}

---
*Exportado automaticamente por el Visualizador de Chats METGO 3D*
"""
                with open(nombre_archivo, 'w', encoding='utf-8') as f:
                    f.write(markdown_content)
            
            print(f"Chat exportado como: {nombre_archivo}")
        
        except Exception as e:
            print(f"Error exportando chat: {e}")

def main():
    """Función principal"""
    print("INICIANDO VISUALIZADOR DE CHATS EXPORTADOS")
    print("Sistema METGO 3D - Version 2.0")
    
    try:
        visualizador = VisualizadorChats()
        visualizador.mostrar_menu_principal()
    except KeyboardInterrupt:
        print("\n\nHasta luego!")
    except Exception as e:
        print(f"\nError inesperado: {e}")

if __name__ == "__main__":
    main()
