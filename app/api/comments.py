from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user, get_db
from app.schemas.comment import CommentCreate, CommentResponse
from app.services.comment_service import create_comment, delete_comment, get_comments_by_task
from app.services.task_service import get_task_by_id

router = APIRouter(prefix="/tasks/{task_id}/comments", tags=["Comments"])


@router.post("/", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
def add_comment(
    task_id: int,
    comment_data: CommentCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    task = get_task_by_id(db, task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return create_comment(db, task_id=task_id, author_id=current_user.id, content=comment_data.content)


@router.get("/", response_model=list[CommentResponse])
def list_comments(
    task_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    task = get_task_by_id(db, task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return get_comments_by_task(db, task_id=task_id)


@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_comment(
    task_id: int,
    comment_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    comment = delete_comment(db, comment_id=comment_id, user_id=current_user.id)
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found or not yours")
