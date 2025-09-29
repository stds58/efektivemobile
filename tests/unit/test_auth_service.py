from datetime import timedelta
from app.services.auth_service import AuthService


def test_verify_password_correct():
    plain = "mypassword"
    hashed = AuthService.get_password_hash(plain)
    assert AuthService.verify_password(plain, hashed) is True

def test_verify_password_incorrect():
    hashed = AuthService.get_password_hash("real")
    assert AuthService.verify_password("fake", hashed) is False

def test_create_and_decode_token():
    data = {"sub": "12345"}
    token = AuthService.create_access_token(data, expires_delta=timedelta(minutes=5))
    payload = AuthService.decode_access_token(token)
    assert payload["sub"] == "12345"
    assert "exp" in payload

def test_decode_invalid_token():
    payload = AuthService.decode_access_token("invalid.token.here")
    assert payload is None
