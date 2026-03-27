from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.models.user import User
from app.core.security import get_current_user
from app.schemas.reportschemas import ReportCreate, ReportResponse
from app.crud.report_crud import create_report

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
