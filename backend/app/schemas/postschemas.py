from pydantic import BaseModel
from typing import Optional, List
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
    moderation_status: str = "APPROVED"
    moderation_note: Optional[str] = None
    moderated_by: Optional[int] = None
    moderated_at: Optional[datetime] = None
    owner: Optional[UserResponse] = None

    class Config:
        from_attributes = True 


class PostModerationRequest(BaseModel):
    action: str  # approve / reject / remove
    note: Optional[str] = None


class PostSearchResponse(BaseModel):
    items: List[PostResponse]
    total: int
    page: int
    limit: int