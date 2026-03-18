from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.security import get_current_user, get_db
from app.schemas.task import TaskCreate
from app.services.task_service import create_task
from app.services.task_service import get_tasks_by_project
from app.services.task_service import update_task_status
from app.schemas.task import TaskStatusUpdate
from app.services.task_service import delete_task
from app.models.project import Project
from app.models.task import Task
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

from pydantic import BaseModel


class TaskCreate(BaseModel):
    title: str
    description: str | None = None
    assigned_to: int | None = None
    
from pydantic import BaseModel

class TaskStatusUpdate(BaseModel):
    status: str
    
from app.services.task_service import update_task_status
from app.schemas.task import TaskStatusUpdate

@router.put("/tasks/{task_id}/status")
def update_task_status_endpoint(
    task_id: int,
    request: TaskStatusUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    task = update_task_status(db, task_id, request.status)

    if not task:
        return {"error": "Task not found"}

    return {
        "message": "Task updated successfully",
        "task_id": task.id,
        "new_status": task.status
    }

@router.delete("/tasks/{task_id}")
def delete_task_endpoint(
    task_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    task = db.query(Task).filter(Task.id == task_id).first()

    if not task:
        return {"error": "Task not found"}

    project = db.query(Project).filter(Project.id == task.project_id).first()

    # Only owner can delete
    if project.owner_id != current_user.id:
        return {"error": "Not authorized to delete this task"}

    db.delete(task)
    db.commit()

    return {
        "message": "Task deleted successfully",
        "task_id": task_id
    }
    
@router.get("/{project_id}/tasks")
def list_project_tasks(
    project_id: int,
    skip: int = 0,
    limit: int = 10,
    status: str | None = None,
    assigned_to: int | None = None,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    tasks = get_tasks_by_project(
        db=db,
        project_id=project_id,
        skip=skip,
        limit=limit,
        status=status,
        assigned_to=assigned_to
    )

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