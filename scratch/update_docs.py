import os
import re

directory = r"d:\METGO_3D_Quillota_60GB\docs\comercial\spati"

replacements = [
    (r"#10b981", "#0ea5e9"),
    (r"SPATI", "VENTORA"),
    (r"\+56 9 XXXX XXXX", "+56 9 9931 9162"),
    (r"contacto@metgo3d\.com", "miguel.lucero@metgo3d.com"),
    (r"Santiago, Chile", "Viña del Mar, Chile (RUT 78.488.123-7)"),
    (r"Julio 2026", "Agosto 2026"),
    (r"(?i)minería", "operaciones portuarias"),
    (r"(?i)terreno complejo", "borde costero"),
    (r"(?i)alta montaña", "puertos"),
    (r"(?i)\bfaena\b", "terminal"),
    (r"(?i)\bfaenas\b", "terminales")
]

for filename in os.listdir(directory):
    filepath = os.path.join(directory, filename)
    if not os.path.isfile(filepath):
        continue
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        
    for old, new in replacements:
        content = re.sub(old, new, content)
        
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

print("Actualización completada.")
