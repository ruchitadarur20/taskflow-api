from sqlalchemy.orm import Session

from app.models.project import Project


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