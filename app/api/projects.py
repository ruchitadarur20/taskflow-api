from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.security import get_current_user, get_db
from app.schemas.project import ProjectCreate
from app.services.project_service import create_project
from app.services.project_service import get_projects_by_owner

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