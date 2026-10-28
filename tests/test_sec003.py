import pytest
from fastapi.testclient import TestClient
from api.main import app, get_current_active_user, get_db
from api.main import ml_models

client = TestClient(app)

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
def override_deps():
    app.dependency_overrides[get_current_active_user] = lambda: type("User", (), {"id": 1})()
    app.dependency_overrides[get_db] = lambda: None
    ml_models["predictor"] = DummyPredictor()
    yield
    app.dependency_overrides.clear()

def test_1_valid():
    response = client.post("/predict", json={
        "sender": "a@example.com",
        "receiver": "b@example.com",
        "subject": "Test",
        "body": "Test body",
        "source": "web"
    })
    assert response.status_code == 200

def test_2_body_at_max():
    response = client.post("/predict", json={
        "sender": "a@example.com",
        "receiver": "b@example.com",
        "subject": "Test",
        "body": "x" * 50000,
        "source": "web"
    })
    assert response.status_code == 200

def test_3_body_above_max():
    response = client.post("/predict", json={
        "sender": "a@example.com",
        "receiver": "b@example.com",
        "subject": "Test",
        "body": "x" * 50001,
        "source": "web"
    })
    assert response.status_code == 422

def test_4_subject_above_max():
    response = client.post("/predict", json={
        "sender": "a@example.com",
        "receiver": "b@example.com",
        "subject": "x" * 999,
        "body": "Test",
        "source": "web"
    })
    assert response.status_code == 422

def test_5_sender_above_max():
    response = client.post("/predict", json={
        "sender": "x" * 321,
        "receiver": "b@example.com",
        "subject": "Test",
        "body": "Test",
        "source": "web"
    })
    assert response.status_code == 422

def test_6_receiver_above_max():
    response = client.post("/predict", json={
        "sender": "a@example.com",
        "receiver": "x" * 321,
        "subject": "Test",
        "body": "Test",
        "source": "web"
    })
    assert response.status_code == 422

def test_7_oversized_input_does_not_reach_predictor():
    class TrackingPredictor(DummyPredictor):
        def __init__(self):
            self.called = False
        def predict(self, sender, receiver, subject, body):
            self.called = True
            return super().predict(sender, receiver, subject, body)
            
    tracker = TrackingPredictor()
    ml_models["predictor"] = tracker
    
    response = client.post("/predict", json={
        "sender": "a@example.com",
        "receiver": "b@example.com",
        "subject": "Test",
        "body": "x" * 50001,
        "source": "web"
    })
    
    assert response.status_code == 422
    assert tracker.called is False
    
    # Verify it normally would be called
    tracker.called = False
    response = client.post("/predict", json={
        "sender": "a@example.com",
        "receiver": "b@example.com",
        "subject": "Test",
        "body": "Test body",
        "source": "web"
    })
    assert response.status_code == 200
    assert tracker.called is True
