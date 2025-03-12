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
from sqlalchemy.orm import Session, joinedload

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
    return db.query(models.Alert).options(joinedload(models.Alert.user)).all()


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
    alert: str = Form(...),  # Expect alert data as a JSON string (of type AlertInput)
    file: Optional[UploadFile] = File(None),  # Optional file upload.
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
    local_kw: str = Query(default=None)
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

    # Parse the JSON string into an AlertInput object.
    try:
        alert_data = schemas.AlertCreate.model_validate_json(alert)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Invalid alert JSON format") from e

    picture_path = None
    if file is not None:
        # Process file upload.
        _, file_extension = os.path.splitext(file.filename)
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        static_folder = "static/alert_images"
        os.makedirs(static_folder, exist_ok=True)
        file_path = os.path.join(static_folder, unique_filename)
        with open(file_path, "wb") as f:
            f.write(file.file.read())
        picture_path = f"/static/alert_images/{unique_filename}"
        logger.info("picture_path: %s", picture_path)

    new_alert = models.Alert(
        alert_title=alert_data.alert_title,
        description=alert_data.description,
        alert_type=alert_data.alert_type,
        picture=picture_path,
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
        user_id=current_user.id  # Set from the backend.
    )
    db.add(new_alert)
    db.commit()
    db.refresh(new_alert)
    return new_alert


@router.put("/{alert_id}", response_model=schemas.AlertResponse)
def update_alert(
    alert_id: int,
    alert: str = Form(...),  # Expect update data as a JSON string (of type AlertUpdate)
    file: Optional[UploadFile] = File(None),  # Optional image file for updating the alert picture.
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Update an existing alert.

    Only the fields provided in the request will be updated.

    Args:
        alert_id (int): The ID of the alert to update.
        alert (str): A JSON string containing the updated alert data.
        file (UploadFile, optional): An optional image file for the alert update.
        db (Session): Database session dependency.
        current_user (models.User): The currently authenticated user.

    Returns:
        schemas.AlertResponse: The updated alert.

    Raises:
        HTTPException: If the alert is not found.
    """
    alert_instance = db.query(models.Alert).filter(models.Alert.id == alert_id).first()
    if not alert_instance:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert not found")

    # Parse the JSON string into an AlertUpdate object.
    try:
        alert_data = schemas.AlertUpdate.model_validate_json(alert)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Invalid alert update JSON format") from e

    # Update fields only if provided.
    if alert_data.alert_title is not None:
        alert_instance.alert_title = alert_data.alert_title
    if alert_data.description is not None:
        alert_instance.description = alert_data.description
    if alert_data.alert_type is not None:
        alert_instance.alert_type = alert_data.alert_type
    if alert_data.closing_date is not None:
        alert_instance.closing_date = alert_data.closing_date
    if alert_data.postal_code is not None:
        alert_instance.postal_code = alert_data.postal_code

    # Update new fields if provided.
    if alert_data.picture is not None:
        alert_instance.picture = alert_data.picture
    if alert_data.starting_date is not None:
        alert_instance.starting_date = alert_data.starting_date
    if alert_data.longitude is not None:
        alert_instance.longitude = alert_data.longitude
    if alert_data.latitude is not None:
        alert_instance.latitude = alert_data.latitude
    if alert_data.radius is not None:
        alert_instance.radius = alert_data.radius
    if alert_data.status is not None:
        alert_instance.status = alert_data.status
    if alert_data.planned_duration is not None:
        alert_instance.planned_duration = alert_data.planned_duration
    if alert_data.severity_level is not None:
        alert_instance.severity_level = alert_data.severity_level
    if alert_data.public_status is not None:
        alert_instance.public_status = alert_data.public_status

    # If a new image file is provided, process and update the picture field.
    if file is not None:
        _, file_extension = os.path.splitext(file.filename)
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        static_folder = "static/alert_images"
        os.makedirs(static_folder, exist_ok=True)
        file_path = os.path.join(static_folder, unique_filename)
        with open(file_path, "wb") as f:
            f.write(file.file.read())
        alert_instance.picture = f"/static/alert_images/{unique_filename}"

    # Ensure the alert remains associated with the current user.
    alert_instance.user_id = current_user.id

    db.commit()
    db.refresh(alert_instance)
    return alert_instance


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
