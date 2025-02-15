from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Float, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class User(Base):
    """
    Modèle représentant un utilisateur.
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

    alerts = relationship("Alert", back_populates="user")
    messages = relationship("Message", back_populates="sender", cascade="all, delete-orphan")

class Alert(Base):
    """
    Modèle représentant une alerte avec les corrections demandées.
    """
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    alert_title = Column(String(255), index=True, nullable=False)  # Correction du champ title
    description = Column(Text, nullable=False)  # Correction du champ message
    alert_type = Column(Integer, nullable=False)  # Ajout du type d'alerte
    closing_date = Column(DateTime, nullable=True)  # Ajout de la date de clôture
    postal_code = Column(String(10), nullable=True)  # Ajout du code postal
    created_at = Column(DateTime, default=datetime.utcnow)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="alerts")
    messages = relationship("Message", back_populates="alert", cascade="all, delete-orphan")


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    alert_id = Column(Integer, ForeignKey("alerts.id"), nullable=False)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)  # Contenu textuel (pour texte, images, liens, emoji, etc.)
    media_url = Column(String(255), nullable=True)  # Optionnel: pour une image ou un fichier attaché
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relations
    alert = relationship("Alert", back_populates="messages")
    sender = relationship("User", back_populates="messages")
    reactions = relationship("MessageReaction", back_populates="message", cascade="all, delete-orphan")
    read_receipts = relationship("MessageRead", back_populates="message", cascade="all, delete-orphan")


class MessageRead(Base):
    __tablename__ = "message_reads"

    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(Integer, ForeignKey("messages.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    read_at = Column(DateTime, default=datetime.utcnow)

    # Relations
    message = relationship("Message", back_populates="read_receipts")
    user = relationship("User")


class MessageReaction(Base):
    __tablename__ = "message_reactions"

    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(Integer, ForeignKey("messages.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    emoji = Column(String(10), nullable=False)  # L'emoji utilisé
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relations
    message = relationship("Message", back_populates="reactions")
