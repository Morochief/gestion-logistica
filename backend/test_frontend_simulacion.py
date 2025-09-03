#!/usr/bin/env python3
"""
Script para simular exactamente lo que hace el frontend
"""
import json


def test_frontend_simulation():
    print("=== SIMULACIÓN DEL FRONTEND ===")

    # Simular la llamada fetch del frontend
    url = "http://localhost:5000/api/paises"
    method = "POST"
    data = {
        'nombre': 'País de Prueba',
        'codigo': 'ZZ'
    }

    print(f"URL: {url}")
    print(f"Method: {method}")
    print(f"Data: {json.dumps(data, indent=2)}")

    # Simular headers que envía el frontend
    headers = {
        'Content-Type': 'application/json',
        # Nota: El frontend también debería enviar Authorization header si hay token
    }

    print(f"Headers: {json.dumps(headers, indent=2)}")

    print("\n=== PRUEBA CON PYTHON REQUESTS ===")
    try:
        import requests

        response = requests.post(url, json=data, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers:")
        for header, value in response.headers.items():
            if header.startswith('Access-Control') or header in ['Content-Type', 'Location']:
                print(f"  {header}: {value}")

        if response.status_code == 201:
            print("✅ EXITO: País creado correctamente")
            print(f"Response: {response.json()}")
        elif response.status_code == 409:
            print("⚠️  Código duplicado (esperado si ZZ ya existe)")
            print(f"Response: {response.json()}")
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")

    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión: {e}")
    except ImportError:
        print("❌ requests no instalado. Instalar con: pip install requests")


if __name__ == "__main__":
    test_frontend_simulation()
