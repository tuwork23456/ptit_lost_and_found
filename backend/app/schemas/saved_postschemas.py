from pydantic import BaseModel
from datetime import datetime
from app.schemas.postschemas import PostResponse


class SavedPostResponse(BaseModel):
    id: int
    user_id: int
    post_id: int
    created_at: datetime
    post: PostResponse

    class Config:
        from_attributes = True

