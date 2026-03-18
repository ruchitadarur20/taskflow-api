from pydantic import BaseModel


class TaskCreate(BaseModel):
    title: str
    description: str | None = None
    assigned_to: int | None = None