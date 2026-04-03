
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import Literal
import asyncio

from app.core.connection_manager import manager
from app.core.security import get_current_user, get_db
from app.models.project import Project
from app.models.task import Task
from app.schemas.comment import CommentCreate, CommentResponse
from app.schemas.task import (
    TaskCreate,
    TaskStatusUpdate,
    TaskResponse,
    TaskStatusResponse,
    TaskDeleteResponse,
)
from app.services.activity_service import log_activity
from app.services.comment_service import create_comment, get_comments_by_task, delete_comment
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


def _broadcast(project_id: int, event: dict):
    """Fire-and-forget WebSocket broadcast from sync context."""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            loop.create_task(manager.broadcast(project_id, event))
    except RuntimeError:
        pass


@router.post("/{project_id}/tasks", response_model=TaskResponse)
def create_project_task(
    project_id: int,
    task_data: TaskCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    if not can_access_project(db, project_id, current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this project")

    task = create_task(
        db=db,
        title=task_data.title,
        description=task_data.description,
        project_id=project_id,
        assigned_to=task_data.assigned_to,
        created_by=current_user.id,
        due_date=task_data.due_date,
    )
    log_activity(db, project_id=project_id, user_id=current_user.id,
                 action="task_created", task_id=task.id, detail=f"Created task '{task.title}'")
    _broadcast(project_id, {"event": "task_created", "task_id": task.id, "title": task.title})
    return task


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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    if project.owner_id != current_user.id and not is_project_member(db, project_id, current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this project")

    return get_tasks_by_project(
        db=db, project_id=project_id, skip=skip, limit=limit,
        status=task_status, assigned_to=assigned_to
    )

@router.get("/tasks/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    if not can_access_project(db, task.project_id, current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this task")

    return task

@router.put("/tasks/{task_id}/status", response_model=TaskStatusResponse)
def update_task_status_endpoint(
    task_id: int,
    request: TaskStatusUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    if not can_access_project(db, task.project_id, current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this task")

    updated_task = update_task_status(db, task_id, request.status)
    log_activity(db, project_id=task.project_id, user_id=current_user.id,
                 action="task_status_changed", task_id=task_id,
                 detail=f"Status changed to '{request.status}'")
    _broadcast(task.project_id, {"event": "task_status_changed", "task_id": task_id, "status": request.status})
    return {"message": "Task updated successfully", "task_id": updated_task.id, "new_status": updated_task.status}


@router.delete("/tasks/{task_id}", response_model=TaskDeleteResponse)
def delete_task_endpoint(
    task_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    project = db.query(Project).filter(Project.id == task.project_id).first()
    if project.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the project owner can delete tasks")

    db.delete(task)
    db.commit()
    return {"message": "Task deleted successfully", "task_id": task_id}


# ── Comments ──────────────────────────────────────────────────────────────────

@router.post("/tasks/{task_id}/comments", response_model=CommentResponse, tags=["Comments"])
def add_comment(
    task_id: int,
    body: CommentCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    if not can_access_project(db, task.project_id, current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    comment = create_comment(db, task_id=task_id, author_id=current_user.id, content=body.content)
    _broadcast(task.project_id, {"event": "comment_added", "task_id": task_id, "comment_id": comment.id})
    return comment


@router.get("/tasks/{task_id}/comments", response_model=list[CommentResponse], tags=["Comments"])
def list_comments(
    task_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    if not can_access_project(db, task.project_id, current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    return get_comments_by_task(db, task_id)


@router.delete("/tasks/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Comments"])
def remove_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    comment = delete_comment(db, comment_id=comment_id, user_id=current_user.id)
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found or not yours")
