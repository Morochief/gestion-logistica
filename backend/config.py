import os


class Config:
    # Usar SQLite para testing - cambiar a PostgreSQL cuando esté configurado
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL') or 'sqlite:///./logistica.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = True
    SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'supersecretkey'
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'supersecretkey'
    PREFERRED_URL_SCHEME = "http"
