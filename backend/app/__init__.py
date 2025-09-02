from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_migrate import Migrate
from flask_caching import Cache
import traceback
import atexit

db = SQLAlchemy()
cache = Cache()


def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    # ⚠️ CONFIGURACIÓN PARA EVITAR REDIRECCIONES QUE CAUSAN CORS ERRORS
    app.config['PREFERRED_URL_SCHEME'] = 'http'
    app.config['SERVER_NAME'] = None
    app.url_map.host_matching = False

    # 🚨 SOLUCIÓN PARA EL PROBLEMA DE REDIRECCIÓN 308
    app.config['MAX_REDIRECTS'] = 0
    app.config['PRESERVE_CONTEXT_ON_EXCEPTION'] = False

    db.init_app(app)

    # Configuración de Caching
    # Cache en memoria para desarrollo
    app.config['CACHE_TYPE'] = 'SimpleCache'
    app.config['CACHE_DEFAULT_TIMEOUT'] = 300  # 5 minutos por defecto
    cache.init_app(app)

    CORS(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:3000", "http://127.0.0.1:3000"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "supports_credentials": False
        }
    })
    migrate = Migrate(app, db)

    with app.app_context():
        # ✅ AUTENTICACIÓN JWT COMPLETA
        from .routes.auth import auth_bp

        # Rutas principales del sistema
        from .routes.paises import paises_bp
        from .routes.ciudades import ciudades_bp
        from .routes.remitentes import remitentes_bp
        from .routes.transportadoras import transportadoras_bp
        from .routes.monedas import monedas_bp
        from .routes.honorarios import honorarios_bp
        from app.routes.crt import crt_bp
        from app.routes.mic import mic_bp
        from app.routes.mic_guardados import mic_guardados_bp
        from .routes.background_reports import background_reports_bp

        # Inicializar background jobs
        from .background_jobs import init_scheduler, shutdown_scheduler
        init_scheduler(app)

        # Inicializar métricas de Prometheus
        from .metrics import init_metrics, update_business_metrics, update_system_metrics
        init_metrics(app)

        # Actualizar métricas cada 30 segundos usando el mismo scheduler
        from .background_jobs import scheduler
        from .metrics import update_business_metrics, update_system_metrics

        # Pasar la app a las funciones de métricas
        def business_metrics_job():
            update_business_metrics(app)

        def system_metrics_job():
            update_system_metrics(app)

        scheduler.add_job(business_metrics_job, 'interval',
                          seconds=30, id='business_metrics')
        scheduler.add_job(system_metrics_job, 'interval',
                          seconds=60, id='system_metrics')

        # Registrar función de limpieza al salir
        atexit.register(shutdown_scheduler)

        # ✅ Se registran todos los módulos del sistema
        app.register_blueprint(auth_bp)  # 🔐 AUTENTICACIÓN JWT
        app.register_blueprint(paises_bp)
        app.register_blueprint(ciudades_bp)
        app.register_blueprint(remitentes_bp)
        app.register_blueprint(transportadoras_bp)
        app.register_blueprint(monedas_bp)
        app.register_blueprint(honorarios_bp)
        app.register_blueprint(crt_bp)
        app.register_blueprint(mic_bp)
        app.register_blueprint(mic_guardados_bp)

        # DIAGNOSTICO: Ver todas las rutas registradas
        print("\nRUTAS REGISTRADAS EN FLASK:")
        for rule in app.url_map.iter_rules():
            print(f"   {rule.rule} -> {rule.methods}")
        print("="*50)

    # 🚀 CORRIGE HEADERS DE CORS DESPUÉS DE CADA RESPUESTA - MEJORADO
    @app.after_request
    def add_cors_headers(response):
        # Solo agregar headers CORS si no están ya presentes (evitar conflictos)
        if "Access-Control-Allow-Origin" not in response.headers:
            response.headers["Access-Control-Allow-Origin"] = "http://localhost:3000"
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
            response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
            response.headers["Access-Control-Max-Age"] = "86400"
        return response

    # 🚀 RUTA para OPTIONS de cualquier ruta /api/* - MEJORADA CON REDIRECT DISABLED
    @app.route("/api/<path:path>", methods=["OPTIONS"])
    def options_api(path):
        response = app.make_response('')
        response.status_code = 200
        response.headers["Access-Control-Allow-Origin"] = "http://localhost:3000"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        response.headers["Access-Control-Max-Age"] = "86400"
        # 🚨 IMPORTANTE: Evitar cualquier redirección
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        return response

    # 🚀 RUTAS ESPECÍFICAS PARA OPTIONS - SOLUCIÓN COMPLETA
    @app.route("/api/paises", methods=["OPTIONS"])
    def options_paises():
        response = app.make_response('')
        response.status_code = 200
        response.headers["Access-Control-Allow-Origin"] = "http://localhost:3000"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        response.headers["Access-Control-Max-Age"] = "86400"
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        return response

    @app.route("/api/ciudades", methods=["OPTIONS"])
    def options_ciudades():
        response = app.make_response('')
        response.status_code = 200
        response.headers["Access-Control-Allow-Origin"] = "http://localhost:3000"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        response.headers["Access-Control-Max-Age"] = "86400"
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        return response

    @app.route("/api/crts/data/paises", methods=["OPTIONS"])
    def options_crts_data_paises():
        response = app.make_response('')
        response.status_code = 200
        response.headers["Access-Control-Allow-Origin"] = "http://localhost:3000"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        response.headers["Access-Control-Max-Age"] = "86400"
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        return response

    @app.route("/api/crts/data/ciudades", methods=["OPTIONS"])
    def options_crts_data_ciudades():
        response = app.make_response('')
        response.status_code = 200
        response.headers["Access-Control-Allow-Origin"] = "http://localhost:3000"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        response.headers["Access-Control-Max-Age"] = "86400"
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        return response

    # 🚀 RUTA para favicon
    @app.route('/favicon.ico')
    def favicon():
        return '', 204

    # ✅ NUEVO: RUTA DE SALUD DEL API
    @app.route('/api/health', methods=['GET'])
    def health_check():
        """
        ✅ Endpoint de salud para verificar que el API esté funcionando
        """
        return jsonify({
            "status": "ok",
            "message": "Sistema Logístico CRT/MIC funcionando correctamente",
            "version": "2.0",
            "endpoints": {
                "crts": "/api/crts",
                "crts_paginated": "/api/crts/paginated",  # ✅ NUEVO
                "crts_estados": "/api/crts/estados",      # ✅ NUEVO
                "mic": "/api/mic",
                "transportadoras": "/api/transportadoras",
                "remitentes": "/api/remitentes",
                "monedas": "/api/monedas",
                "paises": "/api/paises",
                "ciudades": "/api/ciudades"
            }
        })

    # ✅ MEJORADO: HANDLER PARA 404
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({
            "error": "Endpoint no encontrado",
            "message": "La ruta solicitada no existe",
            "available_endpoints": [
                "/api/health",
                "/api/crts",
                "/api/crts/paginated",  # ✅ NUEVO
                "/api/crts/estados",    # ✅ NUEVO
                "/api/mic",
                "/api/transportadoras",
                "/api/remitentes"
            ]
        }), 404

    # ✅ MEJORADO: HANDLER PARA 500
    @app.errorhandler(500)
    def internal_error(e):
        return jsonify({
            "error": "Error interno del servidor",
            "message": "Ocurrió un error inesperado"
        }), 500

    # 🚀 HANDLER GLOBAL PARA ERRORES (MEJORADO)
    @app.errorhandler(Exception)
    def handle_exception(e):
        trace = traceback.format_exc()
        print("\n" + "="*50)
        print("ERROR GLOBAL CAPTURADO:")
        print(trace)
        print("="*50)
        return jsonify({
            "error": str(e),
            "trace": trace if app.debug else None,  # ✅ Solo mostrar trace en debug
            "message": "Error interno del servidor"
        }), 500

    # ✅ Activa el modo debug
    app.debug = True

    # NUEVO: Log de inicialización
    print("Sistema Logístico CRT/MIC inicializado")
    print("Endpoints disponibles:")
    print("   - /api/crts (CRUD CRTs)")
    print("   - /api/crts/paginated (Lista con filtros)")
    print("   - /api/crts/estados (Estados disponibles)")
    print("   - /api/mic (Generación MIC)")
    print("   - /api/health (Salud del sistema)")

    return app
