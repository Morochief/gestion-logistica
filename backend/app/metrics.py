"""
Prometheus metrics for the logistics system
"""
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from flask import Response, request
import time
import logging

logger = logging.getLogger(__name__)

# Request metrics
REQUEST_COUNT = Counter(
    'flask_requests_total',
    'Total number of requests',
    ['method', 'endpoint', 'status']
)

REQUEST_LATENCY = Histogram(
    'flask_request_duration_seconds',
    'Request duration in seconds',
    ['method', 'endpoint']
)

# Business metrics
CRT_CREATED = Counter(
    'crt_created_total',
    'Total number of CRTs created'
)

MIC_CREATED = Counter(
    'mic_created_total',
    'Total number of MICs created'
)

HONORARIOS_TOTAL = Gauge(
    'honorarios_total_amount',
    'Total amount of honorarios'
)

USERS_ACTIVE = Gauge(
    'users_active_total',
    'Total number of active users'
)

# Database metrics
DB_CONNECTIONS_ACTIVE = Gauge(
    'db_connections_active',
    'Number of active database connections'
)

DB_QUERY_DURATION = Histogram(
    'db_query_duration_seconds',
    'Database query duration in seconds',
    ['operation']
)

# System metrics
MEMORY_USAGE = Gauge(
    'memory_usage_bytes',
    'Current memory usage in bytes'
)

CPU_USAGE = Gauge(
    'cpu_usage_percent',
    'Current CPU usage percentage'
)


def init_metrics(app):
    """Initialize Prometheus metrics for the Flask app"""

    @app.before_request
    def before_request():
        request.start_time = time.time()

    @app.after_request
    def after_request(response):
        if hasattr(request, 'start_time'):
            latency = time.time() - request.start_time
            REQUEST_LATENCY.labels(
                method=request.method,
                endpoint=request.endpoint or 'unknown'
            ).observe(latency)

        REQUEST_COUNT.labels(
            method=request.method,
            endpoint=request.endpoint or 'unknown',
            status=response.status_code
        ).inc()

        return response

    @app.route('/metrics')
    def metrics():
        """Prometheus metrics endpoint"""
        return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)


def update_business_metrics(flask_app=None):
    """Update business-related metrics"""
    try:
        if not flask_app:
            from .background_jobs import app as flask_app

        if flask_app:
            with flask_app.app_context():
                from .models import CRT, MIC, Honorario, Usuario

                # Update CRT count
                crt_count = CRT.query.count()
                CRT_CREATED._value = crt_count

                # Update MIC count
                mic_count = MIC.query.count()
                MIC_CREATED._value = mic_count

                # Update honorarios total
                honorarios_total = Honorario.query.with_entities(
                    Honorario.monto
                ).all()
                total_amount = sum(h.monto for h in honorarios_total)
                HONORARIOS_TOTAL.set(total_amount)

                # Update active users
                users_count = Usuario.query.count()
                USERS_ACTIVE.set(users_count)

    except Exception as e:
        logger.warning(f"Failed to update business metrics: {e}")


def update_system_metrics(flask_app=None):
    """Update system-related metrics"""
    try:
        import psutil
        import os

        # Memory usage
        process = psutil.Process(os.getpid())
        memory_info = process.memory_info()
        MEMORY_USAGE.set(memory_info.rss)

        # CPU usage
        cpu_percent = process.cpu_percent(interval=1)
        CPU_USAGE.set(cpu_percent)

    except ImportError:
        # psutil not available
        pass
    except Exception as e:
        logger.warning(f"Failed to update system metrics: {e}")
