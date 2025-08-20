import os

for root, dirs, files in os.walk("."):
    for dir in dirs:
        if dir == "__pycache__":
            path = os.path.join(root, dir)
            print(f"Eliminando carpeta: {path}")
            os.system(f"rmdir /S /Q \"{path}\"")  # en Windows
    for file in files:
        if file.endswith(".pyc"):
            file_path = os.path.join(root, file)
            print(f"Eliminando archivo: {file_path}")
            os.remove(file_path)

print("✔ Cache de Python eliminada. Ahora ejecuta:")
print("    flask run")
