from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.database import Base

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True)
    content = Column(String)

    sender_id = Column(Integer, ForeignKey("users.id"))
    receiver_id = Column(Integer, ForeignKey("users.id"))

    # THÊM MỚI: Cột is_read để đếm tin nhắn chưa đọc (cho icon Chat)
    is_read = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)

    # THÊM MỚI: Relationship mapping ngược lại bảng User
    sender = relationship("User", foreign_keys=[sender_id], back_populates="messages_sent")
    receiver = relationship("User", foreign_keys=[receiver_id], back_populates="messages_received")