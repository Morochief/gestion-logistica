#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script universal para lanzar Flask usando siempre el Python del venv local.
- Autodetecta venv en la carpeta actual y hasta 2 niveles arriba.
- Funciona en Linux/Mac/Windows.
- Soporta cualquier comando Flask CLI.
"""

import os
import sys
import re
from pathlib import Path


def find_venv_python():
    """
    Busca el Python ejecutable del venv desde la ruta actual o padres (hasta 2 niveles).
    """
    base_dirs = [
        Path.cwd(),
        Path.cwd().parent,
        Path.cwd().parent.parent
    ]
    for base in base_dirs:
        # Linux/Mac
        py = base / "venv" / "bin" / "python"
        if py.exists():
            return str(py)
        # Windows
        pyw = base / "venv" / "Scripts" / "python.exe"
        if pyw.exists():
            return str(pyw)
    return None


def main():
    # Si ya estamos ejecutando desde el venv, sigue normal
    if sys.prefix != sys.base_prefix:
        from flask.cli import main as flask_main
        sys.argv[0] = re.sub(r'(-script\.pyw|\.exe)?$', '', sys.argv[0])
        sys.exit(flask_main())

    # Si NO estamos en el venv, relanza usando el venv
    venv_python = find_venv_python()
    if not venv_python:
        print("❌ No se encontró un entorno virtual 'venv' en este proyecto.")
        sys.exit(1)
    # Relanza usando el Python del venv
    os.execv(venv_python, [venv_python] + sys.argv)


if __name__ == "__main__":
    main()
