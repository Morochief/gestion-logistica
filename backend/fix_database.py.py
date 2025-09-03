import sqlite3
import os

# Cambiar al directorio correcto del proyecto
db_path = os.path.join('instance', 'logistica.db')

if not os.path.exists(db_path):
    print(f"Error: No se encuentra la base de datos en {db_path}")
    exit()

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=== VERIFICACIÓN Y ACTUALIZACIÓN DE ESQUEMA ===")

# 1. Limpiar tablas temporales de Alembic
cursor.execute(
    "SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '_alembic_tmp_%'")
temp_tables = cursor.fetchall()
if temp_tables:
    print("Eliminando tablas temporales de Alembic...")
    for table in temp_tables:
        cursor.execute(f'DROP TABLE IF EXISTS {table[0]}')
        print(f"  - Eliminada: {table[0]}")

# 2. Verificar y agregar columnas a la tabla usuarios
print("\n--- Tabla usuarios ---")
cursor.execute('PRAGMA table_info(usuarios)')
user_columns = [row[1] for row in cursor.fetchall()]
print(f"Columnas actuales: {user_columns}")

if 'email' not in user_columns:
    cursor.execute('ALTER TABLE usuarios ADD COLUMN email VARCHAR(120)')
    print("✓ Columna 'email' agregada")

if 'ultimo_login' not in user_columns:
    cursor.execute('ALTER TABLE usuarios ADD COLUMN ultimo_login DATETIME')
    print("✓ Columna 'ultimo_login' agregada")

if 'refresh_token' not in user_columns:
    cursor.execute(
        'ALTER TABLE usuarios ADD COLUMN refresh_token VARCHAR(512)')
    print("✓ Columna 'refresh_token' agregada")

# 3. Verificar y agregar columnas a la tabla crts
print("\n--- Tabla crts ---")
cursor.execute('PRAGMA table_info(crts)')
crt_columns = [row[1] for row in cursor.fetchall()]
print(f"Columnas actuales en crts: {len(crt_columns)} columnas")

if 'firma_remitente' not in crt_columns:
    cursor.execute('ALTER TABLE crts ADD COLUMN firma_remitente VARCHAR(200)')
    print("✓ Columna 'firma_remitente' agregada")

if 'firma_transportador' not in crt_columns:
    cursor.execute(
        'ALTER TABLE crts ADD COLUMN firma_transportador VARCHAR(200)')
    print("✓ Columna 'firma_transportador' agregada")

if 'firma_destinatario' not in crt_columns:
    cursor.execute(
        'ALTER TABLE crts ADD COLUMN firma_destinatario VARCHAR(200)')
    print("✓ Columna 'firma_destinatario' agregada")

# 4. Confirmar cambios
conn.commit()
conn.close()

print("\n=== ACTUALIZACIÓN COMPLETADA ===")
print("Ahora ejecuta: flask db upgrade")
