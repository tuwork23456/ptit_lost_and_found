from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class MessageBase(BaseModel):
    content: str

class MessageCreate(MessageBase):
    receiver_id: int
    message_type: str = "text"
    post_id: Optional[int] = None
    post_title: Optional[str] = None
    # Tương tự comment, sender_id (người gửi) nên lấy từ Token đăng nhập
    # thay vì để Frontend gửi lên để đảm bảo bảo mật.

class MessageResponse(MessageBase):
    id: int
    sender_id: int
    receiver_id: int
    is_read: bool
    created_at: datetime
    message_type: str = "text"
    post_id: Optional[int] = None
    post_title: Optional[str] = None

    model_config = {"from_attributes": True}


class PinnedPost(BaseModel):
    post_id: int
    post_title: str
    pinned_at: datetime
    pinned_by: int


class ChatHistoryResponse(BaseModel):
    messages: List[MessageResponse]
    pinned_post: Optional[PinnedPost] = None