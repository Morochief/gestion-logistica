#!/usr/bin/env python3
"""
Script completo para probar operaciones CRUD de todas las entidades
"""
import requests
import json

BASE_URL = "http://localhost:5000/api"

# Token de autenticación (se obtendrá del login)
auth_token = None


def login_and_get_token():
    """Obtener token de autenticación"""
    global auth_token
    login_data = {
        "usuario": "admin",
        "clave": "admin123"
    }

    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        if response.status_code == 200:
            login_result = response.json()
            auth_token = login_result['access_token']
            print("Login exitoso - Token obtenido")
            return True
        else:
            print(f"Error en login: {response.text}")
            return False
    except Exception as e:
        print(f"Error de conexión en login: {e}")
        return False


def get_headers():
    """Obtener headers con token de autenticación"""
    return {"Authorization": f"Bearer {auth_token}"}


def test_paises_crud():
    """Probar operaciones CRUD para países"""
    print("\n" + "="*50)
    print("PRUEBA CRUD - PAISES")
    print("="*50)

    headers = get_headers()

    # 1. CREATE - Crear país
    print("\n1. CREATE - Creando país...")
    pais_data = {
        "nombre": "Test País",
        "codigo": "TP"
    }

    try:
        response = requests.post(
            f"{BASE_URL}/paises/", json=pais_data, headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 201:
            pais_creado = response.json()
            pais_id = pais_creado['id']
            print(f"   País creado exitosamente (ID: {pais_id})")
        else:
            print(f"   Error: {response.text}")
            return False
    except Exception as e:
        print(f"   Error: {e}")
        return False

    # 2. READ - Obtener todos los países
    print("\n2. READ - Obteniendo todos los países...")
    try:
        response = requests.get(f"{BASE_URL}/paises/", headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            paises = response.json()
            print(f"   Total países: {len(paises)}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")

    # 3. UPDATE - Actualizar país
    print("\n3. UPDATE - Actualizando país...")
    update_data = {
        "nombre": "Test País Actualizado",
        "codigo": "TPA"
    }

    try:
        response = requests.put(
            f"{BASE_URL}/paises/{pais_id}", json=update_data, headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   País actualizado correctamente")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")

    # 4. DELETE - Eliminar país
    print("\n4. DELETE - Eliminando país...")
    try:
        response = requests.delete(
            f"{BASE_URL}/paises/{pais_id}", headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   País eliminado correctamente")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")

    return True


def test_monedas_crud():
    """Probar operaciones CRUD para monedas"""
    print("\n" + "="*50)
    print("PRUEBA CRUD - MONEDAS")
    print("="*50)

    headers = get_headers()

    # 1. CREATE - Crear moneda
    print("\n1. CREATE - Creando moneda...")
    moneda_data = {
        "codigo": "TST",
        "nombre": "Moneda de Test",
        "simbolo": "T$"
    }

    try:
        response = requests.post(
            f"{BASE_URL}/monedas/", json=moneda_data, headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 201:
            moneda_creada = response.json()
            moneda_id = moneda_creada['id']
            print(f"   Moneda creada exitosamente (ID: {moneda_id})")
        else:
            print(f"   Error: {response.text}")
            return False
    except Exception as e:
        print(f"   Error: {e}")
        return False

    # 2. READ - Obtener todas las monedas
    print("\n2. READ - Obteniendo todas las monedas...")
    try:
        response = requests.get(f"{BASE_URL}/monedas/", headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            monedas = response.json()
            print(f"   Total monedas: {len(monedas)}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")

    # 3. UPDATE - Actualizar moneda
    print("\n3. UPDATE - Actualizando moneda...")
    update_data = {
        "codigo": "TST",
        "nombre": "Moneda de Test Actualizada",
        "simbolo": "TA$"
    }

    try:
        response = requests.put(
            f"{BASE_URL}/monedas/{moneda_id}", json=update_data, headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   Moneda actualizada correctamente")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")

    # 4. DELETE - Eliminar moneda
    print("\n4. DELETE - Eliminando moneda...")
    try:
        response = requests.delete(
            f"{BASE_URL}/monedas/{moneda_id}", headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   Moneda eliminada correctamente")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")

    return True


def test_remitentes_crud():
    """Probar operaciones CRUD para remitentes"""
    print("\n" + "="*50)
    print("PRUEBA CRUD - REMITENTES")
    print("="*50)

    headers = get_headers()

    # Primero necesitamos obtener una ciudad existente
    print("\nObteniendo ciudad para remitente...")
    try:
        response = requests.get(f"{BASE_URL}/ciudades/", headers=headers)
        if response.status_code == 200:
            ciudades = response.json()
            if ciudades:
                ciudad_id = ciudades[0]['id']
                print(f"   Usando ciudad ID: {ciudad_id}")
            else:
                print("   No hay ciudades disponibles")
                return False
        else:
            print(f"   Error obteniendo ciudades: {response.text}")
            return False
    except Exception as e:
        print(f"   Error: {e}")
        return False

    # 1. CREATE - Crear remitente
    print("\n1. CREATE - Creando remitente...")
    remitente_data = {
        "tipo_documento": "CI",
        "numero_documento": "12345678",
        "nombre": "Test Remitente",
        "direccion": "Dirección de Test",
        "ciudad_id": ciudad_id
    }

    try:
        response = requests.post(
            f"{BASE_URL}/remitentes/", json=remitente_data, headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 201:
            remitente_creado = response.json()
            remitente_id = remitente_creado['id']
            print(f"   Remitente creado exitosamente (ID: {remitente_id})")
        else:
            print(f"   Error: {response.text}")
            return False
    except Exception as e:
        print(f"   Error: {e}")
        return False

    # 2. READ - Obtener todos los remitentes
    print("\n2. READ - Obteniendo todos los remitentes...")
    try:
        response = requests.get(f"{BASE_URL}/remitentes/", headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            remitentes = response.json()
            print(f"   Total remitentes: {len(remitentes)}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")

    # 3. UPDATE - Actualizar remitente
    print("\n3. UPDATE - Actualizando remitente...")
    update_data = {
        "tipo_documento": "CI",
        "numero_documento": "87654321",
        "nombre": "Test Remitente Actualizado",
        "direccion": "Dirección Actualizada",
        "ciudad_id": ciudad_id
    }

    try:
        response = requests.put(
            f"{BASE_URL}/remitentes/{remitente_id}", json=update_data, headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   Remitente actualizado correctamente")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")

    # 4. DELETE - Eliminar remitente
    print("\n4. DELETE - Eliminando remitente...")
    try:
        response = requests.delete(
            f"{BASE_URL}/remitentes/{remitente_id}", headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   Remitente eliminado correctamente")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")

    return True


def test_transportadoras_crud():
    """Probar operaciones CRUD para transportadoras"""
    print("\n" + "="*50)
    print("PRUEBA CRUD - TRANSPORTADORAS")
    print("="*50)

    headers = get_headers()

    # Primero necesitamos obtener una ciudad existente
    print("\nObteniendo ciudad para transportadora...")
    try:
        response = requests.get(f"{BASE_URL}/ciudades/", headers=headers)
        if response.status_code == 200:
            ciudades = response.json()
            if ciudades:
                ciudad_id = ciudades[0]['id']
                print(f"   Usando ciudad ID: {ciudad_id}")
            else:
                print("   No hay ciudades disponibles")
                return False
        else:
            print(f"   Error obteniendo ciudades: {response.text}")
            return False
    except Exception as e:
        print(f"   Error: {e}")
        return False

    # 1. CREATE - Crear transportadora
    print("\n1. CREATE - Creando transportadora...")
    transportadora_data = {
        "codigo": "TEST001",
        "codigo_interno": "T001",
        "nombre": "Transportadora de Test",
        "direccion": "Dirección de Test",
        "ciudad_id": ciudad_id,
        "tipo_documento": "RUC",
        "numero_documento": "123456789",
        "telefono": "0987654321"
    }

    try:
        response = requests.post(
            f"{BASE_URL}/transportadoras/", json=transportadora_data, headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 201:
            transportadora_creada = response.json()
            transportadora_id = transportadora_creada['id']
            print(
                f"   Transportadora creada exitosamente (ID: {transportadora_id})")
        else:
            print(f"   Error: {response.text}")
            return False
    except Exception as e:
        print(f"   Error: {e}")
        return False

    # 2. READ - Obtener todas las transportadoras
    print("\n2. READ - Obteniendo todas las transportadoras...")
    try:
        response = requests.get(
            f"{BASE_URL}/transportadoras/", headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            transportadoras = response.json()
            print(f"   Total transportadoras: {len(transportadoras)}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")

    # 3. UPDATE - Actualizar transportadora
    print("\n3. UPDATE - Actualizando transportadora...")
    update_data = {
        "codigo": "TEST002",
        "codigo_interno": "T002",
        "nombre": "Transportadora de Test Actualizada",
        "direccion": "Dirección Actualizada",
        "ciudad_id": ciudad_id,
        "tipo_documento": "RUC",
        "numero_documento": "987654321",
        "telefono": "0123456789"
    }

    try:
        response = requests.put(
            f"{BASE_URL}/transportadoras/{transportadora_id}", json=update_data, headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   Transportadora actualizada correctamente")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")

    # 4. DELETE - Eliminar transportadora
    print("\n4. DELETE - Eliminando transportadora...")
    try:
        response = requests.delete(
            f"{BASE_URL}/transportadoras/{transportadora_id}", headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   Transportadora eliminada correctamente")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")

    return True


def test_ciudades_crud():
    """Probar operaciones CRUD para ciudades"""
    print("\n" + "="*50)
    print("PRUEBA CRUD - CIUDADES")
    print("="*50)

    headers = get_headers()

    # Primero necesitamos obtener un país existente
    print("\nObteniendo país para ciudad...")
    try:
        response = requests.get(f"{BASE_URL}/paises/", headers=headers)
        if response.status_code == 200:
            paises = response.json()
            if paises:
                pais_id = paises[0]['id']
                print(f"   Usando país ID: {pais_id}")
            else:
                print("   No hay países disponibles")
                return False
        else:
            print(f"   Error obteniendo países: {response.text}")
            return False
    except Exception as e:
        print(f"   Error: {e}")
        return False

    # 1. CREATE - Crear ciudad
    print("\n1. CREATE - Creando ciudad...")
    ciudad_data = {
        "nombre": "Ciudad de Test",
        "pais_id": pais_id
    }

    try:
        response = requests.post(
            f"{BASE_URL}/ciudades/", json=ciudad_data, headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 201:
            ciudad_creada = response.json()
            ciudad_id = ciudad_creada['id']
            print(f"   Ciudad creada exitosamente (ID: {ciudad_id})")
        else:
            print(f"   Error: {response.text}")
            return False
    except Exception as e:
        print(f"   Error: {e}")
        return False

    # 2. READ - Obtener todas las ciudades
    print("\n2. READ - Obteniendo todas las ciudades...")
    try:
        response = requests.get(f"{BASE_URL}/ciudades/", headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            ciudades = response.json()
            print(f"   Total ciudades: {len(ciudades)}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")

    # 3. UPDATE - Actualizar ciudad
    print("\n3. UPDATE - Actualizando ciudad...")
    update_data = {
        "nombre": "Ciudad de Test Actualizada",
        "pais_id": pais_id
    }

    try:
        response = requests.put(
            f"{BASE_URL}/ciudades/{ciudad_id}", json=update_data, headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   Ciudad actualizada correctamente")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")

    # 4. DELETE - Eliminar ciudad
    print("\n4. DELETE - Eliminando ciudad...")
    try:
        response = requests.delete(
            f"{BASE_URL}/ciudades/{ciudad_id}", headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   Ciudad eliminada correctamente")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")

    return True


def run_all_crud_tests():
    """Ejecutar todas las pruebas CRUD"""
    print("PRUEBA COMPLETA CRUD - SISTEMA LOGISTICO")
    print("=" * 60)

    # Login primero
    if not login_and_get_token():
        print("No se pudo obtener token de autenticación. Abortando pruebas.")
        return False

    # Ejecutar pruebas CRUD
    tests_results = []

    print("\nIniciando pruebas CRUD...")

    # Test Países
    try:
        result = test_paises_crud()
        tests_results.append(("Paises", result))
    except Exception as e:
        print(f"Error en test de paises: {e}")
        tests_results.append(("Paises", False))

    # Test Monedas
    try:
        result = test_monedas_crud()
        tests_results.append(("Monedas", result))
    except Exception as e:
        print(f"Error en test de monedas: {e}")
        tests_results.append(("Monedas", False))

    # Test Ciudades
    try:
        result = test_ciudades_crud()
        tests_results.append(("Ciudades", result))
    except Exception as e:
        print(f"Error en test de ciudades: {e}")
        tests_results.append(("Ciudades", False))

    # Test Remitentes
    try:
        result = test_remitentes_crud()
        tests_results.append(("Remitentes", result))
    except Exception as e:
        print(f"Error en test de remitentes: {e}")
        tests_results.append(("Remitentes", False))

    # Test Transportadoras
    try:
        result = test_transportadoras_crud()
        tests_results.append(("Transportadoras", result))
    except Exception as e:
        print(f"Error en test de transportadoras: {e}")
        tests_results.append(("Transportadoras", False))

    # Resultados finales
    print("\n" + "=" * 60)
    print("RESULTADOS FINALES - PRUEBAS CRUD")
    print("=" * 60)

    passed = 0
    total = len(tests_results)

    for test_name, result in tests_results:
        status = "PASSED" if result else "FAILED"
        print(f"{test_name}: {status}")
        if result:
            passed += 1

    print(f"\nTotal: {passed}/{total} pruebas pasaron")

    if passed == total:
        print("EXITO: Todas las pruebas CRUD pasaron correctamente!")
        return True
    else:
        print("ADVERTENCIA: Algunas pruebas fallaron. Revisar logs arriba.")
        return False


if __name__ == "__main__":
    run_all_crud_tests()
