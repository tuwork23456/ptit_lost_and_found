from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database.database import get_db
from app.models.user import User
from app.core.security import get_current_user
from app.schemas.messageschemas import MessageCreate, MessageResponse
from app.crud.message_crud import create_message, get_chat_history, get_unread_count, mark_messages_read, get_unread_count_by_sender
from app.core.websocket import manager

router = APIRouter(prefix="/messages", tags=["messages"])

@router.post("/send", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def send_message(message_data: MessageCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # 1. Lưu tin nhắn vào DB
    new_msg = create_message(db=db, message_data=message_data, sender_id=current_user.id)
    
    # 2. Gửi tín hiệu WebSocket thời gian thực tới người nhận, nếu họ đang online.
    # Thông báo để Frontend gọi lại API lấy số lượng/nội dung mới
    await manager.send_personal_message(
        {"type": "new_message", "sender_id": current_user.id}, 
        user_id=message_data.receiver_id
    )
    
    return new_msg

@router.get("/history/{receiver_id}", response_model=List[MessageResponse])
def chat_history(receiver_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Lấy lịch sử chat giữa mình và một người được chọn
    messages = get_chat_history(db=db, user1_id=current_user.id, user2_id=receiver_id)
    return messages

@router.get("/unread-count")
def unread_messages_count(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    count = get_unread_count(db=db, user_id=current_user.id)
    return {"unread_count": count}

@router.put("/read/{sender_id}")
def mark_read(sender_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Mark all messages from sender_id → current_user as read."""
    mark_messages_read(db=db, receiver_id=current_user.id, sender_id=sender_id)
    remaining = get_unread_count(db=db, user_id=current_user.id)
    return {"unread_count": remaining}

@router.get("/conversations")
def get_conversations(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Trả về danh sách những người đã từng nhắn tin với user hiện tại.
    Mỗi cuộc trò chuyện gồm: thông tin đối phương + tin nhắn gần đây nhất.
    """
    from app.models.message import Message
    from sqlalchemy import or_, and_, func
    
    # Lấy tất cả messages liên quan đến user hiện tại
    all_msgs = db.query(Message).filter(
        or_(
            Message.sender_id == current_user.id,
            Message.receiver_id == current_user.id
        )
    ).order_by(Message.created_at.desc()).all()
    
    # Gom nhóm theo partner_id, lấy tin nhắn mới nhất
    seen = {}
    for msg in all_msgs:
        partner_id = msg.receiver_id if msg.sender_id == current_user.id else msg.sender_id
        if partner_id not in seen:
            partner = db.query(User).filter(User.id == partner_id).first()
            seen[partner_id] = {
                "id": partner.id,
                "username": partner.username,
                "avatar": getattr(partner, 'avatar', None),
                "last_message": msg.content,
                "last_message_time": msg.created_at.isoformat() if msg.created_at else None,
                "is_mine": msg.sender_id == current_user.id,
                "unread_count": get_unread_count_by_sender(db=db, receiver_id=current_user.id, sender_id=partner_id)
            }
    
    return list(seen.values())
