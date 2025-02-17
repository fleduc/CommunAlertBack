"""
Module: alerts.py
Description: This module defines the API endpoints for managing alerts.
It uses FastAPI for routing and SQLAlchemy for database interactions.
All log messages and error details have been translated to English.
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List

from app import models, schemas, database

logger = logging.getLogger(__name__)

router = APIRouter()

# Log that the alert routes have been loaded.
print("✅ Alerts routes loaded")


def get_db():
    """
    Dependency that provides a database session.

    Yields:
        Session: SQLAlchemy session instance.
    """
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/", response_model=List[schemas.AlertResponse])
def list_alerts(request: Request, db: Session = Depends(get_db)):
    """
    Retrieve a list of all alerts.

    Args:
        request (Request): The incoming HTTP request.
        db (Session, optional): Database session dependency.

    Returns:
        List[schemas.AlertResponse]: A list of alerts.
    """
    logger.info("GET request on /api/alerts/")
    logger.info("Received cookies: %s", request.cookies)
    logger.info("Query parameters: %s", request.query_params)
    return db.query(models.Alert).all()


@router.get("/{alert_id}", response_model=schemas.AlertResponse)
def get_alert(request: Request, alert_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a specific alert by its ID.

    Args:
        request (Request): The incoming HTTP request.
        alert_id (int): The ID of the alert to retrieve.
        db (Session, optional): Database session dependency.

    Returns:
        schemas.AlertResponse: The alert object.

    Raises:
        HTTPException: If the alert is not found.
    """
    logger.info("GET request on /api/alerts/%s/", alert_id)
    logger.info("Received cookies: %s", request.cookies)
    logger.info("Query parameters: %s", request.query_params)
    alert = db.query(models.Alert).filter(models.Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert not found")
    return alert


@router.post("/", response_model=schemas.AlertResponse)
def create_alert(request: Request, alert: schemas.AlertCreate, db: Session = Depends(get_db)):
    """
    Create a new alert.

    Args:
        request (Request): The incoming HTTP request.
        alert (schemas.AlertCreate): The alert data to create.
        db (Session, optional): Database session dependency.

    Returns:
        schemas.AlertResponse: The newly created alert.
    """
    logger.info("POST request on /api/alerts/ with body: %s", alert.dict())
    logger.info("Received cookies: %s", request.cookies)
    new_alert = models.Alert(
        alert_title=alert.alert_title,
        description=alert.description,
        alert_type=alert.alert_type,
        closing_date=alert.closing_date,
        postal_code=alert.postal_code,
        user_id=alert.user_id
    )
    db.add(new_alert)
    db.commit()
    db.refresh(new_alert)
    return new_alert


@router.put("/{alert_id}", response_model=schemas.AlertResponse)
def update_alert(alert_id: int, alert_update: schemas.AlertUpdate, db: Session = Depends(get_db)):
    """
    Update an existing alert.

    Only the fields provided in the request will be updated.

    Args:
        alert_id (int): The ID of the alert to update.
        alert_update (schemas.AlertUpdate): The updated alert data.
        db (Session, optional): Database session dependency.

    Returns:
        schemas.AlertResponse: The updated alert.

    Raises:
        HTTPException: If the alert is not found.
    """
    alert = db.query(models.Alert).filter(models.Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert not found")

    # Update fields only if provided in the request.
    if alert_update.alert_title is not None:
        alert.alert_title = alert_update.alert_title
    if alert_update.description is not None:
        alert.description = alert_update.description
    if alert_update.alert_type is not None:
        alert.alert_type = alert_update.alert_type
    if alert_update.closing_date is not None:
        alert.closing_date = alert_update.closing_date
    if alert_update.postal_code is not None:
        alert.postal_code = alert_update.postal_code
    if alert_update.user_id is not None:
        alert.user_id = alert_update.user_id

    db.commit()
    db.refresh(alert)
    return alert


@router.delete("/{alert_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_alert(alert_id: int, db: Session = Depends(get_db)):
    """
    Delete an alert by its ID.

    Args:
        alert_id (int): The ID of the alert to delete.
        db (Session, optional): Database session dependency.

    Raises:
        HTTPException: If the alert is not found.
    """
    alert = db.query(models.Alert).filter(models.Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert not found")
    db.delete(alert)
    db.commit()
    return
