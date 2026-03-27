from sqlalchemy.orm import Session
from app.models.post import Post


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
        user_id=user_id
    )
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post


def get_all_posts(db: Session):
    return db.query(Post).all()


def get_post_by_id(db: Session, post_id: int):
    return db.query(Post).filter(Post.id == post_id).first()


def get_posts_by_user_id(db: Session, user_id: int):
    return db.query(Post).filter(Post.user_id == user_id).all()


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