"""
Module: database.py
Description: This module configures the database connection using SQLAlchemy.
It creates the database engine, a session local for interacting with the database,
and a declarative base class for model definitions.
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.config import DATABASE_URL

# Create a SQLAlchemy engine instance using the database URL.
engine = create_engine(DATABASE_URL)

# Create a session local class. Each instance of SessionLocal is a database session.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a base class for declarative class definitions.
Base = declarative_base()
