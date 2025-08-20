import os

# Carpetas/archivos a ignorar completamente
IGNORAR = {
    '.venv', 'venv', 'env', 'env.bak', 'node_modules', '__pycache__', '.git', 
    '.pytest_cache', '.mypy_cache', '.idea', '.vscode', 'migrations',
    '.DS_Store', '.next', '.sass-cache', '.cache'
}
# Extensiones a ignorar
IGNORAR_EXT = {
    '.pyc', '.pyo', '.log'
}

def mostrar_estructura(ruta, prefijo=''):
    items = []
    for nombre in sorted(os.listdir(ruta)):
        if nombre in IGNORAR:
            continue
        if any(nombre.endswith(ext) for ext in IGNORAR_EXT):
            continue
        ruta_completa = os.path.join(ruta, nombre)
        items.append((nombre, ruta_completa, os.path.isdir(ruta_completa)))
    for i, (nombre, ruta_completa, es_dir) in enumerate(items):
        es_ultimo = (i == len(items) - 1)
        icono = '└── ' if es_ultimo else '├── '
        sufijo = '/' if es_dir else ''
        print(f"{prefijo}{icono}{nombre}{sufijo}")
        if es_dir:
            mostrar_estructura(ruta_completa, prefijo + ('    ' if es_ultimo else '│   '))

if __name__ == '__main__':
    print('Estructura del proyecto (limpia):\n')
    mostrar_estructura(os.getcwd())
