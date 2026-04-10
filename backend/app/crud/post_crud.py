from sqlalchemy.orm import Session
from app.models.post import Post
from app.models.report import Report
from sqlalchemy import desc, or_, func
from datetime import datetime, timedelta


def create_post(
    db: Session,
    title: str,
    description: str,
    type: str,
    category: str,
    contact: str,
    user_id: int,
    location: str = None,
    image: str = None
):
    new_post = Post(
        title=title,
        description=description,
        type=type,
        category=category,
        location=location,
        contact=contact,
        image=image,
        user_id=user_id,
        # Bai moi phai vao hang cho duyet de admin/mod xu ly.
        moderation_status="PENDING",
    )
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post


def get_all_posts(db: Session):
    # Chỉ hiển thị bài đã được duyệt — đồng nhất với search_posts()
    return db.query(Post).filter(Post.moderation_status == "APPROVED").order_by(desc(Post.created_at), desc(Post.id)).all()


def get_post_by_id(db: Session, post_id: int):
    return db.query(Post).filter(Post.id == post_id).first()


def get_posts_by_user_id(db: Session, user_id: int):
    # User-facing manage page should not show posts already removed by admin/mod.
    return (
        db.query(Post)
        .filter(
            Post.user_id == user_id,
            or_(Post.moderation_status.is_(None), func.upper(Post.moderation_status) != "REMOVED"),
        )
        .order_by(desc(Post.created_at), desc(Post.id))
        .all()
    )


def delete_post(db: Session, post_id: int):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        return None

    db.delete(post)
    db.commit()
    return post

def resolve_post(db: Session, post_id: int):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        return None
    
    post.is_resolved = 1
    db.commit()
    db.refresh(post)
    return post


def moderate_post(db: Session, post_id: int, moderator_id: int, action: str, note: str | None = None):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        return None
    action_map = {
        "approve": "APPROVED",
        "reject": "REJECTED",
        "remove": "REMOVED",
    }
    mapped = action_map.get((action or "").lower())
    if not mapped:
        return None
    post.moderation_status = mapped
    post.moderated_by = moderator_id
    post.moderated_at = datetime.utcnow()
    post.moderation_note = note or ""
    if mapped == "REMOVED":
        (
            db.query(Report)
            .filter(Report.post_id == post.id, Report.status == "PENDING")
            .update({"status": "REVIEWED"}, synchronize_session=False)
        )
    db.commit()
    db.refresh(post)
    return post


def get_posts_by_moderation_status(db: Session, status: str):
    return (
        db.query(Post)
        .filter(Post.moderation_status == status.upper())
        .order_by(desc(Post.created_at), desc(Post.id))
        .all()
    )


def purge_removed_posts_older_than(db: Session, days: int) -> int:
    """Hard-delete posts that stayed REMOVED for more than `days`."""
    keep_days = max(1, int(days or 1))
    cutoff = datetime.utcnow() - timedelta(days=keep_days)
    rows = (
        db.query(Post)
        .filter(
            Post.moderation_status == "REMOVED",
            Post.moderated_at.isnot(None),
            Post.moderated_at <= cutoff,
        )
        .all()
    )
    if not rows:
        return 0
    count = len(rows)
    for p in rows:
        db.delete(p)
    db.commit()
    return count


def search_posts(
    db: Session,
    q: str = "",
    post_type: str | None = None,
    category: str | None = None,
    location: str | None = None,
    page: int = 1,
    limit: int = 10,
):
    query = db.query(Post).filter(Post.moderation_status == "APPROVED")

    if q:
        keyword = f"%{q.strip()}%"
        query = query.filter(
            or_(
                Post.title.ilike(keyword),
                Post.description.ilike(keyword),
                Post.category.ilike(keyword),
                Post.location.ilike(keyword),
            )
        )

    if post_type:
        query = query.filter(Post.type == post_type.upper())
    if category:
        query = query.filter(Post.category == category)
    if location:
        query = query.filter(Post.location.ilike(f"%{location.strip()}%"))

    total = query.count()
    page = max(1, page)
    limit = max(1, min(50, limit))
    offset = (page - 1) * limit
    items = query.order_by(desc(Post.created_at), desc(Post.id)).offset(offset).limit(limit).all()
    return items, total