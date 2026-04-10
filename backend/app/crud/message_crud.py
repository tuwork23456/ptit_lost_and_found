from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from app.models.message import Message
from app.schemas.messageschemas import MessageCreate

def create_message(db: Session, message_data: MessageCreate, sender_id: int):
    new_message = Message(
        content=message_data.content,
        sender_id=sender_id,
        receiver_id=message_data.receiver_id,
        message_type=(message_data.message_type or "text"),
        post_id=message_data.post_id,
        post_title=message_data.post_title,
    )
    db.add(new_message)
    db.commit()
    db.refresh(new_message)
    return new_message

def get_chat_history(db: Session, user1_id: int, user2_id: int):
    return db.query(Message).filter(
        or_(
            and_(Message.sender_id == user1_id, Message.receiver_id == user2_id),
            and_(Message.sender_id == user2_id, Message.receiver_id == user1_id)
        ),
        Message.message_type == "text",
    ).order_by(Message.created_at.asc()).all()


def get_latest_pinned_post_context(db: Session, user1_id: int, user2_id: int):
    return (
        db.query(Message)
        .filter(
            or_(
                and_(Message.sender_id == user1_id, Message.receiver_id == user2_id),
                and_(Message.sender_id == user2_id, Message.receiver_id == user1_id),
            ),
            Message.message_type == "context",
            Message.post_id.isnot(None),
        )
        .order_by(Message.created_at.desc(), Message.id.desc())
        .first()
    )

def get_unread_count(db: Session, user_id: int):
    return db.query(Message).filter(Message.receiver_id == user_id, Message.is_read == False).count()

def mark_messages_read(db: Session, receiver_id: int, sender_id: int):
    """Mark all messages from sender_id to receiver_id as read."""
    db.query(Message).filter(
        Message.receiver_id == receiver_id,
        Message.sender_id == sender_id,
        Message.is_read == False
    ).update({"is_read": True})
    db.commit()

def get_unread_count_by_sender(db: Session, receiver_id: int, sender_id: int):
    """Count unread messages from a specific sender."""
    return db.query(Message).filter(
        Message.receiver_id == receiver_id,
        Message.sender_id == sender_id,
        Message.is_read == False
    ).count()
