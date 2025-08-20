from flask import Blueprint, request, jsonify
from app.models import Ciudad, Pais
from app import db

ciudades_bp = Blueprint('ciudades', __name__, url_prefix='/api/ciudades')

# Listar ciudades (puede filtrar por país)
@ciudades_bp.route('/', methods=['GET'])
def listar_ciudades():
    pais_id = request.args.get('pais_id', type=int)
    query = Ciudad.query
    if pais_id:
        query = query.filter_by(pais_id=pais_id)
    ciudades = query.order_by(Ciudad.nombre).all()
    return jsonify([
        {
            "id": c.id,
            "nombre": c.nombre,
            "pais_id": c.pais_id,
            "pais_nombre": c.pais.nombre if c.pais else "",  # <--- ESTE CAMPO NUEVO
        }
        for c in ciudades
    ])

# Crear ciudad
@ciudades_bp.route('/', methods=['POST'])
def crear_ciudad():
    data = request.json
    if not data.get('nombre') or not data.get('pais_id'):
        return jsonify({"error": "Faltan campos obligatorios"}), 400
    # Valida que el país exista
    pais = Pais.query.get(data['pais_id'])
    if not pais:
        return jsonify({"error": "País no encontrado"}), 404
    ciudad = Ciudad(
        nombre=data['nombre'],
        pais_id=data['pais_id']
    )
    db.session.add(ciudad)
    db.session.commit()
    return jsonify({"message": "Ciudad creada", "id": ciudad.id}), 201

# Modificar ciudad
@ciudades_bp.route('/<int:id>', methods=['PUT'])
def modificar_ciudad(id):
    ciudad = Ciudad.query.get_or_404(id)
    data = request.json
    ciudad.nombre = data.get('nombre', ciudad.nombre)
    if data.get('pais_id'):
        pais = Pais.query.get(data['pais_id'])
        if not pais:
            return jsonify({"error": "País no encontrado"}), 404
        ciudad.pais_id = data['pais_id']
    db.session.commit()
    return jsonify({"message": "Ciudad modificada"})

# Eliminar ciudad
@ciudades_bp.route('/<int:id>', methods=['DELETE'])
def eliminar_ciudad(id):
    ciudad = Ciudad.query.get_or_404(id)
    db.session.delete(ciudad)
    db.session.commit()
    return jsonify({"message": "Ciudad eliminada"})
