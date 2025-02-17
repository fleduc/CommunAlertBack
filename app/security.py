"""
Module: security.py
Description: This module provides functions for creating and verifying JWT access tokens.
It uses the JOSE library for JWT encoding and decoding.
"""

from datetime import datetime, timedelta
from jose import jwt, JWTError
from app.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES


def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    """
    Create a JWT access token containing the provided data.

    Args:
        data (dict): The data to include in the token payload.
        expires_delta (timedelta, optional): The duration until the token expires.
            If not provided, the default expiration time is used.

    Returns:
        str: The encoded JWT access token.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_access_token(token: str):
    """
    Verify the validity of the JWT access token and return the decoded payload.

    Args:
        token (str): The JWT access token to verify.

    Returns:
        dict or None: The decoded token payload if the token is valid;
                      otherwise, None if verification fails.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
