import pytest
from fastapi.testclient import TestClient
from api import httpapi

client = TestClient(httpapi)

# ---------------------------------------------------------------------------------------------------------------------------
# HEALTH CHECK API

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == "OK"


# ---------------------------------------------------------------------------------------------------------------------------
# USER REGISTER API

def test_user_register_invalid_password():
    response = client.post(
        "/auth/register",
        headers={"Content-Type": "application/json"},
        json={
            "email": "john@example.com",
            "password": "PASSWORD"
        })
    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {
                "loc": [
                    "body",
                    "password"
                ],
                "msg": "the password require length 8-32 characters, at least one letter and one number and one special characters",
                "type": "value_error"
            }
        ]
    }


def test_user_register_invalid_email():
    response = client.post(
        "/auth/register",
        headers={"Content-Type": "application/json"},
        json={
            "email": "john@example",
            "password": "P@ssw0rdOK"
        })
    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {
                "loc": [
                    "body",
                    "email"
                ],
                "msg": "invalid email format",
                "type": "value_error"
            }
        ]
    }


def test_new_user_register():
    response = client.post(
        "/auth/register",
        headers={"Content-Type": "application/json"},
        json={
            "email": "john@example.com",
            "password": "P@ssw0rdOK"
        })
    assert response.status_code == 200
    assert response.json() == {
        "status": "passed",
        "detail": None
        }


def test_existing_user_register():
    response = client.post(
        "/auth/register",
        headers={"Content-Type": "application/json"},
        json={
            "email": "john@example.com",
            "password": "P@ssw0rdOK"
        })
    assert response.status_code == 409
    assert response.json() == {
        "status": "failed",
        "detail": "existing user"
        }


# ---------------------------------------------------------------------------------------------------------------------------
# USER LOGIN API

def test_non_user_login():
    response = client.post(
        "/auth/login",
        headers={"Content-Type": "application/json"},
        json={
            "email": "johndoe@example.com",
            "password": "123456789"
        })
    assert response.status_code == 404
    assert response.json() == {"status": "failed", "detail": "user not found"}


def test_wrong_password_login():
    response = client.post(
        "/auth/login",
        headers={"Content-Type": "application/json"},
        json={
            "email": "john@example.com",
            "password": "P@ssw0rdOK111"
        })
    assert response.status_code == 403
    assert response.json() == {
        "status": "failed",
        "detail": "wrong password or email address"
        }


def test_user_login():
    response = client.post(
        "/auth/login",
        headers={"Content-Type": "application/json"},
        json={
            "email": "john@example.com",
            "password": "P@ssw0rdOK"
        })
    pytest.jwttoken = response.json().get('token')
    assert response.status_code == 200


# ---------------------------------------------------------------------------------------------------------------------------
# UPDATE USER API

def test_user_change_password_invalid_token():
    response = client.put(
        "/auth/users",
        headers={"Content-Type": "application/json",
                 "Authorization": "Bearer invalid-token"},
        json={
            "email": "john@example.com",
            "current_password": "P@ssw0rdOK",
            "new_password": "P@ssw0rdOK",
        })
    assert response.status_code == 403
    assert response.json() == {
        "detail": "expired token or invalid token"
        }


def test_user_change_password_mismatch_email():
    response = client.put(
        "/auth/users",
        headers={"Content-Type": "application/json",
                 "Authorization": f"Bearer {pytest.jwttoken}"},
        json={
            "email": "johndoe@example.com",
            "current_password": "P@ssw0rdOK",
            "new_password": "P@ssw0rdOK123",
        })
    assert response.status_code == 400
    assert response.json() == {
        "status": "failed",
        "detail": "bad request"
        }


def test_user_change_password_wrong_current_password():
    response = client.put(
        "/auth/users",
        headers={"Content-Type": "application/json",
                 "Authorization": f"Bearer {pytest.jwttoken}"},
        json={
            "email": "john@example.com",
            "current_password": "P@ssw0rdOK123",
            "new_password": "P@ssw0rdOK",
        })
    assert response.status_code == 403
    assert response.json() == {
        "status": "failed",
        "detail": "current password is not corect"
        }


def test_user_change_password():
    response = client.put(
        "/auth/users",
        headers={"Content-Type": "application/json",
                 "Authorization": f"Bearer {pytest.jwttoken}"},
        json={
            "email": "john@example.com",
            "current_password": "P@ssw0rdOK",
            "new_password": "P@ssw0rdOK123",
        })
    assert response.status_code == 200
    assert response.json() == {
        "status": "passed",
        "detail": None
        }

    response = client.post(
        "/auth/login",
        headers={"Content-Type": "application/json"},
        json={
            "email": "john@example.com",
            "password": "P@ssw0rdOK123"
        })
    assert response.status_code == 200


def test_delete_user():
    # clean up test data which has been created by this run
    # ensure next run will not be failed by dirty data
    response = client.delete(
        "/auth/users",
        headers={"Content-Type": "application/json",
                 "Authorization": f"Bearer {pytest.jwttoken}"},
        json={
            "email": "john@example.com",
            "password": "P@ssw0rdOK123",
        })
    assert response.status_code == 200
    assert response.json() == {
        "status": "passed",
        "detail": None
        }
