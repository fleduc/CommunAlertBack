"""
Module: schemas.py
Description: This module defines the Pydantic models (schemas) used for data validation and
serialization/deserialization within the application. Schemas are provided for authentication tokens,
users, alerts, messages, message read receipts, and message reactions.
"""

from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional, List
from enum import Enum


# Token -----------------
class Token(BaseModel):
    """Schema for access tokens."""
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Schema for token payload data."""
    user_id: Optional[int] = None


# User -----------------
class UserLogin(BaseModel):
    """Schema for user login credentials."""
    email: EmailStr
    password: str


class UserBase(BaseModel):
    """Base schema for user with common attributes."""
    username: str
    email: EmailStr


class UserCreate(UserBase):
    """Schema for creating a new user."""
    password: str


class UserResponse(UserBase):
    """Schema for user response data."""
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class UserBrief(BaseModel):
    """Schema for brief user information."""
    id: int
    username: str

    class Config:
        from_attributes = True


class UserOut(BaseModel):
    """Schema for UserOut user information."""
    id: int
    username: str

    class Config:
        orm_mode = True


# Enums for alerts -----------------
class AlertStatus(str, Enum):
    """Enum for alert status."""
    open = "open"
    closed = "closed"
    archived = "archived"


class SeverityLevel(str, Enum):
    """Enum for alert severity level."""
    low = "low"
    medium = "medium"
    high = "high"


# Alert Schemas -----------------
class AlertBase(BaseModel):
    """Base schema for alerts, used for responses."""
    alert_title: str
    description: str
    alert_type: int
    closing_date: Optional[datetime] = None
    postal_code: Optional[str] = None
    picture: Optional[str] = None          # URL/path to the customer's image (up to 256 characters)
    starting_date: Optional[datetime] = None # The date when the event starts
    longitude: Optional[float] = None        # Longitude of the alert location
    latitude: Optional[float] = None         # Latitude of the alert location
    radius: Optional[float] = None           # Radius in kilometers to spread the alert
    status: AlertStatus = AlertStatus.open   # Alert status (open, closed, archived)
    planned_duration: Optional[int] = None   # Planned duration (in days) for auto-close
    severity_level: Optional[SeverityLevel] = None  # Severity level (low, medium, high)
    public_status: Optional[bool] = False    # Public status (true if visible publicly)
    user_id: int                             # Creator's user ID


class AlertInput(BaseModel):
    """
    Schema for alert input (for creation and update).
    Notice: It excludes the user_id, which will be set in the backend.
    """
    alert_title: str
    description: str
    alert_type: int
    closing_date: Optional[datetime] = None
    postal_code: Optional[str] = None
    picture: Optional[str] = None          # Optional field; not typically provided by the client when using file upload.
    starting_date: Optional[datetime] = None
    longitude: Optional[float] = None
    latitude: Optional[float] = None
    radius: Optional[float] = None
    status: Optional[AlertStatus] = AlertStatus.open
    planned_duration: Optional[int] = None
    severity_level: Optional[SeverityLevel] = None
    public_status: Optional[bool] = False


class AlertCreate(AlertInput):
    """Schema for creating a new alert."""
    pass


class AlertUpdate(BaseModel):
    """
    Schema for updating an alert.
    All fields are optional to allow partial updates.
    """
    alert_title: Optional[str] = None
    description: Optional[str] = None
    alert_type: Optional[int] = None
    closing_date: Optional[datetime] = None
    postal_code: Optional[str] = None
    picture: Optional[str] = None
    starting_date: Optional[datetime] = None
    longitude: Optional[float] = None
    latitude: Optional[float] = None
    radius: Optional[float] = None
    status: Optional[AlertStatus] = None
    planned_duration: Optional[int] = None
    severity_level: Optional[SeverityLevel] = None
    public_status: Optional[bool] = None


class AlertResponse(AlertBase):
    """Schema for alert response data."""
    id: int
    created_at: datetime
    user: Optional["UserBrief"]  # Include brief user information

    class Config:
        from_attributes = True


# Rebuild forward references if necessary.
AlertResponse.model_rebuild()


# Message Reaction -----------------
class MessageReactionBase(BaseModel):
    """Base schema for message reactions."""
    emoji: str


class MessageReactionCreate(MessageReactionBase):
    """Schema for creating a message reaction."""
    pass


class MessageReactionResponse(BaseModel):
    """Schema for message reaction response data."""
    id: int
    message_id: int
    user_id: int
    emoji: str
    created_at: datetime

    class Config:
        from_attributes = True


# Message Read -----------------
class MessageReadBase(BaseModel):
    """Base schema for message read receipts."""
    pass


class MessageReadCreate(MessageReadBase):
    """Schema for creating a message read receipt."""
    pass


class MessageReadResponse(BaseModel):
    """Schema for message read receipt response data."""
    id: int
    message_id: int
    user_id: int
    read_at: datetime

    class Config:
        from_attributes = True


# Message -----------------
class MessageBase(BaseModel):
    """Base schema for messages."""
    content: str
    media_url: Optional[str] = None  # Optional URL for media (image, file, etc.)


class MessageCreate(MessageBase):
    """Schema for creating a new message."""
    pass


class MessageResponse(MessageBase):
    """Schema for message response data."""
    id: int
    alert_id: int
    sender_id: int
    sender: UserBrief
    created_at: datetime
    reactions: Optional[List[MessageReactionResponse]] = []
    read_by: Optional[List[MessageReadResponse]] = []

    class Config:
        from_attributes = True


# Rebuild the MessageResponse model to resolve any potential circular references.
MessageResponse.model_rebuild()
