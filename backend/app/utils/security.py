import jwt
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta

def hash_password(password):
    return generate_password_hash(password)

def verify_password(password, hash_):
    return check_password_hash(hash_, password)

def generate_jwt(payload, secret, expires_in=24):
    exp = datetime.utcnow() + timedelta(hours=expires_in)
    payload['exp'] = exp
    token = jwt.encode(payload, secret, algorithm="HS256")
    return token

def decode_jwt(token, secret):
    try:
        payload = jwt.decode(token, secret, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
