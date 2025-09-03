import sqlite3
import os

# Conectar a la base
conn = sqlite3.connect('instance/logistica.db')
cursor = conn.cursor()

# Eliminar la tabla temporal
cursor.execute('DROP TABLE IF EXISTS _alembic_tmp_transportadoras')

# Confirmar cambios
conn.commit()
conn.close()

print("Tabla temporal eliminada")