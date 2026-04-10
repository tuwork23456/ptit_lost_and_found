from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, contains_eager, joinedload
from sqlalchemy import or_, func

from app.database.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.post import Post
from app.models.saved_post import SavedPost
from app.schemas.saved_postschemas import SavedPostResponse

router = APIRouter(prefix="/saved-posts", tags=["saved-posts"])


@router.get("", response_model=list[SavedPostResponse])
def get_saved_posts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # SQLite often runs without FK enforcement; drop bookmarks whose post row is gone.
    orphans = (
        db.query(SavedPost)
        .outerjoin(Post, SavedPost.post_id == Post.id)
        .filter(SavedPost.user_id == current_user.id, Post.id.is_(None))
        .all()
    )
    for row in orphans:
        db.delete(row)
    if orphans:
        db.commit()

    rows = (
        db.query(SavedPost)
        .join(Post, SavedPost.post_id == Post.id)
        .options(contains_eager(SavedPost.post).joinedload(Post.owner))
        .filter(
            SavedPost.user_id == current_user.id,
            or_(Post.moderation_status.is_(None), func.upper(Post.moderation_status) != "REMOVED"),
        )
        .order_by(SavedPost.created_at.desc())
        .all()
    )
    # Belt-and-suspenders if ORM ever leaves post unset after join.
    return [r for r in rows if r.post is not None]


@router.get("/ids", response_model=list[int])
def get_saved_post_ids(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    rows = (
        db.query(SavedPost.post_id)
        .join(Post, SavedPost.post_id == Post.id)
        .filter(
            SavedPost.user_id == current_user.id,
            or_(Post.moderation_status.is_(None), func.upper(Post.moderation_status) != "REMOVED"),
        )
        .all()
    )
    return [int(r[0]) for r in rows]


@router.post("/{post_id}")
def save_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    post = (
        db.query(Post)
        .filter(
            Post.id == post_id,
            or_(Post.moderation_status.is_(None), func.upper(Post.moderation_status) != "REMOVED"),
        )
        .first()
    )
    if not post:
        return {"ok": False, "message": "Post not found"}
    existed = db.query(SavedPost).filter(SavedPost.user_id == current_user.id, SavedPost.post_id == post_id).first()
    if existed:
        return {"ok": True, "saved": True}
    row = SavedPost(user_id=current_user.id, post_id=post_id)
    db.add(row)
    db.commit()
    return {"ok": True, "saved": True}


@router.delete("/{post_id}")
def unsave_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    row = db.query(SavedPost).filter(SavedPost.user_id == current_user.id, SavedPost.post_id == post_id).first()
    if row:
        db.delete(row)
        db.commit()
    return {"ok": True, "saved": False}

