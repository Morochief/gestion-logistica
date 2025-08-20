from flask import Blueprint, request, jsonify
from app.models import Parametro
from app import db
from sqlalchemy.exc import IntegrityError

parametros_bp = Blueprint('parametros', __name__, url_prefix='/api/parametros')

# Listar todos los parámetros
@parametros_bp.route('/', methods=['GET'])
def listar_parametros():
    parametros = Parametro.query.order_by(Parametro.clave).all()
    return jsonify([
        {
            "id": p.id,
            "clave": p.clave,
            "valor": p.valor
        }
        for p in parametros
    ])

# Crear parámetro
@parametros_bp.route('/', methods=['POST'])
def crear_parametro():
    data = request.json
    if not data.get('clave') or not data.get('valor'):
        return jsonify({"error": "Faltan campos obligatorios"}), 400
    parametro = Parametro(
        clave=data['clave'],
        valor=data['valor']
    )
    try:
        db.session.add(parametro)
        db.session.commit()
        return jsonify({"message": "Parámetro creado", "id": parametro.id}), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "La clave ya existe"}), 409

# Modificar parámetro
@parametros_bp.route('/<int:id>', methods=['PUT'])
def modificar_parametro(id):
    parametro = Parametro.query.get_or_404(id)
    data = request.json
    if data.get('clave'):
        parametro.clave = data.get('clave')
    if data.get('valor'):
        parametro.valor = data.get('valor')
    db.session.commit()
    return jsonify({"message": "Parámetro modificado"})

# Eliminar parámetro
@parametros_bp.route('/<int:id>', methods=['DELETE'])
def eliminar_parametro(id):
    parametro = Parametro.query.get_or_404(id)
    db.session.delete(parametro)
    db.session.commit()
    return jsonify({"message": "Parámetro eliminado"})
