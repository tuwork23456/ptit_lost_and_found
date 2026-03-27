from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class NotificationResponse(BaseModel):
    id: int
    message: str
    is_read: bool
    type: str
    target_id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True