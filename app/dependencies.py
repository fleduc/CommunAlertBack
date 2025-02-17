"""
Module: dependencies.py
Description: This module defines common dependencies for FastAPI routes. It includes functions to:
    - Provide a database session.
    - Retrieve the access token from a cookie.
    - Obtain the currently authenticated user based on the access token.
"""

from fastapi import Cookie, HTTPException, status, Depends
from sqlalchemy.orm import Session

from app import models, database, security


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


def get_token_from_cookie(access_token: str = Cookie(None)):
    """
    Retrieve the access token from a cookie.

    Args:
        access_token (str, optional): The access token extracted from the cookie.

    Returns:
        str: The access token.

    Raises:
        HTTPException: If the access token is not found in the cookie.
    """
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    return access_token


def get_current_user(token: str = Depends(get_token_from_cookie), db: Session = Depends(get_db)) -> models.User:
    """
    Retrieve the currently authenticated user based on the access token.

    This function removes the "Bearer " prefix from the token (if present), verifies the token,
    extracts the user ID from the token payload, and retrieves the user from the database.

    Args:
        token (str): The access token (extracted from the cookie).
        db (Session): Database session dependency.

    Returns:
        models.User: The authenticated user.

    Raises:
        HTTPException: If the token is invalid, the payload is missing the user ID, or the user is not found.
    """
    # Remove "Bearer " prefix if present.
    if token.startswith("Bearer "):
        token = token[7:]

    payload = security.verify_access_token(token)
    if payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")

    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    return user
