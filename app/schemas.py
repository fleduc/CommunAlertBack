from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: Optional[int] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserBase(BaseModel):
    username: str
    email: EmailStr


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Schéma de base pour une alerte
class AlertBase(BaseModel):
    alert_title: str
    description: str
    alert_type: int
    closing_date: Optional[datetime] = None
    postal_code: Optional[str] = None
    user_id: int


# Pour la création, on peut hériter de AlertBase
class AlertCreate(AlertBase):
    pass


# Pour la mise à jour, vous pouvez exiger les mêmes champs ou définir des champs optionnels selon vos besoins.
class AlertUpdate(BaseModel):
    alert_title: Optional[str] = None
    description: Optional[str] = None
    alert_type: Optional[int] = None
    closing_date: Optional[datetime] = None
    postal_code: Optional[str] = None
    user_id: Optional[int] = None


class AlertResponse(AlertBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class MessageBase(BaseModel):
    content: str
    media_url: Optional[str] = None  # Optionnel


class MessageCreate(MessageBase):
    pass


class MessageResponse(MessageBase):
    id: int
    alert_id: int
    sender_id: int
    created_at: datetime

    reactions: Optional[List["MessageReactionResponse"]] = []
    read_by: Optional[List["MessageReadResponse"]] = []

    class Config:
        from_attributes = True


class MessageReadBase(BaseModel):
    pass


class MessageReadCreate(MessageReadBase):
    pass


class MessageReadResponse(BaseModel):
    id: int
    message_id: int
    user_id: int
    read_at: datetime

    class Config:
        from_attributes = True


class MessageReactionBase(BaseModel):
    emoji: str


class MessageReactionCreate(MessageReactionBase):
    pass


class MessageReactionResponse(BaseModel):
    id: int
    message_id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True
