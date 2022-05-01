import random
from sqlalchemy.orm import Session
from config import DEFAULT_TOKEN_EXPIRY
from utils import get_hashed_password, verify_password, generate_jwt_token, validate_jwt_token


EMAIL = 'alice@example.com'
PASSWORD = 'P@ssw0rdOK'
HPASSWORD = '$2b$12$ElKEYvzzbadvQEn39F7xdOuZfR0qRDdYykfJTr4YgR8OkF.wc0f3G'


def randomstr(size=8, chars='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789abcdefghijklmnopqrstuvwxyz!@#'):
    return ''.join(random.choice(chars) for _ in range(size))


def test_password_function():
    plain_password = randomstr(16)
    hashed_password = get_hashed_password(plain_password).decode()
    assert verify_password(plain_password, hashed_password)


def test_password_function_compatible():
    assert verify_password('P@ssw0rdOK', '$2b$12$ElKEYvzzbadvQEn39F7xdOuZfR0qRDdYykfJTr4YgR8OkF.wc0f3G')


def test_jwt_token():
    token = generate_jwt_token(EMAIL)
    payload = validate_jwt_token(token)

    assert payload.get('email') == EMAIL
    assert payload.get('exp') - payload.get('iat') == DEFAULT_TOKEN_EXPIRY
