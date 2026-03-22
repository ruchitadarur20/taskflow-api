from sqlalchemy.orm import Session

from app.models.project import Project
from app.models.project_member import ProjectMember


def create_project(db: Session, name: str, description: str | None, owner_id: int):
    new_project = Project(
        name=name,
        description=description,
        owner_id=owner_id
    )
    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    return new_project


def get_projects_by_owner(db: Session, owner_id: int):
    return db.query(Project).filter(Project.owner_id == owner_id).all()


def get_project_by_id(db: Session, project_id: int):
    return db.query(Project).filter(Project.id == project_id).first()


def add_project_member(db: Session, project_id: int, user_id: int, role_id: int):
    existing_member = (
        db.query(ProjectMember)
        .filter(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == user_id
        )
        .first()
    )

    if existing_member:
        return None

    new_member = ProjectMember(
        project_id=project_id,
        user_id=user_id,
        role_id=role_id
    )

    db.add(new_member)
    db.commit()
    db.refresh(new_member)

    return new_member