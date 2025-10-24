from datetime import timedelta
from app.services.auth.tokens import create_access_token, decode_access_token, create_refresh_token, decode_refresh_token
from app.services.auth.password import verify_password, get_password_hash
from app.services.auth.blacklist import token_blacklist


def test_verify_password_correct():
    plain = "mypassword"
    hashed = get_password_hash(plain)
    assert verify_password(plain, hashed) is True

def test_verify_password_incorrect():
    hashed = get_password_hash("real")
    assert verify_password("fake", hashed) is False

def test_create_and_decode_token():
    data = {"sub": "12345"}
    token = create_access_token(data, expires_delta=timedelta(minutes=5))
    payload = decode_access_token(token)
    assert payload["sub"] == "12345"
    assert "exp" in payload

def test_decode_invalid_token():
    payload = decode_access_token("invalid.token.here")
    assert payload is None
