"""
Authentication and token service.

This module provides utilities for password hashing, JWT token creation and validation,
and retrieving the current user from a token.

Classes:
    Hash: Handles password hashing and verification.

Functions:
    create_access_token: Create a JWT access token.
    get_current_user: Retrieve the current user from a JWT token.
    create_email_token: Create a JWT token for email verification.
    get_email_from_token: Extract email from a JWT token.
"""

from datetime import datetime, timedelta, UTC
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from redis.asyncio import Redis


from src.database.db import get_db, get_redis
from src.conf.config import config
from src.services.users import UserService
from src.schemas import User
from src.database.models import UserRole

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


async def create_access_token(data: dict, expires_delta: Optional[int] = None) -> str:
    """
    Create a JWT access token.

    :param data: A dictionary containing the token payload.
    :param expires_delta: Optional expiration time in seconds.
    :return: Encoded JWT token as a string.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(UTC) + timedelta(seconds=expires_delta)
    else:
        expire = datetime.now(UTC) + timedelta(seconds=config.JWT_EXPIRATION_SECONDS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, config.JWT_SECRET, algorithm=config.JWT_ALGORITHM
    )
    return encoded_jwt


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
    redis: Redis = Depends(get_redis),
):
    """
    Retrieve the current user from the JWT access token with Redis caching.

    Steps:
        1. Decode JWT and extract the username.
        2. Try Redis cache (`user:username:{username}`).
        3. If not cached, query the database and store result in Redis.

    :param token: JWT token provided in the request header.
    :param db: Database session dependency.
    :param redis: Redis client dependency.
    :raises HTTPException: If the token is invalid or user does not exist.
    :return: The authenticated user object.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token, config.JWT_SECRET, algorithms=[config.JWT_ALGORITHM]
        )
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    cached_user = await redis.get(f"user:username:{username}")
    if cached_user:
        return User.model_validate_json(cached_user)

    user_service = UserService(db)
    user = await user_service.get_user_by_username(username)
    if user is None:
        raise credentials_exception

    await redis.set(
        f"user:username:{user.username}",
        User.model_validate(user).model_dump_json(),
        ex=3600,
    )
    return user


def get_current_admin_user(current_user: User = Depends(get_current_user)):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Insufficient access rights")
    return current_user


def create_email_token(data: dict) -> str:
    """
    Create a JWT token for email verification.

    :param data: A dictionary containing the token payload.
    :return: Encoded JWT token as a string valid for 7 days.
    """
    to_encode = data.copy()
    expire = datetime.now(UTC) + timedelta(days=7)
    to_encode.update({"iat": datetime.now(UTC), "exp": expire})
    token = jwt.encode(to_encode, config.JWT_SECRET, algorithm=config.JWT_ALGORITHM)
    return token


async def get_email_from_token(token: str) -> str:
    """
    Extract email from a JWT email verification token.

    :param token: The JWT token containing the email.
    :raises HTTPException: If the token is invalid or expired.
    :return: Email address extracted from the token.
    """
    try:
        payload = jwt.decode(
            token, config.JWT_SECRET, algorithms=[config.JWT_ALGORITHM]
        )
        email = payload["sub"]
        return email
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Неправильний токен для перевірки електронної пошти",
        )
