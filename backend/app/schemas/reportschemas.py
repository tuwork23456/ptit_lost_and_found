from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.schemas.userschemas import UserResponse
from app.schemas.postschemas import PostResponse

class ReportCreate(BaseModel):
    post_id: int
    reason: str

class ReportResponse(BaseModel):
    id: int
    post_id: int
    reporter_id: int
    reason: str
    status: str
    created_at: datetime
    reporter: Optional[UserResponse] = None
    post: Optional[PostResponse] = None

    model_config = {"from_attributes": True}
