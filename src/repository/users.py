"""
User repository module.

This module provides the `UserRepository` class for performing CRUD operations
on `User` objects in the database using SQLAlchemy's asynchronous session.

Classes:
    UserRepository: Handles database interactions for user-related operations.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import User
from src.schemas import UserCreate


class UserRepository:
    """
    Repository class for managing `User` entities in the database.

    Args:
        session (AsyncSession): The asynchronous SQLAlchemy session.
    """

    def __init__(self, session: AsyncSession):
        """
        Initialize the UserRepository with a database session.

        :param session: An instance of AsyncSession for database access.
        """
        self.db = session

    async def get_user_by_id(self, user_id: int) -> User | None:
        """
        Retrieve a user by their ID.

        :param user_id: The ID of the user to retrieve.
        :return: The `User` object if found, otherwise `None`.
        """
        stmt = select(User).filter_by(id=user_id)
        user = await self.db.execute(stmt)
        return user.scalar_one_or_none()

    async def get_user_by_username(self, username: str) -> User | None:
        """
        Retrieve a user by their username.

        :param username: The username of the user to retrieve.
        :return: The `User` object if found, otherwise `None`.
        """
        stmt = select(User).filter_by(username=username)
        user = await self.db.execute(stmt)
        return user.scalar_one_or_none()

    async def get_user_by_email(self, email: str) -> User | None:
        """
        Retrieve a user by their email address.

        :param email: The email of the user to retrieve.
        :return: The `User` object if found, otherwise `None`.
        """
        stmt = select(User).filter_by(email=email)
        user = await self.db.execute(stmt)
        return user.scalar_one_or_none()

    async def create_user(self, body: UserCreate, avatar: str = None) -> User:
        """
        Create a new user in the database.

        :param body: A `UserCreate` schema instance containing user data.
        :param avatar: Optional URL of the user's avatar image.
        :return: The created `User` object.
        """
        user = User(
            **body.model_dump(exclude_unset=True, exclude={"password"}),
            hashed_password=body.password,
            avatar=avatar,
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def confirmed_email(self, email: str) -> None:
        """
        Mark a user's email as confirmed.

        :param email: The email of the user to confirm.
        """
        user = await self.get_user_by_email(email)
        user.confirmed = True
        await self.db.commit()

    async def update_avatar_url(self, email: str, url: str) -> User:
        """
        Update the avatar URL for a specific user.

        :param email: The email of the user to update.
        :param url: The new avatar URL.
        :return: The updated `User` object.
        """
        user = await self.get_user_by_email(email)
        user.avatar = url
        await self.db.commit()
        await self.db.refresh(user)
        return user
