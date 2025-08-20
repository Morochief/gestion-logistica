from flask import Blueprint, request, jsonify
from app.models import Honorario, Transportadora, Moneda
from app import db

honorarios_bp = Blueprint('honorarios', __name__, url_prefix='/api/honorarios')

@honorarios_bp.route('/', methods=['GET'])
def listar_honorarios():
    honorarios = Honorario.query.order_by(Honorario.id.desc()).all()
    resultado = []
    for h in honorarios:
        resultado.append({
            "id": h.id,
            "codigo": h.id,
            "monto": float(h.monto),
            "transportadora_id": h.transportadora_id,
            "transportadora_nombre": h.transportadora.nombre if h.transportadora else "",
            "moneda_id": h.moneda_id,
            "moneda_nombre": h.moneda.nombre if h.moneda else "",
        })
    return jsonify(resultado)

@honorarios_bp.route('/', methods=['POST'])
def crear_honorario():
    data = request.json
    monto = data.get('monto')
    transportadora_id = data.get('transportadora_id')
    moneda_id = data.get('moneda_id')
    if not monto or not transportadora_id or not moneda_id:
        return jsonify({"error": "Faltan campos obligatorios (monto, transportadora y moneda)"}), 400
    # Valida que exista la moneda
    if not Moneda.query.get(moneda_id):
        return jsonify({"error": "Moneda no encontrada"}), 404
    honorario = Honorario(
        monto=monto,
        transportadora_id=transportadora_id,
        moneda_id=moneda_id,
        fecha=data.get('fecha')
    )
    db.session.add(honorario)
    db.session.commit()
    return jsonify({"message": "Honorario creado", "id": honorario.id}), 201

@honorarios_bp.route('/<int:id>', methods=['PUT'])
def modificar_honorario(id):
    honorario = Honorario.query.get_or_404(id)
    data = request.json
    honorario.monto = data.get('monto', honorario.monto)
    honorario.transportadora_id = data.get('transportadora_id', honorario.transportadora_id)
    moneda_id = data.get('moneda_id', honorario.moneda_id)
    # Valida que exista la moneda
    if not moneda_id or not Moneda.query.get(moneda_id):
        return jsonify({"error": "Moneda no encontrada o no definida"}), 400
    honorario.moneda_id = moneda_id
    db.session.commit()
    return jsonify({"message": "Honorario modificado"})

@honorarios_bp.route('/<int:id>', methods=['DELETE'])
def eliminar_honorario(id):
    honorario = Honorario.query.get_or_404(id)
    db.session.delete(honorario)
    db.session.commit()
    return jsonify({"message": "Honorario eliminado"})
