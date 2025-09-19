"""
Authentication API.

This module defines the `/auth` endpoints for user registration, login,
email confirmation, and requesting email verification links. It integrates
with the UserService and email service to handle user authentication
and email confirmation.

Endpoints:
    POST /auth/register: Register a new user.
    POST /auth/login: Authenticate a user and return a JWT token.
    GET /auth/confirmed_email/{token}: Confirm user's email from token.
    POST /auth/request_email: Request a new email confirmation link.
"""

from fastapi import (
    APIRouter,
    HTTPException,
    Depends,
    status,
    BackgroundTasks,
    Request,
)
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from src.schemas import UserCreate, Token, User
from src.services.auth import create_access_token, get_email_from_token, Hash
from src.services.users import UserService
from src.database.db import get_db
from src.services.email import send_email
from src.schemas import RequestEmail

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate,
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Register a new user and send a verification email.

    Checks for duplicate email or username, hashes the password, creates the user,
    and schedules a background task to send a confirmation email.

    :param user_data: UserCreate schema containing registration data.
    :param background_tasks: FastAPI BackgroundTasks for sending email asynchronously.
    :param request: FastAPI Request object to get the base URL.
    :param db: Database session dependency.
    :return: The created User object.
    :raises HTTPException: If the email or username already exists.
    """
    user_service = UserService(db)

    email_user = await user_service.get_user_by_email(user_data.email)
    if email_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Користувач з таким email вже існує",
        )

    username_user = await user_service.get_user_by_username(user_data.username)
    if username_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Користувач з таким іменем вже існує",
        )
    user_data.password = Hash().get_password_hash(user_data.password)
    new_user = await user_service.create_user(user_data)
    background_tasks.add_task(
        send_email, new_user.email, new_user.username, request.base_url
    )
    return new_user


@router.post("/login", response_model=Token)
async def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    """
    Authenticate a user and return a JWT access token.

    Verifies username, password, and email confirmation status. If successful,
    generates and returns an access token.

    :param form_data: OAuth2PasswordRequestForm containing username and password.
    :param db: Database session dependency.
    :return: Dictionary containing access_token and token_type.
    :raises HTTPException: If credentials are invalid or email is not confirmed.
    """
    user_service = UserService(db)
    user = await user_service.get_user_by_username(form_data.username)
    if not user or not Hash().verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неправильний логін або пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.confirmed:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Електронна адреса не підтверджена",
        )
    access_token = await create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/confirmed_email/{token}")
async def confirmed_email(token: str, db: Session = Depends(get_db)):
    """
    Confirm a user's email address using a verification token.

    Decodes the token, checks if the user exists and whether the email is already confirmed.
    Marks the email as confirmed if valid.

    :param token: Email verification JWT token.
    :param db: Database session dependency.
    :return: Dictionary with a confirmation message.
    :raises HTTPException: If the token is invalid or verification fails.
    """
    email = await get_email_from_token(token)
    user_service = UserService(db)
    user = await user_service.get_user_by_email(email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error"
        )
    if user.confirmed:
        return {"message": "Ваша електронна пошта вже підтверджена"}
    await user_service.confirmed_email(email)
    return {"message": "Електронну пошту підтверджено"}


@router.post("/request_email")
async def request_email(
    body: RequestEmail,
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Request a new email verification link.

    Checks if the user exists and whether the email is already confirmed.
    If not, schedules a background task to send a new verification email.

    :param body: RequestEmail schema containing the user's email.
    :param background_tasks: FastAPI BackgroundTasks for sending email asynchronously.
    :param request: FastAPI Request object to get the base URL.
    :param db: Database session dependency.
    :return: Dictionary with a status message.
    """
    user_service = UserService(db)
    user = await user_service.get_user_by_email(body.email)

    if user is None:
        return {"message: Користувача з такою поштою не знайдено"}

    if user.confirmed:
        return {"message": "Ваша електронна пошта вже підтверджена"}
    if user:
        background_tasks.add_task(
            send_email, user.email, user.username, request.base_url
        )
    return {"message": "Перевірте свою електронну пошту для підтвердження"}
