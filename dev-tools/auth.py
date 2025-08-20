from flask import Blueprint, request, jsonify
from app.models import Usuario
from app import db
from ..utils.security import verify_password, generate_jwt, decode_jwt
from flask import current_app as app

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

# Endpoint de login
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    usuario = data.get('usuario')
    clave = data.get('clave')
    if not usuario or not clave:
        return jsonify({"error": "Usuario y clave requeridos"}), 400
    user = Usuario.query.filter_by(usuario=usuario).first()
    if not user or not verify_password(clave, user.clave_hash):
        return jsonify({"error": "Usuario o clave incorrectos"}), 401
    token = generate_jwt(
        {"id": user.id, "usuario": user.usuario, "rol": user.rol},
        app.config["JWT_SECRET_KEY"]
    )
    return jsonify({
        "token": token,
        "usuario": user.usuario,
        "nombre_completo": user.nombre_completo,
        "rol": user.rol
    })

# Endpoint para validar token (protegido)
@auth_bp.route('/validar', methods=['POST'])
def validar():
    data = request.json
    token = data.get("token")
    if not token:
        return jsonify({"error": "Token requerido"}), 400
    payload = decode_jwt(token, app.config["JWT_SECRET_KEY"])
    if not payload:
        return jsonify({"error": "Token inválido o expirado"}), 401
    return jsonify({"valido": True, "usuario": payload})
