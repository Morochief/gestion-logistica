#!/usr/bin/env python3
"""
Script para probar guardar un país con código nuevo
"""
from app import create_app


def test_pais_nuevo():
    app = create_app()

    with app.app_context():
        from app.models import Pais

        print("=== CÓDIGOS DE PAÍSES EXISTENTES ===")
        paises = Pais.query.all()
        for p in paises:
            print(f"  {p.nombre}: {p.codigo}")

        print("\n=== PRUEBA CON CÓDIGO NUEVO ===")
        try:
            with app.test_client() as client:
                response = client.post('/api/paises/',
                                       json={
                                           'nombre': 'Perú',
                                           'codigo': 'PE'
                                       },
                                       content_type='application/json'
                                       )
                print(f"Status: {response.status_code}")
                if response.status_code == 201:
                    data = response.get_json()
                    print(f"✅ País creado exitosamente: {data}")
                else:
                    print(f"❌ Error: {response.get_data(as_text=True)}")
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()

        print("\n=== VERIFICACIÓN FINAL ===")
        paises_final = Pais.query.all()
        print(f"Total países: {len(paises_final)}")


if __name__ == "__main__":
    test_pais_nuevo()
