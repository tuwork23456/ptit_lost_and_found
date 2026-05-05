from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship
from app.database.database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    email = Column(String, unique=True)
    password_hash = Column(String)
    role = Column(String, default="USER", nullable=False)  # USER / MOD / ADMIN
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    posts = relationship("Post", back_populates="owner", cascade="all, delete-orphan", foreign_keys="[Post.user_id]")
    comments = relationship("Comment", back_populates="user", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    messages_sent = relationship("Message", foreign_keys="[Message.sender_id]", back_populates="sender")
    messages_received = relationship("Message", foreign_keys="[Message.receiver_id]", back_populates="receiver")