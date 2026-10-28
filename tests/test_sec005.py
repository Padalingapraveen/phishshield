import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_login_sets_cookie():
    response = client.post(
        "/auth/login",
        data={"username": "admin", "password": "adminpassword"},
        headers={"Origin": "http://localhost:5173"}
    )
    assert response.status_code == 200
    
    # Verify cookie is set with HttpOnly
    cookies = response.cookies
    assert "access_token" in cookies
    
    # We can inspect the raw Set-Cookie header to check HttpOnly
    set_cookie_header = response.headers.get("set-cookie", "")
    assert "HttpOnly" in set_cookie_header
    assert "SameSite=lax" in set_cookie_header

def test_web_dashboard_no_token_in_json():
    response = client.post(
        "/auth/login",
        data={"username": "admin", "password": "adminpassword"},
        headers={"Origin": "http://localhost:5173"}
    )
    assert response.status_code == 200
    json_data = response.json()
    assert "access_token" not in json_data
    assert json_data.get("message") == "Logged in successfully"

def test_extension_receives_token():
    response = client.post(
        "/auth/login",
        data={"username": "admin", "password": "adminpassword"},
        headers={"Origin": "chrome-extension://abcdefgh"}
    )
    assert response.status_code == 200
    json_data = response.json()
    assert "access_token" in json_data
    assert json_data["token_type"] == "bearer"

def test_auth_me_with_cookie():
    # Login first
    login_response = client.post(
        "/auth/login",
        data={"username": "admin", "password": "adminpassword"},
        headers={"Origin": "http://localhost:5173"}
    )
    cookie_token = login_response.cookies.get("access_token")
    
    # Call /auth/me with cookie
    response = client.get(
        "/auth/me",
        cookies={"access_token": cookie_token}
    )
    assert response.status_code == 200
    assert response.json()["username"] == "admin"

def test_auth_me_fails_without_cookie_or_header():
    client.cookies.clear()
    response = client.get("/auth/me")
    assert response.status_code == 401

def test_logout_clears_cookie():
    response = client.post("/auth/logout")
    assert response.status_code == 200
    set_cookie_header = response.headers.get("set-cookie", "")
    assert "access_token=" in set_cookie_header
    # Depending on Starlette version, deleting a cookie sets max-age=0 or expires in the past
    assert "Max-Age=0" in set_cookie_header or "expires=" in set_cookie_header.lower()
