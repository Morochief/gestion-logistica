#!/usr/bin/env python3
"""
Script completo para probar todas las rutas OPTIONS
"""
from app import create_app


def test_options_completo():
    app = create_app()

    print("=== PRUEBA COMPLETA DE RUTAS OPTIONS ===")

    rutas_a_probar = [
        '/api/paises',
        '/api/ciudades',
        '/api/crts/data/paises',
        '/api/crts/data/ciudades'
    ]

    for ruta in rutas_a_probar:
        print(f"\n--- Probando {ruta} ---")
        try:
            with app.test_client() as client:
                response = client.options(ruta,
                                          headers={
                                              'Origin': 'http://localhost:3000',
                                              'Access-Control-Request-Method': 'POST',
                                              'Access-Control-Request-Headers': 'Content-Type, Authorization'
                                          }
                                          )
                print(f"Status: {response.status_code}")

                if response.status_code == 200:
                    print("EXITO: Ruta OPTIONS funcionando")
                    # Mostrar headers CORS
                    cors_headers = {k: v for k, v in response.headers.items(
                    ) if k.startswith('Access-Control')}
                    print(f"Headers CORS encontrados: {len(cors_headers)}")
                    for header, value in cors_headers.items():
                        print(f"  {header}: {value}")
                else:
                    print(f"ERROR: Status {response.status_code}")
                    print(f"Response: {response.get_data(as_text=True)}")

        except Exception as e:
            print(f"ERROR en {ruta}: {e}")
            import traceback
            traceback.print_exc()

    print("\n=== PRUEBA POST A CIUDADES ===")
    try:
        with app.test_client() as client:
            response = client.post('/api/ciudades/',
                                   json={
                                       'nombre': 'Ciudad de Prueba',
                                       'pais_id': 1
                                   },
                                   content_type='application/json'
                                   )
            print(f"POST /api/ciudades/: Status {response.status_code}")
            if response.status_code == 201:
                print("EXITO: Ciudad creada correctamente")
            else:
                print(f"Response: {response.get_data(as_text=True)}")
    except Exception as e:
        print(f"ERROR en POST: {e}")


if __name__ == "__main__":
    test_options_completo()
