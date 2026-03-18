from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Literal

from app.core.security import get_current_user, get_db
from app.services.task_service import create_task, get_tasks_by_project, update_task_status
from app.models.project import Project
from app.models.task import Task
from app.schemas.task import (
    TaskCreate,
    TaskStatusUpdate,
    TaskResponse,
    TaskStatusResponse,
    TaskDeleteResponse,
)

router = APIRouter(prefix="/projects", tags=["Tasks"])


@router.post("/{project_id}/tasks", response_model=TaskResponse)
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


@router.get("/{project_id}/tasks", response_model=list[TaskResponse])
def list_project_tasks(
    project_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=50),
    status: Literal["todo", "in_progress", "done"] | None = None,
    assigned_to: int | None = Query(None, ge=1),
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


@router.put("/tasks/{task_id}/status", response_model=TaskStatusResponse)
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


@router.delete("/tasks/{task_id}", response_model=TaskDeleteResponse)
def delete_task_endpoint(
    task_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    task = db.query(Task).filter(Task.id == task_id).first()

    if not task:
        return {"error": "Task not found"}

    project = db.query(Project).filter(Project.id == task.project_id).first()

    if project.owner_id != current_user.id:
        return {"error": "Not authorized to delete this task"}

    db.delete(task)
    db.commit()

    return {"message": "Task deleted successfully", "task_id": task_id}