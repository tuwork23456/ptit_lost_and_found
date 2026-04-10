from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.database import Base

class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    type = Column(String, nullable=False)   # LOST / FOUND
    category = Column(String,nullable=False) 
    location = Column(String, nullable=True)
    contact = Column(String,nullable=False) 
    image = Column(String, nullable=True)
    views = Column(Integer, default=0)
    is_resolved = Column(Integer, default=0) # SQLite handles boolean as integer 0/1
    moderation_status = Column(String, default="APPROVED", nullable=False)  # PENDING / APPROVED / REJECTED / REMOVED
    moderation_note = Column(String, nullable=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    moderated_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    moderated_at = Column(DateTime, nullable=True)

    owner = relationship("User", back_populates="posts", foreign_keys=[user_id])
    moderator = relationship("User", foreign_keys=[moderated_by])
    comments = relationship("Comment", back_populates="post", cascade="all, delete-orphan")