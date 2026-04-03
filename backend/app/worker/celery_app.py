from celery import Celery
from celery.schedules import crontab

from app.core.config import REDIS_URL

celery_app = Celery(
    "taskflow",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["app.worker.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
)

# Periodic tasks
celery_app.conf.beat_schedule = {
    "send-due-date-reminders-daily": {
        "task": "app.worker.tasks.send_due_date_reminders",
        "schedule": crontab(hour=8, minute=0),  # every day at 08:00 UTC
    },
}
