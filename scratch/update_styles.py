import os
import re

components_dir = r"d:\METGO_3D_Quillota_60GB\frontend\vue\src\components"

replacements = [
    (r'stroke="#e5e7eb"', r'stroke="var(--color-border, #334155)"'),
    (r'stroke="#f3f4f6"', r'stroke="var(--color-surface, #1e293b)"'),
    (r'stroke="#fff"', r'stroke="var(--color-background, #0f172a)"'),
    (r'stroke="#ffffff"', r'stroke="var(--color-background, #0f172a)"'),
    (r'fill="#fff"', r'fill="var(--color-background, #0f172a)"'),
    (r'fill="#ffffff"', r'fill="var(--color-background, #0f172a)"'),
    (r'fill="#6b7280"', r'fill="var(--color-text-muted, #94a3b8)"'),
    (r'color:\s*#6b7280', r'color: var(--color-text-muted, #94a3b8)'),
    (r'background:\s*#ffffff', r'background: var(--color-surface, #1e293b)'),
    (r'background-color:\s*#ffffff', r'background-color: var(--color-surface, #1e293b)'),
    (r'background:\s*#f9fafb', r'background: var(--color-background, #0f172a)'),
    (r'border:\s*1px\s+solid\s+#e5e7eb', r'border: 1px solid var(--color-border, #334155)'),
    (r'border-top:\s*1px\s+solid\s+#e5e7eb', r'border-top: 1px solid var(--color-border, #334155)'),
    (r'border-bottom:\s*1px\s+solid\s+#e5e7eb', r'border-bottom: 1px solid var(--color-border, #334155)'),
    (r'border-color:\s*#e5e7eb', r'border-color: var(--color-border, #334155)'),
]

for root, _, files in os.walk(components_dir):
    for file in files:
        if file.endswith(".vue"):
            path = os.path.join(root, file)
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            
            new_content = content
            for old, new in replacements:
                new_content = re.sub(old, new, new_content)
                
            if new_content != content:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(new_content)
                print(f"Updated {file}")

print("Done.")
