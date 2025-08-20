from flask import Blueprint, request, jsonify
from app.models import Pais
from app import db
from sqlalchemy.exc import IntegrityError

paises_bp = Blueprint('paises', __name__, url_prefix='/api/paises')

# Listar países
@paises_bp.route('/', methods=['GET'])
def listar_paises():
    paises = Pais.query.order_by(Pais.nombre).all()
    return jsonify([
        {"id": p.id, "nombre": p.nombre, "codigo": p.codigo}
        for p in paises
    ])

# Crear país
@paises_bp.route('/', methods=['POST'])
def crear_pais():
    data = request.json
    if not data.get('nombre') or not data.get('codigo'):
        return jsonify({"error": "Faltan campos obligatorios"}), 400
    pais = Pais(
        nombre=data['nombre'],
        codigo=data['codigo']
    )
    try:
        db.session.add(pais)
        db.session.commit()
        return jsonify({"message": "País creado", "id": pais.id}), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Código de país ya existe"}), 409

# Modificar país
@paises_bp.route('/<int:id>', methods=['PUT'])
def modificar_pais(id):
    pais = Pais.query.get_or_404(id)
    data = request.json
    pais.nombre = data.get('nombre', pais.nombre)
    pais.codigo = data.get('codigo', pais.codigo)
    db.session.commit()
    return jsonify({"message": "País modificado"})

# Eliminar país
@paises_bp.route('/<int:id>', methods=['DELETE'])
def eliminar_pais(id):
    pais = Pais.query.get_or_404(id)
    db.session.delete(pais)
    db.session.commit()
    return jsonify({"message": "País eliminado"})
