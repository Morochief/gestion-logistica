#!/usr/bin/env python3
"""
Script para poblar la base de datos con países iniciales
"""
from app import create_app
from app.models import Pais, db


def poblar_paises():
    """Poblar la base de datos con países iniciales"""
    app = create_app()

    with app.app_context():
        # Verificar si ya hay países
        if Pais.query.count() > 0:
            print("Ya hay países en la base de datos. No se poblará nuevamente.")
            return

        # Lista de países iniciales
        paises_iniciales = [
            {"nombre": "Paraguay", "codigo": "PY"},
            {"nombre": "Argentina", "codigo": "AR"},
            {"nombre": "Brasil", "codigo": "BR"},
            {"nombre": "Uruguay", "codigo": "UY"},
            {"nombre": "Bolivia", "codigo": "BO"},
            {"nombre": "Chile", "codigo": "CL"},
            {"nombre": "Colombia", "codigo": "CO"},
            {"nombre": "Ecuador", "codigo": "EC"},
            {"nombre": "Perú", "codigo": "PE"},
            {"nombre": "Venezuela", "codigo": "VE"},
        ]

        print("Poblando países iniciales...")

        for pais_data in paises_iniciales:
            pais = Pais(
                nombre=pais_data["nombre"],
                codigo=pais_data["codigo"]
            )
            db.session.add(pais)
            print(f"Agregado: {pais.nombre} ({pais.codigo})")

        try:
            db.session.commit()
            print(f"✅ {len(paises_iniciales)} países agregados exitosamente!")
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error al poblar países: {e}")


if __name__ == "__main__":
    poblar_paises()
