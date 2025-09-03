#!/usr/bin/env python3
"""
Script para crear un usuario administrador por defecto
"""
from app import create_app
from app.models import Usuario, db
from app.utils.auth import hash_password


def crear_admin():
    """Crear usuario administrador por defecto"""
    app = create_app()

    with app.app_context():
        # Verificar si ya existe un admin
        admin_existente = Usuario.query.filter_by(rol='admin').first()

        if admin_existente:
            print(f"Ya existe un administrador: {admin_existente.usuario}")
            return

        # Crear administrador por defecto
        admin_data = {
            'usuario': 'admin',
            'clave': 'admin123',
            'nombre_completo': 'Administrador del Sistema',
            'email': 'admin@sistema.com',
            'rol': 'admin',
            'estado': 'activo'
        }

        hashed_password = hash_password(admin_data['clave'])

        admin = Usuario(
            usuario=admin_data['usuario'],
            clave_hash=hashed_password,
            nombre_completo=admin_data['nombre_completo'],
            email=admin_data['email'],
            rol=admin_data['rol'],
            estado=admin_data['estado']
        )

        try:
            db.session.add(admin)
            db.session.commit()

            print("Administrador creado exitosamente!")
            print(f"   Usuario: {admin.usuario}")
            print(f"   Contrasena: {admin_data['clave']}")
            print(f"   Email: {admin.email}")
            print("   Rol: admin")
            print("\nCredenciales de acceso:")
            print("   Usuario: admin")
            print("   Contrasena: admin123")

        except Exception as e:
            db.session.rollback()
            print(f"Error creando administrador: {e}")


if __name__ == "__main__":
    crear_admin()
