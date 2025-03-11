"""
Module: alerts.py
Description: This module defines the API endpoints for managing alerts.
It uses FastAPI for routing and SQLAlchemy for database interactions.
All log messages and error details have been translated to English.
"""

import logging
import os
import uuid
import json
from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Request, File, UploadFile, Form, Query, Body
from sqlalchemy.orm import Session

from app import models, schemas, database
from app.dependencies import get_current_user, get_db

logger = logging.getLogger(__name__)

router = APIRouter()

# Log that the alert routes have been loaded.
print("✅ Alerts routes loaded")


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
def create_alert(
    request: Request,
    alert: str = Form(...),  # Expect alert data as a JSON string in a form field.
    file: Optional[UploadFile] = File(None),  # Optional file upload.
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
    local_kw: str = Query(default=None)  # if needed for compatibility
):
    """
    Create a new alert.

    Args:
        request (Request): The incoming HTTP request.
        alert (str): A JSON string containing the alert data.
        file (UploadFile, optional): An optional image file for the alert.
        db (Session): Database session dependency.
        current_user (models.User): The currently authenticated user.

    Returns:
        schemas.AlertResponse: The newly created alert.
    """
    logger.info("POST request on /api/alerts/ with alert data: %s", alert)
    logger.info("Received cookies: %s", request.cookies)

    # Parse the JSON string into an AlertCreate object.
    try:
        alert_data = schemas.AlertCreate.parse_raw(alert)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid alert JSON format") from e

    # If file is an empty string (which may happen), set it to None.
    if file is not None and isinstance(file, str) and file.strip() == "":
        file = None

    picture_path = None
    if file is not None:
        # Extract file extension.
        _, file_extension = os.path.splitext(file.filename)
        # Generate a unique filename using UUID.
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        # Define the directory to store images (ensure it exists).
        static_folder = "static/alert_images"
        os.makedirs(static_folder, exist_ok=True)
        file_path = os.path.join(static_folder, unique_filename)
        with open(file_path, "wb") as f:
            f.write(file.file.read())
        # Set the picture field to the relative URL (assuming static is mounted at /static).
        picture_path = f"/static/alert_images/{unique_filename}"

    logger.info("picture_path: %s", picture_path)

    new_alert = models.Alert(
        alert_title=alert_data.alert_title,
        description=alert_data.description,
        alert_type=alert_data.alert_type,
        picture=picture_path,  # Set to the image URL if available.
        starting_date=alert_data.starting_date,
        closing_date=alert_data.closing_date,
        postal_code=alert_data.postal_code,
        longitude=alert_data.longitude,
        latitude=alert_data.latitude,
        radius=alert_data.radius,
        status=alert_data.status,
        planned_duration=alert_data.planned_duration,
        severity_level=alert_data.severity_level,
        public_status=alert_data.public_status,
        created_at=datetime.utcnow(),
        user_id=current_user.id
    )
    db.add(new_alert)
    db.commit()
    db.refresh(new_alert)
    return new_alert


@router.put("/{alert_id}", response_model=schemas.AlertResponse)
def update_alert(
    alert_id: int,
    alert_update: schemas.AlertUpdate = Body(...),
    file: Optional[UploadFile] = File(None),  # Optional image file for updating the alert picture.
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Update an existing alert.

    Only the fields provided in the request will be updated.

    Args:
        alert_id (int): The ID of the alert to update.
        alert_update (schemas.AlertUpdate): The updated alert data.
        file (UploadFile, optional): An optional image file for the alert update.
        db (Session, optional): Database session dependency.
        current_user (models.User): The currently authenticated user.

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

    # Update new fields if provided.
    if alert_update.picture is not None:
        alert.picture = alert_update.picture
    if alert_update.starting_date is not None:
        alert.starting_date = alert_update.starting_date
    if alert_update.longitude is not None:
        alert.longitude = alert_update.longitude
    if alert_update.latitude is not None:
        alert.latitude = alert_update.latitude
    if alert_update.radius is not None:
        alert.radius = alert_update.radius
    if alert_update.status is not None:
        alert.status = alert_update.status
    if alert_update.planned_duration is not None:
        alert.planned_duration = alert_update.planned_duration
    if alert_update.severity_level is not None:
        alert.severity_level = alert_update.severity_level
    if alert_update.public_status is not None:
        alert.public_status = alert_update.public_status

    # If a new image file is provided, process and update the picture field.
    if file is not None:
        _, file_extension = os.path.splitext(file.filename)
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        static_folder = "static/alert_images"
        os.makedirs(static_folder, exist_ok=True)
        file_path = os.path.join(static_folder, unique_filename)
        with open(file_path, "wb") as f:
            f.write(file.file.read())
        alert.picture = f"/static/alert_images/{unique_filename}"

    # Ensure the alert remains associated with the current user.
    alert.user_id = current_user.id

    db.commit()
    db.refresh(alert)
    return alert


@router.delete("/{alert_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_alert(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Delete an alert by its ID.

    Args:
        alert_id (int): The ID of the alert to delete.
        db (Session, optional): Database session dependency.
        current_user (models.User): The currently authenticated user.

    Raises:
        HTTPException: If the alert is not found.
    """
    alert = db.query(models.Alert).filter(models.Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert not found")

    # Delete only if the current user is the creator of the alert.
    if alert.user_id == current_user.id:
        db.delete(alert)
        db.commit()

    return
