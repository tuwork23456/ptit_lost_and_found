from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class NotificationResponse(BaseModel):
    id: int
    message: str
    is_read: bool
    # Optional vì DB không có nullable=False — bản ghi cũ có thể thiếu 2 trường này
    type: Optional[str] = None
    target_id: Optional[int] = None
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True