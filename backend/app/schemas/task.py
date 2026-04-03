from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict


class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    assigned_to: Optional[int] = None
    project_id: Optional[int] = None
    due_date: Optional[datetime] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    assigned_to: Optional[int] = None


class TaskStatusUpdate(BaseModel):
    status: Literal["todo", "in_progress", "done"]


class TaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: Optional[str] = None
    status: str
    project_id: int
    assigned_to: Optional[int] = None
    created_by: int
    due_date: Optional[datetime] = None
    created_at: Optional[datetime] = None


class TaskStatusResponse(BaseModel):
    message: str
    task_id: int
    new_status: str


class TaskDeleteResponse(BaseModel):
    message: str
    task_id: int