"""Authentication and profile API tests."""

import pytest

from app.services.auth_service import AuthService

REGISTER_BODY = {
    "full_name": "Jane Doe",
    "email": "jane@example.com",
    "password": "StrongPass1",
}


def _register(client):
    resp = client.post("/api/auth/register", json=REGISTER_BODY)
    return resp


def test_register_success(client):
    resp = _register(client)
    assert resp.status_code == 201
    data = resp.json()["data"]
    assert data["access_token"]
    assert data["refresh_token"]
    assert data["user"]["email"] == "jane@example.com"


def test_register_duplicate_email(client):
    _register(client)
    resp = _register(client)
    assert resp.status_code == 409


def test_register_weak_password(client):
    resp = client.post(
        "/api/auth/register",
        json={**REGISTER_BODY, "password": "short"},
    )
    assert resp.status_code == 422


def test_login_success(client):
    _register(client)
    resp = client.post(
        "/api/auth/login",
        json={"email": "jane@example.com", "password": "StrongPass1"},
    )
    assert resp.status_code == 200
    assert resp.json()["data"]["user"]["full_name"] == "Jane Doe"


def test_login_wrong_password(client):
    _register(client)
    resp = client.post(
        "/api/auth/login",
        json={"email": "jane@example.com", "password": "WrongPass1"},
    )
    assert resp.status_code == 401


def test_profile_requires_auth(client):
    resp = client.get("/api/profile")
    assert resp.status_code == 401


def test_profile_flow(client):
    _register(client)
    token = client.post(
        "/api/auth/login",
        json={"email": "jane@example.com", "password": "StrongPass1"},
    ).json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    resp = client.get("/api/profile", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["data"]["email"] == "jane@example.com"

    resp = client.put(
        "/api/profile",
        headers=headers,
        json={
            "full_name": "Jane Updated",
            "profile": {"age": 29, "gender": "female", "height_cm": 168, "weight_kg": 60},
        },
    )
    assert resp.status_code == 200
    assert resp.json()["data"]["age"] == 29
    assert resp.json()["data"]["full_name"] == "Jane Updated"


def test_refresh_token_flow(client):
    _register(client)
    refresh = client.post(
        "/api/auth/login",
        json={"email": "jane@example.com", "password": "StrongPass1"},
    ).json()["data"]["refresh_token"]
    resp = client.post("/api/auth/refresh", json={"refresh_token": refresh})
    assert resp.status_code == 200
    assert resp.json()["data"]["access_token"]


def test_logout_revokes_session(client, db):
    _register(client)
    login = client.post(
        "/api/auth/login",
        json={"email": "jane@example.com", "password": "StrongPass1"},
    ).json()["data"]
    headers = {"Authorization": f"Bearer {login['access_token']}"}

    resp = client.post("/api/auth/logout", headers=headers, json={"refresh_token": login["refresh_token"]})
    assert resp.status_code == 200

    # The same refresh token must no longer work
    resp = client.post("/api/auth/refresh", json={"refresh_token": login["refresh_token"]})
    assert resp.status_code == 401


def test_admin_endpoint_rejected_for_patient(client):
    _register(client)
    token = client.post(
        "/api/auth/login",
        json={"email": "jane@example.com", "password": "StrongPass1"},
    ).json()["data"]["access_token"]
    resp = client.get("/api/admin/dashboard", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 403
