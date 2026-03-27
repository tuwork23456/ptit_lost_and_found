from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.schemas.userschemas import UserResponse

class CommentCreate(BaseModel):
    content: str
    post_id: int
    # user_id được lấy từ JWT token phía backend, không cần gửi từ client


class CommentResponse(BaseModel):
    id: int
    content: str
    user_id: int
    post_id: int
    created_at: datetime
    user: Optional[UserResponse] = None

    model_config = {"from_attributes": True}