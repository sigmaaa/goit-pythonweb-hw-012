from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Contact, User
from src.schemas import ContactBase


class ContactRepository:
    """
    Repository class for managing `Contact` entities in the database.

    Provides asynchronous methods for creating, retrieving, updating,
    and deleting contacts associated with a specific user.

    :param session: Asynchronous database session.
    :type session: AsyncSession
    """

    def __init__(self, session: AsyncSession):
        self.db = session

    async def create_contact(self, body: ContactBase, user: User) -> Contact | None:
        """
        Create a new contact for a given user.

        :param body: Contact data to create.
        :type body: ContactBase
        :param user: The user to whom the contact belongs.
        :type user: User
        :return: The created contact or None if creation failed.
        :rtype: Contact | None
        """
        contact = Contact(**body.model_dump(exclude_unset=True), user=user)
        self.db.add(contact)
        await self.db.commit()
        await self.db.refresh(contact)
        return contact

    async def get_contact_by_id(self, contact_id: int, user: User) -> Contact | None:
        """
        Retrieve a contact by its ID for a given user.

        :param contact_id: ID of the contact.
        :type contact_id: int
        :param user: The user who owns the contact.
        :type user: User
        :return: The contact if found, otherwise None.
        :rtype: Contact | None
        """
        query = select(Contact).filter_by(id=contact_id, user=user)
        contact = await self.db.execute(query)
        return contact.scalar_one_or_none()

    async def get_contacts(self, skip: int, limit: int, user: User) -> List[Contact]:
        """
        Retrieve a list of contacts for a given user with pagination.

        :param skip: Number of records to skip.
        :type skip: int
        :param limit: Maximum number of records to return.
        :type limit: int
        :param user: The user whose contacts are retrieved.
        :type user: User
        :return: List of contacts.
        :rtype: List[Contact]
        """
        query = select(Contact).filter_by(user=user).offset(skip).limit(limit)
        contacts = await self.db.execute(query)
        return contacts.scalars().all()

    async def update_contact(
        self, contact_id: int, body: ContactBase, user: User
    ) -> Contact | None:
        """
        Update an existing contact for a given user.

        :param contact_id: ID of the contact to update.
        :type contact_id: int
        :param body: Updated contact data.
        :type body: ContactBase
        :param user: The user who owns the contact.
        :type user: User
        :return: The updated contact or None if not found.
        :rtype: Contact | None
        """
        contact = await self.get_contact_by_id(contact_id, user)
        if contact:
            contact.name = body.name
            contact.surname = body.surname
            contact.birthday = body.birthday
            contact.email = body.email
            contact.phone = body.phone
            contact.extra_info = body.extra_info
            await self.db.commit()
            await self.db.refresh(contact)
        return contact

    async def remove_contact(self, contact_id: int, user: User) -> Contact | None:
        """
        Remove a contact by its ID for a given user.

        :param contact_id: ID of the contact to remove.
        :type contact_id: int
        :param user: The user who owns the contact.
        :type user: User
        :return: The removed contact or None if not found.
        :rtype: Contact | None
        """
        contact = await self.get_contact_by_id(contact_id, user)
        if contact:
            await self.db.delete(contact)
            await self.db.commit()
        return contact

    async def get_contacts_by_ids(
        self, contact_ids: List[int], user: User
    ) -> list[Contact]:
        """
        Retrieve multiple contacts by their IDs for a given user.

        :param contact_ids: List of contact IDs to retrieve.
        :type contact_ids: List[int]
        :param user: The user who owns the contacts.
        :type user: User
        :return: List of contacts found.
        :rtype: list[Contact]
        """
        query = select(Contact).where(
            Contact.id.in_(contact_ids), Contact.user_id == user.id
        )
        result = await self.db.execute(query)
        return result.scalars().all()
