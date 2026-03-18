from pydantic import BaseModel
from typing import Literal


class TaskCreate(BaseModel):
    title: str
    description: str | None = None
    assigned_to: int | None = None


class TaskStatusUpdate(BaseModel):
    status: Literal["todo", "in_progress", "done"]
    
from pydantic import BaseModel
from typing import Literal


class TaskCreate(BaseModel):
    title: str
    description: str | None = None
    assigned_to: int | None = None


class TaskStatusUpdate(BaseModel):
    status: Literal["todo", "in_progress", "done"]


class TaskResponse(BaseModel):
    id: int
    title: str
    description: str | None = None
    status: str
    project_id: int
    assigned_to: int | None = None
    created_by: int

    class Config:
        from_attributes = True


class TaskStatusResponse(BaseModel):
    message: str
    task_id: int
    new_status: str


class TaskDeleteResponse(BaseModel):
    message: str
    task_id: int