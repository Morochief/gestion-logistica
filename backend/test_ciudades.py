#!/usr/bin/env python3
"""
Script para probar las rutas de ciudades
"""
from app import create_app


def test_ciudades():
    app = create_app()

    with app.app_context():
        from app.models import Ciudad, Pais, db

        print("=== VERIFICACIÓN DE CIUDADES EN BD ===")
        ciudades_db = Ciudad.query.all()
        print(f"Total ciudades en BD: {len(ciudades_db)}")
        for c in ciudades_db[:3]:  # Mostrar primeras 3
            print(f"  - {c.nombre} (País ID: {c.pais_id})")

        # Si no hay ciudades, crear algunas
        if len(ciudades_db) == 0:
            print("\n=== CREANDO CIUDADES DE EJEMPLO ===")
            paises = Pais.query.limit(3).all()
            if paises:
                print(f"Creando ciudades para {len(paises)} países...")

                ciudades_ejemplo = [
                    {'nombre': 'Asunción', 'pais_id': paises[0].id},
                    {'nombre': 'Ciudad del Este', 'pais_id': paises[0].id},
                    {'nombre': 'Buenos Aires', 'pais_id': paises[1].id if len(
                        paises) > 1 else paises[0].id},
                    {'nombre': 'São Paulo', 'pais_id': paises[2].id if len(
                        paises) > 2 else paises[0].id},
                ]

                for ciudad_data in ciudades_ejemplo:
                    ciudad = Ciudad(
                        nombre=ciudad_data['nombre'],
                        pais_id=ciudad_data['pais_id']
                    )
                    db.session.add(ciudad)
                    print(f"  Agregada: {ciudad.nombre}")

                db.session.commit()
                print(f"✅ {len(ciudades_ejemplo)} ciudades creadas")

                # Verificar nuevamente
                ciudades_db = Ciudad.query.all()
                print(f"Total ciudades después de crear: {len(ciudades_db)}")
            else:
                print("❌ No hay países para crear ciudades")

        print("\n=== PRUEBA RUTA /api/crts/data/ciudades ===")
        try:
            with app.test_client() as client:
                response = client.get('/api/crts/data/ciudades')
                print(f"Status: {response.status_code}")
                if response.status_code == 200:
                    data = response.get_json()
                    print(f"Respuesta: {data}")
                else:
                    print(f"Error: {response.get_data(as_text=True)}")
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()

        print("\n=== PRUEBA RUTA /api/ciudades/ ===")
        try:
            with app.test_client() as client:
                response = client.get('/api/ciudades/')
                print(f"Status: {response.status_code}")
                if response.status_code == 200:
                    data = response.get_json()
                    print(f"Total ciudades devueltas: {len(data)}")
                    if data:
                        print(f"Primer ciudad: {data[0]}")
                else:
                    print(f"Error: {response.get_data(as_text=True)}")
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    test_ciudades()
