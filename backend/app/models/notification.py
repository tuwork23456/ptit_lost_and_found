from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.database import Base

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True)
    message = Column(String)
    is_read = Column(Boolean, default=False)
    
    # THÊM MỚI: Phân loại thông báo (VD: 'COMMENT')
    type = Column(String) 
    
    # THÊM MỚI: Lưu ID của bài viết (Post ID) để Frontend biết đường chuyển hướng
    target_id = Column(Integer) 

    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    # THÊM MỚI: Relationship mapping ngược lại bảng User
    user = relationship("User", back_populates="notifications")