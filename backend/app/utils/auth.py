import jwt
import bcrypt
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify, current_app
import os

# Configuración JWT
JWT_SECRET_KEY = os.getenv(
    'JWT_SECRET_KEY', 'tu_clave_secreta_muy_segura_aqui')
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 30
JWT_REFRESH_TOKEN_EXPIRE_DAYS = 7


def hash_password(password):
    """Hashea una contraseña usando bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def verify_password(password, hashed_password):
    """Verifica una contraseña contra su hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))


def create_access_token(data):
    """Crea un token de acceso JWT"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm="HS256")
    return encoded_jwt


def create_refresh_token(data):
    """Crea un token de refresco JWT"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=JWT_REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm="HS256")
    return encoded_jwt


def verify_token(token):
    """Verifica y decodifica un token JWT"""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def token_required(f):
    """Decorador para proteger rutas que requieren autenticación"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None

        # Extraer token del header Authorization
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]

        if not token:
            return jsonify({'error': 'Token de acceso requerido'}), 401

        # Verificar token
        payload = verify_token(token)
        if not payload or payload.get('type') != 'access':
            return jsonify({'error': 'Token inválido o expirado'}), 401

        # Agregar información del usuario al request
        request.user_id = payload.get('user_id')
        request.user_rol = payload.get('rol')

        return f(*args, **kwargs)

    return decorated_function


def admin_required(f):
    """Decorador para rutas que requieren permisos de administrador"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Primero verificar que esté autenticado
        token_required_result = token_required(lambda: None)()
        if token_required_result:  # Si hay error de autenticación
            return token_required_result

        # Verificar rol de administrador
        if request.user_rol != 'admin':
            return jsonify({'error': 'Permisos de administrador requeridos'}), 403

        return f(*args, **kwargs)

    return decorated_function


def get_current_user():
    """Obtiene el usuario actual desde el token"""
    token = None

    if 'Authorization' in request.headers:
        auth_header = request.headers['Authorization']
        if auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]

    if not token:
        return None

    payload = verify_token(token)
    if not payload or payload.get('type') != 'access':
        return None

    return {
        'user_id': payload.get('user_id'),
        'usuario': payload.get('usuario'),
        'rol': payload.get('rol'),
        'nombre_completo': payload.get('nombre_completo')
    }
