from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.security import get_current_user, get_db
from app.schemas.task import TaskCreate
from app.services.task_service import create_task
from app.services.task_service import get_tasks_by_project

router = APIRouter(prefix="/projects", tags=["Tasks"])


@router.post("/{project_id}/tasks")
def create_project_task(
    project_id: int,
    task_data: TaskCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    task = create_task(
        db=db,
        title=task_data.title,
        description=task_data.description,
        project_id=project_id,
        assigned_to=task_data.assigned_to,
        created_by=current_user.id
    )

    return {
        "message": "Task created successfully",
        "task_id": task.id,
        "title": task.title,
        "status": task.status,
        "project_id": task.project_id,
        "assigned_to": task.assigned_to,
        "created_by": task.created_by
    }

@router.get("/{project_id}/tasks")
def list_project_tasks(
    project_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    tasks = get_tasks_by_project(db, project_id)

    return [
        {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "status": task.status,
            "project_id": task.project_id,
            "assigned_to": task.assigned_to,
            "created_by": task.created_by
        }
        for task in tasks
    ]