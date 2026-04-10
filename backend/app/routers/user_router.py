from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_, func

from app.database.database import get_db
from app.models.user import User
from app.models.post import Post
from app.schemas.userschemas import UserResponse
from app.core.security import get_current_user

router = APIRouter(prefix="/users", tags=["users"])


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
