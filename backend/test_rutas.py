#!/usr/bin/env python3
"""
Script para probar las rutas de países
"""
from app import create_app


def test_rutas():
    app = create_app()

    with app.app_context():
        from app.models import Pais

        print("=== VERIFICACIÓN DE PAÍSES EN BD ===")
        paises_db = Pais.query.all()
        print(f"Total países en BD: {len(paises_db)}")
        for p in paises_db[:3]:  # Mostrar primeros 3
            print(f"  - {p.nombre} ({p.codigo})")

        print("\n=== PRUEBA RUTA /api/crts/data/paises ===")
        try:
            with app.test_client() as client:
                response = client.get('/api/crts/data/paises')
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

        print("\n=== PRUEBA RUTA /api/paises/ ===")
        try:
            with app.test_client() as client:
                response = client.get('/api/paises/')
                print(f"Status: {response.status_code}")
                if response.status_code == 200:
                    data = response.get_json()
                    print(f"Total países devueltos: {len(data)}")
                    if data:
                        print(f"Primer país: {data[0]}")
                else:
                    print(f"Error: {response.get_data(as_text=True)}")
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    test_rutas()
