"""
User service module.

This module provides the `UserService` class for performing user-related
business logic, including user creation, retrieval, and email confirmation.

Classes:
    UserService: Provides high-level operations for user management.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from libgravatar import Gravatar
from fastapi import HTTPException
from src.repository.users import UserRepository
from src.schemas import UserCreate, UserRole
from src.utils.hash_utility import Hash


class UserService:
    """
    Service class for managing users.

    Delegates database operations to `UserRepository` and provides
    additional business logic such as avatar generation via Gravatar.

    Args:
        db (AsyncSession): Asynchronous SQLAlchemy session for database access.
    """

    def __init__(self, db: AsyncSession):
        """
        Initialize the UserService with a database session.

        :param db: Asynchronous SQLAlchemy session.
        """
        self.repository = UserRepository(db)

    async def create_user(self, body: UserCreate):
        """
        Create a new user with an optional Gravatar avatar.

        Attempts to generate an avatar URL from the user's email using Gravatar.

        :param body: UserCreate schema instance containing user data.
        :return: The created `User` object.
        """
        avatar = None
        try:
            g = Gravatar(body.email)
            avatar = g.get_image()
        except Exception as e:
            print(e)

        return await self.repository.create_user(body, avatar)

    async def get_user_by_id(self, user_id: int):
        """
        Retrieve a user by their ID.

        :param user_id: The ID of the user to retrieve.
        :return: The `User` object if found, otherwise `None`.
        """
        return await self.repository.get_user_by_id(user_id)

    async def get_user_by_username(self, username: str):
        """
        Retrieve a user by their username.

        :param username: The username of the user to retrieve.
        :return: The `User` object if found, otherwise `None`.
        """
        return await self.repository.get_user_by_username(username)

    async def get_user_by_email(self, email: str):
        """
        Retrieve a user by their email address.

        :param email: The email of the user to retrieve.
        :return: The `User` object if found, otherwise `None`.
        """
        return await self.repository.get_user_by_email(email)

    async def confirmed_email(self, email: str):
        """
        Mark a user's email as confirmed.

        :param email: The email of the user to confirm.
        :return: None
        """
        return await self.repository.confirmed_email(email)

    async def update_avatar_url(self, email: str, url: str):
        """
        Update the avatar URL of a user.

        This method delegates the update operation to the repository layer.

        :param email: The email of the user whose avatar will be updated.
        :param url: The new avatar URL to set for the user.
        :return: The updated `User` object with the new avatar URL.
        """
        user = await self.repository.get_user_by_email(email)
        if user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=403, detail="Only admins can change their avatar"
            )
        user.avatar = url
        return await self.repository.update_avatar_url(email, url)

    async def reset_password(self, email: str, new_password: str):
        """
        Reset a user's password.

        :param email: The email of the user who requested the reset.
        :param new_password: New plain password to hash and save.
        :return: Updated User object or None if not found.
        """
        user = await self.repository.get_user_by_email(email)
        if not user:
            return None

        hashed_password = Hash().get_password_hash(new_password)
        return await self.repository.update_password(user, hashed_password)
