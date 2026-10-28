import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

import sys
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

from api.main import app, ml_models
from api.auth import get_current_active_user, get_current_admin_user
from api.database import get_db

# Create a mock user that has an ID
mock_user = MagicMock()
mock_user.id = 1
mock_user.username = "testuser"
mock_user.role = "user"

mock_admin = MagicMock()
mock_admin.id = 2
mock_admin.username = "admin"
mock_admin.role = "admin"

# Override Depends for DB/Auth just to test the pure endpoint prediction behavior
app.dependency_overrides[get_current_active_user] = lambda: mock_user
app.dependency_overrides[get_db] = lambda: MagicMock()

client = TestClient(app)

def test_health_check_available():
    ml_models["predictor"] = MagicMock()
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_health_check_unavailable():
    ml_models.pop("predictor", None)
    response = client.get("/health")
    # Our updated health check returns 200 with degraded, or 503 if api is offline
    assert response.status_code in (200, 503)

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200

def test_predict_normal_email():
    with TestClient(app) as live_client:
        payload = {
            "sender": "security@example.com",
            "receiver": "user@gmail.com",
            "subject": "Verify your account",
            "body": "Please verify your account."
        }
        response = live_client.post("/predict", json=payload)
        
        assert response.status_code == 200, response.text
        data = response.json()
        assert "label" in data
        assert "phishing_probability" in data
        assert "risk_score" in data

def test_predict_suspicious_email():
    with TestClient(app) as live_client:
        payload = {
            "sender": "admin@paypal-update-info.com",
            "receiver": "victim@gmail.com",
            "subject": "URGENT: Account locked",
            "body": "Click here to unlock http://malicious.com"
        }
        response = live_client.post("/predict", json=payload)
        assert response.status_code == 200

def test_predict_missing_fields():
    with TestClient(app) as live_client:
        payload = {
            "sender": "test@test.com"
        }
        response = live_client.post("/predict", json=payload)
        assert response.status_code == 422

def test_predictor_singleton():
    with TestClient(app) as live_client:
        response1 = live_client.post("/predict", json={"sender": "", "receiver": "", "subject": "", "body": "Hello"})
        assert response1.status_code == 200
        
        response2 = live_client.post("/predict", json={"sender": "", "receiver": "", "subject": "", "body": "World"})
        assert response2.status_code == 200
        
        predictor_instance = ml_models["predictor"]
        assert predictor_instance is not None

# ==============================================================
# NEW AUTHENTICATION AND ROLE TESTS
# ==============================================================

# Note: We create a fresh client without dependency overrides for auth tests
def test_auth_and_roles():
    app.dependency_overrides.clear()
    real_client = TestClient(app)
    
    # 1. Register a new user
    reg_response = real_client.post("/auth/register", json={
        "username": "testauthuser",
        "password": "testpassword"
    })
    
    if reg_response.status_code == 400 and "already registered" in reg_response.text:
        pass # Already exists from previous run, that's fine
    else:
        assert reg_response.status_code == 200
        data = reg_response.json()
        assert data["username"] == "testauthuser"
        assert data["role"] == "user" # Ensure role is forced to user
        
    # 2. Login
    login_response = real_client.post("/auth/login", data={
        "username": "testauthuser",
        "password": "testpassword"
    })
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    
    # 3. Access user endpoint
    me_response = real_client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_response.status_code == 200
    assert me_response.json()["username"] == "testauthuser"
    
    # 4. Attempt to access admin endpoint (should fail)
    admin_response = real_client.get("/admin/stats", headers={"Authorization": f"Bearer {token}"})
    assert admin_response.status_code == 403
    
    # 5. Admin Login (default admin created on init)
    admin_login = real_client.post("/auth/login", data={
        "username": "admin",
        "password": "adminpassword"
    })
    assert admin_login.status_code == 200
    admin_token = admin_login.json()["access_token"]
    
    # 6. Admin accessing admin endpoint (should succeed)
    admin_stats_response = real_client.get("/admin/stats", headers={"Authorization": f"Bearer {admin_token}"})
    assert admin_stats_response.status_code == 200
    assert "total_scans" in admin_stats_response.json()
    
    # 7. Isolated History Check
    events_response = real_client.get("/events", headers={"Authorization": f"Bearer {token}"})
    assert events_response.status_code == 200
    assert isinstance(events_response.json(), list)

    # 8. Unauthenticated access should fail
    fail_response = TestClient(app).get("/events")
    assert fail_response.status_code == 401

def test_unauthenticated_endpoints():
    app.dependency_overrides.clear()
    
    assert TestClient(app).get("/dashboard/recent").status_code == 401
    assert TestClient(app).get("/reports/generate").status_code == 401

def test_pagination_and_isolation():
    app.dependency_overrides.clear()
    
    # Needs context manager for predictor
    with TestClient(app) as _:
        clientA = TestClient(app)
        clientB = TestClient(app)
        admin_client = TestClient(app)
        
        # User A
        clientA.post("/auth/register", json={"username": "userA_iso", "password": "pwd"})
        tokenA = clientA.post("/auth/login", data={"username": "userA_iso", "password": "pwd"}).json()["access_token"]
        headersA = {"Authorization": f"Bearer {tokenA}"}

        # User B
        clientB.post("/auth/register", json={"username": "userB_iso", "password": "pwd", "role": "admin"})
        tokenB = clientB.post("/auth/login", data={"username": "userB_iso", "password": "pwd"}).json()["access_token"]
        headersB = {"Authorization": f"Bearer {tokenB}"}

        # B is not an admin
        b_info = clientB.get("/auth/me", headers=headersB).json()
        assert b_info["role"] == "user"

        # User A creates a scan
        clientA.post("/predict", json={"sender": "a@a.com", "receiver": "b@b.com", "subject": "a", "body": "a"}, headers=headersA)
        clientA.post("/predict", json={"sender": "a2@a.com", "receiver": "b@b.com", "subject": "a", "body": "a"}, headers=headersA)

        # Check User A's events with offset
        events_A = clientA.get("/events?limit=1&offset=1", headers=headersA).json()
        assert len(events_A) == 1

        # Check User B's events (should be empty, isolation)
        events_B = clientB.get("/events", headers=headersB).json()
        assert len(events_B) == 0

        # Check Admin access to pagination
        admin_client.post("/auth/login", data={"username": "admin", "password": "adminpassword"}).json()["access_token"]
        admin_scans = admin_client.get("/admin/scans?limit=1&offset=0").json()
        assert len(admin_scans) == 1
