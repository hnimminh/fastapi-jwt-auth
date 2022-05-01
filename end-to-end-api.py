import sys
import requests
import pytest

API_URL = sys.argv[0]
if API_URL:
    API_URL = 'http://159.223.42.21'

# ---------------------------------------------------------------------------------------------------------------------------
def test_health():
    response = requests.get(f"{API_URL}/health")
    assert response.status_code == 200
    assert response.json() == "OK"

# ---------------------------------------------------------------------------------------------------------------------------
# USER REGISTER API

def test_user_register_invalid_password():
    response = requests.post(
        f"{API_URL}/auth/register",
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
    response = requests.post(
        f"{API_URL}/auth/register",
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
    response = requests.post(
        f"{API_URL}/auth/register",
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
    response = requests.post(
        f"{API_URL}/auth/register",
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
    response = requests.post(
        f"{API_URL}/auth/login",
        headers={"Content-Type": "application/json"},
        json={
            "email": "johndoe@example.com",
            "password": "123456789"
        })
    assert response.status_code == 404
    assert response.json() == {"status": "failed", "detail": "user not found"}


def test_wrong_password_login():
    response = requests.post(
        f"{API_URL}/auth/login",
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
    response = requests.post(
        f"{API_URL}/auth/login",
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
    response = requests.put(
        f"{API_URL}/auth/users",
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
    response = requests.put(
        f"{API_URL}/auth/users",
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
    response = requests.put(
        f"{API_URL}/auth/users",
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
    response = requests.put(
        f"{API_URL}/auth/users",
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

    response = requests.post(
        f"{API_URL}/auth/login",
        headers={"Content-Type": "application/json"},
        json={
            "email": "john@example.com",
            "password": "P@ssw0rdOK123"
        })
    assert response.status_code == 200


def test_delete_user():
    # clean up test data which has been created by this run
    # ensure next run will not be failed by dirty data
    response = requests.delete(
        f"{API_URL}/auth/users",
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

