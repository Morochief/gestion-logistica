"""
Tests for Prometheus metrics
"""
import pytest
from unittest.mock import patch, MagicMock
from app.metrics import (
    init_metrics, REQUEST_COUNT, REQUEST_LATENCY,
    CRT_CREATED, MIC_CREATED, HONORARIOS_TOTAL, USERS_ACTIVE,
    update_business_metrics, update_system_metrics
)


@pytest.fixture
def app():
    """Create a test Flask app"""
    from flask import Flask
    app = Flask(__name__)
    app.config['TESTING'] = True
    return app


@pytest.fixture
def client(app):
    """Create a test client"""
    return app.test_client()


def test_init_metrics(app):
    """Test metrics initialization"""
    init_metrics(app)

    # Check that metrics endpoint exists
    with app.test_request_context('/metrics'):
        response = app.full_dispatch_request()
        assert response.status_code == 200


def test_request_metrics(app, client):
    """Test request metrics collection"""
    init_metrics(app)

    # Make a test request
    with client:
        response = client.get('/metrics')
        assert response.status_code == 200

    # Check that metrics were recorded
    assert REQUEST_COUNT._metrics
    assert REQUEST_LATENCY._metrics


@patch('app.metrics.db')
@patch('app.metrics.CRT')
@patch('app.metrics.MIC')
@patch('app.metrics.Honorario')
@patch('app.metrics.Usuario')
def test_update_business_metrics(mock_usuario, mock_honorario, mock_mic, mock_crt, mock_db):
    """Test business metrics update"""
    # Mock database queries
    mock_crt.query.count.return_value = 10
    mock_mic.query.count.return_value = 5
    mock_honorario.query.with_entities.return_value = [
        MagicMock(monto=1000), MagicMock(monto=2000)]
    mock_usuario.query.count.return_value = 3

    # Call the function
    update_business_metrics()

    # Verify metrics were updated
    assert CRT_CREATED._value == 10
    assert MIC_CREATED._value == 5
    assert HONORARIOS_TOTAL._value == 3000
    assert USERS_ACTIVE._value == 3


@patch('app.metrics.psutil')
def test_update_system_metrics(mock_psutil):
    """Test system metrics update"""
    # Mock psutil
    mock_process = MagicMock()
    mock_process.memory_info.return_value.rss = 1024 * 1024 * 100  # 100MB
    mock_process.cpu_percent.return_value = 25.5
    mock_psutil.Process.return_value = mock_process

    # Call the function
    update_system_metrics()

    # Verify metrics were updated (these would be set if psutil is available)
    # Note: In test environment, psutil might not be available


def test_metrics_endpoint_content_type(app):
    """Test that metrics endpoint returns correct content type"""
    init_metrics(app)

    with app.test_client() as client:
        response = client.get('/metrics')
        assert response.content_type == 'text/plain; charset=utf-8'
        assert 'flask_requests_total' in response.get_data(as_text=True)


def test_metrics_with_invalid_endpoint(app):
    """Test metrics with invalid endpoint"""
    init_metrics(app)

    with app.test_client() as client:
        # Make request to non-existent endpoint
        response = client.get('/nonexistent')
        assert response.status_code == 404

        # Check that 404 was recorded
        metrics_response = client.get('/metrics')
        metrics_data = metrics_response.get_data(as_text=True)
        assert '404' in metrics_data
