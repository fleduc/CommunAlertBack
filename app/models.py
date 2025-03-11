"""
Module: models.py
Description: This module defines the SQLAlchemy models representing the entities in the application,
including users, alerts, messages, message read receipts, and message reactions.
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Float, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base
import enum


class User(Base):
    """
    Model representing a user.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(120), unique=True, index=True, nullable=False)
    password = Column(String(128), nullable=False)
    first_name = Column(String(50), nullable=True)
    last_name = Column(String(50), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    alerts = relationship("Alert", back_populates="user")
    messages = relationship("Message", back_populates="sender", cascade="all, delete-orphan")


# Optional: define an Enum for status and severity_level if you want stricter values.
class AlertStatus(str, enum.Enum):
    open = "open"
    closed = "closed"
    archived = "archived"


class SeverityLevel(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"


class Alert(Base):
    """
    Model representing an alert.
    """
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    alert_title = Column(String(255), index=True, nullable=False)
    description = Column(Text, nullable=False)
    alert_type = Column(Integer, nullable=False)  # Type of alert
    severity_level = Column(Enum(SeverityLevel), nullable=True)
    starting_date = Column(DateTime, nullable=True)
    closing_date = Column(DateTime, nullable=True)  # Closing date of the alert
    planned_duration = Column(Integer, nullable=True)  # In days
    status = Column(Enum(AlertStatus), nullable=False, server_default="open")
    public_status = Column(Boolean, default=False)
    postal_code = Column(String(10), nullable=True)  # Postal code
    longitude = Column(Float, nullable=True)
    latitude = Column(Float, nullable=True)
    radius = Column(Float, nullable=True)  # Radius in kilometers
    picture = Column(String(256), nullable=True)  # Link or path to the client's image
    created_at = Column(DateTime, default=datetime.utcnow)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    # Relationships
    user = relationship("User", back_populates="alerts")
    messages = relationship("Message", back_populates="alert", cascade="all, delete-orphan")


class Message(Base):
    """
    Model representing a message.
    """
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    alert_id = Column(Integer, ForeignKey("alerts.id"), nullable=False)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)  # Text content (for text, images, links, emojis, etc.)
    media_url = Column(String(255), nullable=True)  # Optional: URL for an image or an attached file
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    alert = relationship("Alert", back_populates="messages")
    sender = relationship("User", back_populates="messages")
    reactions = relationship("MessageReaction", back_populates="message", cascade="all, delete-orphan")
    read_receipts = relationship("MessageRead", back_populates="message", cascade="all, delete-orphan")


class MessageRead(Base):
    """
    Model representing a message read receipt.
    """
    __tablename__ = "message_reads"

    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(Integer, ForeignKey("messages.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    read_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    message = relationship("Message", back_populates="read_receipts")
    user = relationship("User")


class MessageReaction(Base):
    """
    Model representing a reaction (emoji) to a message.
    """
    __tablename__ = "message_reactions"

    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(Integer, ForeignKey("messages.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    emoji = Column(String(10), nullable=False)  # The emoji used
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    message = relationship("Message", back_populates="reactions")
