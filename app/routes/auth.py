"""
Module: auth.py
Description: This module defines authentication endpoints for logging in and out.
It uses JWT tokens for authentication and sets a secure cookie containing the token.
All logging messages and user-facing strings are in English.
"""

import logging
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status, Body, Response, Query
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from app import models, schemas, database, security, config
from app.config import ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter()
logger = logging.getLogger(__name__)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify that a plain password matches the hashed password.

    Args:
        plain_password (str): The plain text password.
        hashed_password (str): The hashed password.

    Returns:
        bool: True if the password is valid, False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)


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


@router.post("/login", response_model=schemas.Token, tags=["auth"])
def login(
        user_credentials: schemas.UserLogin = Body(...),
        local_kw: str = Query(default=None),  # Workaround for potential issues, if necessary.
        response: Response = None,
        db: Session = Depends(get_db)
):
    """
    Authenticate the user and return a JWT token.

    Args:
        user_credentials (schemas.UserLogin): The user's login credentials.
        local_kw (str, optional): A query parameter workaround if needed.
        response (Response, optional): The HTTP response object for setting cookies.
        db (Session, optional): Database session dependency.

    Returns:
        dict: A dictionary containing the access token and its type.

    Raises:
        HTTPException: If the email or password is invalid.
    """
    logger.info(f"Attempting login for {user_credentials.email}")

    user = db.query(models.User).filter(models.User.email == user_credentials.email).first()
    if not user or not verify_password(user_credentials.password, user.password):
        logger.warning(f"Login failed for {user_credentials.email}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid email or password")

    access_token_expires = timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
    token = security.create_access_token(
        data={"user_id": user.id, "user_name": user.username},
        expires_delta=access_token_expires
    )

    # Set the JWT cookie with SameSite attribute.
    response.set_cookie(
        key="access_token",
        value=f"Bearer {token}",
        httponly=True,  # Prevent access via JavaScript.
        secure=False,  # Set to True in production with HTTPS.
        samesite="lax",  # 'lax' is recommended to protect against CSRF.
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # Cookie lifespan in seconds.
        path="/",
        domain="localhost"
    )

    logger.info(f"Login successful for {user_credentials.email}, generated token: {token}")
    return {"access_token": token, "token_type": "bearer"}


@router.post("/logout", tags=["auth"])
def logout(response: Response):
    """
    Log out the user by deleting the JWT cookie.

    In a stateless JWT architecture, logging out consists of deleting the cookie that contains the token.

    Args:
        response (Response): The HTTP response object used to delete the cookie.

    Returns:
        dict: A message indicating successful logout.
    """
    response.delete_cookie(key="access_token", path="/")
    return {"message": "Logout successful"}
