from pydantic import BaseModel
from datetime import datetime

class MessageBase(BaseModel):
    content: str

class MessageCreate(MessageBase):
    receiver_id: int
    # Tương tự comment, sender_id (người gửi) nên lấy từ Token đăng nhập
    # thay vì để Frontend gửi lên để đảm bảo bảo mật.

class MessageResponse(MessageBase):
    id: int
    sender_id: int
    receiver_id: int
    is_read: bool
    created_at: datetime

    model_config = {"from_attributes": True}