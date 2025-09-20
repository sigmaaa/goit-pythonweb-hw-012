import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Contact, User
from src.repository.contacts import ContactRepository
from src.schemas import ContactBase


@pytest.fixture
def mock_session():
    return AsyncMock(spec=AsyncSession)


@pytest.fixture
def contact_repository(mock_session):
    return ContactRepository(mock_session)


@pytest.fixture
def user():
    return User(id=1, username="testuser")


@pytest.mark.asyncio
async def test_get_contacts(contact_repository, mock_session, user):
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [
        Contact(id=1, name="test contact", user=user)
    ]
    mock_session.execute = AsyncMock(return_value=mock_result)

    contacts = await contact_repository.get_contacts(skip=0, limit=10, user=user)

    assert len(contacts) == 1
    assert contacts[0].name == "test contact"


@pytest.mark.asyncio
async def test_get_contact_by_id(contact_repository, mock_session, user):
    expected_contact = Contact(id=1, name="test contact", user=user)

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = expected_contact
    mock_session.execute = AsyncMock(return_value=mock_result)

    contact = await contact_repository.get_contact_by_id(contact_id=1, user=user)

    assert contact is not None
    assert contact.id == 1
    assert contact.name == "test contact"


@pytest.mark.asyncio
async def test_create_contact(contact_repository, mock_session, user):
    contact_data = ContactBase(
        name="new contact",
        surname="test",
        email="test@example.com",
        phone="1234567890",
        birthday="2000-01-01",
    )

    result = await contact_repository.create_contact(body=contact_data, user=user)

    assert isinstance(result, Contact)
    assert result.name == "new contact"
    mock_session.add.assert_called_once()
    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once_with(result)


@pytest.mark.asyncio
async def test_update_contact(contact_repository, mock_session, user):
    contact_data = ContactBase(
        name="updated contact",
        surname="test",
        email="test@example.com",
        phone="1234567890",
        birthday="2000-01-01",
    )
    existing_contact = Contact(id=1, name="old contact", user=user)
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = existing_contact
    mock_session.execute = AsyncMock(return_value=mock_result)

    result = await contact_repository.update_contact(
        contact_id=1, body=contact_data, user=user
    )

    assert result is not None
    assert result.name == "updated contact"
    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once_with(existing_contact)


@pytest.mark.asyncio
async def test_remove_contact(contact_repository, mock_session, user):
    existing_contact = Contact(id=1, name="contact to delete", user=user)
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = existing_contact
    mock_session.execute = AsyncMock(return_value=mock_result)

    result = await contact_repository.remove_contact(contact_id=1, user=user)

    assert result is not None
    assert result.name == "contact to delete"
    mock_session.delete.assert_awaited_once_with(existing_contact)
    mock_session.commit.assert_awaited_once()
