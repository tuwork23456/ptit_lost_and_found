from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.user import User
from app.models.post import Post
from app.schemas.userschemas import UserResponse

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/{user_id}")
def get_user_profile(user_id: int, db: Session = Depends(get_db)):
    """Trả về thông tin cơ bản của user + danh sách bài đăng."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    posts = db.query(Post).filter(Post.user_id == user_id)\
               .order_by(Post.created_at.desc()).all()

    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "created_at": user.created_at.isoformat() if user.created_at else None,
        "post_count": len(posts),
        "posts": [
            {
                "id": p.id,
                "title": p.title,
                "type": p.type,
                "category": p.category,
                "location": p.location,
                "image": p.image,
                "views": p.views,
                "created_at": p.created_at.isoformat() if p.created_at else None,
            }
            for p in posts
        ]
    }
