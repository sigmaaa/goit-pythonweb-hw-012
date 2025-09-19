"""
Contacts API.

This module defines the `/contacts` endpoints for managing user contacts,
including listing, retrieving, creating, updating, and deleting contacts.

Endpoints:
    GET /contacts: Retrieve a list of contacts.
    GET /contacts/{contact_id}: Retrieve a single contact by ID.
    POST /contacts: Create a new contact.
    PUT /contacts/{contact_id}: Update an existing contact.
    DELETE /contacts/{contact_id}: Remove a contact.
"""

from typing import List

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.schemas import ContactBase, ContactResponse
from src.database.models import User
from src.services.auth import get_current_user
from src.services.contacts import ContactService

router = APIRouter(prefix="/contacts", tags=["contacts"])


@router.get("/", response_model=List[ContactResponse])
async def get_contacts(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Retrieve a list of contacts for the authenticated user.

    :param skip: Number of records to skip (pagination).
    :param limit: Maximum number of records to return.
    :param db: Asynchronous database session.
    :param user: Currently authenticated user.
    :return: List of ContactResponse objects.
    """
    contact_service = ContactService(db)
    contacts = await contact_service.get_contacts(skip, limit, user=user)
    return contacts


@router.get("/{contact_id}", response_model=ContactResponse)
async def read_contact(
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Retrieve a single contact by its ID.

    :param contact_id: ID of the contact to retrieve.
    :param db: Asynchronous database session.
    :param user: Currently authenticated user.
    :return: ContactResponse object.
    :raises HTTPException: 404 if contact not found.
    """
    contact_service = ContactService(db)
    contact = await contact_service.get_contact(contact_id, user=user)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return contact


@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def create_contact(
    body: ContactBase,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Create a new contact for the authenticated user.

    :param body: ContactBase schema containing contact data.
    :param db: Asynchronous database session.
    :param user: Currently authenticated user.
    :return: The created ContactResponse object.
    """
    contact_service = ContactService(db)
    return await contact_service.create_contact(body, user=user)


@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(
    body: ContactBase,
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Update an existing contact.

    :param body: ContactBase schema with updated contact data.
    :param contact_id: ID of the contact to update.
    :param db: Asynchronous database session.
    :param user: Currently authenticated user.
    :return: The updated ContactResponse object.
    :raises HTTPException: 404 if contact not found.
    """
    contact_service = ContactService(db)
    contact = await contact_service.update_contact(contact_id, body, user=user)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return contact


@router.delete("/{contact_id}", response_model=ContactResponse)
async def remove_contact(
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Delete a contact by its ID.

    :param contact_id: ID of the contact to delete.
    :param db: Asynchronous database session.
    :param user: Currently authenticated user.
    :return: The deleted ContactResponse object.
    :raises HTTPException: 404 if contact not found.
    """
    contact_service = ContactService(db)
    contact = await contact_service.remove_contact(contact_id, user=user)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return contact
