#!/usr/bin/env python3
"""
Script para probar las correcciones de CORS
"""
from app import create_app


def test_cors():
    app = create_app()

    print("=== PRUEBA CORS - Solicitud OPTIONS ===")
    try:
        with app.test_client() as client:
            response = client.options('/api/paises',
                                      headers={
                                          'Origin': 'http://localhost:3000',
                                          'Access-Control-Request-Method': 'POST',
                                          'Access-Control-Request-Headers': 'Content-Type, Authorization'
                                      }
                                      )
            print(f"Status: {response.status_code}")
            print(f"Headers de respuesta:")
            for header, value in response.headers:
                if header.startswith('Access-Control'):
                    print(f"  {header}: {value}")

            if response.status_code == 200:
                print("✅ CORS funcionando correctamente")
            else:
                print(f"❌ Error en CORS: {response.status_code}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

    print("\n=== PRUEBA CORS - Solicitud POST ===")
    try:
        with app.test_client() as client:
            response = client.post('/api/paises',
                                   json={
                                       'nombre': 'Test CORS',
                                       'codigo': 'TC'
                                   },
                                   headers={
                                       'Origin': 'http://localhost:3000',
                                       'Content-Type': 'application/json'
                                   }
                                   )
            print(f"Status: {response.status_code}")
            if response.status_code == 201:
                print("✅ POST funcionando correctamente")
                data = response.get_json()
                print(f"País creado: {data}")
            else:
                error_data = response.get_json()
                print(f"Error: {error_data}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_cors()
