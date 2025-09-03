#!/usr/bin/env python3
"""
Script para probar guardar un país
"""
from app import create_app


def test_guardar_pais():
    app = create_app()

    with app.app_context():
        from app.models import Pais, db

        print("=== VERIFICACIÓN INICIAL ===")
        paises_existentes = Pais.query.all()
        print(f"Países existentes: {len(paises_existentes)}")
        for p in paises_existentes[:3]:
            print(f"  - {p.nombre} ({p.codigo})")

        print("\n=== CREANDO PAÍS DIRECTAMENTE ===")
        nuevo_pais = Pais(
            nombre='México',
            codigo='MX'
        )
        db.session.add(nuevo_pais)
        db.session.commit()
        print(
            f"País creado: {nuevo_pais.nombre} ({nuevo_pais.codigo}) - ID: {nuevo_pais.id}")

        print("\n=== PRUEBA RUTA POST /api/paises/ ===")
        try:
            with app.test_client() as client:
                response = client.post('/api/paises/',
                                       json={
                                           'nombre': 'Colombia',
                                           'codigo': 'CO'
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
        paises_final = Pais.query.all()
        print(f"Total países finales: {len(paises_final)}")


if __name__ == "__main__":
    test_guardar_pais()
