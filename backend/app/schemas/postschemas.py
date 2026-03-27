from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.schemas.userschemas import UserResponse

class PostBase(BaseModel):
    title: str
    description: str
    type: str         
    category: str     
    location: Optional[str] = None
    contact: str       
    image: Optional[str] = None

class PostCreate(PostBase):
    user_id: int 

class PostResponse(PostBase):
    id: int
    views: int
    user_id: int       
    created_at: datetime
    is_resolved: bool = False
    owner: Optional[UserResponse] = None

    class Config:
        from_attributes = True 