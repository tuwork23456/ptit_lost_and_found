from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from app.database.database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    email = Column(String, unique=True)
    password_hash = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    posts = relationship("Post", back_populates="owner")
    comments = relationship("Comment", back_populates="user")
    
    # THÊM MỚI: Khai báo relationship với Message (tách rõ gửi/nhận)
    messages_sent = relationship("Message", foreign_keys="[Message.sender_id]", back_populates="sender")
    messages_received = relationship("Message", foreign_keys="[Message.receiver_id]", back_populates="receiver")
    
    # THÊM MỚI: Khai báo relationship với Notification
    notifications = relationship("Notification", back_populates="user")

    # Thêm cascade để khi xóa User -> xóa luôn bài đăng, comment, thông báo của người đó
    posts = relationship("Post", back_populates="owner", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="user", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    
    # Riêng tin nhắn thì tùy logic, thường người ta giữ lại tin nhắn dù user bị xóa, 
    # nên bạn có thể không cần thêm cascade ở messages.
    messages_sent = relationship("Message", foreign_keys="[Message.sender_id]", back_populates="sender")
    messages_received = relationship("Message", foreign_keys="[Message.receiver_id]", back_populates="receiver")