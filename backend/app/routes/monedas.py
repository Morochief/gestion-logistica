from flask import Blueprint, request, jsonify
from app.models import Moneda
from app import db
from sqlalchemy.exc import IntegrityError

monedas_bp = Blueprint('monedas', __name__, url_prefix='/api/monedas')

# Listar monedas
@monedas_bp.route('/', methods=['GET'])
def listar_monedas():
    monedas = Moneda.query.order_by(Moneda.nombre).all()
    return jsonify([
        {
            "id": m.id,
            "codigo": m.codigo,
            "nombre": m.nombre,
            "simbolo": m.simbolo
        }
        for m in monedas
    ])

# Crear moneda
@monedas_bp.route('/', methods=['POST'])
def crear_moneda():
    data = request.json
    if not data.get('codigo') or not data.get('nombre') or not data.get('simbolo'):
        return jsonify({"error": "Faltan campos obligatorios"}), 400
    moneda = Moneda(
        codigo=data['codigo'],
        nombre=data['nombre'],
        simbolo=data['simbolo']
    )
    try:
        db.session.add(moneda)
        db.session.commit()
        return jsonify({"message": "Moneda creada", "id": moneda.id}), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Código de moneda duplicado"}), 409

# Modificar moneda
@monedas_bp.route('/<int:id>', methods=['PUT'])
def modificar_moneda(id):
    moneda = Moneda.query.get_or_404(id)
    data = request.json
    moneda.codigo = data.get('codigo', moneda.codigo)
    moneda.nombre = data.get('nombre', moneda.nombre)
    moneda.simbolo = data.get('simbolo', moneda.simbolo)
    db.session.commit()
    return jsonify({"message": "Moneda modificada"})

# Eliminar moneda
@monedas_bp.route('/<int:id>', methods=['DELETE'])
def eliminar_moneda(id):
    moneda = Moneda.query.get_or_404(id)
    db.session.delete(moneda)
    db.session.commit()
    return jsonify({"message": "Moneda eliminada"})
