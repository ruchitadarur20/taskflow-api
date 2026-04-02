import asyncio
from datetime import datetime, timedelta, timezone

from app.worker.celery_app import celery_app


@celery_app.task(name="app.worker.tasks.send_due_date_reminders")
def send_due_date_reminders():
    """
    Runs daily. Finds tasks due within the next 24 hours and emails the assignee.
    """
    from app.db.database import SessionLocal
    from app.models.task import Task
    from app.models.user import User
    from app.services.email_service import send_due_date_reminder_email

    db = SessionLocal()
    try:
        now = datetime.now(timezone.utc)
        window_end = now + timedelta(hours=24)

        tasks = (
            db.query(Task)
            .filter(
                Task.due_date.isnot(None),
                Task.due_date >= now,
                Task.due_date <= window_end,
                Task.status != "done",
                Task.assigned_to.isnot(None),
            )
            .all()
        )

        for task in tasks:
            user = db.query(User).filter(User.id == task.assigned_to).first()
            if user:
                due_str = task.due_date.strftime("%Y-%m-%d %H:%M UTC")
                asyncio.run(
                    send_due_date_reminder_email(
                        to_email=user.email,
                        assignee_name=user.full_name,
                        task_title=task.title,
                        due_date=due_str,
                    )
                )
    finally:
        db.close()


@celery_app.task(name="app.worker.tasks.send_assignment_email_task")
def send_assignment_email_task(to_email: str, assignee_name: str, task_title: str, project_name: str):
    """Background task to send a task-assignment notification email."""
    from app.services.email_service import send_task_assignment_email
    asyncio.run(send_task_assignment_email(to_email, assignee_name, task_title, project_name))


@celery_app.task(name="app.worker.tasks.send_invite_email_task")
def send_invite_email_task(to_email: str, invitee_name: str, project_name: str, inviter_name: str):
    """Background task to send a project-invite notification email."""
    from app.services.email_service import send_project_invite_email
    asyncio.run(send_project_invite_email(to_email, invitee_name, project_name, inviter_name))
