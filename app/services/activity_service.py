from sqlalchemy.orm import Session

from app.models.activity_log import ActivityLog


def log_activity(
    db: Session,
    project_id: int,
    user_id: int,
    action: str,
    task_id: int | None = None,
    detail: str | None = None,
) -> ActivityLog:
    entry = ActivityLog(
        project_id=project_id,
        task_id=task_id,
        user_id=user_id,
        action=action,
        detail=detail,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


def get_project_activity(db: Session, project_id: int, limit: int = 50) -> list[ActivityLog]:
    return (
        db.query(ActivityLog)
        .filter(ActivityLog.project_id == project_id)
        .order_by(ActivityLog.created_at.desc())
        .limit(limit)
        .all()
    )
