import os
import re
from pathlib import Path

files_to_update = [
    r"d:\METGO_3D_Quillota_60GB\streamlit_app.py",
    r"d:\METGO_3D_Quillota_60GB\frontend\dashboards\dashboard_meteorologico_profesional.py",
    r"d:\METGO_3D_Quillota_60GB\frontend\dashboards\dashboard_agricola_inteligente.py",
    r"d:\METGO_3D_Quillota_60GB\frontend\dashboards\dashboard_monitoreo_tiempo_real.py",
    r"d:\METGO_3D_Quillota_60GB\frontend\dashboards\dashboard_ia_ml_avanzado.py",
    r"d:\METGO_3D_Quillota_60GB\frontend\dashboards\dashboard_visualizaciones_avanzadas.py",
    r"d:\METGO_3D_Quillota_60GB\frontend\dashboards\dashboard_global_metricas.py",
    r"d:\METGO_3D_Quillota_60GB\frontend\dashboards\dashboard_agricultura_precision.py",
    r"d:\METGO_3D_Quillota_60GB\frontend\dashboards\dashboard_analisis_comparativo.py",
    r"d:\METGO_3D_Quillota_60GB\frontend\dashboards\dashboard_alertas_automaticas.py",
    r"d:\METGO_3D_Quillota_60GB\frontend\dashboards\dashboard_simple_optimizado.py",
    r"d:\METGO_3D_Quillota_60GB\frontend\dashboards\dashboard_unificado_diferenciado.py",
    r"d:\METGO_3D_Quillota_60GB\frontend\dashboards\dashboard_mobile_optimizado.py",
]

import_statement = "from metgo.streamlit_theme import bootstrap_dashboard, PLOTLY_CONFIG, plotly_layout\n"

for path_str in files_to_update:
    p = Path(path_str)
    if not p.exists():
        print(f"NOT FOUND: {path_str}")
        continue
        
    with open(p, "r", encoding="utf-8") as f:
        content = f.read()

    original = content
    
    # 1. Clean up old PLOTLY_CONFIG definitions if they exist.
    old_config_pattern = r'PLOTLY_CONFIG\s*=\s*\{\s*[\s\S]*?\}\s*(?:\n|$)'
    content = re.sub(old_config_pattern, '', content)
    
    # 2. Add imports if missing
    if "from metgo.streamlit_theme import" not in content and "import streamlit_theme" not in content:
        # insert after import streamlit as st
        if "import streamlit as st" in content:
            content = content.replace("import streamlit as st", "import streamlit as st\n" + import_statement)
        else:
            content = import_statement + content
            
    # if it has some imports but missing bootstrap_dashboard, etc, we'll try to just append them to the existing ones
    # A bit risky regex, let's just make sure we have them available.
    
    # 3. Ensure bootstrap_dashboard is called after st.set_page_config
    if "bootstrap_dashboard" not in content:
        page_config_match = re.search(r'st\.set_page_config\([^)]+\)', content, re.DOTALL)
        if page_config_match:
            insert_pos = page_config_match.end()
            # extract title if possible to pass to bootstrap
            title_match = re.search(r'page_title\s*=\s*["\']([^"\']+)["\']', page_config_match.group(0))
            title = title_match.group(1) if title_match else "Dashboard"
            bootstrap_call = f'\n\nbootstrap_dashboard("{title}", "METGO 3D")\n'
            content = content[:insert_pos] + bootstrap_call + content[insert_pos:]
        else:
            # no set_page_config, just add after imports
            pass
            
    # 4. Inject plotly_layout() into fig.update_layout calls.
    # We want to replace fig.update_layout(something) with fig.update_layout(**plotly_layout(height=400), something)
    # Be careful not to replace if already there.
    if "plotly_layout(" not in content:
        # Simple string replacement for common patterns:
        content = re.sub(r'fig\.update_layout\(\s*', 'fig.update_layout(**plotly_layout(height=400), ', content)
    
    if content != original:
        with open(p, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"UPDATED: {p.name}")
    else:
        print(f"NO CHANGES: {p.name}")

print("Done.")
