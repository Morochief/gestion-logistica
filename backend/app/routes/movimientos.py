from flask import Blueprint, request, jsonify
from app.models import Movimiento, Moneda, Remitente, Transportadora, Usuario
from app import db

movimientos_bp = Blueprint('movimientos', __name__, url_prefix='/api/movimientos')

# Listar movimientos (paginado, filtros opcionales)
@movimientos_bp.route('/', methods=['GET'])
def listar_movimientos():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    remitente_id = request.args.get('remitente_id', type=int)
    transportadora_id = request.args.get('transportadora_id', type=int)
    moneda_id = request.args.get('moneda_id', type=int)
    usuario_id = request.args.get('usuario_id', type=int)
    tipo = request.args.get('tipo')
    estado = request.args.get('estado')
    query = Movimiento.query

    if remitente_id:
        query = query.filter_by(remitente_id=remitente_id)
    if transportadora_id:
        query = query.filter_by(transportadora_id=transportadora_id)
    if moneda_id:
        query = query.filter_by(moneda_id=moneda_id)
    if usuario_id:
        query = query.filter_by(usuario_id=usuario_id)
    if tipo:
        query = query.filter_by(tipo=tipo)
    if estado:
        query = query.filter_by(estado=estado)

    movimientos = query.order_by(Movimiento.fecha.desc(), Movimiento.id.desc()).paginate(page=page, per_page=per_page)
    return jsonify({
        "items": [
            {
                "id": m.id,
                "fecha": m.fecha.strftime('%Y-%m-%d %H:%M'),
                "monto": str(m.monto),
                "moneda_id": m.moneda_id,
                "remitente_id": m.remitente_id,
                "transportadora_id": m.transportadora_id,
                "usuario_id": m.usuario_id,
                "tipo": m.tipo,
                "descripcion": m.descripcion,
                "estado": m.estado
            }
            for m in movimientos.items
        ],
        "total": movimientos.total,
        "pages": movimientos.pages,
        "current_page": movimientos.page
    })

# Crear movimiento
@movimientos_bp.route('/', methods=['POST'])
def crear_movimiento():
    data = request.json
    required_fields = ['monto', 'moneda_id', 'remitente_id', 'transportadora_id', 'usuario_id']
    if not all(data.get(f) for f in required_fields):
        return jsonify({"error": "Faltan campos obligatorios"}), 400
    # Validaciones de FK (opcional, puedes quitar para optimizar)
    if not Moneda.query.get(data['moneda_id']):
        return jsonify({"error": "Moneda no encontrada"}), 404
    if not Remitente.query.get(data['remitente_id']):
        return jsonify({"error": "Remitente no encontrado"}), 404
    if not Transportadora.query.get(data['transportadora_id']):
        return jsonify({"error": "Transportadora no encontrada"}), 404
    if not Usuario.query.get(data['usuario_id']):
        return jsonify({"error": "Usuario no encontrado"}), 404
    movimiento = Movimiento(
        monto=data['monto'],
        moneda_id=data['moneda_id'],
        remitente_id=data['remitente_id'],
        transportadora_id=data['transportadora_id'],
        usuario_id=data['usuario_id'],
        tipo=data.get('tipo'),
        descripcion=data.get('descripcion'),
        estado=data.get('estado', 'pendiente'),
        fecha=data.get('fecha')
    )
    db.session.add(movimiento)
    db.session.commit()
    return jsonify({"message": "Movimiento creado", "id": movimiento.id}), 201

# Modificar movimiento
@movimientos_bp.route('/<int:id>', methods=['PUT'])
def modificar_movimiento(id):
    movimiento = Movimiento.query.get_or_404(id)
    data = request.json
    if data.get('monto') is not None:
        movimiento.monto = data.get('monto')
    if data.get('moneda_id'):
        if not Moneda.query.get(data['moneda_id']):
            return jsonify({"error": "Moneda no encontrada"}), 404
        movimiento.moneda_id = data['moneda_id']
    if data.get('remitente_id'):
        if not Remitente.query.get(data['remitente_id']):
            return jsonify({"error": "Remitente no encontrado"}), 404
        movimiento.remitente_id = data['remitente_id']
    if data.get('transportadora_id'):
        if not Transportadora.query.get(data['transportadora_id']):
            return jsonify({"error": "Transportadora no encontrada"}), 404
        movimiento.transportadora_id = data['transportadora_id']
    if data.get('usuario_id'):
        if not Usuario.query.get(data['usuario_id']):
            return jsonify({"error": "Usuario no encontrado"}), 404
        movimiento.usuario_id = data['usuario_id']
    movimiento.tipo = data.get('tipo', movimiento.tipo)
    movimiento.descripcion = data.get('descripcion', movimiento.descripcion)
    movimiento.estado = data.get('estado', movimiento.estado)
    if data.get('fecha'):
        movimiento.fecha = data.get('fecha')
    db.session.commit()
    return jsonify({"message": "Movimiento modificado"})

# Eliminar movimiento
@movimientos_bp.route('/<int:id>', methods=['DELETE'])
def eliminar_movimiento(id):
    movimiento = Movimiento.query.get_or_404(id)
    db.session.delete(movimiento)
    db.session.commit()
    return jsonify({"message": "Movimiento eliminado"})
