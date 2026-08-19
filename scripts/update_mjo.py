import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__)))
from wp_apply_mg_page import wrap, request

mjo_html = """
<div style="width: 100%; height: 85vh; display: flex; flex-direction: column; background: #0d1117;">
  <iframe src="https://metgo-mjo-chile.pages.dev/" style="width: 100%; flex-grow: 1; border: none;" title="MJO Chile"></iframe>
</div>
"""

try:
    request('POST', '/wp/v2/pages/216', {
        'title': 'MJO Chile', 
        'content': wrap(mjo_html, active='mjo_chile'), 
        'status': 'publish'
    })
    print("Página MJO Chile (216) actualizada correctamente con el iframe.")
except Exception as e:
    print(f"Error: {e}")
