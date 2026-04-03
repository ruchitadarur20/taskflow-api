from sqlalchemy.orm import Session

from app.models.comment import Comment


def create_comment(db: Session, task_id: int, author_id: int, content: str) -> Comment:
    comment = Comment(task_id=task_id, author_id=author_id, content=content)
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment


def get_comments_by_task(db: Session, task_id: int) -> list[Comment]:
    return db.query(Comment).filter(Comment.task_id == task_id).order_by(Comment.created_at).all()


def delete_comment(db: Session, comment_id: int, user_id: int) -> Comment | None:
    comment = db.query(Comment).filter(Comment.id == comment_id, Comment.author_id == user_id).first()
    if comment:
        db.delete(comment)
        db.commit()
    return comment
