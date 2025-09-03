"""
Rutas para Background Jobs de Reportes
Permite al frontend crear, monitorear y gestionar reportes asíncronos
"""
from flask import Blueprint, request, jsonify
from ..background_jobs import create_report_job, get_job_status, get_active_jobs, cancel_job
from ..utils.auth import token_required, get_current_user

background_reports_bp = Blueprint(
    'background_reports', __name__, url_prefix='/api/background-reports')


@background_reports_bp.route('/create', methods=['POST'])
@token_required
def create_report():
    """
    Crear un nuevo reporte en background
    """
    try:
        data = request.get_json()
        report_type = data.get('report_type')
        parameters = data.get('parameters', {})
        user = get_current_user()

        if not report_type:
            return jsonify({'error': 'Tipo de reporte requerido'}), 400

        # Validar tipos de reporte permitidos
        allowed_types = ['crt_summary', 'financial', 'activity']
        if report_type not in allowed_types:
            return jsonify({'error': f'Tipo de reporte no válido. Permitidos: {allowed_types}'}), 400

        # Crear el job
        job_id = create_report_job(
            report_type, parameters, user['id'] if user else None)

        return jsonify({
            'success': True,
            'job_id': job_id,
            'message': 'Reporte en cola de procesamiento'
        }), 201

    except Exception as e:
        return jsonify({'error': f'Error al crear reporte: {str(e)}'}), 500


@background_reports_bp.route('/status/<job_id>', methods=['GET'])
@token_required
def get_report_status(job_id):
    """
    Obtener el estado de un reporte
    """
    try:
        status = get_job_status(job_id)

        if status['status'] == 'not_found':
            return jsonify({'error': 'Job no encontrado'}), 404

        return jsonify(status), 200

    except Exception as e:
        return jsonify({'error': f'Error al obtener estado: {str(e)}'}), 500


@background_reports_bp.route('/active', methods=['GET'])
@token_required
def get_active_reports():
    """
    Obtener todos los reportes activos
    """
    try:
        active_jobs = get_active_jobs()
        return jsonify({
            'jobs': active_jobs,
            'count': len(active_jobs)
        }), 200

    except Exception as e:
        return jsonify({'error': f'Error al obtener jobs activos: {str(e)}'}), 500


@background_reports_bp.route('/cancel/<job_id>', methods=['POST'])
@token_required
def cancel_report(job_id):
    """
    Cancelar un reporte en proceso
    """
    try:
        success = cancel_job(job_id)

        if success:
            return jsonify({
                'success': True,
                'message': 'Reporte cancelado exitosamente'
            }), 200
        else:
            return jsonify({'error': 'No se pudo cancelar el reporte'}), 400

    except Exception as e:
        return jsonify({'error': f'Error al cancelar reporte: {str(e)}'}), 500


@background_reports_bp.route('/types', methods=['GET'])
@token_required
def get_report_types():
    """
    Obtener tipos de reportes disponibles
    """
    report_types = {
        'crt_summary': {
            'name': 'Resumen de CRTs',
            'description': 'Reporte completo con estadísticas de CRTs por período',
            'parameters': {
                'date_from': {'type': 'date', 'required': False, 'description': 'Fecha desde'},
                'date_to': {'type': 'date', 'required': False, 'description': 'Fecha hasta'}
            }
        },
        'financial': {
            'name': 'Reporte Financiero',
            'description': 'Análisis financiero de honorarios y pagos',
            'parameters': {
                'date_from': {'type': 'date', 'required': False, 'description': 'Fecha desde'},
                'date_to': {'type': 'date', 'required': False, 'description': 'Fecha hasta'}
            }
        },
        'activity': {
            'name': 'Reporte de Actividad',
            'description': 'Estadísticas generales de actividad del sistema',
            'parameters': {
                'days': {'type': 'number', 'required': False, 'default': 30, 'description': 'Días a analizar'}
            }
        }
    }

    return jsonify(report_types), 200
