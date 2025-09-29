from unittest.mock import AsyncMock, patch
import pytest
from app.models.user import User
from app.schemas.user import SchemaUserCreate, UserPublic
from app.exceptions.base import EmailAlreadyRegisteredError
from app.api.v1.user import read_users_me
from app.api.v1.auth import register_user


@pytest.mark.asyncio
@patch("app.api.v1.auth.UserService")
async def test_register_user_success(mock_user_service_class):
    # Arrange
    mock_service = AsyncMock()
    mock_service.create_user = AsyncMock(return_value=UserPublic(
        id="123e4567-e89b-12d3-a456-426614174000",
        is_active=True
    ))
    mock_user_service_class.return_value = mock_service

    user_in = SchemaUserCreate(
        email="new@test.com",
        password="pass123",
        password_confirm="pass123",
        first_name="Newxx",
        last_name="Userxx"
    )
    db_mock = AsyncMock()

    # Act
    result = await register_user(user_in, db=db_mock)

    # Assert
    assert result.is_active is True
    assert str(result.id) == "123e4567-e89b-12d3-a456-426614174000"

@pytest.mark.asyncio
@patch("app.api.v1.auth.UserService")
async def test_register_user_duplicate_email(mock_user_service_class):
    mock_service = AsyncMock()
    mock_service.create_user = AsyncMock(side_effect=EmailAlreadyRegisteredError())
    mock_user_service_class.return_value = mock_service

    user_in = SchemaUserCreate(
        email="dup@test.com",
        password="pass123",
        password_confirm="pass123",
        first_name="Dupxx",
        last_name="Userxx"
    )
    db_mock = AsyncMock()

    # Act & Assert
    with pytest.raises(EmailAlreadyRegisteredError):
        await register_user(user_in, db=db_mock)


@pytest.mark.asyncio
async def test_read_users_me():
    mock_user = User(
        id="123e4567-e89b-12d3-a456-426614174000",
        email="test@test.com",
        password="hashedpass123",
        is_active=True,
        first_name="Alice",
        last_name="Johnson"
    )
    result = await read_users_me(current_user=mock_user)
    assert str(result.id) == "123e4567-e89b-12d3-a456-426614174000"
    assert result.is_active is True
