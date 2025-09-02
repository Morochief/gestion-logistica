"""
Sistema de Background Jobs para Reportes
Usa APScheduler para procesar reportes de manera asíncrona
"""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.executors.pool import ThreadPoolExecutor
from datetime import datetime, timedelta
import json
import os
from flask import current_app
from . import db
from .models import Reporte, CRT, MIC, Honorario, Movimiento
import traceback

# Configuración del scheduler
jobstores = {
    'default': MemoryJobStore()
}
executors = {
    'default': ThreadPoolExecutor(max_workers=3)
}
job_defaults = {
    'coalesce': False,
    'max_instances': 3,
    'misfire_grace_time': 30
}

scheduler = BackgroundScheduler(
    jobstores=jobstores,
    executors=executors,
    job_defaults=job_defaults,
    timezone='America/Asuncion'
)

# Estado de los jobs
job_status = {}
app = None


def init_scheduler(flask_app):
    """Inicializar el scheduler con la aplicación Flask"""
    global scheduler, app
    app = flask_app

    # Configurar el scheduler
    scheduler.configure(
        jobstores=jobstores,
        executors=executors,
        job_defaults=job_defaults,
        timezone='America/Asuncion'
    )

    # Agregar jobs programados
    scheduler.add_job(
        func=generate_daily_report,
        trigger="cron",
        hour=6,  # 6 AM todos los días
        minute=0,
        id='daily_report',
        name='Reporte Diario del Sistema',
        replace_existing=True
    )

    scheduler.add_job(
        func=cleanup_old_reports,
        trigger="cron",
        day_of_week='mon',  # Lunes
        hour=2,  # 2 AM
        minute=0,
        id='cleanup_reports',
        name='Limpiar Reportes Antiguos',
        replace_existing=True
    )

    # Iniciar el scheduler
    if not scheduler.running:
        scheduler.start()
        flask_app.logger.info("Background scheduler iniciado")


def shutdown_scheduler():
    """Detener el scheduler"""
    if scheduler.running:
        scheduler.shutdown()
        current_app.logger.info("Background scheduler detenido")


def create_report_job(report_type, parameters=None, user_id=None):
    """
    Crear un job de reporte inmediato

    Args:
        report_type (str): Tipo de reporte ('crt_summary', 'financial', 'activity')
        parameters (dict): Parámetros del reporte
        user_id (int): ID del usuario que solicita el reporte

    Returns:
        str: Job ID
    """
    job_id = f"report_{report_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    # Guardar el estado inicial del job
    job_status[job_id] = {
        'status': 'queued',
        'progress': 0,
        'message': 'En cola de procesamiento',
        'created_at': datetime.now(),
        'user_id': user_id,
        'report_type': report_type
    }

    # Agregar el job al scheduler
    scheduler.add_job(
        func=process_report,
        args=[job_id, report_type, parameters or {}],
        id=job_id,
        name=f'Reporte {report_type}',
        replace_existing=True
    )

    return job_id


def get_job_status(job_id):
    """Obtener el estado de un job"""
    return job_status.get(job_id, {'status': 'not_found'})


def process_report(job_id, report_type, parameters):
    """
    Procesar un reporte en background

    Args:
        job_id (str): ID del job
        report_type (str): Tipo de reporte
        parameters (dict): Parámetros del reporte
    """
    try:
        # Actualizar estado
        job_status[job_id]['status'] = 'processing'
        job_status[job_id]['progress'] = 10
        job_status[job_id]['message'] = 'Procesando reporte...'

        # Crear contexto de aplicación
        with scheduler.app.app_context():
            if report_type == 'crt_summary':
                result = generate_crt_summary_report(parameters)
            elif report_type == 'financial':
                result = generate_financial_report(parameters)
            elif report_type == 'activity':
                result = generate_activity_report(parameters)
            else:
                raise ValueError(f"Tipo de reporte desconocido: {report_type}")

            # Actualizar estado final
            job_status[job_id]['status'] = 'completed'
            job_status[job_id]['progress'] = 100
            job_status[job_id]['message'] = 'Reporte completado exitosamente'
            job_status[job_id]['result'] = result
            job_status[job_id]['completed_at'] = datetime.now()

    except Exception as e:
        # Actualizar estado de error
        job_status[job_id]['status'] = 'failed'
        job_status[job_id]['message'] = f'Error: {str(e)}'
        job_status[job_id]['error'] = traceback.format_exc()
        job_status[job_id]['completed_at'] = datetime.now()

        current_app.logger.error(f"Error en job {job_id}: {e}")


def generate_crt_summary_report(parameters):
    """Generar reporte resumen de CRTs"""
    date_from = parameters.get('date_from')
    date_to = parameters.get('date_to')

    query = CRT.query

    if date_from:
        query = query.filter(CRT.fecha_emision >= date_from)
    if date_to:
        query = query.filter(CRT.fecha_emision <= date_to)

    crts = query.all()

    summary = {
        'total_crts': len(crts),
        'total_valor': sum(crt.valor_incoterm or 0 for crt in crts),
        'por_estado': {},
        'por_moneda': {},
        'por_mes': {}
    }

    for crt in crts:
        # Por estado
        estado = crt.estado or 'SIN_ESTADO'
        summary['por_estado'][estado] = summary['por_estado'].get(
            estado, 0) + 1

        # Por moneda
        if crt.moneda:
            moneda = crt.moneda.nombre
            summary['por_moneda'][moneda] = summary['por_moneda'].get(
                moneda, 0) + 1

        # Por mes
        mes = crt.fecha_emision.strftime(
            '%Y-%m') if crt.fecha_emision else 'SIN_FECHA'
        summary['por_mes'][mes] = summary['por_mes'].get(mes, 0) + 1

    return summary


def generate_financial_report(parameters):
    """Generar reporte financiero"""
    date_from = parameters.get('date_from')
    date_to = parameters.get('date_to')

    query = Honorario.query

    if date_from:
        query = query.filter(Honorario.fecha >= date_from)
    if date_to:
        query = query.filter(Honorario.fecha <= date_to)

    honorarios = query.all()

    summary = {
        'total_honorarios': len(honorarios),
        'total_monto': sum(h.monto for h in honorarios),
        'por_transportadora': {},
        'por_mes': {},
        'promedio_por_transportadora': 0
    }

    for h in honorarios:
        # Por transportadora
        transportadora = h.transportadora.nombre if h.transportadora else 'SIN_TRANSPORTADORA'
        if transportadora not in summary['por_transportadora']:
            summary['por_transportadora'][transportadora] = {
                'count': 0, 'total': 0}
        summary['por_transportadora'][transportadora]['count'] += 1
        summary['por_transportadora'][transportadora]['total'] += h.monto

        # Por mes
        mes = h.fecha.strftime('%Y-%m')
        summary['por_mes'][mes] = summary['por_mes'].get(mes, 0) + h.monto

    # Calcular promedio
    if summary['por_transportadora']:
        total_transportadoras = len(summary['por_transportadora'])
        summary['promedio_por_transportadora'] = summary['total_monto'] / \
            total_transportadoras

    return summary


def generate_activity_report(parameters):
    """Generar reporte de actividad del sistema"""
    days = parameters.get('days', 30)
    date_from = datetime.now() - timedelta(days=days)

    # CRTs creados
    crts_count = CRT.query.filter(CRT.fecha_emision >= date_from).count()

    # MICs creados
    mics_count = MIC.query.filter(MIC.creado_en >= date_from).count()

    # Honorarios procesados
    honorarios_count = Honorario.query.filter(
        Honorario.fecha >= date_from).count()

    # Movimientos
    movimientos_count = Movimiento.query.filter(
        Movimiento.fecha >= date_from).count()

    return {
        'periodo_dias': days,
        'crts_creados': crts_count,
        'mics_creados': mics_count,
        'honorarios_procesados': honorarios_count,
        'movimientos_registrados': movimientos_count,
        'actividad_total': crts_count + mics_count + honorarios_count + movimientos_count
    }


def generate_daily_report():
    """Generar reporte diario automático"""
    if not app:
        return

    try:
        with app.app_context():
            yesterday = datetime.now() - timedelta(days=1)

            # Datos del día anterior
            crts_count = CRT.query.filter(
                db.func.date(CRT.fecha_emision) == yesterday.date()
            ).count()

            honorarios_total = db.session.query(
                db.func.sum(Honorario.monto)
            ).filter(
                db.func.date(Honorario.fecha) == yesterday.date()
            ).scalar() or 0

            # Crear reporte en BD
            reporte = Reporte(
                tipo='daily_auto',
                datos=json.dumps({
                    'fecha': yesterday.strftime('%Y-%m-%d'),
                    'crts_creados': crts_count,
                    'honorarios_total': float(honorarios_total),
                    'generado_auto': True
                }),
                generado_por=1  # Sistema
            )

            db.session.add(reporte)
            db.session.commit()

            app.logger.info(
                f"Reporte diario generado: {crts_count} CRTs, ${honorarios_total} en honorarios")

    except Exception as e:
        if app:
            app.logger.error(f"Error generando reporte diario: {e}")


def cleanup_old_reports():
    """Limpiar reportes antiguos (más de 90 días)"""
    if not app:
        return

    try:
        with app.app_context():
            cutoff_date = datetime.now() - timedelta(days=90)

            deleted_count = Reporte.query.filter(
                Reporte.generado_en < cutoff_date
            ).delete()

            db.session.commit()

            app.logger.info(
                f"Limpieza completada: {deleted_count} reportes antiguos eliminados")

    except Exception as e:
        if app:
            app.logger.error(f"Error en limpieza de reportes: {e}")

# Funciones de utilidad para el frontend


def get_active_jobs():
    """Obtener jobs activos"""
    return {
        job_id: status for job_id, status in job_status.items()
        if status['status'] in ['queued', 'processing']
    }


def cancel_job(job_id):
    """Cancelar un job"""
    try:
        scheduler.remove_job(job_id)
        if job_id in job_status:
            job_status[job_id]['status'] = 'cancelled'
            job_status[job_id]['message'] = 'Job cancelado por usuario'
        return True
    except Exception as e:
        current_app.logger.error(f"Error cancelando job {job_id}: {e}")
        return False
