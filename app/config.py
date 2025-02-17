"""
Module: config.py
Description: This module loads environment variables from a .env file and defines
configuration constants for the application, such as the secret key for signing tokens,
the token algorithm, token expiration time, and the database URL.
"""

import os
from dotenv import load_dotenv

# Load environment variables from the .env file.
load_dotenv()

# Secret key for signing tokens (should be changed in production).
SECRET_KEY = os.getenv("SECRET_KEY", "my_super_complex_secret_key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
DATABASE_URL = os.getenv("DATABASE_URL")
