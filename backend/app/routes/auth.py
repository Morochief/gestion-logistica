from flask import Blueprint, request, jsonify
from app.models import Usuario, db
from app.utils.auth import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    verify_token,
    token_required,
    get_current_user
)
from datetime import datetime

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

# Ruta de registro de usuarios


@auth_bp.route('/register', methods=['POST'])
def register():
    """Registrar un nuevo usuario"""
    try:
        data = request.json

        # Validar campos requeridos
        if not data.get('usuario') or not data.get('clave') or not data.get('nombre_completo'):
            return jsonify({'error': 'Usuario, clave y nombre completo son requeridos'}), 400

        # Verificar si el usuario ya existe
        if Usuario.query.filter_by(usuario=data['usuario']).first():
            return jsonify({'error': 'El usuario ya existe'}), 409

        # Verificar si el email ya existe (si se proporciona)
        if data.get('email') and Usuario.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'El email ya está registrado'}), 409

        # Crear nuevo usuario
        hashed_password = hash_password(data['clave'])
        nuevo_usuario = Usuario(
            usuario=data['usuario'],
            clave_hash=hashed_password,
            nombre_completo=data['nombre_completo'],
            email=data.get('email'),
            rol=data.get('rol', 'operador'),  # Por defecto operador
            estado='activo'
        )

        db.session.add(nuevo_usuario)
        db.session.commit()

        return jsonify({
            'message': 'Usuario registrado exitosamente',
            'usuario': {
                'id': nuevo_usuario.id,
                'usuario': nuevo_usuario.usuario,
                'nombre_completo': nuevo_usuario.nombre_completo,
                'email': nuevo_usuario.email,
                'rol': nuevo_usuario.rol
            }
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error al registrar usuario: {str(e)}'}), 500

# Ruta de login


@auth_bp.route('/login', methods=['POST'])
def login():
    """Iniciar sesión y obtener tokens JWT"""
    try:
        data = request.json

        # Validar campos requeridos
        if not data.get('usuario') or not data.get('clave'):
            return jsonify({'error': 'Usuario y clave son requeridos'}), 400

        # Buscar usuario
        usuario = Usuario.query.filter_by(usuario=data['usuario']).first()

        if not usuario:
            return jsonify({'error': 'Usuario no encontrado'}), 401

        # Verificar estado del usuario
        if usuario.estado != 'activo':
            return jsonify({'error': 'Usuario inactivo'}), 401

        # Verificar contraseña
        if not verify_password(data['clave'], usuario.clave_hash):
            return jsonify({'error': 'Contraseña incorrecta'}), 401

        # Actualizar último login
        usuario.ultimo_login = datetime.utcnow()
        db.session.commit()

        # Crear tokens
        token_data = {
            'user_id': usuario.id,
            'usuario': usuario.usuario,
            'rol': usuario.rol,
            'nombre_completo': usuario.nombre_completo
        }

        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)

        # Guardar refresh token en la base de datos
        usuario.refresh_token = refresh_token
        db.session.commit()

        return jsonify({
            'message': 'Login exitoso',
            'access_token': access_token,
            'refresh_token': refresh_token,
            'token_type': 'Bearer',
            'expires_in': 1800,  # 30 minutos
            'usuario': {
                'id': usuario.id,
                'usuario': usuario.usuario,
                'nombre_completo': usuario.nombre_completo,
                'email': usuario.email,
                'rol': usuario.rol
            }
        }), 200

    except Exception as e:
        return jsonify({'error': f'Error en login: {str(e)}'}), 500

# Ruta para refrescar tokens


@auth_bp.route('/refresh', methods=['POST'])
def refresh_token():
    """Refrescar token de acceso usando refresh token"""
    try:
        data = request.json

        if not data.get('refresh_token'):
            return jsonify({'error': 'Refresh token requerido'}), 400

        # Verificar refresh token
        payload = verify_token(data['refresh_token'])

        if not payload or payload.get('type') != 'refresh':
            return jsonify({'error': 'Refresh token inválido'}), 401

        # Verificar que el refresh token existe en la base de datos
        usuario = Usuario.query.get(payload.get('user_id'))

        if not usuario or usuario.refresh_token != data['refresh_token']:
            return jsonify({'error': 'Refresh token no válido'}), 401

        # Verificar estado del usuario
        if usuario.estado != 'activo':
            return jsonify({'error': 'Usuario inactivo'}), 401

        # Crear nuevo access token
        token_data = {
            'user_id': usuario.id,
            'usuario': usuario.usuario,
            'rol': usuario.rol,
            'nombre_completo': usuario.nombre_completo
        }

        new_access_token = create_access_token(token_data)

        return jsonify({
            'message': 'Token refrescado exitosamente',
            'access_token': new_access_token,
            'token_type': 'Bearer',
            'expires_in': 1800
        }), 200

    except Exception as e:
        return jsonify({'error': f'Error al refrescar token: {str(e)}'}), 500

# Ruta para obtener perfil del usuario actual


@auth_bp.route('/profile', methods=['GET'])
@token_required
def get_profile():
    """Obtener perfil del usuario autenticado"""
    try:
        usuario = Usuario.query.get(request.user_id)

        if not usuario:
            return jsonify({'error': 'Usuario no encontrado'}), 404

        return jsonify({
            'id': usuario.id,
            'usuario': usuario.usuario,
            'nombre_completo': usuario.nombre_completo,
            'email': usuario.email,
            'rol': usuario.rol,
            'estado': usuario.estado,
            'creado_en': usuario.creado_en.isoformat() if usuario.creado_en else None,
            'ultimo_login': usuario.ultimo_login.isoformat() if usuario.ultimo_login else None
        }), 200

    except Exception as e:
        return jsonify({'error': f'Error al obtener perfil: {str(e)}'}), 500

# Ruta para cambiar contraseña


@auth_bp.route('/change-password', methods=['POST'])
@token_required
def change_password():
    """Cambiar contraseña del usuario autenticado"""
    try:
        data = request.json

        if not data.get('current_password') or not data.get('new_password'):
            return jsonify({'error': 'Contraseña actual y nueva son requeridas'}), 400

        usuario = Usuario.query.get(request.user_id)

        # Verificar contraseña actual
        if not verify_password(data['current_password'], usuario.clave_hash):
            return jsonify({'error': 'Contraseña actual incorrecta'}), 401

        # Validar nueva contraseña
        if len(data['new_password']) < 6:
            return jsonify({'error': 'La nueva contraseña debe tener al menos 6 caracteres'}), 400

        # Actualizar contraseña
        usuario.clave_hash = hash_password(data['new_password'])
        db.session.commit()

        return jsonify({'message': 'Contraseña cambiada exitosamente'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error al cambiar contraseña: {str(e)}'}), 500

# Ruta para logout (invalidar refresh token)


@auth_bp.route('/logout', methods=['POST'])
@token_required
def logout():
    """Cerrar sesión invalidando el refresh token"""
    try:
        usuario = Usuario.query.get(request.user_id)

        if usuario:
            usuario.refresh_token = None
            db.session.commit()

        return jsonify({'message': 'Logout exitoso'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error en logout: {str(e)}'}), 500

# Ruta para verificar token


@auth_bp.route('/verify', methods=['GET'])
@token_required
def verify_token_endpoint():
    """Verificar que el token de acceso es válido"""
    return jsonify({
        'message': 'Token válido',
        'usuario': get_current_user()
    }), 200
