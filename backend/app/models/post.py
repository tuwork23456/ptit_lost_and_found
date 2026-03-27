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

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="posts")
    comments = relationship("Comment", back_populates="post", cascade="all, delete-orphan")