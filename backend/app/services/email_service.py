from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from pydantic import EmailStr

from app.core.config import (
    MAIL_FROM,
    MAIL_PASSWORD,
    MAIL_PORT,
    MAIL_SERVER,
    MAIL_SSL_TLS,
    MAIL_STARTTLS,
    MAIL_USERNAME,
)

_conf = ConnectionConfig(
    MAIL_USERNAME=MAIL_USERNAME,
    MAIL_PASSWORD=MAIL_PASSWORD,
    MAIL_FROM=MAIL_FROM,
    MAIL_PORT=MAIL_PORT,
    MAIL_SERVER=MAIL_SERVER,
    MAIL_STARTTLS=MAIL_STARTTLS,
    MAIL_SSL_TLS=MAIL_SSL_TLS,
    USE_CREDENTIALS=bool(MAIL_USERNAME),
    VALIDATE_CERTS=True,
)

_mailer = FastMail(_conf)


async def send_task_assignment_email(to_email: EmailStr, assignee_name: str, task_title: str, project_name: str):
    message = MessageSchema(
        subject=f"[TaskFlow] You've been assigned: {task_title}",
        recipients=[to_email],
        body=(
            f"Hi {assignee_name},\n\n"
            f"You have been assigned the task '{task_title}' in project '{project_name}'.\n\n"
            "Log in to TaskFlow to view the details.\n\n"
            "— TaskFlow"
        ),
        subtype=MessageType.plain,
    )
    await _mailer.send_message(message)


async def send_project_invite_email(to_email: EmailStr, invitee_name: str, project_name: str, inviter_name: str):
    message = MessageSchema(
        subject=f"[TaskFlow] You've been added to project: {project_name}",
        recipients=[to_email],
        body=(
            f"Hi {invitee_name},\n\n"
            f"{inviter_name} has added you to the project '{project_name}' on TaskFlow.\n\n"
            "Log in to start collaborating.\n\n"
            "— TaskFlow"
        ),
        subtype=MessageType.plain,
    )
    await _mailer.send_message(message)


async def send_due_date_reminder_email(to_email: EmailStr, assignee_name: str, task_title: str, due_date: str):
    message = MessageSchema(
        subject=f"[TaskFlow] Reminder: '{task_title}' is due soon",
        recipients=[to_email],
        body=(
            f"Hi {assignee_name},\n\n"
            f"This is a reminder that the task '{task_title}' is due on {due_date}.\n\n"
            "— TaskFlow"
        ),
        subtype=MessageType.plain,
    )
    await _mailer.send_message(message)
