from pydantic import BaseModel


class TaskCreate(BaseModel):
    title: str
    description: str | None = None
    assigned_to: int | None = None
    
from pydantic import BaseModel

class TaskStatusUpdate(BaseModel):
    status: str
    
from pydantic import BaseModel

class TaskDelete(BaseModel):
    task_id: int