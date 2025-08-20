from flask import Blueprint, request, jsonify
from app.models import Reporte, Usuario
from app import db

reportes_bp = Blueprint('reportes', __name__, url_prefix='/api/reportes')

# Listar reportes (paginado, filtrado por tipo o usuario)
@reportes_bp.route('/', methods=['GET'])
def listar_reportes():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    tipo = request.args.get('tipo')
    usuario_id = request.args.get('usuario_id', type=int)
    query = Reporte.query
    if tipo:
        query = query.filter_by(tipo=tipo)
    if usuario_id:
        query = query.filter_by(generado_por=usuario_id)
    reportes = query.order_by(Reporte.generado_en.desc(), Reporte.id.desc()).paginate(page=page, per_page=per_page)
    return jsonify({
        "items": [
            {
                "id": r.id,
                "tipo": r.tipo,
                "datos": r.datos,
                "generado_por": r.generado_por,
                "generado_en": r.generado_en.strftime('%Y-%m-%d %H:%M')
            }
            for r in reportes.items
        ],
        "total": reportes.total,
        "pages": reportes.pages,
        "current_page": reportes.page
    })

# Crear reporte
@reportes_bp.route('/', methods=['POST'])
def crear_reporte():
    data = request.json
    if not data.get('tipo') or not data.get('datos') or not data.get('generado_por'):
        return jsonify({"error": "Faltan campos obligatorios"}), 400
    usuario = Usuario.query.get(data['generado_por'])
    if not usuario:
        return jsonify({"error": "Usuario no encontrado"}), 404
    reporte = Reporte(
        tipo=data['tipo'],
        datos=data['datos'],
        generado_por=data['generado_por'],
        generado_en=data.get('generado_en')
    )
    db.session.add(reporte)
    db.session.commit()
    return jsonify({"message": "Reporte creado", "id": reporte.id}), 201

# Eliminar reporte
@reportes_bp.route('/<int:id>', methods=['DELETE'])
def eliminar_reporte(id):
    reporte = Reporte.query.get_or_404(id)
    db.session.delete(reporte)
    db.session.commit()
    return jsonify({"message": "Reporte eliminado"})
