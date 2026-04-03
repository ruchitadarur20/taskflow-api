from pydantic import BaseModel


class ProjectMemberCreate(BaseModel):
    user_id: int
    role_id: int