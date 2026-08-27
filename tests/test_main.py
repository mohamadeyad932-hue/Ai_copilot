import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_check_endpoint():
    """Test GET /health endpoint returns HTTP 200 and expected payload structure."""
    response = client.get("/health")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "ok"
    assert "app_name" in data
    assert "version" in data
    assert "uptime_seconds" in data
    assert isinstance(data["uptime_seconds"], (int, float))


def test_middleware_process_time_header():
    """Test custom HTTP middleware adds X-Process-Time-Ms header to response."""
    response = client.get("/health")
    assert response.status_code == 200
    assert "X-Process-Time-Ms" in response.headers
    # Verify the duration header can be parsed as a float
    duration = float(response.headers["X-Process-Time-Ms"])
    assert duration >= 0.0


def test_analyze_text_valid_input():
    """Test POST /api/v1/analyze-text with valid text input."""
    payload = {
        "text": "Hello world!\nFastAPI is clean and efficient."
    }
    response = client.post("/api/v1/analyze-text", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert data["char_count"] == len(payload["text"])
    assert data["word_count"] == 7
    assert data["line_count"] == 2
    assert data["uppercase_text"] == payload["text"].upper()
    assert data["is_alphanumeric"] is False  # Contains punctuation '!' and '.'
    assert data["estimated_reading_time_minutes"] == round(7 / 200.0, 2)


def test_analyze_text_alphanumeric_input():
    """Test POST /api/v1/analyze-text with strictly alphanumeric input."""
    payload = {
        "text": "Python311 FastAPI2026"
    }
    response = client.post("/api/v1/analyze-text", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert data["word_count"] == 2
    assert data["is_alphanumeric"] is True


def test_analyze_text_whitespace_only():
    """Test POST /api/v1/analyze-text with whitespace-only input returns 400 Bad Request."""
    payload = {
        "text": "   \n\t  "
    }
    response = client.post("/api/v1/analyze-text", json=payload)
    assert response.status_code == 400
    assert response.json()["detail"] == "Text cannot be empty or contain only whitespace."


def test_analyze_text_empty_string():
    """Test POST /api/v1/analyze-text with empty string returns 422 Unprocessable Entity (min_length=1)."""
    payload = {
        "text": ""
    }
    response = client.post("/api/v1/analyze-text", json=payload)
    assert response.status_code == 422


def test_analyze_text_exceeding_max_length():
    """Test POST /api/v1/analyze-text with string > 10,000 chars returns 422 Unprocessable Entity."""
    long_text = "a" * 10001
    payload = {
        "text": long_text
    }
    response = client.post("/api/v1/analyze-text", json=payload)
    assert response.status_code == 422
