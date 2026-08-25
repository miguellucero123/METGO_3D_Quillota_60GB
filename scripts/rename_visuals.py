import os
import re

TARGET_EXTENSIONS = ('.html', '.vue', '.json', '.py', '.md')
SKIP_DIRS = {'.git', 'node_modules', '.venv', '__pycache__', 'dist', 'build'}

def is_visual_context(line):
    # Try to heuristically avoid replacing METGO_ (env vars) or metgo/ (paths)
    # But wait, we want to replace 'METGO' when it's just 'METGO' or 'METGO ' or ' METGO '.
    # Let's use regex to replace 'METGO' with 'METGO3D' only if it's NOT followed by an underscore or a slash or part of a variable name.
    # We'll allow replacing 'METGO' (uppercase), 'Metgo' (titlecase), but leave 'metgo' (lowercase) mostly alone unless in text.
    # Actually, the user says "textos visuales, titulo etc".
    pass

def main():
    root = 'd:/METGO_3D_Quillota_60GB'
    
    # We will look specifically in these paths to minimize risk
    target_paths = [
        os.path.join(root, 'frontend/vue/index.html'),
        os.path.join(root, 'frontend/vue/src'),
        os.path.join(root, 'streamlit_app.py'),
        os.path.join(root, 'backend/05_APIs_Externas')
    ]
    
    for tp in target_paths:
        if os.path.isfile(tp):
            process_file(tp)
        elif os.path.isdir(tp):
            for dirpath, dirnames, filenames in os.walk(tp):
                dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
                for f in filenames:
                    if f.endswith(TARGET_EXTENSIONS):
                        process_file(os.path.join(dirpath, f))

def process_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        original = content
        
        # Safe replaces:
        # Replace 'METGO' -> 'METGO3D' if not followed by underscore or inside a variable name (like METGO_API or METGO3D)
        # We use negative lookahead for _, 3, D, -, \.
        # \b ensures word boundary.
        # \B for cases where it's part of a word? No, we want exact word.
        
        # Replace METGO -> METGO3D
        content = re.sub(r'\bMETGO\b(?!3D|_|-)', 'METGO3D', content)
        
        # Replace Metgo -> Metgo3D
        content = re.sub(r'\bMetgo\b(?!3D|_|-)', 'Metgo3D', content)
        
        # We won't touch 'metgo' to avoid breaking paths (e.g. metgo/quillota) or variables (store.metgo)
        # unless it's clearly text.
        
        if content != original:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Updated: {filepath}")
            
    except Exception as e:
        print(f"Error {filepath}: {e}")

if __name__ == '__main__':
    main()
