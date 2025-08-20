from flask import Blueprint, request, jsonify
from app.models import Usuario
from app import db
from app.utils.security import hash_password
from sqlalchemy.exc import IntegrityError

usuarios_bp = Blueprint('usuarios', __name__, url_prefix='/api/usuarios')

# Listar usuarios (paginación opcional)
@usuarios_bp.route('/', methods=['GET'])
def listar_usuarios():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    usuarios = Usuario.query.order_by(Usuario.id.desc()).paginate(page=page, per_page=per_page)
    return jsonify({
        "items": [
            {
                "id": u.id,
                "nombre_completo": u.nombre_completo,
                "usuario": u.usuario,
                "rol": u.rol,
                "estado": u.estado,
                "creado_en": u.creado_en.strftime('%Y-%m-%d %H:%M')
            }
            for u in usuarios.items
        ],
        "total": usuarios.total,
        "pages": usuarios.pages,
        "current_page": usuarios.page
    })

# Crear usuario
@usuarios_bp.route('/', methods=['POST'])
def crear_usuario():
    data = request.json
    if not data.get('usuario') or not data.get('clave') or not data.get('nombre_completo'):
        return jsonify({"error": "Faltan campos obligatorios"}), 400
    usuario = Usuario(
        nombre_completo=data['nombre_completo'],
        usuario=data['usuario'],
        clave_hash=hash_password(data['clave']),
        rol=data.get('rol', 'operador'),
        estado=data.get('estado', 'activo')
    )
    try:
        db.session.add(usuario)
        db.session.commit()
        return jsonify({"message": "Usuario creado", "id": usuario.id}), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Nombre de usuario ya existe"}), 409

# Modificar usuario
@usuarios_bp.route('/<int:id>', methods=['PUT'])
def modificar_usuario(id):
    usuario = Usuario.query.get_or_404(id)
    data = request.json
    usuario.nombre_completo = data.get('nombre_completo', usuario.nombre_completo)
    usuario.rol = data.get('rol', usuario.rol)
    usuario.estado = data.get('estado', usuario.estado)
    if data.get('clave'):
        usuario.clave_hash = hash_password(data['clave'])
    db.session.commit()
    return jsonify({"message": "Usuario modificado"})

# Eliminar usuario
@usuarios_bp.route('/<int:id>', methods=['DELETE'])
def eliminar_usuario(id):
    usuario = Usuario.query.get_or_404(id)
    db.session.delete(usuario)
    db.session.commit()
    return jsonify({"message": "Usuario eliminado"})
