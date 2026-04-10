from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.models.user import User
from app.core.security import get_current_user
from app.schemas.reportschemas import ReportCreate, ReportResponse
from app.crud.report_crud import create_report
from app.models.report import Report
from app.models.post import Post

router = APIRouter(prefix="/reports", tags=["reports"])

@router.post("", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
def submit_report(
    report_data: ReportCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Tạo báo cáo bài viết. Bất kỳ user nào đăng nhập đều có thể báo cáo.
    """
    report = create_report(db=db, report_data=report_data, reporter_id=current_user.id)
    return report


@router.get("", response_model=List[ReportResponse])
def get_all_reports(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Lấy danh sách tất cả báo cáo. Chỉ dành cho Admin/Mod.
    """
    from app.routers.post_router import is_admin_user
    if not is_admin_user(current_user):
        raise HTTPException(status_code=403, detail="Khong co quyen truy cap.")
    
    return (
        db.query(Report)
        .join(Post, Report.post_id == Post.id)
        .filter(Report.status == "PENDING", Post.moderation_status != "REMOVED")
        .order_by(Report.created_at.desc())
        .all()
    )
