"""
Contact management service.

This module provides the `ContactService` class for managing user contacts,
including creation, retrieval, updating, and deletion. It also includes
a helper for handling database integrity errors.

Classes:
    ContactService: Provides business logic for user contacts.

Functions:
    _handle_integrity_error: Handles SQLAlchemy IntegrityError exceptions.
"""

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from src.repository.contacts import ContactRepository
from src.database.models import User
from src.schemas import ContactBase


def _handle_integrity_error(e: IntegrityError):
    """
    Handle database integrity errors for contacts.

    Raises an HTTPException with appropriate status code and message
    depending on the type of integrity violation.

    :param e: The IntegrityError exception instance.
    :raises HTTPException: HTTP 409 if duplicate contact, HTTP 400 otherwise.
    """
    if "unique_contact_user" in str(e.orig):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Контакт з таким ім'ям вже існує.",
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Помилка цілісності даних.",
        )


class ContactService:
    """
    Service class for managing user contacts.

    Provides methods to create, retrieve, update, and delete contacts,
    handling integrity errors and delegating database operations to
    `ContactRepository`.

    Args:
        db (AsyncSession): Asynchronous SQLAlchemy session for database access.
    """

    def __init__(self, db: AsyncSession):
        """
        Initialize the ContactService with a database session.

        :param db: Asynchronous SQLAlchemy session.
        """
        self.repository = ContactRepository(db)

    async def create_contact(self, body: ContactBase, user: User):
        """
        Create a new contact for a user.

        Handles potential integrity errors (e.g., duplicate contact names).

        :param body: ContactBase schema instance with contact data.
        :param user: User object to whom the contact belongs.
        :return: The created contact object.
        :raises HTTPException: If a database integrity error occurs.
        """
        try:
            return await self.repository.create_contact(body, user)
        except IntegrityError as e:
            await self.repository.db.rollback()
            _handle_integrity_error(e)

    async def get_contact(self, contact_id: int, user: User):
        """
        Retrieve a specific contact by ID for a given user.

        :param contact_id: ID of the contact to retrieve.
        :param user: User object to whom the contact belongs.
        :return: The contact object if found, otherwise None.
        """
        return await self.repository.get_contact_by_id(contact_id, user)

    async def get_contacts(self, skip: int, limit: int, user: User):
        """
        Retrieve a paginated list of contacts for a given user.

        :param skip: Number of contacts to skip (offset).
        :param limit: Maximum number of contacts to return.
        :param user: User object to whom the contacts belong.
        :return: List of contact objects.
        """
        return await self.repository.get_contacts(skip, limit, user)

    async def update_contact(self, contact_id: int, body: ContactBase, user: User):
        """
        Update an existing contact's information.

        :param contact_id: ID of the contact to update.
        :param body: ContactBase schema instance with updated data.
        :param user: User object to whom the contact belongs.
        :return: The updated contact object.
        """
        return await self.repository.update_contact(contact_id, body, user)

    async def remove_contact(self, contact_id: int, user: User):
        """
        Remove a contact for a given user.

        :param contact_id: ID of the contact to remove.
        :param user: User object to whom the contact belongs.
        :return: The removed contact object.
        """
        return await self.repository.remove_contact(contact_id, user)
