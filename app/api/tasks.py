from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import Literal

from app.core.security import get_current_user, get_db
from app.models.project import Project
from app.models.task import Task
from app.schemas.task import (
    TaskCreate,
    TaskStatusUpdate,
    TaskResponse,
    TaskStatusResponse,
    TaskDeleteResponse,
)
from app.services.project_service import is_project_member
from app.services.task_service import create_task, get_tasks_by_project, update_task_status

router = APIRouter(prefix="/projects", tags=["Tasks"])


def can_access_project(db: Session, project_id: int, user_id: int) -> bool:
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        return False

    if project.owner_id == user_id:
        return True

    return is_project_member(db, project_id, user_id)


@router.post("/{project_id}/tasks", response_model=TaskResponse)
def create_project_task(
    project_id: int,
    task_data: TaskCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    if not can_access_project(db, project_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this project"
        )

    task = create_task(
        db=db,
        title=task_data.title,
        description=task_data.description,
        project_id=project_id,
        assigned_to=task_data.assigned_to,
        created_by=current_user.id
    )

    return {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "status": task.status,
        "project_id": task.project_id,
        "assigned_to": task.assigned_to,
        "created_by": task.created_by,
        "created_at": task.created_at,
    }


@router.get("/{project_id}/tasks", response_model=list[TaskResponse])
def list_project_tasks(
    project_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=50),
    task_status: Literal["todo", "in_progress", "done"] | None = None,
    assigned_to: int | None = Query(None, ge=1),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    project = db.query(Project).filter(Project.id == project_id).first()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    if project.owner_id != current_user.id and not is_project_member(db, project_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this project"
        )

    tasks = get_tasks_by_project(
        db=db,
        project_id=project_id,
        skip=skip,
        limit=limit,
        status=task_status,
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
            "created_by": task.created_by,
            "created_at": task.created_at,
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
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    if not can_access_project(db, task.project_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this task"
        )

    updated_task = update_task_status(db, task_id, request.status)

    return {
        "message": "Task updated successfully",
        "task_id": updated_task.id,
        "new_status": updated_task.status
    }


@router.delete("/tasks/{task_id}", response_model=TaskDeleteResponse)
def delete_task_endpoint(
    task_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    task = db.query(Task).filter(Task.id == task_id).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    project = db.query(Project).filter(Project.id == task.project_id).first()

    if project.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the project owner can delete tasks"
        )

    db.delete(task)
    db.commit()

    return {
        "message": "Task deleted successfully",
        "task_id": task_id
    }