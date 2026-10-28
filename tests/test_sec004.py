import os
import pytest
from fastapi.testclient import TestClient
from api.main import app, get_current_active_user, get_db
from api.main import ml_models
from api.database import Base, engine, SessionLocal
from api.models import User
from api.auth import get_password_hash

# Set up test database
Base.metadata.create_all(bind=engine)

def get_test_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Mock the predictor
class DummyPredictor:
    def predict(self, sender, receiver, subject, body):
        return {
            "label": "Safe",
            "predicted_class": 0,
            "phishing_probability": 0.1,
            "non_phishing_probability": 0.9,
            "risk_score": 0.1,
            "graph_neighbors": 0,
            "graph_edge_types": {},
            "sender_entity": "mock",
            "receiver_entity": "mock",
            "domain_entities": {}
        }

@pytest.fixture(autouse=True)
def setup_test_state():
    # Setup db and predictor
    app.dependency_overrides[get_db] = get_test_db
    ml_models["predictor"] = DummyPredictor()
    
    # Create test user for login and prediction tests
    db = SessionLocal()
    user = db.query(User).filter(User.username == "ratelimit_user").first()
    if not user:
        hashed_pw = get_password_hash("password")
        user = User(username="ratelimit_user", hashed_password=hashed_pw, role="user", is_active=True)
        db.add(user)
        db.commit()
    db.close()
    
    yield
    app.dependency_overrides.clear()

def test_1_register_rate_limit():
    # We will clear the limiter's storage to ensure a clean state
    app.state.limiter.reset()
    client = TestClient(app)
    
    import uuid
    random_id = uuid.uuid4().hex[:8]
    
    # In config, it's 3/minute. We can just hit it 4 times.
    for i in range(3):
        response = client.post("/auth/register", json={
            "username": f"new_user_{random_id}_{i}",
            "password": "password"
        })
        # The first few should succeed
        assert response.status_code == 200, response.text
        
    # The 4th should fail with 429
    response = client.post("/auth/register", json={
        "username": f"new_user_{random_id}_4",
        "password": "password"
    })
    assert response.status_code == 429
    assert "error" in response.json()
    assert "Rate limit exceeded" in response.json()["error"]
    # Check that secrets are not exposed
    assert "test-secret" not in response.text
    
def test_2_login_rate_limit():
    app.state.limiter.reset()
    client = TestClient(app)
    
    # Limit is 5/minute.
    for i in range(5):
        response = client.post("/auth/login", data={
            "username": "ratelimit_user",
            "password": "password"
        })
        assert response.status_code == 200
        
    # 6th should fail
    response = client.post("/auth/login", data={
        "username": "ratelimit_user",
        "password": "password"
    })
    assert response.status_code == 429

def test_3_predict_rate_limit():
    app.state.limiter.reset()
    client = TestClient(app)
    
    # To test predict limit (100/minute) easily without waiting, we can mock the current active user
    app.dependency_overrides[get_current_active_user] = lambda: type("User", (), {"id": 1})()
    
    # Instead of hitting 100 times, let's just do a smaller loop since 100 requests in test client takes ~100ms
    for i in range(100):
        response = client.post("/predict", json={
            "sender": "a@example.com",
            "receiver": "b@example.com",
            "subject": "Test",
            "body": "Test body",
            "source": "web"
        })
        assert response.status_code == 200
        
    # 101th should fail
    response = client.post("/predict", json={
        "sender": "a@example.com",
        "receiver": "b@example.com",
        "subject": "Test",
        "body": "Test body",
        "source": "web"
    })
    assert response.status_code == 429

if __name__ == "__main__":
    pytest.main([__file__])
