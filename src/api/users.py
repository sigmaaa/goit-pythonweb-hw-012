"""
Users API.

This module defines the `/users` endpoints for managing user data,
including retrieving the current user's profile and updating the avatar.

Endpoints:
    GET /users/me: Retrieve the currently authenticated user's information.
    PATCH /users/avatar: Update the authenticated user's avatar image.
"""

from fastapi import APIRouter, Request, Depends, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from src.schemas import User
from src.services.auth import get_current_user
from slowapi import Limiter
from src.services.upload_file import UploadFileService
from src.conf.config import config
from src.database.db import get_db
from src.services.users import UserService

router = APIRouter(prefix="/users", tags=["users"])
limiter = Limiter(key_func=lambda request: request.client.host)


@router.get(
    "/me", response_model=User, description="No more than 10 requests per minute"
)
@limiter.limit("10/minute")
async def me(request: Request, user: User = Depends(get_current_user)):
    """
    Retrieve the currently authenticated user's profile.

    :param request: FastAPI request object.
    :param user: Currently authenticated user, injected via dependency.
    :return: User object with the authenticated user's information.
    """
    return user


@router.patch("/avatar", response_model=User)
async def update_avatar_user(
    file: UploadFile = File(),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update the authenticated user's avatar.

    :param file: Uploaded avatar image file.
    :param user: Currently authenticated user, injected via dependency.
    :param db: Asynchronous database session.
    :return: Updated User object with the new avatar URL.
    """
    avatar_url = UploadFileService(
        config.CLD_NAME, config.CLD_API_KEY, config.CLD_API_SECRET
    ).upload_file(file, user.username)

    user_service = UserService(db)
    user = await user_service.update_avatar_url(user.email, avatar_url)

    return user
