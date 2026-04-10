from sqlalchemy.orm import Session
from app.models.comment import Comment
from app.models.post import Post
from app.models.notification import Notification


def create_comment(db: Session, content, user_id, post_id, parent_comment_id=None):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        return None
    parent_comment = None
    if parent_comment_id:
        parent_comment = db.query(Comment).filter(Comment.id == parent_comment_id).first()
        if not parent_comment or parent_comment.post_id != post_id:
            return None

    comment = Comment(
        content=content,
        user_id=user_id,
        post_id=post_id,
        parent_comment_id=parent_comment_id,
    )
    db.add(comment)

    # ==========================
    # HỆ THỐNG THÔNG BÁO THÔNG MINH
    # ==========================
    
    # Lấy ra tất cả bình luận TRƯỚC ĐÓ trong bài viết này để lọc ra người theo dõi
    previous_comments = db.query(Comment).filter(Comment.post_id == post_id).all()
    
    # Dùng set() để lôi ra các user_id duy nhất của những người đã từng bình luận
    follower_ids = {c.user_id for c in previous_comments}
    
    # Chủ bài viết sẽ nhận message riêng, người đang viết (user_id) thì không cần nhận báo. Ta xóa cả 2 khỏi tập set này.
    follower_ids.discard(post.user_id)
    follower_ids.discard(user_id)

    # A. Tạo thông báo cho CHỦ BÀI VIẾT (trừ phi họ tự comment bài của chính mình)
    if post.user_id != user_id:
        owner_notification = Notification(
            user_id=post.user_id,
            message=f"Co binh luan moi trong bai: {post.title}",
            type="COMMENT",
            target_id=post_id
        )
        db.add(owner_notification)

    # B. Tạo thông báo cho người được trả lời trực tiếp
    if parent_comment and parent_comment.user_id not in {user_id, post.user_id}:
        reply_notification = Notification(
            user_id=parent_comment.user_id,
            message=f"Co phan hoi moi trong binh luan cua ban tai bai: {post.title}",
            type="COMMENT",
            target_id=post_id
        )
        db.add(reply_notification)

    # C. Tạo thông báo cho TẤT CẢ NGƯỜI TỪNG COMMENT (Followers)
    for f_id in follower_ids:
        if parent_comment and f_id == parent_comment.user_id:
            continue
        follower_notification = Notification(
            user_id=f_id,
            message=f"Co binh luan moi trong bai: {post.title}",
            type="COMMENT",
            target_id=post_id
        )
        db.add(follower_notification)

    # CUỐI CÙNG: Lưu đồng loạt cả Comment mới và toàn bộ Thông báo vào cơ sở dữ liệu
    db.commit()
    db.refresh(comment)
    return comment


def get_comments_by_post_id(db: Session, post_id: int):
    return db.query(Comment).filter(Comment.post_id == post_id).order_by(Comment.created_at.asc()).all()


def get_comment_by_id(db: Session, comment_id: int):
    return db.query(Comment).filter(Comment.id == comment_id).first()


def delete_comment(db: Session, comment_id: int):
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        return None

    db.delete(comment)
    db.commit()
    return comment