"""
Tests for background jobs functionality
"""
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
from app.background_jobs import (
    create_report_job, get_job_status, get_active_jobs, cancel_job,
    process_report, generate_crt_summary_report, generate_financial_report,
    generate_activity_report, generate_daily_report, cleanup_old_reports
)


@pytest.fixture
def mock_db():
    """Mock database session"""
    with patch('app.background_jobs.db') as mock:
        yield mock


@pytest.fixture
def mock_scheduler():
    """Mock APScheduler"""
    with patch('app.background_jobs.scheduler') as mock:
        yield mock


def test_create_report_job(mock_scheduler):
    """Test creating a report job"""
    job_id = create_report_job('crt_summary', {'date_from': '2024-01-01'})

    assert job_id.startswith('report_crt_summary_')
    mock_scheduler.add_job.assert_called_once()


def test_get_job_status():
    """Test getting job status"""
    from app.background_jobs import job_status

    # Initially should be not found
    status = get_job_status('nonexistent')
    assert status['status'] == 'not_found'

    # Add a job and check status
    job_status['test_job'] = {'status': 'completed', 'progress': 100}
    status = get_job_status('test_job')
    assert status['status'] == 'completed'


def test_get_active_jobs():
    """Test getting active jobs"""
    from app.background_jobs import job_status

    # Clear existing jobs
    job_status.clear()

    # Add some jobs
    job_status['job1'] = {'status': 'processing'}
    job_status['job2'] = {'status': 'queued'}
    job_status['job3'] = {'status': 'completed'}

    active_jobs = get_active_jobs()
    assert len(active_jobs) == 2
    assert 'job1' in active_jobs
    assert 'job2' in active_jobs
    assert 'job3' not in active_jobs


def test_cancel_job(mock_scheduler):
    """Test canceling a job"""
    from app.background_jobs import job_status

    # Add a job
    job_status['test_job'] = {'status': 'processing'}

    # Mock scheduler cancel
    mock_scheduler.remove_job.return_value = True

    result = cancel_job('test_job')
    assert result is True
    assert job_status['test_job']['status'] == 'cancelled'
    mock_scheduler.remove_job.assert_called_once_with('test_job')


@patch('app.background_jobs.generate_crt_summary_report')
def test_process_report_crt_summary(mock_generate):
    """Test processing CRT summary report"""
    mock_generate.return_value = {'total_crts': 10}

    from app.background_jobs import job_status
    job_status['test_job'] = {'status': 'processing', 'progress': 0}

    process_report('test_job', 'crt_summary', {})

    assert job_status['test_job']['status'] == 'completed'
    assert job_status['test_job']['progress'] == 100
    assert job_status['test_job']['result'] == {'total_crts': 10}
    mock_generate.assert_called_once_with({})


@patch('app.background_jobs.generate_financial_report')
def test_process_report_financial(mock_generate):
    """Test processing financial report"""
    mock_generate.return_value = {'total_honorarios': 1000}

    from app.background_jobs import job_status
    job_status['test_job'] = {'status': 'processing', 'progress': 0}

    process_report('test_job', 'financial', {})

    assert job_status['test_job']['status'] == 'completed'
    assert job_status['test_job']['result'] == {'total_honorarios': 1000}


def test_process_report_invalid_type():
    """Test processing report with invalid type"""
    from app.background_jobs import job_status
    job_status['test_job'] = {'status': 'processing', 'progress': 0}

    process_report('test_job', 'invalid_type', {})

    assert job_status['test_job']['status'] == 'failed'
    assert 'Tipo de reporte desconocido' in job_status['test_job']['message']


@patch('app.background_jobs.CRT')
def test_generate_crt_summary_report(mock_crt):
    """Test CRT summary report generation"""
    # Mock CRT query
    mock_query = MagicMock()
    mock_crt.query.filter.return_value = mock_query

    mock_crt_obj = MagicMock()
    mock_crt_obj.fecha_emision = datetime.now()
    mock_crt_obj.estado = 'COMPLETADO'
    mock_crt_obj.valor_incoterm = 1000
    mock_crt_obj.moneda.nombre = 'USD'

    mock_query.all.return_value = [mock_crt_obj]

    result = generate_crt_summary_report({})

    assert 'total_crts' in result
    assert 'por_estado' in result
    assert 'por_moneda' in result
    assert result['total_crts'] == 1


@patch('app.background_jobs.Honorario')
def test_generate_financial_report(mock_honorario):
    """Test financial report generation"""
    # Mock Honorario query
    mock_query = MagicMock()
    mock_honorario.query.filter.return_value = mock_query

    mock_honorario_obj = MagicMock()
    mock_honorario_obj.fecha = datetime.now()
    mock_honorario_obj.monto = 500
    mock_honorario_obj.transportadora.nombre = 'Transportadora A'

    mock_query.all.return_value = [mock_honorario_obj]

    result = generate_financial_report({})

    assert 'total_honorarios' in result
    assert 'total_monto' in result
    assert 'por_transportadora' in result
    assert result['total_monto'] == 500


@patch('app.background_jobs.CRT')
@patch('app.background_jobs.MIC')
@patch('app.background_jobs.Honorario')
@patch('app.background_jobs.Movimiento')
def test_generate_activity_report(mock_movimiento, mock_honorario, mock_mic, mock_crt):
    """Test activity report generation"""
    # Mock queries
    mock_crt.query.filter.return_value.count.return_value = 10
    mock_mic.query.filter.return_value.count.return_value = 5
    mock_honorario.query.filter.return_value.count.return_value = 3
    mock_movimiento.query.filter.return_value.count.return_value = 2

    result = generate_activity_report({'days': 30})

    assert result['crts_creados'] == 10
    assert result['mics_creados'] == 5
    assert result['honorarios_procesados'] == 3
    assert result['movimientos_registrados'] == 2
    assert result['actividad_total'] == 20


@patch('app.background_jobs.db')
@patch('app.background_jobs.Reporte')
def test_generate_daily_report(mock_reporte, mock_db):
    """Test daily report generation"""
    # Mock database operations
    mock_session = MagicMock()
    mock_db.session = mock_session

    # Mock CRT count query
    mock_crt_count = MagicMock()
    mock_crt_count.scalar.return_value = 5
    mock_db.session.query.return_value.filter.return_value.count.return_value = 5

    # Mock honorarios sum query
    mock_sum_query = MagicMock()
    mock_sum_query.filter.return_value.scalar.return_value = 2500.0
    mock_db.session.query.return_value.filter.return_value.scalar.return_value = 2500.0

    generate_daily_report()

    # Verify that a Reporte was created
    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()


@patch('app.background_jobs.db')
@patch('app.background_jobs.Reporte')
def test_cleanup_old_reports(mock_reporte, mock_db):
    """Test cleanup of old reports"""
    # Mock query
    mock_query = MagicMock()
    mock_reporte.query.filter.return_value.delete.return_value = 5
    mock_db.session = MagicMock()

    cleanup_old_reports()

    # Verify delete was called
    mock_reporte.query.filter.return_value.delete.assert_called_once_with()
    mock_db.session.commit.assert_called_once()
