from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.models.user import User
from app.models.notification import Notification
from app.core.security import get_current_user
from app.schemas.messageschemas import MessageCreate, MessageResponse, ChatHistoryResponse
from app.crud.message_crud import (
    create_message,
    get_chat_history,
    get_latest_pinned_post_context,
    get_unread_count,
    mark_messages_read,
    get_unread_count_by_sender,
)
from app.core.websocket import manager

router = APIRouter(prefix="/messages", tags=["messages"])


@router.post("/send", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def send_message(
    message_data: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    message_type = (message_data.message_type or "text").strip().lower()
    if message_type not in {"text", "context"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="message_type khong hop le.",
        )

    # Chặn user tự nhắn tin cho chính mình
    if message_data.receiver_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Khong the tu nhan tin cho chinh minh.",
        )

    # 1. Lưu tin nhắn vào DB
    new_msg = create_message(db=db, message_data=message_data, sender_id=current_user.id)
    if message_type == "text":
        db.add(
            Notification(
                user_id=message_data.receiver_id,
                message=f"Tin nhắn mới từ {current_user.username}",
                type="MESSAGE",
                target_id=current_user.id,
            )
        )
        db.commit()

    # 2. Gửi tín hiệu WebSocket thời gian thực tới người nhận nếu đang online
    await manager.send_personal_message(
        {
            "type": "new_message",
            "sender_id": current_user.id,
            "receiver_id": message_data.receiver_id,
        },
        user_id=message_data.receiver_id,
    )

    return new_msg


@router.get("/history/{receiver_id}", response_model=ChatHistoryResponse)
def chat_history(
    receiver_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    messages = get_chat_history(db=db, user1_id=current_user.id, user2_id=receiver_id)
    pinned = get_latest_pinned_post_context(db=db, user1_id=current_user.id, user2_id=receiver_id)
    pinned_payload = None
    if pinned and pinned.post_id:
        pinned_payload = {
            "post_id": int(pinned.post_id),
            "post_title": str(pinned.post_title or f"Bai viet #{pinned.post_id}"),
            "pinned_at": pinned.created_at,
            "pinned_by": int(pinned.sender_id),
        }
    return {"messages": messages, "pinned_post": pinned_payload}


@router.get("/unread-count")
def unread_messages_count(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    count = get_unread_count(db=db, user_id=current_user.id)
    return {"unread_count": count}


@router.put("/read/{sender_id}")
def mark_read(
    sender_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Mark all messages from sender_id → current_user as read."""
    mark_messages_read(db=db, receiver_id=current_user.id, sender_id=sender_id)
    db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.type == "MESSAGE",
        Notification.target_id == sender_id,
        Notification.is_read == False,
    ).update({"is_read": True})
    db.commit()
    remaining = get_unread_count(db=db, user_id=current_user.id)
    return {"unread_count": remaining}


@router.get("/conversations")
def get_conversations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Trả về danh sách những người đã từng nhắn tin với user hiện tại.
    Mỗi cuộc trò chuyện gồm: thông tin đối phương + tin nhắn gần đây nhất.
    """
    from app.models.message import Message
    from sqlalchemy import or_

    # Lấy tất cả messages liên quan đến user hiện tại
    all_msgs = (
        db.query(Message)
        .filter(
            or_(
                Message.sender_id == current_user.id,
                Message.receiver_id == current_user.id,
            )
        )
        .order_by(Message.created_at.desc())
        .all()
    )

    # Gom nhóm theo partner_id, lấy tin nhắn mới nhất
    seen = {}
    for msg in all_msgs:
        partner_id = (
            msg.receiver_id if msg.sender_id == current_user.id else msg.sender_id
        )
        if partner_id not in seen:
            partner = db.query(User).filter(User.id == partner_id).first()
            if not partner:
                continue
            seen[partner_id] = {
                "id": partner.id,
                "username": partner.username,
                "avatar": None,  # User model chưa có trường avatar
                "last_message": msg.content,
                "last_message_time": (
                    msg.created_at.isoformat() if msg.created_at else None
                ),
                "is_mine": msg.sender_id == current_user.id,
                "unread_count": get_unread_count_by_sender(
                    db=db,
                    receiver_id=current_user.id,
                    sender_id=partner_id,
                ),
            }
            pinned = get_latest_pinned_post_context(
                db=db, user1_id=current_user.id, user2_id=partner_id
            )
            if pinned and pinned.post_id:
                seen[partner_id]["pinned_post"] = {
                    "post_id": int(pinned.post_id),
                    "post_title": str(pinned.post_title or f"Bai viet #{pinned.post_id}"),
                    "pinned_at": pinned.created_at.isoformat() if pinned.created_at else None,
                    "pinned_by": int(pinned.sender_id),
                }
            else:
                seen[partner_id]["pinned_post"] = None

    return list(seen.values())
