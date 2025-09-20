import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import User
from src.repository.users import UserRepository
from src.schemas import UserCreate


@pytest.fixture
def mock_session():
    return AsyncMock(spec=AsyncSession)


@pytest.fixture
def user_repository(mock_session):
    return UserRepository(mock_session)


@pytest.fixture
def user():
    return User(
        id=1, username="testuser", email="test@example.com", hashed_password="hashed"
    )


# ---------------------- get_user_by_id ----------------------
@pytest.mark.asyncio
async def test_get_user_by_id(user_repository, mock_session, user):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = user
    mock_session.execute = AsyncMock(return_value=mock_result)

    result = await user_repository.get_user_by_id(user_id=1)

    assert result is not None
    assert result.id == 1
    assert result.username == "testuser"


# ---------------------- get_user_by_username ----------------------
@pytest.mark.asyncio
async def test_get_user_by_username(user_repository, mock_session, user):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = user
    mock_session.execute = AsyncMock(return_value=mock_result)

    result = await user_repository.get_user_by_username(username="testuser")

    assert result is not None
    assert result.username == "testuser"


# ---------------------- get_user_by_email ----------------------
@pytest.mark.asyncio
async def test_get_user_by_email(user_repository, mock_session, user):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = user
    mock_session.execute = AsyncMock(return_value=mock_result)

    result = await user_repository.get_user_by_email(email="test@example.com")

    assert result is not None
    assert result.email == "test@example.com"


# ---------------------- create_user ----------------------
@pytest.mark.asyncio
async def test_create_user(user_repository, mock_session):
    user_data = UserCreate(
        username="newuser", email="new@example.com", password="secret123"
    )

    result = await user_repository.create_user(
        body=user_data, avatar="http://avatar.com/pic.png"
    )

    assert isinstance(result, User)
    assert result.username == "newuser"
    assert result.avatar == "http://avatar.com/pic.png"
    mock_session.add.assert_called_once()
    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once_with(result)


# ---------------------- confirmed_email ----------------------
@pytest.mark.asyncio
async def test_confirmed_email(user_repository, mock_session, user, monkeypatch):
    # Patch get_user_by_email to return our user
    async def fake_get_user_by_email(email: str):
        return user

    monkeypatch.setattr(user_repository, "get_user_by_email", fake_get_user_by_email)

    await user_repository.confirmed_email(email="test@example.com")

    assert user.confirmed is True
    mock_session.commit.assert_awaited_once()


# ---------------------- update_avatar_url ----------------------
@pytest.mark.asyncio
async def test_update_avatar_url(user_repository, mock_session, user, monkeypatch):
    async def fake_get_user_by_email(email: str):
        return user

    monkeypatch.setattr(user_repository, "get_user_by_email", fake_get_user_by_email)

    result = await user_repository.update_avatar_url(
        email="test@example.com", url="http://new.avatar"
    )

    assert result.avatar == "http://new.avatar"
    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once_with(user)
