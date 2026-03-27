from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database.database import get_db
from app.models.user import User
from app.schemas.postschemas import PostResponse
from app.crud.post_crud import create_post, get_all_posts, get_post_by_id, delete_post, get_posts_by_user_id
from app.services.cloudinary_service import upload_image_to_cloudinary
from app.core.security import get_current_user

router = APIRouter(prefix="/posts", tags=["posts"])

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
        result = upload_image_to_cloudinary(file_bytes, file.filename)
        image_url = result.get("secure_url")

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
    if post.user_id != current_user.id:
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