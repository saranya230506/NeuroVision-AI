"""
Automated integration tests for Flask REST API and routes.
"""

import io
import pytest
from PIL import Image

from app import app
import config


@pytest.fixture
def client():
    """Create Flask test client."""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_homepage_route(client):
    """Verify homepage returns HTTP 200 and loads title."""
    response = client.get("/")
    assert response.status_code == 200
    assert b"NeuroVision" in response.data


def test_upload_page_route(client):
    """Verify upload page loads successfully."""
    response = client.get("/upload")
    assert response.status_code == 200
    assert b"Brain MRI Scanner" in response.data


def test_dashboard_route(client):
    """Verify analytics dashboard loads."""
    response = client.get("/dashboard")
    assert response.status_code == 200


def test_history_route(client):
    """Verify scan history page loads."""
    response = client.get("/history")
    assert response.status_code == 200


def test_about_route(client):
    """Verify technical specs about page loads."""
    response = client.get("/about")
    assert response.status_code == 200
    assert b"EfficientNetB0" in response.data


def test_api_health(client):
    """Verify healthcheck endpoint returns JSON healthy."""
    response = client.get("/api/health")
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data["status"] == "healthy"
    assert "service" in json_data


def test_api_stats(client):
    """Verify statistics API returns JSON data."""
    response = client.get("/api/stats")
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data["success"] is True
    assert "stats" in json_data


def test_api_sample_prediction(client):
    """Verify running prediction on pre-bundled sample."""
    sample_file = config.SAMPLES_DIR / "glioma_sample.jpg"
    if sample_file.exists():
        response = client.post("/api/sample/glioma")
        assert response.status_code == 200
        json_data = response.get_json()
        assert json_data["success"] is True
        assert json_data["predicted_class"] in config.CLASS_NAMES
        assert "confidence" in json_data
        assert "probabilities" in json_data
