import subprocess
import os

os.chdir(r"D:\METGO_3D_Quillota_60GB\frontend\vue")
result = subprocess.run(["npx.cmd", "vite", "build"], capture_output=True, text=True)
print("--- STDOUT ---")
print(result.stdout)
print("--- STDERR ---")
print(result.stderr)
print("--- CODE ---")
print(result.returncode)
