#!/usr/bin/env python3
"""
Script para arreglar la base de datos agregando columnas faltantes
"""
import sqlite3
import os


def fix_database():
    """Agregar columnas faltantes a la tabla usuarios"""
    db_path = os.path.join(os.path.dirname(__file__),
                           'instance', 'logistica.db')

    if not os.path.exists(db_path):
        print(f"❌ Base de datos no encontrada en: {db_path}")
        return

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Verificar columnas existentes
        cursor.execute("PRAGMA table_info(usuarios)")
        columns = [row[1] for row in cursor.fetchall()]
        print(f"Columnas existentes en usuarios: {columns}")

        # Agregar columnas faltantes
        if 'email' not in columns:
            cursor.execute(
                "ALTER TABLE usuarios ADD COLUMN email VARCHAR(120)")
            print("✅ Columna 'email' agregada")

        if 'ultimo_login' not in columns:
            cursor.execute(
                "ALTER TABLE usuarios ADD COLUMN ultimo_login DATETIME")
            print("✅ Columna 'ultimo_login' agregada")

        if 'refresh_token' not in columns:
            cursor.execute(
                "ALTER TABLE usuarios ADD COLUMN refresh_token VARCHAR(512)")
            print("✅ Columna 'refresh_token' agregada")

        # Agregar columna firma_remitente a crts si no existe
        cursor.execute("PRAGMA table_info(crts)")
        crt_columns = [row[1] for row in cursor.fetchall()]

        if 'firma_remitente' not in crt_columns:
            cursor.execute(
                "ALTER TABLE crts ADD COLUMN firma_remitente VARCHAR(200)")
            print("✅ Columna 'firma_remitente' agregada a crts")

        if 'firma_transportador' not in crt_columns:
            cursor.execute(
                "ALTER TABLE crts ADD COLUMN firma_transportador VARCHAR(200)")
            print("✅ Columna 'firma_transportador' agregada a crts")

        if 'firma_destinatario' not in crt_columns:
            cursor.execute(
                "ALTER TABLE crts ADD COLUMN firma_destinatario VARCHAR(200)")
            print("✅ Columna 'firma_destinatario' agregada a crts")

        conn.commit()
        conn.close()

        print("✅ Base de datos actualizada exitosamente!")

    except Exception as e:
        print(f"❌ Error actualizando base de datos: {e}")
        if 'conn' in locals():
            conn.close()


if __name__ == "__main__":
    fix_database()
