"""
Module: users.py
Description: This module provides API endpoints for managing users.
Endpoints include creating, retrieving, listing, and deleting users.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app import models, schemas, database
from passlib.context import CryptContext

# Log that the users routes have been loaded.
print("✅ Users routes loaded")

router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_db():
    """
    Dependency that provides a database session.

    Yields:
        Session: A SQLAlchemy session instance.
    """
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Create a new user.

    Args:
        user (schemas.UserCreate): The user data for creation.
        db (Session): Database session dependency.

    Returns:
        schemas.UserResponse: The created user.

    Raises:
        HTTPException: If the email is already in use.
    """
    # Check if the email already exists.
    existing_user = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already used")

    # Hash the password.
    hashed_password = pwd_context.hash(user.password)

    # Create a new user.
    new_user = models.User(username=user.username, email=user.email, password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.get("/{user_id}", response_model=schemas.UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a user by their ID.

    Args:
        user_id (int): The ID of the user.
        db (Session): Database session dependency.

    Returns:
        schemas.UserResponse: The retrieved user.

    Raises:
        HTTPException: If the user is not found.
    """
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/", response_model=list[schemas.UserResponse])
def list_users(db: Session = Depends(get_db)):
    """
    Retrieve a list of all users.

    Args:
        db (Session): Database session dependency.

    Returns:
        List[schemas.UserResponse]: A list of users.
    """
    return db.query(models.User).all()


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """
    Delete a user by their ID.

    Args:
        user_id (int): The ID of the user to delete.
        db (Session): Database session dependency.

    Raises:
        HTTPException: If the user is not found.
    """
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return
