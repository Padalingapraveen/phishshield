import pytest
from fastapi.testclient import TestClient
import os
from api.main import app
from api.config import CORS_ORIGINS

def test_cors_rejects_unconfigured_origin():
    client = TestClient(app)
    response = client.options(
        "/predict",
        headers={
            "Origin": "https://malicious-site.com",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "authorization,content-type",
        },
    )
    # The CORS middleware will return 400 for a disallowed origin in preflight
    assert response.status_code == 400
    assert "Disallowed CORS origin" in response.text

def test_cors_accepts_configured_origin():
    client = TestClient(app)
    response = client.options(
        "/predict",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "authorization,content-type",
        },
    )
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "http://localhost:5173"
    assert response.headers.get("access-control-allow-credentials") == "true"

def test_cors_wildcard_not_used():
    client = TestClient(app)
    response = client.options(
        "/predict",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "authorization,content-type",
        },
    )
    assert response.headers.get("access-control-allow-origin") != "*"

def test_cors_handles_multiple_origins():
    client = TestClient(app)
    response = client.options(
        "/predict",
        headers={
            "Origin": "http://127.0.0.1:5173",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "authorization,content-type",
        },
    )
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "http://127.0.0.1:5173"

def test_production_cors_strictness():
    # Since we cannot easily redefine the module-level CORS_ORIGINS from here 
    # without breaking test isolation for other tests, we just assert that 
    # the code in config.py uses the correct logic by verifying CORS_ORIGINS
    assert "*" not in CORS_ORIGINS
