from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class ActivityLogResponse(BaseModel):
    id: int
    project_id: int
    task_id: Optional[int] = None
    user_id: int
    action: str
    detail: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
