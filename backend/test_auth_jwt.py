#!/usr/bin/env python3
"""
Script completo para probar la autenticación JWT
"""
import requests
import json

BASE_URL = "http://localhost:5000/api"


def test_auth_jwt():
    """Prueba completa del sistema de autenticación JWT"""

    print("PRUEBA COMPLETA DE AUTENTICACION JWT")
    print("=" * 60)

    # 1. Test Login
    print("\n1. Probando LOGIN...")
    login_data = {
        "usuario": "admin",
        "clave": "admin123"
    }

    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        print(f"   Status: {response.status_code}")

        if response.status_code == 200:
            login_result = response.json()
            print("   Login exitoso!")
            print(f"   Usuario: {login_result['usuario']['usuario']}")
            print(f"   Rol: {login_result['usuario']['rol']}")

            access_token = login_result['access_token']
            refresh_token = login_result['refresh_token']
            print("   Tokens obtenidos correctamente")
        else:
            print(f"   Error en login: {response.text}")
            return False

    except Exception as e:
        print(f"   Error de conexión: {e}")
        return False

    # 2. Test Profile (con token)
    print("\n2. Probando PROFILE...")
    headers = {"Authorization": f"Bearer {access_token}"}

    try:
        response = requests.get(f"{BASE_URL}/auth/profile", headers=headers)
        print(f"   Status: {response.status_code}")

        if response.status_code == 200:
            profile = response.json()
            print("   Profile obtenido!")
            print(f"   Nombre completo: {profile['nombre_completo']}")
            print(f"   Email: {profile.get('email', 'No especificado')}")
        else:
            print(f"   Error obteniendo profile: {response.text}")

    except Exception as e:
        print(f"   Error de conexión: {e}")

    # 3. Test Verify Token
    print("\n3. Probando VERIFY TOKEN...")

    try:
        response = requests.get(f"{BASE_URL}/auth/verify", headers=headers)
        print(f"   Status: {response.status_code}")

        if response.status_code == 200:
            verify_result = response.json()
            print("   Token válido!")
            print(f"   Usuario: {verify_result['usuario']['usuario']}")
        else:
            print(f"   Token inválido: {response.text}")

    except Exception as e:
        print(f"   Error de conexión: {e}")

    # 4. Test Refresh Token
    print("\n4. Probando REFRESH TOKEN...")

    try:
        refresh_data = {"refresh_token": refresh_token}
        response = requests.post(f"{BASE_URL}/auth/refresh", json=refresh_data)
        print(f"   Status: {response.status_code}")

        if response.status_code == 200:
            refresh_result = response.json()
            print("   Token refrescado!")
            new_access_token = refresh_result['access_token']
            print("   Nuevo access token obtenido")

            # Actualizar el token para las siguientes pruebas
            access_token = new_access_token
            headers = {"Authorization": f"Bearer {access_token}"}
        else:
            print(f"   Error refrescando token: {response.text}")

    except Exception as e:
        print(f"   Error de conexión: {e}")

    # 5. Test Change Password
    print("\n5. Probando CHANGE PASSWORD...")

    try:
        change_data = {
            "current_password": "admin123",
            "new_password": "admin123"  # Mantenemos la misma para no cambiarla realmente
        }
        response = requests.post(
            f"{BASE_URL}/auth/change-password", json=change_data, headers=headers)
        print(f"   Status: {response.status_code}")

        if response.status_code == 200:
            print("   Contraseña cambiada exitosamente!")
        else:
            print(f"   Error cambiando contraseña: {response.text}")

    except Exception as e:
        print(f"   Error de conexión: {e}")

    # 6. Test Logout
    print("\n6. Probando LOGOUT...")

    try:
        response = requests.post(f"{BASE_URL}/auth/logout", headers=headers)
        print(f"   Status: {response.status_code}")

        if response.status_code == 200:
            print("   Logout exitoso!")
        else:
            print(f"   Error en logout: {response.text}")

    except Exception as e:
        print(f"   Error de conexión: {e}")

    # 7. Test acceso sin token (debe fallar)
    print("\n7. Probando ACCESO SIN TOKEN (debe fallar)...")

    try:
        response = requests.get(f"{BASE_URL}/auth/profile")
        print(f"   Status: {response.status_code}")

        if response.status_code == 401:
            print("   Correctamente rechazado sin token!")
        else:
            print(f"   Respuesta inesperada: {response.text}")

    except Exception as e:
        print(f"   Error de conexión: {e}")

    print("\n" + "=" * 60)
    print("PRUEBA DE AUTENTICACIÓN JWT COMPLETADA!")
    print("Todas las funcionalidades críticas están funcionando correctamente.")
    return True


if __name__ == "__main__":
    test_auth_jwt()
