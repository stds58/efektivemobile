from unittest.mock import AsyncMock, MagicMock
import pytest
from app.crud.user import user as crud_user
from app.services.user import UserService
from app.schemas.user import SchemaUserCreate
from app.exceptions.base import EmailAlreadyRegisteredError, BadCredentialsError, UserInactiveError
from app.models.user import User
from app.services.auth.password import get_password_hash


# pylint: disable=redefined-outer-name

@pytest.fixture
def mock_db_session():
    return AsyncMock()

@pytest.fixture
def user_service(mock_db_session):
    return UserService(mock_db_session)

@pytest.mark.asyncio
async def test_create_user_success(user_service, mock_db_session):
    user_in = SchemaUserCreate(
        email="test@example.com",
        password="pass123",
        password_confirm="pass123",
        first_name="Testxx",
        last_name="Userxx"
    )

    # Мокаем: нет существующего пользователя
    mock_result_empty = MagicMock()
    mock_result_empty.scalars().first.return_value = None
    mock_db_session.execute = AsyncMock(return_value=mock_result_empty)

    # Мокаем создание через CRUD
    with pytest.MonkeyPatch.context() as mp:
        mock_create = AsyncMock(return_value=User(
            id="123e4567-e89b-12d3-a456-426614174000",
            email="test@example.com",
            password=get_password_hash("pass123"),
            first_name="Alice",
            last_name="Johnson",
            is_active=True
        ))
        mp.setattr(crud_user, 'create', mock_create)

        result = await user_service.create_user(user_in)

    assert str(result.id) == "123e4567-e89b-12d3-a456-426614174000"
    assert result.is_active is True

@pytest.mark.asyncio
async def test_create_user_email_exists(user_service, mock_db_session):
    user_in = SchemaUserCreate(
        email="exists@example.com",
        password="pass123",
        password_confirm="pass123",
        first_name="Alice",
        last_name="Smith"
    )

    existing_user = User(
        id="uuid", email="exists@example.com",
        password="hash", is_active=True
    )
    mock_result = MagicMock()
    mock_result.scalars().first.return_value = existing_user
    mock_db_session.execute = AsyncMock(return_value=mock_result)

    with pytest.raises(EmailAlreadyRegisteredError):
        await user_service.create_user(user_in)

@pytest.mark.asyncio
async def test_authenticate_user_success(user_service, mock_db_session):
    email = "auth@example.com"
    password = "secret"
    hashed = get_password_hash(password)
    user = User(id="123e4567-e89b-12d3-a456-426614174000", email=email, password=hashed, is_active=True)

    mock_result = MagicMock()
    mock_result.scalars().first.return_value = user
    mock_db_session.execute = AsyncMock(return_value=mock_result)

    result = await user_service.authenticate_user(email, password)
    assert result.email == email

@pytest.mark.asyncio
async def test_authenticate_user_wrong_password(user_service, mock_db_session):
    user = User(email="badpass@example.com", password=get_password_hash("realpass"), is_active=True)
    mock_result = MagicMock()
    mock_result.scalars().first.return_value = user
    mock_db_session.execute = AsyncMock(return_value=mock_result)

    with pytest.raises(BadCredentialsError):
        await user_service.authenticate_user("badpass@example.com", "wrong")

@pytest.mark.asyncio
async def test_authenticate_user_inactive(user_service, mock_db_session):
    user = User(email="inactive@example.com", password=get_password_hash("pass"), is_active=False)
    mock_result = MagicMock()
    mock_result.scalars().first.return_value = user
    mock_db_session.execute = AsyncMock(return_value=mock_result)

    with pytest.raises(UserInactiveError):
        await user_service.authenticate_user("inactive@example.com", "pass")
