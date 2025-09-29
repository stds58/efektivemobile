from unittest.mock import AsyncMock, patch
import pytest
from app.models.user import User
from app.dependencies.get_current_user import get_current_user


@pytest.mark.asyncio
async def test_get_current_user_success():
    token = "valid.jwt.token"
    payload = {"sub": "123e4567-e89b-12d3-a456-426614174000"}

    with patch("app.dependencies.get_current_user.jwt.decode", return_value=payload):
        mock_user = User(id=payload["sub"], email="test@test.com", is_active=True)
        with patch("app.services.user.UserService.get_user_by_id", AsyncMock(return_value=mock_user)):
            db_mock = AsyncMock()
            user = await get_current_user(token, db_mock)
            assert str(user.id) == payload["sub"]
