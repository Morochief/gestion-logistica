from flask import Blueprint, request, jsonify
from app.models import Remitente, Ciudad
from app import db

remitentes_bp = Blueprint('remitentes', __name__, url_prefix='/api/remitentes')

# Listar remitentes (paginado, búsqueda por nombre/documento)


@remitentes_bp.route('/', methods=['GET'])
def listar_remitentes():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)  # Cambiar de 10 a 50
    q = request.args.get('q', '', type=str).strip()

    query = Remitente.query

    if q:
        search = f"%{q}%"
        query = query.filter(
            db.or_(
                Remitente.nombre.ilike(search),
                Remitente.numero_documento.ilike(search)
            )
        )

    remitentes = query.order_by(Remitente.id.desc()).paginate(
        page=page,
        per_page=per_page,
        error_out=False  # Evitar errores si la página no existe
    )

    return jsonify({
        "items": [
            {
                "id": r.id,
                "nombre": r.nombre,
                "tipo_documento": r.tipo_documento,
                "numero_documento": r.numero_documento,
                "direccion": r.direccion,
                "ciudad_id": r.ciudad_id,
                "ciudad_nombre": r.ciudad.nombre if r.ciudad else ""
            }
            for r in remitentes.items
        ],
        "total": remitentes.total,
        "pages": remitentes.pages,
        "current_page": remitentes.page
    })

# Crear remitente


@remitentes_bp.route('/', methods=['POST'])
def crear_remitente():
    try:
        data = request.json
        if not data.get('nombre') or not data.get('ciudad_id'):
            return jsonify({"error": "Faltan campos obligatorios"}), 400

        ciudad = Ciudad.query.get(data['ciudad_id'])
        if not ciudad:
            return jsonify({"error": "Ciudad no encontrada"}), 404

        remitente = Remitente(
            nombre=data['nombre'],
            tipo_documento=data.get('tipo_documento'),
            numero_documento=data.get('numero_documento'),
            direccion=data.get('direccion'),
            ciudad_id=data['ciudad_id']
        )

        db.session.add(remitente)
        db.session.commit()

        return jsonify({"message": "Remitente creado", "id": remitente.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# Modificar remitente


@remitentes_bp.route('/<int:id>', methods=['PUT'])
def modificar_remitente(id):
    try:
        remitente = Remitente.query.get_or_404(id)
        data = request.json

        remitente.nombre = data.get('nombre', remitente.nombre)
        remitente.tipo_documento = data.get(
            'tipo_documento', remitente.tipo_documento)
        remitente.numero_documento = data.get(
            'numero_documento', remitente.numero_documento)
        remitente.direccion = data.get('direccion', remitente.direccion)

        if data.get('ciudad_id'):
            ciudad = Ciudad.query.get(data['ciudad_id'])
            if not ciudad:
                return jsonify({"error": "Ciudad no encontrada"}), 404
            remitente.ciudad_id = data['ciudad_id']

        db.session.commit()
        return jsonify({"message": "Remitente modificado"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# Eliminar remitente


@remitentes_bp.route('/<int:id>', methods=['DELETE'])
def eliminar_remitente(id):
    try:
        remitente = Remitente.query.get_or_404(id)
        db.session.delete(remitente)
        db.session.commit()
        return jsonify({"message": "Remitente eliminado"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
