from pydantic import BaseModel
from typing import Literal


class TaskCreate(BaseModel):
    title: str
    description: str | None = None
    assigned_to: int | None = None


class TaskStatusUpdate(BaseModel):
    status: Literal["todo", "in_progress", "done"]