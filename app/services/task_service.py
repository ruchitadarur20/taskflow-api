from sqlalchemy.orm import Session
from app.models.task import Task


def create_task(
    db: Session,
    title: str,
    description: str | None,
    project_id: int,
    assigned_to: int | None,
    created_by: int
):
    new_task = Task(
        title=title,
        description=description,
        status="todo",
        project_id=project_id,
        assigned_to=assigned_to,
        created_by=created_by
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task


def get_tasks_by_project(
    db: Session,
    project_id: int,
    skip: int = 0,
    limit: int = 10,
    status: str | None = None,
    assigned_to: int | None = None
):
    query = db.query(Task).filter(Task.project_id == project_id)

    if status:
        query = query.filter(Task.status == status)

    if assigned_to is not None:
        query = query.filter(Task.assigned_to == assigned_to)

    return query.offset(skip).limit(limit).all()


def update_task_status(db: Session, task_id: int, status: str):
    task = db.query(Task).filter(Task.id == task_id).first()

    if not task:
        return None

    task.status = status
    db.commit()
    db.refresh(task)
    return task
