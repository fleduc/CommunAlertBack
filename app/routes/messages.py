"""
Module: messages.py
Description: This module provides API endpoints for managing messages within alerts.
Endpoints include creating messages, listing messages, deleting messages, marking messages as read,
adding reactions, and removing reactions.
"""

import logging
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session, joinedload

from app import models, schemas, database
from app.dependencies import get_current_user, get_db

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/", response_model=schemas.MessageResponse)
def create_message(
        request: Request,
        alert_id: int,
        message: schemas.MessageCreate,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_user)
):
    """
    Create a new message for a given alert.

    Args:
        request (Request): The incoming HTTP request.
        alert_id (int): The ID of the alert.
        message (schemas.MessageCreate): The message data.
        db (Session): Database session dependency.
        current_user (models.User): The currently authenticated user.

    Returns:
        schemas.MessageResponse: The created message object.

    Raises:
        HTTPException: If the alert does not exist.
    """
    logger.info("POST request on /api/alerts/%s/messages/ with body: %s", alert_id, message.dict())
    logger.info("Received cookies: %s", request.cookies)

    # Verify that the alert exists.
    alert = db.query(models.Alert).filter(models.Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    new_message = models.Message(
        alert_id=alert_id,
        sender_id=current_user.id,  # Use the currently authenticated user's ID.
        content=message.content,
        media_url=message.media_url,
        created_at=datetime.utcnow()
    )
    db.add(new_message)
    db.commit()
    db.refresh(new_message)
    return new_message


@router.get("/", response_model=list[schemas.MessageResponse])
def list_messages(
        alert_id: int,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_user)
):
    """
    List all messages for a specific alert.

    Args:
        alert_id (int): The ID of the alert.
        db (Session): Database session dependency.
        current_user (models.User): The currently authenticated user.

    Returns:
        List[schemas.MessageResponse]: A list of messages.

    Raises:
        HTTPException: If the alert does not exist.
    """
    # Verify that the alert exists.
    alert = db.query(models.Alert).filter(models.Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    messages = (
        db.query(models.Message)
        .options(joinedload(models.Message.sender))
        .filter(models.Message.alert_id == alert_id)
        .all()
    )
    logger.info("Retrieved messages: %s", messages)
    return messages


@router.delete("/{message_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_message(
        alert_id: int,
        message_id: int,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_user)
):
    """
    Delete a message. Only the sender is allowed to delete their message.

    Args:
        alert_id (int): The ID of the alert associated with the message.
        message_id (int): The ID of the message to delete.
        db (Session): Database session dependency.
        current_user (models.User): The currently authenticated user.

    Raises:
        HTTPException: If the message is not found or if the user is not authorized to delete it.
    """
    message = db.query(models.Message).filter(
        models.Message.id == message_id,
        models.Message.alert_id == alert_id
    ).first()
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")

    if message.sender_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this message")

    db.delete(message)
    db.commit()
    return


@router.post("/{message_id}/read", response_model=schemas.MessageReadResponse)
def mark_message_read(
        alert_id: int,
        message_id: int,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_user)
):
    """
    Mark a message as read by creating a read receipt.

    Args:
        alert_id (int): The ID of the alert associated with the message.
        message_id (int): The ID of the message to mark as read.
        db (Session): Database session dependency.
        current_user (models.User): The currently authenticated user.

    Returns:
        schemas.MessageReadResponse: The read receipt object.

    Raises:
        HTTPException: If the message is not found.
    """
    message = db.query(models.Message).filter(
        models.Message.id == message_id,
        models.Message.alert_id == alert_id
    ).first()
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")

    # Check if a read receipt already exists for this user and message.
    read_receipt = db.query(models.MessageRead).filter(
        models.MessageRead.message_id == message_id,
        models.MessageRead.user_id == current_user.id
    ).first()

    if read_receipt:
        return read_receipt

    new_receipt = models.MessageRead(
        message_id=message_id,
        user_id=current_user.id
    )
    db.add(new_receipt)
    db.commit()
    db.refresh(new_receipt)
    return new_receipt


@router.post("/{message_id}/reaction", response_model=schemas.MessageReactionResponse)
def add_reaction(
        alert_id: int,
        message_id: int,
        reaction: schemas.MessageReactionCreate,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_user)
):
    """
    Add a reaction (emoji) to a message.

    Args:
        alert_id (int): The ID of the alert associated with the message.
        message_id (int): The ID of the message.
        reaction (schemas.MessageReactionCreate): The reaction data.
        db (Session): Database session dependency.
        current_user (models.User): The currently authenticated user.

    Returns:
        schemas.MessageReactionResponse: The added reaction object.

    Raises:
        HTTPException: If the message is not found or if the same reaction already exists.
    """
    message = db.query(models.Message).filter(
        models.Message.id == message_id,
        models.Message.alert_id == alert_id
    ).first()
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")

    # Check if the user has already reacted with the same emoji.
    existing_reaction = db.query(models.MessageReaction).filter(
        models.MessageReaction.message_id == message_id,
        models.MessageReaction.user_id == current_user.id,
        models.MessageReaction.emoji == reaction.emoji
    ).first()
    if existing_reaction:
        raise HTTPException(status_code=400, detail="Reaction already added")

    new_reaction = models.MessageReaction(
        message_id=message_id,
        user_id=current_user.id,
        emoji=reaction.emoji
    )
    db.add(new_reaction)
    db.commit()
    db.refresh(new_reaction)
    return new_reaction


@router.delete("/{message_id}/reaction", status_code=status.HTTP_204_NO_CONTENT)
def remove_reaction(
        alert_id: int,
        message_id: int,
        emoji: str,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_user)
):
    """
    Remove a reaction (emoji) from a message.

    Args:
        alert_id (int): The ID of the alert associated with the message.
        message_id (int): The ID of the message.
        emoji (str): The emoji reaction to remove.
        db (Session): Database session dependency.
        current_user (models.User): The currently authenticated user.

    Raises:
        HTTPException: If the reaction is not found.
    """
    reaction = db.query(models.MessageReaction).filter(
        models.MessageReaction.message_id == message_id,
        models.MessageReaction.user_id == current_user.id,
        models.MessageReaction.emoji == emoji
    ).first()
    if not reaction:
        raise HTTPException(status_code=404, detail="Reaction not found")
    db.delete(reaction)
    db.commit()
    return
