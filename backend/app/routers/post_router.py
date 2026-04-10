from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from pathlib import Path
from uuid import uuid4
import os

from app.database.database import get_db
from app.models.user import User
from app.schemas.postschemas import PostResponse, PostModerationRequest, PostSearchResponse
from app.crud.post_crud import (
    create_post,
    get_all_posts,
    get_post_by_id,
    delete_post,
    get_posts_by_user_id,
    moderate_post,
    get_posts_by_moderation_status,
    purge_removed_posts_older_than,
    search_posts,
)
from app.services.cloudinary_service import upload_image_to_cloudinary
from app.core.security import get_current_user, is_admin_user

router = APIRouter(prefix="/posts", tags=["posts"])
REMOVED_POST_RETENTION_DAYS = int(os.getenv("REMOVED_POST_RETENTION_DAYS", "14"))


def _save_image_local(file_bytes: bytes, filename: str) -> str:
    ext = Path(filename).suffix.lower() if filename else ".jpg"
    if ext not in {".jpg", ".jpeg", ".png", ".webp", ".gif"}:
        ext = ".jpg"
    upload_dir = Path(__file__).resolve().parents[1] / "uploads"
    upload_dir.mkdir(parents=True, exist_ok=True)
    stored_name = f"{uuid4().hex}{ext}"
    file_path = upload_dir / stored_name
    file_path.write_bytes(file_bytes)
    # Store as relative path for portability across host/port changes.
    return f"/uploads/{stored_name}"

@router.post("", response_model=PostResponse)
async def create_post_api(
    title: str = Form(...),
    description: str = Form(...),
    type: str = Form(...),
    category: str = Form(...),
    location: Optional[str] = Form(None),
    contact: str = Form(...),
    file: UploadFile = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    image_url = None
    if file and file.filename:
        file_bytes = await file.read()
        if not file_bytes:
            raise HTTPException(status_code=400, detail="File anh rong. Vui long chon lai anh.")
        try:
            result = upload_image_to_cloudinary(file_bytes, file.filename)
            image_url = result.get("secure_url")
            if not image_url:
                image_url = _save_image_local(file_bytes, file.filename)
        except Exception:
            # Fallback local storage so post creation remains usable.
            image_url = _save_image_local(file_bytes, file.filename)

    # Chuyển đổi thành chuỗi rỗng thay vì None để tránh lỗi NOT NULL nếu DB cũ chưa migrate
    clean_location = location if location and location.strip() != "" else ""

    new_post = create_post(
        db=db,
        title=title,
        description=description,
        type=type,
        category=category,
        location=clean_location,
        contact=contact,
        image=image_url,
        user_id=current_user.id
    )
    return new_post

@router.get("/my", response_model=List[PostResponse])
def get_my_posts(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Trả về tất cả bài đăng của user đang đăng nhập."""
    return get_posts_by_user_id(db, current_user.id)

@router.get("", response_model=List[PostResponse])
def get_posts(db: Session = Depends(get_db)):
    return get_all_posts(db)


@router.get("/search", response_model=PostSearchResponse)
def search_posts_api(
    q: str = "",
    type: Optional[str] = None,
    category: Optional[str] = None,
    location: Optional[str] = None,
    page: int = 1,
    limit: int = 10,
    db: Session = Depends(get_db),
):
    items, total = search_posts(
        db=db,
        q=q,
        post_type=type,
        category=category,
        location=location,
        page=page,
        limit=limit,
    )
    return {"items": items, "total": total, "page": max(1, page), "limit": max(1, min(50, limit))}


@router.get("/moderation/{status}", response_model=List[PostResponse])
def get_posts_for_moderation(
    status: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not is_admin_user(current_user):
        raise HTTPException(status_code=403, detail="Khong co quyen kiem duyet")
    if status.upper() == "REMOVED":
        # Keep REMOVED list clean on each admin refresh.
        purge_removed_posts_older_than(db, REMOVED_POST_RETENTION_DAYS)
    return get_posts_by_moderation_status(db, status)

@router.get("/{post_id}", response_model=PostResponse)
def get_post(post_id: int, db: Session = Depends(get_db)):
    post = get_post_by_id(db, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post

@router.delete("/{post_id}", status_code=status.HTTP_200_OK)
def remove_post(post_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    post = get_post_by_id(db, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if post.user_id != current_user.id and not is_admin_user(current_user):
        raise HTTPException(status_code=403, detail="Không có quyền xóa bài này")
    delete_post(db, post_id)
    return {"message": "Post deleted successfully"}

@router.put("/{post_id}/resolve", response_model=PostResponse)
def mark_post_resolved(post_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    from app.crud.post_crud import resolve_post
    post = get_post_by_id(db, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if post.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Không có quyền thực hiện hành động này")
    
    updated_post = resolve_post(db, post_id)
    return updated_post


@router.put("/{post_id}/image", response_model=PostResponse)
async def update_post_image_api(
    post_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    post = get_post_by_id(db, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if post.user_id != current_user.id and not is_admin_user(current_user):
        raise HTTPException(status_code=403, detail="Khong co quyen cap nhat anh bai nay")
    if not file or not file.filename:
        raise HTTPException(status_code=400, detail="Vui long chon anh.")

    file_bytes = await file.read()
    if not file_bytes:
        raise HTTPException(status_code=400, detail="File anh rong. Vui long chon lai anh.")

    image_url = ""
    try:
        result = upload_image_to_cloudinary(file_bytes, file.filename)
        image_url = str(result.get("secure_url") or "").strip()
    except Exception:
        image_url = ""
    if not image_url:
        image_url = _save_image_local(file_bytes, file.filename)

    post.image = image_url
    db.commit()
    db.refresh(post)
    return post


@router.put("/{post_id}/moderate", response_model=PostResponse)
def moderate_post_api(
    post_id: int,
    payload: PostModerationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not is_admin_user(current_user):
        raise HTTPException(status_code=403, detail="Khong co quyen kiem duyet")
    updated = moderate_post(
        db=db,
        post_id=post_id,
        moderator_id=current_user.id,
        action=payload.action,
        note=payload.note,
    )
    if not updated:
        raise HTTPException(status_code=400, detail="Action moderation khong hop le hoac bai viet khong ton tai")
    return updated