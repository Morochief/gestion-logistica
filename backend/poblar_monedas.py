#!/usr/bin/env python3
"""
Script para poblar la base de datos con monedas iniciales
"""
from app import create_app
from app.models import Moneda, db


def poblar_monedas():
    """Poblar la base de datos con monedas iniciales"""
    app = create_app()

    with app.app_context():
        # Verificar si ya hay monedas
        if Moneda.query.count() > 0:
            print("Ya hay monedas en la base de datos. No se poblará nuevamente.")
            return

        # Lista de monedas iniciales
        monedas_iniciales = [
            {"codigo": "PYG", "nombre": "Guaraní", "simbolo": "₲"},
            {"codigo": "USD", "nombre": "Dólar Estadounidense", "simbolo": "$"},
            {"codigo": "ARS", "nombre": "Peso Argentino", "simbolo": "$"},
            {"codigo": "BRL", "nombre": "Real Brasileño", "simbolo": "R$"},
            {"codigo": "EUR", "nombre": "Euro", "simbolo": "€"},
            {"codigo": "UYU", "nombre": "Peso Uruguayo", "simbolo": "$"},
            {"codigo": "BOB", "nombre": "Boliviano", "simbolo": "Bs"},
            {"codigo": "CLP", "nombre": "Peso Chileno", "simbolo": "$"},
            {"codigo": "COP", "nombre": "Peso Colombiano", "simbolo": "$"},
            {"codigo": "PEN", "nombre": "Sol Peruano", "simbolo": "S/"},
            {"codigo": "VES", "nombre": "Bolívar Venezolano", "simbolo": "Bs"},
        ]

        print("Poblando monedas iniciales...")

        for moneda_data in monedas_iniciales:
            moneda = Moneda(
                codigo=moneda_data["codigo"],
                nombre=moneda_data["nombre"],
                simbolo=moneda_data["simbolo"]
            )
            db.session.add(moneda)
            print(f"Agregado: {moneda.nombre} ({moneda.codigo})")

        try:
            db.session.commit()
            print(f"✅ {len(monedas_iniciales)} monedas agregadas exitosamente!")
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error al poblar monedas: {e}")


if __name__ == "__main__":
    poblar_monedas()
