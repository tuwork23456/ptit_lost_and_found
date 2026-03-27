from sqlalchemy.orm import Session
from app.models.report import Report
from app.schemas.reportschemas import ReportCreate

def create_report(db: Session, report_data: ReportCreate, reporter_id: int):
    new_report = Report(
        post_id=report_data.post_id,
        reporter_id=reporter_id,
        reason=report_data.reason
    )
    db.add(new_report)
    db.commit()
    db.refresh(new_report)
    return new_report
