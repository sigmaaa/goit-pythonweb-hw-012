from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Contact, User
from src.schemas import ContactBase


class ContactRepository:
    def __init__(self, session: AsyncSession):
        self.db = session

    async def create_contact(self, body: ContactBase, user: User) -> Contact | None:
        contact = Contact(**body.model_dump(exclude_unset=True), user=user)
        self.db.add(contact)
        await self.db.commit()
        await self.db.refresh(contact)
        return contact

    async def get_contact_by_id(self, contact_id: int, user: User) -> Contact | None:
        query = select(Contact).filter_by(id=contact_id, user=user)
        contact = await self.db.execute(query)
        return contact.scalar_one_or_none()

    async def get_contacts(self, skip: int, limit: int, user: User) -> List[Contact]:
        query = select(Contact).filter_by(user=user).offset(skip).limit(limit)
        contacts = await self.db.execute(query)
        return contacts.scalars().all()

    async def update_contact(
        self, contact_id: int, body: ContactBase, user: User
    ) -> Contact | None:
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
        contact = await self.get_contact_by_id(contact_id, user)
        if contact:
            await self.db.delete(contact)
            await self.db.commit()
        return contact

    async def get_contacts_by_ids(
        self, contact_ids: List[int], user: User
    ) -> list[Contact]:
        query = select(Contact).where(
            Contact.id.in_(contact_ids), Contact.user_id == user.id
        )
        result = await self.db.execute(query)
        return result.scalars().all()
