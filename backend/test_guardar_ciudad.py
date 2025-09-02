#!/usr/bin/env python3
"""
Script para probar guardar una ciudad
"""
from app import create_app


def test_guardar_ciudad():
    app = create_app()

    with app.app_context():
        from app.models import Ciudad, Pais, db

        print("=== VERIFICACIÓN INICIAL ===")
        ciudades = Ciudad.query.all()
        paises = Pais.query.all()
        print(f"Ciudades en BD: {len(ciudades)}")
        print(f"Países en BD: {len(paises)}")

        if not paises:
            print("❌ No hay países para crear ciudades")
            return

        print("\n=== CREANDO CIUDAD DIRECTAMENTE ===")
        nueva_ciudad = Ciudad(
            nombre='Montevideo',
            pais_id=paises[0].id
        )
        db.session.add(nueva_ciudad)
        db.session.commit()
        print(f"Ciudad creada: {nueva_ciudad.nombre} (ID: {nueva_ciudad.id})")

        print("\n=== PRUEBA RUTA POST /api/ciudades/ ===")
        try:
            with app.test_client() as client:
                response = client.post('/api/ciudades/',
                                       json={
                                           'nombre': 'Encarnación',
                                           'pais_id': paises[0].id
                                       },
                                       content_type='application/json'
                                       )
                print(f"Status: {response.status_code}")
                if response.status_code == 201:
                    data = response.get_json()
                    print(f"Respuesta: {data}")
                else:
                    print(f"Error: {response.get_data(as_text=True)}")
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()

        print("\n=== VERIFICACIÓN FINAL ===")
        ciudades_final = Ciudad.query.all()
        print(f"Total ciudades finales: {len(ciudades_final)}")


if __name__ == "__main__":
    test_guardar_ciudad()
