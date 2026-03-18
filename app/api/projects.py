from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.security import get_current_user, get_db
from app.schemas.project import ProjectCreate
from app.services.project_service import create_project
from app.services.project_service import get_projects_by_owner
from app.schemas.project_member import ProjectMemberCreate
from app.services.project_service import create_project, get_projects_by_owner, add_project_member

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.post("/")
def create_new_project(
    project_data: ProjectCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    project = create_project(
        db=db,
        name=project_data.name,
        description=project_data.description,
        owner_id=current_user.id
    )

    return {
        "message": "Project created successfully",
        "project_id": project.id,
        "name": project.name,
        "owner_id": project.owner_id
    }
    
@router.get("/my-projects")
def list_my_projects(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    projects = get_projects_by_owner(db, current_user.id)

    return [
        {
            "id": project.id,
            "name": project.name,
            "description": project.description,
            "owner_id": project.owner_id
        }
        for project in projects
    ]
    
@router.post("/{project_id}/members")
def add_member_to_project(
    project_id: int,
    member_data: ProjectMemberCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    member = add_project_member(
        db=db,
        project_id=project_id,
        user_id=member_data.user_id,
        role_id=member_data.role_id
    )

    if not member:
        return {"message": "User is already a member of this project"}

    return {
        "message": "Member added successfully",
        "project_id": member.project_id,
        "user_id": member.user_id,
        "role_id": member.role_id
    }