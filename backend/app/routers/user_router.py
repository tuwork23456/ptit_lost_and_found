from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_, func

from app.database.database import get_db
from app.models.user import User
from app.models.post import Post
from app.schemas.userschemas import UserResponse
from pydantic import BaseModel
from app.core.security import get_current_user, is_admin_user

router = APIRouter(prefix="/users", tags=["users"])

class UserStatusUpdate(BaseModel):
    is_active: bool


@router.get("/locked", response_model=list[UserResponse])
def get_locked_users(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not is_admin_user(current_user):
        raise HTTPException(status_code=403, detail="Khong co quyen quan tri")
    return (
        db.query(User)
        .filter(User.is_active == False)
        .order_by(User.created_at.desc())
        .all()
    )


@router.get("/me", response_model=UserResponse)
def get_my_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Trả về thông tin đầy đủ (kể cả email) của chính user đang đăng nhập."""
    return current_user


@router.get("/{user_id}")
def get_user_profile(user_id: int, db: Session = Depends(get_db)):
    """Trả về thông tin công khai của user + danh sách bài đăng. Email bị ẩn."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    posts = (
        db.query(Post)
        .filter(
            Post.user_id == user_id,
            or_(Post.moderation_status.is_(None), func.upper(Post.moderation_status) != "REMOVED"),
        )
        .order_by(Post.created_at.desc())
        .all()
    )

    return {
        "id": user.id,
        "username": user.username,
        # email bị ẩn khỏi public profile (chỉ dùng /users/me để xem email của chính mình)
        "created_at": user.created_at.isoformat() if user.created_at else None,
        "post_count": len(posts),
        "posts": [
            {
                "id": p.id,
                "user_id": p.user_id,
                "username": user.username,
                "title": p.title,
                "description": p.description,
                "type": p.type,
                "category": p.category,
                "location": p.location,
                "image": p.image,
                "views": p.views,
                "created_at": p.created_at.isoformat() if p.created_at else None,
            }
            for p in posts
        ],
    }


@router.put("/{user_id}/status", response_model=UserResponse)
def update_user_status(
    user_id: int,
    payload: UserStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not is_admin_user(current_user):
        raise HTTPException(status_code=403, detail="Khong co quyen quan tri")
    target = db.query(User).filter(User.id == user_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="User not found")
    if target.id == current_user.id and payload.is_active is False:
        raise HTTPException(status_code=400, detail="Khong the tu khoa tai khoan cua chinh minh")
    if (getattr(target, "role", "") or "").upper() == "ADMIN" and payload.is_active is False:
        raise HTTPException(status_code=400, detail="Khong the khoa tai khoan ADMIN")
    target.is_active = bool(payload.is_active)
    db.commit()
    db.refresh(target)
    return target
